#!/bin/bash
#
# Setup DATABASE_URL using Docker secret
# This script constructs the DATABASE_URL from Docker secrets and environment variables
#

set -e

# Default values
POSTGRES_USER=${POSTGRES_USER:-mcpuser}
POSTGRES_DB=${POSTGRES_DB:-mcpsystem}
POSTGRES_HOST=${POSTGRES_HOST:-postgres}
POSTGRES_PORT=${POSTGRES_PORT:-5432}

# Read password from Docker secret
if [ -f /run/secrets/db_password ]; then
    DB_PASSWORD=$(cat /run/secrets/db_password)
elif [ -n "$DB_PASSWORD" ]; then
    # Fallback to environment variable for compatibility
    echo "Warning: Fallback authentication method in use."
else
    echo "Error: No database password found in secrets or environment"
    exit 1
fi

# Construct DATABASE_URL
export DATABASE_URL="postgresql://${POSTGRES_USER}:${DB_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"

# Execute the main command
exec "$@"