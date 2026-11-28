from app.extensions import db
from app.models import Task
from conftest import login, register


def test_create_and_list_task(logged_in):
    logged_in.post("/tasks", data={"title": "Write report", "description": "chapter 1"})
    body = logged_in.get("/tasks").data
    assert b"Write report" in body and b"chapter 1" in body


def test_empty_and_too_long_titles_are_rejected(logged_in, app):
    logged_in.post("/tasks", data={"title": "   "})
    logged_in.post("/tasks", data={"title": "x" * 101})
    with app.app_context():
        assert db.session.query(Task).count() == 0


def test_too_long_description_is_rejected(logged_in, app):
    logged_in.post("/tasks", data={"title": "ok", "description": "d" * 501})
    with app.app_context():
        assert db.session.query(Task).count() == 0


def test_toggle_marks_task_done_and_back(logged_in, app):
    logged_in.post("/tasks", data={"title": "t1"})
    with app.app_context():
        task_id = db.session.query(Task).one().id
    logged_in.post(f"/tasks/{task_id}/toggle")
    with app.app_context():
        assert db.session.get(Task, task_id).done is True
    logged_in.post(f"/tasks/{task_id}/toggle")
    with app.app_context():
        assert db.session.get(Task, task_id).done is False


def test_delete_removes_task(logged_in, app):
    logged_in.post("/tasks", data={"title": "t1"})
    with app.app_context():
        task_id = db.session.query(Task).one().id
    logged_in.post(f"/tasks/{task_id}/delete")
    with app.app_context():
        assert db.session.query(Task).count() == 0


def test_user_only_sees_own_tasks(app):
    a, b = app.test_client(), app.test_client()
    register(a, "alice_a"); login(a, "alice_a")
    register(b, "bob_b");   login(b, "bob_b")
    a.post("/tasks", data={"title": "alice-secret-task"})
    assert b"alice-secret-task" in a.get("/tasks").data
    assert b"alice-secret-task" not in b.get("/tasks").data


def test_user_cannot_toggle_or_delete_someone_elses_task(app):
    a, b = app.test_client(), app.test_client()
    register(a, "alice_a"); login(a, "alice_a")
    register(b, "bob_b");   login(b, "bob_b")
    a.post("/tasks", data={"title": "alice-task"})
    with app.app_context():
        task_id = db.session.query(Task).one().id
    assert b.post(f"/tasks/{task_id}/toggle").status_code == 404
    assert b.post(f"/tasks/{task_id}/delete").status_code == 404
    with app.app_context():
        assert db.session.get(Task, task_id) is not None


def test_html_in_task_title_is_escaped(logged_in):
    logged_in.post("/tasks", data={"title": "<script>alert(1)</script>"})
    body = logged_in.get("/tasks").data
    assert b"<script>alert(1)</script>" not in body
    assert b"&lt;script&gt;" in body


def test_missing_task_gives_404(logged_in):
    assert logged_in.post("/tasks/9999/delete").status_code == 404
