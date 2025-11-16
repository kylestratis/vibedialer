"""Tests for modem audio analysis."""

from unittest.mock import patch

import pytest

from vibedialer.modem import ModemBackend


class TestModemAudioAnalysis:
    """Tests for modem audio tone analysis."""

    def test_audio_analysis_disabled_returns_none(self):
        """Test that audio analysis returns None when disabled."""
        modem = ModemBackend(enable_audio_analysis=False)
        result = modem._analyze_audio_tone()
        assert result is None

    def test_audio_analysis_no_pyaudio_returns_none(self):
        """Test that audio analysis returns None if pyaudio not available."""
        modem = ModemBackend(enable_audio_analysis=True)
        # Without pyaudio or recording file, should return None
        result = modem._analyze_audio_tone()
        # Returns None gracefully when no audio source available
        assert result is None

    @patch("vibedialer.audio_analysis.analyze_audio_buffer")
    def test_audio_analysis_from_file(self, mock_analyze):
        """Test that audio analysis can work from a file."""
        mock_analyze.return_value = {
            "tone_type": "fax",
            "peak_frequency": 1100.0,
            "confidence": 0.92,
        }

        modem = ModemBackend(
            enable_audio_analysis=True, audio_capture_file="/tmp/test.wav"
        )

        result = modem._analyze_audio_tone()

        assert result == "fax"
        mock_analyze.assert_called_once()

    @patch("vibedialer.audio_analysis.analyze_audio_buffer")
    def test_audio_analysis_detects_modem(self, mock_analyze):
        """Test that audio analysis correctly identifies modem tones."""
        mock_analyze.return_value = {
            "tone_type": "modem",
            "peak_frequency": 2400.0,
            "confidence": 0.88,
        }

        modem = ModemBackend(
            enable_audio_analysis=True, audio_capture_file="/tmp/modem.wav"
        )

        result = modem._analyze_audio_tone()

        assert result == "modem"

    @patch("vibedialer.audio_analysis.analyze_audio_buffer")
    def test_audio_analysis_detects_fax(self, mock_analyze):
        """Test that audio analysis correctly identifies fax tones."""
        mock_analyze.return_value = {
            "tone_type": "fax",
            "peak_frequency": 1100.0,
            "confidence": 0.95,
        }

        modem = ModemBackend(
            enable_audio_analysis=True, audio_capture_file="/tmp/fax.wav"
        )

        result = modem._analyze_audio_tone()

        assert result == "fax"

    @patch("vibedialer.audio_analysis.analyze_audio_buffer")
    def test_audio_analysis_detects_voice(self, mock_analyze):
        """Test that audio analysis correctly identifies voice."""
        mock_analyze.return_value = {
            "tone_type": "voice",
            "peak_frequency": 500.0,
            "confidence": 0.75,
        }

        modem = ModemBackend(
            enable_audio_analysis=True, audio_capture_file="/tmp/voice.wav"
        )

        result = modem._analyze_audio_tone()

        assert result == "voice"

    @patch("vibedialer.audio_analysis.analyze_audio_buffer")
    def test_audio_analysis_handles_unknown(self, mock_analyze):
        """Test that audio analysis handles unknown tones."""
        mock_analyze.return_value = {
            "tone_type": "unknown",
            "peak_frequency": None,
            "confidence": 0.0,
        }

        modem = ModemBackend(
            enable_audio_analysis=True, audio_capture_file="/tmp/unknown.wav"
        )

        result = modem._analyze_audio_tone()

        # Unknown should return None (fall back to modem response codes)
        assert result is None

    @patch("vibedialer.audio_analysis.analyze_audio_buffer")
    def test_audio_analysis_handles_errors(self, mock_analyze):
        """Test that audio analysis handles errors gracefully."""
        mock_analyze.side_effect = Exception("Audio device error")

        modem = ModemBackend(
            enable_audio_analysis=True, audio_capture_file="/tmp/error.wav"
        )

        result = modem._analyze_audio_tone()

        # Should return None on error, not crash
        assert result is None

    def test_audio_analysis_low_confidence_returns_none(self):
        """Test that low confidence results return None."""
        with patch("vibedialer.audio_analysis.analyze_audio_buffer") as mock_analyze:
            mock_analyze.return_value = {
                "tone_type": "modem",
                "peak_frequency": 2000.0,
                "confidence": 0.3,  # Low confidence
            }

            modem = ModemBackend(
                enable_audio_analysis=True, audio_capture_file="/tmp/low.wav"
            )

            result = modem._analyze_audio_tone()

            # Low confidence should return None
            assert result is None

    @pytest.mark.skipif(
        True, reason="Requires pyaudio and hardware audio setup"
    )
    def test_audio_analysis_with_pyaudio(self):
        """Test real-time audio capture with pyaudio (requires hardware)."""
        # This test is skipped by default as it requires:
        # 1. pyaudio library installed
        # 2. Audio hardware connected (modem line tap)
        # 3. Active call with carrier tone

        # Would test: modem = ModemBackend(enable_audio_analysis=True)
        # Would test: result = modem._analyze_audio_tone()
        # Would assert: result in ["modem", "fax", "voice"]
        # But skipped for CI/testing because it requires:
        # - pyaudio library, hardware audio setup, active call
        pass
