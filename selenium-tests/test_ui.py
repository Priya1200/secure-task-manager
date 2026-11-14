import json
import os
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

BASE = os.environ.get("BASE_URL", "http://app:5000")
FLAGS = os.environ.get("FLAGS_PATH", "/config/flags.json")
OUT = "shots"
results = []


def make_driver():
    opts = Options()
    opts.binary_location = "/usr/bin/chromium"
    for arg in ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
                "--disable-gpu", "--window-size=1000,400"]:
        opts.add_argument(arg)
    return webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=opts)


def set_flags(**values):
    with open(FLAGS, "w") as f:
        json.dump(values, f)


def check(name, condition):
    print(("PASS  " if condition else "FAIL  ") + name)
    results.append(bool(condition))


driver = make_driver()
try:
    set_flags(new_greeting=False, beta_tasks=False)
    driver.get(BASE + "/")
    text = driver.find_element(By.ID, "greeting").text
    check("Home page shows the OLD greeting when new_greeting is OFF", "Hello from my containerized app!" in text)
    driver.save_screenshot(OUT + "/01_new_greeting_OFF.png")

    set_flags(new_greeting=True, beta_tasks=False)
    driver.get(BASE + "/")
    text = driver.find_element(By.ID, "greeting").text
    check("Home page shows the NEW greeting when new_greeting is ON", "Welcome to the NEW Task Manager!" in text)
    driver.save_screenshot(OUT + "/02_new_greeting_ON.png")

    set_flags(new_greeting=False, beta_tasks=False)
    driver.get(BASE + "/tasks")
    check("Tasks page lists 3 tasks", len(driver.find_elements(By.CSS_SELECTOR, "#task-list li")) == 3)
    check("No beta banner when beta_tasks is OFF", len(driver.find_elements(By.ID, "beta-banner")) == 0)
    driver.save_screenshot(OUT + "/03_beta_tasks_OFF.png")

    set_flags(new_greeting=False, beta_tasks=True)
    driver.get(BASE + "/tasks")
    check("Beta banner is visible when beta_tasks is ON", driver.find_element(By.ID, "beta-banner").is_displayed())
    driver.save_screenshot(OUT + "/04_beta_tasks_ON.png")

    driver.get(BASE + "/health")
    body = driver.find_element(By.TAG_NAME, "body").text.replace(" ", "")
    check("Health endpoint returns status ok", '"status":"ok"' in body)
finally:
    driver.quit()
    set_flags(new_greeting=False, beta_tasks=False)

print("\n%d/%d checks passed" % (sum(results), len(results)))
sys.exit(0 if all(results) else 1)
