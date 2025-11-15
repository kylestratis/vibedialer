# Telephony Backends

VibeDialer supports multiple telephony backends for actual war dialing functionality.

## Backend Types

### 1. Simulation Backend (Default)

The simulation backend is used for testing and demonstration. It generates realistic simulated results without requiring any hardware.

**Usage:**
```bash
vibedialer dial 555-12 --backend simulation
```

**Characteristics:**
- No hardware required
- Weighted probability simulation
- Safe for testing

### 2. Dial-Up Modem Backend (Recommended for Real War Dialing)

The modem backend uses a physical dial-up modem connected via serial port to actually dial phone numbers.

**Requirements:**
- USB dial-up modem or serial modem
- pyserial library (already included)
- Appropriate permissions for serial port access

**Usage:**
```bash
# Default port (/dev/ttyUSB0)
vibedialer dial 555-12 --backend modem

# Custom port
vibedialer dial 555-12 --backend modem --modem-port /dev/ttyUSB1

# Custom baudrate
vibedialer dial 555-12 --backend modem --modem-baudrate 115200
```

**Supported Modems:**
- Most Hayes-compatible modems
- USB modems (often show as /dev/ttyUSBx on Linux)
- Internal modems (often /dev/ttyS0, /dev/ttyS1, etc.)

**AT Commands Used:**
- `ATZ` - Reset modem
- `ATE0` - Disable echo
- `ATX4` - Extended result codes
- `ATDT<number>` - Dial tone number
- `ATH0` - Hang up

**Response Codes:**
- `CONNECT` - Modem carrier detected
- `BUSY` - Line busy
- `NO CARRIER` - No answer/hung up
- `NO DIAL TONE` - Phone line problem
- `ERROR` - Command error

**Linux Serial Port Permissions:**
```bash
# Add your user to dialout group
sudo usermod -a -G dialout $USER

# Or use udev rules for specific device
sudo nano /etc/udev/rules.d/99-modem.rules
# Add: SUBSYSTEM=="tty", ATTRS{idVendor}=="xxxx", MODE="0666"
```

### 3. VoIP Backend (Stub - Not Implemented)

The VoIP backend is a placeholder for future SIP/VoIP integration.

**Status:** Stub implementation only

**Intended Features:**
- SIP registration
- RTP stream analysis
- Audio tone detection

**Usage:**
```bash
vibedialer dial 555-12 --backend voip \\
    --sip-server sip.example.com \\
    --sip-username user \\
    --sip-password pass
```

**Note:** Currently returns error messages indicating it's not implemented.

### 4. IP Relay Backend (Stub - Not Recommended)

The IP relay backend is a placeholder and **should not be used** for war dialing.

**Status:** Stub implementation only

**Why Not to Use:**
- IP relay services are for accessibility (deaf/hard-of-hearing users)
- Involves human operators
- Not suitable for automated dialing
- Likely violates terms of service

**Usage:**
```bash
# This will fail with an error message
vibedialer dial 555-12 --backend ip-relay
```

## Configuration

Backends can be configured via CLI flags or (in future versions) configuration files.

### CLI Flags

- `--backend <type>` - Backend type (simulation, modem, voip, ip-relay)
- `--modem-port <port>` - Serial port for modem
- `--modem-baudrate <rate>` - Baud rate for modem
- `--modem-timeout <seconds>` - Dial timeout in seconds
- `--sip-server <url>` - SIP server for VoIP
- `--sip-username <user>` - SIP username
- `--sip-password <pass>` - SIP password

## Examples

### Test with Simulation

```bash
vibedialer dial 555-00 --backend simulation --random
```

### Real War Dialing with Modem

```bash
# Find your modem port first
ls /dev/ttyUSB*

# Dial with modem
vibedialer dial 555-12 --backend modem --modem-port /dev/ttyUSB0

# Interactive TUI with modem
vibedialer dial 555-12 --backend modem --interactive
```

### Troubleshooting Modem

```bash
# Test modem connection
screen /dev/ttyUSB0 57600
# Type: ATZ (should return OK)
# Type: ATI (should return modem info)
# Ctrl+A, K to exit

# Check permissions
ls -l /dev/ttyUSB0

# Monitor modem output
tail -f /var/log/syslog | grep tty
```

## Legal and Ethical Considerations

**IMPORTANT:** War dialing may be illegal in your jurisdiction without proper authorization. Only use this tool:

- On phone lines you own or have explicit permission to test
- In compliance with local telecommunications laws
- For legitimate security research or testing purposes
- Not for harassment or unauthorized access

The authors of VibeDialer are not responsible for misuse of this software.
