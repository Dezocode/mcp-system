FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for TypeScript templates
RUN apt-get update && apt-get install -y nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY bin/ ./bin/
COPY pyproject.toml .

# Install the package
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app
USER mcpuser

# Set up MCP system directories
RUN mkdir -p /home/mcpuser/.mcp-system/{components,docs,templates,backups,logs} && \
    mkdir -p /home/mcpuser/bin

# Set environment variables
ENV PATH="/home/mcpuser/bin:$PATH"
ENV MCP_SYSTEM_PATH="/home/mcpuser/.mcp-system"
ENV MCP_AUTO_DISCOVERY=true
ENV MCP_SAFE_MODE=true

# Install MCP system
RUN chmod +x bin/install.sh && ./bin/install.sh

# Default command
CMD ["mcp-universal", "--help"]

# Labels
LABEL org.opencontainers.image.title="MCP System"
LABEL org.opencontainers.image.description="Universal MCP server management system"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="DezoCode"
LABEL org.opencontainers.image.source="https://github.com/dezocode/mcp-system"