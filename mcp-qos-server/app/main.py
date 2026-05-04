from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
import app.tools as tools
from app.models import MCPToolResponse

app = FastAPI(title="MCP QoS Server", description="MCP tool interface for optical xHaul QoS orchestration")

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/tools")
async def list_tools() -> List[str]:
    return [
        "get_qos_state",
        "get_link_telemetry",
        "get_queue_stats",
        "get_policy_status",
        "apply_urllc_priority_policy",
        "apply_embb_borrowing_policy",
        "restore_static_qos_policy",
        "run_qos_validation_test",
        "export_qos_test_report",
        "optimize_throughput_closed_loop"
    ]

@app.post("/tools/get_qos_state", response_model=MCPToolResponse)
async def endpoint_get_qos_state(): return await tools.tool_get_qos_state()

@app.post("/tools/get_link_telemetry", response_model=MCPToolResponse)
async def endpoint_get_link_telemetry(): return await tools.tool_get_link_telemetry()

@app.post("/tools/get_queue_stats", response_model=MCPToolResponse)
async def endpoint_get_queue_stats(): return await tools.tool_get_queue_stats()

@app.post("/tools/get_policy_status", response_model=MCPToolResponse)
async def endpoint_get_policy_status(): return await tools.tool_get_policy_status()

@app.post("/tools/apply_urllc_priority_policy", response_model=MCPToolResponse)
async def endpoint_apply_urllc_priority_policy(): return await tools.tool_apply_urllc_priority_policy()

@app.post("/tools/apply_embb_borrowing_policy", response_model=MCPToolResponse)
async def endpoint_apply_embb_borrowing_policy(): return await tools.tool_apply_embb_borrowing_policy()

@app.post("/tools/restore_static_qos_policy", response_model=MCPToolResponse)
async def endpoint_restore_static_qos_policy(): return await tools.tool_restore_static_qos_policy()

@app.post("/tools/run_qos_validation_test", response_model=MCPToolResponse)
async def endpoint_run_qos_validation_test(): return await tools.tool_run_qos_validation_test()

@app.post("/tools/export_qos_test_report", response_model=MCPToolResponse)
async def endpoint_export_qos_test_report(): return await tools.tool_export_qos_test_report()

@app.post("/tools/optimize_throughput_closed_loop", response_model=MCPToolResponse)
async def endpoint_optimize_throughput_closed_loop(): return await tools.tool_optimize_throughput_closed_loop()
