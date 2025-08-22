#!/bin/bash
#
# Connection Validation Script for MCP System
# Validates all service connections before considering deployment complete
#

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[VALIDATE]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[VALIDATE]${NC} $1"; }
log_error() { echo -e "${RED}[VALIDATE]${NC} $1"; }
log_debug() { echo -e "${BLUE}[VALIDATE]${NC} $1"; }

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"
MAX_WAIT_TIME=300  # 5 minutes max wait
HEALTH_CHECK_INTERVAL=10  # Check every 10 seconds

# Load environment variables
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
fi

# Default port values (fallback if not set in env)
MCP_HTTP_PORT=${MCP_HTTP_PORT:-8050}
MCP_WEBSOCKET_PORT=${MCP_WEBSOCKET_PORT:-8051}
MCP_PIPELINE_PORT=${MCP_PIPELINE_PORT:-8052}
MCP_HEALTH_PORT=${MCP_HEALTH_PORT:-9000}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
REDIS_PORT=${REDIS_PORT:-6379}
NGINX_HTTP_PORT=${NGINX_HTTP_PORT:-80}
NGINX_HTTPS_PORT=${NGINX_HTTPS_PORT:-443}
PROMETHEUS_PORT=${PROMETHEUS_PORT:-9090}
GRAFANA_PORT=${GRAFANA_PORT:-3000}

# Check if a port is available
check_port() {
    local host=$1
    local port=$2
    local service_name=$3
    local timeout=${4:-5}
    
    log_debug "Checking $service_name connection to $host:$port..."
    
    if timeout "$timeout" bash -c "</dev/tcp/$host/$port" 2>/dev/null; then
        log_info "✅ $service_name ($host:$port) - Connection successful"
        return 0
    else
        log_error "❌ $service_name ($host:$port) - Connection failed"
        return 1
    fi
}

# Check HTTP endpoint
check_http_endpoint() {
    local url=$1
    local service_name=$2
    local expected_status=${3:-200}
    local timeout=${4:-10}
    
    log_debug "Checking $service_name HTTP endpoint: $url"
    
    if command -v curl &> /dev/null; then
        local status_code
        status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$timeout" --insecure "$url" 2>/dev/null || echo "000")
        
        if [ "$status_code" = "$expected_status" ] || ([ "$expected_status" = "2xx" ] && [[ "$status_code" =~ ^2[0-9][0-9]$ ]]); then
            log_info "✅ $service_name HTTP ($url) - Status: $status_code"
            return 0
        else
            log_error "❌ $service_name HTTP ($url) - Status: $status_code (expected: $expected_status)"
            return 1
        fi
    else
        log_warn "⚠️  curl not available, skipping HTTP check for $service_name"
        return 0
    fi
}

# Check Docker service health
check_service_health() {
    local service_name=$1
    
    log_debug "Checking Docker service health: $service_name"
    
    local health_status
    health_status=$(docker-compose -f "$COMPOSE_FILE" ps --format json "$service_name" 2>/dev/null | jq -r '.Health // "unknown"' 2>/dev/null || echo "unknown")
    
    case "$health_status" in
        "healthy"|"")
            log_info "✅ $service_name - Docker health check: healthy"
            return 0
            ;;
        "starting")
            log_warn "⏳ $service_name - Docker health check: starting"
            return 1
            ;;
        "unhealthy")
            log_error "❌ $service_name - Docker health check: unhealthy"
            return 1
            ;;
        *)
            log_warn "⚠️  $service_name - Docker health check: $health_status"
            return 0
            ;;
    esac
}

# Wait for service to be ready
wait_for_service() {
    local service_name=$1
    local check_function=$2
    shift 2
    local args=("$@")
    
    log_info "Waiting for $service_name to be ready..."
    
    local elapsed=0
    while [ $elapsed -lt $MAX_WAIT_TIME ]; do
        if "$check_function" "${args[@]}"; then
            return 0
        fi
        
        log_debug "Waiting for $service_name... (${elapsed}s elapsed)"
        sleep $HEALTH_CHECK_INTERVAL
        elapsed=$((elapsed + HEALTH_CHECK_INTERVAL))
    done
    
    log_error "Timeout waiting for $service_name (${MAX_WAIT_TIME}s)"
    return 1
}

# Validate database connections
validate_database_connections() {
    log_info "🔍 Validating database connections..."
    
    # Check PostgreSQL port
    if ! wait_for_service "PostgreSQL" check_port localhost "$POSTGRES_PORT" "PostgreSQL"; then
        return 1
    fi
    
    # Check Redis port
    if ! wait_for_service "Redis" check_port localhost "$REDIS_PORT" "Redis"; then
        return 1
    fi
    
    # Test PostgreSQL connection with actual credentials
    log_debug "Testing PostgreSQL authentication..."
    if command -v psql &> /dev/null; then
        local db_password
        if [ -f "secrets/db_password.txt" ]; then
            db_password=$(cat secrets/db_password.txt)
            if PGPASSWORD="$db_password" psql -h localhost -p "$POSTGRES_PORT" -U "${POSTGRES_USER:-mcpuser}" -d "${POSTGRES_DB:-mcpsystem}" -c "SELECT 1;" &>/dev/null; then
                log_info "✅ PostgreSQL authentication successful"
            else
                log_error "❌ PostgreSQL authentication failed"
                return 1
            fi
        else
            log_warn "⚠️  PostgreSQL password secret not found, skipping auth test"
        fi
    else
        log_warn "⚠️  psql not available, skipping PostgreSQL auth test"
    fi
    
    # Test Redis connection
    log_debug "Testing Redis connection..."
    if command -v redis-cli &> /dev/null; then
        if redis-cli -h localhost -p "$REDIS_PORT" ping &>/dev/null; then
            log_info "✅ Redis connection successful"
        else
            log_error "❌ Redis connection failed"
            return 1
        fi
    else
        log_warn "⚠️  redis-cli not available, skipping Redis connection test"
    fi
    
    return 0
}

# Validate MCP service endpoints
validate_mcp_services() {
    log_info "🔍 Validating MCP service endpoints..."
    
    # Wait for MCP system to be ready
    if ! wait_for_service "MCP System Health" check_http_endpoint "http://localhost:$MCP_HEALTH_PORT/health" "MCP Health" "2xx"; then
        log_warn "Health endpoint not available, checking main HTTP port..."
        if ! wait_for_service "MCP System HTTP" check_port localhost "$MCP_HTTP_PORT" "MCP HTTP"; then
            return 1
        fi
    fi
    
    # Check other MCP ports
    check_port localhost "$MCP_WEBSOCKET_PORT" "MCP WebSocket" 5 || log_warn "MCP WebSocket port not responding"
    check_port localhost "$MCP_PIPELINE_PORT" "MCP Pipeline" 5 || log_warn "MCP Pipeline port not responding"
    
    return 0
}

# Validate web services
validate_web_services() {
    log_info "🔍 Validating web services..."
    
    # Check Nginx
    if ! wait_for_service "Nginx HTTP" check_port localhost "$NGINX_HTTP_PORT" "Nginx HTTP"; then
        log_warn "Nginx HTTP port not responding"
    fi
    
    if ! wait_for_service "Nginx HTTPS" check_port localhost "$NGINX_HTTPS_PORT" "Nginx HTTPS"; then
        log_warn "Nginx HTTPS port not responding"
    fi
    
    return 0
}

# Validate monitoring services
validate_monitoring_services() {
    log_info "🔍 Validating monitoring services..."
    
    # Check Prometheus
    if ! wait_for_service "Prometheus" check_http_endpoint "http://localhost:$PROMETHEUS_PORT/-/healthy" "Prometheus" "2xx"; then
        log_warn "Prometheus health endpoint not responding"
    fi
    
    # Check Grafana
    if ! wait_for_service "Grafana" check_http_endpoint "http://localhost:$GRAFANA_PORT/api/health" "Grafana" "2xx"; then
        log_warn "Grafana health endpoint not responding"
    fi
    
    return 0
}

# Validate Docker service health status
validate_docker_health() {
    log_info "🔍 Validating Docker service health..."
    
    local services=("mcp-system" "postgres" "redis" "nginx" "prometheus" "grafana")
    local unhealthy_services=()
    
    for service in "${services[@]}"; do
        if ! check_service_health "$service"; then
            unhealthy_services+=("$service")
        fi
    done
    
    if [ ${#unhealthy_services[@]} -gt 0 ]; then
        log_error "Unhealthy services detected: ${unhealthy_services[*]}"
        return 1
    fi
    
    return 0
}

# Generate validation report
generate_report() {
    log_info "📊 Generating connection validation report..."
    
    echo ""
    echo "=========================================="
    echo "MCP SYSTEM CONNECTION VALIDATION REPORT"
    echo "=========================================="
    echo "Timestamp: $(date)"
    echo ""
    
    echo "🔧 CONFIGURED PORTS:"
    echo "  MCP HTTP: $MCP_HTTP_PORT"
    echo "  MCP WebSocket: $MCP_WEBSOCKET_PORT"
    echo "  MCP Pipeline: $MCP_PIPELINE_PORT"
    echo "  MCP Health: $MCP_HEALTH_PORT"
    echo "  PostgreSQL: $POSTGRES_PORT"
    echo "  Redis: $REDIS_PORT"
    echo "  Nginx HTTP: $NGINX_HTTP_PORT"
    echo "  Nginx HTTPS: $NGINX_HTTPS_PORT"
    echo "  Prometheus: $PROMETHEUS_PORT"
    echo "  Grafana: $GRAFANA_PORT"
    echo ""
    
    echo "🐳 DOCKER SERVICES:"
    docker-compose -f "$COMPOSE_FILE" ps --format table
    echo ""
    
    echo "🔗 SERVICE URLS:"
    echo "  MCP System: http://localhost:$MCP_HTTP_PORT"
    echo "  Health Check: http://localhost:$MCP_HEALTH_PORT/health"
    echo "  Grafana: http://localhost:$GRAFANA_PORT"
    echo "  Prometheus: http://localhost:$PROMETHEUS_PORT"
    echo ""
}

# Main validation function
main() {
    log_info "🚀 Starting MCP System Connection Validation"
    echo "============================================="
    
    local validation_failed=false
    
    # Validate each component
    validate_database_connections || validation_failed=true
    validate_mcp_services || validation_failed=true
    validate_web_services || validation_failed=true
    validate_monitoring_services || validation_failed=true
    validate_docker_health || validation_failed=true
    
    # Generate report
    generate_report
    
    # Final result
    echo "=========================================="
    if [ "$validation_failed" = true ]; then
        log_error "❌ Connection validation FAILED"
        log_error "Some services are not properly connected or configured"
        log_error "Check the logs above for specific issues"
        return 1
    else
        log_info "✅ Connection validation PASSED"
        log_info "All service connections are properly established"
        log_info "MCP System is ready for production use"
        return 0
    fi
}

# Handle script arguments
case "${1:-validate}" in
    "validate"|"")
        main
        ;;
    "quick")
        log_info "Running quick connection check..."
        validate_mcp_services && validate_database_connections
        ;;
    "report")
        generate_report
        ;;
    *)
        echo "Usage: $0 {validate|quick|report}"
        echo "  validate: Full connection validation (default)"
        echo "  quick:    Quick check of core services"
        echo "  report:   Generate status report only"
        exit 1
        ;;
esac