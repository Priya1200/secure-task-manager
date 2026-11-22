#!/bin/bash
# usage: switch.sh blue|green  -- moves live traffic after checking the target is ready
set -e
TARGET="${1:?usage: switch.sh blue|green}"; NS=bluegreen
echo "Checking $TARGET environment is ready..."
kubectl -n $NS rollout status deployment/flask-$TARGET --timeout=60s
echo "Switching live traffic to $TARGET"
kubectl -n $NS patch service flask-svc -p "{\"spec\":{\"selector\":{\"app\":\"flask\",\"version\":\"$TARGET\"}}}"
kubectl -n $NS get endpoints flask-svc
