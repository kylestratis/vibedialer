"""Tests for resume functionality."""

import tempfile
from pathlib import Path

import pytest

from vibedialer.backends import DialResult
from vibedialer.resume import (
    calculate_remaining_numbers,
    infer_pattern_from_numbers,
    prepare_resume,
    read_dialed_numbers,
    read_dialed_numbers_from_csv,
    read_dialed_numbers_from_sqlite,
)
from vibedialer.storage import SQLiteStorage


@pytest.fixture
def sample_csv_file():
    """Create a sample CSV file with dialed numbers."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as f:
        csv_file = f.name
        f.write(
            "phone_number,status,timestamp,success,message,carrier_detected,tone_type\n"
        )
        f.write("555-234-5600,no_answer,2025-11-15T12:00:00,False,No answer,False,\n")
        f.write("555-234-5601,busy,2025-11-15T12:01:00,False,Busy,False,\n")
        f.write(
            "555-234-5602,modem,2025-11-15T12:02:00,True,Modem detected,True,modem\n"
        )

    yield csv_file
    Path(csv_file).unlink(missing_ok=True)


@pytest.fixture
def sample_sqlite_file():
    """Create a sample SQLite database with dialed numbers."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_file = f.name

    storage = SQLiteStorage(database=db_file)
    results = [
        DialResult(
            success=False,
            status="no_answer",
            message="No answer",
            phone_number="555-234-5600",
            timestamp="2025-11-15T12:00:00",
        ),
        DialResult(
            success=False,
            status="busy",
            message="Busy",
            phone_number="555-234-5601",
            timestamp="2025-11-15T12:01:00",
        ),
        DialResult(
            success=True,
            status="modem",
            message="Modem detected",
            phone_number="555-234-5602",
            timestamp="2025-11-15T12:02:00",
            carrier_detected=True,
            tone_type="modem",
        ),
    ]
    storage.save_results(results)
    storage.close()

    yield db_file
    Path(db_file).unlink(missing_ok=True)


# Tests for reading dialed numbers


def test_read_dialed_numbers_from_csv(sample_csv_file):
    """Test reading dialed numbers from CSV file."""
    numbers = read_dialed_numbers_from_csv(sample_csv_file)

    assert len(numbers) == 3
    assert "555-234-5600" in numbers
    assert "555-234-5601" in numbers
    assert "555-234-5602" in numbers


def test_read_dialed_numbers_from_csv_nonexistent():
    """Test reading from nonexistent CSV file."""
    with pytest.raises(FileNotFoundError):
        read_dialed_numbers_from_csv("nonexistent.csv")


def test_read_dialed_numbers_from_sqlite(sample_sqlite_file):
    """Test reading dialed numbers from SQLite database."""
    numbers = read_dialed_numbers_from_sqlite(sample_sqlite_file)

    assert len(numbers) == 3
    assert "555-234-5600" in numbers
    assert "555-234-5601" in numbers
    assert "555-234-5602" in numbers


def test_read_dialed_numbers_from_sqlite_nonexistent():
    """Test reading from nonexistent SQLite database."""
    with pytest.raises(FileNotFoundError):
        read_dialed_numbers_from_sqlite("nonexistent.db")


def test_read_dialed_numbers_auto_detects_csv(sample_csv_file):
    """Test automatic format detection for CSV."""
    numbers = read_dialed_numbers(sample_csv_file)

    assert len(numbers) == 3
    assert "555-234-5600" in numbers


def test_read_dialed_numbers_auto_detects_sqlite(sample_sqlite_file):
    """Test automatic format detection for SQLite."""
    numbers = read_dialed_numbers(sample_sqlite_file)

    assert len(numbers) == 3
    assert "555-234-5600" in numbers


def test_read_dialed_numbers_unsupported_format():
    """Test reading from unsupported file format."""
    with tempfile.NamedTemporaryFile(suffix=".txt") as f:
        with pytest.raises(ValueError, match="Unsupported file format"):
            read_dialed_numbers(f.name)


# Tests for pattern inference


def test_infer_pattern_simple():
    """Test inferring pattern from simple sequential numbers."""
    numbers = {"555-234-5600", "555-234-5601", "555-234-5602", "555-234-5699"}
    pattern = infer_pattern_from_numbers(numbers)

    assert pattern == "555-234-56"


def test_infer_pattern_full_range():
    """Test inferring pattern from full number range."""
    numbers = {f"555-234-{i:04d}" for i in range(10000)}
    pattern = infer_pattern_from_numbers(numbers)

    assert pattern == "555-234"


def test_infer_pattern_partial_range():
    """Test inferring pattern from partial range."""
    numbers = {"555-234-5634", "555-234-5635", "555-234-5650"}
    pattern = infer_pattern_from_numbers(numbers)

    assert pattern == "555-234-56"


def test_infer_pattern_empty():
    """Test inferring pattern from empty set."""
    pattern = infer_pattern_from_numbers(set())
    assert pattern is None


def test_infer_pattern_single_number():
    """Test inferring pattern from single number."""
    numbers = {"555-234-5634"}
    pattern = infer_pattern_from_numbers(numbers)

    # Single number - pattern inference returns full number
    assert pattern == "555-234-5634"


def test_infer_pattern_scattered_numbers():
    """Test inferring pattern from scattered numbers."""
    numbers = {"555-234-0000", "555-234-5555", "555-234-9999"}
    pattern = infer_pattern_from_numbers(numbers)

    assert pattern == "555-234"


# Tests for calculating remaining numbers


def test_calculate_remaining_numbers():
    """Test calculating remaining numbers to dial."""
    dialed = {"555-234-5600", "555-234-5601", "555-234-5602"}
    remaining = calculate_remaining_numbers("555-234-56", dialed)

    assert len(remaining) == 97  # 100 - 3
    assert "555-234-5600" not in remaining
    assert "555-234-5601" not in remaining
    assert "555-234-5602" not in remaining
    assert "555-234-5603" in remaining
    assert "555-234-5699" in remaining


def test_calculate_remaining_numbers_all_dialed():
    """Test when all numbers have been dialed."""
    dialed = {f"555-234-560{i}" for i in range(10)}
    remaining = calculate_remaining_numbers("555-234-560", dialed)

    assert len(remaining) == 0


def test_calculate_remaining_numbers_none_dialed():
    """Test when no numbers have been dialed."""
    dialed = set()
    remaining = calculate_remaining_numbers("555-234-56", dialed)

    assert len(remaining) == 100


def test_calculate_remaining_numbers_randomize():
    """Test randomizing remaining numbers."""
    dialed = {"555-234-5600"}
    remaining1 = calculate_remaining_numbers("555-234-56", dialed, randomize=False)
    remaining2 = calculate_remaining_numbers("555-234-56", dialed, randomize=True)

    # Same set of numbers
    assert set(remaining1) == set(remaining2)
    # But likely in different order (very high probability)
    assert remaining1 != remaining2 or len(remaining1) <= 1


# Tests for prepare_resume


def test_prepare_resume_with_prefix(sample_csv_file):
    """Test preparing resume with explicit prefix."""
    prefix, remaining, total, dialed = prepare_resume(
        sample_csv_file, prefix="555-234-56", randomize=False
    )

    assert prefix == "555-234-56"
    assert len(remaining) == 97  # 100 - 3
    assert total == 100
    assert dialed == 3
    assert "555-234-5600" not in remaining
    assert "555-234-5603" in remaining


def test_prepare_resume_infer_prefix(sample_csv_file):
    """Test preparing resume with inferred prefix."""
    prefix, remaining, total, dialed = prepare_resume(sample_csv_file, prefix=None)

    assert prefix == "555-234-560"
    assert len(remaining) == 7  # 10 - 3 (555-234-5600 through 555-234-5609)
    assert total == 10
    assert dialed == 3


def test_prepare_resume_randomize(sample_csv_file):
    """Test preparing resume with randomization."""
    prefix1, remaining1, _, _ = prepare_resume(
        sample_csv_file, prefix="555-234-56", randomize=False
    )
    prefix2, remaining2, _, _ = prepare_resume(
        sample_csv_file, prefix="555-234-56", randomize=True
    )

    # Same prefix and set of numbers
    assert prefix1 == prefix2
    assert set(remaining1) == set(remaining2)
    # But likely in different order
    assert remaining1 != remaining2 or len(remaining1) <= 1


def test_prepare_resume_with_sqlite(sample_sqlite_file):
    """Test preparing resume from SQLite database."""
    prefix, remaining, total, dialed = prepare_resume(
        sample_sqlite_file, prefix="555-234-56"
    )

    assert prefix == "555-234-56"
    assert len(remaining) == 97
    assert total == 100
    assert dialed == 3


def test_prepare_resume_nonexistent_file():
    """Test preparing resume from nonexistent file."""
    with pytest.raises(FileNotFoundError):
        prepare_resume("nonexistent.csv", prefix="555-234-56")


def test_prepare_resume_empty_file():
    """Test preparing resume from empty CSV file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as f:
        csv_file = f.name
        f.write(
            "phone_number,status,timestamp,success,message,carrier_detected,tone_type\n"
        )

    try:
        with pytest.raises(ValueError, match="No dialed numbers found"):
            prepare_resume(csv_file, prefix="555-234-56")
    finally:
        Path(csv_file).unlink(missing_ok=True)


def test_prepare_resume_cannot_infer_pattern():
    """Test when pattern cannot be inferred."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as f:
        csv_file = f.name
        f.write(
            "phone_number,status,timestamp,success,message,carrier_detected,tone_type\n"
        )
        f.write("5,no_answer,2025-11-15T12:00:00,False,No answer,False,\n")

    try:
        with pytest.raises(ValueError, match="Could not infer pattern"):
            prepare_resume(csv_file, prefix=None)
    finally:
        Path(csv_file).unlink(missing_ok=True)
