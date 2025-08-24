FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml ./
RUN pip install -e .

# Copy source code
COPY src/ ./src/
COPY .env.example ./.env

# Expose port
EXPOSE 8055

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8055/health || exit 1

# Run server
CMD ["python", "src/main.py"]
