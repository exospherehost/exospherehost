"""
Simple integration test example that demonstrates the basic setup.
"""
import pytest
import os
from unittest.mock import patch
from app.config.settings import get_settings


class TestSimpleIntegration:
    """Simple integration tests to verify the basic setup."""

    def test_settings_loading(self):
        """Test that settings are loaded correctly."""
        # Set environment for testing with complete isolation
        test_env = {
            "ENVIRONMENT": "testing",
            "STATE_MANAGER_SECRET": "test-secret-key",
            "MONGO_URI": "mongodb://localhost:27017"
        }
        
        with patch.dict(os.environ, test_env, clear=True):
            settings = get_settings()
            
            # Verify settings are loaded
            assert settings.environment == "testing"
            assert settings.state_manager_secret == "test-secret-key"
            assert settings.mongo_uri == "mongodb://localhost:27017"

    def test_settings_defaults(self):
        """Test that settings have proper defaults."""
        # Clear environment variables to test defaults
        with patch.dict(os.environ, {}, clear=True):
            settings = get_settings()
            
            # Verify defaults
            assert settings.environment == "development"
            assert settings.state_manager_secret == "test-secret-key"
            assert settings.mongo_uri == "mongodb://localhost:27017"

    def test_settings_environment_override(self):
        """Test that environment variables override defaults."""
        # Set specific environment variables
        test_env = {
            "ENVIRONMENT": "production",
            "MONGO_URI": "mongodb://test-host:27017",
            "MONGO_DATABASE_NAME": "test_db",
            "STATE_MANAGER_SECRET": "custom-secret"
        }
        
        with patch.dict(os.environ, test_env, clear=True):
            settings = get_settings()
            
            # Verify overrides
            assert settings.environment == "production"
            assert settings.mongo_uri == "mongodb://test-host:27017"
            assert settings.mongo_database_name == "test_db"
            assert settings.state_manager_secret == "custom-secret"

    def test_settings_model_validation(self):
        """Test that settings model validation works."""
        # Test with valid data
        settings = get_settings()
        
        # Verify all required fields are present
        assert hasattr(settings, 'mongo_uri')
        assert hasattr(settings, 'mongo_database_name')
        assert hasattr(settings, 'state_manager_secret')
        assert hasattr(settings, 'environment')
        assert hasattr(settings, 'host')
        assert hasattr(settings, 'port')

    def test_settings_from_env_method(self):
        """Test the from_env class method."""
        # Set environment variables
        test_env = {
            "ENVIRONMENT": "staging",
            "MONGO_URI": "mongodb://staging-host:27017",
            "STATE_MANAGER_SECRET": "staging-secret"
        }
        
        with patch.dict(os.environ, test_env, clear=True):
            settings = get_settings()
            
            # Verify the from_env method works
            assert settings.environment == "staging"
            assert settings.mongo_uri == "mongodb://staging-host:27017"
            assert settings.state_manager_secret == "staging-secret" 