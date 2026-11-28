from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from ..extensions import db
from ..models import Task
from .auth import login_required

bp = Blueprint("tasks", __name__)


def _own_task_or_404(task_id):
    """A user can only touch their own tasks. Someone else's task looks like it does not exist."""
    task = db.session.get(Task, task_id)
    if task is None or task.user_id != g.user.id:
        abort(404)
    return task


@bp.route("/tasks", methods=["GET"])
@login_required
def list_tasks():
    tasks = (db.session.query(Task).filter_by(user_id=g.user.id)
             .order_by(Task.created_at.desc(), Task.id.desc()).all())
    return render_template("tasks.html", tasks=tasks)


@bp.route("/tasks", methods=["POST"])
@login_required
def create_task():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    if not 1 <= len(title) <= 100:
        flash("Title is required (1-100 characters).", "error")
    elif len(description) > 500:
        flash("Description can be at most 500 characters.", "error")
    else:
        db.session.add(Task(title=title, description=description, user_id=g.user.id))
        db.session.commit()
        flash("Task added.", "ok")
    return redirect(url_for("tasks.list_tasks"))


@bp.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    task = _own_task_or_404(task_id)
    task.done = not task.done
    db.session.commit()
    return redirect(url_for("tasks.list_tasks"))


@bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = _own_task_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted.", "ok")
    return redirect(url_for("tasks.list_tasks"))
