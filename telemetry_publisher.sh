#!/usr/bin/env bash
RAPP=${RAPP:-http://127.0.0.1:8090/ingest}
while true; do
  J=${JITTER_MS:-0.6}
  D=${DELAY_MS:-0.7}
  E=${EMBB_DEMAND_G:-7.5}
  U=${URLLC_LOAD_G:-1.2}
  curl -s -X POST "$RAPP" -H 'Content-Type: application/json'     -d "{"jitter_ms":$J,"delay_ms":$D,"embb_demand_gbps":$E,"urllc_load_gbps":$U}" >/dev/null
  sleep ${PERIOD_S:-3}
done
