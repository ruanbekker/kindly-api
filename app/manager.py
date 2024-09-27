import subprocess
import os
import re
import random
import string
import docker
from flask import Flask, jsonify, request

app = Flask(__name__)

# Initialize Docker client using the Docker host defined in the environment
client = docker.DockerClient(base_url=os.environ['DOCKER_HOST'])

# In-memory storage for clusters
# TODO: use redis or something similar
clusters = {}

# Base directory to store kubeconfig files
KUBECONFIG_DIR = "/tmp/kubeconfigs"
if not os.path.exists(KUBECONFIG_DIR):
    os.makedirs(KUBECONFIG_DIR)

# Function: Generate a cluster name
def generate_cluster_name():
    return "kind-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

# Function: Check if a port is available
def is_port_available(port):
    with subprocess.Popen(f"netstat -an | grep {port}", shell=True, stdout=subprocess.PIPE) as proc:
        output = proc.stdout.read()
    return len(output.strip()) == 0

# Function: Find an available port within defined range
def find_available_port():
    while True:
        port = random.randint(45000, 45010)
        if is_port_available(port):
            return port

# API: Test docker
@app.route("/test-docker", methods=["GET"])
def test_docker():
    try:
        containers = client.containers.list()
        return jsonify({"containers": [c.name for c in containers]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Function: Deploy a cluster
def deploy_cluster(cluster_name, host_port):
    node_ip_address = os.environ['NODE_IP_ADDRESS']
    kind_config = f"""
---
# https://kind.sigs.k8s.io/docs/user/configuration
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
networking:
  # WARNING: It is _strongly_ recommended that you keep this the default
  # (127.0.0.1) for security reasons. However it is possible to change this.
  apiServerAddress: "0.0.0.0"
  # By default the API server listens on a random open port.
  # You may choose a specific port but probably don't need to in most cases.
  # Using a random port makes it easier to spin up multiple clusters.
  apiServerPort: {host_port}
nodes:
  - role: control-plane
kubeadmConfigPatchesJSON6902:
  - group: kubeadm.k8s.io
    version: v1beta3
    kind: ClusterConfiguration
    patch: |
      - op: add
        path: /apiServer/certSANs/-
        value: {node_ip_address}
"""
    kind_config_file = f"{KUBECONFIG_DIR}/{cluster_name}-kindconfig.yaml"

    # Write the config file
    with open(kind_config_file, "w") as f:
        f.write(kind_config)

    # Create the cluster
    subprocess.run(["kind", "create", "cluster", "--name", cluster_name, "--config", kind_config_file])

    # Update kubeconfig
    kubeconfig_file = f"{KUBECONFIG_DIR}/{cluster_name}-config.yaml"

    result = subprocess.run(
        ["kind", "get", "kubeconfig", "--name", cluster_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Check for errors
    if result.returncode != 0:
        print(f"Error retrieving kubeconfig: {result.stderr}")
        return False

    # Write the output to the kubeconfig file
    with open(kubeconfig_file, "w") as f:
        f.write(result.stdout)

    # Substitute 0.0.0.0 with Node IP
    external_ip = os.environ['NODE_IP_ADDRESS']
    with open(kubeconfig_file, "r") as f:
        kubeconfig_data = f.read().replace("0.0.0.0", external_ip)
        kubeconfig_data = re.sub(r":\d+", f":{host_port}", kubeconfig_data)

    with open(kubeconfig_file, "w") as f:
        f.write(kubeconfig_data)

    # Save cluster details
    clusters[cluster_name] = {
        "name": cluster_name,
        "host_port": host_port,
        "kubeconfig": kubeconfig_file,
        "kindconfig": kind_config_file
    }

    return cluster_name

# Function: Destroy a cluster
def destroy_cluster(cluster_name):
    subprocess.run(["kind", "delete", "cluster", "--name", cluster_name])
    if cluster_name in clusters:
        del clusters[cluster_name]

# API: Deploy a cluster
@app.route("/clusters/deploy", methods=["POST"])
def deploy():
    cluster_name = generate_cluster_name()
    host_port = find_available_port()
    deploy_cluster(cluster_name, host_port)
    return jsonify({"message": "Cluster deployed", "cluster_name": cluster_name, "port": host_port}), 201

# API: Destroy a cluster
@app.route("/clusters/destroy/<cluster_name>", methods=["DELETE"])
def destroy(cluster_name):
    if cluster_name in clusters:
        destroy_cluster(cluster_name)
        return jsonify({"message": f"Cluster {cluster_name} destroyed"}), 200
    else:
        return jsonify({"error": "Cluster not found"}), 404

# API: List clusters
@app.route("/clusters", methods=["GET"])
def list_clusters():
    return jsonify(clusters), 200

# API: Get kubeconfig for a cluster
@app.route("/clusters/kubeconfig/<cluster_name>", methods=["GET"])
def get_kubeconfig(cluster_name):
    if cluster_name in clusters:
        kubeconfig_path = clusters[cluster_name]["kubeconfig"]
        with open(kubeconfig_path, "r") as f:
            kubeconfig = f.read()
        return jsonify({"kubeconfig": kubeconfig}), 200
    else:
        return jsonify({"error": "Cluster not found"}), 404

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

