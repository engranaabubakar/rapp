#!/bin/bash
echo "[CORE] Starting 5G Core endpoint on 192.168.200.50"
iperf3 -s -D  # Receive traffic
sleep infinity
