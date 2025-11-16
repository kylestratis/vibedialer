"""Tests for TUI stop dialing functionality."""

from unittest.mock import Mock, patch

import pytest
from textual.widgets import Button

from vibedialer.backends import BackendType
from vibedialer.ui.tui import DialingScreen, VibeDialerApp


class TestTUIStopDialing:
    """Tests for stop dialing functionality."""

    @pytest.mark.asyncio
    async def test_stop_dialing_sets_flag(self):
        """Test that stop_dialing sets the is_dialing flag to False."""
        app = VibeDialerApp(backend_type=BackendType.SIMULATION)
        async with app.run_test():
            # Create and push dialing screen directly (disable auto_start for tests)
            dialing_screen = DialingScreen(
                phone_number="555", backend_type=BackendType.SIMULATION, auto_start=False
            )
            await app.push_screen(dialing_screen)

            assert isinstance(app.screen, DialingScreen)

            app.screen.is_dialing = True
            app.screen.stop_dialing()
            assert app.screen.is_dialing is False

    @pytest.mark.asyncio
    async def test_stop_dialing_hangs_up_current_call(self):
        """Test that stop_dialing hangs up any active call."""
        app = VibeDialerApp(backend_type=BackendType.SIMULATION)
        async with app.run_test():
            # Create and push dialing screen directly (disable auto_start for tests)
            dialing_screen = DialingScreen(
                phone_number="555", backend_type=BackendType.SIMULATION, auto_start=False
            )
            await app.push_screen(dialing_screen)

            assert isinstance(app.screen, DialingScreen)

            # Mock the backend hangup method
            app.screen.dialer.backend.hangup = Mock()

            app.screen.is_dialing = True
            app.screen.stop_dialing()

            # Verify hangup was called
            app.screen.dialer.backend.hangup.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_dialing_flushes_storage(self):
        """Test that stop_dialing flushes storage to save results."""
        app = VibeDialerApp(backend_type=BackendType.SIMULATION)
        async with app.run_test():
            # Create and push dialing screen directly (disable auto_start for tests)
            dialing_screen = DialingScreen(
                phone_number="555", backend_type=BackendType.SIMULATION, auto_start=False
            )
            await app.push_screen(dialing_screen)

            assert isinstance(app.screen, DialingScreen)

            # Mock the storage flush method
            app.screen.dialer.storage.flush = Mock()

            app.screen.is_dialing = True
            app.screen.stop_dialing()

            # Verify flush was called
            app.screen.dialer.storage.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_dialing_updates_ui_status(self):
        """Test that stop_dialing updates the UI status label."""
        app = VibeDialerApp(backend_type=BackendType.SIMULATION)
        async with app.run_test():
            # Create and push dialing screen directly (disable auto_start for tests)
            dialing_screen = DialingScreen(
                phone_number="555", backend_type=BackendType.SIMULATION, auto_start=False
            )
            await app.push_screen(dialing_screen)

            assert isinstance(app.screen, DialingScreen)

            app.screen.is_dialing = True
            app.screen.stop_dialing()

            # Check that status was updated
            status_label = app.screen.query_one("#current-status")
            label_text = str(status_label.render())
            assert "Stopped" in label_text or "stopped" in label_text.lower()

    @pytest.mark.asyncio
    @patch("vibedialer.backends.voip.VoIPBackend")
    async def test_stop_dialing_waits_for_voip_analyses(self, mock_voip):
        """Test that stop_dialing waits for pending VoIP audio analyses."""
        # Create mock VoIP backend with pending analyses
        mock_backend_instance = Mock()
        mock_backend_instance.pending_analyses = {"CA123": Mock()}
        mock_backend_instance._wait_for_pending_analyses = Mock()
        mock_voip.return_value = mock_backend_instance

        app = VibeDialerApp(
            backend_type=BackendType.VOIP,
            backend_kwargs={
                "account_sid": "AC123",
                "auth_token": "token",
                "from_number": "+15551234567",
            },
        )
        async with app.run_test():
            # Create and push dialing screen directly (disable auto_start for tests)
            dialing_screen = DialingScreen(
                phone_number="555",
                backend_type=BackendType.VOIP,
                backend_kwargs={
                    "account_sid": "AC123",
                    "auth_token": "token",
                    "from_number": "+15551234567",
                },
                auto_start=False,
            )
            await app.push_screen(dialing_screen)

            assert isinstance(app.screen, DialingScreen)

            # Replace the backend with our mock
            app.screen.dialer.backend = mock_backend_instance

            app.screen.is_dialing = True
            app.screen.stop_dialing()

            # Verify wait for analyses was called
            mock_backend_instance._wait_for_pending_analyses.assert_called()

    @pytest.mark.asyncio
    async def test_dialing_loop_checks_is_dialing_flag(self):
        """Test that the dialing loop checks is_dialing and stops when False."""
        app = VibeDialerApp(backend_type=BackendType.SIMULATION)

        async with app.run_test():
            # Create and push dialing screen directly
            dialing_screen = DialingScreen(
                phone_number="555-234",  # Valid pattern: exchange starts with 2
                backend_type=BackendType.SIMULATION,
                auto_start=False,
            )
            await app.push_screen(dialing_screen)

            assert isinstance(app.screen, DialingScreen)

            # Mock dial to count calls
            original_dial = app.screen.dialer.dial
            call_count = []

            def mock_dial(number):
                call_count.append(number)
                # Stop after first call
                if len(call_count) == 1:
                    app.screen.is_dialing = False
                return original_dial(number)

            app.screen.dialer.dial = mock_dial

            # Start dialing (would normally dial 10 numbers)
            await app.screen.start_dialing()

            # Should have stopped after 1 call instead of 10
            assert len(call_count) == 1

    @pytest.mark.asyncio
    async def test_stop_button_calls_stop_dialing(self):
        """Test that pressing the stop button calls stop_dialing."""
        app = VibeDialerApp(backend_type=BackendType.SIMULATION)

        async with app.run_test():
            # Create and push dialing screen directly (disable auto_start for tests)
            dialing_screen = DialingScreen(
                phone_number="555", backend_type=BackendType.SIMULATION, auto_start=False
            )
            await app.push_screen(dialing_screen)

            assert isinstance(app.screen, DialingScreen)

            # Mock stop_dialing to track if it was called
            original_stop = app.screen.stop_dialing
            stop_called = []

            def mock_stop():
                stop_called.append(True)
                original_stop()

            app.screen.stop_dialing = mock_stop

            # Simulate stop button press
            stop_btn = app.screen.query_one("#stop-btn", Button)
            stop_btn.press()

            # Give the event loop a moment to process the button press
            import asyncio

            await asyncio.sleep(0.05)

            # Verify stop_dialing was called
            assert len(stop_called) > 0
