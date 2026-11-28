from flask import Flask

from .config import Config
from .extensions import csrf, db


def create_app(config_class=Config):
    """Application factory: builds a fresh app, so tests can use their own settings."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY is not set. Provide it as an environment variable.")

    db.init_app(app)
    csrf.init_app(app)

    from .routes import auth, main, tasks
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(tasks.bp)

    from . import models  # noqa: F401  (registers the tables)
    with app.app_context():
        db.create_all()

    @app.after_request
    def security_headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        return resp

    return app
