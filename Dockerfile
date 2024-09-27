# Base image
FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    bash \
    net-tools \
    && apt-get clean

# Install Docker CLI to communicate with dind
RUN curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh

# Install kind
RUN curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64 \
    && chmod +x ./kind && mv ./kind /usr/local/bin/kind

# Install kubectl
RUN curl -LO https://dl.k8s.io/release/v1.31.0/bin/linux/amd64/kubectl \
    && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Set the working directory
WORKDIR /app

# Copy dependencies file
COPY app/requirements.txt /src/requirements.txt

# Install python dependencies
RUN pip install --no-cache-dir -r /src/requirements.txt

# Copy the current directory contents into the container at /app
COPY app/manager.py /app/manager.py

# Expose flask app port for docs
EXPOSE 5000

# Use bridge network in docker
ENV KIND_EXPERIMENTAL_DOCKER_NETWORK=bridge

# Start the flask app
CMD ["python", "manager.py"]
