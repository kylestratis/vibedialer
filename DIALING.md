# VibeDialer: Phone Number Dialing Guide

This guide explains how to dial phone numbers and ranges using VibeDialer, including phone number validation and country code support.

## Table of Contents

- [Quick Start](#quick-start)
- [Phone Number Formats](#phone-number-formats)
- [Range Dialing](#range-dialing)
- [Country Code Support](#country-code-support)
- [Validation Rules](#validation-rules)
- [Examples](#examples)

## Quick Start

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
