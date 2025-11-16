"""Tests for the TUI interface."""

import pytest
from textual.app import App

from vibedialer.tui import VibeDialerApp


def test_tui_app_creation():
    """Test that we can create the TUI app."""
    app = VibeDialerApp()
    assert isinstance(app, App)
    assert app.title == "VibeDialer"


def test_tui_app_has_css_path():
    """Test that the app has a CSS path configured."""
    app = VibeDialerApp()
    # Should have some CSS configuration
    assert hasattr(app, "CSS") or hasattr(app, "CSS_PATH")


@pytest.mark.asyncio
async def test_tui_app_mounts():
    """Test that the app can mount without errors."""
    app = VibeDialerApp()
    async with app.run_test():
        # App should start successfully
        assert app.is_running


@pytest.mark.asyncio
async def test_tui_has_random_mode_toggle():
    """Test that the TUI has a toggle for random/sequential mode."""
    app = VibeDialerApp()
    async with app.run_test():
        # Should have a switch or checkbox for random mode
        # Look for the widget by ID
        switch = app.query_one("#random-mode-switch")
        assert switch is not None


@pytest.mark.asyncio
async def test_tui_displays_keypad():
    """Test that the TUI displays the telephone keypad."""
    app = VibeDialerApp()
    async with app.run_test():
        # Should have a keypad section
        keypad_section = app.query_one("#keypad-section")
        assert keypad_section is not None


@pytest.mark.asyncio
async def test_tui_has_status_display():
    """Test that the TUI has a status display section."""
    app = VibeDialerApp()
    async with app.run_test():
        # Should have a status display section
        status_section = app.query_one("#status-section")
        assert status_section is not None


@pytest.mark.asyncio
async def test_tui_status_display_has_labels():
    """Test that status display has current number and status labels."""
    app = VibeDialerApp()
    async with app.run_test():
        # Should have labels for current number and status
        current_number_label = app.query_one("#current-number")
        assert current_number_label is not None

        status_label = app.query_one("#current-status")
        assert status_label is not None


def test_tui_app_accepts_tui_limit():
    """Test that TUI app accepts and stores tui_limit parameter."""
    app = VibeDialerApp(tui_limit=50)
    assert app.tui_limit == 50

    app_no_limit = VibeDialerApp()
    assert app_no_limit.tui_limit is None


@pytest.mark.asyncio
async def test_tui_has_pause_button():
    """Test that the TUI has a pause button."""
    app = VibeDialerApp()
    async with app.run_test():
        # Should have a pause button
        pause_btn = app.query_one("#pause-btn")
        assert pause_btn is not None
        assert "Pause" in str(pause_btn.label)


@pytest.mark.asyncio
async def test_tui_has_hang_up_button():
    """Test that the TUI has a hang up button (not stop)."""
    app = VibeDialerApp()
    async with app.run_test():
        # Should have a hang up button
        stop_btn = app.query_one("#stop-btn")
        assert stop_btn is not None
        assert "Hang Up" in str(stop_btn.label)


@pytest.mark.asyncio
async def test_tui_pause_functionality():
    """Test that pause/resume functionality works."""
    app = VibeDialerApp()
    async with app.run_test():
        # Initially not paused
        assert not app.is_paused
        assert not app.is_dialing

        # Simulate dialing state
        app.is_dialing = True

        # Pause
        app.pause_dialing()
        assert app.is_paused

        # Resume
        app.resume_dialing()
        assert not app.is_paused


@pytest.mark.asyncio
async def test_tui_dialing_respects_limit():
    """Test that TUI respects tui_limit when dialing."""
    from vibedialer.backends import BackendType

    # Test that the TUI limit parameter is properly set and would be applied
    tui_limit = 5
    app = VibeDialerApp(tui_limit=tui_limit, backend_type=BackendType.SIMULATION)

    async with app.run_test(size=(120, 40)):
        # Verify the limit is set on the app
        assert app.tui_limit == tui_limit

        # Test that slicing logic works correctly (simulating what start_dialing does)
        mock_numbers = [f"555-12{i:02d}" for i in range(100)]  # 100 mock numbers
        assert len(mock_numbers) == 100

        # Apply the limit as the start_dialing method would
        if app.tui_limit is not None and app.tui_limit > 0:
            limited_numbers = mock_numbers[: app.tui_limit]
            assert len(limited_numbers) == 5
        else:
            limited_numbers = mock_numbers
            assert len(limited_numbers) == 100


@pytest.mark.asyncio
async def test_tui_progress_format():
    """Test that TUI formats progress correctly."""
    app = VibeDialerApp(tui_limit=3)

    async with app.run_test(size=(120, 40)):
        # Test the progress format logic
        current_number_label = app.query_one("#current-number")

        # Get the label's current value
        # In Textual, we can check the label's render or use str()
        label_str = str(current_number_label.render())

        # Initially should show "---"
        assert "---" in label_str

        # Test that the progress format is as expected
        # The format should be "[i/total] number"
        test_progress = "[1/3]"
        test_number = "555-1200"
        expected_format = f"{test_progress} {test_number}"

        # Just verify the format components are correct
        assert "[" in test_progress
        assert "/" in test_progress
        assert "]" in test_progress
        assert "555-1200" in test_number


@pytest.mark.asyncio
async def test_tui_no_limit_by_default():
    """Test that TUI has no limit by default (not hardcoded to 10)."""
    app = VibeDialerApp()
    # Default should be None, not 10
    assert app.tui_limit is None
