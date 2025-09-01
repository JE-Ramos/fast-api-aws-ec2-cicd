"""
AWS Secrets Manager integration for secure credential management.

This module provides utilities to fetch secrets from AWS Secrets Manager,
enabling centralized secret management without hardcoding credentials.
"""

import json
import os
from functools import lru_cache
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError


class SecretsManager:
    """Handle AWS Secrets Manager operations."""
    
    def __init__(self, region_name: str = None):
        """Initialize Secrets Manager client.
        
        Args:
            region_name: AWS region. Defaults to AWS_REGION env var or us-east-1.
        """
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.client = boto3.client("secretsmanager", region_name=self.region_name)
    
    @lru_cache(maxsize=32)
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """Retrieve secret from AWS Secrets Manager.
        
        Args:
            secret_name: Name or ARN of the secret.
            
        Returns:
            Dict containing the secret values.
            
        Raises:
            ClientError: If secret cannot be retrieved.
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            
            # Secrets Manager returns either SecretString or SecretBinary
            if "SecretString" in response:
                return json.loads(response["SecretString"])
            else:
                # Binary secrets are not supported in this implementation
                raise ValueError(f"Binary secret {secret_name} is not supported")
                
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ResourceNotFoundException":
                raise ValueError(f"Secret {secret_name} not found") from e
            elif error_code == "AccessDeniedException":
                raise PermissionError(f"Access denied to secret {secret_name}") from e
            else:
                raise
    
    def get_secret_value(self, secret_name: str, key: str, default: Any = None) -> Any:
        """Get specific value from a secret.
        
        Args:
            secret_name: Name or ARN of the secret.
            key: Key within the secret JSON.
            default: Default value if key not found.
            
        Returns:
            The value for the specified key.
        """
        try:
            secret = self.get_secret(secret_name)
            return secret.get(key, default)
        except (ValueError, PermissionError):
            return default


# Global instance for easy access
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get or create global SecretsManager instance.
    
    Returns:
        SecretsManager instance.
    """
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


def get_app_secret(key: str, default: Any = None) -> Any:
    """Convenience function to get application secrets.
    
    Args:
        key: Key within the application secrets.
        default: Default value if key not found.
        
    Returns:
        The secret value.
    """
    # Try to get from environment variable first (for local development)
    env_value = os.getenv(key.upper())
    if env_value:
        return env_value
    
    # Then try Secrets Manager
    secret_name = os.getenv("APP_SECRETS_NAME", "FastAPIAppSecrets")
    try:
        return get_secrets_manager().get_secret_value(secret_name, key, default)
    except Exception:
        # Fallback to default if Secrets Manager is not available
        return default


def get_deployment_secret(key: str, default: Any = None) -> Any:
    """Convenience function to get deployment secrets.
    
    Args:
        key: Key within the deployment secrets.
        default: Default value if key not found.
        
    Returns:
        The secret value.
    """
    secret_name = os.getenv("DEPLOYMENT_SECRETS_NAME", "FastAPIDeploymentSecrets")
    try:
        return get_secrets_manager().get_secret_value(secret_name, key, default)
    except Exception:
        return default