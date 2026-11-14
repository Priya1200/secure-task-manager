import json
import os

from flask import Flask, jsonify

app = Flask(__name__)

FLAGS_FILE = os.environ.get("FLAGS_FILE", "config/flags.json")
DEFAULT_FLAGS = {"new_greeting": False, "beta_tasks": False}


def load_flags():
    """Read the flag file on every request, so a flag can change without a restart."""
    try:
        with open(FLAGS_FILE) as f:
            return {**DEFAULT_FLAGS, **json.load(f)}
    except (OSError, ValueError):
        return dict(DEFAULT_FLAGS)


@app.route('/')
def hello():
    if load_flags()["new_greeting"]:
        return "<h1 id='greeting'>Welcome to the NEW Task Manager!</h1>"
    return "<h1 id='greeting'>Hello from my containerized app!</h1>"


@app.route('/tasks')
def tasks():
    items = ["Write report", "Review code", "Deploy app"]
    beta = load_flags()["beta_tasks"]
    html = "<h1>Tasks</h1><ul id='task-list'>"
    for i, t in enumerate(items):
        suffix = " - priority" if beta and i == 0 else ""
        html += "<li>" + t + suffix + "</li>"
    html += "</ul>"
    if beta:
        html += "<p id='beta-banner'>BETA: priority tasks enabled</p>"
    return html


@app.route('/health')
def health():
    return jsonify(status="ok")


@app.route('/flags')
def flags():
    return jsonify(load_flags())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # nosec B104 - container must listen on all interfaces
