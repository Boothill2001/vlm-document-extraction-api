from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "VLM Document Extraction API"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    default_provider: str = "mock"
    claude_api_key: str = ""
    deepseek_api_key: str = ""
    gemini_api_key: str = ""
    gpt4_api_key: str = ""

    max_file_size_mb: int = 10
    upload_dir: str = "uploads"

    confidence_threshold: float = 0.75

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings(_env_file=".env")
