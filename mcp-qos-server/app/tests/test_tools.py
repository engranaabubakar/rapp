import pytest
from app.tools import execute_tool
import asyncio

@pytest.mark.asyncio
async def test_execute_tool_success():
    async def mock_func():
        return {"result": "success"}
    
    response = await execute_tool("mock_tool", mock_func)
    assert response.success == True
    assert response.data == {"result": "success"}
    assert response.error is None
    assert response.latency_ms > 0

@pytest.mark.asyncio
async def test_execute_tool_failure():
    async def mock_func():
        raise ValueError("Mock error")
    
    response = await execute_tool("mock_tool", mock_func)
    assert response.success == False
    assert response.data is None
    assert response.error == "Mock error"
    assert response.latency_ms > 0
