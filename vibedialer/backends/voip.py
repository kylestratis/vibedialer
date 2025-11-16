"""VoIP backend for VibeDialer using Twilio."""

import atexit
import logging
import time
from concurrent.futures import Future, ThreadPoolExecutor

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from vibedialer.backends.base import DialResult, TelephonyBackend

logger = logging.getLogger(__name__)


class VoIPBackend(TelephonyBackend):
    """
    VoIP backend using Twilio's Voice API.

    This backend uses Twilio to make actual phone calls and detect carriers.
    Requires a Twilio account with:
    - Account SID
    - Auth Token
    - A purchased/verified Twilio phone number

    Get started at: https://www.twilio.com/
    """

    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        from_number: str,
        timeout: int = 30,
        twiml_url: str | None = None,
        enable_amd: bool = True,
        amd_timeout: int = 5,
        enable_recording: bool = True,
        recording_duration: int = 10,
        enable_audio_analysis: bool = True,
        async_analysis: bool = True,
        cleanup_recordings: bool = True,
        max_analysis_workers: int = 4,
    ):
        """
        Initialize Twilio VoIP backend.

        Args:
            account_sid: Twilio Account SID (starts with 'AC')
            auth_token: Twilio Auth Token
            from_number: Twilio phone number to call from
                (E.164 format, e.g., '+15551234567')
            timeout: Max time to wait for call connection (default: 30)
            twiml_url: Optional TwiML URL for call instructions
            enable_amd: Enable Answering Machine Detection (default: True)
            amd_timeout: AMD detection timeout in seconds (default: 5)
            enable_recording: Enable call recording for fax/unknown (default: True)
            recording_duration: Max recording duration in seconds (default: 10)
            enable_audio_analysis: Enable FFT audio analysis (default: True)
            async_analysis: Run audio analysis in parallel (default: True)
            cleanup_recordings: Delete recordings after analysis (default: True)
            max_analysis_workers: Max parallel analysis workers (default: 4)
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.timeout = timeout
        self.twiml_url = twiml_url or "http://demo.twilio.com/docs/voice.xml"
        self.client: Client | None = None
        self._connected = False
        self.current_call = None

        # AMD settings
        self.enable_amd = enable_amd
        self.amd_timeout = amd_timeout

        # Recording settings
        self.enable_recording = enable_recording
        self.recording_duration = recording_duration
        self.cleanup_recordings = cleanup_recordings

        # Audio analysis settings
        self.enable_audio_analysis = enable_audio_analysis
        self.async_analysis = async_analysis

        # Track pending analyses and recordings
        self.pending_analyses: dict[str, Future] = {}
        self.pending_recordings: list[str] = []

        # Thread pool for async audio analysis
        self.analysis_executor = (
            ThreadPoolExecutor(max_workers=max_analysis_workers)
            if async_analysis and enable_audio_analysis
            else None
        )

        # Register cleanup handler
        atexit.register(self._cleanup_on_exit)

    def connect(self) -> bool:
        """
        Connect to Twilio service (initialize client).

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Initialize Twilio client
            self.client = Client(self.account_sid, self.auth_token)

            # Verify credentials by fetching account info
            account = self.client.api.accounts(self.account_sid).fetch()
            logger.info(f"Connected to Twilio account: {account.friendly_name}")

            # Verify the from_number exists and is valid
            try:
                number = self.client.incoming_phone_numbers.list(
                    phone_number=self.from_number, limit=1
                )
                if not number:
                    logger.warning(
                        f"Phone number {self.from_number} not found in account. "
                        f"Calls may fail if number is not verified."
                    )
            except TwilioRestException as e:
                logger.warning(f"Could not verify phone number: {e}")

            self._connected = True
            return True

        except TwilioRestException as e:
            logger.error(f"Failed to connect to Twilio: {e}")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Twilio: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from Twilio service and cleanup resources."""
        if self.current_call:
            try:
                self.hangup()
            except Exception as e:
                logger.error(f"Error hanging up during disconnect: {e}")

        # Wait for pending analyses to complete
        self._wait_for_pending_analyses()

        # Cleanup recordings if enabled
        if self.cleanup_recordings:
            self._cleanup_recordings()

        # Shutdown thread pool
        if self.analysis_executor:
            self.analysis_executor.shutdown(wait=True)

        self.client = None
        self._connected = False
        logger.info("Disconnected from Twilio service")

    def dial(self, phone_number: str) -> DialResult:
        """
        Dial a phone number via Twilio.

        Args:
            phone_number: The phone number to dial (will be converted to E.164 format)

        Returns:
            DialResult with outcome
        """
        if not self.is_connected() or not self.client:
            return DialResult(
                success=False,
                status="error",
                message="Not connected to Twilio service",
            )

        # Normalize phone number to E.164 format
        to_number = self._normalize_phone_number(phone_number)

        logger.info(f"Dialing via Twilio: {to_number}")

        try:
            # Build call parameters
            call_params = {
                "to": to_number,
                "from_": self.from_number,
                "url": self.twiml_url,
                "timeout": self.timeout,
                "status_callback_event": [
                    "initiated",
                    "ringing",
                    "answered",
                    "completed",
                ],
            }

            # Add AMD parameters if enabled
            if self.enable_amd:
                call_params["machine_detection"] = "Enable"
                call_params["machine_detection_timeout"] = self.amd_timeout

            # Add recording parameters if enabled
            if self.enable_recording:
                call_params["record"] = True
                call_params["recording_status_callback_event"] = ["completed"]
                call_params["recording_channels"] = "mono"
                call_params["recording_track"] = "both"

            # Initiate the call
            call = self.client.calls.create(**call_params)

            self.current_call = call

            # Wait for call to connect or timeout
            max_wait = self.timeout
            wait_interval = 0.5  # Check every 500ms
            elapsed = 0

            while elapsed < max_wait:
                # Fetch latest call status
                call = self.client.calls(call.sid).fetch()

                # Check call status
                if call.status in [
                    "completed",
                    "failed",
                    "busy",
                    "no-answer",
                    "canceled",
                ]:
                    break

                time.sleep(wait_interval)
                elapsed += wait_interval

            # Analyze call results
            result = self._analyze_call_result(call, phone_number)

            # Hang up if still connected
            if call.status in ["in-progress", "ringing"]:
                self.hangup()

            return result

        except TwilioRestException as e:
            logger.error(f"Twilio API error dialing {to_number}: {e}")
            return DialResult(
                success=False,
                status="error",
                message=f"Twilio error: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Unexpected error dialing {to_number}: {e}")
            return DialResult(
                success=False,
                status="error",
                message=f"Unexpected error: {str(e)}",
            )

    def hangup(self) -> None:
        """Hang up the current Twilio call."""
        if not self.current_call or not self.client:
            return

        try:
            # Update call status to completed (hangup)
            self.client.calls(self.current_call.sid).update(status="completed")
            logger.debug(f"Hung up call {self.current_call.sid}")
        except TwilioRestException as e:
            logger.error(f"Error hanging up call: {e}")
        finally:
            self.current_call = None

    def is_connected(self) -> bool:
        """
        Check if connected to Twilio service.

        Returns:
            True if connected, False otherwise
        """
        return self._connected and self.client is not None

    def _normalize_phone_number(self, phone_number: str) -> str:
        """
        Normalize phone number to E.164 format for Twilio.

        Args:
            phone_number: Phone number in various formats

        Returns:
            Phone number in E.164 format (e.g., '+15551234567')
        """
        # Remove all non-digit characters except leading +
        if phone_number.startswith("+"):
            # Already in E.164 format
            digits = "+" + "".join(c for c in phone_number[1:] if c.isdigit())
        else:
            # Extract digits
            digits = "".join(c for c in phone_number if c.isdigit())

            # Add country code if not present (default to US +1)
            if len(digits) == 10:
                digits = "+1" + digits
            elif len(digits) == 11 and digits.startswith("1"):
                digits = "+" + digits
            elif not digits.startswith("+"):
                digits = "+" + digits

        return digits

    def _analyze_call_result(self, call, phone_number: str) -> DialResult:
        """
        Analyze Twilio call result with AMD and audio analysis.

        Args:
            call: Twilio call object
            phone_number: Original phone number dialed

        Returns:
            DialResult with detected status and analysis
        """
        # Extract AMD results if available
        answered_by = getattr(call, "answered_by", None)
        amd_duration = getattr(call, "answering_machine_detection_duration", None)

        # Convert AMD duration to float if present
        if amd_duration is not None:
            try:
                amd_duration = float(amd_duration)
            except (ValueError, TypeError):
                amd_duration = None

        twilio_status = call.status
        duration = call.duration or 0

        # Initialize result fields
        success = False
        our_status = "error"
        message = ""
        carrier_detected = False
        tone_type = None
        fft_peak_frequency = None
        fft_confidence = None
        recording_url = None
        recording_duration = None

        # Process based on call status and AMD results
        if twilio_status == "completed":
            # Call was answered - determine what answered it
            if answered_by == "human":
                success = True
                our_status = "person"
                message = (
                    f"Human answered (AMD: {amd_duration:.1f}s), duration: {duration}s"
                )

            elif answered_by == "fax":
                success = True
                our_status = "modem"
                carrier_detected = True
                tone_type = "fax"
                message = f"Fax detected (AMD: {amd_duration:.1f}s)"

                # Get recording and perform FFT to confirm fax vs modem
                recording_url, recording_duration = self._get_recording(call.sid)
                if recording_url and self.enable_audio_analysis:
                    fft_result = self._analyze_audio(call.sid, recording_url)
                    if fft_result:
                        tone_type = fft_result.get("tone_type", tone_type)
                        fft_peak_frequency = fft_result.get("peak_frequency")
                        fft_confidence = fft_result.get("confidence")

                        # Update message with FFT result if different
                        if tone_type != "fax":
                            message = (
                                f"{tone_type.capitalize()} carrier detected "
                                f"(AMD said fax, FFT corrected)"
                            )

            elif answered_by in [
                "machine_start",
                "machine_end_beep",
                "machine_end_silence",
                "machine_end_other",
            ]:
                success = False
                our_status = "no_answer"  # Voicemail = no human
                message = f"Voicemail/machine detected (AMD: {amd_duration:.1f}s)"

            elif answered_by == "unknown":
                # AMD couldn't determine - use recording + FFT
                recording_url, recording_duration = self._get_recording(call.sid)
                if recording_url and self.enable_audio_analysis:
                    fft_result = self._analyze_audio(call.sid, recording_url)
                    if fft_result:
                        tone_type = fft_result.get("tone_type")
                        fft_peak_frequency = fft_result.get("peak_frequency")
                        fft_confidence = fft_result.get("confidence")

                        if tone_type in ["modem", "fax"]:
                            success = True
                            our_status = "modem"
                            carrier_detected = True
                            message = (
                                f"{tone_type.capitalize()} detected via FFT "
                                f"(AMD unknown)"
                            )
                        elif tone_type == "voice":
                            success = True
                            our_status = "person"
                            message = "Voice detected via FFT (AMD unknown)"
                        else:
                            success = False
                            our_status = "error"
                            message = (
                                f"Unknown signal (AMD: {amd_duration:.1f}s, "
                                f"FFT inconclusive)"
                            )
                else:
                    # No recording or analysis - fall back to duration heuristic
                    if duration and int(duration) < 3:
                        success = True
                        our_status = "modem"
                        carrier_detected = True
                        message = (
                            f"Possible carrier (AMD unknown, "
                            f"short duration: {duration}s)"
                        )
                    else:
                        success = True
                        our_status = "person"
                        message = (
                            f"Answered but unknown type (AMD: {amd_duration:.1f}s)"
                        )

            else:
                # No AMD result - fall back to old behavior
                if duration and int(duration) < 3:
                    success = True
                    our_status = "modem"
                    carrier_detected = True
                    message = f"Possible modem carrier (short duration: {duration}s)"
                else:
                    success = True
                    our_status = "person"
                    message = f"Call answered, duration: {duration}s"

        elif twilio_status == "busy":
            our_status = "busy"
            message = "Busy signal"

        elif twilio_status == "no-answer":
            our_status = "no_answer"
            message = "No answer"

        elif twilio_status in ["failed", "canceled"]:
            our_status = "error"
            message = f"Call {twilio_status}"

        # Log detailed call results
        logger.info(
            f"Call to {phone_number}: status={twilio_status}, "
            f"our_status={our_status}, answered_by={answered_by}, "
            f"duration={duration}, amd_duration={amd_duration}, "
            f"tone_type={tone_type}, fft_freq={fft_peak_frequency}"
        )

        return DialResult(
            success=success,
            status=our_status,
            message=message,
            phone_number=phone_number,
            carrier_detected=carrier_detected,
            tone_type=tone_type,
            answered_by=answered_by,
            amd_duration=amd_duration,
            fft_peak_frequency=fft_peak_frequency,
            fft_confidence=fft_confidence,
            recording_url=recording_url,
            recording_duration=recording_duration,
        )

    def _get_recording(self, call_sid: str) -> tuple[str | None, float | None]:
        """
        Get recording URL for a call.

        Args:
            call_sid: Twilio call SID

        Returns:
            Tuple of (recording_url, duration) or (None, None) if not found
        """
        if not self.enable_recording or not self.client:
            return None, None

        try:
            # Fetch recordings for this call
            recordings = self.client.recordings.list(call_sid=call_sid, limit=1)

            if recordings:
                recording = recordings[0]
                # Build full URL for WAV format
                recording_url = (
                    f"https://api.twilio.com{recording.uri.replace('.json', '.wav')}"
                )
                duration = float(recording.duration) if recording.duration else None

                # Track recording for cleanup
                self.pending_recordings.append(recording.sid)

                logger.debug(f"Found recording for call {call_sid}: {recording.sid}")
                return recording_url, duration

        except Exception as e:
            logger.warning(f"Failed to fetch recording for call {call_sid}: {e}")

        return None, None

    def _analyze_audio(self, call_sid: str, recording_url: str) -> dict | None:
        """
        Analyze audio recording using FFT.

        Args:
            call_sid: Call SID for tracking
            recording_url: URL to recording

        Returns:
            Analysis result dict or None
        """
        if not self.enable_audio_analysis:
            return None

        try:
            if self.async_analysis and self.analysis_executor:
                # Run analysis asynchronously
                from vibedialer.audio_analysis import analyze_recording_async

                future = analyze_recording_async(recording_url, self.analysis_executor)
                self.pending_analyses[call_sid] = future

                # For async, try to get result with short timeout
                # If not ready, return None and result will be available later
                try:
                    return future.result(timeout=0.1)
                except Exception:
                    logger.debug(f"Audio analysis for {call_sid} pending...")
                    return None
            else:
                # Run analysis synchronously
                from vibedialer.audio_analysis import analyze_recording

                return analyze_recording(recording_url)

        except Exception as e:
            logger.error(f"Audio analysis failed for {call_sid}: {e}")
            return None

    def _wait_for_pending_analyses(self, timeout: float = 5.0) -> None:
        """
        Wait for all pending audio analyses to complete.

        Args:
            timeout: Max time to wait for each analysis
        """
        if not self.pending_analyses:
            return

        logger.info(f"Waiting for {len(self.pending_analyses)} pending analyses...")

        for call_sid, future in list(self.pending_analyses.items()):
            try:
                result = future.result(timeout=timeout)
                logger.debug(
                    f"Analysis for {call_sid} completed: {result.get('tone_type')}"
                )
            except Exception as e:
                logger.warning(f"Analysis for {call_sid} failed or timed out: {e}")

        self.pending_analyses.clear()

    def _cleanup_recordings(self) -> None:
        """Delete all pending recordings from Twilio."""
        if not self.pending_recordings or not self.client:
            return

        logger.info(f"Cleaning up {len(self.pending_recordings)} recordings...")

        for recording_sid in list(self.pending_recordings):
            try:
                from vibedialer.audio_analysis import cleanup_recording

                cleanup_recording(recording_sid, self.client)
            except Exception as e:
                logger.warning(f"Failed to cleanup recording {recording_sid}: {e}")

        self.pending_recordings.clear()

    def _cleanup_on_exit(self) -> None:
        """Cleanup handler called on program exit."""
        try:
            if self._connected:
                logger.info("Cleaning up VoIP backend on exit...")
                self._wait_for_pending_analyses(timeout=2.0)
                if self.cleanup_recordings:
                    self._cleanup_recordings()
                if self.analysis_executor:
                    self.analysis_executor.shutdown(wait=False)
        except Exception as e:
            logger.error(f"Error during exit cleanup: {e}")
