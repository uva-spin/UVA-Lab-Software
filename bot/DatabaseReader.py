import sqlite3
import os
from typing import Any, Optional
from datetime import datetime

class DatabaseReader:
    def __init__(self, db_path: str):
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found or inaccessible: {db_path}")
        
        # Open as read-only
        self.conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        self.cursor = self.conn.cursor()

    def list_tables(self) -> list[str]:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in self.cursor.fetchall()]

    def get_schema(self, table_name: str) -> list[tuple]:
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        return self.cursor.fetchall()

    def get_last_thermocouple_reading(self, table_name: str = "thermocouple") -> Optional[tuple]:
        """
        Returns the latest thermocouple reading from the specified table.
        Assumes there's a timestamp or ID field to sort by.
        """
        try:
            self.cursor.execute(f"""
                SELECT * FROM {table_name}
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def get_latest_value(self, table: str, column: str) -> Optional[Any]:
        """
        Returns the most recent value in a specific column of a table.
        """
        try:
            self.cursor.execute(f"""
                SELECT {column} FROM {table}
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error retrieving value: {e}")
            return None

    def get_last_timestamp(self, table: str) -> Optional[datetime]:
        try:
            self.cursor.execute(f"""
                SELECT timestamp FROM {table}
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            result = self.cursor.fetchone()
            if result and result[0]:
                return datetime.fromisoformat(result[0])
        except Exception as e:
            print(f"Error getting last timestamp from {table}: {e}")
        return None

    def close(self):
        self.conn.close()
