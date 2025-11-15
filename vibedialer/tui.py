"""Textual TUI interface for VibeDialer."""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
    Switch,
)

from vibedialer.art import get_telephone_keypad
from vibedialer.dialer import PhoneDialer


class VibeDialerApp(App):
    """A Textual app for war dialing phone numbers."""

    CSS = """
    Screen {
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

    TITLE = "VibeDialer"
    SUB_TITLE = "War Dialer TUI"

    def __init__(self, *args, **kwargs):
        """Initialize the VibeDialer app."""
        super().__init__(*args, **kwargs)
        self.phone_number = ""
        self.randomize = False
        self.dialer = PhoneDialer()
        self.title = "VibeDialer"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container(id="main-container"):
            # Display telephone keypad at the top
            with Vertical(id="keypad-section"):
                yield Static(get_telephone_keypad())

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
                with Horizontal(id="mode-section"):
                    yield Label("Random Mode:")
                    yield Switch(id="random-mode-switch", value=self.randomize)
                with Horizontal(id="controls"):
                    yield Button("Start Dialing", id="start-btn", variant="primary")
                    yield Button("Stop", id="stop-btn", variant="error")
                    yield Button("Clear Results", id="clear-btn")

            with Vertical(id="results-section"):
                yield Label("Dial Results:")
                yield DataTable(id="results-table")

        yield Footer()

    def on_mount(self) -> None:
        """Set up the app when it mounts."""
        table = self.query_one("#results-table", DataTable)
        table.add_columns("Phone Number", "Status", "Timestamp")
        table.cursor_type = "row"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "start-btn":
            self.start_dialing()
        elif event.button.id == "stop-btn":
            self.stop_dialing()
        elif event.button.id == "clear-btn":
            self.clear_results()

    def start_dialing(self) -> None:
        """Start the dialing sequence."""
        phone_input = self.query_one("#phone-input", Input)
        phone_number = phone_input.value.strip()

        if not phone_number:
            return

        # Get random mode setting from switch
        random_switch = self.query_one("#random-mode-switch", Switch)
        randomize = random_switch.value

        # Generate numbers to dial
        numbers = self.dialer.generate_numbers(phone_number, randomize=randomize)

        # For now, just show the first few as a demo
        # In a real implementation, this would be async and incremental
        table = self.query_one("#results-table", DataTable)
        current_number_label = self.query_one("#current-number", Label)
        current_status_label = self.query_one("#current-status", Label)

        for number in numbers[:10]:  # Limit to first 10 for demo
            # Update status display with current number being dialed
            current_number_label.update(number)
            current_status_label.update("Dialing...")
            current_status_label.remove_class(
                "status-ringing",
                "status-busy",
                "status-modem",
                "status-person",
                "status-error",
                "status-no_answer",
            )

            result = self.dialer.dial(number)

            # Update status display with result
            status_display = self._format_status_display(result.status)
            current_status_label.update(status_display)
            current_status_label.add_class(f"status-{result.status}")

            # Add to results table
            table.add_row(
                result.phone_number,
                status_display,
                result.timestamp,
            )

        # Reset status display
        current_number_label.update("---")
        current_status_label.update("Complete")
        current_status_label.remove_class(
            "status-ringing",
            "status-busy",
            "status-modem",
            "status-person",
            "status-error",
            "status-no_answer",
        )

    def _format_status_display(self, status: str) -> str:
        """
        Format status for display.

        Args:
            status: Raw status string

        Returns:
            Formatted status string
        """
        status_map = {
            "ringing": "🔔 Ringing",
            "busy": "📵 Busy",
            "modem": "💻 Modem Found!",
            "person": "👤 Person",
            "error": "❌ Error",
            "no_answer": "📭 No Answer",
        }
        return status_map.get(status, status.title())

    def stop_dialing(self) -> None:
        """Stop the current dialing sequence."""
        # Placeholder for stopping logic
        pass

    def clear_results(self) -> None:
        """Clear the results table."""
        table = self.query_one("#results-table", DataTable)
        table.clear()
        self.dialer.results.clear()

        # Reset status display
        current_number_label = self.query_one("#current-number", Label)
        current_status_label = self.query_one("#current-status", Label)
        current_number_label.update("---")
        current_status_label.update("Idle")
        current_status_label.remove_class(
            "status-ringing",
            "status-busy",
            "status-modem",
            "status-person",
            "status-error",
            "status-no_answer",
        )


def run_tui(phone_number: str = "") -> None:
    """Run the TUI application."""
    app = VibeDialerApp()
    app.phone_number = phone_number
    app.run()
