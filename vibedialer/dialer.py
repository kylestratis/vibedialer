"""Core dialer logic for VibeDialer."""

import logging
import random
from datetime import datetime

from vibedialer.backends import (
    BackendType,
    DialResult,
    TelephonyBackend,
    create_backend,
)
from vibedialer.session import (
    create_session_metadata,
    generate_session_id,
)
from vibedialer.storage import ResultStorage, StorageType, create_storage
from vibedialer.validation import CountryCode, get_validator

logger = logging.getLogger(__name__)


class PhoneDialer:
    """Core phone dialer that generates and dials phone numbers."""

    def __init__(
        self,
        backend: TelephonyBackend | None = None,
        backend_type: BackendType = BackendType.SIMULATION,
        storage: ResultStorage | None = None,
        storage_type: StorageType = StorageType.CSV,
        country_code: CountryCode | str = CountryCode.USA,
        session_id: str | None = None,
        phone_pattern: str = "",
        randomize: bool = False,
        **kwargs,
    ):
        """
        Initialize the phone dialer.

        Args:
            backend: Pre-configured backend instance (optional)
            backend_type: Type of backend to create if backend not provided
            storage: Pre-configured storage instance (optional)
            storage_type: Type of storage to create if storage not provided
            country_code: Country code for phone number validation (default: USA)
            session_id: Session ID for grouping dial results
                (auto-generated if not provided)
            phone_pattern: Phone number pattern being dialed (for session metadata)
            randomize: Whether numbers are being dialed in random order
            **kwargs: Backend and storage specific configuration
        """
        # Separate backend and storage kwargs
        backend_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k
            in [
                "port",
                "baudrate",
                "timeout",
                "enable_audio_analysis",
                "sip_server",
                "username",
                "password",
                "relay_service_url",
                "api_key",
            ]
        }
        storage_kwargs = {
            k: v for k, v in kwargs.items() if k in ["filename", "database"]
        }

        # Initialize backend
        if backend is not None:
            self.backend = backend
        else:
            self.backend = create_backend(backend_type, **backend_kwargs)

        # Initialize storage
        if storage is not None:
            self.storage = storage
        else:
            self.storage = create_storage(storage_type, **storage_kwargs)

        # Initialize phone number validator
        self.validator = get_validator(country_code)
        self.country_code = self.validator.country_code

        self.results: list[DialResult] = []
        self._backend_connected = False

        # Initialize session tracking
        self.session_id = session_id or generate_session_id()
        self.session_metadata = create_session_metadata(
            session_id=self.session_id,
            backend_type=backend_type.value,
            storage_type=storage_type.value,
            phone_pattern=phone_pattern,
            country_code=str(self.country_code.value),
            randomized=randomize,
        )
        self._session_saved = False

    def generate_numbers(
        self, partial_number: str, randomize: bool = False
    ) -> list[str]:
        """
        Generate phone numbers from a partial number.

        Validates the pattern and generates all possible combinations.
        For USA/NANP, generates 10-digit numbers (NXX-NXX-XXXX).

        Args:
            partial_number: A partial phone number (e.g., "555-12")
            randomize: If True, return numbers in random order. If False, sequential.

        Returns:
            List of generated phone numbers

        Raises:
            ValueError: If the pattern is invalid for the country
        """
        # Validate the pattern first
        is_valid, error = self.validator.validate_pattern(partial_number)
        if not is_valid:
            raise ValueError(
                f"Invalid phone number pattern '{partial_number}': {error}"
            )

        # Remove any formatting characters for processing
        clean_number = self.validator.normalize_number(partial_number)

        # Determine target length based on country
        # For USA/NANP, we want 10 digits (area code + exchange + subscriber)
        if self.country_code in (CountryCode.USA, CountryCode.CANADA):
            target_length = 10
        else:
            target_length = self.validator.format_spec.max_length

        current_length = len(clean_number)

        if current_length >= target_length:
            # Already a full number, validate and return it formatted
            is_valid, error = self.validator.validate(clean_number)
            if not is_valid:
                raise ValueError(f"Invalid phone number '{partial_number}': {error}")
            formatted = self.validator.format_number(
                clean_number, include_country_code=False
            )
            return [formatted] if formatted else []

        # Generate all possible combinations for remaining digits
        digits_needed = target_length - current_length
        max_combinations = 10**digits_needed

        numbers = []
        for i in range(max_combinations):
            # Pad the number with zeros to get the right length
            suffix = str(i).zfill(digits_needed)
            full_number = clean_number + suffix

            # Validate each generated number
            is_valid, error = self.validator.validate(full_number)
            if is_valid:
                # Format using validator
                formatted = self.validator.format_number(
                    full_number, include_country_code=False
                )
                if formatted:
                    numbers.append(formatted)
            else:
                logger.debug(f"Skipping invalid number {full_number}: {error}")

        logger.info(
            f"Generated {len(numbers)} valid numbers from pattern '{partial_number}'"
        )

        # Randomize if requested
        if randomize:
            random.shuffle(numbers)

        return numbers

    def count_numbers(self, partial_number: str) -> int:
        """
        Count how many phone numbers would be generated from a partial number.

        This is much faster than generating all numbers, especially for large ranges.
        Uses mathematical calculation instead of actually generating the numbers.

        Args:
            partial_number: A partial phone number (e.g., "555-12")

        Returns:
            Count of phone numbers that would be generated

        Raises:
            ValueError: If the pattern is invalid for the country
        """
        # Validate the pattern first
        is_valid, error = self.validator.validate_pattern(partial_number)
        if not is_valid:
            raise ValueError(
                f"Invalid phone number pattern '{partial_number}': {error}"
            )

        # Remove any formatting characters for processing
        clean_number = self.validator.normalize_number(partial_number)

        # Determine target length based on country
        if self.country_code in (CountryCode.USA, CountryCode.CANADA):
            target_length = 10
        else:
            target_length = self.validator.format_spec.max_length

        current_length = len(clean_number)

        if current_length >= target_length:
            # Already a full number, just one number
            return 1

        # Calculate how many digits we need to fill
        digits_needed = target_length - current_length

        # For USA/NANP, we need to account for validation rules
        if self.country_code in (CountryCode.USA, CountryCode.CANADA):
            # If we have area code but not exchange (3 digits)
            if current_length == 3:
                # Exchange first digit must be 2-9 (8 choices)
                # Remaining 6 digits can be anything (10^6 choices)
                return 8 * (10**6)
            # If we have area code + partial exchange (4 or 5 digits)
            elif current_length == 4:
                # Exchange first digit is already set and valid
                # Need 6 more digits: 10^6
                return 10**6
            elif current_length == 5:
                # Exchange first two digits are set
                # Need 5 more digits: 10^5
                return 10**5
            # If we have area code + exchange (6+ digits)
            else:
                # All remaining digits are valid (0-9)
                return 10**digits_needed
        else:
            # For other countries, all combinations are valid
            return 10**digits_needed

    def _format_number(self, number: str) -> str:
        """
        Format a phone number using the validator.

        Note: This method is deprecated. Use validator.format_number() directly.

        Args:
            number: Unformatted phone number string

        Returns:
            Formatted phone number
        """
        formatted = self.validator.format_number(number, include_country_code=False)
        return formatted if formatted else number

    def connect(self) -> bool:
        """
        Connect to the telephony backend.

        Returns:
            True if connection successful, False otherwise
        """
        if not self._backend_connected:
            self._backend_connected = self.backend.connect()
        return self._backend_connected

    def disconnect(self) -> None:
        """Disconnect from the telephony backend."""
        if self._backend_connected:
            self.backend.disconnect()
            self._backend_connected = False

    def _save_session_metadata(self) -> None:
        """Save or update session metadata to storage."""
        # Check if storage supports session metadata
        if hasattr(self.storage, "save_session"):
            try:
                self.storage.save_session(self.session_metadata)
                self._session_saved = True
                logger.debug(f"Saved session metadata for session {self.session_id}")
            except Exception as e:
                logger.warning(f"Failed to save session metadata: {e}")
        else:
            logger.debug(
                f"Storage type {type(self.storage).__name__} "
                "does not support session metadata"
            )
            self._session_saved = True  # Mark as saved to avoid repeated attempts

    def cleanup(self) -> None:
        """
        Clean up resources and save any pending data.

        This should be called when shutting down the dialer.
        """
        # Update session end time
        self.session_metadata.end_time = datetime.now().isoformat()

        # Save final session metadata
        self._save_session_metadata()

        # Flush and close storage
        if self.storage:
            self.storage.flush()
            self.storage.close()

        # Disconnect backend
        self.disconnect()

    def dial(self, phone_number: str) -> DialResult:
        """
        Dial a phone number and return the result.

        Args:
            phone_number: The phone number to dial

        Returns:
            DialResult with the outcome
        """
        # Save session metadata on first dial
        if not self._session_saved:
            self._save_session_metadata()

        # Ensure backend is connected
        if not self._backend_connected:
            if not self.connect():
                return DialResult(
                    success=False,
                    status="error",
                    message="Failed to connect to backend",
                    phone_number=phone_number,
                    timestamp=datetime.now().isoformat(),
                    session_id=self.session_id,
                )

        # Use backend to dial
        result = self.backend.dial(phone_number)

        # Add timestamp, phone number, and session ID to result
        result.phone_number = phone_number
        result.timestamp = datetime.now().isoformat()
        result.session_id = self.session_id

        # Update session statistics
        self.session_metadata.total_calls += 1
        if result.success:
            self.session_metadata.successful_calls += 1
        if result.status == "modem" or result.carrier_detected:
            self.session_metadata.modem_detections += 1

        # Save result to storage
        self.storage.save_result(result)

        self.results.append(result)
        return result

    def dial_sequence(
        self, partial_number: str, randomize: bool = False
    ) -> list[DialResult]:
        """
        Dial a sequence of numbers generated from a partial number.

        Args:
            partial_number: Partial phone number to expand and dial
            randomize: If True, dial numbers in random order. If False, sequential.

        Returns:
            List of DialResults for all dialed numbers
        """
        numbers = self.generate_numbers(partial_number, randomize=randomize)
        results = []

        for number in numbers:
            result = self.dial(number)
            results.append(result)

        return results
