"""Core dialer logic for VibeDialer."""

import random
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

        # Simulate different status outcomes
        # Weighted probabilities for realistic war dialing
        statuses = [
            ("no_answer", 0.40),  # 40% - Most numbers won't answer
            ("busy", 0.20),  # 20% - Busy signal
            ("person", 0.15),  # 15% - Person answers
            ("modem", 0.10),  # 10% - Modem/fax detected
            ("error", 0.10),  # 10% - Invalid number or error
            ("ringing", 0.05),  # 5% - Still ringing (timeout)
        ]

        # Select status based on weighted probabilities
        rand = random.random()
        cumulative = 0
        selected_status = "no_answer"

        for status, probability in statuses:
            cumulative += probability
            if rand < cumulative:
                selected_status = status
                break

        # Create metadata based on status
        metadata = {}
        if selected_status == "error":
            error_codes = [
                "Invalid number",
                "Number not in service",
                "Circuit busy",
                "Call cannot be completed",
            ]
            metadata["message"] = random.choice(error_codes)
        elif selected_status == "modem":
            metadata["message"] = "Modem carrier detected"
        elif selected_status == "person":
            metadata["message"] = "Human voice detected"
        else:
            metadata["message"] = f"Status: {selected_status}"

        result = DialResult(
            phone_number=phone_number,
            status=selected_status,
            timestamp=timestamp,
            metadata=metadata,
        )

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
