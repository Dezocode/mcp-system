# Non-Functional File Types - Internal Trash Classification

## File Types for Internal Trash Directory

### 🗑️ **System Generated Files (Auto-Trash)**
```
.DS_Store           # macOS Finder metadata
Thumbs.db          # Windows thumbnail cache  
.gitkeep           # Empty directory placeholders
*.tmp              # Temporary files
*.temp             # Temporary files
*.swp              # Vim swap files
*.swo              # Vim swap files
*~                 # Editor backup files
.#*                # Emacs lock files
```

### 📊 **Log Files (Conditional Trash)**
```
*.log              # General log files
pipeline-daemon-*.log  # Pipeline daemon logs
.pipeline-*.log    # Pipeline system logs
*.trace            # Debug trace files
*.debug            # Debug output files
audit-*.log        # Audit logs
error-*.log        # Error logs
```

### 🔧 **Cache & Compiled Files (Auto-Trash)**
```
__pycache__/       # Python bytecode cache
*.pyc              # Python compiled files
*.pyo              # Python optimized files
*.egg-info/        # Python egg metadata
.pytest_cache/     # Pytest cache
node_modules/      # Node.js dependencies (if unused)
.coverage          # Coverage reports
*.cache            # Generic cache files
```

### 🔒 **Lock & Process Files (Auto-Trash)**
```
*.pid              # Process ID files
*.lock             # Lock files
*.socket           # Socket files
*.monitor.pid      # Monitor process files
.running           # Running status files
```

### 💾 **Database & Binary Files (Conditional)**
```
*.sqlite           # SQLite databases (if temporary)
*.db               # Database files (if temporary)
*.dump             # Memory dumps
*.core             # Core dumps
*.dmp              # Windows dump files
*.stackdump        # Stack dump files
```

### 🔨 **Compiled Binaries (Platform-Specific)**
```
*.exe              # Windows executables
*.dll              # Windows libraries  
*.so               # Linux shared objects
*.dylib            # macOS dynamic libraries
*.a                # Static libraries
*.o                # Object files
*.obj              # Windows object files
```

## Trash Directory Structure

```
.mcp-system-trash-internal/
├── auto-removed/          # Files automatically moved
│   ├── system/           # OS-generated files
│   ├── cache/           # Cache and compiled files
│   ├── logs/            # Log files
│   └── temp/            # Temporary files
├── conditional/          # Files requiring manual review
│   ├── databases/       # Database files
│   ├── binaries/        # Compiled binaries
│   └── unknown/         # Unclassified files
└── metadata/
    ├── moved-files.json # Tracking moved files
    └── restore.md       # Restoration instructions
```

## Safety Rules

### ✅ **Always Safe to Move**
- System metadata files (.DS_Store, Thumbs.db)
- Editor temporary files (*.swp, *~)
- Python cache (__pycache__/, *.pyc)
- Lock/PID files older than 24 hours
- Log files older than 7 days

### ⚠️ **Conditional - Review First**
- Database files (might contain data)
- Binary executables (might be needed)
- Large cache directories
- Process files from active processes

### ❌ **Never Move**
- Source code files (*.py, *.js, *.md, etc.)
- Configuration files in active use
- Active lock files (from running processes)
- Required system binaries

## Implementation Strategy

1. **Scan Phase**: Identify non-functional files
2. **Classification**: Sort into auto-trash vs conditional
3. **Safety Check**: Verify files aren't actively used
4. **Move Operation**: Transfer to internal trash with metadata
5. **Monitoring**: Track moved files for potential restoration
6. **Cleanup**: Periodically purge old trash entries

## Watchdog Integration

The file sync manager will:
- Automatically detect new non-functional files
- Move them to appropriate trash subdirectories
- Log all movements with timestamps
- Provide restoration mechanisms
- Skip files that match "never move" patterns