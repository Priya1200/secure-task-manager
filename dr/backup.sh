#!/bin/bash
# DR backup: k8s state, config, Jenkins job config, app image (keeps last 3)
set -e
export PATH=$PATH:/usr/local/bin:/snap/bin
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BK="${BACKUP_DIR:-$HOME/backups}"; TS=$(date +%Y%m%d-%H%M%S); DEST="$BK/backup-$TS"
mkdir -p "$DEST"
echo "[1/4] Kubernetes live state";  kubectl get deployment flask-app-deployment -o yaml > "$DEST/deployment-live.yaml"
echo "[2/4] Config + manifests";     cp -r "$ROOT/k8s" "$DEST/k8s"; [ -d "$ROOT/docker-practice/config" ] && cp -r "$ROOT/docker-practice/config" "$DEST/config" || true
echo "[3/4] Jenkins job config";     sudo tar czf "$DEST/jenkins-config.tar.gz" -C /var/lib/jenkins config.xml jobs/secure-task-manager/config.xml; sudo chown "$USER" "$DEST/jenkins-config.tar.gz"
echo "[4/4] Application image";      docker save sample-flask-app:1.0 | gzip > "$DEST/app-image.tar.gz"
( cd "$DEST" && find . -type f ! -name SHA256SUMS -exec sha256sum {} + > SHA256SUMS )
ls -dt "$BK"/backup-* | tail -n +4 | xargs -r rm -rf
echo "BACKUP OK: $DEST"
