"""Dial-up modem backend for VibeDialer."""

import logging
import time

import serial

from vibedialer.backends import DialResult, TelephonyBackend

logger = logging.getLogger(__name__)


class ModemBackend(TelephonyBackend):
    """Dial-up modem backend using AT commands via serial port."""

    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 57600,
        timeout: int = 30,
        enable_audio_analysis: bool = False,
    ):
        """
        Initialize modem backend.

        Args:
            port: Serial port path (e.g., '/dev/ttyUSB0', 'COM1')
            baudrate: Baud rate for serial connection (default: 57600)
            timeout: Timeout in seconds for dial attempts
            enable_audio_analysis: Enable advanced audio tone analysis
                (requires pyaudio)
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.enable_audio_analysis = enable_audio_analysis
        self.serial_conn: serial.Serial | None = None
        self._connected = False

    def connect(self) -> bool:
        """
        Connect to the modem via serial port.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=2,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )

            # Initialize modem
            if not self._send_command("ATZ"):  # Reset modem
                return False

            if not self._send_command("ATE0"):  # Disable echo
                return False

            if not self._send_command("ATQ0V1"):  # Enable verbal responses
                return False

            # Enable extended result codes for better status detection
            self._send_command("ATX4")

            self._connected = True
            logger.info(f"Connected to modem on {self.port}")
            return True

        except (serial.SerialException, OSError) as e:
            logger.error(f"Failed to connect to modem: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from the modem."""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.hangup()
                self.serial_conn.close()
                logger.info("Disconnected from modem")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
        self._connected = False

    def dial(self, phone_number: str) -> DialResult:
        """
        Dial a phone number using the modem.

        Args:
            phone_number: The phone number to dial

        Returns:
            DialResult with outcome of the dial attempt
        """
        if not self.is_connected():
            return DialResult(
                success=False,
                status="error",
                message="Not connected to modem",
            )

        try:
            # Clean phone number (remove formatting)
            clean_number = (
                phone_number.replace("-", "")
                .replace(" ", "")
                .replace("(", "")
                .replace(")", "")
            )

            # Send dial command (ATDT for tone dialing)
            dial_cmd = f"ATDT{clean_number}"
            logger.info(f"Dialing {phone_number}")

            if not self.serial_conn:
                return DialResult(
                    success=False,
                    status="error",
                    message="Serial connection not available",
                )

            self.serial_conn.write(f"{dial_cmd}\r".encode())

            # Wait for response with timeout
            start_time = time.time()
            response_lines = []
            ring_count = 0

            while time.time() - start_time < self.timeout:
                if self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode().strip()
                    if line:
                        response_lines.append(line)
                        logger.debug(f"Modem response: {line}")

                        # Count rings
                        if "RING" in line.upper():
                            ring_count += 1
                            logger.debug(f"Ring count: {ring_count}")

                        # Check for final result codes
                        result = self._parse_response(line, ring_count)
                        if result:
                            self.hangup()  # Hang up after getting result
                            return result

                time.sleep(0.1)

            # Timeout occurred
            self.hangup()
            timeout_message = "Dial timeout - no answer"
            if ring_count > 0:
                timeout_message = f"No answer after {ring_count} rings"
            return DialResult(
                success=False,
                status="ringing",
                message=timeout_message,
            )

        except Exception as e:
            logger.error(f"Error during dial: {e}")
            self.hangup()
            return DialResult(
                success=False,
                status="error",
                message=f"Dial error: {str(e)}",
            )

    def hangup(self) -> None:
        """Hang up the current call."""
        if not self.serial_conn or not self.serial_conn.is_open:
            return

        try:
            # Send hangup command
            time.sleep(0.5)
            self.serial_conn.write(b"+++")  # Escape to command mode
            time.sleep(1)
            self._send_command("ATH0")  # Hang up
            logger.debug("Hung up")
        except Exception as e:
            logger.error(f"Error hanging up: {e}")

    def is_connected(self) -> bool:
        """
        Check if modem is connected.

        Returns:
            True if connected, False otherwise
        """
        return (
            self._connected
            and self.serial_conn is not None
            and self.serial_conn.is_open
        )

    def _send_command(self, command: str, timeout: float = 2.0) -> bool:
        """
        Send AT command to modem and wait for OK response.

        Args:
            command: AT command to send
            timeout: Timeout in seconds

        Returns:
            True if OK received, False otherwise
        """
        if not self.serial_conn:
            return False

        try:
            self.serial_conn.write(f"{command}\r".encode())
            start_time = time.time()

            while time.time() - start_time < timeout:
                if self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode().strip()
                    logger.debug(f"AT response: {line}")
                    if "OK" in line:
                        return True
                    if "ERROR" in line:
                        return False
                time.sleep(0.05)

            return False
        except Exception as e:
            logger.error(f"Error sending command {command}: {e}")
            return False

    def _parse_response(self, response: str, ring_count: int = 0) -> DialResult | None:
        """
        Parse modem response and return DialResult if final status reached.

        Args:
            response: Response line from modem
            ring_count: Number of rings detected so far

        Returns:
            DialResult if final status, None if still waiting
        """
        response_upper = response.upper()

        # Busy signal
        if "BUSY" in response_upper:
            busy_message = "Busy signal detected"
            if ring_count > 0:
                busy_message = f"Busy after {ring_count} rings"
            return DialResult(
                success=False,
                status="busy",
                message=busy_message,
            )

        # No carrier (no answer or hung up)
        if "NO CARRIER" in response_upper:
            no_carrier_message = "No carrier detected"
            if ring_count > 0:
                no_carrier_message = f"No carrier after {ring_count} rings"
            return DialResult(
                success=False,
                status="no_answer",
                message=no_carrier_message,
            )

        # No dial tone
        if "NO DIAL" in response_upper or "NO DIALTONE" in response_upper:
            return DialResult(
                success=False,
                status="error",
                message="No dial tone",
            )

        # Connect - carrier detected!
        if "CONNECT" in response_upper:
            # Parse connection speed if available
            carrier_detected = True
            tone_type = "modem"
            connection_info = {}

            # Detect specific carrier types
            # Fax detection
            if "FAX" in response_upper or "+FCO" in response_upper:
                tone_type = "fax"
            # Check for specific modulation standards in response
            elif any(
                proto in response_upper
                for proto in ["V.21", "V.22", "V.32", "V.34", "V.90", "V.92"]
            ):
                # These are data modem protocols
                tone_type = "modem"
                # Extract protocol if present
                for proto in ["V.21", "V.22", "V.32", "V.34", "V.90", "V.92"]:
                    if proto in response_upper:
                        connection_info["modulation"] = proto
                        break

            # Parse connection speed (e.g., "CONNECT 2400" or "CONNECT 28800/ARQ/V34")
            parts = response.split()
            if len(parts) >= 2:
                speed_info = parts[1]
                # Extract speed (first number before any slash)
                if "/" in speed_info:
                    speed_str, protocol_info = speed_info.split("/", 1)
                    connection_info["protocol"] = protocol_info
                else:
                    speed_str = speed_info

                # Try to parse speed as integer
                try:
                    connection_info["speed"] = int(speed_str)
                except ValueError:
                    pass

            # Attempt audio analysis if enabled
            if self.enable_audio_analysis:
                audio_result = self._analyze_audio_tone()
                if audio_result:
                    tone_type = audio_result

            # Build detailed message
            message = f"Carrier detected: {response}"
            if "speed" in connection_info:
                carrier_desc = "Fax" if tone_type == "fax" else "Modem"
                message = f"{carrier_desc} carrier at {connection_info['speed']} bps"
                if "modulation" in connection_info:
                    message += f" ({connection_info['modulation']})"
                elif "protocol" in connection_info:
                    message += f" ({connection_info['protocol']})"

            return DialResult(
                success=True,
                status="modem",
                message=message,
                carrier_detected=carrier_detected,
                tone_type=tone_type,
            )

        # Voice detected (some modems support this)
        if "VOICE" in response_upper:
            return DialResult(
                success=True,
                status="person",
                message="Voice detected",
                carrier_detected=False,
                tone_type="voice",
            )

        # Error
        if "ERROR" in response_upper:
            return DialResult(
                success=False,
                status="error",
                message=f"Modem error: {response}",
            )

        # Not a final result
        return None

    def _analyze_audio_tone(self) -> str | None:
        """
        Analyze audio tone to determine carrier type.

        This is a placeholder for advanced audio frequency analysis.
        When implemented, this would:
        1. Capture audio from the modem line
        2. Perform FFT (Fast Fourier Transform) to identify frequency peaks
        3. Identify carrier types based on frequency:
           - Fax CNG tone: ~1100 Hz
           - Fax CED tone: ~2100 Hz
           - Modem carrier: 1650-2400 Hz (depending on protocol)
           - Voice: Broad spectrum 300-3400 Hz with varying patterns

        Returns:
            Tone type string ("modem", "fax", "voice") or None if cannot determine

        Note:
            Requires pyaudio or similar audio capture library to implement.
            For now, returns None (relies on modem response codes only).
        """
        # TODO: Implement audio frequency analysis
        # This would require:
        # - pyaudio for audio capture
        # - numpy/scipy for FFT analysis
        # - Frequency range detection logic
        logger.debug("Audio analysis not yet implemented")
        return None
