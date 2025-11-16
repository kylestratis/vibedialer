"""Storage implementations for VibeDialer."""

from vibedialer.storage.base import (
    DryRunStorage,
    ResultStorage,
    StorageType,
    create_storage,
)
from vibedialer.storage.csv import CSVStorage
from vibedialer.storage.sqlite import SQLiteStorage

__all__ = [
    "CSVStorage",
    "DryRunStorage",
    "ResultStorage",
    "SQLiteStorage",
    "StorageType",
    "create_storage",
]
