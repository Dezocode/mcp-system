# MCP System Docker Build Analysis

## Executive Summary
The MCP system has significant cross-platform issues that need resolution before Docker containerization.

## Critical Issues Found

### 1. **Hardcoded Platform-Specific Paths**
- **MacOS paths hardcoded**: `/Users/dezmondhollins/` found in 30+ files
- **Windows paths**: Mixed path separators and Windows-specific commands
- **Linux paths**: `/home/mcpuser/` hardcoded in Docker configs

### 2. **Installation Script Issues**

#### Current Dockerfile Problems:
```dockerfile
# Line 24: Missing templates/ directory
COPY templates/ ./templates/

# Line 47: References non-existent install.sh
RUN ./install.sh
```

#### Python Installer Issues:
- Uses `Path.home()` which varies by OS
- No Docker environment detection
- Hardcoded shell script dependencies

### 3. **Missing Components**
- No `templates/` directory exists
- No root `install.sh` file (only in `bin/`)
- Missing `Dockerfile.enhanced` referenced in compose

### 4. **Cross-Platform Incompatibilities**

#### Path Issues:
```python
# In mcp-router.py
cmd = f"/Users/dezmondhollins/mcp {server} start"  # MacOS specific

# Should be:
cmd = f"{os.environ.get('MCP_BIN', 'mcp')} {server} start"
```

#### Shell Scripts:
- Bash-specific syntax not portable to Alpine
- No Windows CMD/PowerShell equivalents

### 5. **Docker Configuration Issues**

#### docker-compose.enhanced.yml:
- References `Dockerfile.enhanced` (doesn't exist)
- Mounts host config files that may not exist
- No build args for cross-platform support

## Recommended Docker Build Strategy

### 1. **Create Multi-Stage Dockerfile**
```dockerfile
# Stage 1: Dependencies
FROM python:3.12-slim AS deps
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Builder
FROM deps AS builder
COPY . .
RUN python scripts/prepare_docker_build.py

# Stage 3: Runtime
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /build/dist /app
```

### 2. **Environment Variables for Paths**
```python
# config/paths.py
import os
from pathlib import Path

MCP_HOME = Path(os.environ.get('MCP_HOME', '/app/.mcp-system'))
MCP_BIN = Path(os.environ.get('MCP_BIN', '/app/bin'))
MCP_DATA = Path(os.environ.get('MCP_DATA', '/app/data'))
```

### 3. **Platform Detection**
```python
# config/platform.py
import platform
import os

def get_platform():
    if os.environ.get('MCP_ENV') == 'docker':
        return 'docker'
    system = platform.system().lower()
    return {
        'darwin': 'macos',
        'linux': 'linux',
        'windows': 'windows'
    }.get(system, 'unknown')
```

### 4. **Create Missing Components**

#### install.sh (root directory):
```bash
#!/bin/bash
set -e

echo "Installing MCP System..."

# Detect environment
if [ -f /.dockerenv ]; then
    export MCP_ENV=docker
fi

# Run Python installer
python3 installers/install-mcp-system.py --docker
```

#### templates/ directory structure:
```
templates/
├── servers/
│   ├── python.template
│   └── typescript.template
├── config/
│   └── default.json
└── docker/
    └── Dockerfile.template
```

### 5. **Fix Hardcoded Paths**

Create a migration script:
```python
# scripts/fix_hardcoded_paths.py
import re
from pathlib import Path

REPLACEMENTS = {
    r'/Users/dezmondhollins/': '${MCP_HOME}/',
    r'/home/mcpuser/': '${MCP_HOME}/',
    r'C:\\\\': '${MCP_HOME}/',
}

def fix_file(filepath):
    content = filepath.read_text()
    for pattern, replacement in REPLACEMENTS.items():
        content = re.sub(pattern, replacement, content)
    filepath.write_text(content)
```

### 6. **Docker Build Script**
```bash
#!/bin/bash
# build-docker.sh

# Fix hardcoded paths
python3 scripts/fix_hardcoded_paths.py

# Create missing directories
mkdir -p templates

# Build Docker image
docker build -t mcp-system:latest .

# Run tests
docker run --rm mcp-system:latest python -m pytest
```

## Implementation Priority

1. **High Priority**:
   - Fix hardcoded paths in all Python files
   - Create missing install.sh
   - Add templates directory
   - Update Dockerfile with correct paths

2. **Medium Priority**:
   - Add platform detection
   - Create Dockerfile.enhanced
   - Update docker-compose files

3. **Low Priority**:
   - Add Windows support
   - Optimize image size
   - Add multi-arch builds

## Testing Strategy

1. Build on each platform:
   ```bash
   docker build --platform linux/amd64 -t mcp:amd64 .
   docker build --platform linux/arm64 -t mcp:arm64 .
   ```

2. Test core functionality:
   ```bash
   docker run --rm mcp:latest mcp --help
   docker run --rm mcp:latest python scripts/version_keeper.py --help
   ```

3. Validate cross-platform:
   ```bash
   docker run --rm -e MCP_ENV=docker mcp:latest python -c "
   from src.config.environment_detector import environment_detector
   print(environment_detector.detect())
   "
   ```

## Next Steps

1. Create platform-agnostic path handling
2. Remove all hardcoded paths
3. Create missing files and directories
4. Test Docker build
5. Create CI/CD pipeline for automated builds