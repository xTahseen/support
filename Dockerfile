# Use an official lightweight Python image
FROM python:3.10-slim-buster

# Set working directory
WORKDIR /app

# Install system dependencies (optional, if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot source code
COPY . .

# Set default command
CMD ["python3", "-m", "app"]
