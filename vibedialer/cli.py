"""Command-line interface for VibeDialer."""

from typing import Annotated

import typer

from vibedialer import __version__
from vibedialer.tui import VibeDialerApp

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
) -> None:
    """
    Dial a phone number or range of numbers.

    If a partial number is provided, VibeDialer will generate and dial
    all possible numbers in either sequential or random order.
    """
    if interactive:
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


if __name__ == "__main__":
    app()
