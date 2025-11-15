"""Command-line interface for VibeDialer."""

from typing import Annotated

import typer
from rich.console import Console

from vibedialer import __version__
from vibedialer.art import display_keypad, display_welcome_screen
from vibedialer.backends import BackendType
from vibedialer.resume import prepare_resume
from vibedialer.storage import StorageType
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
    backend: Annotated[
        str,
        typer.Option(
            "--backend",
            "-b",
            help="Telephony backend to use (modem, voip, iprelay, simulation)",
        ),
    ] = "simulation",
    modem_port: Annotated[
        str,
        typer.Option(
            "--modem-port",
            help="Serial port for modem backend (e.g., /dev/ttyUSB0, COM1)",
        ),
    ] = "/dev/ttyUSB0",
    modem_baudrate: Annotated[
        int,
        typer.Option(
            "--modem-baudrate",
            help="Baud rate for modem connection",
        ),
    ] = 57600,
    storage: Annotated[
        str,
        typer.Option(
            "--storage",
            "-s",
            help="Storage backend for results (csv, sqlite, dry-run)",
        ),
    ] = "csv",
    output_file: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output file for CSV or database for SQLite",
        ),
    ] = "",
    resume_file: Annotated[
        str,
        typer.Option(
            "--resume",
            help="Resume from a previous session (CSV or SQLite file)",
        ),
    ] = "",
    resume_prefix: Annotated[
        str,
        typer.Option(
            "--resume-prefix",
            help="Prefix to resume dialing (will infer if not provided)",
        ),
    ] = "",
    infer_prefix: Annotated[
        bool,
        typer.Option(
            "--infer-prefix",
            help="Infer pattern from resume file and ask for confirmation",
        ),
    ] = False,
) -> None:
    """
    Dial a phone number or range of numbers.

    If a partial number is provided, VibeDialer will generate and dial
    all possible numbers in either sequential or random order.
    """
    # Parse backend type
    try:
        backend_type = BackendType(backend.lower())
    except ValueError as e:
        typer.echo(
            f"Error: Invalid backend '{backend}'. "
            f"Choose from: modem, voip, iprelay, simulation",
            err=True,
        )
        raise typer.Exit(1) from e

    # Parse storage type
    try:
        storage_type = StorageType(storage.lower())
    except ValueError as e:
        typer.echo(
            f"Error: Invalid storage '{storage}'. Choose from: csv, sqlite, dry-run",
            err=True,
        )
        raise typer.Exit(1) from e

    # Prepare backend kwargs
    backend_kwargs = {}
    if backend_type == BackendType.MODEM:
        backend_kwargs = {
            "port": modem_port,
            "baudrate": modem_baudrate,
        }

    # Prepare storage kwargs
    storage_kwargs = {}
    if output_file:
        if storage_type == StorageType.CSV:
            storage_kwargs["filename"] = output_file
        elif storage_type == StorageType.SQLITE:
            storage_kwargs["database"] = output_file

    # Handle resume mode
    resume_numbers = None
    if resume_file:
        try:
            # Prepare resume with optional prefix
            resume_prefix_val = resume_prefix if resume_prefix else None

            inferred_prefix, remaining, total, dialed = prepare_resume(
                resume_file, resume_prefix_val, random
            )

            # If infer_prefix flag is set, ask for confirmation
            if infer_prefix and not resume_prefix:
                typer.echo(f"\nInferred pattern from {resume_file}: {inferred_prefix}")
                typer.echo(f"  Total numbers in pattern: {total}")
                typer.echo(f"  Already dialed: {dialed}")
                typer.echo(f"  Remaining to dial: {len(remaining)}")
                typer.echo()

                confirm = typer.confirm("Continue with this pattern?")
                if not confirm:
                    typer.echo("Resume cancelled.")
                    raise typer.Exit(0)

            # Use the remaining numbers
            resume_numbers = remaining
            phone_number = inferred_prefix  # Set for display purposes

            typer.echo(
                f"\nResuming from {resume_file}: "
                f"{len(remaining)} numbers remaining (pattern: {inferred_prefix})"
            )

        except (FileNotFoundError, ValueError) as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1) from e

    if interactive:
        # Optionally show welcome screen
        if show_welcome:
            display_welcome_screen(console)
            import time

            time.sleep(2)  # Brief pause to show the welcome screen

        # Launch the TUI
        tui_app = VibeDialerApp(
            backend_type=backend_type,
            backend_kwargs=backend_kwargs,
            storage_type=storage_type,
            storage_kwargs=storage_kwargs,
            resume_numbers=resume_numbers,
        )
        tui_app.phone_number = phone_number
        tui_app.randomize = random

        try:
            tui_app.run()
        finally:
            # Ensure cleanup happens even on error or user interrupt
            if hasattr(tui_app, "dialer") and tui_app.dialer:
                tui_app.dialer.cleanup()
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
