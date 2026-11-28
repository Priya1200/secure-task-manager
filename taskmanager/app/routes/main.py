from flask import Blueprint, jsonify, render_template

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/health")
def health():
    """Used by Docker, Kubernetes probes and the pipeline's integration tests."""
    return jsonify(status="ok")
