# Multi-stage build for production
FROM python:3.12-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    build-essential \
    default-libmysqlclient-dev \
    python3-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r django \
    && useradd -r -g django django

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create directories and set permissions
RUN mkdir -p /app/static /app/media /app/staticfiles \
    && chown -R django:django /app

# Switch to non-root user
USER django

# Database Configuration Environment Variables
ENV DB_NAME=testcase_management
ENV DB_USER=root
ENV DB_PASSWORD=hXLujfuQ
ENV DB_HOST=mysql
ENV DB_PORT=3306
ENV DB_CHARSET=utf8mb4
ENV DB_CONN_MAX_AGE=600

# Django Production Configuration
ENV DEBUG=False
ENV SECRET_KEY=change-this-in-production
ENV ALLOWED_HOSTS=localhost,127.0.0.1,.clackypaas.com

# Expose port 8000
EXPOSE 8000

# Collect static files
RUN python manage.py collectstatic --noinput

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/accounts/login/ || exit 1

# Use gunicorn for production
CMD ["sh", "-c", "python scripts/wait-for-db.py && python manage.py migrate && gunicorn testcase_management.wsgi:application --bind 0.0.0.0:8000 --workers 4"]
