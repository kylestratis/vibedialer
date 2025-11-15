"""VoIP backend for VibeDialer (stub implementation)."""

import logging

from vibedialer.backends import DialResult, TelephonyBackend

logger = logging.getLogger(__name__)


class VoIPBackend(TelephonyBackend):
    """
    VoIP backend using SIP/RTP protocols.

    This is a stub implementation. In a real implementation, this would use
    libraries like pjsua2 or linphone to make VoIP calls through a SIP provider.
    """

    def __init__(self, sip_server: str, username: str, password: str):
        """
        Initialize VoIP backend.

        Args:
            sip_server: SIP server address (e.g., 'sip.example.com')
            username: SIP account username
            password: SIP account password
        """
        self.sip_server = sip_server
        self.username = username
        self.password = password
        self._connected = False

    def connect(self) -> bool:
        """
        Connect to VoIP service.

        Returns:
            True if connection successful, False otherwise
        """
        logger.warning(
            "VoIP backend is not implemented yet. "
            "This is a placeholder that returns simulated results."
        )
        # In real implementation: register with SIP server
        self._connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from VoIP service."""
        # In real implementation: unregister from SIP server
        self._connected = False
        logger.info("Disconnected from VoIP service (stub)")

    def dial(self, phone_number: str) -> DialResult:
        """
        Dial a phone number via VoIP.

        Args:
            phone_number: The phone number to dial

        Returns:
            DialResult with outcome (simulated)
        """
        if not self.is_connected():
            return DialResult(
                success=False,
                status="error",
                message="Not connected to VoIP service",
            )

        logger.info(f"VoIP dial (stub): {phone_number}")

        # Stub: return a placeholder result
        # In real implementation: use SIP INVITE, monitor RTP stream,
        # analyze audio to detect modem carriers, voices, etc.
        return DialResult(
            success=False,
            status="error",
            message="VoIP backend not implemented - use modem backend instead",
        )

    def hangup(self) -> None:
        """Hang up the current VoIP call."""
        # In real implementation: send SIP BYE
        logger.debug("VoIP hangup (stub)")

    def is_connected(self) -> bool:
        """
        Check if connected to VoIP service.

        Returns:
            True if connected, False otherwise
        """
        return self._connected
