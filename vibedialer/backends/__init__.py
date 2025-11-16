"""Backend implementations for VibeDialer."""

from vibedialer.backends.base import (
    BackendType,
    DialResult,
    SimulationBackend,
    TelephonyBackend,
    create_backend,
)
from vibedialer.backends.iprelay import IPRelayBackend
from vibedialer.backends.modem import ModemBackend
from vibedialer.backends.voip import VoIPBackend

__all__ = [
    "BackendType",
    "DialResult",
    "IPRelayBackend",
    "ModemBackend",
    "SimulationBackend",
    "TelephonyBackend",
    "VoIPBackend",
    "create_backend",
]
