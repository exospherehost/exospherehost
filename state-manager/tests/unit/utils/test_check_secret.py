import os
import pytest
from unittest.mock import patch
from fastapi import HTTPException
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED

from app.utils.check_secret import api_key_header, API_KEY_NAME


class TestCheckApiKey:
    """Test cases for check_api_key function"""

    @patch.dict(os.environ, {'STATE_MANAGER_SECRET': 'test-secret-key'})
    @pytest.mark.asyncio
    async def test_check_api_key_success_with_valid_key(self):
        """Test check_api_key succeeds with valid API key"""
        # Import here to get the updated environment variable
        from app.utils.check_secret import check_api_key
        
        # Reload the module to pick up the new environment variable
        import importlib
        import app.utils.check_secret
        importlib.reload(app.utils.check_secret)
        
        result = await check_api_key('test-secret-key')
        assert result == 'test-secret-key'

    @patch.dict(os.environ, {'STATE_MANAGER_SECRET': 'test-secret-key'})
    @pytest.mark.asyncio
    async def test_check_api_key_fails_with_invalid_key(self):
        """Test check_api_key fails with invalid API key"""
        # Import here to get the updated environment variable
        import importlib
        import app.utils.check_secret
        importlib.reload(app.utils.check_secret)
        from app.utils.check_secret import check_api_key
        
        with pytest.raises(HTTPException) as exc_info:
            await check_api_key('wrong-key')
        
        assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid API key"

    @patch.dict(os.environ, {'STATE_MANAGER_SECRET': 'test-secret-key'})
    @pytest.mark.asyncio
    async def test_check_api_key_fails_with_none_key(self):
        """Test check_api_key fails with None API key"""
        import importlib
        import app.utils.check_secret
        importlib.reload(app.utils.check_secret)
        from app.utils.check_secret import check_api_key
        
        with pytest.raises(HTTPException) as exc_info:
            await check_api_key(None) # type: ignore
        
        assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid API key"

    @patch.dict(os.environ, {'STATE_MANAGER_SECRET': 'test-secret-key'})
    @pytest.mark.asyncio
    async def test_check_api_key_fails_with_empty_string_key(self):
        """Test check_api_key fails with empty string API key"""
        import importlib
        import app.utils.check_secret
        importlib.reload(app.utils.check_secret)
        from app.utils.check_secret import check_api_key
        
        with pytest.raises(HTTPException) as exc_info:
            await check_api_key('')
        
        assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid API key"

    @patch.dict(os.environ, {'STATE_MANAGER_SECRET': 'case-sensitive-key'})
    @pytest.mark.asyncio
    async def test_check_api_key_is_case_sensitive(self):
        """Test check_api_key is case sensitive"""
        import importlib
        import app.utils.check_secret
        importlib.reload(app.utils.check_secret)
        from app.utils.check_secret import check_api_key
        
        with pytest.raises(HTTPException) as exc_info:
            await check_api_key('CASE-SENSITIVE-KEY')
        
        assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid API key"

    @patch.dict(os.environ, {'STATE_MANAGER_SECRET': 'whitespace-key'})
    @pytest.mark.asyncio
    async def test_check_api_key_whitespace_sensitive(self):
        """Test check_api_key is sensitive to whitespace"""
        import importlib
        import app.utils.check_secret
        importlib.reload(app.utils.check_secret)
        from app.utils.check_secret import check_api_key
        
        with pytest.raises(HTTPException) as exc_info:
            await check_api_key(' whitespace-key ')
        
        assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid API key"

    @patch.dict(os.environ, {'STATE_MANAGER_SECRET': 'special-chars-!@#$%^&*()'})
    @pytest.mark.asyncio
    async def test_check_api_key_with_special_characters(self):
        """Test check_api_key works with special characters"""
        import importlib
        import app.utils.check_secret
        importlib.reload(app.utils.check_secret)
        from app.utils.check_secret import check_api_key
        
        result = await check_api_key('special-chars-!@#$%^&*()')
        assert result == 'special-chars-!@#$%^&*()'

    @patch.dict(os.environ, {'STATE_MANAGER_SECRET': 'unicode-key-你好'})
    @pytest.mark.asyncio
    async def test_check_api_key_with_unicode_characters(self):
        """Test check_api_key works with unicode characters"""
        import importlib
        import app.utils.check_secret
        importlib.reload(app.utils.check_secret)
        from app.utils.check_secret import check_api_key
        
        result = await check_api_key('unicode-key-你好')
        assert result == 'unicode-key-你好'

    @patch.dict(os.environ, {'STATE_MANAGER_SECRET': ''})
    @pytest.mark.asyncio
    async def test_check_api_key_with_empty_env_variable(self):
        """Test check_api_key when STATE_MANAGER_SECRET is empty string"""
        import importlib
        import app.utils.check_secret
        importlib.reload(app.utils.check_secret)
        from app.utils.check_secret import check_api_key
        
        # Empty string should match empty string
        result = await check_api_key('')
        assert result == ''

    @patch.dict(os.environ, {'STATE_MANAGER_SECRET': 'very-long-key-with-many-characters-1234567890-abcdefghijklmnopqrstuvwxyz-ABCDEFGHIJKLMNOPQRSTUVWXYZ'})
    @pytest.mark.asyncio
    async def test_check_api_key_with_very_long_key(self):
        """Test check_api_key works with very long keys"""
        import importlib
        import app.utils.check_secret
        importlib.reload(app.utils.check_secret)
        from app.utils.check_secret import check_api_key
        
        long_key = 'very-long-key-with-many-characters-1234567890-abcdefghijklmnopqrstuvwxyz-ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        result = await check_api_key(long_key)
        assert result == long_key


class TestModuleConstants:
    """Test cases for module constants and configuration"""

    def test_api_key_name_constant(self):
        """Test API_KEY_NAME constant is correct"""
        assert API_KEY_NAME == "x-api-key"

    def test_api_key_header_configuration(self):
        """Test api_key_header is configured correctly"""
        assert isinstance(api_key_header, APIKeyHeader)
        assert api_key_header.model.name == "x-api-key"
        assert api_key_header.auto_error is False

    @patch.dict(os.environ, {'STATE_MANAGER_SECRET': 'test-constant-key'})
    def test_api_key_loads_from_environment(self):
        """Test API_KEY loads from environment variable"""
        import importlib
        import app.utils.check_secret
        importlib.reload(app.utils.check_secret)
        
        # Access the reloaded module's API_KEY
        assert app.utils.check_secret.API_KEY == 'test-constant-key'

class TestIntegrationWithFastAPI:
    """Integration tests with FastAPI dependency system"""

    @patch.dict(os.environ, {'STATE_MANAGER_SECRET': 'integration-test-key'})
    @pytest.mark.asyncio
    async def test_dependency_integration_success(self):
        """Test successful integration as FastAPI dependency"""
        import importlib
        import app.utils.check_secret
        importlib.reload(app.utils.check_secret)
        from app.utils.check_secret import check_api_key
        
        # Simulate FastAPI calling the dependency with the correct header value
        result = await check_api_key('integration-test-key')
        assert result == 'integration-test-key'

    @patch.dict(os.environ, {'STATE_MANAGER_SECRET': 'integration-test-key'})
    @pytest.mark.asyncio
    async def test_dependency_integration_failure(self):
        """Test failed integration as FastAPI dependency"""
        import importlib
        import app.utils.check_secret
        importlib.reload(app.utils.check_secret)
        from app.utils.check_secret import check_api_key
        
        # Simulate FastAPI calling the dependency with wrong header value
        with pytest.raises(HTTPException) as exc_info:
            await check_api_key('wrong-integration-key')
        
        assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED
        assert "Invalid API key" in exc_info.value.detail

    def test_api_key_header_accepts_none_when_auto_error_false(self):
        """Test api_key_header configuration allows None when auto_error is False"""
        # This tests the configuration, not the actual FastAPI behavior
        # but ensures our APIKeyHeader is set up to not auto-error
        assert api_key_header.auto_error is False
        # This means FastAPI won't automatically raise 403 when header is missing