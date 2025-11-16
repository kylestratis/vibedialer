"""SQLite database storage backend for dial results."""

import logging
import sqlite3
from pathlib import Path

from vibedialer.backends import DialResult
from vibedialer.session import SessionMetadata
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

        # Create dial_results table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dial_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                message TEXT,
                carrier_detected BOOLEAN,
                tone_type TEXT
            )
        """)

        # Create sessions table for session metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                backend_type TEXT,
                storage_type TEXT,
                phone_pattern TEXT,
                total_calls INTEGER DEFAULT 0,
                successful_calls INTEGER DEFAULT 0,
                modem_detections INTEGER DEFAULT 0,
                country_code TEXT,
                randomized BOOLEAN
            )
        """)

        # Create indexes for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id
            ON dial_results(session_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_phone_number
            ON dial_results(phone_number)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON dial_results(timestamp)
        """)

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
            (session_id, phone_number, status, timestamp, success, message,
             carrier_detected, tone_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                result.session_id,
                result.phone_number,
                result.status,
                result.timestamp,
                result.success,
                result.message,
                result.carrier_detected,
                result.tone_type,
            ),
        )

        logger.debug(
            f"Saved result to database: {result.phone_number} "
            f"(session: {result.session_id})"
        )

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
                result.session_id,
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
            (session_id, phone_number, status, timestamp, success, message,
             carrier_detected, tone_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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

    def save_session(self, session: SessionMetadata) -> None:
        """
        Save session metadata to the database.

        Args:
            session: SessionMetadata to save
        """
        if not self.connection:
            logger.error("Database connection not initialized")
            return

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO sessions
            (session_id, start_time, end_time, backend_type, storage_type,
             phone_pattern, total_calls, successful_calls, modem_detections,
             country_code, randomized)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                session.session_id,
                session.start_time,
                session.end_time,
                session.backend_type,
                session.storage_type,
                session.phone_pattern,
                session.total_calls,
                session.successful_calls,
                session.modem_detections,
                session.country_code,
                session.randomized,
            ),
        )

        self.connection.commit()
        logger.info(f"Saved session metadata: {session.session_id}")

    def get_session(self, session_id: str) -> SessionMetadata | None:
        """
        Retrieve session metadata by session ID.

        Args:
            session_id: Session ID to look up

        Returns:
            SessionMetadata if found, None otherwise
        """
        if not self.connection:
            logger.error("Database connection not initialized")
            return None

        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT session_id, start_time, end_time, backend_type, storage_type,
                   phone_pattern, total_calls, successful_calls, modem_detections,
                   country_code, randomized
            FROM sessions
            WHERE session_id = ?
        """,
            (session_id,),
        )

        row = cursor.fetchone()
        if row:
            return SessionMetadata(
                session_id=row[0],
                start_time=row[1],
                end_time=row[2],
                backend_type=row[3],
                storage_type=row[4],
                phone_pattern=row[5],
                total_calls=row[6],
                successful_calls=row[7],
                modem_detections=row[8],
                country_code=row[9],
                randomized=bool(row[10]),
            )
        return None

    def get_latest_session_id(self) -> str | None:
        """
        Get the most recent session ID from the database.

        Returns:
            Latest session ID if found, None if no sessions exist
        """
        if not self.connection:
            logger.error("Database connection not initialized")
            return None

        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT session_id
            FROM sessions
            ORDER BY start_time DESC
            LIMIT 1
        """
        )

        row = cursor.fetchone()
        return row[0] if row else None

    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.flush()
            self.connection.close()
            self.connection = None
            logger.info(f"Closed database: {self.database}")
