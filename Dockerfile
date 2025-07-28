# Multi-stage build for smaller image
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r casino && useradd -r -g casino casino

WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/casino/.local

# Copy application code
COPY app ./app

# Create data directory with proper permissions
RUN mkdir -p /data && \
    echo "[]" > /data/users.json && \
    echo "[]" > /data/balance_history.json && \
    chown -R casino:casino /app /data

# Switch to non-root user
USER casino

# Add local bin to PATH
ENV PATH=/home/casino/.local/bin:$PATH
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/metrics')"

EXPOSE 5000

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app.app:app"]

