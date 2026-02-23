"""
Unified database loader - single INSERT implementation.
Schema-driven, connection-pool based. No scattered insert logic.
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import mariadb

from .schema import TABLE_SCHEMAS

logger = logging.getLogger(__name__)


def db_config(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Pass through config keys directly from the config file."""
    return dict(raw)


class MariaDBLoader:
    """Single loader for all tables. Schema-driven INSERTs."""

    def __init__(self, config_path: str):
        with open(config_path) as f:
            raw = json.load(f)
        db_raw = raw.get("database", raw)
        self._config = db_config(db_raw)
        self._pool: Optional[mariadb.ConnectionPool] = None

    def connect(self, pool_size: int = 10) -> None:
        if self._pool:
            return
        self._pool = mariadb.ConnectionPool(
            pool_name="daq_pool",
            pool_size=pool_size,
            **self._config,
        )
        # Verify
        conn = self._pool.get_connection()
        try:
            conn.cursor().execute("SELECT 1")
        finally:
            conn.close()
        logger.info("MariaDB connection pool initialized")

    def close(self) -> None:
        if self._pool:
            self._pool.close()
            self._pool = None
            logger.info("MariaDB connection pool closed")

    def _get_conn(self):
        if not self._pool:
            raise RuntimeError("Loader not connected")
        return self._pool.get_connection()

    def insert(self, table: str, columns: List[str], values: List[Any]) -> bool:
        """
        Execute INSERT for given table/columns/values.
        values must match columns in order.
        """
        if table not in TABLE_SCHEMAS:
            logger.error(f"Unknown table: {table}")
            return False
        placeholders = ", ".join("?" * len(values))
        cols = ", ".join(f"`{c}`" for c in columns)
        sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        conn = None
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute(sql, values)
            conn.commit()
            logger.debug(f"Inserted into {table}")
            return True
        except mariadb.Error as e:
            logger.error(f"Insert failed {table}: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def insert_row(self, table: str, row: Dict[str, Any], timestamp: Optional[str] = None) -> bool:
        """
        Insert a row dict. Keys must match schema columns.
        If timestamp is provided, it overrides row.get('Timestamp').
        """
        schema_cols = TABLE_SCHEMAS.get(table)
        if not schema_cols:
            logger.error(f"Unknown table: {table}")
            return False
        # Filter to columns we have data for
        cols = [c for c in schema_cols if c in row or (c == "Timestamp" and timestamp)]
        if not cols:
            return False
        ts = timestamp or row.get("Timestamp")
        values = []
        for c in cols:
            if c == "Timestamp":
                values.append(ts)
            else:
                values.append(row.get(c))
        return self.insert(table, cols, values)
