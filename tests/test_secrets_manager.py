"""
Tests for AWS Secrets Manager integration.
"""

import json
import os
from unittest.mock import Mock, patch

import pytest
from botocore.exceptions import ClientError

from app.secrets_manager import (
    SecretsManager,
    get_secrets_manager,
    get_app_secret,
    get_deployment_secret,
)


class TestSecretsManager:
    """Test the SecretsManager class."""

    def test_init_default_region(self):
        """Test initialization with default region."""
        with patch.dict(os.environ, {"AWS_REGION": "us-west-2"}):
            sm = SecretsManager()
            assert sm.region_name == "us-west-2"

    def test_init_explicit_region(self):
        """Test initialization with explicit region."""
        sm = SecretsManager(region_name="eu-west-1")
        assert sm.region_name == "eu-west-1"

    def test_init_fallback_region(self):
        """Test initialization falls back to us-east-1."""
        with patch.dict(os.environ, {}, clear=True):
            sm = SecretsManager()
            assert sm.region_name == "us-east-1"

    @patch("boto3.client")
    def test_get_secret_success(self, mock_boto_client):
        """Test successful secret retrieval."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        test_secret = {"key1": "value1", "key2": "value2"}
        mock_client.get_secret_value.return_value = {"SecretString": json.dumps(test_secret)}

        sm = SecretsManager()
        result = sm.get_secret("test-secret")

        assert result == test_secret
        mock_client.get_secret_value.assert_called_once_with(SecretId="test-secret")

    @patch("boto3.client")
    def test_get_secret_not_found(self, mock_boto_client):
        """Test secret not found error."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        error = ClientError(error_response={"Error": {"Code": "ResourceNotFoundException"}}, operation_name="GetSecretValue")
        mock_client.get_secret_value.side_effect = error

        sm = SecretsManager()

        with pytest.raises(ValueError, match="Secret test-secret not found"):
            sm.get_secret("test-secret")

    @patch("boto3.client")
    def test_get_secret_access_denied(self, mock_boto_client):
        """Test access denied error."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        error = ClientError(error_response={"Error": {"Code": "AccessDeniedException"}}, operation_name="GetSecretValue")
        mock_client.get_secret_value.side_effect = error

        sm = SecretsManager()

        with pytest.raises(PermissionError, match="Access denied to secret test-secret"):
            sm.get_secret("test-secret")

    @patch("boto3.client")
    def test_get_secret_binary_not_supported(self, mock_boto_client):
        """Test binary secrets are not supported."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        mock_client.get_secret_value.return_value = {"SecretBinary": b"binary-data"}

        sm = SecretsManager()

        with pytest.raises(ValueError, match="Binary secret test-secret is not supported"):
            sm.get_secret("test-secret")

    @patch("boto3.client")
    def test_get_secret_value_success(self, mock_boto_client):
        """Test getting specific value from secret."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        test_secret = {"key1": "value1", "key2": "value2"}
        mock_client.get_secret_value.return_value = {"SecretString": json.dumps(test_secret)}

        sm = SecretsManager()
        result = sm.get_secret_value("test-secret", "key1")

        assert result == "value1"

    @patch("boto3.client")
    def test_get_secret_value_with_default(self, mock_boto_client):
        """Test getting value with default fallback."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        test_secret = {"key1": "value1"}
        mock_client.get_secret_value.return_value = {"SecretString": json.dumps(test_secret)}

        sm = SecretsManager()
        result = sm.get_secret_value("test-secret", "missing_key", "default_value")

        assert result == "default_value"

    @patch("boto3.client")
    def test_get_secret_value_error_returns_default(self, mock_boto_client):
        """Test error in get_secret_value returns default."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        error = ClientError(error_response={"Error": {"Code": "ResourceNotFoundException"}}, operation_name="GetSecretValue")
        mock_client.get_secret_value.side_effect = error

        sm = SecretsManager()
        result = sm.get_secret_value("test-secret", "key1", "default")

        assert result == "default"


class TestGlobalFunctions:
    """Test module-level convenience functions."""

    @patch("app.secrets_manager.SecretsManager")
    def test_get_secrets_manager_singleton(self, mock_sm_class):
        """Test global secrets manager is singleton."""
        mock_instance = Mock()
        mock_sm_class.return_value = mock_instance

        # Clear any existing instance
        import app.secrets_manager

        app.secrets_manager._secrets_manager = None

        # First call creates instance
        result1 = get_secrets_manager()
        # Second call returns same instance
        result2 = get_secrets_manager()

        assert result1 == result2
        mock_sm_class.assert_called_once()

    @patch.dict(os.environ, {"JWT_SECRET": "env-jwt-secret"})
    def test_get_app_secret_from_env(self):
        """Test getting secret from environment variable first."""
        result = get_app_secret("jwt_secret", "default")
        assert result == "env-jwt-secret"

    @patch.dict(os.environ, {}, clear=True)
    @patch("app.secrets_manager.get_secrets_manager")
    def test_get_app_secret_from_secrets_manager(self, mock_get_sm):
        """Test getting secret from Secrets Manager when env var not set."""
        mock_sm = Mock()
        mock_get_sm.return_value = mock_sm
        mock_sm.get_secret_value.return_value = "sm-jwt-secret"

        result = get_app_secret("jwt_secret", "default")

        assert result == "sm-jwt-secret"
        mock_sm.get_secret_value.assert_called_once_with("FastAPIAppSecrets", "jwt_secret", "default")

    @patch.dict(os.environ, {}, clear=True)
    @patch("app.secrets_manager.get_secrets_manager")
    def test_get_app_secret_fallback_to_default(self, mock_get_sm):
        """Test fallback to default when Secrets Manager fails."""
        mock_sm = Mock()
        mock_get_sm.return_value = mock_sm
        mock_sm.get_secret_value.side_effect = Exception("AWS error")

        result = get_app_secret("jwt_secret", "default")

        assert result == "default"

    @patch.dict(os.environ, {"APP_SECRETS_NAME": "CustomAppSecrets"})
    @patch("app.secrets_manager.get_secrets_manager")
    def test_get_app_secret_custom_name(self, mock_get_sm):
        """Test using custom secret name from environment."""
        mock_sm = Mock()
        mock_get_sm.return_value = mock_sm
        mock_sm.get_secret_value.return_value = "secret-value"

        get_app_secret("jwt_secret")

        mock_sm.get_secret_value.assert_called_once_with("CustomAppSecrets", "jwt_secret", None)

    @patch("app.secrets_manager.get_secrets_manager")
    def test_get_deployment_secret_success(self, mock_get_sm):
        """Test successful deployment secret retrieval."""
        mock_sm = Mock()
        mock_get_sm.return_value = mock_sm
        mock_sm.get_secret_value.return_value = "ec2-host-value"

        result = get_deployment_secret("ec2_host", "default")

        assert result == "ec2-host-value"
        mock_sm.get_secret_value.assert_called_once_with("FastAPIDeploymentSecrets", "ec2_host", "default")

    @patch("app.secrets_manager.get_secrets_manager")
    def test_get_deployment_secret_error_fallback(self, mock_get_sm):
        """Test deployment secret fallback on error."""
        mock_sm = Mock()
        mock_get_sm.return_value = mock_sm
        mock_sm.get_secret_value.side_effect = Exception("AWS error")

        result = get_deployment_secret("ec2_host", "default")

        assert result == "default"

    @patch.dict(os.environ, {"DEPLOYMENT_SECRETS_NAME": "CustomDeploySecrets"})
    @patch("app.secrets_manager.get_secrets_manager")
    def test_get_deployment_secret_custom_name(self, mock_get_sm):
        """Test using custom deployment secret name."""
        mock_sm = Mock()
        mock_get_sm.return_value = mock_sm
        mock_sm.get_secret_value.return_value = "secret-value"

        get_deployment_secret("ec2_host")

        mock_sm.get_secret_value.assert_called_once_with("CustomDeploySecrets", "ec2_host", None)
