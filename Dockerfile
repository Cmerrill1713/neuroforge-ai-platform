# Multi-stage Dockerfile for AI Assistant Platform
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY knowledge_base/ ./knowledge_base/
COPY *.py ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8004

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8004/api/system/health || exit 1

# Start command
CMD ["python", "-m", "uvicorn", "src.api.consolidated_api_architecture:create_consolidated_app", "--host", "0.0.0.0", "--port", "8004"]
