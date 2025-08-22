#!/bin/bash
#
# Setup Docker Secrets for MCP System Production Deployment
# This script creates secret files from environment variables
#

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[SECRETS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[SECRETS]${NC} $1"; }
log_error() { echo -e "${RED}[SECRETS]${NC} $1"; }

# Ensure secrets directory exists
SECRETS_DIR="./secrets"
mkdir -p "$SECRETS_DIR"

log_info "Setting up Docker secrets for MCP System..."

# Setup database password
if [ -n "$DB_PASSWORD" ] && [ "$DB_PASSWORD" != "your_secure_db_password_here" ]; then
    echo "$DB_PASSWORD" > "$SECRETS_DIR/db_password.txt"
    log_info "✅ Database password secret created"
elif [ ! -f "$SECRETS_DIR/db_password.txt" ]; then
    log_warn "⚠️  DB_PASSWORD not set or using placeholder value"
    log_warn "   Please set a secure database password:"
    log_warn "   export DB_PASSWORD='your_secure_password'"
    log_warn "   Or manually create: $SECRETS_DIR/db_password.txt"
else
    log_info "✅ Database password secret already exists"
fi

# Setup Grafana password
if [ -n "$GRAFANA_PASSWORD" ] && [ "$GRAFANA_PASSWORD" != "your_secure_grafana_password_here" ]; then
    echo "$GRAFANA_PASSWORD" > "$SECRETS_DIR/grafana_password.txt"
    log_info "✅ Grafana password secret created"
elif [ ! -f "$SECRETS_DIR/grafana_password.txt" ]; then
    log_warn "⚠️  GRAFANA_PASSWORD not set or using placeholder value"
    log_warn "   Please set a secure Grafana password:"
    log_warn "   export GRAFANA_PASSWORD='your_secure_password'"
    log_warn "   Or manually create: $SECRETS_DIR/grafana_password.txt"
else
    log_info "✅ Grafana password secret already exists"
fi

# Setup JWT secret
if [ -n "$JWT_SECRET_KEY" ] && [ "$JWT_SECRET_KEY" != "your-production-jwt-secret-key-here" ]; then
    echo "$JWT_SECRET_KEY" > "$SECRETS_DIR/jwt_secret.txt"
    log_info "✅ JWT secret created"
elif [ ! -f "$SECRETS_DIR/jwt_secret.txt" ]; then
    log_warn "⚠️  JWT_SECRET_KEY not set or using placeholder value"
    log_warn "   Generating a secure JWT secret..."
    openssl rand -base64 32 > "$SECRETS_DIR/jwt_secret.txt"
    log_info "✅ Generated secure JWT secret"
else
    log_info "✅ JWT secret already exists"
fi

# Set secure permissions
chmod 600 "$SECRETS_DIR"/*.txt 2>/dev/null || true
log_info "✅ Secure permissions set on secret files"

echo ""
log_info "📋 Secret Files Status:"
echo "========================"
for secret in db_password.txt grafana_password.txt jwt_secret.txt; do
    if [ -f "$SECRETS_DIR/$secret" ]; then
        size=$(stat -c%s "$SECRETS_DIR/$secret" 2>/dev/null || echo "0")
        if [ "$size" -gt 0 ]; then
            echo "  ✅ $secret (${size} bytes)"
        else
            echo "  ❌ $secret (empty file)"
        fi
    else
        echo "  ❌ $secret (missing)"
    fi
done

echo ""
log_info "🔐 Security Recommendations:"
echo "============================"
echo "  1. Verify all secret files contain strong, unique values"
echo "  2. Keep secret files out of version control (.gitignore)"
echo "  3. Restrict file permissions: chmod 600 ./secrets/*.txt"
echo "  4. Consider using external secret management in production"
echo "  5. Rotate secrets regularly"

echo ""
log_info "🚀 Next Steps:"
echo "=============="
echo "  1. Review and validate secret values"
echo "  2. Update .env.prod with your configuration"
echo "  3. Run: ./deploy.sh"
echo ""

# Check if we have all required secrets
missing_secrets=0
for secret in db_password.txt grafana_password.txt jwt_secret.txt; do
    if [ ! -f "$SECRETS_DIR/$secret" ] || [ ! -s "$SECRETS_DIR/$secret" ]; then
        missing_secrets=1
        break
    fi
done

if [ $missing_secrets -eq 0 ]; then
    log_info "🎉 All secrets are configured and ready for deployment!"
    exit 0
else
    log_error "❌ Some secrets are missing or empty. Please review and fix before deployment."
    exit 1
fi