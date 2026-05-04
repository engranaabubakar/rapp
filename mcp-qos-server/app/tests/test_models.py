import pytest
from app.models import QoSPolicyPayload, SliceConfig

def test_valid_payload():
    payload = QoSPolicyPayload(
        profile="test",
        urllc=SliceConfig(vlan=100, dscp=46, class_id="1:10", min_rate_gbps=2.0, ceil_rate_gbps=20.0, queue="fq_codel"),
        embb=SliceConfig(vlan=200, dscp=0, class_id="1:20", min_rate_gbps=8.0, ceil_rate_gbps=180.0, queue="cake"),
        link_capacity_gbps=200.0,
        telemetry_interval_ms=250
    )
    assert payload.urllc.vlan == 100

def test_invalid_bandwidth():
    with pytest.raises(ValueError, match="Sum of URLLC and eMBB minimum rates exceeds link capacity"):
        QoSPolicyPayload(
            profile="test",
            urllc=SliceConfig(vlan=100, dscp=46, class_id="1:10", min_rate_gbps=150.0, ceil_rate_gbps=200.0, queue="fq_codel"),
            embb=SliceConfig(vlan=200, dscp=0, class_id="1:20", min_rate_gbps=60.0, ceil_rate_gbps=200.0, queue="cake"),
            link_capacity_gbps=200.0,
            telemetry_interval_ms=250
        )

def test_invalid_vlan_clash():
    with pytest.raises(ValueError, match="URLLC and eMBB cannot share the same VLAN ID"):
        QoSPolicyPayload(
            profile="test",
            urllc=SliceConfig(vlan=100, dscp=46, class_id="1:10", min_rate_gbps=2.0, ceil_rate_gbps=20.0, queue="fq_codel"),
            embb=SliceConfig(vlan=100, dscp=0, class_id="1:20", min_rate_gbps=8.0, ceil_rate_gbps=180.0, queue="cake"),
            link_capacity_gbps=200.0,
            telemetry_interval_ms=250
        )

def test_invalid_dscp():
    with pytest.raises(ValueError):
        SliceConfig(vlan=100, dscp=99, class_id="1:10", min_rate_gbps=2.0, ceil_rate_gbps=20.0, queue="fq_codel")
