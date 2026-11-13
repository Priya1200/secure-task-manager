#!/bin/bash
# DevSecOps security gate: exits 1 if any scan finds a problem
FAIL=0
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="$ROOT/docker-practice"

echo "=== 1/4 Dependency scan (pip-audit) ==="
docker run --rm -v "$APP":/src -w /src python:3.11-slim sh -c "pip install -q pip-audit 2>/dev/null && pip-audit -r requirements.txt" || FAIL=1

echo "=== 2/4 Static code analysis (Bandit) ==="
docker run --rm -v "$APP":/src -w /src python:3.11-slim sh -c "pip install -q bandit 2>/dev/null && bandit -q -r app.py" || FAIL=1

echo "=== 3/4 Secret scan (Gitleaks) ==="
docker run --rm -v "$ROOT":/repo zricethezav/gitleaks:latest detect --no-git --source /repo || FAIL=1

echo "=== 4/4 Container image scan (Trivy) ==="
docker build -q -t sample-flask-app:secure "$APP" > /dev/null && \
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache/ aquasec/trivy:latest image --quiet --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 sample-flask-app:secure || FAIL=1

if [ $FAIL -eq 0 ]; then echo "SECURITY GATE: PASSED"; else echo "SECURITY GATE: FAILED"; fi
exit $FAIL
