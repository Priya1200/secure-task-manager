import pytest

from app import create_app
from app.config import Config


def test_health_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_home_page_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Secure Task Manager" in resp.data


def test_unknown_page_gives_404(client):
    assert client.get("/does-not-exist").status_code == 404


def test_app_refuses_to_start_without_secret_key(monkeypatch):
    class NoKey(Config):
        SECRET_KEY = None
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    with pytest.raises(RuntimeError):
        create_app(NoKey)
