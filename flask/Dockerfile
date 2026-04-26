# Use the official slim Python image (smaller = faster)
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first (Docker caches this layer then speeds up rebuilds)
COPY requirements.txt .

# Installs Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the Flask app
COPY app/ .

# Expose port 5000 so docker-compose can map it to your machine
EXPOSE 5000

# Start the app with gunicorn
# 'app:app' means: the file app.py, the Flask instance named app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
