"""Session tracking and metadata management for VibeDialer."""

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SessionMetadata:
    """Metadata for a war dialing session."""

    session_id: str
    start_time: str  # ISO 8601 timestamp
    end_time: str | None = None
    backend_type: str = ""
    storage_type: str = ""
    phone_pattern: str = ""  # Pattern being dialed (e.g., "555-234-56")
    total_calls: int = 0
    successful_calls: int = 0
    modem_detections: int = 0
    country_code: str = ""
    randomized: bool = False


def generate_session_id() -> str:
    """
    Generate a short session ID.

    Uses first 8 characters of UUID4 for uniqueness while keeping it readable.

    Returns:
        Short session ID (e.g., "a3f5c2d1")
    """
    return str(uuid.uuid4())[:8]


def generate_session_id_from_timestamp() -> str:
    """
    Generate a session ID based on timestamp.

    Format: YYYYMMDD-HHMMSS (e.g., "20251115-143022")

    Returns:
        Timestamp-based session ID
    """
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def create_session_metadata(
    backend_type: str,
    storage_type: str,
    phone_pattern: str,
    country_code: str = "1",
    randomized: bool = False,
    session_id: str | None = None,
) -> SessionMetadata:
    """
    Create session metadata for a new dialing session.

    Args:
        backend_type: Type of telephony backend used
        storage_type: Type of storage backend used
        phone_pattern: Phone number pattern being dialed
        country_code: Country code for phone numbers
        randomized: Whether numbers are dialed in random order
        session_id: Optional session ID (generated if not provided)

    Returns:
        SessionMetadata object
    """
    return SessionMetadata(
        session_id=session_id or generate_session_id(),
        start_time=datetime.now().isoformat(),
        backend_type=backend_type,
        storage_type=storage_type,
        phone_pattern=phone_pattern,
        country_code=country_code,
        randomized=randomized,
    )
