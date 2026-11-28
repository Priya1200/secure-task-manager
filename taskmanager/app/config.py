import os


class Config:
    """Settings come from environment variables, never from hard-coded values."""
    SECRET_KEY = os.environ.get("SECRET_KEY")          # required: no default on purpose
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///taskmanager.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Session cookie hardening
    SESSION_COOKIE_HTTPONLY = True                     # JavaScript cannot read the cookie
    SESSION_COOKIE_SAMESITE = "Lax"                    # not sent on cross-site POSTs
    SESSION_COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "0") == "1"   # set 1 when served over HTTPS
    MAX_CONTENT_LENGTH = 16 * 1024                     # reject huge requests


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-only-not-a-real-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False                           # turned on in the CSRF test
