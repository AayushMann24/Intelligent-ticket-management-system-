from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    # Database
    database_url: str = Field(..., description="PostgreSQL connection URL")

    # JWT
    secret_key: str = Field(..., description="JWT secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiry in minutes")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiry in days")

    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:5173"],
        description="Allowed CORS origins"
    )

    # File Uploads
    upload_dir: str = Field(default="./uploads", description="Directory for file uploads")

    # SLA Monitor (Phase 2C-2)
    sla_monitor_enabled: bool = Field(default=True, description="Enable SLA background monitor")
    sla_check_interval_seconds: int = Field(default=60, description="SLA check interval in seconds")

    # Environment
    environment: str = Field(default="development", description="Environment name")
    debug: bool = Field(default=False, description="Debug mode")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()