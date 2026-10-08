from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
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

    # Rate Limiting (Phase 2C-3A)
    rate_limit_enabled: bool = Field(default=True, description="Enable API rate limiting")
    rate_limit_requests: int = Field(default=10, description="Maximum requests per window")
    rate_limit_window_seconds: int = Field(default=60, description="Rate limit window in seconds")
    # Stricter limits for authentication endpoints
    auth_rate_limit_requests: int = Field(default=5, description="Maximum auth requests per window")
    auth_rate_limit_window_seconds: int = Field(default=300, description="Auth rate limit window in seconds (5 minutes)")

    # Secure Cookie Authentication (Phase 2C-3A Checkpoint 2)
    cookie_enabled: bool = Field(default=True, description="Enable cookie-based authentication")
    cookie_secure: bool = Field(default=False, description="Secure flag for cookies (HTTPS only)")
    cookie_samesite: str = Field(default="lax", description="SameSite policy: lax, strict, none")
    cookie_domain: str = Field(default="", description="Cookie domain (empty for default)")
    cookie_path: str = Field(default="/", description="Cookie path")
    access_token_cookie_name: str = Field(default="access_token", description="Access token cookie name")
    refresh_token_cookie_name: str = Field(default="refresh_token", description="Refresh token cookie name")

    # CSRF Protection
    csrf_enabled: bool = Field(default=True, description="Enable CSRF protection")
    csrf_cookie_name: str = Field(default="csrf_token", description="CSRF token cookie name")
    csrf_header_name: str = Field(default="X-CSRF-Token", description="CSRF token header name")

    # Environment
    environment: str = Field(default="development", description="Environment name")
    debug: bool = Field(default=False, description="Debug mode")

    # Security Headers (Phase 2C-3A Checkpoint 3)
    security_headers_enabled: bool = Field(default=True, description="Enable security headers middleware")
    # Content Security Policy
    csp_enabled: bool = Field(default=True, description="Enable Content Security Policy")
    # HSTS - only for HTTPS/production
    hsts_enabled: bool = Field(default=False, description="Enable HSTS (HTTPS only)")
    hsts_max_age: int = Field(default=31536000, description="HSTS max-age in seconds (1 year)")
    hsts_include_subdomains: bool = Field(default=False, description="HSTS includeSubDomains")
    hsts_preload: bool = Field(default=False, description="HSTS preload")

    # Embedding / RAG (Phase 3)
    embedding_provider: str = Field(default="ollama", description="Embedding provider: ollama")
    embedding_model: str = Field(default="nomic-embed-text", description="Embedding model name")
    embedding_dimension: int = Field(default=768, description="Embedding vector dimension")
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama base URL")
    chunk_size: int = Field(default=500, description="Text chunk size in characters")
    chunk_overlap: int = Field(default=100, description="Text chunk overlap in characters")

    # AI Gateway / LLM (Phase 4)
    ai_provider: str = Field(default="ollama", description="AI provider: gemini or ollama")
    gemini_api_key: Optional[str] = Field(default=None, description="Gemini API key")
    gemini_model: str = Field(default="gemini-1.5-flash", description="Gemini model name")
    ollama_model: str = Field(default="llama3.2", description="Ollama model name")
    ai_temperature: float = Field(default=0.0, description="AI sampling temperature")
    ai_max_output_tokens: int = Field(default=4096, description="Max output tokens")
    ai_timeout_seconds: int = Field(default=30, description="AI request timeout in seconds")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()