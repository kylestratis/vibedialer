# Session Tracking and Metadata for VibeDialer

## Summary

This PR adds comprehensive session tracking to VibeDialer, enabling users to group dial results by session, track statistics, and seamlessly resume interrupted operations.

## Features

### Session ID Management
- **Auto-generated Session IDs**: Short 8-character UUIDs (e.g., `a3f5c2d1`) automatically created for each session
- **Custom Session IDs**: Manually specify session IDs via CLI for better organization
- **Session Continuation**: Automatically continue previous session when resuming from a file
- **Session Metadata**: Track comprehensive statistics including total calls, successes, and modem detections

### CLI Enhancements

Three new command-line flags:

```bash
# Manually specify session ID
vibedialer dial --session-id office-scan-2025 555-234-56

# Continue previous session (default behavior)
vibedialer dial --resume calls.db --infer-prefix --continue-session

# Force new session even when resuming
vibedialer dial --resume calls.db --infer-prefix --new-session
```

### Session Metadata Fields

| Field              | Description                                    |
|--------------------|------------------------------------------------|
| session_id         | Unique identifier (8-char UUID or custom)      |
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

## Implementation Details

### New Module: `vibedialer/session.py`

```python
@dataclass
class SessionMetadata:
    """Metadata for a war dialing session."""
    session_id: str
    start_time: str  # ISO 8601 timestamp
    end_time: str | None = None
    backend_type: str = ""
    storage_type: str = ""
    phone_pattern: str = ""
    total_calls: int = 0
    successful_calls: int = 0
    modem_detections: int = 0
    country_code: str = ""
    randomized: bool = False

def generate_session_id() -> str:
    """Generate a short 8-character UUID."""
    return str(uuid.uuid4())[:8]

def create_session_metadata(...) -> SessionMetadata:
    """Factory function for creating session metadata."""
```

### Updated Data Model: `DialResult`

```python
@dataclass
class DialResult:
    success: bool
    status: str
    message: str
    carrier_detected: bool = False
    tone_type: str | None = None
    phone_number: str = ""
    timestamp: str = ""
    session_id: str = ""  # NEW: Session identifier
```

### CSV Storage Enhancement

CSV files now include `session_id` as the first column:

```csv
session_id,phone_number,status,timestamp,success,message,carrier_detected,tone_type
a3f5c2d1,555-234-5600,busy,2025-11-16T14:30:00,False,Busy signal,False,
a3f5c2d1,555-234-5601,modem,2025-11-16T14:30:01,True,Modem detected,True,modem
```

### SQLite Storage Enhancement

#### New Sessions Table

```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    start_time TEXT NOT NULL,
    end_time TEXT,
    backend_type TEXT,
    storage_type TEXT,
    phone_pattern TEXT,
    total_calls INTEGER DEFAULT 0,
    successful_calls INTEGER DEFAULT 0,
    modem_detections INTEGER DEFAULT 0,
    country_code TEXT,
    randomized BOOLEAN
);
```

#### Updated dial_results Table

```sql
CREATE TABLE dial_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,  -- NEW: Foreign key to sessions
    phone_number TEXT NOT NULL,
    status TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    message TEXT,
    carrier_detected BOOLEAN,
    tone_type TEXT
);

CREATE INDEX idx_session_id ON dial_results(session_id);  -- NEW INDEX
```

#### New SQLite Methods

```python
class SQLiteStorage:
    def save_session(self, session: SessionMetadata) -> None:
        """Save or update session metadata."""

    def get_session(self, session_id: str) -> SessionMetadata | None:
        """Retrieve session metadata by ID."""

    def get_latest_session_id(self) -> str | None:
        """Get the most recent session ID."""
```

### PhoneDialer Integration

```python
class PhoneDialer:
    def __init__(
        self,
        session_id: str | None = None,  # NEW
        phone_pattern: str = "",         # NEW
        randomize: bool = False,         # NEW
        **kwargs,
    ):
        # Auto-generate session ID if not provided
        self.session_id = session_id or generate_session_id()

        # Create session metadata
        self.session_metadata = create_session_metadata(
            session_id=self.session_id,
            backend_type=backend_type.value,
            storage_type=storage_type.value,
            phone_pattern=phone_pattern,
            country_code=str(self.country_code.value),
            randomized=randomize,
        )

    def dial(self, phone_number: str) -> DialResult:
        # Save session metadata on first dial
        if not self._session_saved:
            self._save_session_metadata()

        # Dial and update statistics
        result = self.backend.dial(phone_number)
        result.session_id = self.session_id

        # Update session statistics
        self.session_metadata.total_calls += 1
        if result.success:
            self.session_metadata.successful_calls += 1
        if result.status == "modem" or result.carrier_detected:
            self.session_metadata.modem_detections += 1
```

## Usage Examples

### Basic Session Tracking

```bash
# Auto-generated session ID
vibedialer dial 555-234-56
# Session ID: a3f5c2d1 (auto-generated)

# Custom session ID
vibedialer dial --session-id office-scan-2025-11-16 555-234-56
# Session ID: office-scan-2025-11-16
```

### Session Continuation

```bash
# Initial session with SQLite storage
vibedialer dial --storage sqlite --output calls.db 555-234-56
# Session ID: a3f5c2d1

# Resume later - continues same session by default
vibedialer dial --resume calls.db --infer-prefix
# Session ID: a3f5c2d1 (continued)

# Force new session on resume
vibedialer dial --resume calls.db --infer-prefix --new-session
# Session ID: b7e9f4a2 (new session)
```

### Querying Session Data (SQLite)

```sql
-- List all sessions
SELECT session_id, phone_pattern, total_calls, modem_detections
FROM sessions
ORDER BY start_time DESC;

-- Get all modem hits for a specific session
SELECT phone_number, timestamp, message
FROM dial_results
WHERE session_id = 'a3f5c2d1' AND status = 'modem';

-- Calculate success rate per session
SELECT
    session_id,
    backend_type,
    total_calls,
    (successful_calls * 100.0 / total_calls) as success_rate
FROM sessions;

-- Compare sessions
SELECT
    s.session_id,
    s.phone_pattern,
    s.backend_type,
    s.total_calls,
    s.modem_detections,
    COUNT(DISTINCT d.phone_number) as unique_numbers
FROM sessions s
LEFT JOIN dial_results d ON s.session_id = d.session_id
GROUP BY s.session_id;
```

### Filtering CSV Results by Session

```bash
# Get all results for a specific session
grep "a3f5c2d1" results.csv

# Count modem detections per session
awk -F',' '$3=="modem" {count[$1]++} END {for (s in count) print s, count[s]}' results.csv
```

## Testing

### Test Coverage

Added 18 new tests across two test files:

**`tests/test_session.py` (10 tests):**
- Session ID generation and uniqueness
- Session ID format validation
- SessionMetadata dataclass creation
- Session metadata factory function
- Auto-generation from None and empty string

**`tests/test_storage.py` (8 new tests):**
- CSV session_id column presence and ordering
- CSV session_id storage and retrieval
- SQLite sessions table creation
- SQLite session_id column and index
- SQLite save_session() method
- SQLite get_session() method
- SQLite get_latest_session_id() method
- SQLite dial results with session_id

### Test Results

```
============================= test session starts ==============================
collected 184 items

tests/test_session.py ..........                                         [ 5%]
tests/test_storage.py ...........................                        [20%]
[... other tests ...]

============================== 184 passed in 2.60s ==============================
```

All tests passing with 100% success rate.

## Documentation

### Updated DIALING.md

Added comprehensive "Session Tracking" section with:

- **Session Concepts**: What sessions are and how they work
- **Session ID Format**: Auto-generated vs. custom IDs
- **Session Metadata Table**: Complete field reference
- **CLI Flag Reference**: All session-related flags
- **Storage Formats**: CSV and SQLite storage details
- **SQL Query Examples**: Common queries for analyzing sessions
- **Session Report Example**: Sample output format
- **Best Practices**: Recommendations for session management

### Example Documentation Snippets

```markdown
## Session Tracking

### What is a Session?

A **session** represents a single war dialing operation. Each session has:
- **Session ID**: A unique 8-character identifier (e.g., `a3f5c2d1`)
- **Metadata**: Backend type, storage type, phone pattern, statistics
- **Results**: All dial results grouped by session ID

### Session CLI Flags

| Flag                 | Description                              | Default    |
|----------------------|------------------------------------------|------------|
| `--session-id`       | Manually specify session ID              | Auto-gen   |
| `--continue-session` | Continue previous session when resuming  | True       |
| `--new-session`      | Force new session even when resuming     | False      |
```

## Code Quality

### Linting

All code passes `ruff` linting with zero errors:

```bash
$ uv run ruff check vibedialer/ tests/
All checks passed!
```

### Type Safety

All code uses proper type hints:
- `session_id: str | None`
- `SessionMetadata` dataclass with typed fields
- Proper return type annotations

## Migration Notes

### Backward Compatibility

✅ **Fully backward compatible** - No breaking changes:

- Existing CSV files work without session_id column
- Existing SQLite databases automatically upgraded with new tables
- Session ID auto-generated if not specified
- All existing CLI commands work unchanged

### Storage Migration

**CSV Files**: No migration needed. New writes include session_id as first column.

**SQLite Databases**: Automatically upgraded on first open:
- New `sessions` table created
- `session_id` column added to `dial_results` if missing
- Indexes created automatically

## Benefits

### For Users

1. **Better Organization**: Group related dial operations by session
2. **Progress Tracking**: Monitor statistics for each session
3. **Resume Support**: Continue interrupted sessions seamlessly
4. **Analysis**: Query and compare results across sessions
5. **Debugging**: Trace issues back to specific sessions

### For Developers

1. **Clean Architecture**: Session logic isolated in `session.py`
2. **Extensible**: Easy to add new metadata fields
3. **Well-tested**: 18 new tests with 100% pass rate
4. **Type-safe**: Full type hints throughout
5. **Documented**: Comprehensive documentation and examples

## Related Issues

This feature addresses user requests for:
- Grouping dial results by campaign/session
- Tracking statistics per dial operation
- Resuming sessions without duplicating work
- Better data analysis capabilities

## Checklist

- [x] Implementation complete
- [x] Tests added (18 new tests)
- [x] All tests passing (184/184)
- [x] Documentation updated (DIALING.md)
- [x] Linting passing (ruff)
- [x] Backward compatible
- [x] Type hints added
- [x] Examples provided
- [x] Migration path documented

## Files Changed

### New Files
- `vibedialer/session.py` - Session metadata and ID generation
- `tests/test_session.py` - Session tracking tests

### Modified Files
- `vibedialer/backends.py` - Added session_id to DialResult
- `vibedialer/cli.py` - Added session CLI flags and logic
- `vibedialer/csv_storage.py` - Added session_id column
- `vibedialer/dialer.py` - Session tracking integration
- `vibedialer/sqlite_storage.py` - Sessions table and methods
- `vibedialer/tui.py` - Pass session_id to dialer
- `tests/test_storage.py` - Session storage tests
- `DIALING.md` - Session documentation

## Statistics

- **Lines Added**: ~900
- **Lines Removed**: ~10
- **Net Change**: +890 lines
- **Tests Added**: 18
- **Files Created**: 2
- **Files Modified**: 8
- **Test Pass Rate**: 100% (184/184)
