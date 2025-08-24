FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements-minimal.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Set environment variable for port
ENV PORT=5000

# Run the application
CMD ["python", "run.py"]
