#!/bin/bash
# DevSecOps security gate for the Task Manager app: exits 1 if any scan finds a problem
FAIL=0
APP="$(cd "$(dirname "$0")/.." && pwd)"     # the taskmanager folder

echo "=== 1/4 Dependency scan (pip-audit) ==="
docker run --rm -v "$APP":/src:ro -w /src python:3.11-slim sh -c "pip install -q pip-audit 2>/dev/null && pip-audit -r requirements.txt" || FAIL=1

echo "=== 2/4 Static code analysis (Bandit) ==="
docker run --rm -v "$APP":/src:ro -w /src python:3.11-slim sh -c "pip install -q bandit 2>/dev/null && bandit -q -r app wsgi.py" || FAIL=1

echo "=== 3/4 Secret scan (Gitleaks) ==="
docker run --rm -v "$APP":/repo:ro zricethezav/gitleaks:latest detect --no-git --source /repo --config /repo/.gitleaks.toml || FAIL=1

echo "=== 4/4 Container image scan (Trivy) ==="
docker build -q -t taskmanager:secure "$APP" > /dev/null && \
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache/ aquasec/trivy:latest image --quiet --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 taskmanager:secure || FAIL=1

if [ $FAIL -eq 0 ]; then echo "SECURITY GATE: PASSED"; else echo "SECURITY GATE: FAILED"; fi
exit $FAIL
