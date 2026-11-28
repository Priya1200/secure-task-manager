#!/usr/bin/env bash
# Canary rollout with automatic analysis and rollback.
# Usage: bash canary/analysis/rollout.sh <new_version> <error_rate_percent> <latency_ms>
set -uo pipefail
NS=canary
VER=${1:?new version, e.g. v2}; ERR=${2:?error rate %}; LAT=${3:?latency ms}
MAX_ERR=5          # rollback trigger 1: canary error rate above 5 %
LAT_FACTOR=3       # rollback trigger 2: canary latency above 3x stable (and above 50 ms)
REQS=120           # requests per analysis step
STEPS="1 3"        # canary pods (stable stays at 3): 25 % then 50 %
START=$SECONDS

measure() {   # prints: version requests errors error% avg_ms
  kubectl -n $NS delete pod loadgen --ignore-not-found --wait=true >/dev/null 2>&1
  kubectl -n $NS run loadgen --image=curlimages/curl --image-pull-policy=IfNotPresent \
    --restart=Never --command -- sh -c "for i in \$(seq 1 $REQS); do curl -s -w ' %{http_code} %{time_total}\n' http://app-svc; done" >/dev/null
  kubectl -n $NS wait --for=jsonpath='{.status.phase}'=Succeeded pod/loadgen --timeout=180s >/dev/null
  kubectl -n $NS logs loadgen | awk '$3!=""{n[$2]++; if($3!="200")e[$2]++; t[$2]+=$4}
    END{for(v in n) printf "%s %d %d %.1f %.1f\n", v, n[v], e[v]+0, 100*(e[v]+0)/n[v], 1000*t[v]/n[v]}' | sort
}
show() { awk '{printf "    %-4s requests=%-4s errors=%-4s error_rate=%5s%%  avg_latency=%6s ms\n",$1,$2,$3,$4,$5}'; }
rollback() {
  kubectl -n $NS scale deploy/app-canary --replicas=0 >/dev/null
  echo "  >>> ROLLBACK TRIGGERED: $1"
  echo "  >>> canary scaled to 0 pods after $((SECONDS-START)) s"
  sleep 5
  echo "--- Traffic after rollback ---"; measure | show
}

STABLE_V=$(kubectl -n $NS get deploy app-stable -o jsonpath='{.spec.template.spec.containers[0].env[?(@.name=="VERSION")].value}')
RATE=$(awk -v e=$ERR 'BEGIN{print e/100}')
echo "=== Canary rollout: stable=$STABLE_V  new=$VER (error_rate=${ERR}%, latency=${LAT}ms) ==="
echo "    Triggers: error rate > ${MAX_ERR}%  OR  latency > ${LAT_FACTOR}x stable"
kubectl -n $NS set env deploy/app-canary VERSION=$VER ERROR_RATE=$RATE LATENCY_MS=$LAT >/dev/null

for N in $STEPS; do
  kubectl -n $NS scale deploy/app-canary --replicas=$N >/dev/null
  kubectl -n $NS rollout status deploy/app-canary --timeout=120s >/dev/null
  echo "--- Step: canary pods=$N, stable pods=3 ---"
  OUT=$(measure); echo "$OUT" | show
  CAN=$(echo "$OUT" | awk -v v=$VER '$1==v'); STB=$(echo "$OUT" | awk -v v=$STABLE_V '$1==v')
  [ -z "$CAN" ] && { rollback "no canary traffic seen, cannot verify"; exit 1; }
  CE=$(echo $CAN | awk '{print $4}'); CL=$(echo $CAN | awk '{print $5}'); SL=$(echo $STB | awk '{print $5}')
  if awk -v e=$CE -v m=$MAX_ERR 'BEGIN{exit !(e>m)}'; then
    rollback "canary error rate ${CE}% is above ${MAX_ERR}%"; exit 1; fi
  if awk -v c=$CL -v s=$SL -v f=$LAT_FACTOR 'BEGIN{exit !(c>f*s && c>50)}'; then
    rollback "canary latency ${CL} ms is above ${LAT_FACTOR}x stable (${SL} ms)"; exit 1; fi
  echo "  gate passed: error ${CE}% <= ${MAX_ERR}%, latency ${CL} ms vs stable ${SL} ms"
done

echo "=== All gates passed: PROMOTE $VER to 100% ==="
kubectl -n $NS set env deploy/app-stable VERSION=$VER ERROR_RATE=$RATE LATENCY_MS=$LAT >/dev/null
kubectl -n $NS rollout status deploy/app-stable --timeout=180s >/dev/null
kubectl -n $NS scale deploy/app-canary --replicas=0 >/dev/null
sleep 5
echo "--- Traffic after promotion ---"; measure | show
echo "=== Done in $((SECONDS-START)) s ==="
