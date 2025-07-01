# Use Python 3.12 base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set proper permissions
RUN chmod -R 755 /app

# Create directories for static and media files
RUN mkdir -p /app/static /app/media

# Expose port 8000
EXPOSE 8000

# Define command to run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
