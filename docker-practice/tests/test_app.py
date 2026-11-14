import json

import pytest

import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    flags_file = tmp_path / "flags.json"
    monkeypatch.setattr(app_module, "FLAGS_FILE", str(flags_file))
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client(), flags_file


def set_flags(path, **values):
    path.write_text(json.dumps(values))


def test_health_returns_ok(client):
    c, _ = client
    resp = c.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_greeting_is_old_when_flag_off(client):
    c, flags = client
    set_flags(flags, new_greeting=False)
    assert b"Hello from my containerized app!" in c.get("/").data


def test_greeting_is_new_when_flag_on(client):
    c, flags = client
    set_flags(flags, new_greeting=True)
    assert b"Welcome to the NEW Task Manager!" in c.get("/").data


def test_tasks_have_no_beta_banner_when_flag_off(client):
    c, flags = client
    set_flags(flags, beta_tasks=False)
    body = c.get("/tasks").data
    assert b"Write report" in body
    assert b"beta-banner" not in body


def test_tasks_show_beta_banner_when_flag_on(client):
    c, flags = client
    set_flags(flags, beta_tasks=True)
    body = c.get("/tasks").data
    assert b"beta-banner" in body
    assert b"priority" in body


def test_flags_endpoint_reports_current_values(client):
    c, flags = client
    set_flags(flags, new_greeting=True, beta_tasks=False)
    assert c.get("/flags").get_json() == {"new_greeting": True, "beta_tasks": False}


def test_missing_flag_file_falls_back_to_defaults(client):
    c, _ = client   # the flag file was never created
    assert c.get("/flags").get_json() == {"new_greeting": False, "beta_tasks": False}


def test_corrupt_flag_file_falls_back_to_defaults(client):
    c, flags = client
    flags.write_text("this is not json")
    assert c.get("/flags").get_json() == {"new_greeting": False, "beta_tasks": False}
