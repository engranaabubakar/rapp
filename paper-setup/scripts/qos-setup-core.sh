#!/bin/bash
INTERFACE="eth1"
echo "[QoS-Core] Configuring HTB on core dataplane"

tc qdisc del dev $INTERFACE root 2>/dev/null || true
tc qdisc add dev $INTERFACE root handle 1: htb default 11
tc class add dev $INTERFACE parent 1: classid 1:1 htb rate 9000mbit burst 15k
tc class add dev $INTERFACE parent 1:1 classid 1:10 htb rate 500mbit ceil 2000mbit burst 15k prio 0
tc class add dev $INTERFACE parent 1:1 classid 1:11 htb rate 100mbit ceil 7000mbit burst 15k prio 1
tc qdisc add dev $INTERFACE parent 1:10 handle 10: pfifo_fast
tc qdisc add dev $INTERFACE parent 1:11 handle 11: fq_codel

echo "[QoS-Core] ✓ Ready"
