"""Integration tests: run against the BUILT container over HTTP (not the Flask test client).
They follow a real user: register, log in, manage tasks, and try things a user must NOT be able to do."""
import os
import re
import time

import pytest
import requests

BASE = os.environ.get("BASE_URL", "http://localhost:5000")


@pytest.fixture(scope="session", autouse=True)
def wait_for_app():
    for _ in range(30):
        try:
            if requests.get(BASE + "/health", timeout=2).status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(1)
    pytest.fail("app did not start in 30s")


def csrf_token(session, path):
    """Forms contain a hidden CSRF token; a real browser sends it back, so do we."""
    html = session.get(BASE + path).text
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


def register_and_login(username, password="correct-horse-1"):
    s = requests.Session()
    s.post(BASE + "/register", data={"username": username, "password": password,
                                     "csrf_token": csrf_token(s, "/register")})
    r = s.post(BASE + "/login", data={"username": username, "password": password,
                                      "csrf_token": csrf_token(s, "/login")}, allow_redirects=False)
    assert r.status_code == 302
    return s


def unique(prefix):
    return f"{prefix}_{int(time.time() * 1000) % 10**9}"


def test_health_ok():
    r = requests.get(BASE + "/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_security_headers_present():
    h = requests.get(BASE + "/").headers
    assert h["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in h["Content-Security-Policy"]
    assert h["X-Content-Type-Options"] == "nosniff"


def test_tasks_require_login():
    r = requests.get(BASE + "/tasks", allow_redirects=False)
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_post_without_csrf_token_is_rejected():
    r = requests.post(BASE + "/register", data={"username": unique("nocsrf"), "password": "correct-horse-1"})
    assert r.status_code == 400


def test_wrong_password_is_rejected():
    name = unique("wrongpw")
    register_and_login(name)
    s = requests.Session()
    r = s.post(BASE + "/login", data={"username": name, "password": "not-the-password",
                                      "csrf_token": csrf_token(s, "/login")})
    assert r.status_code == 401


def test_full_user_journey():
    s = register_and_login(unique("journey"))
    s.post(BASE + "/tasks", data={"title": "Write report", "description": "chapter 1",
                                  "csrf_token": csrf_token(s, "/tasks")})
    page = s.get(BASE + "/tasks").text
    assert "Write report" in page and "chapter 1" in page


def test_users_cannot_see_each_others_tasks():
    a = register_and_login(unique("alice"))
    b = register_and_login(unique("bob"))
    a.post(BASE + "/tasks", data={"title": "alice-private-task", "csrf_token": csrf_token(a, "/tasks")})
    assert "alice-private-task" in a.get(BASE + "/tasks").text
    assert "alice-private-task" not in b.get(BASE + "/tasks").text


def test_script_in_task_title_is_not_executed():
    s = register_and_login(unique("xss"))
    s.post(BASE + "/tasks", data={"title": "<script>alert(1)</script>", "csrf_token": csrf_token(s, "/tasks")})
    page = s.get(BASE + "/tasks").text
    assert "<script>alert(1)</script>" not in page and "&lt;script&gt;" in page


def test_unknown_route_returns_404():
    assert requests.get(BASE + "/does-not-exist").status_code == 404
