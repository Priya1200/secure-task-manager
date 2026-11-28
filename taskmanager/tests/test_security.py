import re

from app import create_app
from app.config import TestConfig


def test_security_headers_are_set(client):
    h = client.get("/").headers
    assert h["X-Content-Type-Options"] == "nosniff"
    assert h["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in h["Content-Security-Policy"]
    assert h["Referrer-Policy"] == "no-referrer"


def test_session_cookie_flags(app, client):
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


def test_csrf_blocks_post_without_token():
    class WithCsrf(TestConfig):
        WTF_CSRF_ENABLED = True

    client = create_app(WithCsrf).test_client()
    resp = client.post("/register", data={"username": "priya", "password": "correct-horse-1"})
    assert resp.status_code == 400            # rejected: no CSRF token


def test_csrf_allows_post_with_valid_token():
    class WithCsrf(TestConfig):
        WTF_CSRF_ENABLED = True

    client = create_app(WithCsrf).test_client()
    page = client.get("/register").get_data(as_text=True)
    token = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)
    resp = client.post("/register", data={"username": "priya", "password": "correct-horse-1", "csrf_token": token})
    assert resp.status_code == 302


def test_oversized_request_is_rejected(client):
    resp = client.post("/register", data={"username": "a" * 20000, "password": "b"})
    assert resp.status_code == 413
