#!/bin/bash
# DR restore: verify checksums, reload image, restore config, redeploy
set -e
export PATH=$PATH:/usr/local/bin:/snap/bin
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BK="${1:?usage: restore.sh <backup-dir>}"; START=$(date +%s)
echo "[1/4] Verifying backup integrity"; ( cd "$BK" && sha256sum -c SHA256SUMS --quiet ) && echo "checksums OK"
echo "[2/4] Restoring image";  gunzip -c "$BK/app-image.tar.gz" | docker load
docker save sample-flask-app:1.0 | docker exec -i minikube ctr -n k8s.io images import -
echo "[3/4] Restoring config"; if [ -d "$BK/config" ]; then mkdir -p "$ROOT/docker-practice/config"; cp -r "$BK/config/." "$ROOT/docker-practice/config/"; fi
echo "[4/4] Redeploying";      kubectl apply -f "$BK/k8s/deployment.yaml"; kubectl rollout status deployment/flask-app-deployment --timeout=180s
echo "RECOVERY TIME (RTO): $(( $(date +%s) - START )) seconds"
