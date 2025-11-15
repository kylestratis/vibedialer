"""Resume functionality for continuing interrupted war dialing sessions."""

import csv
import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


def read_dialed_numbers_from_csv(filename: str) -> set[str]:
    """
    Read already-dialed phone numbers from a CSV file.

    Args:
        filename: Path to CSV file

    Returns:
        Set of phone numbers that have been dialed

    Raises:
        FileNotFoundError: If CSV file doesn't exist
    """
    file_path = Path(filename)
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {filename}")

    dialed = set()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "phone_number" in row:
                dialed.add(row["phone_number"])

    logger.info(f"Read {len(dialed)} already-dialed numbers from {filename}")
    return dialed


def read_dialed_numbers_from_sqlite(database: str) -> set[str]:
    """
    Read already-dialed phone numbers from a SQLite database.

    Args:
        database: Path to SQLite database file

    Returns:
        Set of phone numbers that have been dialed

    Raises:
        FileNotFoundError: If database file doesn't exist
    """
    db_path = Path(database)
    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {database}")

    dialed = set()
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT phone_number FROM dial_results")
        for row in cursor.fetchall():
            dialed.add(row[0])
    finally:
        conn.close()

    logger.info(f"Read {len(dialed)} already-dialed numbers from {database}")
    return dialed


def read_dialed_numbers(filename: str) -> set[str]:
    """
    Read already-dialed phone numbers from a file.

    Automatically detects CSV or SQLite format based on file extension.

    Args:
        filename: Path to results file (.csv or .db)

    Returns:
        Set of phone numbers that have been dialed

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is not supported
    """
    file_path = Path(filename)
    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        return read_dialed_numbers_from_csv(filename)
    elif suffix == ".db":
        return read_dialed_numbers_from_sqlite(filename)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Use .csv or .db files.")


def infer_pattern_from_numbers(numbers: set[str]) -> str | None:
    """
    Infer the phone number pattern from a set of dialed numbers.

    Looks for common prefixes and determines the pattern used for dialing.

    Args:
        numbers: Set of phone numbers

    Returns:
        Inferred pattern (e.g., "555-12") or None if no pattern found

    Examples:
        >>> infer_pattern_from_numbers({"555-1200", "555-1201", "555-1299"})
        "555-12"
        >>> infer_pattern_from_numbers({"555-0000", "555-9999"})
        "555"
    """
    if not numbers:
        return None

    # Convert to list and sort
    number_list = sorted(numbers)

    # Find common prefix by comparing first and last numbers
    first = number_list[0]
    last = number_list[-1]

    # Find common prefix
    common_prefix = ""
    for c1, c2 in zip(first, last, strict=False):
        if c1 == c2:
            common_prefix += c1
        else:
            break

    # Remove trailing dash if present
    if common_prefix.endswith("-"):
        common_prefix = common_prefix[:-1]

    # Try to find the most meaningful pattern by removing trailing digits
    # This helps with cases like "555-1234" (full number) -> "555-12"
    # We want to generate patterns that make sense (10, 100, 1000 numbers)
    clean_prefix = common_prefix.replace("-", "")

    # If the prefix is a full 7-digit number, try to shorten it
    if len(clean_prefix) == 7:  # Full 7-digit number like "555-1234"
        # Try removing last 1-2 digits to find a better pattern
        for trim in [2, 1]:
            if len(common_prefix) > trim:
                candidate = common_prefix[:-trim]
            else:
                candidate = common_prefix
            # Remove trailing dash
            if candidate.endswith("-"):
                candidate = candidate[:-1]
            # Check if this makes sense
            candidate_clean = candidate.replace("-", "")
            if len(candidate_clean) >= 2:
                return candidate

    # If we found a meaningful prefix (at least 2 digits after formatting)
    if len(clean_prefix) >= 2:
        return common_prefix

    return None


def calculate_remaining_numbers(
    prefix: str, dialed: set[str], randomize: bool = False
) -> list[str]:
    """
    Calculate which numbers remain to be dialed.

    Args:
        prefix: Phone number prefix (e.g., "555-12")
        dialed: Set of already-dialed numbers
        randomize: Whether to randomize the remaining numbers

    Returns:
        List of numbers that still need to be dialed
    """
    from vibedialer.dialer import PhoneDialer

    # Generate all numbers for this prefix
    dialer = PhoneDialer()
    all_numbers = dialer.generate_numbers(prefix, randomize=False)

    # Filter out already-dialed numbers
    remaining = [num for num in all_numbers if num not in dialed]

    # Randomize if requested
    if randomize:
        import random

        random.shuffle(remaining)

    logger.info(
        f"Total numbers for '{prefix}': {len(all_numbers)}, "
        f"Already dialed: {len(dialed)}, "
        f"Remaining: {len(remaining)}"
    )

    return remaining


def prepare_resume(
    resume_file: str, prefix: str | None = None, randomize: bool = False
) -> tuple[str, list[str], int, int]:
    """
    Prepare to resume a dialing session.

    Args:
        resume_file: Path to results file to resume from
        prefix: Phone number prefix to resume (or None to infer)
        randomize: Whether to randomize remaining numbers

    Returns:
        Tuple of (inferred_prefix, remaining_numbers, total_count, dialed_count)

    Raises:
        FileNotFoundError: If resume file doesn't exist
        ValueError: If prefix cannot be inferred and none provided
    """
    # Read already-dialed numbers
    dialed = read_dialed_numbers(resume_file)

    if not dialed:
        raise ValueError(f"No dialed numbers found in {resume_file}")

    # Infer prefix if not provided
    if prefix is None:
        prefix = infer_pattern_from_numbers(dialed)
        if prefix is None:
            raise ValueError(
                "Could not infer pattern from dialed numbers. "
                "Please provide a prefix with --resume-prefix"
            )
        logger.info(f"Inferred pattern: {prefix}")

    # Calculate remaining numbers
    remaining = calculate_remaining_numbers(prefix, dialed, randomize)

    total_count = len(remaining) + len(dialed)

    return prefix, remaining, total_count, len(dialed)
