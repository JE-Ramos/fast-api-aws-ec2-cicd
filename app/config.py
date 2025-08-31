from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    app_name: str = "FastAPI AWS App"
    environment: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_session_token: str = ""


@lru_cache()
def get_settings():
    return Settings()