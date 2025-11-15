"""Tests for storage backends."""

import csv
import sqlite3
import tempfile
from pathlib import Path

import pytest

from vibedialer.backends import DialResult
from vibedialer.csv_storage import CSVStorage
from vibedialer.sqlite_storage import SQLiteStorage
from vibedialer.storage import DryRunStorage, StorageType, create_storage


@pytest.fixture
def sample_result():
    """Create a sample DialResult for testing."""
    return DialResult(
        success=True,
        status="modem",
        message="Modem carrier detected",
        carrier_detected=True,
        tone_type="modem",
        phone_number="555-1234",
        timestamp="2025-11-15T12:00:00",
    )


@pytest.fixture
def sample_results():
    """Create multiple sample DialResults for testing."""
    return [
        DialResult(
            success=True,
            status="modem",
            message="Modem detected",
            phone_number="555-1234",
            timestamp="2025-11-15T12:00:00",
        ),
        DialResult(
            success=False,
            status="busy",
            message="Busy signal",
            phone_number="555-1235",
            timestamp="2025-11-15T12:01:00",
        ),
        DialResult(
            success=False,
            status="no_answer",
            message="No answer",
            phone_number="555-1236",
            timestamp="2025-11-15T12:02:00",
        ),
    ]


# DryRunStorage tests


def test_dry_run_storage_creation():
    """Test creating a dry-run storage backend."""
    storage = DryRunStorage()
    assert storage is not None
    assert storage.result_count == 0


def test_dry_run_storage_save_result(sample_result):
    """Test saving a result in dry-run mode."""
    storage = DryRunStorage()
    storage.save_result(sample_result)
    assert storage.result_count == 1


def test_dry_run_storage_save_multiple(sample_results):
    """Test saving multiple results in dry-run mode."""
    storage = DryRunStorage()
    storage.save_results(sample_results)
    assert storage.result_count == 3


def test_dry_run_storage_flush():
    """Test flushing dry-run storage."""
    storage = DryRunStorage()
    storage.flush()  # Should not raise


def test_dry_run_storage_close(sample_result):
    """Test closing dry-run storage."""
    storage = DryRunStorage()
    storage.save_result(sample_result)
    storage.close()  # Should not raise


# CSVStorage tests


def test_csv_storage_creation():
    """Test creating a CSV storage backend."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        csv_file = f.name

    try:
        storage = CSVStorage(filename=csv_file)
        assert storage is not None
        assert Path(csv_file).exists()
        storage.close()
    finally:
        Path(csv_file).unlink(missing_ok=True)


def test_csv_storage_creates_header():
    """Test that CSV storage creates a header row."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        csv_file = f.name

    try:
        storage = CSVStorage(filename=csv_file)
        storage.close()

        with open(csv_file) as f:
            reader = csv.reader(f)
            header = next(reader)
            assert "phone_number" in header
            assert "status" in header
            assert "timestamp" in header
    finally:
        Path(csv_file).unlink(missing_ok=True)


def test_csv_storage_save_result(sample_result):
    """Test saving a result to CSV."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        csv_file = f.name

    try:
        storage = CSVStorage(filename=csv_file)
        storage.save_result(sample_result)
        storage.close()

        with open(csv_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["phone_number"] == "555-1234"
            assert rows[0]["status"] == "modem"
            assert rows[0]["success"] == "True"
    finally:
        Path(csv_file).unlink(missing_ok=True)


def test_csv_storage_save_multiple(sample_results):
    """Test saving multiple results to CSV."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        csv_file = f.name

    try:
        storage = CSVStorage(filename=csv_file)
        storage.save_results(sample_results)
        storage.close()

        with open(csv_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 3
            assert rows[0]["phone_number"] == "555-1234"
            assert rows[1]["phone_number"] == "555-1235"
            assert rows[2]["phone_number"] == "555-1236"
    finally:
        Path(csv_file).unlink(missing_ok=True)


def test_csv_storage_append_mode(sample_results):
    """Test that CSV storage appends to existing file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        csv_file = f.name

    try:
        # First session
        storage1 = CSVStorage(filename=csv_file)
        storage1.save_result(sample_results[0])
        storage1.close()

        # Second session
        storage2 = CSVStorage(filename=csv_file)
        storage2.save_result(sample_results[1])
        storage2.close()

        # Verify both results are there
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
    finally:
        Path(csv_file).unlink(missing_ok=True)


# SQLiteStorage tests


def test_sqlite_storage_creation():
    """Test creating a SQLite storage backend."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_file = f.name

    try:
        storage = SQLiteStorage(database=db_file)
        assert storage is not None
        assert Path(db_file).exists()
        storage.close()
    finally:
        Path(db_file).unlink(missing_ok=True)


def test_sqlite_storage_creates_table():
    """Test that SQLite storage creates the table."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_file = f.name

    try:
        storage = SQLiteStorage(database=db_file)
        storage.close()

        # Check table exists
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='dial_results'"
        )
        result = cursor.fetchone()
        assert result is not None
        conn.close()
    finally:
        Path(db_file).unlink(missing_ok=True)


def test_sqlite_storage_save_result(sample_result):
    """Test saving a result to SQLite."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_file = f.name

    try:
        storage = SQLiteStorage(database=db_file)
        storage.save_result(sample_result)
        storage.close()

        # Verify data
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT phone_number, status, success FROM dial_results")
        row = cursor.fetchone()
        assert row[0] == "555-1234"
        assert row[1] == "modem"
        assert row[2] == 1  # True
        conn.close()
    finally:
        Path(db_file).unlink(missing_ok=True)


def test_sqlite_storage_save_multiple(sample_results):
    """Test saving multiple results to SQLite."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_file = f.name

    try:
        storage = SQLiteStorage(database=db_file)
        storage.save_results(sample_results)
        storage.close()

        # Verify data
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dial_results")
        count = cursor.fetchone()[0]
        assert count == 3
        conn.close()
    finally:
        Path(db_file).unlink(missing_ok=True)


def test_sqlite_storage_indexes():
    """Test that SQLite storage creates indexes."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_file = f.name

    try:
        storage = SQLiteStorage(database=db_file)
        storage.close()

        # Check indexes exist
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        assert "idx_phone_number" in indexes
        assert "idx_timestamp" in indexes
        assert "idx_status" in indexes
        conn.close()
    finally:
        Path(db_file).unlink(missing_ok=True)


# Factory tests


def test_create_storage_dry_run():
    """Test creating dry-run storage via factory."""
    storage = create_storage(StorageType.DRY_RUN)
    assert isinstance(storage, DryRunStorage)


def test_create_storage_csv():
    """Test creating CSV storage via factory."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        csv_file = f.name

    try:
        storage = create_storage(StorageType.CSV, filename=csv_file)
        assert isinstance(storage, CSVStorage)
        storage.close()
    finally:
        Path(csv_file).unlink(missing_ok=True)


def test_create_storage_sqlite():
    """Test creating SQLite storage via factory."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_file = f.name

    try:
        storage = create_storage(StorageType.SQLITE, database=db_file)
        assert isinstance(storage, SQLiteStorage)
        storage.close()
    finally:
        Path(db_file).unlink(missing_ok=True)


def test_create_storage_default_filenames():
    """Test that factory uses default filenames."""
    # CSV default
    storage_csv = create_storage(StorageType.CSV)
    assert isinstance(storage_csv, CSVStorage)
    assert storage_csv.filename == "vibedialer_results.csv"
    storage_csv.close()
    Path("vibedialer_results.csv").unlink(missing_ok=True)

    # SQLite default
    storage_sqlite = create_storage(StorageType.SQLITE)
    assert isinstance(storage_sqlite, SQLiteStorage)
    assert storage_sqlite.database == "vibedialer_results.db"
    storage_sqlite.close()
    Path("vibedialer_results.db").unlink(missing_ok=True)
