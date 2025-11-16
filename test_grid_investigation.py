"""Test to investigate Grid layout issues in status sections."""

import pytest
from textual.app import App
from vibedialer.ui.tui import MainMenuScreen, DialingScreen


@pytest.mark.asyncio
async def test_main_menu_status_grid_layout():
    """Investigate the MainMenuScreen status grid layout."""
    from textual.widgets import Label
    from textual.containers import Grid

    app = App()
    async with app.run_test(size=(120, 40)):
        menu_screen = MainMenuScreen()
        await app.push_screen(menu_screen)

        # Find the status grid
        status_area = app.screen.query_one("#status-area")
        print(f"\n=== MainMenuScreen Status Area ===")
        print(f"Status area exists: {status_area is not None}")

        # Find grid with class "status-grid-menu"
        grids = status_area.query(".status-grid-menu")
        print(f"Number of grids with 'status-grid-menu' class: {len(grids)}")

        if grids:
            grid = grids[0]
            print(f"Grid type: {type(grid)}")
            print(f"Grid styles: {grid.styles}")

            # Get all labels in the grid
            labels = grid.query(Label)
            print(f"Number of labels in grid: {len(labels)}")

            for i, label in enumerate(labels):
                print(f"  Label {i}: id='{label.id}', classes={label.classes}, text='{str(label.render())[:30]}'")

        # Check individual status labels
        try:
            status_pattern = app.screen.query_one("#status-pattern")
            print(f"\nStatus pattern label: '{str(status_pattern.render())}'")
        except Exception as e:
            print(f"Error finding status-pattern: {e}")

        try:
            status_backend = app.screen.query_one("#status-backend")
            print(f"Status backend label: '{str(status_backend.render())}'")
        except Exception as e:
            print(f"Error finding status-backend: {e}")


@pytest.mark.asyncio
async def test_dialing_screen_status_grid_layout():
    """Investigate the DialingScreen status grid layout."""
    from textual.widgets import Label
    from textual.containers import Grid

    app = App()
    async with app.run_test(size=(120, 40)):
        dialing_screen = DialingScreen(phone_number="555-1234", auto_start=False)
        await app.push_screen(dialing_screen)

        # Find the status section
        status_section = app.screen.query_one("#status-section")
        print(f"\n=== DialingScreen Status Section ===")
        print(f"Status section exists: {status_section is not None}")

        # Find grid with class "status-grid"
        grids = status_section.query(".status-grid")
        print(f"Number of grids with 'status-grid' class: {len(grids)}")

        if grids:
            grid = grids[0]
            print(f"Grid type: {type(grid)}")
            print(f"Grid styles: {grid.styles}")

            # Get all labels in the grid
            labels = grid.query(Label)
            print(f"Number of labels in grid: {len(labels)}")

            for i, label in enumerate(labels):
                print(f"  Label {i}: id='{label.id}', classes={label.classes}, text='{str(label.render())[:30]}'")

        # Check individual status labels
        try:
            current_backend = app.screen.query_one("#current-backend")
            print(f"\nCurrent backend label: '{str(current_backend.render())}'")
            print(f"  Classes: {current_backend.classes}")
            print(f"  Styles: width={current_backend.styles.width}, display={current_backend.styles.display}")
        except Exception as e:
            print(f"Error finding current-backend: {e}")

        try:
            current_pattern = app.screen.query_one("#current-pattern")
            print(f"Current pattern label: '{str(current_pattern.render())}'")
            print(f"  Classes: {current_pattern.classes}")
        except Exception as e:
            print(f"Error finding current-pattern: {e}")

        try:
            current_status = app.screen.query_one("#current-status")
            print(f"Current status label: '{str(current_status.render())}'")
            print(f"  Classes: {current_status.classes}")
        except Exception as e:
            print(f"Error finding current-status: {e}")


@pytest.mark.asyncio
async def test_main_menu_config_area_visibility():
    """Test that configuration area is actually rendered and positioned."""
    app = App()
    async with app.run_test(size=(120, 40)):
        menu_screen = MainMenuScreen()
        await app.push_screen(menu_screen)

        print(f"\n=== MainMenuScreen Config Area ===")

        # Check if config area exists
        config_area = app.screen.query_one("#config-area")
        print(f"Config area exists: {config_area is not None}")
        print(f"Config area styles: {config_area.styles}")

        # Check all config controls
        controls = [
            "#backend-select",
            "#storage-select",
            "#output-file-input",
            "#country-code-input",
            "#tui-limit-input",
            "#random-mode-switch",
        ]

        for control_id in controls:
            try:
                control = app.screen.query_one(control_id)
                print(f"{control_id}: exists={control is not None}, type={type(control).__name__}")
            except Exception as e:
                print(f"{control_id}: ERROR - {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_main_menu_status_grid_layout())
    asyncio.run(test_dialing_screen_status_grid_layout())
    asyncio.run(test_main_menu_config_area_visibility())
