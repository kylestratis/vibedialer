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
