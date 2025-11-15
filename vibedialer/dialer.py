"""Core dialer logic for VibeDialer."""

import random
from datetime import datetime

from vibedialer.backends import (
    BackendType,
    DialResult,
    TelephonyBackend,
    create_backend,
)
from vibedialer.storage import ResultStorage, StorageType, create_storage


class PhoneDialer:
    """Core phone dialer that generates and dials phone numbers."""

    def __init__(
        self,
        backend: TelephonyBackend | None = None,
        backend_type: BackendType = BackendType.SIMULATION,
        storage: ResultStorage | None = None,
        storage_type: StorageType = StorageType.CSV,
        **kwargs,
    ):
        """
        Initialize the phone dialer.

        Args:
            backend: Pre-configured backend instance (optional)
            backend_type: Type of backend to create if backend not provided
            storage: Pre-configured storage instance (optional)
            storage_type: Type of storage to create if storage not provided
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

        self.results: list[DialResult] = []
        self._backend_connected = False

    def generate_numbers(
        self, partial_number: str, randomize: bool = False
    ) -> list[str]:
        """
        Generate phone numbers from a partial number.

        Args:
            partial_number: A partial phone number (e.g., "555-12")
            randomize: If True, return numbers in random order. If False, sequential.

        Returns:
            List of generated phone numbers
        """
        # Remove any formatting characters for processing
        clean_number = partial_number.replace("-", "").replace(" ", "")

        # Determine how many digits we need to add
        # For simplicity, assuming we want 7-digit local numbers (NXX-XXXX format)
        target_length = 7
        current_length = len(clean_number)

        if current_length >= target_length:
            # Already a full number, return it formatted
            return [self._format_number(clean_number[:target_length])]

        # Generate all possible combinations for remaining digits
        digits_needed = target_length - current_length
        max_combinations = 10**digits_needed

        numbers = []
        for i in range(max_combinations):
            # Pad the number with zeros to get the right length
            suffix = str(i).zfill(digits_needed)
            full_number = clean_number + suffix
            formatted = self._format_number(full_number)
            numbers.append(formatted)

        # Randomize if requested
        if randomize:
            random.shuffle(numbers)

        return numbers

    def _format_number(self, number: str) -> str:
        """
        Format a phone number as NXX-XXXX.

        Args:
            number: Unformatted phone number string

        Returns:
            Formatted phone number
        """
        if len(number) >= 7:
            return f"{number[:3]}-{number[3:7]}"
        return number

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

    def cleanup(self) -> None:
        """
        Clean up resources and save any pending data.

        This should be called when shutting down the dialer.
        """
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
        # Ensure backend is connected
        if not self._backend_connected:
            if not self.connect():
                return DialResult(
                    success=False,
                    status="error",
                    message="Failed to connect to backend",
                    phone_number=phone_number,
                    timestamp=datetime.now().isoformat(),
                )

        # Use backend to dial
        result = self.backend.dial(phone_number)

        # Add timestamp and phone number to result
        result.phone_number = phone_number
        result.timestamp = datetime.now().isoformat()

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
