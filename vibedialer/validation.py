"""Phone number validation and formatting for VibeDialer."""

import logging
import re
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CountryCode(Enum):
    """Supported country codes for phone number validation."""

    USA = "1"
    CANADA = "1"  # Same as USA (NANP)
    UK = "44"
    GERMANY = "49"
    FRANCE = "33"
    JAPAN = "81"
    AUSTRALIA = "61"


@dataclass
class PhoneNumberFormat:
    """Phone number format specification for a country."""

    country_code: str
    min_length: int
    max_length: int
    pattern: str | None = None
    description: str = ""


# Format specifications for different countries
FORMATS = {
    CountryCode.USA: PhoneNumberFormat(
        country_code="1",
        min_length=10,
        max_length=10,
        pattern=r"^[2-9]\d{2}[2-9]\d{6}$",
        description="USA/Canada NANP: NXX-NXX-XXXX (N=2-9, X=0-9)",
    ),
    CountryCode.UK: PhoneNumberFormat(
        country_code="44",
        min_length=10,
        max_length=10,
        description="UK: 10 digits after country code",
    ),
    CountryCode.GERMANY: PhoneNumberFormat(
        country_code="49",
        min_length=10,
        max_length=11,
        description="Germany: 10-11 digits after country code",
    ),
}


class PhoneNumberValidator:
    """
    Validates and formats phone numbers according to country-specific rules.

    Supports multiple country codes and formats, with USA/NANP as the default.
    """

    def __init__(self, country_code: CountryCode = CountryCode.USA):
        """
        Initialize validator with a country code.

        Args:
            country_code: Country code to use for validation (default: USA)
        """
        self.country_code = country_code
        self.format_spec = FORMATS.get(
            country_code,
            PhoneNumberFormat(
                country_code=country_code.value,
                min_length=10,
                max_length=15,
                description=f"Country code {country_code.value}",
            ),
        )

    def normalize_number(self, phone_number: str) -> str:
        """
        Normalize a phone number by removing formatting characters.

        Args:
            phone_number: Phone number to normalize

        Returns:
            Phone number with only digits
        """
        # Remove all non-digit characters except leading +
        normalized = re.sub(r"[^\d+]", "", phone_number)

        # Remove leading + if present
        if normalized.startswith("+"):
            normalized = normalized[1:]

        return normalized

    def validate_usa_nanp(self, digits: str) -> tuple[bool, str | None]:
        """
        Validate a USA/NANP phone number.

        USA phone numbers follow the North American Numbering Plan (NANP):
        - Format: NXX-NXX-XXXX
        - N = 2-9 (can't be 0 or 1)
        - X = 0-9
        - Area code can't be N11 (service codes like 911, 411)
        - Exchange code first digit must be 2-9 (not 0 or 1)

        Args:
            digits: Phone number digits (without country code)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(digits) != 10:
            return False, f"USA numbers must be 10 digits, got {len(digits)}"

        # Extract components
        area_code = digits[0:3]
        exchange = digits[3:6]
        # subscriber = digits[6:10]  # Not currently validated

        # Validate area code - first digit must be 2-9
        if area_code[0] not in "23456789":
            return False, f"Area code must start with 2-9: {area_code}"

        # Check for N11 service codes (911, 411, 211, etc.)
        if area_code[1:3] == "11":
            return False, f"Area code cannot be N11 service code: {area_code}"

        # Validate exchange - first digit must be 2-9
        if exchange[0] not in "23456789":
            return False, f"Exchange code must start with 2-9: {exchange}"

        # All digits must be numeric (should already be true, but double-check)
        if not digits.isdigit():
            return False, "Phone number must contain only digits"

        return True, None

    def validate(self, phone_number: str) -> tuple[bool, str | None]:
        """
        Validate a phone number according to country-specific rules.

        Args:
            phone_number: Phone number to validate (can include formatting)

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Normalize the number
        normalized = self.normalize_number(phone_number)

        # Check if it includes country code
        # For USA/NANP, only treat as having country code if it's 11 digits
        # (1 + 10 digits) to avoid treating area codes starting with 1 as country codes
        if self.country_code in (CountryCode.USA, CountryCode.CANADA):
            has_country_code = (
                normalized.startswith(self.format_spec.country_code)
                and len(normalized) == 11
            )
        else:
            has_country_code = normalized.startswith(self.format_spec.country_code)

        # Remove country code if present
        if has_country_code:
            digits = normalized[len(self.format_spec.country_code) :]
        else:
            digits = normalized

        # Check length
        if len(digits) < self.format_spec.min_length:
            return (
                False,
                f"Number too short: {len(digits)} digits "
                f"(minimum {self.format_spec.min_length})",
            )

        if len(digits) > self.format_spec.max_length:
            return (
                False,
                f"Number too long: {len(digits)} digits "
                f"(maximum {self.format_spec.max_length})",
            )

        # Country-specific validation
        if self.country_code in (CountryCode.USA, CountryCode.CANADA):
            return self.validate_usa_nanp(digits)

        # For other countries, just check length and pattern if available
        if self.format_spec.pattern:
            if not re.match(self.format_spec.pattern, digits):
                return (
                    False,
                    f"Number doesn't match format: {self.format_spec.description}",
                )

        return True, None

    def format_number(
        self, phone_number: str, include_country_code: bool = True
    ) -> str | None:
        """
        Format a phone number according to country conventions.

        Args:
            phone_number: Phone number to format
            include_country_code: Whether to include the country code prefix

        Returns:
            Formatted phone number, or None if invalid
        """
        # Validate first
        is_valid, error = self.validate(phone_number)
        if not is_valid:
            logger.warning(f"Invalid phone number '{phone_number}': {error}")
            return None

        # Normalize
        normalized = self.normalize_number(phone_number)

        # Remove country code if present for processing
        # For USA/NANP, only treat as having country code if it's 11 digits
        if self.country_code in (CountryCode.USA, CountryCode.CANADA):
            has_country_code = (
                normalized.startswith(self.format_spec.country_code)
                and len(normalized) == 11
            )
        else:
            has_country_code = normalized.startswith(self.format_spec.country_code)

        if has_country_code:
            digits = normalized[len(self.format_spec.country_code) :]
        else:
            digits = normalized

        # Format according to country
        if self.country_code in (CountryCode.USA, CountryCode.CANADA):
            # Format as XXX-XXX-XXXX
            formatted = f"{digits[0:3]}-{digits[3:6]}-{digits[6:10]}"
        else:
            # Default: just add dashes every 3-4 digits
            formatted = digits

        # Add country code if requested
        if include_country_code:
            return f"+{self.format_spec.country_code}-{formatted}"
        else:
            return formatted

    def validate_pattern(self, pattern: str) -> tuple[bool, str | None]:
        """
        Validate a phone number pattern (partial number for range dialing).

        A pattern can be:
        - A full phone number (validates normally)
        - A partial prefix like "555-12" (validates the prefix portion)

        Args:
            pattern: Phone number pattern to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Normalize
        normalized = self.normalize_number(pattern)

        # Remove country code if present
        # For USA/NANP, only treat as having country code if we have enough digits
        if self.country_code in (CountryCode.USA, CountryCode.CANADA):
            # Could be 11 digits (full number with country code) or more
            has_country_code = (
                normalized.startswith(self.format_spec.country_code)
                and len(normalized) >= 11
            )
        else:
            has_country_code = normalized.startswith(self.format_spec.country_code)

        if has_country_code:
            digits = normalized[len(self.format_spec.country_code) :]
        else:
            digits = normalized

        # For USA/NANP, validate partial patterns
        if self.country_code in (CountryCode.USA, CountryCode.CANADA):
            # Must be at least area code
            if len(digits) < 3:
                return False, "Pattern must include at least area code (3 digits)"

            # If we have area code, validate it
            if len(digits) >= 3:
                area_code = digits[0:3]
                if area_code[0] not in "23456789":
                    return False, f"Area code must start with 2-9: {area_code}"
                if len(area_code) >= 3 and area_code[1:3] == "11":
                    return (
                        False,
                        f"Area code cannot be N11 service code: {area_code}",
                    )

            # If we have exchange, validate it
            if len(digits) >= 6:
                exchange = digits[3:6]
                if exchange[0] not in "23456789":
                    return False, f"Exchange must start with 2-9: {exchange}"

        # All digits must be numeric
        if not digits.isdigit():
            return False, "Pattern must contain only digits"

        return True, None


def get_validator(
    country_code: str | CountryCode = CountryCode.USA,
) -> PhoneNumberValidator:
    """
    Get a phone number validator for a specific country.

    Args:
        country_code: Country code (string or CountryCode enum)

    Returns:
        PhoneNumberValidator instance
    """
    if isinstance(country_code, str):
        # Try to find matching country code
        for cc in CountryCode:
            if cc.value == country_code:
                country_code = cc
                break
        else:
            # Unknown country code, create custom format
            logger.warning(f"Unknown country code: {country_code}, using default")
            country_code = CountryCode.USA

    return PhoneNumberValidator(country_code)
