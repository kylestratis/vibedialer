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
    # Use valid pattern: exchange must start with 2-9
    result = runner.invoke(
        app, ["dial", "555-234", "--no-interactive", "--storage", "dry-run"]
    )
    assert result.exit_code == 0


def test_cli_dial_with_random_flag():
    """Test that the --random flag is accepted."""
    result = runner.invoke(
        app,
        ["dial", "555-234", "--no-interactive", "--random", "--storage", "dry-run"],
    )
    assert result.exit_code == 0


def test_cli_dial_with_sequential_flag():
    """Test that the --sequential flag is accepted."""
    result = runner.invoke(
        app,
        ["dial", "555-234", "--no-interactive", "--sequential", "--storage", "dry-run"],
    )
    assert result.exit_code == 0


def test_cli_dial_random_flag_in_help():
    """Test that random/sequential options appear in help."""
    result = runner.invoke(app, ["dial", "--help"])
    assert result.exit_code == 0
    # Should show the random/sequential option
    assert "random" in result.stdout.lower() or "sequential" in result.stdout.lower()


def test_cli_welcome_command_exists():
    """Test that the welcome command exists."""
    result = runner.invoke(app, ["welcome", "--help"])
    assert result.exit_code == 0


def test_cli_keypad_command_exists():
    """Test that the keypad command exists."""
    result = runner.invoke(app, ["keypad", "--help"])
    assert result.exit_code == 0


def test_cli_welcome_command_runs():
    """Test that the welcome command runs without errors."""
    result = runner.invoke(app, ["welcome"])
    assert result.exit_code == 0


def test_cli_keypad_command_runs():
    """Test that the keypad command runs without errors."""
    result = runner.invoke(app, ["keypad"])
    assert result.exit_code == 0
    # Should contain some numbers
    assert any(str(i) in result.stdout for i in range(10))
