"""Tests for CLI non-interactive mode."""

import tempfile
from pathlib import Path

from typer.testing import CliRunner

from vibedialer.cli import app

runner = CliRunner()


class TestNonInteractiveDialing:
    """Tests for non-interactive dialing functionality."""

    def test_noninteractive_mode_dials_numbers(self):
        """Test that non-interactive mode actually dials numbers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "results.csv"

            result = runner.invoke(
                app,
                [
                    "dial",
                    "555-234",  # Valid pattern (exchange starts with 2-9)
                    "--no-interactive",
                    "--backend",
                    "simulation",
                    "--output",
                    str(output_file),
                ],
            )

            # Should complete successfully
            assert result.exit_code == 0

            # Should show dialing activity
            assert "Dialing" in result.stdout or "dialing" in result.stdout.lower()

            # Results file should be created
            assert output_file.exists()

    def test_noninteractive_mode_shows_results(self):
        """Test that non-interactive mode displays dial results."""
        result = runner.invoke(
            app,
            [
                "dial",
                "555-234",
                "--no-interactive",
                "--backend",
                "simulation",
                "--storage",
                "dry-run",  # Don't create files
            ],
        )

        assert result.exit_code == 0

        # Should show phone numbers being dialed
        assert "555" in result.stdout

        # Should show some status (e.g., "Modem", "Busy", etc.)
        # Simulation backend returns various statuses
        status_indicators = [
            "modem",
            "busy",
            "ringing",
            "person",
            "no answer",
            "error",
        ]
        assert any(
            indicator in result.stdout.lower() for indicator in status_indicators
        )

    def test_noninteractive_mode_respects_random_flag(self):
        """Test that random mode affects number generation."""
        # This is harder to test directly, but we can at least verify
        # it doesn't crash with random mode
        result = runner.invoke(
            app,
            [
                "dial",
                "555-234",
                "--no-interactive",
                "--random",
                "--backend",
                "simulation",
                "--storage",
                "dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "random" in result.stdout.lower()

    def test_noninteractive_mode_respects_sequential_flag(self):
        """Test that sequential mode affects number generation."""
        result = runner.invoke(
            app,
            [
                "dial",
                "555-234",
                "--no-interactive",
                "--sequential",
                "--backend",
                "simulation",
                "--storage",
                "dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "sequential" in result.stdout.lower()

    def test_noninteractive_mode_with_resume(self):
        """Test that non-interactive mode works with resume file."""
        # Create a temporary CSV with some numbers
        with tempfile.TemporaryDirectory() as tmpdir:
            resume_file = Path(tmpdir) / "previous.csv"

            # Create a simple CSV with some dialed numbers
            resume_file.write_text(
                "session_id,phone_number,status,timestamp,success,message,"
                "carrier_detected,tone_type,answered_by,amd_duration,"
                "fft_peak_frequency,fft_confidence,recording_url,"
                "recording_duration\n"
                "test123,555-2340,busy,2024-01-01 12:00:00,False,"
                "Busy signal,False,,,,,,,\n"
                "test123,555-2341,modem,2024-01-01 12:00:01,True,"
                "Modem detected,True,modem,,,,,,\n"
            )

            result = runner.invoke(
                app,
                [
                    "dial",
                    "555-234",  # Provide phone number directly
                    "--no-interactive",
                    "--resume",
                    str(resume_file),
                    "--backend",
                    "simulation",
                    "--storage",
                    "dry-run",
                ],
            )

            # Should complete successfully
            assert result.exit_code == 0

            # Should mention resuming
            assert "remaining" in result.stdout.lower()

    def test_noninteractive_mode_saves_to_sqlite(self):
        """Test that non-interactive mode can save to SQLite."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "results.db"

            result = runner.invoke(
                app,
                [
                    "dial",
                    "555-234",
                    "--no-interactive",
                    "--backend",
                    "simulation",
                    "--storage",
                    "sqlite",
                    "--output",
                    str(db_file),
                ],
            )

            assert result.exit_code == 0
            assert db_file.exists()

    def test_noninteractive_mode_displays_summary(self):
        """Test that non-interactive mode shows a summary at the end."""
        result = runner.invoke(
            app,
            [
                "dial",
                "555-234",
                "--no-interactive",
                "--backend",
                "simulation",
                "--storage",
                "dry-run",
            ],
        )

        assert result.exit_code == 0

        # Should show some kind of completion/summary
        summary_indicators = [
            "complete",
            "finished",
            "done",
            "dialed",
            "total",
        ]
        assert any(
            indicator in result.stdout.lower() for indicator in summary_indicators
        )

    def test_noninteractive_mode_without_phone_number_fails(self):
        """Test that non-interactive mode requires a phone number or resume file."""
        result = runner.invoke(
            app,
            [
                "dial",
                "--no-interactive",
                "--backend",
                "simulation",
            ],
        )

        # Should fail with no phone number
        assert result.exit_code != 0

    def test_noninteractive_mode_with_modem_backend(self):
        """Test that modem backend parameters are accepted."""
        # This won't actually connect to a modem, but should parse args correctly
        result = runner.invoke(
            app,
            [
                "dial",
                "555-234",
                "--no-interactive",
                "--backend",
                "modem",
                "--modem-port",
                "/dev/ttyUSB0",
                "--storage",
                "dry-run",
            ],
        )

        # Might fail due to no modem, but should at least parse args
        # The important thing is it doesn't crash on argument parsing
        assert "modem" in result.stdout.lower() or result.exit_code == 0
