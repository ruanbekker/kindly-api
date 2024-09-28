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

ARG DOCKER_VERSION=23.0.1
ARG KIND_VERSION=0.20.0
ARG KUBECTL_VERSION=1.31.0

ENV DOCKER_VERSION=$DOCKER_VERSION
ENV KIND_VERSION=$KIND_VERSION
ENV KUBECTL_VERSION=$KUBECTL_VERSION

# Install Docker CLI to communicate with dind
COPY --from=docker:23.0.1-dind /usr/local/bin/docker /usr/local/bin/docker

# Install kind
RUN curl -Lo ./kind https://kind.sigs.k8s.io/dl/v$KIND_VERSION/kind-linux-amd64 \
    && install -o root -g root -m 0755 kind /usr/local/bin/kind

# Install kubectl
RUN curl -LO https://dl.k8s.io/release/v$KUBECTL_VERSION/bin/linux/amd64/kubectl \
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

# Start the flask app
CMD ["python", "manager.py"]
