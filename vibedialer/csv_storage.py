"""CSV storage backend for dial results."""

import csv
import logging
from pathlib import Path

from vibedialer.backends import DialResult
from vibedialer.storage import ResultStorage

logger = logging.getLogger(__name__)


class CSVStorage(ResultStorage):
    """CSV file storage backend."""

    def __init__(self, filename: str = "vibedialer_results.csv"):
        """
        Initialize CSV storage.

        Args:
            filename: Path to CSV file for storing results
        """
        self.filename = filename
        self.file_handle = None
        self.csv_writer = None
        self._initialize_file()

    def _initialize_file(self) -> None:
        """Initialize the CSV file with headers if it doesn't exist."""
        file_path = Path(self.filename)
        file_exists = file_path.exists()

        # Open file in append mode
        self.file_handle = open(self.filename, "a", newline="", encoding="utf-8")
        self.csv_writer = csv.writer(self.file_handle)

        # Write header if file is new
        if not file_exists or file_path.stat().st_size == 0:
            self.csv_writer.writerow(
                [
                    "phone_number",
                    "status",
                    "timestamp",
                    "success",
                    "message",
                    "carrier_detected",
                    "tone_type",
                ]
            )
            self.file_handle.flush()
            logger.info(f"Created new CSV file: {self.filename}")

    def save_result(self, result: DialResult) -> None:
        """
        Save a single dial result to CSV.

        Args:
            result: DialResult to save
        """
        if not self.csv_writer:
            logger.error("CSV writer not initialized")
            return

        self.csv_writer.writerow(
            [
                result.phone_number,
                result.status,
                result.timestamp,
                result.success,
                result.message,
                result.carrier_detected,
                result.tone_type or "",
            ]
        )
        logger.debug(f"Saved result to CSV: {result.phone_number}")

    def save_results(self, results: list[DialResult]) -> None:
        """
        Save multiple dial results to CSV.

        Args:
            results: List of DialResults to save
        """
        for result in results:
            self.save_result(result)
        self.flush()

    def flush(self) -> None:
        """Flush buffered data to disk."""
        if self.file_handle:
            self.file_handle.flush()
            logger.debug("Flushed CSV data to disk")

    def close(self) -> None:
        """Close the CSV file."""
        if self.file_handle:
            self.flush()
            self.file_handle.close()
            self.file_handle = None
            self.csv_writer = None
            logger.info(f"Closed CSV file: {self.filename}")
