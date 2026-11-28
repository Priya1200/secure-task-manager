from app.extensions import db
from app.models import User
from conftest import login, register


def test_register_creates_user_and_redirects_to_login(client, app):
    resp = register(client)
    assert resp.status_code == 302 and "/login" in resp.headers["Location"]
    with app.app_context():
        assert db.session.query(User).filter_by(username="priya").count() == 1


def test_password_is_stored_hashed_not_plain(client, app):
    register(client, password="correct-horse-1")
    with app.app_context():
        user = db.session.query(User).filter_by(username="priya").first()
        assert "correct-horse-1" not in user.password_hash
        assert user.password_hash.startswith(("scrypt:", "pbkdf2:"))


def test_duplicate_username_is_rejected(client):
    register(client)
    resp = register(client)
    assert resp.status_code == 400
    assert b"already taken" in resp.data


def test_bad_username_is_rejected(client):
    for bad in ["ab", "has space", "semi;colon", "<script>", "x" * 31]:
        assert register(client, username=bad).status_code == 400


def test_short_and_huge_passwords_are_rejected(client):
    assert register(client, password="short").status_code == 400
    assert register(client, password="x" * 129).status_code == 400


def test_login_success_sets_session_and_opens_tasks(client):
    register(client)
    resp = login(client)
    assert resp.status_code == 302 and "/tasks" in resp.headers["Location"]
    assert client.get("/tasks").status_code == 200


def test_wrong_password_and_unknown_user_give_same_message(client):
    register(client)
    wrong_pw = login(client, password="wrong-password-1")
    unknown = login(client, username="nobody")
    assert wrong_pw.status_code == unknown.status_code == 401
    assert b"Invalid username or password." in wrong_pw.data
    assert b"Invalid username or password." in unknown.data


def test_sql_injection_string_does_not_log_in(client):
    register(client)
    resp = login(client, username="priya' OR '1'='1", password="x")
    assert resp.status_code == 401


def test_logout_ends_the_session(logged_in):
    resp = logged_in.post("/logout")
    assert resp.status_code == 302
    assert logged_in.get("/tasks").status_code == 302   # sent back to login


def test_tasks_page_requires_login(client):
    resp = client.get("/tasks")
    assert resp.status_code == 302 and "/login" in resp.headers["Location"]
