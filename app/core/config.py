from pickle import TRUE
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Swiggy AI Agent"
    DEBUG: bool = True

    NVIDIA_API_KEY: str
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    LLM_MODEL: str = "mistralai/mistral-medium-3.5-128b"
    LLM_REASONING_EFFORT: str = "medium"

    SWIGGY_MCP_BASE_URL : str = "https://mcp.swiggy.com"
    SWIGGY_ACCESS_TOKEN: str = ""

    REDIS_URL: str = "redis://localhost:6379/0"

    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = SettingsConfigDict(env_file=".env", 
                            env_file_encoding="utf-8", 
                            extra="ignore",
                            case_sensitive= True)

settings = Settings()