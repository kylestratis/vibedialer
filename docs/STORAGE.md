# Storage Backends

VibeDialer supports multiple storage backends for saving dial results automatically.

## Storage Types

### 1. CSV Storage (Default)

CSV storage saves results to a comma-separated values file, which can be opened in Excel, Google Sheets, or any text editor.

**Usage:**
```bash
# Launch TUI (default) - storage can be configured in interface
vibedialer

# Or use dial command with custom storage
vibedialer dial 555-12 --storage csv --output results.csv
```

**Features:**
- Automatic header row creation
- Append mode - subsequent runs add to existing file
- Human-readable format
- Easy to import into spreadsheet applications

**CSV Format:**
```csv
phone_number,status,timestamp,success,message,carrier_detected,tone_type
555-1234,modem,2025-11-15T12:00:00,True,Modem carrier detected,True,modem
555-1235,busy,2025-11-15T12:01:00,False,Busy signal detected,False,
555-1236,no_answer,2025-11-15T12:02:00,False,No answer after 3 rings,False,
```

### 2. SQLite Storage

SQLite storage saves results to a relational database file, enabling complex queries and analysis.

**Usage:**
```bash
# Default SQLite storage (vibedialer_results.db)
vibedialer dial 555-12 --storage sqlite

# Custom database file
vibedialer dial 555-12 --storage sqlite --output my_results.db
```

**Features:**
- Indexed for fast queries
- Supports complex SQL queries
- Compact storage format
- Transaction-based for data integrity

**Database Schema:**
```sql
CREATE TABLE dial_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL,
    status TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    message TEXT,
    carrier_detected BOOLEAN,
    tone_type TEXT
);

-- Indexes
CREATE INDEX idx_phone_number ON dial_results(phone_number);
CREATE INDEX idx_timestamp ON dial_results(timestamp);
CREATE INDEX idx_status ON dial_results(status);
```

**Query Examples:**
```sql
-- Find all modems detected
SELECT * FROM dial_results WHERE status = 'modem';

-- Count results by status
SELECT status, COUNT(*) as count
FROM dial_results
GROUP BY status
ORDER BY count DESC;

-- Find all results in a date range
SELECT * FROM dial_results
WHERE timestamp BETWEEN '2025-11-15 00:00:00' AND '2025-11-15 23:59:59';
```

### 3. Dry-Run Mode

Dry-run mode doesn't save any results to disk. Useful for testing or when you don't want to persist data.

**Usage:**
```bash
# Dry-run mode - no data saved
vibedialer dial 555-12 --storage dry-run
```

**Features:**
- No files created
- Results still displayed in TUI
- Logs what would have been saved
- Useful for testing and demonstrations

## CLI Usage

### Basic Commands

```bash
# CSV storage (default)
vibedialer dial 555-12

# Explicit CSV with custom file
vibedialer dial 555-12 --storage csv --output my_scan.csv

# SQLite storage
vibedialer dial 555-12 --storage sqlite --output scan_results.db

# Dry-run mode
vibedialer dial 555-12 --storage dry-run
```

### Combined with Backend Options

```bash
# Modem backend with CSV storage
vibedialer dial 555-12 --backend modem --storage csv --output modem_scan.csv

# Simulation with SQLite
vibedialer dial 555-12 --backend simulation --storage sqlite --output test.db
```

## TUI Usage

When using the interactive TUI, storage is configured via CLI flags when launching:

```bash
# Launch TUI with CSV storage
vibedialer dial 555-12 --interactive --storage csv --output session.csv

# Launch TUI with SQLite storage
vibedialer dial 555-12 --interactive --storage sqlite --output session.db
```

The TUI will automatically save results as you dial.

## Automatic Saving

Results are automatically saved in real-time:

- **CSV**: Each result is written immediately and flushed to disk
- **SQLite**: Each result is inserted immediately (transactions auto-committed)
- **Dry-Run**: Results logged but not persisted

## Exit Handling

VibeDialer ensures data is saved even when the application exits unexpectedly:

- **Normal Exit**: Storage is properly closed, all data flushed
- **Ctrl+C (SIGINT)**: Exit handlers ensure data is saved before termination
- **Error/Exception**: try-finally blocks guarantee cleanup
- **TUI Close**: on_unmount event triggers storage cleanup

## Programmatic Usage

```python
from vibedialer.dialer import PhoneDialer
from vibedialer.backends import BackendType
from vibedialer.storage import StorageType

# Create dialer with CSV storage
dialer = PhoneDialer(
    backend_type=BackendType.SIMULATION,
    storage_type=StorageType.CSV,
    filename="my_results.csv"
)

try:
    # Dial numbers - results saved automatically
    result = dialer.dial("555-1234")
    print(f"Result: {result.status}")
finally:
    # Ensure cleanup happens
    dialer.cleanup()
```

## Storage File Locations

By default, storage files are created in the current working directory:

- CSV: `vibedialer_results.csv`
- SQLite: `vibedialer_results.db`

Use the `--output` flag to specify custom locations:

```bash
# Absolute path
vibedialer dial 555-12 --storage csv --output /path/to/results.csv

# Relative path
vibedialer dial 555-12 --storage sqlite --output ../data/scan.db
```

## Performance Considerations

### CSV Storage

- **Pros**: Human-readable, universally compatible, simple format
- **Cons**: Slower for large datasets, no query capabilities

**Best for**: Small to medium scans (< 10,000 numbers), when you need to view results in a spreadsheet

### SQLite Storage

- **Pros**: Fast queries, indexed, compact, supports complex analysis
- **Cons**: Binary format (not human-readable without tools)

**Best for**: Large scans (> 10,000 numbers), when you need to query and analyze results

### Dry-Run

- **Pros**: No disk I/O, fastest option
- **Cons**: Data not persisted

**Best for**: Testing, demonstrations, when results aren't needed

## Best Practices

1. **Choose the right storage type**:
   - CSV for simple scans and manual review
   - SQLite for large scans and analysis
   - Dry-run for testing

2. **Use meaningful filenames**:
   ```bash
   vibedialer dial 555-12 --storage csv --output scan_555-12_2025-11-15.csv
   ```

3. **Back up your data**:
   - Storage files contain valuable scan results
   - Consider backing up before re-running scans

4. **Clean up old results**:
   - CSV and SQLite files persist between runs
   - Delete old files or use unique names for each scan

## Troubleshooting

### Permission Errors

```
Error: [Errno 13] Permission denied: 'results.csv'
```

**Solution**: Check file permissions or use a different output location

### File Already Open

```
Error: database is locked
```

**Solution**: Close other applications accessing the database file

### Disk Space

For large scans, ensure adequate disk space:
- CSV: ~100 bytes per result
- SQLite: ~50 bytes per result (more compact)

## Resuming Interrupted Sessions

VibeDialer can resume from interrupted dialing sessions, picking up where you left off.

### Basic Resume

```bash
# Resume from a CSV file with explicit prefix
vibedialer dial 555-12 --resume vibedialer_results.csv --resume-prefix 555-12

# Resume from SQLite database
vibedialer dial 555-12 --resume vibedialer_results.db --resume-prefix 555-12
```

### Automatic Pattern Inference

VibeDialer can automatically infer the pattern from your results file:

```bash
# Infer pattern automatically (silent mode)
vibedialer dial 555-12 --resume vibedialer_results.csv

# Infer with confirmation prompt
vibedialer dial 555-12 --resume vibedialer_results.csv --infer-prefix
```

When using `--infer-prefix`, you'll see:

```
Inferred pattern from vibedialer_results.csv: 555-12
  Total numbers in pattern: 100
  Already dialed: 37
  Remaining to dial: 63

Continue with this pattern? [y/N]:
```

### How It Works

1. **Reads Completed Numbers**: Scans the results file for already-dialed numbers
2. **Infers Pattern**: Finds the common prefix (e.g., "555-12" from "555-1200", "555-1201", etc.)
3. **Calculates Remaining**: Generates full list and filters out completed numbers
4. **Continues Dialing**: Dials only the remaining numbers

### Resume Examples

**Scenario 1: Power Outage**
```bash
# Start scan
vibedialer dial 555-12 --backend modem --storage csv

# Power goes out after 37 numbers...

# Resume later
vibedialer dial dummy --resume vibedialer_results.csv --backend modem
```

**Scenario 2: Network Error**
```bash
# Scan interrupted at number 523
vibedialer dial 212-555 --backend modem --storage sqlite --output scan.db

# Resume with explicit prefix
vibedialer dial dummy --resume scan.db --resume-prefix 212-555 --backend modem
```

**Scenario 3: Partial Completion**
```bash
# You dialed 555-1200 through 555-1250, want to finish 555-12xx

# Check what's left with --infer-prefix
vibedialer dial dummy --resume results.csv --infer-prefix

# If pattern looks good, resume
vibedialer dial dummy --resume results.csv --backend modem
```

### Resume with Different Storage

You can resume from one file and save to another:

```bash
# Resume from CSV, save to SQLite
vibedialer dial dummy \
  --resume old_scan.csv \
  --storage sqlite \
  --output new_scan.db

# Resume from SQLite, save to new CSV
vibedialer dial dummy \
  --resume scan.db \
  --storage csv \
  --output continued_scan.csv
```

### Resume Options

| Flag | Description |
|------|-------------|
| `--resume <file>` | Resume from results file (CSV or SQLite) |
| `--resume-prefix <prefix>` | Explicit pattern to resume (e.g., "555-12") |
| `--infer-prefix` | Show inferred pattern and ask for confirmation |

### Pattern Inference Rules

VibeDialer infers patterns by finding the common prefix of dialed numbers:

- `555-1200` through `555-1299` → `555-12` (100 numbers)
- `555-0000` through `555-9999` → `555` (10,000 numbers)
- `212-5550` through `212-5559` → `212-555` (10 numbers)

For best results:
- Keep prefix explicit when resuming large ranges
- Use `--infer-prefix` to verify pattern before long scans
- Resume files should contain contiguous ranges for accurate inference

### Troubleshooting Resume

**"Could not infer pattern"**
- Solution: Use `--resume-prefix` to specify pattern explicitly
- Cause: Numbers in file don't share a common prefix

**"No dialed numbers found"**
- Solution: Check file path and format
- Cause: Empty results file or wrong file type

**Wrong pattern inferred**
- Solution: Use `--infer-prefix` to check, then provide explicit `--resume-prefix`
- Cause: Mixed patterns in same file

## Advanced Usage

### Querying SQLite Results

```bash
# Connect to database
sqlite3 vibedialer_results.db

# Example queries
.mode column
.headers on

SELECT status, COUNT(*) FROM dial_results GROUP BY status;
SELECT * FROM dial_results WHERE carrier_detected = 1;
```

### Converting CSV to SQLite

```bash
# Import CSV into SQLite
sqlite3 results.db <<EOF
.mode csv
.import vibedialer_results.csv dial_results
EOF
```

### Exporting SQLite to CSV

```bash
sqlite3 -header -csv vibedialer_results.db \
  "SELECT * FROM dial_results" > export.csv
```
