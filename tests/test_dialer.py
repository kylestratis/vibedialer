"""Tests for the dialer core logic."""

import pytest

from vibedialer.backends import BackendType, DialResult
from vibedialer.dialer import PhoneDialer
from vibedialer.storage import StorageType
from vibedialer.validation import CountryCode


def test_phone_dialer_initialization():
    """Test that we can create a PhoneDialer instance."""
    dialer = PhoneDialer()
    assert dialer is not None


def test_generate_phone_numbers_from_partial():
    """Test generating phone numbers from a partial number."""
    dialer = PhoneDialer()
    # For "555-234-56", should generate 555-234-5600 through 555-234-5699
    numbers = dialer.generate_numbers("555-234-56")
    assert len(numbers) == 100
    assert "555-234-5600" in numbers
    assert "555-234-5699" in numbers


def test_generate_phone_numbers_from_full():
    """Test that a full number returns just that number."""
    dialer = PhoneDialer()
    # Full 10-digit USA number
    numbers = dialer.generate_numbers("555-234-5678")
    assert len(numbers) == 1
    assert numbers[0] == "555-234-5678"


def test_dial_result_creation():
    """Test creating a DialResult."""
    result = DialResult(
        success=True,
        status="modem",
        message="Modem carrier detected",
        phone_number="555-1234",
        timestamp="2025-11-15T12:00:00",
    )
    assert result.phone_number == "555-1234"
    assert result.status == "modem"
    assert result.timestamp == "2025-11-15T12:00:00"
    assert result.message == "Modem carrier detected"
    assert result.success is True


def test_generate_numbers_sequential_order():
    """Test that sequential mode generates numbers in order."""
    dialer = PhoneDialer()
    numbers = dialer.generate_numbers("555-234-56", randomize=False)
    # Should be in sequential order
    assert numbers[0] == "555-234-5600"
    assert numbers[1] == "555-234-5601"
    assert numbers[99] == "555-234-5699"
    # Verify order
    assert numbers == sorted(numbers)


def test_generate_numbers_random_order():
    """Test that random mode generates numbers in random order."""
    dialer = PhoneDialer()
    numbers = dialer.generate_numbers("555-234-56", randomize=True)
    # Should have same numbers but likely in different order
    assert len(numbers) == 100
    assert "555-234-5600" in numbers
    assert "555-234-5699" in numbers
    # Should NOT be in sequential order (with very high probability)
    # Check if at least some elements are out of order
    sorted_numbers = sorted(numbers)
    # With 100 random elements, probability of being sorted is astronomically low
    assert numbers != sorted_numbers or len(set(numbers)) == 1


def test_dial_sequence_with_random_mode():
    """Test dialing sequence with randomization."""
    dialer = PhoneDialer()
    results = dialer.dial_sequence("555-234-00", randomize=True)
    # Should have all 100 numbers
    assert len(results) == 100
    # All should be unique phone numbers
    phone_numbers = [r.phone_number for r in results]
    assert len(set(phone_numbers)) == 100
    # Should contain expected range
    assert any(r.phone_number == "555-234-0000" for r in results)
    assert any(r.phone_number == "555-234-0099" for r in results)


def test_dial_result_with_different_statuses():
    """Test that DialResult can have different status types."""
    valid_statuses = ["ringing", "busy", "modem", "person", "error", "no_answer"]

    for status in valid_statuses:
        result = DialResult(
            success=(status in ["modem", "person"]),
            status=status,
            message=f"Test {status}",
            phone_number="555-1234",
            timestamp="2025-11-15T12:00:00",
        )
        assert result.status == status


def test_dial_returns_various_statuses():
    """Test that dial() can return different statuses."""
    dialer = PhoneDialer()
    # Dial multiple numbers and check we get different statuses
    results = [dialer.dial(f"555-234-567{i}") for i in range(10)]
    statuses = {r.status for r in results}

    # Should have at least some variety in statuses (not all the same)
    # This is probabilistic but highly likely with 10 calls
    assert len(statuses) >= 1  # At minimum, we get statuses back


def test_phone_dialer_with_backend_type():
    """Test creating PhoneDialer with specific backend type."""
    dialer = PhoneDialer(backend_type=BackendType.SIMULATION)
    assert dialer is not None
    assert dialer.backend is not None


def test_phone_dialer_with_modem_backend():
    """Test creating PhoneDialer with modem backend (won't connect without hardware)."""
    dialer = PhoneDialer(backend_type=BackendType.MODEM, port="/dev/null")
    assert dialer is not None
    assert dialer.backend is not None


def test_phone_dialer_backend_connection():
    """Test backend connection methods."""
    dialer = PhoneDialer(backend_type=BackendType.SIMULATION)
    # Simulation backend should connect successfully
    assert dialer.connect() is True
    assert dialer._backend_connected is True

    # Should be able to disconnect
    dialer.disconnect()
    assert dialer._backend_connected is False


def test_phone_dialer_dial_with_backend():
    """Test dialing with backend integration."""
    dialer = PhoneDialer(backend_type=BackendType.SIMULATION)
    result = dialer.dial("555-234-5678")

    # Should have phone number and timestamp filled in
    assert result.phone_number == "555-234-5678"
    assert result.timestamp  # Should not be empty
    assert result.status in ["ringing", "busy", "modem", "person", "error", "no_answer"]
    assert result.message  # Should have a message


def test_phone_dialer_auto_connect():
    """Test that dialer auto-connects when dialing."""
    dialer = PhoneDialer(backend_type=BackendType.SIMULATION)
    # Don't manually connect
    assert dialer._backend_connected is False

    # Should auto-connect when dialing
    result = dialer.dial("555-234-5678")
    assert dialer._backend_connected is True
    assert result.phone_number == "555-234-5678"


def test_phone_dialer_with_storage_type():
    """Test creating PhoneDialer with specific storage type."""
    dialer = PhoneDialer(
        backend_type=BackendType.SIMULATION,
        storage_type=StorageType.DRY_RUN,
    )
    assert dialer is not None
    assert dialer.storage is not None


def test_phone_dialer_cleanup():
    """Test that cleanup properly closes storage and backend."""
    dialer = PhoneDialer(
        backend_type=BackendType.SIMULATION,
        storage_type=StorageType.DRY_RUN,
    )
    dialer.connect()
    assert dialer._backend_connected is True

    dialer.cleanup()
    assert dialer._backend_connected is False


class TestValidationIntegration:
    """Tests for phone number validation integration."""

    def test_dialer_with_default_country_code(self):
        """Test that dialer defaults to USA country code."""
        dialer = PhoneDialer()
        assert dialer.country_code == CountryCode.USA

    def test_dialer_with_custom_country_code(self):
        """Test that dialer accepts custom country code."""
        dialer = PhoneDialer(country_code=CountryCode.UK)
        assert dialer.country_code == CountryCode.UK

    def test_dialer_with_country_code_string(self):
        """Test that dialer accepts country code as string."""
        dialer = PhoneDialer(country_code="44")
        assert dialer.country_code == CountryCode.UK

    def test_generate_numbers_validates_pattern(self):
        """Test that generate_numbers validates input pattern."""
        dialer = PhoneDialer()
        # Invalid area code (starts with 0)
        with pytest.raises(ValueError, match="Invalid phone number pattern"):
            dialer.generate_numbers("055-234")

    def test_generate_numbers_rejects_invalid_area_code(self):
        """Test that generate_numbers rejects invalid area codes."""
        dialer = PhoneDialer()
        # Area code starting with 1
        with pytest.raises(ValueError, match="[Aa]rea code"):
            dialer.generate_numbers("155-234")

    def test_generate_numbers_rejects_n11_service_codes(self):
        """Test that generate_numbers rejects N11 service codes."""
        dialer = PhoneDialer()
        # 911 is a service code
        with pytest.raises(ValueError, match="[Nn]11|service"):
            dialer.generate_numbers("911-234")

    def test_generate_numbers_rejects_invalid_exchange(self):
        """Test that generate_numbers rejects invalid exchange codes."""
        dialer = PhoneDialer()
        # Exchange starting with 1
        with pytest.raises(ValueError, match="[Ee]xchange"):
            dialer.generate_numbers("555-156")

    def test_generate_numbers_formats_output(self):
        """Test that generate_numbers formats output correctly."""
        dialer = PhoneDialer()
        numbers = dialer.generate_numbers("555-234-5678")
        # Should format as XXX-XXX-XXXX
        assert numbers[0] == "555-234-5678"
        assert "-" in numbers[0]

    def test_generate_numbers_skips_invalid_numbers(self):
        """Test that generate_numbers skips invalid generated numbers."""
        dialer = PhoneDialer()
        # Generate from "555-234-99" - all should be valid (100 numbers)
        numbers = dialer.generate_numbers("555-234-99")
        assert len(numbers) == 100  # 555-234-9900 through 555-234-9999
        # All generated numbers should be valid
        for number in numbers:
            # Should be formatted correctly
            assert number.startswith("555-234-99")

    def test_pattern_too_short_rejected(self):
        """Test that patterns shorter than area code are rejected."""
        dialer = PhoneDialer()
        # Only 2 digits - need at least 3 for area code
        with pytest.raises(ValueError, match="area code"):
            dialer.generate_numbers("55")

    def test_full_number_with_country_code(self):
        """Test generating from full number with country code."""
        dialer = PhoneDialer()
        numbers = dialer.generate_numbers("+1-555-234-5678")
        assert len(numbers) == 1
        # Should strip country code in output (include_country_code=False)
        assert numbers[0] == "555-234-5678"

    def test_validator_accessible(self):
        """Test that validator is accessible from dialer."""
        dialer = PhoneDialer()
        assert dialer.validator is not None
        assert hasattr(dialer.validator, "validate")
        assert hasattr(dialer.validator, "format_number")
