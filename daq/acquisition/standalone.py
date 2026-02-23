"""
Standalone data acquisition - ETL pipeline entry point.
Usage:
    python -m daq.acquisition.standalone
    python -m daq.acquisition.standalone --verbose --terminal-log
"""
import argparse
import asyncio
import logging
import os
import signal
import sys
import time

# Ensure daq/ is on path when run as script or module
_daq_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _daq_root not in sys.path:
    sys.path.insert(0, _daq_root)

from config import (
    DATABASE_FILE,
    FLOAT_PORT,
    INT_PORT,
    IVC_PORT,
    LABJACK_CHECK_INTERVAL,
    LAKESHORE_PORTS,
    NUM_REG_TO_READ,
    PLC_IP,
    QT_LABELS,
    SLEEP_INTERVAL,
    TELEDYNE_CHECK_INTERVAL,
    UNIT_ID,
)
from core.loaders import MariaDBLoader
from core.pipeline import AcquisitionPipeline
from devices import (
    QTReader,
    TeledyneDataReader,
    LabJackReader_1,
    LabJackReader_2,
    LakeShoreReader,
    MaxiGaugeReader,
    IVCReader,
)

logger = logging.getLogger(__name__)
STATUS_SYMBOLS = {"success": "✅", "warning": "⚠️", "error": "❌", "none": "⏸️"}

_USE_COLOR = sys.stdout.isatty()
_RESET = "\033[0m" if _USE_COLOR else ""
_GREEN = "\033[92m" if _USE_COLOR else ""
_YELLOW = "\033[93m" if _USE_COLOR else ""
_RED = "\033[91m" if _USE_COLOR else ""
_DIM = "\033[90m" if _USE_COLOR else ""
_BOLD = "\033[1m" if _USE_COLOR else ""
_CYAN = "\033[96m" if _USE_COLOR else ""


def setup_logging(verbose: bool = False, terminal: bool = False) -> None:
    os.makedirs("logs", exist_ok=True)
    fmt_file = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    fmt_console = "%(asctime)s - %(levelname)s - %(message)s"
    handlers = []
    fh = logging.FileHandler("logs/data_acquisition.log")
    fh.setFormatter(logging.Formatter(fmt_file))
    handlers.append(fh)
    if verbose:
        dh = logging.FileHandler("logs/data_acquisition_debug.log")
        dh.setFormatter(logging.Formatter(fmt_file))
        handlers.append(dh)
    if terminal:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(logging.Formatter(fmt_console))
        handlers.append(ch)
    logging.basicConfig(level=logging.DEBUG, handlers=handlers, force=True)


# Device display config: (key, short_label, description)
_DEVICE_ROWS = [
    ("qt", "QT (PLC)", "Flow controllers & sensors"),
    ("teledyne", "Teledyne", "Flow meters"),
    ("labjack_1", "LabJack 1", "Pressures & thermocouple"),
    ("labjack_2", "LabJack 2", "Flow & magnet temps"),
    ("lakeshore_ts", "LakeShore TS", "Target stick temp"),
    ("lakeshore_ft", "LakeShore FT", "Fridge temp"),
    ("lakeshore_mt", "LakeShore MT", "Magnet temp"),
    ("maxigauge", "MaxiGauge", "Vacuum gauges"),
    ("ivc", "IVC", "Ion pump pressure"),
]

_START_TIME: float = 0.0
_STATUS_FIRST = True  


def _status_color(s: str) -> str:
    if s == "success":
        return f"{_GREEN}{STATUS_SYMBOLS['success']}{_RESET}"
    if s == "warning":
        return f"{_YELLOW}{STATUS_SYMBOLS['warning']}{_RESET}"
    if s == "error":
        return f"{_RED}{STATUS_SYMBOLS['error']}{_RESET}"
    return f"{_DIM}{STATUS_SYMBOLS['none']}{_RESET}"


def _print_header() -> None:
    from datetime import datetime
    import pytz
    est = pytz.timezone("America/New_York")
    t = datetime.now(est).strftime("%Y-%m-%d %H:%M:%S")
    w = 60
    print()
    print(f"{_BOLD}{_CYAN}{'═' * w}{_RESET}")
    print(f"{_BOLD}{_CYAN}  UVA Lab Data Acquisition System{_RESET}")
    print(f"{_BOLD}{_CYAN}{'═' * w}{_RESET}")
    print(f"  {_DIM}Started: {t}  │  MariaDB  │  logs/data_acquisition.log{_RESET}")
    print(f"{_BOLD}{_CYAN}{'─' * w}{_RESET}")
    print()


def _format_uptime(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"


def _print_status(iteration: int, status: dict) -> None:
    from datetime import datetime
    import pytz
    est = pytz.timezone("America/New_York")
    now = datetime.now(est).strftime("%H:%M:%S")
    uptime = _format_uptime(time.monotonic() - _START_TIME)
    ok = sum(1 for s in status.values() if s == "success")
    total = len(status)

    lines = []
    lines.append(f"  {_BOLD}Cycle {iteration}{_RESET}  │  {_CYAN}{now}{_RESET}  │  Uptime: {uptime}  │  {_GREEN}{ok}/{total} OK{_RESET}")
    lines.append("")
    for key, label, desc in _DEVICE_ROWS:
        s = status.get(key, "none")
        icon = _status_color(s)
        state = "OK" if s == "success" else ("Error" if s == "error" else "Idle")
        lines.append(f"    {icon}  {label:14}  {_DIM}{desc:28}{_RESET}  {state}")
    lines.append("")
    lines.append(f"  {_DIM}Press Ctrl+C to stop{_RESET}")

    global _STATUS_FIRST
    block_height = len(lines)
    clear = ("\033[F" * (block_height - 1)) if (_USE_COLOR and not _STATUS_FIRST) else ""
    _STATUS_FIRST = False
    out = clear + "\n".join(lines)
    print(out, end="", flush=True)


async def run_standalone() -> None:
    parser = argparse.ArgumentParser(description="Data Acquisition System")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    parser.add_argument("--terminal-log", action="store_true", help="Show logs in terminal")
    args = parser.parse_args()

    setup_logging(verbose=args.verbose, terminal=args.terminal_log)
    shutdown = asyncio.Event()

    def on_signal(sig, frame):
        logger.info(f"Signal {sig}, shutting down")
        shutdown.set()

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    if not args.verbose and not args.terminal_log:
        _print_header()
        global _START_TIME
        _START_TIME = time.monotonic()

    # Loader
    loader = MariaDBLoader(DATABASE_FILE)
    loader.connect()

    # Device readers
    readers = {}
    try:
        readers["qt"] = QTReader(plc_ip=PLC_IP, unit_id=UNIT_ID, int_port=INT_PORT, float_port=FLOAT_PORT,
                                 num_reg_to_read=NUM_REG_TO_READ, labels=QT_LABELS)
        readers["teledyne"] = TeledyneDataReader(TELEDYNE_CHECK_INTERVAL)
        readers["teledyne"].start()
        readers["labjack_1"] = LabJackReader_1(LABJACK_CHECK_INTERVAL)
        readers["labjack_1"].start()
        readers["labjack_2"] = LabJackReader_2(LABJACK_CHECK_INTERVAL)
        readers["labjack_2"].start()
        readers["lakeshore_ts"] = LakeShoreReader(port=LAKESHORE_PORTS["target_stick"])
        readers["lakeshore_ts"].start()
        readers["lakeshore_ft"] = LakeShoreReader(port=LAKESHORE_PORTS["fridge_temp"])
        readers["lakeshore_ft"].start()
        readers["lakeshore_mt"] = LakeShoreReader(port=LAKESHORE_PORTS["magnet_temp"])
        readers["lakeshore_mt"].start()
        readers["maxigauge"] = MaxiGaugeReader()
        readers["maxigauge"].start()
        readers["ivc"] = IVCReader(port=IVC_PORT)
        readers["ivc"].start()
    except Exception as e:
        logger.error(f"Failed to init readers: {e}")
        loader.close()
        return

    # Extractors: sync callables
    extractors = {
        "qt": lambda: readers["qt"].read_qt_data(),
        "teledyne": lambda: readers["teledyne"].get_latest_data(),
        "labjack_1": lambda: readers["labjack_1"].get_latest_data(),
        "labjack_2": lambda: readers["labjack_2"].get_latest_data(),
        "lakeshore_ts": lambda: readers["lakeshore_ts"].get_latest_data(),
        "lakeshore_ft": lambda: readers["lakeshore_ft"].get_latest_data(),
        "lakeshore_mt": lambda: readers["lakeshore_mt"].get_latest_data(),
        "maxigauge": lambda: readers["maxigauge"].get_latest_data(),
        "ivc": lambda: readers["ivc"].get_latest_data(),
    }

    pipeline = AcquisitionPipeline(loader, extractors)
    iteration = 0

    try:
        while not shutdown.is_set():
            try:
                iteration += 1
                status = await pipeline.run_once()

                if not args.verbose and not args.terminal_log:
                    _print_status(iteration, status)

                success = sum(1 for s in status.values() if s == "success")
                logger.info(f"Cycle {iteration}: {success}/{len(status)} sources OK")

            except Exception as e:
                logger.error(f"Cycle error: {e}")
                if not args.verbose and not args.terminal_log:
                    _print_status(iteration, {k: "error" for k in extractors})

            if not shutdown.is_set():
                await asyncio.sleep(SLEEP_INTERVAL)

    finally:
        logger.info("Shutting down...")
        for r in [readers.get("teledyne"), readers.get("labjack_1"), readers.get("labjack_2"),
                  readers.get("lakeshore_ts"), readers.get("lakeshore_ft"), readers.get("lakeshore_mt"),
                  readers.get("maxigauge"), readers.get("ivc")]:
            if r and hasattr(r, "stop"):
                r.stop()
        if readers.get("qt") and hasattr(readers["qt"], "close_connections"):
            readers["qt"].close_connections()
        loader.close()
        if not args.verbose and not args.terminal_log:
            print("\n\n✅ Shutdown complete")


if __name__ == "__main__":
    asyncio.run(run_standalone())
