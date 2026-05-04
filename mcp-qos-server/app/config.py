from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8088
    transport_controller_url: str = "http://127.0.0.1:8080"
    telemetry_collector_url: str = "http://127.0.0.1:8081"
    default_telemetry_interval_ms: int = 250
    enable_dry_run: bool = False
    log_level: str = "INFO"
    qos_profile: str = "dynamic"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
