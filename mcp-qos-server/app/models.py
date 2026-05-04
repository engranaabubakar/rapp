from pydantic import BaseModel, Field, model_validator
from typing import Optional, Any, Dict, List

class SliceConfig(BaseModel):
    vlan: int = Field(..., ge=1, le=4094, description="VLAN ID for the slice")
    dscp: int = Field(..., ge=0, le=63, description="DSCP value for the slice")
    class_id: str = Field(..., description="HTB class ID, e.g., '1:10'")
    min_rate_gbps: float = Field(..., ge=0, description="Minimum guaranteed rate in Gbps")
    ceil_rate_gbps: float = Field(..., gt=0, description="Maximum allowed rate in Gbps")
    queue: str = Field(..., description="Queueing discipline, e.g., 'fq_codel' or 'cake'")
    burst_mb: Optional[float] = Field(default=15.0, description="HTB burst size in MB")
    r2q: Optional[int] = Field(default=1000, description="HTB Rate-to-Quantum ratio")

class QoSPolicyPayload(BaseModel):
    profile: str = Field(..., description="Name of the QoS profile")
    urllc: SliceConfig = Field(..., description="URLLC slice configuration")
    embb: SliceConfig = Field(..., description="eMBB slice configuration")
    link_capacity_gbps: float = Field(..., gt=0, description="Total link capacity in Gbps")
    telemetry_interval_ms: int = Field(..., gt=0, description="Telemetry interval in milliseconds")

    @model_validator(mode='after')
    def validate_bandwidth_and_vlans(self) -> 'QoSPolicyPayload':
        if self.urllc.min_rate_gbps + self.embb.min_rate_gbps > self.link_capacity_gbps:
            raise ValueError("Sum of URLLC and eMBB minimum rates exceeds link capacity")
        if self.urllc.vlan == self.embb.vlan:
            raise ValueError("URLLC and eMBB cannot share the same VLAN ID")
        return self

class MCPToolResponse(BaseModel):
    success: bool
    tool: str
    latency_ms: float
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
