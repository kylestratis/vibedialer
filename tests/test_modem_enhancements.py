"""Tests for enhanced modem backend features."""

from vibedialer.modem import ModemBackend


def test_modem_backend_parse_connect_with_speed():
    """Test parsing CONNECT response with speed."""
    modem = ModemBackend()
    result = modem._parse_response("CONNECT 2400", ring_count=0)

    assert result is not None
    assert result.status == "modem"
    assert result.carrier_detected is True
    assert "2400 bps" in result.message


def test_modem_backend_parse_connect_with_protocol():
    """Test parsing CONNECT response with protocol info."""
    modem = ModemBackend()
    result = modem._parse_response("CONNECT 28800/ARQ/V34/LAPM", ring_count=0)

    assert result is not None
    assert result.status == "modem"
    assert result.carrier_detected is True
    assert "28800 bps" in result.message
    assert "ARQ/V34/LAPM" in result.message


def test_modem_backend_parse_connect_with_modulation():
    """Test parsing CONNECT response with modulation standard."""
    modem = ModemBackend()
    result = modem._parse_response("CONNECT 33600/V.34", ring_count=0)

    assert result is not None
    assert result.status == "modem"
    assert result.carrier_detected is True
    assert "33600 bps" in result.message
    assert "V.34" in result.message


def test_modem_backend_parse_fax_connect():
    """Test parsing FAX CONNECT response."""
    modem = ModemBackend()
    result = modem._parse_response("CONNECT FAX", ring_count=0)

    assert result is not None
    assert result.status == "modem"
    assert result.tone_type == "fax"
    assert result.carrier_detected is True


def test_modem_backend_parse_busy_with_rings():
    """Test parsing BUSY response with ring count."""
    modem = ModemBackend()
    result = modem._parse_response("BUSY", ring_count=3)

    assert result is not None
    assert result.status == "busy"
    assert "3 rings" in result.message


def test_modem_backend_parse_no_carrier_with_rings():
    """Test parsing NO CARRIER response with ring count."""
    modem = ModemBackend()
    result = modem._parse_response("NO CARRIER", ring_count=5)

    assert result is not None
    assert result.status == "no_answer"
    assert "5 rings" in result.message


def test_modem_backend_parse_no_carrier_without_rings():
    """Test parsing NO CARRIER response without rings."""
    modem = ModemBackend()
    result = modem._parse_response("NO CARRIER", ring_count=0)

    assert result is not None
    assert result.status == "no_answer"
    assert "No carrier detected" in result.message


def test_modem_backend_audio_analysis_disabled():
    """Test that audio analysis returns None when disabled."""
    modem = ModemBackend(enable_audio_analysis=False)
    result = modem._analyze_audio_tone()
    assert result is None


def test_modem_backend_audio_analysis_stub():
    """Test that audio analysis is a stub (returns None even when enabled)."""
    modem = ModemBackend(enable_audio_analysis=True)
    result = modem._analyze_audio_tone()
    # Currently returns None as it's not implemented
    assert result is None


def test_modem_backend_with_audio_analysis_flag():
    """Test creating modem backend with audio analysis flag."""
    modem = ModemBackend(enable_audio_analysis=True)
    assert modem.enable_audio_analysis is True

    modem2 = ModemBackend(enable_audio_analysis=False)
    assert modem2.enable_audio_analysis is False


def test_modem_backend_parse_voice_response():
    """Test parsing VOICE response."""
    modem = ModemBackend()
    result = modem._parse_response("VOICE", ring_count=2)

    assert result is not None
    assert result.status == "person"
    assert result.tone_type == "voice"
    assert "Voice detected" in result.message


def test_modem_backend_parse_error_response():
    """Test parsing ERROR response."""
    modem = ModemBackend()
    result = modem._parse_response("ERROR", ring_count=0)

    assert result is not None
    assert result.status == "error"
    assert "error" in result.message.lower()


def test_modem_backend_parse_no_dial_tone():
    """Test parsing NO DIAL TONE response."""
    modem = ModemBackend()
    result = modem._parse_response("NO DIALTONE", ring_count=0)

    assert result is not None
    assert result.status == "error"
    assert "dial tone" in result.message.lower()


def test_modem_backend_parse_ring_not_final():
    """Test that RING response doesn't return a final result."""
    modem = ModemBackend()
    result = modem._parse_response("RING", ring_count=1)

    # RING is not a final result, should return None
    assert result is None
