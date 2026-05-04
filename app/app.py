from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Flask en Kubernetes",
        "version": "1.0.0",
        "hostname": socket.gethostname()
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/about')
def about():
    return jsonify({
        "app": "Flask K8s Demo",
        "version": "1.0.0",
        "environment": os.getenv("APP_ENV", "development")
    })

if __name__ == '__main__':
    port = int(os.getenv("PORT", "5000"))
    app.run(host='0.0.0.0', port=port)