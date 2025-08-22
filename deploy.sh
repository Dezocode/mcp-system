#!/bin/bash
#
# MCP System Production Deployment Script
# Deploys the complete MCP system using Docker Compose
#

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[DEPLOY]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[DEPLOY]${NC} $1"; }
log_error() { echo -e "${RED}[DEPLOY]${NC} $1"; }
log_debug() { echo -e "${BLUE}[DEPLOY]${NC} $1"; }

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"
BACKUP_ENABLED=${BACKUP_ENABLED:-true}

# Check prerequisites
check_prerequisites() {
    log_info "Checking deployment prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is required but not installed"
        return 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is required but not installed"
        return 1
    fi
    
    # Check environment file
    if [ ! -f "$ENV_FILE" ]; then
        log_warn "Environment file $ENV_FILE not found, creating from template..."
        cp .env.prod.example "$ENV_FILE" 2>/dev/null || {
            log_error "Please create $ENV_FILE with your configuration"
            return 1
        }
    fi
    
    # Setup Docker secrets
    log_info "Setting up Docker secrets..."
    if [ -f "scripts/setup-secrets.sh" ]; then
        ./scripts/setup-secrets.sh || {
            log_error "Failed to setup secrets. Please configure secrets manually."
            return 1
        }
    else
        log_warn "Secret setup script not found, checking for manual secret configuration..."
        if [ ! -f "secrets/db_password.txt" ] || [ ! -f "secrets/grafana_password.txt" ] || [ ! -f "secrets/jwt_secret.txt" ]; then
            log_error "Docker secrets not configured. Please run: ./scripts/setup-secrets.sh"
            return 1
        fi
    fi
    
    # Check SSL certificates
    if [ ! -f "ssl/mcp.crt" ] || [ ! -f "ssl/mcp.key" ]; then
        log_warn "SSL certificates not found, generating self-signed certificates..."
        generate_ssl_certificates
    fi
    
    log_info "✅ Prerequisites check passed"
    return 0
}

# Generate self-signed SSL certificates
generate_ssl_certificates() {
    mkdir -p ssl
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/mcp.key \
        -out ssl/mcp.crt \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
        2>/dev/null || {
        log_error "Failed to generate SSL certificates"
        return 1
    }
    
    log_info "✅ Generated self-signed SSL certificates"
}

# Pre-deployment security scan
security_scan() {
    log_info "Running security scan..."
    
    # Scan Docker images for vulnerabilities
    if command -v trivy &> /dev/null; then
        log_debug "Scanning images with Trivy..."
        trivy image --format table dezocode/mcp-system:latest || log_warn "Trivy scan found issues"
    else
        log_warn "Trivy not found, skipping vulnerability scan"
    fi
    
    # Check for secrets in environment file (legacy check)
    if grep -q "your_.*_here" "$ENV_FILE"; then
        log_warn "Default placeholder values found in $ENV_FILE"
        log_warn "These should be migrated to Docker secrets for better security"
    fi
    
    # Check Docker secrets configuration
    local secrets_ok=true
    for secret_file in secrets/db_password.txt secrets/grafana_password.txt secrets/jwt_secret.txt; do
        if [ ! -f "$secret_file" ] || [ ! -s "$secret_file" ]; then
            log_error "Missing or empty secret file: $secret_file"
            secrets_ok=false
        fi
    done
    
    if [ "$secrets_ok" = false ]; then
        log_error "Docker secrets are not properly configured"
        log_error "Run: ./scripts/setup-secrets.sh"
        return 1
    fi
    
    # Check secret file permissions
    for secret_file in secrets/*.txt; do
        if [ -f "$secret_file" ]; then
            perms=$(stat -c "%a" "$secret_file" 2>/dev/null || echo "777")
            if [ "$perms" != "600" ]; then
                log_warn "Insecure permissions on $secret_file (${perms}), should be 600"
                chmod 600 "$secret_file"
                log_info "Fixed permissions on $secret_file"
            fi
        fi
    done
    
    log_info "✅ Security scan completed"
}

# Pre-deployment backup
create_backup() {
    if [ "$BACKUP_ENABLED" = "true" ]; then
        log_info "Creating pre-deployment backup..."
        
        # Check if system is already running
        if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
            docker-compose -f "$COMPOSE_FILE" run --rm backup
            log_info "✅ Backup completed"
        else
            log_debug "No running system to backup"
        fi
    fi
}

# Build and deploy
deploy_system() {
    log_info "Building and deploying MCP System..."
    
    # Pull latest base images
    log_debug "Pulling latest base images..."
    docker-compose -f "$COMPOSE_FILE" pull postgres redis nginx prometheus grafana
    
    # Build application image
    log_debug "Building MCP System image..."
    docker-compose -f "$COMPOSE_FILE" build mcp-system
    
    # Deploy with rolling update strategy
    log_debug "Deploying services..."
    docker-compose -f "$COMPOSE_FILE" up -d --remove-orphans
    
    log_info "✅ Deployment completed"
}

# Post-deployment verification
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Wait for services to be ready
    log_debug "Waiting for services to be ready..."
    sleep 30
    
    # Run comprehensive connection validation
    log_info "Running connection validation..."
    if [ -f "scripts/validate-connections.sh" ]; then
        if ./scripts/validate-connections.sh; then
            log_info "✅ All service connections validated successfully"
        else
            log_error "❌ Connection validation failed"
            log_error "Some services may not be properly connected"
            return 1
        fi
    else
        log_warn "Connection validation script not found, running basic checks..."
        
        # Basic service health check (fallback)
        UNHEALTHY_SERVICES=()
        
        for service in mcp-system postgres redis nginx prometheus grafana; do
            if ! docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "healthy\|Up"; then
                UNHEALTHY_SERVICES+=("$service")
            fi
        done
        
        if [ ${#UNHEALTHY_SERVICES[@]} -gt 0 ]; then
            log_error "Unhealthy services: ${UNHEALTHY_SERVICES[*]}"
            log_error "Check logs: docker-compose -f $COMPOSE_FILE logs <service>"
            return 1
        fi
        
        # Test API endpoints
        log_debug "Testing API endpoints..."
        if ! curl -k -f https://localhost/health &>/dev/null; then
            log_warn "Health check endpoint not responding"
        fi
    fi
    
    log_info "✅ Deployment verification completed"
}

# Show deployment status
show_status() {
    echo ""
    log_info "📊 Deployment Status"
    echo "===================="
    
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    log_info "🔗 Service URLs"
    echo "==============="
    echo "  MCP System:  https://localhost"
    echo "  Grafana:     https://localhost/grafana"
    echo "  Prometheus:  https://localhost/prometheus"
    echo ""
    
    log_info "📄 View logs: docker-compose -f $COMPOSE_FILE logs -f <service>"
    log_info "🛑 Stop services: docker-compose -f $COMPOSE_FILE down"
}

# Main deployment flow
main() {
    log_info "🚀 Starting MCP System Production Deployment"
    echo "=============================================="
    
    # Pre-deployment checks
    if ! check_prerequisites; then
        log_error "Prerequisites check failed"
        exit 1
    fi
    
    if ! security_scan; then
        log_error "Security scan failed"
        exit 1
    fi
    
    # Backup existing system
    create_backup
    
    # Deploy system
    if ! deploy_system; then
        log_error "Deployment failed"
        exit 1
    fi
    
    # Verify deployment
    if ! verify_deployment; then
        log_error "Deployment verification failed"
        exit 1
    fi
    
    # Show status
    show_status
    
    echo "=============================================="
    log_info "🎉 MCP System Production Deployment Complete!"
    log_info "Your MCP system is now running in production mode"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "status")
        docker-compose -f "$COMPOSE_FILE" ps
        ;;
    "logs")
        docker-compose -f "$COMPOSE_FILE" logs -f "${2:-mcp-system}"
        ;;
    "stop")
        docker-compose -f "$COMPOSE_FILE" down
        ;;
    "backup")
        docker-compose -f "$COMPOSE_FILE" run --rm backup
        ;;
    "validate")
        if [ -f "scripts/validate-connections.sh" ]; then
            ./scripts/validate-connections.sh
        else
            log_error "Connection validation script not found"
            exit 1
        fi
        ;;
    "setup-secrets")
        if [ -f "scripts/setup-secrets.sh" ]; then
            ./scripts/setup-secrets.sh
        else
            log_error "Secrets setup script not found"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 {deploy|status|logs|stop|backup|validate|setup-secrets}"
        echo "  deploy:       Full deployment (default)"
        echo "  status:       Show service status"
        echo "  logs:         View service logs"
        echo "  stop:         Stop all services"
        echo "  backup:       Create database backup"
        echo "  validate:     Validate all service connections"
        echo "  setup-secrets: Setup Docker secrets"
        exit 1
        ;;
esac