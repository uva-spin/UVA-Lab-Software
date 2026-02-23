"""
ETL Pipeline: Extract → Transform → Load.
Orchestrates device readers and loader. Single acquisition loop.
"""
import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import pytz

from .loaders import MariaDBLoader
from .schema import QT_RAW_TO_COLS, TABLE_SCHEMAS

logger = logging.getLogger(__name__)
EST = pytz.timezone("America/New_York")


def _est_str() -> str:
    return datetime.now(EST).strftime("%Y-%m-%d %H:%M:%S")


# --- Record definitions: (table, transform_fn) ---
# transform_fn: raw_data -> Optional[Dict] or Optional[Tuple[Dict,...]] for multi-table

def _qt_transform(raw: List[float]) -> Optional[Dict]:
    if not raw or len(raw) != 18:
        return None
    row = {}
    for idx, col in QT_RAW_TO_COLS:
        if idx < len(raw):
            row[col] = raw[idx]
    row["Timestamp"] = _est_str()
    return row


def _teledyne_transform(raw: List) -> Optional[Dict]:
    if not raw or len(raw) < 3 or not any(v is not None for v in raw[:3]):
        return None
    return {
        "seperator_flow": raw[0],
        "magnet_flow": raw[1],
        "main_flow": raw[2],
        "Timestamp": _est_str(),
    }


def _labjack1_transform(raw: List) -> Optional[Dict]:
    if not raw or len(raw) < 6:
        return None
    return {
        "root_exhaust_pressure": raw[0],
        "buffer_pressure": raw[1],
        "magnet_pressure": raw[2],
        "purifier_inlet_pressure": raw[3],
        "fridge_vapor_pressure": raw[4],
        "thermocouple": raw[5],
        "Timestamp": _est_str(),
    }


def _labjack2_transform(raw: List) -> Optional[Tuple[Dict, Dict]]:
    """Returns (Flow_Rates row, Labjack row) - two inserts."""
    if not raw or len(raw) < 4:
        return None
    ts = _est_str()
    return (
        {"microwave_flow": raw[0], "heat_exchanger_flow": raw[1], "Timestamp": ts},
        {"magnet_bottom_temperature": raw[2], "magnet_top_temperature": raw[3], "Timestamp": ts},
    )


def _lakeshore_transform(raw: List, table: str) -> Optional[Dict]:
    if not raw or len(raw) < 8:
        return None
    cols = [c for c in TABLE_SCHEMAS[table] if c != "Timestamp"]
    row = {c: raw[i] for i, c in enumerate(cols) if i < len(raw)}
    row["Timestamp"] = _est_str()
    return row


def _maxigauge_transform(raw: List) -> Optional[Dict]:
    if not raw or len(raw) != 6:
        return None
    cols = [c for c in TABLE_SCHEMAS["MaxiGauge"] if c != "Timestamp"]
    row = {c: raw[i] for i, c in enumerate(cols)}
    row["Timestamp"] = _est_str()
    return row


def _ivc_transform(raw: Any) -> Optional[Dict]:
    if raw is None or not isinstance(raw, (int, float)):
        return None
    return {"ivc_pressure": float(raw), "Timestamp": _est_str()}


class AcquisitionPipeline:
    """
    ETL pipeline: runs extractors, transforms, loads to DB.
    """

    def __init__(self, loader: MariaDBLoader, extractors: Dict[str, Callable]):
        """
        extractors: { "qt": async_fn, "teledyne": async_fn, ... }
        Each async_fn returns raw data (list/float/None).
        """
        self.loader = loader
        self.extractors = extractors
        self._status: Dict[str, str] = {}

    async def run_once(self) -> Dict[str, str]:
        """Execute one E→T→L cycle. Returns status dict."""
        status = {k: "none" for k in self.extractors}

        # Extract (concurrent)
        tasks = {k: asyncio.create_task(self._safe_extract(k, fn)) for k, fn in self.extractors.items()}
        results = {}
        for k, t in tasks.items():
            try:
                results[k] = await t
            except Exception as e:
                logger.error(f"Extract {k}: {e}")
                results[k] = None

        # Transform & Load
        load_ops = []

        # QT
        if row := _qt_transform(results.get("qt")):
            load_ops.append(("QT", "qt", row))

        # Teledyne
        if row := _teledyne_transform(results.get("teledyne")):
            load_ops.append(("Flow_Rates", "teledyne", row))

        # LabJack 1
        if row := _labjack1_transform(results.get("labjack_1")):
            load_ops.append(("Labjack", "labjack_1", row))

        # LabJack 2 (two tables)
        if pair := _labjack2_transform(results.get("labjack_2")):
            load_ops.append(("Flow_Rates", "labjack_2", pair[0]))
            load_ops.append(("Labjack", "labjack_2", pair[1]))

        # Lakeshore
        for suffix, key in [("Target_Stick", "lakeshore_ts"), ("Fridge_Temp", "lakeshore_ft"), ("Magnet_Temp", "lakeshore_mt")]:
            table = f"Lakeshore_{suffix}"
            if row := _lakeshore_transform(results.get(key), table):
                load_ops.append((table, key, row))

        # MaxiGauge
        if row := _maxigauge_transform(results.get("maxigauge")):
            load_ops.append(("MaxiGauge", "maxigauge", row))

        # IVC
        if row := _ivc_transform(results.get("ivc")):
            load_ops.append(("IVC", "ivc", row))

        # Execute loads (sync, in thread if needed to avoid blocking)
        for table, key, row in load_ops:
            cols = [c for c in row.keys()]
            vals = [row[c] for c in cols]
            ok = self.loader.insert(table, cols, vals)
            status[key] = "success" if ok else "error"

        self._status = status
        return status

    async def _safe_extract(self, name: str, fn: Callable) -> Any:
        try:
            if asyncio.iscoroutinefunction(fn):
                return await fn()
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, fn)
        except Exception as e:
            logger.debug(f"Extract {name}: {e}")
            return None
