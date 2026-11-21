import os, time, requests, pytest
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

def test_health_ok():
    r = requests.get(BASE + "/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"

def test_home_page_renders():
    r = requests.get(BASE + "/")
    assert r.status_code == 200 and "greeting" in r.text

def test_tasks_page_lists_three_tasks():
    r = requests.get(BASE + "/tasks")
    assert r.status_code == 200 and r.text.count("<li") == 3

def test_flags_endpoint_has_default_flags():
    data = requests.get(BASE + "/flags").json()
    assert "new_greeting" in data and "beta_tasks" in data

def test_unknown_route_returns_404():
    assert requests.get(BASE + "/does-not-exist").status_code == 404
