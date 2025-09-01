import os
from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    app_name: str = "FastAPI AWS App"
    environment: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_session_token: str = ""
    
    # Secrets Manager configuration
    use_secrets_manager: bool = Field(default=False, description="Enable AWS Secrets Manager")
    app_secrets_name: str = Field(default="FastAPIAppSecrets", description="Name of app secrets in Secrets Manager")
    deployment_secrets_name: str = Field(default="FastAPIDeploymentSecrets", description="Name of deployment secrets")
    
    # Application secrets (can be loaded from Secrets Manager)
    db_password: Optional[str] = Field(default=None, description="Database password")
    jwt_secret: Optional[str] = Field(default=None, description="JWT signing secret")
    api_keys: Optional[str] = Field(default=None, description="External API keys")
    
    @field_validator("use_secrets_manager", mode="before")
    @classmethod
    def check_ec2_environment(cls, v):
        """Auto-enable Secrets Manager when running on EC2."""
        # Check if running on EC2 by looking for instance metadata
        if os.path.exists("/var/lib/cloud/instance"):
            return True
        # Also check for explicit environment variable
        return os.getenv("USE_SECRETS_MANAGER", str(v)).lower() in ("true", "1", "yes")
    
    def load_from_secrets_manager(self):
        """Load secrets from AWS Secrets Manager if enabled."""
        if not self.use_secrets_manager:
            return
        
        try:
            from app.secrets_manager import get_app_secret
            
            # Load application secrets
            self.db_password = get_app_secret("db_password", self.db_password)
            self.jwt_secret = get_app_secret("jwt_secret", self.jwt_secret)
            self.api_keys = get_app_secret("api_keys", self.api_keys)
            
        except ImportError:
            print("Warning: secrets_manager module not found, skipping Secrets Manager integration")
        except Exception as e:
            print(f"Warning: Failed to load secrets from Secrets Manager: {e}")


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.load_from_secrets_manager()
    return settings
