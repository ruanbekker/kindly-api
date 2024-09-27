# Base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy dependencies file
COPY requirements.txt /src/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /src/requirements.txt

# Copy the current directory contents into the container at /app
COPY manager.py /app/manager.py

# Expose Flask app port
EXPOSE 5000

# Start the Flask app
CMD ["python", "manager.py"]

