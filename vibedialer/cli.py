"""Command-line interface for VibeDialer."""

from typing import Annotated

import typer
from rich.console import Console

from vibedialer import __version__
from vibedialer.art import display_keypad, display_welcome_screen
from vibedialer.tui import VibeDialerApp

console = Console()

app = typer.Typer(
    name="vibedialer",
    help="A war dialer TUI application for sequential phone number dialing.",
    add_completion=False,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"vibedialer version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = None,
) -> None:
    """VibeDialer - A war dialer TUI application."""
    pass


@app.command()
def dial(
    phone_number: Annotated[
        str,
        typer.Argument(help="Phone number or partial phone number to dial"),
    ],
    interactive: Annotated[
        bool,
        typer.Option(
            "--interactive/--no-interactive",
            "-i/-I",
            help="Launch interactive TUI mode",
        ),
    ] = True,
    random: Annotated[
        bool,
        typer.Option(
            "--random/--sequential",
            "-r/-s",
            help=(
                "Dial numbers in random order (--random) or "
                "sequential order (--sequential)"
            ),
        ),
    ] = False,
    show_welcome: Annotated[
        bool,
        typer.Option(
            "--show-welcome/--no-welcome",
            "-w/-W",
            help="Show welcome screen before launching TUI",
        ),
    ] = False,
) -> None:
    """
    Dial a phone number or range of numbers.

    If a partial number is provided, VibeDialer will generate and dial
    all possible numbers in either sequential or random order.
    """
    if interactive:
        # Optionally show welcome screen
        if show_welcome:
            display_welcome_screen(console)
            import time

            time.sleep(2)  # Brief pause to show the welcome screen

        # Launch the TUI
        tui_app = VibeDialerApp()
        tui_app.phone_number = phone_number
        tui_app.randomize = random
        tui_app.run()
    else:
        # Simple non-interactive mode (placeholder for now)
        mode = "random" if random else "sequential"
        typer.echo(f"Dialing {phone_number} in {mode} order...")
        typer.echo("Non-interactive mode not yet implemented.")


@app.command()
def welcome() -> None:
    """Display the welcome screen with vaporwave banner."""
    display_welcome_screen(console)


@app.command()
def keypad() -> None:
    """Display the telephone keypad ASCII art."""
    display_keypad(console)


if __name__ == "__main__":
    app()
