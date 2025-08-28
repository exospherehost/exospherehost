import pytest
from unittest.mock import patch, MagicMock

from app.config.cors import get_cors_config, get_cors_origins


class TestCORSConfiguration:
    """Test cases for CORS configuration"""

    def test_get_cors_origins_default(self):
        """Test get_cors_origins with default configuration"""
        with patch('app.config.cors.os.getenv', return_value=""):
            result = get_cors_origins()
            
            # Verify default origins are returned
            expected_origins = [
                "http://localhost:3000",
                "http://localhost:3001", 
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001"
            ]
            assert result == expected_origins

    def test_get_cors_origins_from_environment(self):
        """Test get_cors_origins with environment variable"""
        with patch('app.config.cors.os.getenv', return_value="https://example.com,https://test.com"):
            result = get_cors_origins()
            
            # Verify environment origins are returned
            expected_origins = ["https://example.com", "https://test.com"]
            assert result == expected_origins

    def test_get_cors_origins_with_whitespace(self):
        """Test get_cors_origins with whitespace in environment variable"""
        with patch('app.config.cors.os.getenv', return_value="  https://example.com , https://test.com  "):
            result = get_cors_origins()
            
            # Verify whitespace is stripped
            expected_origins = ["https://example.com", "https://test.com"]
            assert result == expected_origins

    def test_get_cors_origins_empty_entries(self):
        """Test get_cors_origins with empty entries in environment variable"""
        with patch('app.config.cors.os.getenv', return_value="https://example.com,,https://test.com"):
            result = get_cors_origins()
            
            # Verify empty entries are filtered out
            expected_origins = ["https://example.com", "https://test.com"]
            assert result == expected_origins

    def test_get_cors_config_default(self):
        """Test get_cors_config with default configuration"""
        with patch('app.config.cors.get_cors_origins') as mock_get_origins:
            mock_get_origins.return_value = ["http://localhost:3000"]
            
            result = get_cors_config()
            
            # Verify configuration structure
            assert 'allow_origins' in result
            assert 'allow_credentials' in result
            assert 'allow_methods' in result
            assert 'allow_headers' in result
            assert 'expose_headers' in result
            
            # Verify values
            assert result['allow_origins'] == ["http://localhost:3000"]
            assert result['allow_credentials'] is True
            assert result['allow_methods'] == ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
            assert "X-API-Key" in result['allow_headers']
            assert "X-Exosphere-Request-ID" in result['allow_headers']
            assert result['expose_headers'] == ["X-Exosphere-Request-ID"]

    def test_get_cors_config_headers_validation(self):
        """Test get_cors_config headers validation"""
        with patch('app.config.cors.get_cors_origins') as mock_get_origins:
            mock_get_origins.return_value = ["http://localhost:3000"]
            
            result = get_cors_config()
            
            # Verify all required headers are present
            required_headers = [
                "Accept", "Accept-Language", "Content-Language", "Content-Type",
                "X-API-Key", "Authorization", "X-Requested-With", "X-Exosphere-Request-ID"
            ]
            
            for header in required_headers:
                assert header in result['allow_headers']

    def test_get_cors_config_methods_validation(self):
        """Test get_cors_config methods validation"""
        with patch('app.config.cors.get_cors_origins') as mock_get_origins:
            mock_get_origins.return_value = ["http://localhost:3000"]
            
            result = get_cors_config()
            
            # Verify all required methods are present
            required_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
            
            for method in required_methods:
                assert method in result['allow_methods']

    def test_get_cors_config_expose_headers(self):
        """Test get_cors_config expose headers"""
        with patch('app.config.cors.get_cors_origins') as mock_get_origins:
            mock_get_origins.return_value = ["http://localhost:3000"]
            
            result = get_cors_config()
            
            # Verify expose headers
            assert result['expose_headers'] == ["X-Exosphere-Request-ID"]

    def test_get_cors_config_credentials_setting(self):
        """Test get_cors_config credentials setting"""
        with patch('app.config.cors.get_cors_origins') as mock_get_origins:
            mock_get_origins.return_value = ["http://localhost:3000"]
            
            result = get_cors_config()
            
            # Verify credentials are enabled
            assert result['allow_credentials'] is True

    def test_get_cors_config_integration(self):
        """Test get_cors_config integration with get_cors_origins"""
        with patch('app.config.cors.os.getenv', return_value="https://example.com"):
            result = get_cors_config()
            
            # Verify origins are passed through correctly
            assert result['allow_origins'] == ["https://example.com"] 