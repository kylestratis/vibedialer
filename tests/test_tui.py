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
