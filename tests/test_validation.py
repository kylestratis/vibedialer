"""Tests for phone number validation module."""

from vibedialer.validation import (
    CountryCode,
    PhoneNumberValidator,
    get_validator,
)


class TestPhoneNumberValidator:
    """Tests for PhoneNumberValidator class."""

    def test_validator_initialization(self):
        """Test that validator initializes with default USA country code."""
        validator = PhoneNumberValidator()
        assert validator.country_code == CountryCode.USA

    def test_validator_initialization_with_country(self):
        """Test that validator initializes with specified country code."""
        validator = PhoneNumberValidator(CountryCode.UK)
        assert validator.country_code == CountryCode.UK

    def test_normalize_number_removes_formatting(self):
        """Test that normalize_number removes dashes and spaces."""
        validator = PhoneNumberValidator()
        assert validator.normalize_number("555-123-4567") == "5551234567"
        assert validator.normalize_number("555 123 4567") == "5551234567"
        assert validator.normalize_number("(555) 123-4567") == "5551234567"

    def test_normalize_number_removes_country_code_prefix(self):
        """Test that normalize_number handles +1 prefix."""
        validator = PhoneNumberValidator()
        assert validator.normalize_number("+1-555-123-4567") == "15551234567"
        assert validator.normalize_number("+15551234567") == "15551234567"

    def test_normalize_number_with_only_digits(self):
        """Test that normalize_number works with plain digits."""
        validator = PhoneNumberValidator()
        assert validator.normalize_number("5551234567") == "5551234567"


class TestUSAValidation:
    """Tests for USA/NANP phone number validation."""

    def test_valid_usa_number(self):
        """Test validation of valid USA phone number."""
        validator = PhoneNumberValidator(CountryCode.USA)
        is_valid, error = validator.validate("555-234-5678")
        assert is_valid
        assert error is None

    def test_valid_usa_number_with_country_code(self):
        """Test validation of USA number with +1 prefix."""
        validator = PhoneNumberValidator(CountryCode.USA)
        is_valid, error = validator.validate("+1-555-234-5678")
        assert is_valid
        assert error is None

    def test_invalid_usa_number_too_short(self):
        """Test that short numbers are rejected."""
        validator = PhoneNumberValidator(CountryCode.USA)
        is_valid, error = validator.validate("555-1234")
        assert not is_valid
        assert "too short" in error.lower()

    def test_invalid_usa_number_too_long(self):
        """Test that long numbers are rejected."""
        validator = PhoneNumberValidator(CountryCode.USA)
        is_valid, error = validator.validate("555-123-456789")
        assert not is_valid
        assert "too long" in error.lower()

    def test_invalid_area_code_starts_with_zero(self):
        """Test that area codes starting with 0 are rejected."""
        validator = PhoneNumberValidator(CountryCode.USA)
        is_valid, error = validator.validate("055-123-4567")
        assert not is_valid
        assert "area code" in error.lower()
        assert "0" in error or "1" in error

    def test_invalid_area_code_starts_with_one(self):
        """Test that area codes starting with 1 are rejected."""
        validator = PhoneNumberValidator(CountryCode.USA)
        is_valid, error = validator.validate("155-234-5678")
        assert not is_valid
        assert "area code" in error.lower()

    def test_invalid_area_code_n11(self):
        """Test that N11 area codes (service codes) are rejected."""
        validator = PhoneNumberValidator(CountryCode.USA)
        # 911 is emergency
        is_valid, error = validator.validate("911-123-4567")
        assert not is_valid
        assert "n11" in error.lower() or "service" in error.lower()

        # 411 is directory assistance
        is_valid, error = validator.validate("411-123-4567")
        assert not is_valid
        assert "n11" in error.lower() or "service" in error.lower()

    def test_invalid_exchange_starts_with_zero(self):
        """Test that exchange codes starting with 0 are rejected."""
        validator = PhoneNumberValidator(CountryCode.USA)
        is_valid, error = validator.validate("555-012-4567")
        assert not is_valid
        assert "exchange" in error.lower()

    def test_invalid_exchange_starts_with_one(self):
        """Test that exchange codes starting with 1 are rejected."""
        validator = PhoneNumberValidator(CountryCode.USA)
        is_valid, error = validator.validate("555-156-7890")
        assert not is_valid
        assert "exchange" in error.lower()

    def test_valid_area_codes(self):
        """Test that valid area codes are accepted."""
        validator = PhoneNumberValidator(CountryCode.USA)

        # Some real USA area codes
        valid_area_codes = ["212", "310", "415", "650", "800", "888"]

        for area_code in valid_area_codes:
            is_valid, error = validator.validate(f"{area_code}-555-4567")
            assert is_valid, (
                f"Area code {area_code} should be valid, got error: {error}"
            )


class TestFormatting:
    """Tests for phone number formatting."""

    def test_format_usa_number_without_country_code(self):
        """Test formatting USA number without country code."""
        validator = PhoneNumberValidator(CountryCode.USA)
        formatted = validator.format_number("5552345678", include_country_code=False)
        assert formatted == "555-234-5678"

    def test_format_usa_number_with_country_code(self):
        """Test formatting USA number with country code."""
        validator = PhoneNumberValidator(CountryCode.USA)
        formatted = validator.format_number("5552345678", include_country_code=True)
        assert formatted == "+1-555-234-5678"

    def test_format_already_formatted_number(self):
        """Test formatting a number that's already formatted."""
        validator = PhoneNumberValidator(CountryCode.USA)
        formatted = validator.format_number("555-234-5678", include_country_code=False)
        assert formatted == "555-234-5678"

    def test_format_invalid_number_returns_none(self):
        """Test that formatting invalid numbers returns None."""
        validator = PhoneNumberValidator(CountryCode.USA)
        formatted = validator.format_number("123")  # Too short
        assert formatted is None

    def test_format_number_with_existing_country_code(self):
        """Test formatting number that already has country code."""
        validator = PhoneNumberValidator(CountryCode.USA)
        formatted = validator.format_number(
            "+1-555-234-5678", include_country_code=True
        )
        assert formatted == "+1-555-234-5678"


class TestPatternValidation:
    """Tests for validating partial phone number patterns."""

    def test_validate_full_pattern(self):
        """Test validating a full 10-digit pattern."""
        validator = PhoneNumberValidator(CountryCode.USA)
        is_valid, error = validator.validate_pattern("555-234-5678")
        assert is_valid
        assert error is None

    def test_validate_partial_pattern_area_code_only(self):
        """Test validating pattern with only area code."""
        validator = PhoneNumberValidator(CountryCode.USA)
        is_valid, error = validator.validate_pattern("555")
        assert is_valid
        assert error is None

    def test_validate_partial_pattern_area_code_and_exchange(self):
        """Test validating pattern with area code and partial exchange."""
        validator = PhoneNumberValidator(CountryCode.USA)
        is_valid, error = validator.validate_pattern("555-12")
        assert is_valid
        assert error is None

    def test_validate_partial_pattern_too_short(self):
        """Test that patterns shorter than area code are rejected."""
        validator = PhoneNumberValidator(CountryCode.USA)
        is_valid, error = validator.validate_pattern("55")
        assert not is_valid
        assert "area code" in error.lower()

    def test_validate_pattern_invalid_area_code(self):
        """Test that patterns with invalid area codes are rejected."""
        validator = PhoneNumberValidator(CountryCode.USA)
        is_valid, error = validator.validate_pattern("055")
        assert not is_valid
        assert "area code" in error.lower()

    def test_validate_pattern_invalid_exchange(self):
        """Test that patterns with invalid exchanges are rejected."""
        validator = PhoneNumberValidator(CountryCode.USA)
        is_valid, error = validator.validate_pattern("555-012")
        assert not is_valid
        assert "exchange" in error.lower()

    def test_validate_pattern_with_dashes(self):
        """Test validating patterns with formatting."""
        validator = PhoneNumberValidator(CountryCode.USA)
        is_valid, error = validator.validate_pattern("555-2345")
        assert is_valid
        assert error is None


class TestGetValidator:
    """Tests for get_validator factory function."""

    def test_get_validator_with_enum(self):
        """Test getting validator with CountryCode enum."""
        validator = get_validator(CountryCode.USA)
        assert validator.country_code == CountryCode.USA

    def test_get_validator_with_string(self):
        """Test getting validator with country code string."""
        validator = get_validator("1")
        assert validator.country_code == CountryCode.USA

    def test_get_validator_with_unknown_code(self):
        """Test getting validator with unknown country code defaults to USA."""
        validator = get_validator("999")
        assert validator.country_code == CountryCode.USA

    def test_get_validator_default(self):
        """Test getting validator with default (USA)."""
        validator = get_validator()
        assert validator.country_code == CountryCode.USA


class TestMultipleCountries:
    """Tests for multiple country support."""

    def test_uk_validator_initialization(self):
        """Test that UK validator initializes correctly."""
        validator = PhoneNumberValidator(CountryCode.UK)
        assert validator.country_code == CountryCode.UK
        assert validator.format_spec.country_code == "44"

    def test_germany_validator_initialization(self):
        """Test that Germany validator initializes correctly."""
        validator = PhoneNumberValidator(CountryCode.GERMANY)
        assert validator.country_code == CountryCode.GERMANY
        assert validator.format_spec.country_code == "49"

    def test_uk_number_validation(self):
        """Test basic UK number validation."""
        validator = PhoneNumberValidator(CountryCode.UK)
        # UK numbers are 10 digits after country code
        is_valid, error = validator.validate("2012345678")
        assert is_valid
        assert error is None
