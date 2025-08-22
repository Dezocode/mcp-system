# MCP System Development Instructions

**ALWAYS follow these instructions first and only fallback to additional search and context gathering if the information here is incomplete or found to be in error.**

## Working Effectively

### Bootstrap and Dependencies
- **Install Python 3.8+ (3.12+ recommended)**: Verify with `python3 --version`
- **Install Git**: Required for repository operations
- **Install Node.js 18+**: Required for TypeScript templates and some features
- **Install Docker** (optional): For containerized deployment

### Build and Install Process
```bash
# NEVER CANCEL: Dependency installation takes 2-3 minutes
cd /path/to/mcp-system
pip install -r requirements.txt --timeout=300
```

**CRITICAL TIMING**: Set timeout to 300+ seconds. NEVER CANCEL dependency installation as it requires downloading multiple packages.

### Development Installation
```bash
# NEVER CANCEL: Package installation takes 2-3 minutes  
pip install -e . --timeout=300
```

If installation fails due to network issues, retry with:
```bash
pip install -r requirements.txt --timeout=300 --retries=3
```

### Run Tests
```bash
# Fast execution: Tests complete in 1-2 seconds
python -m pytest tests/ -v
```

**Expected Results**: 23-25 tests should pass, 0-2 may be skipped. Tests are very fast.

### Code Quality and Linting
```bash
# Instant execution: Format checking
black --check src/ tests/

# Instant execution: Import sorting  
isort --check-only src/ tests/

# Moderate execution: Type checking takes 10-15 seconds
mypy src/ --timeout=30

# Optional: Fix formatting automatically
black src/ tests/
isort src/ tests/
```

**ALWAYS run these before committing** or CI will fail.

## Manual Validation and Testing

### Test Core Installation System
```bash
# Test installation script - takes 30-60 seconds
chmod +x bin/install.sh
./bin/install.sh
```

### Test MCP Server Components
```bash
# Test core Python modules
python src/install_mcp_system.py

# Test MCP server (requires PYTHONPATH)
PYTHONPATH=/path/to/mcp-system python src/pipeline_mcp_server.py

# Test other components
python src/claude_code_mcp_bridge.py --help
```

### Test Auto-Discovery System  
```bash
# Test project initialization
python src/auto_discovery_system.py --help
```

### Validate Docker Configuration
```bash
# Quick validation without full build
./validate.sh
```

## Docker Deployment

### Build Docker Image
```bash
# NEVER CANCEL: Docker build takes 5-10 minutes
docker build -t mcp-system:latest . --timeout=900
```

**CRITICAL**: Set timeout to 900+ seconds (15+ minutes). Docker builds can be slow.

### Production Deployment
```bash
# NEVER CANCEL: Full deployment takes 3-5 minutes
./deploy.sh --timeout=400
```

**Note**: Docker builds may fail in environments with SSL certificate issues or network timeouts. This is environment-specific, not a code issue. If builds fail with SSL errors, this indicates network infrastructure limitations.

### Known Build Issues
- **SSL certificate verification failed**: Environment network policy issue
- **Read timed out errors**: Network connectivity problems  
- **PyPI connection failures**: Temporary infrastructure issues

These issues are **NOT code problems** and should be retried or reported as infrastructure issues.

## Performance and Timing Expectations

### Command Timing Reference
- **Tests**: 1 second (very fast)
- **Linting**: Instant for black/isort, 9 seconds for mypy  
- **pip install**: 2-3 minutes (**NEVER CANCEL**)
- **Docker build**: 5-10 minutes (**NEVER CANCEL**)
- **Full deployment**: 3-5 minutes (**NEVER CANCEL**)
- **Installation script**: 30-60 seconds
- **Complete validation workflow**: Under 3 seconds total

### Required Timeout Values
- **pip operations**: 300+ seconds minimum
- **Docker builds**: 900+ seconds minimum  
- **Deployment scripts**: 400+ seconds minimum
- **Test suite**: 30 seconds (but usually completes in 1-2 seconds)

## Key Project Structure

### Core Components
```
src/
├── pipeline_mcp_server.py      # Main MCP server implementation
├── install_mcp_system.py       # Installation system
├── claude_code_mcp_bridge.py   # Claude integration bridge
├── auto_discovery_system.py    # Project auto-discovery
└── mcp_local_types.py          # Type definitions
```

### Build and Configuration Files
```
pyproject.toml          # Main project configuration and dependencies
requirements.txt        # Python dependencies
.github/workflows/      # CI/CD pipeline definitions
docker-compose.prod.yml # Production Docker orchestration
Dockerfile             # Container build definition
```

### Testing and Quality
```
tests/                  # Test suite (pytest-based)
.flake8                # Linting configuration
```

### Scripts and Tools
```
bin/install.sh         # One-click installation
bin/mcp-universal      # Universal launcher
deploy.sh             # Production deployment
validate.sh           # Configuration validation
run-pipeline          # Pipeline execution
```

## Validation Scenarios

### Manual Functional Testing Scenarios

After any code changes, ALWAYS test these complete user workflows:

1. **MCP Server Integration Test**:
   ```bash
   # Start the MCP server and verify functionality
   PYTHONPATH=/path/to/mcp-system python src/pipeline_mcp_server.py
   ```
   **Verify**: Server starts, logs show "6 tools available", "MCP Protocol: v1.0"

2. **Installation System Test**:
   ```bash
   # Test the complete installation workflow
   python src/install_mcp_system.py
   ./bin/install.sh
   ```
   **Verify**: Installation completes without errors, directories created

3. **Pipeline Integration Test**:
   ```bash
   # Test pipeline components
   python src/auto_discovery_system.py
   ```
   **Verify**: Auto-discovery runs successfully

4. **Docker Configuration Test**:
   ```bash
   # Validate Docker setup without building
   ./validate.sh
   ```
   **Verify**: All validation checks pass, report generated

**CRITICAL**: Simply checking that scripts start/stop is NOT sufficient. You must verify actual functionality and expected outputs.

### Essential Validation Steps  
After running the manual functional tests above, ALWAYS run these automated validation scenarios:

1. **Test Suite Validation**:
   ```bash
   python -m pytest tests/ -v
   ```
   **Expected**: 23+ tests pass, 0-2 skipped

2. **Code Quality Validation**:
   ```bash
   black --check src/ tests/
   isort --check-only src/ tests/
   mypy src/
   ```
   **Expected**: No formatting issues, type checking passes

3. **Installation Validation**:
   ```bash
   python src/install_mcp_system.py
   ```
   **Expected**: Installation completes successfully

4. **MCP Server Validation**:
   ```bash
   PYTHONPATH=/path/to/mcp-system python src/pipeline_mcp_server.py
   ```
   **Expected**: Server starts, shows "6 tools available", "MCP Protocol: v1.0"

### Complete End-to-End Validation
```bash
# Full workflow validation - NEVER CANCEL: Takes under 3 seconds total
python -m pytest tests/ -v
black --check src/ tests/
isort --check-only src/ tests/  
python src/install_mcp_system.py
./validate.sh
```

## Common Issues and Solutions

### Network-Related Issues
- **pip install timeouts**: Retry with `--retries=3` flag
- **Docker build SSL errors**: Environment-specific, not code issues
- **PyPI connection failures**: Wait and retry, use longer timeouts

### Build Issues
- **Missing dependencies**: Ensure Python 3.8+ installed
- **Permission errors**: Use `chmod +x` on shell scripts
- **Import errors**: Run `pip install -e .` to install package

### Test Issues  
- **Test failures**: Expected if dependencies missing
- **Skipped tests**: Normal, indicates optional functionality

## CI/CD Integration

The project includes GitHub Actions workflows:
- **ci.yml**: Runs tests, linting, security scans
- **docker-deployment.yml**: Container builds and deployment
- **pipeline-integration.yml**: Full pipeline validation

### Local CI Simulation
```bash
# Simulate CI pipeline locally
python -m pytest tests/ --cov=src --cov-report=xml -v
black --check src/ tests/
isort --check-only src/ tests/
mypy src/
```

## Critical Reminders

1. **NEVER CANCEL** any build, install, or deployment operation
2. **ALWAYS** set appropriate timeouts (5+ minutes for builds)
3. **ALWAYS** run the complete validation scenarios after changes
4. **ALWAYS** test actual functionality, not just startup/shutdown
5. **Network issues** are environment-specific, not code problems
6. **Use validated timeout values** from this documentation
7. **Run linting before committing** or CI will fail

## Emergency Recovery

If builds consistently fail:
1. Check Python version: `python3 --version` (need 3.8+)
2. Clear pip cache: `pip cache purge`
3. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
4. Check network connectivity to PyPI
5. Try Docker build without cache: `docker build --no-cache`

This system is production-ready with comprehensive CI/CD, Docker deployment, and extensive testing. Follow these instructions exactly for reliable development workflow.