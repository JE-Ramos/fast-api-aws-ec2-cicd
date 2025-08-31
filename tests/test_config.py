import pytest
from unittest.mock import patch
from app.config import Settings, get_settings


def test_default_settings():
    settings = Settings()
    assert settings.app_name == "FastAPI AWS App"
    assert settings.environment == "development"
    assert settings.debug is True
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.aws_region == "us-east-1"


def test_settings_from_env():
    with patch.dict('os.environ', {
        'APP_NAME': 'Test App',
        'ENVIRONMENT': 'production',
        'DEBUG': 'false',
        'AWS_REGION': 'us-west-2'
    }):
        settings = Settings()
        assert settings.app_name == 'Test App'
        assert settings.environment == 'production'
        assert settings.debug is False
        assert settings.aws_region == 'us-west-2'


def test_get_settings_singleton():
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


def test_settings_extra_fields_ignored():
    with patch.dict('os.environ', {
        'EXTRA_FIELD': 'should_be_ignored',
        'CDK_DEFAULT_ACCOUNT': 'account123'
    }):
        settings = Settings()
        assert not hasattr(settings, 'extra_field')
        assert not hasattr(settings, 'cdk_default_account')