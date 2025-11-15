"""Telephony backend implementations for VibeDialer."""

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class BackendType(Enum):
    """Types of telephony backends."""

    MODEM = "modem"
    VOIP = "voip"
    IP_RELAY = "ip_relay"
    SIMULATION = "simulation"


@dataclass
class DialResult:
    """Result from a dial attempt."""

    success: bool
    status: str
    message: str
    carrier_detected: bool = False
    tone_type: str | None = None  # "modem", "fax", "voice", etc.
    phone_number: str = ""
    timestamp: str = ""


class TelephonyBackend(ABC):
    """Abstract base class for telephony backends."""

    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the telephony device/service.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the telephony device/service."""
        pass

    @abstractmethod
    def dial(self, phone_number: str) -> DialResult:
        """
        Dial a phone number.

        Args:
            phone_number: The phone number to dial

        Returns:
            DialResult with outcome of the dial attempt
        """
        pass

    @abstractmethod
    def hangup(self) -> None:
        """Hang up the current call."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if backend is connected.

        Returns:
            True if connected, False otherwise
        """
        pass


class SimulationBackend(TelephonyBackend):
    """Simulation backend for testing and demo purposes."""

    def __init__(self):
        """Initialize simulation backend."""
        self._connected = False

    def connect(self) -> bool:
        """
        Connect to simulation backend (always succeeds).

        Returns:
            True
        """
        self._connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from simulation backend."""
        self._connected = False

    def dial(self, phone_number: str) -> DialResult:
        """
        Simulate dialing a phone number.

        Args:
            phone_number: The phone number to dial

        Returns:
            DialResult with simulated outcome
        """
        if not self.is_connected():
            return DialResult(
                success=False,
                status="error",
                message="Not connected",
            )

        # Simulate different outcomes with weighted probabilities
        statuses = [
            ("no_answer", 0.40, False, None),
            ("busy", 0.20, False, None),
            ("person", 0.15, False, "voice"),
            ("modem", 0.10, True, "modem"),
            ("error", 0.10, False, None),
            ("ringing", 0.05, False, None),
        ]

        rand = random.random()
        cumulative = 0

        for status, probability, carrier, tone in statuses:
            cumulative += probability
            if rand < cumulative:
                success = status == "modem" or status == "person"
                message = f"Simulated: {status}"

                if status == "error":
                    error_codes = [
                        "Invalid number",
                        "Number not in service",
                        "Circuit busy",
                    ]
                    message = random.choice(error_codes)
                elif status == "modem":
                    message = "Modem carrier detected (simulated)"
                elif status == "person":
                    message = "Voice detected (simulated)"

                return DialResult(
                    success=success,
                    status=status,
                    message=message,
                    carrier_detected=carrier,
                    tone_type=tone,
                )

        # Default fallback
        return DialResult(
            success=False,
            status="no_answer",
            message="No answer (simulated)",
        )

    def hangup(self) -> None:
        """Simulate hanging up."""
        pass

    def is_connected(self) -> bool:
        """
        Check if simulation backend is connected.

        Returns:
            True if connected, False otherwise
        """
        return self._connected


def create_backend(backend_type: BackendType, **kwargs) -> TelephonyBackend:
    """
    Factory function to create telephony backends.

    Args:
        backend_type: Type of backend to create
        **kwargs: Backend-specific configuration

    Returns:
        TelephonyBackend instance

    Raises:
        ValueError: If backend type is invalid
    """
    if backend_type == BackendType.SIMULATION:
        return SimulationBackend()

    elif backend_type == BackendType.MODEM:
        from vibedialer.modem import ModemBackend

        port = kwargs.get("port", "/dev/ttyUSB0")
        baudrate = kwargs.get("baudrate", 57600)
        timeout = kwargs.get("timeout", 30)
        return ModemBackend(port=port, baudrate=baudrate, timeout=timeout)

    elif backend_type == BackendType.VOIP:
        from vibedialer.voip import VoIPBackend

        # Twilio VoIP backend
        account_sid = kwargs.get("account_sid", "")
        auth_token = kwargs.get("auth_token", "")
        from_number = kwargs.get("from_number", "")
        timeout = kwargs.get("timeout", 30)
        twiml_url = kwargs.get("twiml_url")
        return VoIPBackend(
            account_sid=account_sid,
            auth_token=auth_token,
            from_number=from_number,
            timeout=timeout,
            twiml_url=twiml_url,
        )

    elif backend_type == BackendType.IP_RELAY:
        from vibedialer.iprelay import IPRelayBackend

        relay_service_url = kwargs.get("relay_service_url", "")
        api_key = kwargs.get("api_key")
        return IPRelayBackend(relay_service_url=relay_service_url, api_key=api_key)

    else:
        raise ValueError(f"Unknown backend type: {backend_type}")
