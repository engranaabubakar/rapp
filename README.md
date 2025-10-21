# rApp + Transport Controller (Dynamic QoS over xHaul)

This package deploys a minimal SMO-like rApp and a Transport Controller to dynamically configure
Linux `tc` (HTB + FQ-CoDel/CAKE) for URLLC/eMBB VLAN slicing over your xHaul interface.

## Run
1) Set controller iface in docker-compose.yml (`XHAUL_IFACE`, default `eth1`)
2) Set rApp `TRANSPORT_CTRL` URL if controller is on another host
3) `docker compose up --build -d`

## Telemetry
`./telemetry_publisher.sh` posts delay/jitter and loads to the rApp to trigger policy changes.

## Verify
`curl -s http://127.0.0.1:8080/tc_show`

## Policies
- Baseline: URLLC 2 Gb/s, eMBB 6 Gb/s
- Protect URLCC: enforce on delay>0.95ms or jitter>0.8ms
- Borrow to eMBB: if URLLC<0.5 Gb/s and eMBB≥7 Gb/s
