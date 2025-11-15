"""SQLite database storage backend for dial results."""

import logging
import sqlite3
from pathlib import Path

from vibedialer.backends import DialResult
from vibedialer.storage import ResultStorage

logger = logging.getLogger(__name__)


class SQLiteStorage(ResultStorage):
    """SQLite database storage backend."""

    def __init__(self, database: str = "vibedialer_results.db"):
        """
        Initialize SQLite storage.

        Args:
            database: Path to SQLite database file
        """
        self.database = database
        self.connection = None
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize the SQLite database and create tables if needed."""
        db_path = Path(self.database)
        db_exists = db_path.exists()

        # Connect to database
        self.connection = sqlite3.connect(self.database)
        cursor = self.connection.cursor()

        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dial_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                message TEXT,
                carrier_detected BOOLEAN,
                tone_type TEXT
            )
        """)

        # Create index on phone_number for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_phone_number
            ON dial_results(phone_number)
        """)

        # Create index on timestamp for time-based queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON dial_results(timestamp)
        """)

        # Create index on status for filtering
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status
            ON dial_results(status)
        """)

        self.connection.commit()

        if not db_exists:
            logger.info(f"Created new SQLite database: {self.database}")
        else:
            logger.info(f"Opened existing SQLite database: {self.database}")

    def save_result(self, result: DialResult) -> None:
        """
        Save a single dial result to the database.

        Args:
            result: DialResult to save
        """
        if not self.connection:
            logger.error("Database connection not initialized")
            return

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO dial_results
            (phone_number, status, timestamp, success, message,
             carrier_detected, tone_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                result.phone_number,
                result.status,
                result.timestamp,
                result.success,
                result.message,
                result.carrier_detected,
                result.tone_type,
            ),
        )

        logger.debug(f"Saved result to database: {result.phone_number}")

    def save_results(self, results: list[DialResult]) -> None:
        """
        Save multiple dial results to the database.

        Args:
            results: List of DialResults to save
        """
        if not self.connection:
            logger.error("Database connection not initialized")
            return

        cursor = self.connection.cursor()
        data = [
            (
                result.phone_number,
                result.status,
                result.timestamp,
                result.success,
                result.message,
                result.carrier_detected,
                result.tone_type,
            )
            for result in results
        ]

        cursor.executemany(
            """
            INSERT INTO dial_results
            (phone_number, status, timestamp, success, message,
             carrier_detected, tone_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            data,
        )

        self.connection.commit()
        logger.info(f"Saved {len(results)} results to database")

    def flush(self) -> None:
        """Commit any pending transactions."""
        if self.connection:
            self.connection.commit()
            logger.debug("Committed database transactions")

    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.flush()
            self.connection.close()
            self.connection = None
            logger.info(f"Closed database: {self.database}")
