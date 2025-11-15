"""Tests for the CLI interface."""

from typer.testing import CliRunner

from vibedialer.cli import app

runner = CliRunner()


def test_cli_help():
    """Test that the CLI help command works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "vibedialer" in result.stdout.lower() or "Usage" in result.stdout


def test_cli_version():
    """Test that the CLI version command works."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_cli_dial_command_exists():
    """Test that the dial command exists."""
    result = runner.invoke(app, ["dial", "--help"])
    assert result.exit_code == 0
    assert "dial" in result.stdout.lower()


def test_cli_dial_with_phone_number():
    """Test that we can invoke dial with a phone number."""
    # Use --no-interactive to avoid launching the TUI
    result = runner.invoke(app, ["dial", "555-1234", "--no-interactive"])
    # Should not crash, but might not do much yet
    assert result.exit_code == 0


def test_cli_dial_with_random_flag():
    """Test that the --random flag is accepted."""
    result = runner.invoke(app, ["dial", "555-1234", "--no-interactive", "--random"])
    assert result.exit_code == 0


def test_cli_dial_with_sequential_flag():
    """Test that the --sequential flag is accepted."""
    result = runner.invoke(
        app, ["dial", "555-1234", "--no-interactive", "--sequential"]
    )
    assert result.exit_code == 0


def test_cli_dial_random_flag_in_help():
    """Test that random/sequential options appear in help."""
    result = runner.invoke(app, ["dial", "--help"])
    assert result.exit_code == 0
    # Should show the random/sequential option
    assert "random" in result.stdout.lower() or "sequential" in result.stdout.lower()
