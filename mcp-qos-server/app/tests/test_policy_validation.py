import pytest
from app.transport_client import TransportClient
import asyncio

@pytest.mark.asyncio
async def test_transport_client_dry_run():
    client = TransportClient()
    client.dry_run = True
    
    result = await client.get_qos_status()
    assert result["mocked"] == True
    
    result = await client.apply_qos_policy({"test": "data"})
    assert result["mocked"] == True
    assert result["payload_received"] == {"test": "data"}
