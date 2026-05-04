import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
import os

LOG_DIR = "/app/logs" if os.environ.get("DOCKER_ENV") else "./logs"
os.makedirs(LOG_DIR, exist_ok=True)
AUDIT_LOG_FILE = os.path.join(LOG_DIR, "mcp_audit.jsonl")

# Setup structured logger
logger = logging.getLogger("mcp_audit")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(AUDIT_LOG_FILE)
handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(handler)

def log_action(tool_name: str, input_params: Dict[str, Any], result: Optional[Dict[str, Any]], success: bool, latency_ms: float, error: Optional[str] = None):
    """
    Logs an action to the JSONL audit log.
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tool": tool_name,
        "input": input_params,
        "result": result,
        "success": success,
        "latency_ms": latency_ms,
        "error": error
    }
    logger.info(json.dumps(log_entry))
