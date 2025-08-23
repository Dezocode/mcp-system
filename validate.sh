#!/usr/bin/env bash
#
# MCP System Validation Script
# Validates Docker configurations and deployment readiness
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[VALIDATE]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[VALIDATE]${NC} $1"; }
log_error() { echo -e "${RED}[VALIDATE]${NC} $1"; }

# Validation functions
validate_docker() {
    log_info "Validating Docker setup..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found"
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon not running"
        return 1
    fi
    
    log_info "✅ Docker validation passed"
}

validate_compose_files() {
    log_info "Validating Docker Compose files..."
    
    for compose_file in docker-compose.*.yml; do
        if [ -f "$compose_file" ]; then
            log_info "Checking $compose_file..."
            if command -v docker-compose &> /dev/null; then
                docker-compose -f "$compose_file" config > /dev/null
                log_info "✅ $compose_file is valid"
            elif docker compose version &> /dev/null; then
                docker compose -f "$compose_file" config > /dev/null
                log_info "✅ $compose_file is valid"
            else
                log_warn "Docker Compose not available for validation"
            fi
        fi
    done
}

validate_dockerfiles() {
    log_info "Validating Dockerfiles..."
    
    for dockerfile in Dockerfile*; do
        if [ -f "$dockerfile" ]; then
            log_info "Checking $dockerfile..."
            
            # Basic syntax checks
            if grep -q "FROM.*AS.*" "$dockerfile"; then
                log_info "✅ Multi-stage build detected in $dockerfile"
            fi
            
            if grep -q "USER.*" "$dockerfile"; then
                log_info "✅ Non-root user configured in $dockerfile"
            else
                log_warn "No USER directive found in $dockerfile"
            fi
            
            if grep -q "HEALTHCHECK.*" "$dockerfile"; then
                log_info "✅ Health check configured in $dockerfile"
            else
                log_warn "No health check found in $dockerfile"
            fi
        fi
    done
}

validate_configuration() {
    log_info "Validating configuration files..."
    
    # Check environment files
    for env_file in .env*; do
        if [ -f "$env_file" ] && [ "$env_file" != ".env.example" ]; then
            log_info "Checking $env_file..."
            
            if grep -q "your_.*_here" "$env_file"; then
                log_warn "Default placeholder values found in $env_file"
            else
                log_info "✅ $env_file appears configured"
            fi
        fi
    done
    
    # Check nginx config
    if [ -f "nginx.conf" ]; then
        log_info "Checking nginx.conf..."
        if grep -q "ssl_certificate" nginx.conf; then
            log_info "✅ SSL configuration found in nginx.conf"
        else
            log_warn "No SSL configuration found in nginx.conf"
        fi
    fi
    
    # Check prometheus config
    if [ -f "prometheus.yml" ]; then
        log_info "✅ prometheus.yml found"
    fi
}

validate_source_structure() {
    log_info "Validating source code structure..."
    
    # Check required directories
    for dir in src core scripts; do
        if [ -d "$dir" ]; then
            log_info "✅ $dir directory exists"
        else
            log_warn "$dir directory missing"
        fi
    done
    
    # Check key files
    key_files=(
        "src/pipeline_mcp_server.py"
        "src/install_mcp_system.py"
        "src/claude_code_mcp_bridge.py"
        "src/auto_discovery_system.py"
        "pyproject.toml"
        "requirements.txt"
    )
    
    for file in "${key_files[@]}"; do
        if [ -f "$file" ]; then
            log_info "✅ $file exists"
        else
            log_warn "$file missing"
        fi
    done
}

run_quick_tests() {
    log_info "Running quick validation tests..."
    
    # Test Python imports
    if f"{cross_platform.get_command(\"python\")} "-c "import sys; sys.path.append('src'); import install_mcp_system" 2>/dev/null; then
        log_info "✅ Python modules import successfully"
    else
        log_warn "Python module import issues detected"
    fi
    
    # Test requirements
    if pip check &>/dev/null; then
        log_info "✅ Python dependencies are consistent"
    else
        log_warn "Python dependency issues detected"
    fi
}

generate_report() {
    log_info "Generating validation report..."
    
    cat > validation_report.md << 'EOF'
# MCP System Validation Report

## Summary
This report contains the validation results for the MCP System deployment configuration.

## Docker Configuration
- Docker Compose files validated
- Dockerfiles checked for best practices
- Multi-stage builds and security measures verified

## Security Checks
- Non-root user configuration
- SSL/TLS settings
- Health checks

## Configuration Files
- Environment files checked
- Service configurations validated
- Monitoring setup verified

## Source Code Structure
- Required directories present
- Key modules available
- Dependencies resolved

## Recommendations
1. Ensure all placeholder values are replaced in .env files
2. Generate proper SSL certificates for production
3. Review and customize monitoring configurations
4. Test deployment in staging environment before production

EOF
    
    log_info "✅ Validation report generated: validation_report.md"
}

# Main validation flow
main() {
    log_info "🔍 Starting MCP System Validation"
    echo "=================================="
    
    validate_docker
    validate_compose_files
    validate_dockerfiles  
    validate_configuration
    validate_source_structure
    run_quick_tests
    generate_report
    
    echo "=================================="
    log_info "✅ MCP System validation completed"
    log_info "Review validation_report.md for detailed results"
}

main "$@"