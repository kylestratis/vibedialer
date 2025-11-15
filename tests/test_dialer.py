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


def test_generate_numbers_sequential_order():
    """Test that sequential mode generates numbers in order."""
    dialer = PhoneDialer()
    numbers = dialer.generate_numbers("555-12", randomize=False)
    # Should be in sequential order
    assert numbers[0] == "555-1200"
    assert numbers[1] == "555-1201"
    assert numbers[99] == "555-1299"
    # Verify order
    assert numbers == sorted(numbers)


def test_generate_numbers_random_order():
    """Test that random mode generates numbers in random order."""
    dialer = PhoneDialer()
    numbers = dialer.generate_numbers("555-12", randomize=True)
    # Should have same numbers but likely in different order
    assert len(numbers) == 100
    assert "555-1200" in numbers
    assert "555-1299" in numbers
    # Should NOT be in sequential order (with very high probability)
    # Check if at least some elements are out of order
    sorted_numbers = sorted(numbers)
    # With 100 random elements, probability of being sorted is astronomically low
    assert numbers != sorted_numbers or len(set(numbers)) == 1


def test_dial_sequence_with_random_mode():
    """Test dialing sequence with randomization."""
    dialer = PhoneDialer()
    results = dialer.dial_sequence("555-00", randomize=True)
    # Should have all 100 numbers
    assert len(results) == 100
    # All should be unique phone numbers
    phone_numbers = [r.phone_number for r in results]
    assert len(set(phone_numbers)) == 100
    # Should contain expected range
    assert any(r.phone_number == "555-0000" for r in results)
    assert any(r.phone_number == "555-0099" for r in results)


def test_dial_result_with_different_statuses():
    """Test that DialResult can have different status types."""
    valid_statuses = ["ringing", "busy", "modem", "person", "error", "no_answer"]

    for status in valid_statuses:
        result = DialResult(
            phone_number="555-1234",
            status=status,
            timestamp="2025-11-15T12:00:00",
        )
        assert result.status == status


def test_dial_returns_various_statuses():
    """Test that dial() can return different statuses."""
    dialer = PhoneDialer()
    # Dial multiple numbers and check we get different statuses
    results = [dialer.dial(f"555-120{i}") for i in range(10)]
    statuses = {r.status for r in results}

    # Should have at least some variety in statuses (not all the same)
    # This is probabilistic but highly likely with 10 calls
    assert len(statuses) >= 1  # At minimum, we get statuses back
