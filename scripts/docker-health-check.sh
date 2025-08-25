#!/bin/bash
# Enhanced Docker Health Check Script
# Comprehensive health validation for containerized MCP environments

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Health check configuration
readonly HEALTH_TIMEOUT=${HEALTH_TIMEOUT:-30}
readonly MAX_RETRIES=${MAX_RETRIES:-3}
readonly RETRY_DELAY=${RETRY_DELAY:-5}

# Health status codes
readonly STATUS_HEALTHY=0
readonly STATUS_WARNING=1
readonly STATUS_CRITICAL=2
readonly STATUS_UNKNOWN=3

# Log function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Check if we're running in Docker
is_docker_environment() {
    [[ -f /.dockerenv ]] || grep -q docker /proc/1/cgroup 2>/dev/null
}

# Check Python health
check_python_health() {
    log "Checking Python environment..."
    
    if ! command -v python3 >/dev/null 2>&1; then
        log_error "Python3 not found"
        return $STATUS_CRITICAL
    fi
    
    # Check if we can import key modules
    if ! python3 -c "import sys, json, pathlib" 2>/dev/null; then
        log_error "Python standard libraries not accessible"
        return $STATUS_CRITICAL
    fi
    
    # Check MCP dependencies
    if ! python3 -c "import mcp" 2>/dev/null; then
        log_warning "MCP library not found"
        return $STATUS_WARNING
    fi
    
    log_success "Python environment healthy"
    return $STATUS_HEALTHY
}

# Check filesystem health
check_filesystem_health() {
    log "Checking filesystem health..."
    
    local issues=0
    
    # Check critical directories
    local directories=("/app" "/tmp" "/app/pipeline-sessions" "/app/logs")
    
    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            if [[ "$dir" == "/app/pipeline-sessions" ]] || [[ "$dir" == "/app/logs" ]]; then
                log_warning "Directory $dir does not exist, creating..."
                mkdir -p "$dir" 2>/dev/null || {
                    log_error "Failed to create directory $dir"
                    ((issues++))
                }
            else
                log_error "Critical directory $dir does not exist"
                ((issues++))
            fi
        elif [[ ! -w "$dir" ]]; then
            log_error "Directory $dir is not writable"
            ((issues++))
        fi
    done
    
    # Check disk space
    local available_space
    available_space=$(df /app 2>/dev/null | awk 'NR==2 {print $4}' || echo "0")
    
    if [[ "$available_space" -lt 100000 ]]; then # Less than 100MB
        log_error "Low disk space: ${available_space}KB available"
        ((issues++))
    elif [[ "$available_space" -lt 500000 ]]; then # Less than 500MB
        log_warning "Disk space getting low: ${available_space}KB available"
    fi
    
    if [[ $issues -eq 0 ]]; then
        log_success "Filesystem healthy"
        return $STATUS_HEALTHY
    elif [[ $issues -le 2 ]]; then
        log_warning "Filesystem has minor issues"
        return $STATUS_WARNING
    else
        log_error "Filesystem has critical issues"
        return $STATUS_CRITICAL
    fi
}

# Check MCP server health
check_mcp_server_health() {
    log "Checking MCP server health..."
    
    # Check if enhanced orchestrator is available
    if [[ -f "/app/mcp-claude-pipeline-enhanced.py" ]]; then
        if python3 /app/mcp-claude-pipeline-enhanced.py --help >/dev/null 2>&1; then
            log_success "Enhanced orchestrator available"
        else
            log_warning "Enhanced orchestrator has issues"
            return $STATUS_WARNING
        fi
    else
        log_warning "Enhanced orchestrator not found"
        return $STATUS_WARNING
    fi
    
    # Check pipeline scripts
    local scripts=("/app/run-pipeline-enhanced" "/app/run-direct-pipeline-enhanced")
    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            if [[ -x "$script" ]]; then
                log_success "Script $script available and executable"
            else
                log_warning "Script $script not executable"
                return $STATUS_WARNING
            fi
        else
            log_warning "Script $script not found"
            return $STATUS_WARNING
        fi
    done
    
    # Check if scripts can run
    if ! /app/run-pipeline-enhanced --help >/dev/null 2>&1; then
        log_error "Enhanced pipeline script has execution issues"
        return $STATUS_CRITICAL
    fi
    
    log_success "MCP server components healthy"
    return $STATUS_HEALTHY
}

# Check process health
check_process_health() {
    log "Checking process health..."
    
    local issues=0
    
    # Check memory usage
    if command -v free >/dev/null 2>&1; then
        local memory_usage
        memory_usage=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
        
        if (( $(echo "$memory_usage > 90" | bc -l 2>/dev/null || echo "0") )); then
            log_error "High memory usage: ${memory_usage}%"
            ((issues++))
        elif (( $(echo "$memory_usage > 75" | bc -l 2>/dev/null || echo "0") )); then
            log_warning "Elevated memory usage: ${memory_usage}%"
        else
            log_success "Memory usage normal: ${memory_usage}%"
        fi
    fi
    
    # Check CPU load if available
    if [[ -f /proc/loadavg ]]; then
        local load_avg
        load_avg=$(cut -d' ' -f1 /proc/loadavg)
        local cpu_count
        cpu_count=$(nproc 2>/dev/null || echo "1")
        
        if (( $(echo "$load_avg > $cpu_count * 2" | bc -l 2>/dev/null || echo "0") )); then
            log_error "High CPU load: $load_avg (CPUs: $cpu_count)"
            ((issues++))
        elif (( $(echo "$load_avg > $cpu_count" | bc -l 2>/dev/null || echo "0") )); then
            log_warning "Elevated CPU load: $load_avg (CPUs: $cpu_count)"
        else
            log_success "CPU load normal: $load_avg (CPUs: $cpu_count)"
        fi
    fi
    
    if [[ $issues -eq 0 ]]; then
        return $STATUS_HEALTHY
    elif [[ $issues -le 1 ]]; then
        return $STATUS_WARNING
    else
        return $STATUS_CRITICAL
    fi
}

# Main health check function
main() {
    log "Starting Enhanced Docker Health Check"
    log "======================================"
    
    if is_docker_environment; then
        log "Running in Docker environment"
    else
        log "Running in local environment"
    fi
    
    # Perform all health checks
    PYTHON_STATUS=$STATUS_UNKNOWN
    FS_STATUS=$STATUS_UNKNOWN
    MCP_STATUS=$STATUS_UNKNOWN
    PROCESS_STATUS=$STATUS_UNKNOWN
    
    check_python_health
    PYTHON_STATUS=$?
    
    check_filesystem_health
    FS_STATUS=$?
    
    check_mcp_server_health
    MCP_STATUS=$?
    
    check_process_health
    PROCESS_STATUS=$?
    
    # Determine overall status
    local overall_status=$STATUS_HEALTHY
    
    for status in $PYTHON_STATUS $FS_STATUS $MCP_STATUS $PROCESS_STATUS; do
        if [[ $status -eq $STATUS_CRITICAL ]]; then
            overall_status=$STATUS_CRITICAL
            break
        elif [[ $status -eq $STATUS_WARNING && $overall_status -eq $STATUS_HEALTHY ]]; then
            overall_status=$STATUS_WARNING
        fi
    done
    
    # Print final status
    echo
    case $overall_status in
        $STATUS_HEALTHY)
            log_success "Health Check PASSED - All systems healthy"
            ;;
        $STATUS_WARNING)
            log_warning "Health Check WARNING - Some issues detected"
            ;;
        $STATUS_CRITICAL)
            log_error "Health Check FAILED - Critical issues detected"
            ;;
        *)
            log_error "Health Check UNKNOWN - Unable to determine status"
            ;;
    esac
    
    exit $overall_status
}

# Run main function
main "$@"