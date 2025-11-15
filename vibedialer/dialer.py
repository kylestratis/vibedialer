"""Core dialer logic for VibeDialer."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class DialResult:
    """Result from dialing a phone number."""

    phone_number: str
    status: str  # e.g., "connected", "busy", "no_answer", "error"
    timestamp: str
    metadata: dict | None = None


class PhoneDialer:
    """Core phone dialer that generates and dials phone numbers."""

    def __init__(self):
        """Initialize the phone dialer."""
        self.results: list[DialResult] = []

    def generate_numbers(self, partial_number: str) -> list[str]:
        """
        Generate phone numbers from a partial number.

        Args:
            partial_number: A partial phone number (e.g., "555-12")

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

    def dial(self, phone_number: str) -> DialResult:
        """
        Dial a phone number and return the result.

        This is a placeholder implementation that simulates dialing.

        Args:
            phone_number: The phone number to dial

        Returns:
            DialResult with the outcome
        """
        # Placeholder: In a real implementation, this would actually
        # interface with telephony hardware/software
        timestamp = datetime.now().isoformat()

        result = DialResult(
            phone_number=phone_number,
            status="simulated",
            timestamp=timestamp,
            metadata={"message": "This is a simulated dial"},
        )

        self.results.append(result)
        return result

    def dial_sequence(self, partial_number: str) -> list[DialResult]:
        """
        Dial a sequence of numbers generated from a partial number.

        Args:
            partial_number: Partial phone number to expand and dial

        Returns:
            List of DialResults for all dialed numbers
        """
        numbers = self.generate_numbers(partial_number)
        results = []

        for number in numbers:
            result = self.dial(number)
            results.append(result)

        return results
