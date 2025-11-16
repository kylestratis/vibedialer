"""Tests for TUI layout and display issues."""

import pytest

from vibedialer.ui.tui import MainMenuScreen, VibeDialerApp


@pytest.mark.asyncio
async def test_main_menu_all_sections_present():
    """Test that all sections are present in the main menu."""
    app = VibeDialerApp()
    async with app.run_test():
        menu_screen = MainMenuScreen()
        await app.push_screen(menu_screen)

        # Verify all main sections exist
        assert app.screen.query_one("#instructions") is not None
        assert app.screen.query_one("#input-area") is not None
        assert app.screen.query_one("#config-area") is not None
        assert app.screen.query_one("#actions-area") is not None


@pytest.mark.asyncio
async def test_main_menu_config_section_has_all_controls():
    """Test that configuration section has all expected controls."""
    app = VibeDialerApp()
    async with app.run_test():
        menu_screen = MainMenuScreen()
        await app.push_screen(menu_screen)

        # Verify all configuration controls exist
        assert app.screen.query_one("#backend-select") is not None
        assert app.screen.query_one("#storage-select") is not None
        assert app.screen.query_one("#output-file-input") is not None
        assert app.screen.query_one("#country-code-input") is not None
        assert app.screen.query_one("#tui-limit-input") is not None
        assert app.screen.query_one("#random-mode-switch") is not None


@pytest.mark.asyncio
async def test_main_menu_pattern_display_shows_initial_state():
    """Test that pattern display shows '(empty)' initially."""
    app = VibeDialerApp()
    async with app.run_test():
        menu_screen = MainMenuScreen()
        await app.push_screen(menu_screen)

        # Pattern display should show (empty) initially
        pattern_display = app.screen.query_one("#pattern-display")
        assert pattern_display is not None
        pattern_text = str(pattern_display.render())
        assert "(empty)" in pattern_text


@pytest.mark.asyncio
async def test_main_menu_validation_feedback_shows_initial_state():
    """Test that validation feedback shows initial message."""
    app = VibeDialerApp()
    async with app.run_test():
        menu_screen = MainMenuScreen()
        await app.push_screen(menu_screen)

        # Validation feedback should show initial prompt
        feedback = app.screen.query_one("#validation-feedback")
        assert feedback is not None
        feedback_text = str(feedback.render())
        assert len(feedback_text) > 0  # Should have some content


@pytest.mark.asyncio
async def test_main_menu_input_has_placeholder():
    """Test that pattern input has a placeholder."""
    app = VibeDialerApp()
    async with app.run_test():
        menu_screen = MainMenuScreen()
        await app.push_screen(menu_screen)

        # Pattern input should have placeholder
        pattern_input = app.screen.query_one("#pattern-input")
        assert pattern_input is not None
        assert pattern_input.placeholder is not None
        assert len(str(pattern_input.placeholder)) > 0


@pytest.mark.asyncio
async def test_main_menu_has_status_section():
    """Test that main menu has a status section."""
    app = VibeDialerApp()
    async with app.run_test():
        menu_screen = MainMenuScreen()
        await app.push_screen(menu_screen)

        # Should have status area
        status_area = app.screen.query_one("#status-area")
        assert status_area is not None


@pytest.mark.asyncio
async def test_main_menu_status_shows_pattern():
    """Test that status section shows the current pattern."""
    app = VibeDialerApp()
    async with app.run_test():
        menu_screen = MainMenuScreen()
        await app.push_screen(menu_screen)

        # Status should show pattern
        status_pattern = app.screen.query_one("#status-pattern")
        assert status_pattern is not None
        # Initially should be "(empty)"
        assert "(empty)" in str(status_pattern.render())


@pytest.mark.asyncio
async def test_main_menu_status_shows_backend():
    """Test that status section shows the current backend."""
    from vibedialer.backends import BackendType

    app = VibeDialerApp()
    async with app.run_test():
        menu_screen = MainMenuScreen(backend_type=BackendType.SIMULATION)
        await app.push_screen(menu_screen)

        # Status should show backend
        status_backend = app.screen.query_one("#status-backend")
        assert status_backend is not None
        assert "Simulation" in str(status_backend.render())


@pytest.mark.asyncio
async def test_main_menu_status_shows_storage():
    """Test that status section shows the current storage type."""
    from vibedialer.storage import StorageType

    app = VibeDialerApp()
    async with app.run_test():
        menu_screen = MainMenuScreen(storage_type=StorageType.CSV)
        await app.push_screen(menu_screen)

        # Status should show storage
        status_storage = app.screen.query_one("#status-storage")
        assert status_storage is not None
        assert "CSV" in str(status_storage.render())


@pytest.mark.asyncio
async def test_main_menu_status_updates_when_pattern_changes():
    """Test that status pattern updates when user enters a pattern."""
    from textual.widgets import Input

    app = VibeDialerApp()
    async with app.run_test():
        menu_screen = MainMenuScreen()
        await app.push_screen(menu_screen)

        # Get pattern input
        pattern_input = app.screen.query_one("#pattern-input", Input)
        status_pattern = app.screen.query_one("#status-pattern")

        # Change pattern
        pattern_input.value = "555"
        # Trigger update manually
        menu_screen.phone_pattern = "555"
        menu_screen._update_pattern_display()

        # Status should update
        assert "555" in str(status_pattern.render())
