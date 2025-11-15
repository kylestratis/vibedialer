"""VoIP backend for VibeDialer using Twilio."""

import logging
import time

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from vibedialer.backends import DialResult, TelephonyBackend

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
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.timeout = timeout
        self.twiml_url = twiml_url or "http://demo.twilio.com/docs/voice.xml"
        self.client: Client | None = None
        self._connected = False
        self.current_call = None

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
        """Disconnect from Twilio service."""
        if self.current_call:
            try:
                self.hangup()
            except Exception as e:
                logger.error(f"Error hanging up during disconnect: {e}")

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
            # Initiate the call
            call = self.client.calls.create(
                to=to_number,
                from_=self.from_number,
                url=self.twiml_url,
                timeout=self.timeout,
                # Request status callbacks for better detection
                status_callback_event=["initiated", "ringing", "answered", "completed"],
            )

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
        Analyze Twilio call result and create DialResult.

        Args:
            call: Twilio call object
            phone_number: Original phone number dialed

        Returns:
            DialResult with detected status
        """
        status_map = {
            "completed": "person",  # Call was answered and completed
            "busy": "busy",
            "no-answer": "no_answer",
            "failed": "error",
            "canceled": "error",
        }

        twilio_status = call.status
        our_status = status_map.get(twilio_status, "error")

        # Determine if call was successful
        success = twilio_status == "completed"

        # Build message
        if success:
            duration = call.duration or 0
            message = f"Call answered, duration: {duration}s"

            # Try to detect modem carriers based on very short durations
            # (modems typically disconnect quickly after handshake)
            if duration and int(duration) < 3:
                our_status = "modem"
                message = (
                    f"Possible modem carrier detected (short duration: {duration}s)"
                )
        else:
            message = f"Call {twilio_status}"
            if call.end_time:
                message += f" at {call.end_time}"

        # Log call details
        logger.info(
            f"Call to {phone_number}: status={twilio_status}, "
            f"duration={call.duration}, price={call.price}"
        )

        return DialResult(
            success=success,
            status=our_status,
            message=message,
            phone_number=phone_number,
        )
