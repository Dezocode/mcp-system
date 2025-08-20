# File Creation Time Standards for MCP System

## Standard Timestamp Formats

### 1. **ISO 8601 Compatible (Primary)**
```
Format: YYYY-mm-dd_HH-MM-SS
Example: 2024-08-20_14-30-45
Usage: Primary format for all system files
```

### 2. **Compact ISO (Secondary)**
```
Format: YYYYmmdd-HHMMSS  
Example: 20240820-143045
Usage: Lint reports, session files (space-constrained)
```

### 3. **Full ISO 8601 (Documentation)**
```
Format: YYYY-mm-ddTHH:MM:SSZ
Example: 2024-08-20T14:30:45Z
Usage: JSON metadata, API responses
```

### 4. **Human Readable (Reports)**
```
Format: YYYY-mm-dd HH:MM:SS
Example: 2024-08-20 14:30:45
Usage: User-facing reports, logs
```

## File Naming Conventions

### **Configuration Files**
```
claude-lint-report-20240820-143045.json
claude_patch_session_20240820_143045.json
mcp-pipeline-state-20240820-143045.json
```

### **Documentation Files**
```
final_report_20240820_143045.md
pipeline_run_20240820_143045.md
```

### **Backup Files**
```
version_keeper_20240820_143045.py.backup
mcp-system_20240820_143045.tar.gz
```

## Watchdog Integration

The file sync manager automatically recognizes these patterns:
- Timestamps in filenames for organization
- Creation time metadata preservation
- Automatic directory routing based on timestamp patterns

## Implementation Notes

1. **Consistency**: Always use the same format within file types
2. **Sortability**: Formats are lexicographically sortable
3. **Timezone**: Use UTC for system files, local time for user files
4. **Parsing**: Standard regex patterns available in sync manager

## Standard Creation Time Metadata

```python
# File metadata example
{
    "created_at": "2024-08-20T14:30:45Z",
    "created_timestamp": 1724162645,
    "created_readable": "2024-08-20 14:30:45",
    "filename_timestamp": "20240820-143045"
}
```