# VibeDialer: Phone Number Dialing Guide

This guide explains how to dial phone numbers and ranges using VibeDialer, including phone number validation and country code support.

## Table of Contents

- [Quick Start](#quick-start)
- [Telephony Backends](#telephony-backends)
- [Phone Number Formats](#phone-number-formats)
- [Range Dialing](#range-dialing)
- [Country Code Support](#country-code-support)
- [Session Tracking](#session-tracking)
- [Validation Rules](#validation-rules)
- [Examples](#examples)

## Quick Start

### Launch the TUI (Default)

```bash
# Launch the interactive TUI - configure all settings in the interface
vibedialer
```

### Dial a Single Number

```bash
vibedialer dial 555-234-5678
```

### Dial a Range of Numbers

```bash
# Dial all numbers from 555-234-5600 to 555-234-5699
vibedialer dial 555-234-56
```

### Dial with Country Code

```bash
# Dial UK numbers
vibedialer dial --country-code 44 2012345678
```

## Telephony Backends

VibeDialer supports multiple telephony backends for actually placing calls. Choose the backend that best suits your needs.

### Simulation (Default)

The simulation backend is perfect for testing and development. It simulates dial results without making real calls.

```bash
# Simulation is the default
vibedialer dial 555-234-56

# Or explicitly specify
vibedialer dial --backend simulation 555-234-56
```

**Features**:
- No real calls made
- Randomized realistic responses
- Various statuses (busy, no answer, modem, person)
- Free to use

### Twilio VoIP

Make real phone calls using Twilio's Voice API. Requires a Twilio account.

#### Setup

1. Create a Twilio account at [https://www.twilio.com/](https://www.twilio.com/)
2. Get your Account SID and Auth Token from the Twilio Console
3. Purchase or verify a Twilio phone number
4. Use the credentials with VibeDialer

#### Usage

```bash
vibedialer dial \
  --backend voip \
  --twilio-account-sid "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" \
  --twilio-auth-token "your_auth_token_here" \
  --twilio-from-number "+15551234567" \
  555-234-56
```

**Features**:
- Real phone calls via Twilio
- Carrier detection (modem vs voice)
- Call duration tracking
- Detailed call logs
- Pay-per-use pricing

**Optional Parameters**:
- `--twilio-twiml-url`: Custom TwiML URL for call instructions (default uses Twilio demo)

#### Modem Carrier Detection

Twilio VoIP backend attempts to detect modem carriers by analyzing call duration:
- Calls lasting less than 3 seconds are flagged as potential modem carriers
- Modems typically disconnect quickly after handshake
- Voice calls usually last longer

#### Pricing

Twilio charges per minute for outbound calls. Costs vary by destination:
- **USA**: ~$0.013/min
- **Canada**: ~$0.013/min
- **UK**: ~$0.024/min
- **Other countries**: Varies

Visit [Twilio Pricing](https://www.twilio.com/voice/pricing) for current rates.

⚠️ **Important**: War dialing can incur significant costs. Always:
- Start with small test ranges
- Monitor your Twilio usage dashboard
- Set up billing alerts
- Use simulation mode for testing

### Modem

Use a physical Hayes-compatible modem connected to your computer.

```bash
vibedialer dial \
  --backend modem \
  --modem-port /dev/ttyUSB0 \
  --modem-baudrate 57600 \
  555-234-56
```

**Features**:
- Direct modem connection
- Audio carrier detection
- Modem tone analysis
- No per-call costs (only phone line charges)

**Requirements**:
- Hayes-compatible modem
- Serial port connection (USB-to-Serial adapter supported)
- Active phone line

### Backend Comparison

| Backend    | Real Calls | Cost        | Setup Complexity | Carrier Detection |
|------------|------------|-------------|------------------|-------------------|
| Simulation | No         | Free        | None             | Simulated         |
| Twilio VoIP| Yes        | Pay-per-use | Easy             | Duration-based    |
| Modem      | Yes        | Phone line  | Moderate         | Audio analysis    |

## Phone Number Formats

### USA/Canada (NANP)

VibeDialer defaults to USA/Canada phone number format (North American Numbering Plan - NANP):

- **Format**: `NXX-NXX-XXXX`
- **Length**: 10 digits (area code + exchange + subscriber)
- **Area Code**: First digit must be 2-9 (not 0 or 1)
- **Exchange**: First digit must be 2-9 (not 0 or 1)
- **Country Code**: `1`

**Valid Examples**:
- `555-234-5678`
- `212-555-9999`
- `+1-800-234-5678`

**Invalid Examples**:
- `155-234-5678` (area code starts with 1)
- `555-156-7890` (exchange starts with 1)
- `911-234-5678` (N11 service code)

### Other Countries

VibeDialer supports multiple country codes:

- **UK** (`44`): 10 digits after country code
- **Germany** (`49`): 10-11 digits after country code
- **France** (`33`): Variable length
- **Japan** (`81`): Variable length
- **Australia** (`61`): Variable length

## Range Dialing

Range dialing allows you to dial multiple phone numbers by providing a partial number pattern. VibeDialer will generate all possible combinations and dial them in sequence.

### How It Works

When you provide a partial number, VibeDialer:

1. **Validates** the partial pattern
2. **Generates** all possible completions
3. **Filters** out invalid numbers
4. **Dials** each valid number in sequence (or random order)

### Pattern Examples

#### Last 2 Digits (100 numbers)

```bash
# Dials: 555-234-5600 through 555-234-5699
vibedialer dial 555-234-56
```

#### Last 3 Digits (1,000 numbers)

```bash
# Dials: 555-234-5000 through 555-234-5999
vibedialer dial 555-234-5
```

#### Last 4 Digits (10,000 numbers)

```bash
# Dials: 555-234-0000 through 555-234-9999
vibedialer dial 555-234
```

#### Minimum Pattern Length

For USA/NANP numbers, you must provide at least the area code (3 digits):

```bash
# Valid: includes area code
vibedialer dial 555

# Invalid: too short
vibedialer dial 55  # Error: Pattern must include at least area code
```

### Sequential vs Random Order

By default, numbers are dialed in sequential order. Use `--random` to randomize:

```bash
# Sequential (default): 555-234-5600, 555-234-5601, 555-234-5602, ...
vibedialer dial 555-234-56

# Random: 555-234-5642, 555-234-5601, 555-234-5688, ...
vibedialer dial --random 555-234-56
```

## Country Code Support

### Specifying Country Code

Use the `--country-code` (or `-c`) flag to specify the country:

```bash
# USA/Canada (default)
vibedialer dial 555-234-5678

# UK
vibedialer dial --country-code 44 2012345678

# Germany
vibedialer dial --country-code 49 3012345678
```

### Supported Country Codes

| Country       | Code | Format Notes                        |
|---------------|------|-------------------------------------|
| USA/Canada    | 1    | 10 digits (NXX-NXX-XXXX)           |
| UK            | 44   | 10 digits after country code       |
| Germany       | 49   | 10-11 digits after country code    |
| France        | 33   | Variable length                    |
| Japan         | 81   | Variable length                    |
| Australia     | 61   | Variable length                    |

## Session Tracking

VibeDialer tracks each war dialing session with a unique session ID, making it easy to analyze results and resume interrupted sessions.

### What is a Session?

A **session** represents a single war dialing operation. Each session has:
- **Session ID**: A unique 8-character identifier (e.g., `a3f5c2d1`)
- **Metadata**: Backend type, storage type, phone pattern, statistics
- **Results**: All dial results grouped by session ID

### Session IDs

Session IDs are short, unique identifiers that group related dial results together:

```bash
# Auto-generated session ID
vibedialer dial 555-234-56
# Session ID: a3f5c2d1 (auto-generated)

# Manually specify session ID
vibedialer dial --session-id mysession1 555-234-56
# Session ID: mysession1 (your choice)
```

#### Session ID Format

- **Auto-generated**: 8 characters from UUID4 (e.g., `a3f5c2d1`)
- **Manual**: Any string you provide (e.g., `office-scan-2025`)

### Session Metadata

VibeDialer tracks comprehensive metadata for each session:

| Field              | Description                                    |
|--------------------|------------------------------------------------|
| session_id         | Unique identifier                              |
| start_time         | When the session started (ISO 8601)            |
| end_time           | When the session ended (ISO 8601)              |
| backend_type       | Backend used (simulation, voip, modem)         |
| storage_type       | Storage backend (csv, sqlite)                  |
| phone_pattern      | Pattern being dialed (e.g., "555-234-56")      |
| total_calls        | Total number of calls made                     |
| successful_calls   | Number of successful calls                     |
| modem_detections   | Number of modem carriers detected              |
| country_code       | Country code used (e.g., "1" for USA)          |
| randomized         | Whether numbers were dialed in random order    |

**Note**: Session metadata is only saved when using SQLite storage. CSV storage only includes session_id in each result row.

### Continuing Sessions

By default, when resuming from a file, VibeDialer continues the previous session:

```bash
# Initial session
vibedialer dial --storage sqlite --output calls.db 555-234-56
# Session ID: a3f5c2d1 (auto-generated)

# Resume later - continues same session
vibedialer dial --resume calls.db --infer-prefix
# Session ID: a3f5c2d1 (continued from previous session)
```

### Starting a New Session on Resume

To force a new session when resuming:

```bash
# Force new session even when resuming
vibedialer dial --resume calls.db --infer-prefix --new-session
# Session ID: b7e9f4a2 (new session)
```

### Session CLI Flags

| Flag                 | Description                                              | Default    |
|----------------------|----------------------------------------------------------|------------|
| `--session-id`       | Manually specify session ID                              | Auto-gen   |
| `--continue-session` | Continue previous session when resuming                  | True       |
| `--new-session`      | Force new session even when resuming                     | False      |

### Session Data Storage

#### CSV Storage

CSV files include `session_id` as the first column:

```csv
session_id,phone_number,status,timestamp,success,message,carrier_detected,tone_type
a3f5c2d1,555-234-5600,busy,2025-11-16T14:30:00,False,Busy signal,False,
a3f5c2d1,555-234-5601,modem,2025-11-16T14:30:01,True,Modem detected,True,modem
```

You can filter results by session:

```bash
# Filter results for specific session
grep "a3f5c2d1" results.csv
```

#### SQLite Storage

SQLite databases store session metadata in a dedicated `sessions` table:

```sql
-- View all sessions
SELECT * FROM sessions;

-- View results for specific session
SELECT * FROM dial_results WHERE session_id = 'a3f5c2d1';

-- Session statistics
SELECT
    session_id,
    phone_pattern,
    total_calls,
    successful_calls,
    modem_detections
FROM sessions;
```

### Analyzing Sessions

#### Query Session Results (SQLite)

```bash
# Open SQLite database
sqlite3 calls.db

# List all sessions
SELECT session_id, phone_pattern, total_calls, modem_detections
FROM sessions
ORDER BY start_time DESC;

# Get all modem hits for a session
SELECT phone_number, timestamp, message
FROM dial_results
WHERE session_id = 'a3f5c2d1' AND status = 'modem';

# Compare sessions
SELECT session_id, backend_type, total_calls,
       (successful_calls * 100.0 / total_calls) as success_rate
FROM sessions;
```

#### Session Report Example

```bash
# Session: a3f5c2d1
# Pattern: 555-234-56 (100 numbers)
# Backend: Twilio VoIP
# Started: 2025-11-16T14:30:00
# Ended:   2025-11-16T14:45:00
#
# Results:
#   Total calls:       100
#   Successful:         45 (45%)
#   Modem detections:    5 (5%)
#   Busy:               20 (20%)
#   No answer:          30 (30%)
#   Errors:              5 (5%)
```

### Best Practices

1. **Use SQLite for Session Metadata**: CSV only stores session_id, not full metadata
2. **Name Sessions Meaningfully**: Use `--session-id office-scan-2025-11-16` for clarity
3. **Continue Sessions on Resume**: Default behavior maintains session continuity
4. **Query Sessions Regularly**: Use SQLite queries to track progress
5. **Group Related Scans**: Use same session ID for related scanning operations

## Validation Rules

### USA/NANP Rules

VibeDialer enforces strict validation for USA/NANP numbers:

1. **Area Code Restrictions**:
   - First digit must be 2-9
   - Cannot be N11 service codes (211, 311, 411, 511, 611, 711, 811, 911)

2. **Exchange Code Restrictions**:
   - First digit must be 2-9

3. **Total Length**:
   - Must be exactly 10 digits

### Pattern Validation

When using range dialing, VibeDialer validates the pattern before generating numbers:

```bash
# Valid pattern
vibedialer dial 555-234     # ✓ Valid area code and exchange

# Invalid patterns
vibedialer dial 155-234     # ✗ Area code starts with 1
vibedialer dial 555-156     # ✗ Exchange starts with 1
vibedialer dial 911-234     # ✗ N11 service code
vibedialer dial 55          # ✗ Too short (need at least area code)
```

### Invalid Number Skipping

When generating a range, VibeDialer automatically skips invalid numbers:

```bash
# Pattern: 555-234-5
# Generates: 555-234-5000 through 555-234-5999
# Skips any invalid combinations (though all should be valid here)
vibedialer dial 555-234-5
```

## Examples

### Example 1: Basic Range Dialing

Dial 100 numbers in a local exchange:

```bash
vibedialer dial 555-234-56
```

This generates and dials:
- `555-234-5600`
- `555-234-5601`
- `555-234-5602`
- ...
- `555-234-5699`

### Example 2: Random Order Dialing

Dial numbers in random order to avoid patterns:

```bash
vibedialer dial --random 555-234-56
```

### Example 3: Specify Backend

Dial using a real modem:

```bash
vibedialer dial --backend modem --modem-port /dev/ttyUSB0 555-234-56
```

### Example 4: Save Results

Save results to a CSV file:

```bash
vibedialer dial --storage csv --output results.csv 555-234-56
```

### Example 5: Resume Dialing

Resume from a previous session:

```bash
# Initial dial (gets interrupted)
vibedialer dial --output session1.csv 555-234-56

# Resume later
vibedialer dial --resume session1.csv --resume-prefix 555-234-56
```

Or let VibeDialer infer the pattern:

```bash
vibedialer dial --resume session1.csv --infer-prefix
```

### Example 6: UK Numbers

Dial UK numbers:

```bash
# Single UK number
vibedialer dial --country-code 44 2012345678

# Range of UK numbers
vibedialer dial --country-code 44 201234567
```

### Example 7: Non-Interactive Mode

Run without the TUI interface:

```bash
vibedialer dial --no-interactive 555-234-56
```

## Tips and Best Practices

### 1. Start Small

When testing, start with a small range to verify your setup:

```bash
# Just 10 numbers
vibedialer dial 555-234-560
```

### 2. Use Dry-Run Mode

Test without actually dialing:

```bash
vibedialer dial --storage dry-run 555-234-56
```

### 3. Save Results

Always save results for later analysis:

```bash
vibedialer dial --storage csv --output results.csv 555-234-56
```

### 4. Random Order for Stealth

Use random order to avoid detection:

```bash
vibedialer dial --random 555-234-56
```

### 5. Resume Long Sessions

For long dialing sessions, use resume functionality:

```bash
# Session 1
vibedialer dial --output session.db --storage sqlite 555-234

# Session 2 (resume)
vibedialer dial --resume session.db --infer-prefix
```

## Error Messages

### Common Validation Errors

| Error Message                                    | Cause                                      | Solution                          |
|--------------------------------------------------|--------------------------------------------|------------------------------------|
| `Pattern must include at least area code`        | Pattern too short                          | Provide at least 3 digits          |
| `Area code must start with 2-9`                  | Invalid area code                          | Use valid area code (200-999)      |
| `Exchange must start with 2-9`                   | Invalid exchange code                      | Use valid exchange (200-999)       |
| `Area code cannot be N11 service code`           | Tried to use 911, 411, etc.               | Use different area code            |
| `Number too short/long`                          | Invalid length for country                 | Check country format requirements  |

## Additional Resources

- [README.md](README.md) - Project overview and installation
- [CLAUDE.md](CLAUDE.md) - Development guidelines
- Run `vibedialer --help` for CLI reference
- Run `vibedialer dial --help` for dial command options
