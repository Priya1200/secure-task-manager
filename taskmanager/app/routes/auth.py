import re
from functools import wraps

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ..models import User

bp = Blueprint("auth", __name__)

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,30}$")
MIN_PASSWORD, MAX_PASSWORD = 8, 128
# Checked when the username does not exist, so "unknown user" and "wrong password"
# take the same time and give the same message (no user discovery).
_DUMMY_HASH = generate_password_hash("dummy-password-for-timing")


@bp.before_app_request
def load_user():
    user_id = session.get("user_id")
    g.user = db.session.get(User, user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash("Please log in first.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        error = None
        if not USERNAME_RE.match(username):
            error = "Username must be 3-30 characters: letters, digits or underscore."
        elif not (MIN_PASSWORD <= len(password) <= MAX_PASSWORD):
            error = f"Password must be {MIN_PASSWORD}-{MAX_PASSWORD} characters."
        elif db.session.query(User).filter_by(username=username).first():
            error = "That username is already taken."
        if error:
            flash(error, "error")
            return render_template("register.html"), 400
        db.session.add(User(username=username, password_hash=generate_password_hash(password)))
        db.session.commit()
        flash("Account created. Please log in.", "ok")
        return redirect(url_for("auth.login"))
    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = db.session.query(User).filter_by(username=username).first()
        stored = user.password_hash if user else _DUMMY_HASH
        if check_password_hash(stored, password) and user:
            session.clear()                      # new session after login (prevents session fixation)
            session["user_id"] = user.id
            return redirect(url_for("tasks.list_tasks"))
        flash("Invalid username or password.", "error")
        return render_template("login.html"), 401
    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You are logged out.", "ok")
    return redirect(url_for("main.index"))
