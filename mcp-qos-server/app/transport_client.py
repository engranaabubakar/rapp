import httpx
from typing import Dict, Any
from app.config import settings

class TransportClient:
    def __init__(self):
        self.base_url = settings.transport_controller_url
        self.dry_run = settings.enable_dry_run
        self.timeout = httpx.Timeout(5.0)

    async def _get(self, path: str) -> Dict[str, Any]:
        if self.dry_run:
            return {"status": "ok", "mocked": True, "path": path}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}{path}")
            response.raise_for_status()
            return response.json()

    async def _post(self, path: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        if self.dry_run:
            return {"status": "ok", "mocked": True, "path": path, "payload_received": payload}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}{path}", json=payload)
            response.raise_for_status()
            return response.json()

    async def health(self) -> Dict[str, Any]:
        return await self._get("/health")

    async def get_qos_status(self) -> Dict[str, Any]:
        return await self._get("/qos/status")

    async def apply_qos_policy(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post("/qos/apply", payload=policy)

    async def restore_qos_policy(self) -> Dict[str, Any]:
        return await self._post("/qos/restore")

    async def validate_qos_policy(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post("/qos/validate", payload=policy)

transport_client = TransportClient()
