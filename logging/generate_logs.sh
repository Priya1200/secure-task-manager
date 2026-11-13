#!/bin/bash
LOGFILE="./logs/app.log"
ROUTES=("/tasks" "/login" "/tasks/create" "/tasks/delete" "/health")
LEVELS=("INFO" "INFO" "INFO" "WARNING" "ERROR")
STATUSES=(200 200 201 404 500)

for i in $(seq 1 40); do
  TS=$(date "+%Y-%m-%d %H:%M:%S")
  MS=$(printf "%03d" $((RANDOM % 1000)))
  LEVEL=${LEVELS[$RANDOM % ${#LEVELS[@]}]}
  ROUTE=${ROUTES[$RANDOM % ${#ROUTES[@]}]}
  STATUS=${STATUSES[$RANDOM % ${#STATUSES[@]}]}
  echo "$TS,$MS $LEVEL 127.0.0.1 - \"GET $ROUTE HTTP/1.1\" $STATUS" >> "$LOGFILE"
  sleep 0.2
done
