"""Tests for session tracking functionality."""

from datetime import datetime

from vibedialer.session import (
    SessionMetadata,
    create_session_metadata,
    generate_session_id,
)


class TestSessionIdGeneration:
    """Test session ID generation."""

    def test_generate_session_id_returns_8_char_string(self):
        """Test that session IDs are 8 characters long."""
        session_id = generate_session_id()
        assert isinstance(session_id, str)
        assert len(session_id) == 8

    def test_generate_session_id_is_unique(self):
        """Test that generated session IDs are unique."""
        ids = [generate_session_id() for _ in range(100)]
        # All IDs should be unique
        assert len(ids) == len(set(ids))

    def test_generate_session_id_contains_valid_chars(self):
        """Test that session IDs only contain valid UUID characters."""
        session_id = generate_session_id()
        valid_chars = set("0123456789abcdef-")
        assert all(c in valid_chars for c in session_id)


class TestSessionMetadata:
    """Test SessionMetadata dataclass."""

    def test_session_metadata_creation(self):
        """Test creating SessionMetadata with required fields."""
        metadata = SessionMetadata(
            session_id="abc12345",
            start_time=datetime.now().isoformat(),
        )
        assert metadata.session_id == "abc12345"
        assert metadata.start_time is not None
        assert metadata.end_time is None
        assert metadata.total_calls == 0
        assert metadata.successful_calls == 0
        assert metadata.modem_detections == 0

    def test_session_metadata_with_all_fields(self):
        """Test SessionMetadata with all fields populated."""
        start = datetime.now().isoformat()
        end = datetime.now().isoformat()

        metadata = SessionMetadata(
            session_id="test1234",
            start_time=start,
            end_time=end,
            backend_type="simulation",
            storage_type="csv",
            phone_pattern="555-234-56",
            total_calls=100,
            successful_calls=45,
            modem_detections=5,
            country_code="1",
            randomized=True,
        )

        assert metadata.session_id == "test1234"
        assert metadata.start_time == start
        assert metadata.end_time == end
        assert metadata.backend_type == "simulation"
        assert metadata.storage_type == "csv"
        assert metadata.phone_pattern == "555-234-56"
        assert metadata.total_calls == 100
        assert metadata.successful_calls == 45
        assert metadata.modem_detections == 5
        assert metadata.country_code == "1"
        assert metadata.randomized is True


class TestCreateSessionMetadata:
    """Test session metadata factory function."""

    def test_create_session_metadata_basic(self):
        """Test creating session metadata with minimal parameters."""
        metadata = create_session_metadata(
            backend_type="simulation",
            storage_type="csv",
            phone_pattern="555-234-56",
            session_id="test5678",
        )

        assert metadata.session_id == "test5678"
        assert metadata.backend_type == "simulation"
        assert metadata.storage_type == "csv"
        assert metadata.phone_pattern == "555-234-56"
        assert metadata.start_time is not None
        assert metadata.end_time is None
        assert metadata.total_calls == 0
        assert metadata.successful_calls == 0
        assert metadata.modem_detections == 0

    def test_create_session_metadata_with_optional_fields(self):
        """Test creating session metadata with all optional fields."""
        metadata = create_session_metadata(
            backend_type="voip",
            storage_type="sqlite",
            phone_pattern="212-555-12",
            country_code="1",
            randomized=True,
            session_id="xyz98765",
        )

        assert metadata.session_id == "xyz98765"
        assert metadata.backend_type == "voip"
        assert metadata.storage_type == "sqlite"
        assert metadata.phone_pattern == "212-555-12"
        assert metadata.country_code == "1"
        assert metadata.randomized is True

    def test_create_session_metadata_start_time_is_iso_format(self):
        """Test that start_time is in ISO 8601 format."""
        metadata = create_session_metadata(
            backend_type="simulation",
            storage_type="csv",
            phone_pattern="555-123",
            session_id="test1111",
        )

        # Should be able to parse as ISO format
        start_time = datetime.fromisoformat(metadata.start_time)
        assert isinstance(start_time, datetime)

    def test_create_session_metadata_auto_generates_session_id(self):
        """Test that session ID can be auto-generated when None."""
        metadata = create_session_metadata(
            backend_type="modem",
            storage_type="sqlite",
            phone_pattern="800-555",
            session_id=None,
        )

        # None session_id should trigger auto-generation
        assert metadata.session_id != ""
        assert len(metadata.session_id) == 8

    def test_create_session_metadata_auto_generates_from_empty_string(self):
        """Test that session ID auto-generates from empty string."""
        metadata = create_session_metadata(
            backend_type="simulation",
            storage_type="csv",
            phone_pattern="555-234",
            session_id="",
        )

        # Empty string should evaluate to falsy and trigger auto-generation
        assert metadata.session_id != ""
        assert len(metadata.session_id) == 8
