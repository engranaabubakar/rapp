Dynamic QoS Orchestration over 200 Gb/s Optical xHaul for Edge-Enabled O-RAN
This repository contains the implementation artifacts for the paper:
> **Dynamic QoS Orchestration over 200 Gb/s Optical xHaul for Edge-Enabled O-RAN**  
> Rana Abu Bakar, Hafiz Mati Ur Rahman, Arsalan Ahmad, Muhammad Imran
The demo implements an O-RAN-aligned optical xHaul testbed using two NVIDIA DGX Spark nodes, containerized 5G RAN/Core components, and a telemetry-driven QoS orchestration framework. The objective is to validate dynamic QoS control for mixed URLLC and eMBB traffic over a high-capacity optical xHaul path.
The implementation supports:
Containerized 5G SA deployment using OpenAirInterface components
OAI gNB and NR-UE in RF simulator mode
OAI 5G Core with AMF, SMF, UPF, NRF, UDM, UDR, AUSF, and MySQL
Optical xHaul connectivity between access-side and core-side DGX Spark nodes
URLLC/eMBB service differentiation using VLAN, DSCP, and Linux `tc`
HTB-based bandwidth control
FQ-CoDel/CAKE queueing experiments
SMO/rApp/MCP-assisted dynamic QoS policy control
PDU session establishment with UE tunnel creation
A successful run creates the UE tunnel interface:
```bash
docker exec oai-nr-ue ip addr show oaitun_ue1
```
Expected output:
```text
oaitun_ue1: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1500 ...
    inet 12.1.1.66/24 scope global oaitun_ue1
```
---
1. Paper Context
The paper investigates dynamic QoS orchestration over an O-RAN-aligned optical xHaul testbed. The main motivation is that many xHaul deployments still rely on static QoS rules, which are not sufficient when latency-sensitive URLLC traffic and high-throughput eMBB traffic share the same transport infrastructure.
The proposed system extends the SMO/rApp control model toward the transport domain. A telemetry-driven rApp monitors the xHaul state, while an MCP-assisted control layer validates and applies QoS updates through a transport controller. QoS enforcement is performed using VLAN, DSCP, HTB, and queue-management rules.
This repository provides the practical demo environment used to validate the deployment and control-plane behavior.
---
2. High-Level Architecture
The testbed follows the architecture described in the paper:
```text
+----------------------------+       200 Gb/s Optical xHaul       +-----------------------------+
| Access-Side DGX Spark      | <-------------------------------> | Core-Side DGX Spark         |
|                            |                                   |                             |
|  OAI gNB                   |                                   |  OAI AMF                    |
|  OAI NR-UE                 |                                   |  OAI SMF                    |
|  Telemetry Collector       |                                   |  OAI UPF                    |
|  rApp / QoS Controller     |                                   |  NRF / UDM / UDR / AUSF     |
|  MCP QoS Server            |                                   |  MySQL Subscriber DB        |
|                            |                                   |                             |
+----------------------------+                                   +-----------------------------+
          |                                                                  |
          |                                                                  |
          +---------- Tofino / Transponders / 80 km Fiber / FS Switch --------+
```
The optical xHaul path carries both:
N2 control-plane traffic between gNB and AMF
N3 user-plane traffic between gNB and UPF
---
3. Relation to Paper Contributions
This repository supports the following paper contributions:
Paper Contribution	Repository Implementation
O-RAN-aligned xHaul testbed over DGX Spark nodes	Docker Compose deployment of OAI Core, gNB, UE, telemetry, and QoS components
Dynamic QoS control loop	rApp/MCP-assisted policy execution and telemetry-driven QoS updates
VLAN/DSCP/HTB service differentiation	Linux `tc`, VLAN, DSCP, HTB, FQ-CoDel/CAKE configuration
URLLC/eMBB traffic isolation	Separate QoS classes and DNN/slice configuration
Experimental validation	PDU session, tunnel creation, throughput, latency, and queue statistics
---
4. Tested Environment
The demo was tested using two NVIDIA DGX Spark nodes.
Component	Example Host	Role
Access-side DGX Spark	`spark-925b`	OAI gNB, NR-UE, access-side traffic tools
Core-side DGX Spark	`spark-6e5e`	OAI 5G Core, UPF, SMF, AMF, database
Optical path	External testbed	Tofino switch, optical transponders, 80 km fiber pool, FS switch
Example IP allocation:
Function	Interface Role	Example IP
AMF	N2 / NGAP	`192.168.200.40`
gNB	N2 / NGAP	`192.168.200.21`
SMF	N4 / PFCP	`192.168.200.51`
UPF	N3/N4 / GTP-U/PFCP	`192.168.200.50`
UE tunnel	PDU session	`12.1.1.66/24`
---
5. Repository Structure
```text
paper-oran/
├── docker-compose.yml
├── configs/
│   ├── gnb.conf
│   ├── nr-ue.conf
│   ├── amf-config.yaml
│   ├── upf-config.yaml
│   ├── oai_db.sql
│   └── qos/
│       ├── htb-urlcc-embb.sh
│       ├── fq-codel.sh
│       └── cake.sh
├── scripts/
│   ├── start-core.sh
│   ├── start-ran.sh
│   ├── validate-demo.sh
│   └── collect-results.sh
└── README.md
```
The exact structure may differ depending on the branch. The key files are the Docker Compose file, OAI configuration files, subscriber database file, and QoS scripts.
---
6. Prerequisites
Install Docker and required networking tools on both DGX Spark nodes:
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin jq lksctp-tools net-tools iproute2 iperf3
```
Enable SCTP if required:
```bash
lsmod | grep sctp || sudo modprobe sctp
```
Check Docker:
```bash
docker --version
docker compose version
```
---
7. Network Model
The demo uses two Docker networks:
```text
core_net:   192.168.150.0/24
dataplane: 192.168.200.0/24
```
The most important point is that N2, N3, and N4 must use the dataplane network.
Recommended mapping:
Interface	Network	Purpose
AMF `eth1`	`192.168.200.40`	N2 / NGAP
gNB dataplane interface	`192.168.200.21`	N2/N3 access side
SMF `eth1`	`192.168.200.51`	N4 / PFCP
UPF `eth1`	`192.168.200.50`	N3/N4 / GTP-U/PFCP
Core service interfaces	`192.168.150.0/24`	SBI and internal 5GC services
---
8. Key 5G Configuration
Use consistent PLMN, TAC, DNN, and slice parameters across AMF, gNB, UE, SMF, UPF, and MySQL.
```text
MCC: 208
MNC: 95
PLMN: 20895
TAC: 1
SST: 1
SD: 000001
DNN: oai.ipv4
UE IMSI: 208950000000131
UE IP pool: 12.1.1.0/24
```
---
9. OAI Configuration Notes
9.1 AMF
The AMF must bind NGAP/N2 to the dataplane interface:
```yaml
AMF_INTERFACE_NAME_FOR_NGAP: eth1
AMF_INTERFACE_NAME_FOR_N11: eth0
AMF_INTERFACE_NAME_FOR_SBI: eth0
```
Expected log:
```text
Set N2 AMF IPv4 Addr 192.168.200.40, port 38412
```
9.2 gNB
The gNB must point to the AMF dataplane IP:
```conf
amf_ip_address = ({ ipv4 = "192.168.200.40"; });

GNB_IPV4_ADDRESS_FOR_NG_AMF = "192.168.200.21";
GNB_IPV4_ADDRESS_FOR_NGU    = "192.168.200.21";
```
Expected gNB log:
```text
Received NGSetupResponse from AMF
Received NGAP_REGISTER_GNB_CNF: associated AMF 1
```
9.3 NR-UE
The UE configuration must match the subscriber database:
```conf
imsi = "208950000000131";
dnn = "oai.ipv4";
nssai_sst = 1;
nssai_sd = 0x000001;
```
9.4 SMF
The SMF N4 interface must bind to the dataplane side:
```yaml
SMF_INTERFACE_NAME_FOR_N4: eth1
SMF_INTERFACE_NAME_FOR_SBI: eth0
```
Expected log:
```text
pfcp_l4_stack created listening to 192.168.200.51:8805
```
9.5 UPF
The UPF must expose PFCP and GTP-U on the dataplane side:
```yaml
upf:
  pfcp:
    port: 8805
    interface_name: eth1

  gtpu:
    port: 2152
    interface_name: eth1

dnns:
  - dnn: oai.ipv4
    pdu_session_type: IPV4
    ipv4_subnet: 12.1.1.0/24
    n6: eth0
```
Expected UPF logs:
```text
pfcp_l4_stack created listening to 192.168.200.50:8805
gtpu_l4_stack created listening to 192.168.200.50:2152
DNN oai.ipv4
```
---
10. Subscriber Database
Check the subscriber information:
```bash
docker exec mysql mysql -utest -ptest oai_db -e "
SELECT ueid, supi FROM AuthenticationSubscription;
SELECT ueid FROM AccessAndMobilitySubscriptionData;
SELECT ueid, servingPlmnid, singleNssai, dnnConfigurations
FROM SessionManagementSubscriptionData\G
"
```
Expected values:
```text
ueid: 208950000000131
supi: 208950000000131
servingPlmnid: 20895
singleNssai: {"sd": "000001", "sst": 1}
DNN: oai.ipv4
```
If the IMSI must be corrected:
```bash
OLD_IMSI="208990000000001"
NEW_IMSI="208950000000131"

docker exec mysql mysql -utest -ptest oai_db -e "
UPDATE AuthenticationSubscription
SET ueid='${NEW_IMSI}', supi='${NEW_IMSI}'
WHERE ueid='${OLD_IMSI}' OR supi='${OLD_IMSI}';

UPDATE AccessAndMobilitySubscriptionData
SET ueid='${NEW_IMSI}'
WHERE ueid='${OLD_IMSI}';

UPDATE SessionManagementSubscriptionData
SET ueid='${NEW_IMSI}'
WHERE ueid='${OLD_IMSI}';
"
```
---
11. Running the Demo
11.1 Start the 5G Core
On the core-side DGX Spark node:
```bash
cd ~/paper-oran

docker compose up -d mysql oai-nrf oai-udr oai-udm oai-ausf oai-amf oai-smf oai-upf
```
Check running containers:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```
---
11.2 Validate AMF
```bash
docker logs oai-amf --since 2m | grep -iE "Set N2|PLMN|TAC|SNSSAI|error|fail"
sudo ss -lnp -A sctp | grep 38412
```
Expected:
```text
Set N2 AMF IPv4 Addr 192.168.200.40, port 38412
```
---
11.3 Validate SMF-UPF PFCP
```bash
docker logs oai-smf --since 2m | grep -iE "pfcp_l4_stack|UPF|Association|oai.ipv4|error|fail"
```
Expected:
```text
pfcp_l4_stack created listening to 192.168.200.51:8805
Received N4 ASSOCIATION SETUP RESPONSE from an UPF
Successfully added UPF node
```
---
11.4 Start gNB
On the access-side DGX Spark node:
```bash
cd ~/paper-oran

docker compose up -d --force-recreate oai-gnb
```
Check gNB logs:
```bash
docker logs oai-gnb --since 2m | grep -iE "NGSetup|NG Setup|AMF|PLMN|slice|failure|reject|associated"
```
Expected:
```text
Received NGSetupResponse from AMF
Received NGAP_REGISTER_GNB_CNF: associated AMF 1
```
---
11.5 Start NR-UE
```bash
docker compose up -d --force-recreate oai-nr-ue
```
Check UE logs:
```bash
docker logs oai-nr-ue --since 2m | grep -iE "Registration|Authentication|Security|PDU|accepted|reject|establish|oaitun|uesimtun|12.1.1"
```
Expected:
```text
Received Registration Accept with result 3GPP
Received PDU Session Establishment Accept, UE IPv4: 12.1.1.66
TUN Interface oaitun_ue1 successfully configured
```
---
12. Final Validation
Check the UE tunnel:
```bash
docker exec oai-nr-ue ip addr show oaitun_ue1
```
Expected:
```text
8025: oaitun_ue1: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1500 ...
    inet 12.1.1.66/24 scope global oaitun_ue1
```
Check the PDU session logs:
```bash
docker logs oai-nr-ue --since 5m | grep -iE "PDU Session Establishment Accept|oaitun|12.1.1"
```
Expected:
```text
Received PDU Session Establishment Accept, UE IPv4: 12.1.1.66
TUN Interface oaitun_ue1 successfully configured
```
---
13. QoS Experiment Mapping
The paper evaluates three traffic-control modes:
Mode	Description
Best-effort	No explicit QoS control; URLLC and eMBB compete directly
Static QoS	Fixed HTB allocation and queueing rules
Dynamic QoS	rApp/MCP-assisted adaptation of VLAN, DSCP, and HTB policies
The traffic classes are mapped as follows:
Service	VLAN	DSCP	HTB Class	Queueing
URLLC	100	EF / 46	`1:10`	FQ-CoDel
eMBB	200	BE / 0	`1:20`	FQ-CoDel or CAKE
Example QoS setup command:
```bash
sudo tc qdisc replace dev <IFACE> root handle 1: htb default 20
sudo tc class add dev <IFACE> parent 1: classid 1:10 htb rate 20gbit ceil 40gbit
sudo tc class add dev <IFACE> parent 1: classid 1:20 htb rate 20gbit ceil 160gbit
sudo tc qdisc add dev <IFACE> parent 1:10 fq_codel
sudo tc qdisc add dev <IFACE> parent 1:20 fq_codel
```
Replace `<IFACE>` with the xHaul-facing network interface.
---
14. Measurement Methodology
The paper uses two complementary evaluation modes.
14.1 Maximum-Throughput Stress Test
This test evaluates the containerized DGX Spark datapath over the verified 200 Gb/s optical xHaul path.
Reported result:
```text
Aggregate throughput: 134.7 Gb/s
eMBB throughput:      111.0 Gb/s
URLLC throughput:     23.7 Gb/s
Line utilization:     67.35%
```
14.2 Controlled QoS-Comparison Experiment
This test compares best-effort, static QoS, and dynamic QoS under mixed URLLC/eMBB traffic.
Configuration	Throughput	URLLC P99.9	Packet Loss
Best-effort	110.00 Gb/s	2.52 ms	0%
Static QoS	45.24 Gb/s	1.07 ms	0%
Dynamic QoS	45.28 Gb/s	0.99 ms	0%
The dynamic configuration satisfies the configured URLLC target:
```text
URLLC P99.9 latency target: < 1 ms
Measured dynamic QoS P99.9: 0.99 ms
```
---
15. Control-Plane and MCP Role
The MCP server is used as a controlled management interface between the rApp and the transport controller. It does not forward user-plane traffic.
The MCP layer provides:
Policy validation
Safe QoS action execution
Audit logging
Telemetry query interface
Controlled access to transport-management tools
Closed-loop throughput and latency optimization support
The control loop follows:
```text
Telemetry Collection
        ↓
rApp Analysis
        ↓
MCP Policy Validation
        ↓
Transport Controller Update
        ↓
VLAN / DSCP / HTB Enforcement
        ↓
QoS Measurement Feedback
```
---
16. Useful Debug Commands
Check container networks
```bash
docker inspect oai-amf --format '{{json .NetworkSettings.Networks}}' | jq
docker inspect oai-smf --format '{{json .NetworkSettings.Networks}}' | jq
docker inspect oai-upf --format '{{json .NetworkSettings.Networks}}' | jq
```
Check mounted configs
```bash
docker inspect oai-amf --format '{{json .Mounts}}' | jq
docker inspect oai-smf --format '{{json .Mounts}}' | jq
docker inspect oai-upf --format '{{json .Mounts}}' | jq
```
If this returns `[]`, the container is not using a bind-mounted local config.
Check AMF config
```bash
docker exec oai-amf grep -RniE "tac|mcc|mnc|sst|sd|ngap|interface" /openair-amf/etc
```
Check SMF config
```bash
docker exec oai-smf grep -RniE "n4|pfcp|upf|dnn|sst|sd|interface" /openair-smf/etc
```
Check UPF config
```bash
docker exec oai-upf grep -RniE "pfcp|gtpu|dnn|sst|sd|interface|n3|n4|n6" /openair-upf/etc
```
Check SCTP
```bash
sudo ss -anp -A sctp
```
Check PFCP/GTP-U
```bash
docker logs oai-smf --since 5m | grep -i "pfcp_l4_stack"
docker logs oai-upf --since 5m | grep -iE "pfcp_l4_stack|gtpu_l4_stack"
```
---
17. Common Problems and Fixes
17.1 NG Setup Failure
Symptom:
```text
Received NG setup failure for AMF
No common PLMN between gNB and AMF
```
Fix:
Match MCC/MNC between AMF and gNB.
Match TAC.
Match S-NSSAI.
---
17.2 AMF Binds to Wrong IP
Bad log:
```text
Set N2 AMF IPv4 Addr 192.168.150.10, port 38412
```
Correct log:
```text
Set N2 AMF IPv4 Addr 192.168.200.40, port 38412
```
Fix:
```yaml
AMF_INTERFACE_NAME_FOR_NGAP: eth1
```
Then recreate AMF:
```bash
docker compose stop oai-amf
docker compose rm -f oai-amf
docker compose up -d --force-recreate oai-amf
```
---
17.3 Registration Reject
Symptom:
```text
Received Registration reject
```
Fix:
Make sure UE IMSI exists in MySQL.
Make sure `ueid` and `supi` match.
Make sure `servingPlmnid` is `20895`.
Make sure the S-NSSAI is `sst=1`, `sd=000001`.
---
17.4 PDU Session Establishment Reject
Symptom:
```text
Received PDU Session Establishment reject
UPF selection failed
```
Fix:
Ensure SMF DNN is `oai.ipv4`.
Ensure UPF DNN is `oai.ipv4`.
Ensure SMF and UPF share the same S-NSSAI.
Ensure SMF N4/PFCP listens on `192.168.200.51:8805`.
Ensure UPF PFCP listens on `192.168.200.50:8805`.
Enable static UPF association if NRF discovery resolves the wrong interface.
Expected success:
```text
Received N4 ASSOCIATION SETUP RESPONSE from an UPF
Received PDU Session Establishment Accept, UE IPv4: 12.1.1.66
```
---
18. Successful Demo Checklist
A complete successful run should show the following.
gNB
```text
Received NGSetupResponse from AMF
Received NGAP_REGISTER_GNB_CNF: associated AMF 1
```
AMF
```text
Received Registration Request message
Registration Accept
```
SMF
```text
pfcp_l4_stack created listening to 192.168.200.51:8805
Received N4 ASSOCIATION SETUP RESPONSE from an UPF
Successfully added UPF node
```
UPF
```text
pfcp_l4_stack created listening to 192.168.200.50:8805
gtpu_l4_stack created listening to 192.168.200.50:2152
DNN oai.ipv4
```
UE
```text
Received Registration Accept with result 3GPP
Received PDU Session Establishment Accept, UE IPv4: 12.1.1.66
TUN Interface oaitun_ue1 successfully configured
```
Tunnel
```bash
docker exec oai-nr-ue ip addr show oaitun_ue1
```
```text
inet 12.1.1.66/24 scope global oaitun_ue1
```
---
19. Citation
If you use this repository, please cite the related paper:
```bibtex
@inproceedings{abubakar2026dynamicqos,
  title     = {Dynamic QoS Orchestration over 200 Gb/s Optical xHaul for Edge-Enabled O-RAN},
  author    = {Abu Bakar, Rana and Rahman, Hafiz Mati Ur and Ahmad, Arsalan and Imran, Muhammad},
  booktitle = {IEEE Conference Proceedings},
  year      = {2026}
}
```
Update the venue information once the paper is accepted/published.
---
20. Acknowledgment
This work was conducted at Scuola Superiore Sant'Anna, Pisa, Italy, within the TECIP Institute facilities. The authors acknowledge the support of the PNTLAB infrastructure used for the experimental evaluation.
---
21. License
Add your preferred license here, for example:
```text
MIT License
```
or
```text
For academic and research use only.
```
