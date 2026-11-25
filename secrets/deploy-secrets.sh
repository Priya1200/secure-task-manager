#!/usr/bin/env bash
# Vault se secret padhta hai aur Kubernetes Secret bana deta hai.
# Secret ki value kabhi print nahi hoti, na git me jaati hai.
set -euo pipefail
: "${VAULT_ADDR:?VAULT_ADDR set karo}"
: "${VAULT_TOKEN:?VAULT_TOKEN set karo (limited token)}"
NS="${NS:-secrets-demo}"

JSON=$(curl -sf -H "X-Vault-Token: ${VAULT_TOKEN}" "${VAULT_ADDR}/v1/secret/data/taskmanager")
DB=$(echo "$JSON" | python3 -c 'import sys,json;print(json.load(sys.stdin)["data"]["data"]["db_password"])')
KEY=$(echo "$JSON" | python3 -c 'import sys,json;print(json.load(sys.stdin)["data"]["data"]["api_key"])')
VER=$(echo "$JSON" | python3 -c 'import sys,json;print(json.load(sys.stdin)["data"]["metadata"]["version"])')

kubectl create namespace "$NS" --dry-run=client -o yaml | kubectl apply -f -
# --from-env-file: values argv me nahi aati (ps se chhupi rehti hain)
kubectl -n "$NS" create secret generic taskmanager-secrets \
  --from-env-file=<(printf 'db_password=%s\napi_key=%s\n' "$DB" "$KEY") \
  --dry-run=client -o yaml | kubectl apply -f -
echo "OK: Vault secret (version ${VER}) -> K8s Secret taskmanager-secrets [values hidden]"
