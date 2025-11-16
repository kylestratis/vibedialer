"""Command-line interface for VibeDialer."""

from typing import Annotated

import typer
from rich.console import Console

from vibedialer import __version__
from vibedialer.art import display_keypad, display_welcome_screen
from vibedialer.backends import BackendType
from vibedialer.dialer import PhoneDialer
from vibedialer.resume import prepare_resume
from vibedialer.storage import StorageType
from vibedialer.tui import VibeDialerApp
from vibedialer.validation import CountryCode

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
    twilio_account_sid: Annotated[
        str,
        typer.Option(
            "--twilio-account-sid",
            help="Twilio Account SID (for VoIP backend)",
        ),
    ] = "",
    twilio_auth_token: Annotated[
        str,
        typer.Option(
            "--twilio-auth-token",
            help="Twilio Auth Token (for VoIP backend)",
        ),
    ] = "",
    twilio_from_number: Annotated[
        str,
        typer.Option(
            "--twilio-from-number",
            help="Twilio phone number to call from (E.164 format, e.g., +15551234567)",
        ),
    ] = "",
    twilio_twiml_url: Annotated[
        str,
        typer.Option(
            "--twilio-twiml-url",
            help="Optional TwiML URL for call instructions",
        ),
    ] = "",
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
    session_id: Annotated[
        str,
        typer.Option(
            "--session-id",
            help=(
                "Manually specify session ID for grouping results "
                "(auto-generated if not provided)"
            ),
        ),
    ] = "",
    continue_session: Annotated[
        bool,
        typer.Option(
            "--continue-session",
            help="Continue previous session (uses latest session ID from resume file)",
        ),
    ] = True,
    new_session: Annotated[
        bool,
        typer.Option(
            "--new-session",
            help="Force a new session even when resuming",
        ),
    ] = False,
    country_code: Annotated[
        str,
        typer.Option(
            "--country-code",
            "-c",
            help=(
                "Country code for phone number validation "
                "(1=USA/Canada, 44=UK, 49=Germany)"
            ),
        ),
    ] = "1",
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
    elif backend_type == BackendType.VOIP:
        # Twilio VoIP backend
        if not twilio_account_sid or not twilio_auth_token or not twilio_from_number:
            typer.echo(
                "Error: VoIP backend requires --twilio-account-sid, "
                "--twilio-auth-token, and --twilio-from-number",
                err=True,
            )
            raise typer.Exit(1)

        backend_kwargs = {
            "account_sid": twilio_account_sid,
            "auth_token": twilio_auth_token,
            "from_number": twilio_from_number,
        }
        if twilio_twiml_url:
            backend_kwargs["twiml_url"] = twilio_twiml_url

    # Prepare storage kwargs
    storage_kwargs = {}
    if output_file:
        if storage_type == StorageType.CSV:
            storage_kwargs["filename"] = output_file
        elif storage_type == StorageType.SQLITE:
            storage_kwargs["database"] = output_file

    # Validate and prepare country code
    country_code_val = country_code
    try:
        # Try to find matching CountryCode enum
        for cc in CountryCode:
            if cc.value == country_code:
                country_code_val = cc
                break
    except Exception:
        # If validation fails, let the dialer handle it
        pass

    # Handle resume mode
    resume_numbers = None
    resume_session_id = None
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

            # Get latest session ID if continuing session
            if continue_session and not new_session:
                # Try to get latest session ID from storage
                try:
                    from vibedialer.storage import create_storage

                    resume_storage_type = (
                        StorageType.SQLITE
                        if resume_file.endswith(".db")
                        else StorageType.CSV
                    )
                    resume_storage_kwargs = {}
                    if resume_storage_type == StorageType.SQLITE:
                        resume_storage_kwargs["database"] = resume_file
                    else:
                        resume_storage_kwargs["filename"] = resume_file

                    temp_storage = create_storage(
                        resume_storage_type, **resume_storage_kwargs
                    )

                    # Get latest session ID if storage supports it
                    if hasattr(temp_storage, "get_latest_session_id"):
                        resume_session_id = temp_storage.get_latest_session_id()
                        if resume_session_id:
                            typer.echo(
                                f"Continuing previous session: {resume_session_id}"
                            )

                    temp_storage.close()
                except Exception as e:
                    typer.echo(
                        f"Warning: Could not retrieve session ID from "
                        f"{resume_file}: {e}",
                        err=True,
                    )

            typer.echo(
                f"\nResuming from {resume_file}: "
                f"{len(remaining)} numbers remaining (pattern: {inferred_prefix})"
            )

        except (FileNotFoundError, ValueError) as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1) from e

    # Determine final session ID
    final_session_id = None
    if session_id:
        # Manually specified session ID takes precedence
        final_session_id = session_id
    elif new_session:
        # Force new session (will be auto-generated by PhoneDialer)
        final_session_id = None
    elif resume_session_id:
        # Use session ID from resume file
        final_session_id = resume_session_id
    # Otherwise, let PhoneDialer auto-generate

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
            country_code=country_code_val,
            session_id=final_session_id,
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
        # Non-interactive mode - dial numbers and display results in console
        mode = "random" if random else "sequential"
        typer.echo(f"Dialing {phone_number} in {mode} order...")
        typer.echo()

        # Create PhoneDialer with configured parameters
        dialer = PhoneDialer(
            backend_type=backend_type,
            storage_type=storage_type,
            country_code=country_code_val,
            session_id=final_session_id,
            phone_pattern=phone_number,
            randomize=random,
            **{**backend_kwargs, **storage_kwargs},
        )

        try:
            # Generate or use resume numbers
            if resume_numbers:
                numbers = resume_numbers
            else:
                # Validate phone number provided
                if not phone_number:
                    typer.echo("Error: Phone number is required", err=True)
                    raise typer.Exit(1)

                numbers = dialer.generate_numbers(phone_number, randomize=random)

            # Display session info
            typer.echo(f"Session ID: {dialer.session_id}")
            typer.echo(f"Backend: {backend_type.value}")
            typer.echo(f"Storage: {storage_type.value}")
            typer.echo(f"Numbers to dial: {len(numbers)}")
            typer.echo()

            # Track results for summary
            results_summary = {
                "total": len(numbers),
                "modem": 0,
                "person": 0,
                "busy": 0,
                "no_answer": 0,
                "error": 0,
            }

            # Dial each number
            for i, number in enumerate(numbers, 1):
                typer.echo(f"[{i}/{len(numbers)}] Dialing {number}...", nl=False)

                result = dialer.dial(number)

                # Display result with appropriate formatting
                status_emoji = {
                    "modem": "💻",
                    "person": "👤",
                    "busy": "📵",
                    "no_answer": "📭",
                    "ringing": "🔔",
                    "error": "❌",
                }

                emoji = status_emoji.get(result.status, "•")
                typer.echo(f" {emoji} {result.status.upper()}: {result.message}")

                # Update summary
                if result.status in results_summary:
                    results_summary[result.status] += 1

            # Display summary
            typer.echo()
            typer.echo("=" * 60)
            typer.echo("SUMMARY")
            typer.echo("=" * 60)
            typer.echo(f"Total numbers dialed: {results_summary['total']}")
            typer.echo(f"  💻 Modems found: {results_summary['modem']}")
            typer.echo(f"  👤 People answered: {results_summary['person']}")
            typer.echo(f"  📵 Busy signals: {results_summary['busy']}")
            typer.echo(f"  📭 No answer: {results_summary['no_answer']}")
            typer.echo(f"  ❌ Errors: {results_summary['error']}")
            typer.echo("=" * 60)
            typer.echo(f"Results saved to storage ({storage_type.value})")
            typer.echo()

        except KeyboardInterrupt:
            typer.echo()
            typer.echo("Dialing interrupted by user.")
        finally:
            # Ensure cleanup happens
            dialer.cleanup()
            typer.echo("Cleanup complete.")


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
