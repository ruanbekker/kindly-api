# kindly-api

**KindlyAPI** is a Flask-based API server designed to simplify the process of deploying, managing, and destroying Kubernetes clusters using [Kind](https://kind.sigs.k8s.io/). The API allows users to interact over the network to create clusters, retrieve kubeconfig files, and clean up clusters after testing, making it ideal for environments where temporary Kubernetes clusters are required.

### Features:

- **Deploy Kubernetes Clusters**: Easily deploy new Kind clusters with a single API call.
- **List Clusters**: View all running clusters managed by the API.
- **Retrieve Kubeconfig**: Fetch the kubeconfig for a specific cluster to manage it remotely.
- **Destroy Clusters**: Tear down clusters when they are no longer needed.

### Requirements:
- Docker
- Kind
- Python 3.11+
- Flask

---

## Endpoints

### 1. **List Clusters**
   - **GET** `/clusters`
   - Returns a list of active clusters.
   - **Example**:
     ```bash
     curl http://localhost:5000/clusters
     ```

### 2. **Deploy a Cluster**
   - **POST** `/clusters/deploy`
   - Deploys a new Kubernetes cluster using Kind.
   - **Example**:
     ```bash
     curl -X POST http://localhost:5000/clusters/deploy
     ```

### 3. **Retrieve Kubeconfig**
   - **GET** `/clusters/kubeconfig/<cluster-id>`
   - Fetches the kubeconfig for the specified cluster.
   - **Example**:
     ```bash
     curl -s http://localhost:5000/clusters/kubeconfig/kind-12345 | jq -r '.kubeconfig'
     ```

### 4. **Destroy a Cluster**
   - **DELETE** `/clusters/destroy/<cluster-id>`
   - Destroys the specified Kubernetes cluster.
   - **Example**:
     ```bash
     curl -X DELETE http://localhost:5000/clusters/destroy/kind-12345
     ```

---

## Getting Started

### 1. Clone the repository:
```bash
git clone https://github.com/ruanbekker/kindly-api.git
cd kindly-api
```

### 2. Set up Docker and Docker Compose:

Ensure you have Docker and Docker Compose installed and running.

### 3. Build and Run the Application:

```bash
docker-compose up --build
```

This will start the Flask API on port `5000`.

### 4. Interact with the API:

You can now interact with the API using the endpoints listed above. For example, deploy a new cluster:

```bash
curl -X POST http://localhost:5000/clusters/deploy
```

### 5. View Logs:

To view logs from the running containers, use:

```bash
docker-compose logs -f
```

---

## Configuration

- **NODE_IP_ADDRESS**: Set this environment variable in `docker-compose.yml` to match your host machine's IP address so that the kubeconfig files can be generated correctly for remote use.
- **DOCKER_HOST**: This is set to `/var/run/docker.sock` to communicate with the Docker daemon.

---

## License

This project is licensed under the MIT License.

