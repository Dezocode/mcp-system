#!/bin/bash
#
# MCP System Backup Script
# Performs automated backups of database and application data
#

set -e

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="mcpsystem"
DB_USER="mcpuser"
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "🔄 Starting MCP System backup at $(date)"

# Database backup
echo "📄 Backing up database..."
pg_dump -h postgres -U "$DB_USER" -d "$DB_NAME" --no-password | gzip > "$BACKUP_DIR/database_$TIMESTAMP.sql.gz"

# MCP System data backup
echo "💾 Backing up MCP system data..."
if [ -d "/home/mcpuser/.mcp-system" ]; then
    tar -czf "$BACKUP_DIR/mcp_data_$TIMESTAMP.tar.gz" -C /home/mcpuser .mcp-system
fi

# Configuration backup
echo "⚙️ Backing up configuration files..."
tar -czf "$BACKUP_DIR/config_$TIMESTAMP.tar.gz" \
    /app/.env* \
    /app/docker-compose.prod.yml \
    /app/nginx.conf \
    /app/prometheus.yml 2>/dev/null || true

# Cleanup old backups
echo "🧹 Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete

# Verify backups
echo "✅ Verifying backups..."
LATEST_DB_BACKUP=$(ls -t "$BACKUP_DIR"/database_*.sql.gz | head -n1)
if [ -f "$LATEST_DB_BACKUP" ]; then
    echo "  Database backup: $(basename "$LATEST_DB_BACKUP") ($(du -h "$LATEST_DB_BACKUP" | cut -f1))"
else
    echo "  ❌ Database backup failed!"
    exit 1
fi

LATEST_DATA_BACKUP=$(ls -t "$BACKUP_DIR"/mcp_data_*.tar.gz | head -n1)
if [ -f "$LATEST_DATA_BACKUP" ]; then
    echo "  Data backup: $(basename "$LATEST_DATA_BACKUP") ($(du -h "$LATEST_DATA_BACKUP" | cut -f1))"
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