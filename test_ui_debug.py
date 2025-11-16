"""Debug script to test UI layout issues."""

from textual.app import App
from textual.containers import Grid, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Label, Static


class TestApp(App):
    """Test app to debug layout issues."""

    CSS = """
    #main-container {
        width: 100%;
        height: 100%;
    }

    #content {
        width: 100%;
        height: auto;
        padding: 2;
    }

    #section-1 {
        height: auto;
        padding: 2;
        margin-bottom: 1;
        border: solid green;
        background: $boost;
    }

    #section-2 {
        height: auto;
        padding: 2;
        margin-bottom: 1;
        border: solid cyan;
        background: $boost;
    }

    #section-3 {
        height: auto;
        padding: 2;
        margin-bottom: 1;
        border: solid yellow;
        background: $boost;
    }

    .status-grid {
        grid-size: 2 4;
        grid-gutter: 1 0;
        width: 100%;
        height: auto;
    }

    .status-label {
        width: 15;
        text-align: right;
        padding-right: 1;
    }

    .status-value {
        width: 1fr;
    }
    """

    def compose(self):
        """Compose the test UI."""
        yield Header()
        with VerticalScroll(id="main-container"):
            with Vertical(id="content"):
                # Section 1
                with Vertical(id="section-1"):
                    yield Label("Section 1: Instructions")
                    for i in range(20):
                        yield Label(f"Line {i + 1}")

                # Section 2: Status with Grid
                with Vertical(id="section-2"):
                    yield Label("Section 2: Current Status (Grid)")
                    with Grid(classes="status-grid"):
                        yield Label("Backend:", classes="status-label")
                        yield Label("SIMULATION", classes="status-value")
                        yield Label("Pattern:", classes="status-label")
                        yield Label("555-1234", classes="status-value")
                        yield Label("Number:", classes="status-label")
                        yield Label("(waiting)", classes="status-value")
                        yield Label("Status:", classes="status-label")
                        yield Label("Ready", classes="status-value")

                # Section 3: More content
                with Vertical(id="section-3"):
                    yield Label("Section 3: Configuration")
                    for i in range(10):
                        yield Label(f"Config option {i + 1}")

                # Bottom marker
                yield Static("=== BOTTOM BORDER SHOULD BE VISIBLE ABOVE THIS ===")

        yield Footer()


if __name__ == "__main__":
    app = TestApp()
    app.run()
