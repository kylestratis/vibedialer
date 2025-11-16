"""Textual TUI interface for VibeDialer."""

import asyncio

from textual.app import App, ComposeResult
from textual.containers import Center, Container, Grid, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Select,
    Static,
    Switch,
)

from vibedialer.art import (
    get_telephone_keypad,
    get_telephone_keypad_with_highlight,
    get_welcome_banner,
)
from vibedialer.backends import BackendType
from vibedialer.dialer import PhoneDialer
from vibedialer.storage import StorageType
from vibedialer.validation import CountryCode


class WelcomeScreen(Screen):
    """Welcome screen with vaporwave banner."""

    CSS = """
    WelcomeScreen {
        align: center middle;
        background: $surface;
    }

    #welcome-container {
        width: auto;
        height: auto;
        padding: 2;
    }

    #continue-btn {
        margin-top: 2;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets for the welcome screen."""
        with Center():
            with Vertical(id="welcome-container"):
                yield Static(get_welcome_banner(), id="welcome-banner")
                yield Button("Continue", id="continue-btn", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press to continue to main menu."""
        if event.button.id == "continue-btn":
            self.app.push_screen("menu")


class InteractiveDialpad(Static):
    """An interactive telephone dialpad with clickable buttons."""

    CSS = """
    InteractiveDialpad {
        width: auto;
        height: auto;
        padding: 1;
    }

    .dialpad-grid {
        grid-size: 3 4;
        grid-gutter: 1;
        width: auto;
        height: auto;
    }

    .dialpad-button {
        width: 9;
        height: 3;
        min-width: 9;
        min-height: 3;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the interactive dialpad layout."""
        with Container():
            yield Label("📞 Interactive Dialpad", id="dialpad-title")
            with Grid(classes="dialpad-grid"):
                # Row 1: 1, 2, 3
                yield Button("1", id="dial-1", classes="dialpad-button")
                yield Button("2\nABC", id="dial-2", classes="dialpad-button")
                yield Button("3\nDEF", id="dial-3", classes="dialpad-button")
                # Row 2: 4, 5, 6
                yield Button("4\nGHI", id="dial-4", classes="dialpad-button")
                yield Button("5\nJKL", id="dial-5", classes="dialpad-button")
                yield Button("6\nMNO", id="dial-6", classes="dialpad-button")
                # Row 3: 7, 8, 9
                yield Button("7\nPRS", id="dial-7", classes="dialpad-button")
                yield Button("8\nTUV", id="dial-8", classes="dialpad-button")
                yield Button("9\nWXY", id="dial-9", classes="dialpad-button")
                # Row 4: *, 0, #
                yield Button("*", id="dial-star", classes="dialpad-button")
                yield Button("0\n+", id="dial-0", classes="dialpad-button")
                yield Button("#", id="dial-hash", classes="dialpad-button")


class MainMenuScreen(Screen):
    """Main menu screen for entering phone pattern."""

    CSS = """
    MainMenuScreen {
        background: $surface;
    }

    #menu-container {
        width: 100%;
        height: 100%;
        padding: 2;
    }

    #instructions {
        height: auto;
        padding: 1;
        margin-bottom: 1;
        border: solid $accent;
        background: $boost;
    }

    #input-area {
        height: auto;
        padding: 2;
        border: solid $primary;
    }

    #dialpad-section {
        width: auto;
        height: auto;
        margin-top: 2;
    }

    #pattern-display {
        color: $success;
        text-style: bold;
        margin: 1 0;
    }

    .button-row {
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, *args, **kwargs):
        """Initialize the main menu screen."""
        super().__init__(*args, **kwargs)
        self.phone_pattern = ""

    def compose(self) -> ComposeResult:
        """Create child widgets for the main menu."""
        yield Header()
        with Container(id="menu-container"):
            # Instructions section
            with Vertical(id="instructions"):
                yield Label("Welcome to VibeDialer!", id="title")
                yield Label("")
                yield Label("📋 Pattern Requirements:")
                yield Label(
                    "  • Enter a partial phone number "
                    "(e.g., 555-12 or 555-1234)"
                )
                yield Label("  • Use '-' as a wildcard for any digit")
                yield Label(
                    "  • Example: '555-12' will dial "
                    "555-1200 through 555-1299"
                )
                yield Label(
                    "  • Example: '555-1234' will dial "
                    "just that specific number"
                )
                yield Label("")
                yield Label("💡 Input Methods:")
                yield Label("  • Type directly in the text field below, OR")
                yield Label("  • Click the dialpad buttons to build your pattern")

            # Input section
            with Vertical(id="input-area"):
                yield Label("Current Pattern:", id="pattern-label")
                yield Label("(empty)", id="pattern-display")
                yield Label("")
                yield Label("Text Input:")
                yield Input(
                    placeholder="e.g., 555-12 or 555-1234",
                    id="pattern-input",
                )

                # Interactive dialpad
                with Center(id="dialpad-section"):
                    yield InteractiveDialpad()

                # Control buttons
                with Horizontal(classes="button-row"):
                    yield Button("Clear", id="clear-btn", variant="warning")
                    yield Button("Backspace", id="backspace-btn")
                    yield Button(
                        "Continue to Dialing",
                        id="start-dial-btn",
                        variant="success",
                    )

        yield Footer()

    def on_mount(self) -> None:
        """Focus the input when screen mounts."""
        self.query_one("#pattern-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Update pattern display when text input changes."""
        if event.input.id == "pattern-input":
            self.phone_pattern = event.value
            self._update_pattern_display()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        # Handle dialpad button presses
        if button_id and button_id.startswith("dial-"):
            digit = (
                button_id.replace("dial-", "")
                .replace("star", "*")
                .replace("hash", "#")
            )
            # Map digit buttons to actual digits
            digit_map = {
                "0": "0", "1": "1", "2": "2", "3": "3", "4": "4",
                "5": "5", "6": "6", "7": "7", "8": "8", "9": "9",
                "*": "*", "#": "#"
            }
            if digit in digit_map:
                self._add_digit(digit_map[digit])

        # Handle control buttons
        elif button_id == "clear-btn":
            self._clear_pattern()
        elif button_id == "backspace-btn":
            self._backspace()
        elif button_id == "start-dial-btn":
            if self.phone_pattern:
                # Switch to dialing screen with the pattern
                self.app.switch_screen("dialing")

    def _add_digit(self, digit: str) -> None:
        """Add a digit to the pattern."""
        pattern_input = self.query_one("#pattern-input", Input)
        pattern_input.value = pattern_input.value + digit
        self.phone_pattern = pattern_input.value
        self._update_pattern_display()

    def _backspace(self) -> None:
        """Remove last character from pattern."""
        pattern_input = self.query_one("#pattern-input", Input)
        if pattern_input.value:
            pattern_input.value = pattern_input.value[:-1]
            self.phone_pattern = pattern_input.value
            self._update_pattern_display()

    def _clear_pattern(self) -> None:
        """Clear the entire pattern."""
        pattern_input = self.query_one("#pattern-input", Input)
        pattern_input.value = ""
        self.phone_pattern = ""
        self._update_pattern_display()

    def _update_pattern_display(self) -> None:
        """Update the pattern display label."""
        pattern_display = self.query_one("#pattern-display", Label)
        if self.phone_pattern:
            pattern_display.update(self.phone_pattern)
        else:
            pattern_display.update("(empty)")


class DialingScreen(Screen):
    """Main dialing screen with keypad and results."""

    CSS = """
    DialingScreen {
        background: $surface;
    }

    #main-container {
        width: 100%;
        height: 100%;
        padding: 1;
    }

    #keypad-section {
        height: auto;
        padding: 0 1;
        margin-bottom: 1;
        align: center middle;
    }

    #input-section {
        height: auto;
        padding: 1;
        border: solid $primary;
    }

    #results-section {
        height: 1fr;
        padding: 1;
        margin-top: 1;
        border: solid $primary;
    }

    #controls {
        height: auto;
        margin-top: 1;
    }

    Input {
        margin: 1 0;
    }

    Button {
        margin: 0 1;
    }

    DataTable {
        height: 100%;
    }

    Label {
        margin: 1 0;
    }

    Switch {
        margin: 1 0;
    }

    #mode-section {
        height: auto;
        margin-top: 1;
    }

    #backend-section {
        height: auto;
        margin-top: 1;
    }

    Select {
        width: 30;
    }

    #status-section {
        height: auto;
        padding: 1;
        margin-bottom: 1;
        border: solid $accent;
        background: $boost;
    }

    #current-number {
        color: $success;
        text-style: bold;
        margin: 0 1;
    }

    #current-status {
        margin: 0 1;
    }

    .status-ringing {
        color: $warning;
    }

    .status-busy {
        color: $error;
    }

    .status-modem {
        color: $success;
        text-style: bold;
    }

    .status-person {
        color: $accent;
    }

    .status-error {
        color: $error;
        text-style: bold;
    }

    .status-no_answer {
        color: $text-muted;
    }
    """

    def __init__(
        self,
        backend_type: BackendType = BackendType.SIMULATION,
        backend_kwargs: dict | None = None,
        storage_type: StorageType = StorageType.CSV,
        storage_kwargs: dict | None = None,
        resume_numbers: list[str] | None = None,
        country_code: CountryCode | str = CountryCode.USA,
        session_id: str | None = None,
        tui_limit: int | None = None,
        phone_number: str = "",
        randomize: bool = False,
        *args,
        **kwargs,
    ):
        """Initialize the dialing screen."""
        super().__init__(*args, **kwargs)
        self.phone_number = phone_number
        self.randomize = randomize
        self.backend_type = backend_type
        self.backend_kwargs = backend_kwargs or {}
        self.storage_type = storage_type
        self.storage_kwargs = storage_kwargs or {}
        self.resume_numbers = resume_numbers
        self.country_code = country_code
        self.session_id = session_id
        self.tui_limit = tui_limit
        self.dialer = PhoneDialer(
            backend_type=backend_type,
            storage_type=storage_type,
            country_code=country_code,
            session_id=session_id,
            phone_pattern=self.phone_number,
            randomize=self.randomize,
            **{**self.backend_kwargs, **self.storage_kwargs},
        )
        self.is_dialing = False
        self.is_paused = False

    def compose(self) -> ComposeResult:
        """Create child widgets for the dialing screen."""
        yield Header()
        with Container(id="main-container"):
            # Display telephone keypad at the top
            with Vertical(id="keypad-section"):
                yield Static(get_telephone_keypad(), id="keypad-display")

            # Status display section
            with Vertical(id="status-section"):
                yield Label("Current Status:", id="status-header")
                with Horizontal():
                    yield Label("Number:", id="number-label")
                    yield Label("---", id="current-number")
                with Horizontal():
                    yield Label("Status:", id="status-label")
                    yield Label("Idle", id="current-status")

            with Vertical(id="input-section"):
                yield Label("Enter phone number or partial number:")
                yield Input(
                    placeholder="e.g., 555-12 or 555-1234",
                    id="phone-input",
                    value=self.phone_number,
                )
                with Horizontal(id="backend-section"):
                    yield Label("Backend:")
                    yield Select(
                        options=[
                            ("Simulation", BackendType.SIMULATION),
                            ("Modem", BackendType.MODEM),
                            ("VoIP", BackendType.VOIP),
                            ("IP Relay", BackendType.IP_RELAY),
                        ],
                        value=self.backend_type,
                        id="backend-select",
                        allow_blank=False,
                    )
                with Horizontal(id="mode-section"):
                    yield Label("Random Mode:")
                    yield Switch(id="random-mode-switch", value=self.randomize)
                with Horizontal(id="controls"):
                    yield Button("Start Dialing", id="start-btn", variant="primary")
                    yield Button("Pause", id="pause-btn", variant="warning")
                    yield Button("Hang Up", id="stop-btn", variant="error")
                    yield Button("Clear Results", id="clear-btn")
                    yield Button("Back to Menu", id="menu-btn")

            with Vertical(id="results-section"):
                yield Label("Dial Results:")
                yield DataTable(id="results-table")

        yield Footer()

    def on_mount(self) -> None:
        """Set up the screen when it mounts."""
        table = self.query_one("#results-table", DataTable)
        table.add_columns("Phone Number", "Status", "Timestamp")
        table.cursor_type = "row"

    def on_unmount(self) -> None:
        """Clean up when the screen unmounts."""
        if hasattr(self, "dialer") and self.dialer:
            self.dialer.cleanup()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "start-btn":
            if self.is_paused:
                self.resume_dialing()
            else:
                self.run_worker(self.start_dialing())
        elif event.button.id == "pause-btn":
            self.pause_dialing()
        elif event.button.id == "stop-btn":
            self.stop_dialing()
        elif event.button.id == "clear-btn":
            self.clear_results()
        elif event.button.id == "menu-btn":
            # Go back to main menu
            self.app.pop_screen()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle backend selection changes."""
        if event.select.id == "backend-select" and event.value is not Select.BLANK:
            self.dialer.cleanup()
            self.backend_type = event.value
            self.dialer = PhoneDialer(
                backend_type=self.backend_type,
                storage_type=self.storage_type,
                country_code=self.country_code,
                **{**self.backend_kwargs, **self.storage_kwargs},
            )

    async def animate_keypad_for_number(self, phone_number: str) -> None:
        """Animate the keypad by highlighting each digit."""
        keypad_display = self.query_one("#keypad-display", Static)
        digits = "".join(c for c in phone_number if c in "0123456789*#")
        for digit in digits:
            keypad_display.update(get_telephone_keypad_with_highlight(digit))
            await asyncio.sleep(0.1)
        await asyncio.sleep(0.2)
        keypad_display.update(get_telephone_keypad())

    async def start_dialing(self) -> None:
        """Start the dialing sequence."""
        phone_input = self.query_one("#phone-input", Input)
        phone_number = phone_input.value.strip()

        if not phone_number and not self.resume_numbers:
            return

        self.is_dialing = True
        self.is_paused = False

        start_btn = self.query_one("#start-btn", Button)
        pause_btn = self.query_one("#pause-btn", Button)
        start_btn.disabled = True
        pause_btn.disabled = False

        random_switch = self.query_one("#random-mode-switch", Switch)
        randomize = random_switch.value

        if self.resume_numbers:
            numbers = self.resume_numbers
            self.resume_numbers = None
        else:
            numbers = self.dialer.generate_numbers(phone_number, randomize=randomize)

        if self.tui_limit is not None and self.tui_limit > 0:
            numbers = numbers[: self.tui_limit]

        total_numbers = len(numbers)
        table = self.query_one("#results-table", DataTable)
        current_number_label = self.query_one("#current-number", Label)
        current_status_label = self.query_one("#current-status", Label)

        batch_size = 5
        for i, number in enumerate(numbers, 1):
            if not self.is_dialing:
                break

            while self.is_paused and self.is_dialing:
                await asyncio.sleep(0.1)

            if not self.is_dialing:
                break

            progress = f"[{i}/{total_numbers}]"
            current_number_label.update(f"{progress} {number}")
            current_status_label.update("Dialing...")
            current_status_label.remove_class(
                "status-ringing", "status-busy", "status-modem",
                "status-person", "status-error", "status-no_answer",
            )

            await self.animate_keypad_for_number(number)
            result = self.dialer.dial(number)

            status_display = self._format_status_display(result.status)
            current_status_label.update(status_display)
            current_status_label.add_class(f"status-{result.status}")

            display_message = f"{status_display} - {result.message}"
            table.add_row(result.phone_number, display_message, result.timestamp)

            await asyncio.sleep(0.3)
            if i % batch_size == 0:
                await asyncio.sleep(0.05)

        current_number_label.update("---")
        final_status = "Stopped" if not self.is_dialing else "Complete"
        current_status_label.update(final_status)
        current_status_label.remove_class(
            "status-ringing", "status-busy", "status-modem",
            "status-person", "status-error", "status-no_answer",
        )

        self.is_dialing = False
        self.is_paused = False
        start_btn.disabled = False
        pause_btn.disabled = True
        pause_btn.label = "Pause"

    def _format_status_display(self, status: str) -> str:
        """Format status for display."""
        status_map = {
            "ringing": "🔔 Ringing",
            "busy": "📵 Busy",
            "modem": "💻 Modem Found!",
            "person": "👤 Person",
            "error": "❌ Error",
            "no_answer": "📭 No Answer",
        }
        return status_map.get(status, status.title())

    def pause_dialing(self) -> None:
        """Pause the current dialing sequence."""
        if not self.is_dialing or self.is_paused:
            return

        self.is_paused = True
        try:
            current_status_label = self.query_one("#current-status", Label)
            current_status_label.update("Paused")
            current_status_label.remove_class(
                "status-ringing", "status-busy", "status-modem",
                "status-person", "status-error", "status-no_answer",
            )
            pause_btn = self.query_one("#pause-btn", Button)
            pause_btn.label = "Resume"
            pause_btn.variant = "success"
        except Exception:
            pass

    def resume_dialing(self) -> None:
        """Resume dialing after pause."""
        if not self.is_paused:
            return

        self.is_paused = False
        try:
            current_status_label = self.query_one("#current-status", Label)
            current_status_label.update("Resuming...")
            pause_btn = self.query_one("#pause-btn", Button)
            pause_btn.label = "Pause"
            pause_btn.variant = "warning"
        except Exception:
            pass

    def stop_dialing(self) -> None:
        """Stop the current dialing sequence."""
        self.is_dialing = False
        self.is_paused = False

        if self.dialer.backend:
            try:
                self.dialer.backend.hangup()
            except Exception:
                pass

        if hasattr(self.dialer.backend, "_wait_for_pending_analyses"):
            try:
                self.dialer.backend._wait_for_pending_analyses(timeout=2.0)
            except Exception:
                pass

        if self.dialer.storage:
            try:
                self.dialer.storage.flush()
            except Exception:
                pass

        try:
            current_status_label = self.query_one("#current-status", Label)
            current_status_label.update("Stopped")
            current_status_label.remove_class(
                "status-ringing", "status-busy", "status-modem",
                "status-person", "status-error", "status-no_answer",
            )
            start_btn = self.query_one("#start-btn", Button)
            pause_btn = self.query_one("#pause-btn", Button)
            start_btn.disabled = False
            pause_btn.disabled = True
            pause_btn.label = "Pause"
            pause_btn.variant = "warning"
        except Exception:
            pass

    def clear_results(self) -> None:
        """Clear the results table."""
        table = self.query_one("#results-table", DataTable)
        table.clear()
        self.dialer.results.clear()

        current_number_label = self.query_one("#current-number", Label)
        current_status_label = self.query_one("#current-status", Label)
        current_number_label.update("---")
        current_status_label.update("Idle")
        current_status_label.remove_class(
            "status-ringing", "status-busy", "status-modem",
            "status-person", "status-error", "status-no_answer",
        )


class VibeDialerApp(App):
    """A Textual app for war dialing phone numbers with screen-based navigation."""

    TITLE = "VibeDialer"
    SUB_TITLE = "War Dialer TUI"

    # Install screens
    SCREENS = {
        "welcome": WelcomeScreen,
        "menu": MainMenuScreen,
        "dialing": DialingScreen,
    }

    def __init__(
        self,
        backend_type: BackendType = BackendType.SIMULATION,
        backend_kwargs: dict | None = None,
        storage_type: StorageType = StorageType.CSV,
        storage_kwargs: dict | None = None,
        resume_numbers: list[str] | None = None,
        country_code: CountryCode | str = CountryCode.USA,
        session_id: str | None = None,
        tui_limit: int | None = None,
        phone_number: str = "",
        randomize: bool = False,
        *args,
        **kwargs,
    ):
        """Initialize the VibeDialer app."""
        super().__init__(*args, **kwargs)
        self.phone_number = phone_number
        self.randomize = randomize
        self.backend_type = backend_type
        self.backend_kwargs = backend_kwargs or {}
        self.storage_type = storage_type
        self.storage_kwargs = storage_kwargs or {}
        self.resume_numbers = resume_numbers
        self.country_code = country_code
        self.session_id = session_id
        self.tui_limit = tui_limit

    def on_mount(self) -> None:
        """Set up the app when it mounts - start with welcome screen."""
        self.push_screen("welcome")

    def switch_screen(self, screen_name: str) -> None:
        """Switch to a different screen, passing pattern from menu to dialing."""
        if screen_name == "dialing":
            # Get the pattern from the menu screen
            menu_screen = self.screen
            if isinstance(menu_screen, MainMenuScreen):
                pattern = menu_screen.phone_pattern

                # Create and install the dialing screen with the pattern
                dialing_screen = DialingScreen(
                    backend_type=self.backend_type,
                    backend_kwargs=self.backend_kwargs,
                    storage_type=self.storage_type,
                    storage_kwargs=self.storage_kwargs,
                    resume_numbers=self.resume_numbers,
                    country_code=self.country_code,
                    session_id=self.session_id,
                    tui_limit=self.tui_limit,
                    phone_number=pattern,
                    randomize=self.randomize,
                )
                # Push the dialing screen
                self.push_screen(dialing_screen)


def run_tui(phone_number: str = "") -> None:
    """Run the TUI application."""
    app = VibeDialerApp()
    app.phone_number = phone_number
    app.run()
