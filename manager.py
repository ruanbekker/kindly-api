from flask import Flask, jsonify

app = Flask(__name__)

# Main Flask Route
@app.route("/", methods=["GET"])
def root():
    return jsonify({"containers": "results"}), 200

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
