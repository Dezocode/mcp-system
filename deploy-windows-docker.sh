#!/bin/bash
# 🐳 Automated Windows Docker Desktop Deployment Script
# Fully automated, permissionless deployment for MCP System

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
DEPLOYMENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${DEPLOYMENT_DIR}/.env"
COMPOSE_FILE="${DEPLOYMENT_DIR}/docker-compose.prod.yml"
DOCKERFILE="${DEPLOYMENT_DIR}/Dockerfile.production"

# Auto-generate secure passwords
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if running in WSL
    if ! grep -qEi "(microsoft|wsl)" /proc/version 2>/dev/null; then
        log_warning "Not running in WSL - this script is optimized for WSL2 + Windows Docker Desktop"
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install Docker Desktop on Windows and enable WSL2 integration."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose not found. Please install Docker Desktop with Compose."
        exit 1
    fi
    
    # Verify Docker is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon not running. Please start Docker Desktop."
        exit 1
    fi
    
    log_success "All prerequisites met"
}

# Generate environment file
create_environment() {
    log_info "Creating environment configuration..."
    
    if [[ ! -f "${ENV_FILE}" ]]; then
        cat > "${ENV_FILE}" << EOF
# MCP System Production Environment
# Auto-generated $(date)

# Database Configuration
DB_PASSWORD=$(generate_password)

# Monitoring Configuration  
GRAFANA_PASSWORD=$(generate_password)

# MCP System Configuration
MCP_ENV=production
MCP_DEBUG=false
MCP_LOG_LEVEL=warning
MCP_SAFE_MODE=true
MCP_AUTO_DISCOVERY=true

# Network Configuration
COMPOSE_PROJECT_NAME=mcp-system
DOCKER_BUILDKIT=1

# Backup Configuration
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE=daily
EOF
        log_success "Environment file created with auto-generated passwords"
    else
        log_info "Environment file already exists, skipping generation"
    fi
}

# Stop any existing deployment
cleanup_existing() {
    log_info "Cleaning up existing deployment..."
    
    # Stop and remove containers
    docker-compose -f "${COMPOSE_FILE}" down --remove-orphans 2>/dev/null || true
    
    # Remove old images (optional)
    docker image prune -f &>/dev/null || true
    
    log_success "Cleanup completed"
}

# Build production image
build_image() {
    log_info "Building production Docker image..."
    
    # Use BuildKit for faster builds
    export DOCKER_BUILDKIT=1
    
    # Build with cache optimization
    docker build \
        -f "${DOCKERFILE}" \
        -t mcp-system:latest \
        --cache-from mcp-system:latest \
        "${DEPLOYMENT_DIR}"
    
    log_success "Production image built successfully"
}

# Deploy stack
deploy_stack() {
    log_info "Deploying production stack..."
    
    # Pull external images in parallel
    docker-compose -f "${COMPOSE_FILE}" pull --parallel postgres redis nginx prometheus grafana 2>/dev/null || true
    
    # Start services with health check waits
    docker-compose -f "${COMPOSE_FILE}" up -d --remove-orphans
    
    log_success "Stack deployment initiated"
}

# Wait for services to be healthy
wait_for_health() {
    log_info "Waiting for services to become healthy..."
    
    local max_attempts=60
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        local healthy_count=$(docker-compose -f "${COMPOSE_FILE}" ps --format json 2>/dev/null | \
                             jq -r '.[] | select(.Health == "healthy" or .Health == "") | .Name' | wc -l)
        
        local total_count=$(docker-compose -f "${COMPOSE_FILE}" ps --format json 2>/dev/null | jq -r '.[] | .Name' | wc -l)
        
        if [[ $healthy_count -eq $total_count ]] && [[ $total_count -gt 0 ]]; then
            log_success "All services are healthy"
            return 0
        fi
        
        log_info "Waiting for services... ($healthy_count/$total_count healthy)"
        sleep 5
        ((attempt++))
    done
    
    log_warning "Timeout waiting for all services to become healthy"
    return 1
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check container status
    local failed_services=()
    while IFS= read -r line; do
        if [[ $line =~ Exit\ [^0] ]]; then
            failed_services+=("$(echo "$line" | awk '{print $1}')")
        fi
    done < <(docker-compose -f "${COMPOSE_FILE}" ps)
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        log_error "Failed services detected: ${failed_services[*]}"
        return 1
    fi
    
    # Test service endpoints
    local endpoints=(
        "http://localhost:8050/health:MCP System"
        "http://localhost:9090/-/healthy:Prometheus" 
        "http://localhost:3000/api/health:Grafana"
    )
    
    for endpoint_info in "${endpoints[@]}"; do
        local url=$(echo "$endpoint_info" | cut -d: -f1-2)
        local name=$(echo "$endpoint_info" | cut -d: -f3)
        
        if curl -sf "$url" &>/dev/null; then
            log_success "$name endpoint responding"
        else
            log_warning "$name endpoint not responding (may still be starting)"
        fi
    done
    
    # Database connectivity test
    if docker-compose -f "${COMPOSE_FILE}" exec -T postgres pg_isready -U mcpuser &>/dev/null; then
        log_success "PostgreSQL responding"
    else
        log_warning "PostgreSQL not responding"
    fi
    
    # Redis connectivity test  
    if docker-compose -f "${COMPOSE_FILE}" exec -T redis redis-cli ping &>/dev/null; then
        log_success "Redis responding"
    else
        log_warning "Redis not responding"
    fi
}

# Setup automatic startup
setup_startup() {
    log_info "Setting up automatic startup..."
    
    # Create systemd service for automatic startup
    local service_content="[Unit]
Description=MCP System Docker Stack
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=${DEPLOYMENT_DIR}
ExecStart=/usr/bin/docker-compose -f ${COMPOSE_FILE} up -d
ExecStop=/usr/bin/docker-compose -f ${COMPOSE_FILE} down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target"
    
    # Only create if systemd is available
    if command -v systemctl &>/dev/null; then
        echo "$service_content" | sudo tee /etc/systemd/system/mcp-system.service &>/dev/null
        sudo systemctl daemon-reload
        sudo systemctl enable mcp-system.service
        log_success "Systemd service created for automatic startup"
    else
        log_info "Systemd not available, skipping automatic startup setup"
    fi
}

# Display deployment info
show_deployment_info() {
    log_success "🚀 MCP System deployment completed!"
    echo
    echo "📊 Service URLs:"
    echo "  • MCP System:    http://localhost:8050"
    echo "  • Prometheus:    http://localhost:9090" 
    echo "  • Grafana:       http://localhost:3000"
    echo "  • PostgreSQL:    localhost:5432"
    echo "  • Redis:         localhost:6379"
    echo
    echo "🔐 Grafana Login:"
    echo "  • Username:      admin"
    echo "  • Password:      $(grep GRAFANA_PASSWORD "${ENV_FILE}" | cut -d= -f2)"
    echo
    echo "🛠️ Management Commands:"
    echo "  • View logs:     docker-compose -f ${COMPOSE_FILE} logs -f"
    echo "  • Stop stack:    docker-compose -f ${COMPOSE_FILE} down"
    echo "  • Restart:       docker-compose -f ${COMPOSE_FILE} restart"
    echo "  • Status:        docker-compose -f ${COMPOSE_FILE} ps"
    echo
    echo "💾 Data persisted in Docker volumes - safe to restart containers"
}

# Error handler
handle_error() {
    log_error "Deployment failed at step: $1"
    log_info "Check logs with: docker-compose -f ${COMPOSE_FILE} logs"
    exit 1
}

# Main deployment process
main() {
    echo "🐳 MCP System - Automated Windows Docker Deployment"
    echo "=================================================="
    echo
    
    # Set error trap
    trap 'handle_error "Unknown step"' ERR
    
    check_prerequisites || handle_error "Prerequisites check"
    create_environment || handle_error "Environment creation"
    cleanup_existing || handle_error "Cleanup"
    build_image || handle_error "Image build"
    deploy_stack || handle_error "Stack deployment"
    
    # Wait for health checks (allow partial success)
    wait_for_health || log_warning "Some services may still be starting"
    
    verify_deployment || handle_error "Deployment verification"
    setup_startup || log_warning "Automatic startup setup failed (non-critical)"
    show_deployment_info
    
    log_success "Deployment completed successfully! 🎉"
}

# Run main function
main "$@"