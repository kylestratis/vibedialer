# VibeDialer

A war dialer TUI application for sequential phone number dialing with modem, VoIP, and simulation backends. Written for the Practical Data Discord Vibecoding Hackathon almost entirely on a phone from a children's birthday party and, later, a brewery mostly using voice with Wispr Flow.

## Installation

### Install as a tool with uv (Recommended)

```bash
# From the project directory
uv tool install .

# Then run with
uvx vibedialer
```

### Alternative: Install with uv pip

```bash
# From the project directory
uv pip install .

# Or install in editable mode for development
uv pip install -e .
```

### Install from Git (Future)

```bash
# Once published, you'll be able to install directly from GitHub
uv tool install git+https://github.com/kylestratis/vibedialer.git
```

## Usage

After installation, you can run VibeDialer in several ways:

### Quick Start - Interactive TUI (Default)

```bash
# Launch the TUI interface (default behavior)
uvx vibedialer

# Or if installed with uv pip
vibedialer
```

The TUI allows you to enter phone numbers, configure backends, and manage dialing sessions interactively.

### Advanced Usage - dial command

For more control and CLI mode, use the `dial` command:

```bash
# Interactive TUI mode with specific number pattern
vibedialer dial 555-12

# Non-interactive CLI mode
vibedialer dial 555-12 --no-interactive

# With specific backend
vibedialer dial 555-12 --backend modem --modem-port /dev/ttyUSB0

# With VoIP backend
vibedialer dial 555-12 --backend voip \
  --twilio-account-sid YOUR_SID \
  --twilio-auth-token YOUR_TOKEN \
  --twilio-from-number +15551234567

# Limit TUI to first 25 numbers (useful for testing)
vibedialer dial 555-12 --tui-limit 25

# Random order dialing
vibedialer dial 555-12 --random

# Save to SQLite
vibedialer dial 555-12 --storage sqlite --output results.db

# Resume from previous session
vibedialer dial --resume results.csv --infer-prefix

# Show version
vibedialer --version

# Show help
vibedialer --help
```

### As a Python module

```bash
# Run as a module
python -m vibedialer

# Or with uv
uv run python -m vibedialer
```

### In development (without installation)

```bash
# Using uv (from project directory)
uv run vibedialer

# With specific dial command
uv run vibedialer dial 555-12
```

## Features

### TUI Features
- **Vaporwave-styled interface** with animated telephone keypad
- **Progress indicator** showing `[X/Y]` current/total numbers
- **Pause/Resume** button for temporary suspension
- **Hang Up** button to stop dialing immediately
- **Real-time results** table with status updates
- **Backend switching** between Simulation, Modem, VoIP, and IP Relay
- **No hardcoded limits** - dials all generated numbers by default

### Telephony Backends
1. **Simulation** - Testing with weighted probabilities
2. **Modem** - Real hardware modem via serial port
3. **VoIP** - Twilio integration with AMD and FFT analysis
4. **IP Relay** - Stub implementation (not recommended)

### Storage Options
- **CSV** - Simple comma-separated values
- **SQLite** - Full database with session tracking
- **Dry-run** - Logging only, no file output

### Advanced Features
- **Country-specific validation** (USA, Canada, UK, Germany, France, Japan, Australia)
- **Answering Machine Detection** (VoIP backend)
- **FFT audio analysis** for modem/fax tone detection
- **Session management** with auto-generated or custom IDs
- **Resume capability** for interrupted scans
- **Random or sequential** dialing order

## CLI Options

### Key Flags

- `--interactive` / `--no-interactive` - Enable/disable TUI mode
- `--tui-limit N` - Limit TUI to first N numbers (0 = no limit)
- `--random` / `--sequential` - Dialing order
- `--backend [simulation|modem|voip|iprelay]` - Backend type
- `--storage [csv|sqlite|dry-run]` - Storage type
- `--output FILE` - Output file path
- `--resume FILE` - Resume from previous session
- `--session-id ID` - Specify session ID
- `--country-code CODE` - Country code (1=USA/Canada, 44=UK, etc.)

### Modem Options
- `--modem-port PORT` - Serial port (e.g., /dev/ttyUSB0, COM1)
- `--modem-baudrate RATE` - Baud rate (default: 57600)

### VoIP Options
- `--twilio-account-sid SID` - Twilio Account SID
- `--twilio-auth-token TOKEN` - Twilio Auth Token
- `--twilio-from-number NUMBER` - Twilio phone number (E.164 format)
- `--twilio-twiml-url URL` - Optional TwiML URL

## Examples

### Test with simulation backend
```bash
vibedialer dial 555-12 --tui-limit 10
```

### Production scan with modem
```bash
vibedialer dial 555-12 --backend modem \
  --modem-port /dev/ttyUSB0 \
  --storage sqlite \
  --output scan_results.db
```

### VoIP scan with Twilio
```bash
vibedialer dial 555-1 --backend voip \
  --twilio-account-sid AC... \
  --twilio-auth-token ... \
  --twilio-from-number +15551234567 \
  --storage sqlite \
  --output twilio_scan.db \
  --tui-limit 50
```

### Resume interrupted session
```bash
vibedialer dial --resume scan_results.db \
  --continue-session \
  --backend modem \
  --modem-port /dev/ttyUSB0
```

## Development

### Run tests
```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/test_tui.py -v

# With coverage
uv run coverage run -m pytest
uv run coverage report
```

### Code formatting
```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check

# Auto-fix issues
uv run ruff check --fix
```

## Project Structure

```
vibedialer/
    vibedialer/          # Main package
        __init__.py
        __main__.py      # Module entry point
        cli.py           # CLI interface
        tui.py           # TUI interface
        dialer.py        # Core dialing logic
        backends.py      # Telephony backends
        storage.py       # Storage backends
        validation.py    # Phone number validation
        session.py       # Session management
        resume.py        # Resume functionality
        audio_analysis.py # FFT audio analysis
        art.py           # ASCII art
    tests/               # Test suite
    pyproject.toml       # Project configuration
    README.md           # This file
```

## License

See LICENSE file for details.

## Documentation

For detailed information on specific topics, see the following guides:

- **[Backends](docs/BACKENDS.md)** - Telephony backend configuration (Simulation, Modem, VoIP, IP Relay)
- **[Dialing](docs/DIALING.md)** - Phone number dialing guide, country codes, and session tracking
- **[Storage](docs/STORAGE.md)** - Storage backend options (CSV, SQLite, Dry-run) and resuming sessions

## Safety Notes

- **Legal compliance**: Ensure you have permission to dial numbers in your jurisdiction
- **N11 blocking**: Service codes (911, 411, etc.) are automatically blocked for USA/NANP
- **Rate limiting**: Consider adding delays between calls to avoid being flagged
- **Cost tracking**: VoIP backends may incur charges - use `--tui-limit` for testing
- **Do-not-call lists**: Respect local do-not-call registries

## Contributing

1. Use test-driven development (TDD)
2. Use `uv` for dependency management
3. Run `pytest` before committing
4. Use `ruff` for formatting and linting
5. Follow conventional commits

## Version

Current version: 0.1.0
