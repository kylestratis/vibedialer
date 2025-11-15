"""Tests for the dialer core logic."""


from vibedialer.dialer import DialResult, PhoneDialer


def test_phone_dialer_initialization():
    """Test that we can create a PhoneDialer instance."""
    dialer = PhoneDialer()
    assert dialer is not None


def test_generate_phone_numbers_from_partial():
    """Test generating phone numbers from a partial number."""
    dialer = PhoneDialer()
    # For "555-12", should generate 555-1200 through 555-1299
    numbers = dialer.generate_numbers("555-12")
    assert len(numbers) == 100
    assert "555-1200" in numbers
    assert "555-1299" in numbers


def test_generate_phone_numbers_from_full():
    """Test that a full number returns just that number."""
    dialer = PhoneDialer()
    # Full 7-digit number (local format)
    numbers = dialer.generate_numbers("555-1234")
    assert len(numbers) == 1
    assert numbers[0] == "555-1234"


def test_dial_result_creation():
    """Test creating a DialResult."""
    result = DialResult(
        phone_number="555-1234",
        status="connected",
        timestamp="2025-11-15T12:00:00",
    )
    assert result.phone_number == "555-1234"
    assert result.status == "connected"
    assert result.timestamp == "2025-11-15T12:00:00"
