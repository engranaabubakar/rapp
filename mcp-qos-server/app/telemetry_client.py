import httpx
from typing import Dict, Any
from app.config import settings
import random

class TelemetryClient:
    def __init__(self):
        self.base_url = settings.telemetry_collector_url
        self.dry_run = settings.enable_dry_run
        self.timeout = httpx.Timeout(5.0)

    async def _get(self, path: str) -> Dict[str, Any]:
        if self.dry_run:
            # Mock telemetry data for dry runs
            if path == "/telemetry/link":
                return {"status": "ok", "mocked": True, "link_utilization_percent": round(random.uniform(50, 98), 2)}
            elif path == "/telemetry/queues":
                return {"status": "ok", "mocked": True, "urllc_latency_ms": round(random.uniform(0.1, 1.5), 3)}
            return {"status": "ok", "mocked": True, "path": path}
            
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}{path}")
            response.raise_for_status()
            return response.json()

    async def get_link_telemetry(self) -> Dict[str, Any]:
        return await self._get("/telemetry/link")

    async def get_queue_stats(self) -> Dict[str, Any]:
        return await self._get("/telemetry/queues")

    async def get_current_state(self) -> Dict[str, Any]:
        link_data = await self.get_link_telemetry()
        queue_data = await self.get_queue_stats()
        return {
            "link": link_data,
            "queues": queue_data
        }

telemetry_client = TelemetryClient()
