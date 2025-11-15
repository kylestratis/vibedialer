"""Storage backends for saving dial results."""

import logging
from abc import ABC, abstractmethod
from enum import Enum

from vibedialer.backends import DialResult

logger = logging.getLogger(__name__)


class StorageType(Enum):
    """Types of storage backends."""

    CSV = "csv"
    SQLITE = "sqlite"
    DRY_RUN = "dry-run"


class ResultStorage(ABC):
    """Abstract base class for result storage backends."""

    @abstractmethod
    def save_result(self, result: DialResult) -> None:
        """
        Save a single dial result.

        Args:
            result: DialResult to save
        """
        pass

    @abstractmethod
    def save_results(self, results: list[DialResult]) -> None:
        """
        Save multiple dial results.

        Args:
            results: List of DialResults to save
        """
        pass

    @abstractmethod
    def flush(self) -> None:
        """Flush any buffered results to storage."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the storage backend and ensure all data is saved."""
        pass


class DryRunStorage(ResultStorage):
    """Storage backend that doesn't actually save anything (dry-run mode)."""

    def __init__(self):
        """Initialize dry-run storage."""
        self.result_count = 0

    def save_result(self, result: DialResult) -> None:
        """Log the result but don't save it."""
        self.result_count += 1
        logger.debug(
            f"[DRY-RUN] Would save result: {result.phone_number} - {result.status}"
        )

    def save_results(self, results: list[DialResult]) -> None:
        """Log the results but don't save them."""
        for result in results:
            self.save_result(result)

    def flush(self) -> None:
        """Nothing to flush in dry-run mode."""
        logger.debug(f"[DRY-RUN] Would flush {self.result_count} results")

    def close(self) -> None:
        """Nothing to close in dry-run mode."""
        logger.info(
            f"[DRY-RUN] Session complete. {self.result_count} results "
            "would have been saved."
        )


def create_storage(storage_type: StorageType, **kwargs) -> ResultStorage:
    """
    Factory function to create storage backends.

    Args:
        storage_type: Type of storage backend to create
        **kwargs: Backend-specific configuration

    Returns:
        ResultStorage instance

    Raises:
        ValueError: If storage type is invalid
    """
    if storage_type == StorageType.DRY_RUN:
        return DryRunStorage()

    elif storage_type == StorageType.CSV:
        from vibedialer.csv_storage import CSVStorage

        filename = kwargs.get("filename", "vibedialer_results.csv")
        return CSVStorage(filename=filename)

    elif storage_type == StorageType.SQLITE:
        from vibedialer.sqlite_storage import SQLiteStorage

        database = kwargs.get("database", "vibedialer_results.db")
        return SQLiteStorage(database=database)

    else:
        raise ValueError(f"Unknown storage type: {storage_type}")
