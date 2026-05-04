# MCP QoS Server

This is an MCP (Model Context Protocol) Server for managing QoS policies in an O-RAN aligned optical xHaul environment.

## Architecture

The server acts as an intermediary between the SMO/rApps and the Transport Controller, enforcing strict validation on all QoS requests and providing a unified API for telemetry and policy management.

## Environment Variables
- `MCP_HOST` / `MCP_PORT`: The interface and port to bind to.
- `TRANSPORT_CONTROLLER_URL`: URL of the transport controller.
- `TELEMETRY_COLLECTOR_URL`: URL of the telemetry collector.
- `ENABLE_DRY_RUN`: Set to `true` to mock transport controller responses.
- `DOCKER_ENV`: Automatically set when running in docker.

## Testing
To run tests locally:
```bash
pip install -r requirements.txt
pytest app/tests/
```

## Running with Docker
```bash
docker-compose up --build -d
```
