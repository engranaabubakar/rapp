#!/bin/bash
echo "[RAN] Starting base station emulator on 192.168.200.10"
iperf3 -s -D  # Background server mode
sleep infinity
