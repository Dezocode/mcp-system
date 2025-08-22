#!/bin/bash
#
# MCP System Backup Script
# Performs automated backups of database and application data
# Compatible with Docker secrets
#

set -e

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="${POSTGRES_DB:-mcpsystem}"
DB_USER="${POSTGRES_USER:-mcpuser}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "🔄 Starting MCP System backup at $(date)"

# Get database password from secret or environment
if [ -f /run/secrets/db_password ]; then
    export PGPASSWORD=$(cat /run/secrets/db_password)
    echo "📡 Using database password from Docker secret"
elif [ -n "$POSTGRES_PASSWORD" ]; then
    export PGPASSWORD="$POSTGRES_PASSWORD"
    echo "⚠️  Using database password from environment variable"
else
    echo "❌ No database password found in secrets or environment"
    exit 1
fi

# Database backup
echo "📄 Backing up database..."
if ! pg_dump -h postgres -U "$DB_USER" -d "$DB_NAME" --no-password | gzip > "$BACKUP_DIR/database_$TIMESTAMP.sql.gz"; then
    echo "❌ Database backup failed!"
    exit 1
fi

# MCP System data backup
echo "💾 Backing up MCP system data..."
if [ -d "/home/mcpuser/.mcp-system" ]; then
    tar -czf "$BACKUP_DIR/mcp_data_$TIMESTAMP.tar.gz" -C /home/mcpuser .mcp-system
else
    echo "⚠️  MCP system data directory not found, skipping..."
fi

# Configuration backup (excluding secrets for security)
echo "⚙️ Backing up configuration files..."
tar -czf "$BACKUP_DIR/config_$TIMESTAMP.tar.gz" \
    --exclude="secrets/*" \
    --exclude="*.key" \
    --exclude="*.pem" \
    /app/.env* \
    /app/docker-compose.prod.yml \
    /app/nginx.conf \
    /app/prometheus.yml 2>/dev/null || true

# Cleanup old backups
echo "🧹 Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete

# Verify backups
echo "✅ Verifying backups..."
LATEST_DB_BACKUP=$(ls -t "$BACKUP_DIR"/database_*.sql.gz 2>/dev/null | head -n1 || echo "")
if [ -f "$LATEST_DB_BACKUP" ]; then
    echo "  Database backup: $(basename "$LATEST_DB_BACKUP") ($(du -h "$LATEST_DB_BACKUP" | cut -f1))"
else
    echo "  ❌ Database backup failed!"
    exit 1
fi

LATEST_DATA_BACKUP=$(ls -t "$BACKUP_DIR"/mcp_data_*.tar.gz 2>/dev/null | head -n1 || echo "")
if [ -f "$LATEST_DATA_BACKUP" ]; then
    echo "  Data backup: $(basename "$LATEST_DATA_BACKUP") ($(du -h "$LATEST_DATA_BACKUP" | cut -f1))"
fi

LATEST_CONFIG_BACKUP=$(ls -t "$BACKUP_DIR"/config_*.tar.gz 2>/dev/null | head -n1 || echo "")
if [ -f "$LATEST_CONFIG_BACKUP" ]; then
    echo "  Config backup: $(basename "$LATEST_CONFIG_BACKUP") ($(du -h "$LATEST_CONFIG_BACKUP" | cut -f1))"
fi

echo "✅ Backup completed successfully at $(date)"

# Optional: Upload to cloud storage
if [ -n "$BACKUP_CLOUD_BUCKET" ]; then
    echo "☁️ Uploading backups to cloud storage..."
    # Add your cloud storage upload commands here
    # Example for AWS S3:
    # aws s3 cp "$LATEST_DB_BACKUP" s3://"$BACKUP_CLOUD_BUCKET"/database/
    # aws s3 cp "$LATEST_DATA_BACKUP" s3://"$BACKUP_CLOUD_BUCKET"/data/
fi