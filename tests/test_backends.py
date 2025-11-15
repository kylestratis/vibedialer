"""Tests for telephony backends."""

import pytest

from vibedialer.backends import (
    BackendType,
    DialResult,
    SimulationBackend,
    create_backend,
)


def test_dial_result_creation():
    """Test creating a DialResult."""
    result = DialResult(
        success=True,
        status="modem",
        message="Carrier detected",
        carrier_detected=True,
        tone_type="modem",
    )
    assert result.success is True
    assert result.status == "modem"
    assert result.carrier_detected is True
    assert result.tone_type == "modem"


def test_simulation_backend_connect():
    """Test simulation backend connection."""
    backend = SimulationBackend()
    assert not backend.is_connected()

    result = backend.connect()
    assert result is True
    assert backend.is_connected()


def test_simulation_backend_disconnect():
    """Test simulation backend disconnection."""
    backend = SimulationBackend()
    backend.connect()
    assert backend.is_connected()

    backend.disconnect()
    assert not backend.is_connected()


def test_simulation_backend_dial():
    """Test simulation backend dial."""
    backend = SimulationBackend()
    backend.connect()

    result = backend.dial("555-1234")
    assert isinstance(result, DialResult)
    assert result.status in ["no_answer", "busy", "person", "modem", "error", "ringing"]


def test_simulation_backend_dial_not_connected():
    """Test simulation backend dial when not connected."""
    backend = SimulationBackend()

    result = backend.dial("555-1234")
    assert result.success is False
    assert result.status == "error"
    assert "not connected" in result.message.lower()


def test_simulation_backend_hangup():
    """Test simulation backend hangup."""
    backend = SimulationBackend()
    backend.connect()

    # Should not raise an exception
    backend.hangup()


def test_simulation_backend_dial_variety():
    """Test that simulation backend produces variety of statuses."""
    backend = SimulationBackend()
    backend.connect()

    # Dial many numbers to ensure we get variety
    results = [backend.dial(f"555-120{i}") for i in range(100)]
    statuses = {r.status for r in results}

    # Should have at least 3 different statuses in 100 calls
    assert len(statuses) >= 3


def test_create_backend_simulation():
    """Test factory creates simulation backend."""
    backend = create_backend(BackendType.SIMULATION)
    assert isinstance(backend, SimulationBackend)


def test_create_backend_modem():
    """Test factory creates modem backend."""
    backend = create_backend(
        BackendType.MODEM, port="/dev/ttyUSB0", baudrate=57600, timeout=30
    )
    # Import here to avoid issues if not available
    from vibedialer.modem import ModemBackend

    assert isinstance(backend, ModemBackend)
    assert backend.port == "/dev/ttyUSB0"
    assert backend.baudrate == 57600
    assert backend.timeout == 30


def test_create_backend_voip():
    """Test factory creates VoIP backend."""
    backend = create_backend(
        BackendType.VOIP,
        sip_server="sip.example.com",
        username="user",
        password="pass",
    )
    from vibedialer.voip import VoIPBackend

    assert isinstance(backend, VoIPBackend)
    assert backend.sip_server == "sip.example.com"
    assert backend.username == "user"


def test_create_backend_ip_relay():
    """Test factory creates IP relay backend."""
    backend = create_backend(
        BackendType.IP_RELAY,
        relay_service_url="https://relay.example.com",
        api_key="test_key",
    )
    from vibedialer.iprelay import IPRelayBackend

    assert isinstance(backend, IPRelayBackend)
    assert backend.relay_service_url == "https://relay.example.com"
    assert backend.api_key == "test_key"


def test_create_backend_invalid_type():
    """Test factory raises error for invalid backend type."""

    # Create a fake backend type
    class FakeType:
        pass

    with pytest.raises(ValueError, match="Unknown backend type"):
        create_backend(FakeType())  # type: ignore
