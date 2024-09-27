import docker
from flask import Flask, jsonify, request

app = Flask(__name__)

# Initialize Docker client using the Docker host defined in the environment
client = docker.DockerClient(base_url=os.environ['DOCKER_HOST'])

# API: Test Docker via API
@app.route("/test-docker", methods=["GET"])
def test_docker():
    try:
        containers = client.containers.list()
        return jsonify({"containers": [c.name for c in containers]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

