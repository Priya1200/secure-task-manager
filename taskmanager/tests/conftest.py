import pytest

from app import create_app
from app.extensions import db
from app.config import TestConfig


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()   # close the SQLite connection cleanly


@pytest.fixture
def client(app):
    return app.test_client()


def register(client, username="priya", password="correct-horse-1"):
    return client.post("/register", data={"username": username, "password": password})


def login(client, username="priya", password="correct-horse-1"):
    return client.post("/login", data={"username": username, "password": password})


@pytest.fixture
def logged_in(client):
    register(client)
    login(client)
    return client
