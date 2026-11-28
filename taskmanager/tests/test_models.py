import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Task, User


def make_user(name="priya"):
    u = User(username=name, password_hash="not-a-real-hash")
    db.session.add(u)
    db.session.commit()
    return u


def test_user_can_own_tasks(app):
    with app.app_context():
        u = make_user()
        db.session.add(Task(title="Write report", user_id=u.id))
        db.session.commit()
        assert len(u.tasks) == 1
        assert u.tasks[0].owner.username == "priya"


def test_task_defaults(app):
    with app.app_context():
        u = make_user()
        t = Task(title="Review code", user_id=u.id)
        db.session.add(t)
        db.session.commit()
        assert t.done is False
        assert t.description == ""
        assert t.created_at is not None


def test_username_must_be_unique(app):
    with app.app_context():
        make_user("priya")
        db.session.add(User(username="priya", password_hash="x"))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_deleting_user_deletes_their_tasks(app):
    with app.app_context():
        u = make_user()
        db.session.add(Task(title="t1", user_id=u.id))
        db.session.commit()
        db.session.delete(u)
        db.session.commit()
        assert db.session.query(Task).count() == 0
