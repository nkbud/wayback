# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml .
COPY src ./src

# Set version for setuptools-scm since .git directory is not available in Docker build
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_WAYBACK=0.1.0

# Install Python dependencies
RUN pip install --no-cache-dir -e .[mcp]

# Expose the default MCP server port
EXPOSE 8000

# Create a non-root user
RUN useradd --create-home --shell /bin/bash mcp_user
USER mcp_user

# Set environment variables
ENV PYTHONPATH=/app/src
ENV MCP_SERVER_HOST=0.0.0.0
ENV MCP_SERVER_PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Run the MCP server
CMD ["python", "-m", "wayback.mcp_server.server"]