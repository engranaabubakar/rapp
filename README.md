OAI 5G SA Demo on NVIDIA DGX Spark
Here is Demo video link https://youtu.be/XYVi2nt2xS0

This repository provides a containerized OpenAirInterface (OAI) 5G Standalone (SA) demo deployed across NVIDIA DGX Spark systems. The demo brings up an OAI 5G Core, gNB, and NR-UE using Docker Compose, RF simulator mode, and a working PDU session through the OAI UPF.
The final expected result is a registered UE with a working tunnel interface:
```bash
docker exec oai-nr-ue ip addr show oaitun_ue1
```
Expected output:
```text
oaitun_ue1: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1500 ...
    inet 12.1.1.66/24 scope global oaitun_ue1
```
---
1. Demo Objective
The goal of this demo is to show a complete 5G SA control-plane and user-plane setup on DGX Spark:
```text
NR-UE  ->  OAI gNB  ->  OAI AMF  ->  OAI SMF  ->  OAI UPF
                                  ->  NRF/UDM/UDR/AUSF/MySQL
```
The demo validates:
NGAP association between gNB and AMF
UE authentication and registration
SMF to UPF N4/PFCP association
PDU session establishment
UE tunnel creation with `oaitun_ue1`
UE IP allocation from the DNN subnet
---
2. Tested Environment
This setup was tested on NVIDIA DGX Spark hosts using Docker Compose.
Example host layout:
Component	Host	Example IP
5G Core	DGX Spark core-side node	`spark-6e5e`
gNB + NR-UE	DGX Spark UE-side node	`spark-925b`
AMF N2 / NGAP	Dataplane network	`192.168.200.40`
gNB N2 address	Dataplane network	`192.168.200.21`
SMF N4 address	Dataplane network	`192.168.200.51`
UPF N3/N4 address	Dataplane network	`192.168.200.50`
UE tunnel IP	OAI DNN subnet	`12.1.1.66/24`
---
3. Repository Structure
A typical repository layout is:
```text
paper-oran/
├── docker-compose.yml
├── configs/
│   ├── gnb.conf
│   ├── nr-ue.conf
│   ├── amf-config.yaml
│   ├── upf-config.yaml
│   └── oai_db.sql
└── README.md
```
Some OAI containers may use internal default config files unless explicitly mounted. Always verify what config the running container is actually using.
---
4. Prerequisites
Install the following packages on the DGX Spark hosts:
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin jq lksctp-tools net-tools iproute2
```
Verify Docker:
```bash
docker --version
docker compose version
```
Verify SCTP support:
```bash
lsmod | grep sctp || sudo modprobe sctp
```
---
5. Network Design
The demo uses two logical Docker networks:
```text
core_net:     192.168.150.0/24
dataplane:   192.168.200.0/24
```
Recommended IP mapping:
Function	Interface Role	IP
AMF	N2/NGAP	`192.168.200.40`
SMF	N4/PFCP	`192.168.200.51`
UPF	N3/N4/GTP-U/PFCP	`192.168.200.50`
gNB	N2/NGAP	`192.168.200.21`
UE tunnel	PDU session	`12.1.1.66/24`
---
6. Important Configuration Values
6.1 PLMN and Slice
Use the same PLMN and slice across AMF, gNB, UE, SMF, UPF, and database.
```text
MCC: 208
MNC: 95
PLMN: 20895
SST: 1
SD: 000001
TAC: 1
DNN: oai.ipv4
```
6.2 gNB Configuration
In `configs/gnb.conf`, verify:
```conf
plmn_list = ({
  mcc = 208;
  mnc = 95;
  mnc_length = 2;
  snssaiList = ({ sst = 1; sd = 0x000001; })
});

amf_ip_address = ({ ipv4 = "192.168.200.40"; });

GNB_IPV4_ADDRESS_FOR_NG_AMF = "192.168.200.21";
GNB_IPV4_ADDRESS_FOR_NGU    = "192.168.200.21";
```
6.3 UE Configuration
In `configs/nr-ue.conf`, verify:
```conf
imsi = "208950000000131";
dnn = "oai.ipv4";
nssai_sst = 1;
nssai_sd = 0x000001;
```
> The IMSI must exist in MySQL and must match the subscriber data.
6.4 AMF Configuration
The AMF must bind NGAP/N2 on the dataplane interface:
```yaml
AMF_INTERFACE_NAME_FOR_NGAP: eth1
AMF_INTERFACE_NAME_FOR_N11: eth0
AMF_INTERFACE_NAME_FOR_SBI: eth0
```
The AMF should report:
```text
Set N2 AMF IPv4 Addr 192.168.200.40, port 38412
```
6.5 SMF Configuration
The SMF must bind N4/PFCP on the dataplane interface:
```yaml
SMF_INTERFACE_NAME_FOR_N4: eth1
SMF_INTERFACE_NAME_FOR_SBI: eth0
```
Expected log:
```text
pfcp_l4_stack created listening to 192.168.200.51:8805
```
6.6 UPF Configuration
The UPF should listen on the dataplane interface for PFCP and GTP-U:
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
7. Subscriber Database
Check subscriber data in MySQL:
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
Example SQL update if IMSI must be changed:
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
8. Deployment Steps
8.1 Start the 5G Core
On the core-side DGX Spark node:
```bash
cd ~/paper-oran

docker compose up -d mysql oai-nrf oai-udr oai-udm oai-ausf oai-amf oai-smf oai-upf
```
Check status:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```
8.2 Verify AMF N2/NGAP
```bash
docker logs oai-amf --since 2m | grep -iE "Set N2|PLMN|TAC|SNSSAI|error|fail"
sudo ss -lnp -A sctp | grep 38412
```
Expected:
```text
Set N2 AMF IPv4 Addr 192.168.200.40, port 38412
LISTEN ... 38412
```
8.3 Verify SMF N4/PFCP
```bash
docker logs oai-smf --since 2m | grep -iE "pfcp_l4_stack|UPF|Association|oai.ipv4|error|fail"
```
Expected:
```text
pfcp_l4_stack created listening to 192.168.200.51:8805
```
8.4 Verify UPF PFCP/GTP-U
```bash
docker logs oai-upf --since 2m | grep -iE "pfcp|gtpu|REGISTERED|upfInfo|oai.ipv4"
```
Expected:
```text
pfcp_l4_stack created listening to 192.168.200.50:8805
gtpu_l4_stack created listening to 192.168.200.50:2152
DNN oai.ipv4
```
8.5 Start gNB
On the UE/gNB-side DGX Spark node:
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
8.6 Start NR-UE
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
9. Final Validation
9.1 Check UE Tunnel
```bash
docker exec oai-nr-ue ip addr show oaitun_ue1
```
Expected:
```text
inet 12.1.1.66/24 scope global oaitun_ue1
```
9.2 Check PDU Session Logs
```bash
docker logs oai-nr-ue --since 5m | grep -iE "PDU Session Establishment Accept|oaitun|12.1.1"
```
Expected:
```text
Received PDU Session Establishment Accept, UE IPv4: 12.1.1.66
TUN Interface oaitun_ue1 successfully configured
```
9.3 Check PFCP Association
```bash
docker logs oai-smf --since 5m | grep -iE "ASSOCIATION SETUP RESPONSE|Successfully added UPF|PFCP"
```
Expected:
```text
Received N4 ASSOCIATION SETUP RESPONSE from an UPF
Successfully added UPF node
```
---
10. Troubleshooting
Problem 1: gNB shows `NG setup failure`
Example:
```text
Received NG setup failure for AMF
No common PLMN between gNB and AMF
```
Fix:
Match MCC/MNC between AMF and gNB.
Match TAC.
Match slice SST/SD.
Check AMF:
```bash
docker logs oai-amf --since 3m | grep -iE "PLMN Support|TAC|Slice Support|Unknown PLMN|NGSetup|failure"
```
Check gNB:
```bash
grep -n "plmn_list\|amf_ip_address\|GNB_IPV4_ADDRESS_FOR_NG_AMF" configs/gnb.conf
```
---
Problem 2: AMF binds to wrong IP
Bad example:
```text
Set N2 AMF IPv4 Addr 192.168.150.10, port 38412
```
Expected:
```text
Set N2 AMF IPv4 Addr 192.168.200.40, port 38412
```
Fix the AMF NGAP interface:
```yaml
AMF_INTERFACE_NAME_FOR_NGAP: eth1
```
Recreate AMF:
```bash
docker compose stop oai-amf
docker compose rm -f oai-amf
docker compose up -d --force-recreate oai-amf
```
---
Problem 3: UE Registration Reject
Example:
```text
Received Registration reject
```
Common causes:
IMSI does not exist in MySQL.
`supi` still contains the old IMSI.
UDR SUPI range does not include the IMSI.
PLMN does not match `servingPlmnid`.
Check:
```bash
docker exec mysql mysql -utest -ptest oai_db -e "
SELECT ueid, supi FROM AuthenticationSubscription;
SELECT ueid FROM AccessAndMobilitySubscriptionData;
SELECT ueid, servingPlmnid, singleNssai, dnnConfigurations
FROM SessionManagementSubscriptionData\G
"
```
---
Problem 4: Registration Accept but PDU Session Reject
Example:
```text
Received Registration Accept
Received PDU Session Establishment reject
```
Common cause:
```text
UPF selection failed
```
Check SMF logs:
```bash
docker logs oai-smf --since 5m | grep -iE "UPF selection failed|PDU Session|DNN|NSSAI|PFCP|Association|reject"
```
Fix:
Match SMF DNN with UPF DNN.
Match slice SST/SD.
Ensure SMF N4 and UPF PFCP are on the same reachable network.
Ensure SMF listens on `192.168.200.51:8805`.
Ensure UPF listens on `192.168.200.50:8805`.
Expected SMF:
```text
pfcp_l4_stack created listening to 192.168.200.51:8805
Received N4 ASSOCIATION SETUP RESPONSE from an UPF
```
Expected UPF:
```text
pfcp_l4_stack created listening to 192.168.200.50:8805
```
---
Problem 5: SMF resolves UPF to `192.168.150.8`
Example:
```text
Resolved a DNS name oai-upf: Ip Addr 192.168.150.8
```
If the UPF is configured to listen on dataplane `192.168.200.50`, make sure the SMF also uses the dataplane path for N4/PFCP.
Recommended options:
Put SMF N4 on `eth1`.
Put UPF PFCP on `eth1`.
Use direct UPF IP if DNS resolves the wrong network.
Enable UPF without NRF discovery only if you explicitly want static UPF selection.
---
11. Useful Debug Commands
Show container environment
```bash
docker inspect oai-amf --format '{{range .Config.Env}}{{println .}}{{end}}' | sort
docker inspect oai-smf --format '{{range .Config.Env}}{{println .}}{{end}}' | sort
docker inspect oai-upf --format '{{range .Config.Env}}{{println .}}{{end}}' | sort
```
Show container networks
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
Check live config inside containers
```bash
docker exec oai-amf grep -RniE "tac|mcc|mnc|sst|sd|ngap|interface" /openair-amf/etc
docker exec oai-smf grep -RniE "n4|pfcp|upf|dnn|sst|sd|interface" /openair-smf/etc
docker exec oai-upf grep -RniE "pfcp|gtpu|dnn|sst|sd|interface|n3|n4|n6" /openair-upf/etc
```
Check SCTP
```bash
sudo ss -anp -A sctp
```
Check PFCP and GTP-U ports
```bash
docker logs oai-smf --since 5m | grep -i "pfcp_l4_stack"
docker logs oai-upf --since 5m | grep -iE "pfcp_l4_stack|gtpu_l4_stack"
```
---
12. Successful Demo Output
A successful run should show:
gNB
```text
Received NGSetupResponse from AMF
Received NGAP_REGISTER_GNB_CNF: associated AMF 1
```
UE
```text
Received Registration Accept with result 3GPP
Received PDU Session Establishment Accept, UE IPv4: 12.1.1.66
TUN Interface oaitun_ue1 successfully configured
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
UE Tunnel
```bash
docker exec oai-nr-ue ip addr show oaitun_ue1
```
```text
inet 12.1.1.66/24 scope global oaitun_ue1
```
---
13. Notes
The `tini` warning is usually not the root cause of OAI failure in this demo.
Most failures came from mismatched PLMN/TAC/S-NSSAI, wrong AMF/SMF interface binding, or UPF selection failure.
Always verify the running container config, not only the repository file.
If `docker inspect <container> --format '{{json .Mounts}}'` returns `[]`, the container is not using your local config file as a bind mount.
For a permanent fix, mount the corrected config files in `docker-compose.yml` instead of editing inside containers manually.
---
14. Quick Final Check
Run this after starting all services:
```bash
docker logs oai-gnb --since 5m | grep -iE "NGSetupResponse|associated AMF"
docker logs oai-nr-ue --since 5m | grep -iE "Registration Accept|PDU Session Establishment Accept|oaitun|12.1.1"
docker logs oai-smf --since 5m | grep -iE "ASSOCIATION SETUP RESPONSE|Successfully added UPF"
docker exec oai-nr-ue ip addr show oaitun_ue1
```
Expected final line:
```text
inet 12.1.1.66/24 scope global oaitun_ue1
```
