from unittest.mock import patch
import os

from app.config.cors import get_cors_origins, get_cors_config


class TestCORS:
    """Test cases for CORS configuration"""

    def test_get_cors_origins_with_environment_variable(self):
        """Test get_cors_origins with CORS_ORIGINS environment variable"""
        test_origins = "https://example.com,https://test.com,https://app.com"
        
        with patch.dict(os.environ, {'CORS_ORIGINS': test_origins}):
            origins = get_cors_origins()
            
            assert origins == ["https://example.com", "https://test.com", "https://app.com"]

    def test_get_cors_origins_with_whitespace(self):
        """Test get_cors_origins with whitespace in environment variable"""
        test_origins = "  https://example.com  ,  https://test.com  ,  https://app.com  "
        
        with patch.dict(os.environ, {'CORS_ORIGINS': test_origins}):
            origins = get_cors_origins()
            
            assert origins == ["https://example.com", "https://test.com", "https://app.com"]

    def test_get_cors_origins_with_empty_entries(self):
        """Test get_cors_origins with empty entries in environment variable"""
        test_origins = "https://example.com,,https://test.com, ,https://app.com"
        
        with patch.dict(os.environ, {'CORS_ORIGINS': test_origins}):
            origins = get_cors_origins()
            
            assert origins == ["https://example.com", "https://test.com", "https://app.com"]

    def test_get_cors_origins_with_single_origin(self):
        """Test get_cors_origins with single origin"""
        test_origins = "https://example.com"
        
        with patch.dict(os.environ, {'CORS_ORIGINS': test_origins}):
            origins = get_cors_origins()
            
            assert origins == ["https://example.com"]

    def test_get_cors_origins_with_empty_string(self):
        """Test get_cors_origins with empty string"""
        test_origins = ""
        
        with patch.dict(os.environ, {'CORS_ORIGINS': test_origins}):
            origins = get_cors_origins()
            
            # When CORS_ORIGINS is empty string, it should return default origins
            expected_defaults = [
                "http://localhost:3000",  # Next.js frontend
                "http://localhost:3001",  # Alternative frontend port
                "http://127.0.0.1:3000",  # Alternative localhost
                "http://127.0.0.1:3001",  # Alternative localhost port
            ]
            assert origins == expected_defaults

    def test_get_cors_origins_with_whitespace_only(self):
        """Test get_cors_origins with whitespace-only string"""
        test_origins = "   "
        
        with patch.dict(os.environ, {'CORS_ORIGINS': test_origins}):
            origins = get_cors_origins()
            
            assert origins == []

    def test_get_cors_origins_default_when_no_env_var(self):
        """Test get_cors_origins returns defaults when no environment variable"""
        with patch.dict(os.environ, {}, clear=True):
            origins = get_cors_origins()
            
            expected_defaults = [
                "http://localhost:3000",  # Next.js frontend
                "http://localhost:3001",  # Alternative frontend port
                "http://127.0.0.1:3000",  # Alternative localhost
                "http://127.0.0.1:3001",  # Alternative localhost port
            ]
            
            assert origins == expected_defaults

    def test_get_cors_origins_default_when_env_var_not_set(self):
        """Test get_cors_origins returns defaults when CORS_ORIGINS is not set"""
        # Remove CORS_ORIGINS if it exists
        env_copy = os.environ.copy()
        if 'CORS_ORIGINS' in env_copy:
            del env_copy['CORS_ORIGINS']
        
        with patch.dict(os.environ, env_copy, clear=True):
            origins = get_cors_origins()
            
            expected_defaults = [
                "http://localhost:3000",  # Next.js frontend
                "http://localhost:3001",  # Alternative frontend port
                "http://127.0.0.1:3000",  # Alternative localhost
                "http://127.0.0.1:3001",  # Alternative localhost port
            ]
            
            assert origins == expected_defaults

    def test_get_cors_config_structure(self):
        """Test get_cors_config returns correct structure"""
        config = get_cors_config()
        
        # Check required keys
        assert "allow_origins" in config
        assert "allow_credentials" in config
        assert "allow_methods" in config
        assert "allow_headers" in config
        assert "expose_headers" in config

    def test_get_cors_config_allow_credentials(self):
        """Test get_cors_config allow_credentials setting"""
        config = get_cors_config()
        
        assert config["allow_credentials"] is True

    def test_get_cors_config_allow_methods(self):
        """Test get_cors_config allow_methods"""
        config = get_cors_config()
        
        expected_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        assert config["allow_methods"] == expected_methods

    def test_get_cors_config_allow_headers(self):
        """Test get_cors_config allow_headers"""
        config = get_cors_config()
        
        expected_headers = [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "X-API-Key",
            "Authorization",
            "X-Requested-With",
            "X-Exosphere-Request-ID",
        ]
        assert config["allow_headers"] == expected_headers

    def test_get_cors_config_expose_headers(self):
        """Test get_cors_config expose_headers"""
        config = get_cors_config()
        
        expected_expose_headers = ["X-Exosphere-Request-ID"]
        assert config["expose_headers"] == expected_expose_headers

    def test_get_cors_config_origins_integration(self):
        """Test that get_cors_config uses get_cors_origins"""
        test_origins = ["https://custom1.com", "https://custom2.com"]
        
        with patch('app.config.cors.get_cors_origins', return_value=test_origins):
            config = get_cors_config()
            
            assert config["allow_origins"] == test_origins

    def test_get_cors_config_with_custom_origins(self):
        """Test get_cors_config with custom origins from environment"""
        test_origins = "https://custom1.com,https://custom2.com"
        
        with patch.dict(os.environ, {'CORS_ORIGINS': test_origins}):
            config = get_cors_config()
            
            assert config["allow_origins"] == ["https://custom1.com", "https://custom2.com"]

    def test_get_cors_config_with_default_origins(self):
        """Test get_cors_config with default origins"""
        with patch.dict(os.environ, {}, clear=True):
            config = get_cors_config()
            
            expected_defaults = [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
            ]
            
            assert config["allow_origins"] == expected_defaults

    def test_cors_origins_edge_cases(self):
        """Test get_cors_origins with various edge cases"""
        test_cases = [
            ("https://example.com", ["https://example.com"]),
            ("https://example.com,", ["https://example.com"]),
            (",https://example.com", ["https://example.com"]),
            (",,https://example.com,,", ["https://example.com"]),
            ("   https://example.com   ", ["https://example.com"]),
            ("https://example.com   ,   https://test.com", ["https://example.com", "https://test.com"]),
        ]
        
        for input_origins, expected_origins in test_cases:
            with patch.dict(os.environ, {'CORS_ORIGINS': input_origins}):
                origins = get_cors_origins()
                assert origins == expected_origins

    def test_cors_config_immutability(self):
        """Test that get_cors_config returns a new dict each time"""
        config1 = get_cors_config()
        config2 = get_cors_config()
        
        # Should be different objects
        assert config1 is not config2
        
        # But should have same content
        assert config1 == config2

    def test_cors_origins_immutability(self):
        """Test that get_cors_origins returns a new list each time"""
        with patch.dict(os.environ, {'CORS_ORIGINS': 'https://example.com'}):
            origins1 = get_cors_origins()
            origins2 = get_cors_origins()
            
            # Should be different objects
            assert origins1 is not origins2
            
            # But should have same content
            assert origins1 == origins2

    def test_cors_config_methods_immutability(self):
        """Test that allow_methods in config is a new list"""
        config = get_cors_config()
        
        # Modify the returned list
        config["allow_methods"].append("CUSTOM_METHOD")
        
        # Get a new config
        new_config = get_cors_config()
        
        # The new config should not be affected
        assert "CUSTOM_METHOD" not in new_config["allow_methods"]

    def test_cors_config_headers_immutability(self):
        """Test that allow_headers in config is a new list"""
        config = get_cors_config()
        
        # Modify the returned list
        config["allow_headers"].append("CUSTOM_HEADER")
        
        # Get a new config
        new_config = get_cors_config()
        
        # The new config should not be affected
        assert "CUSTOM_HEADER" not in new_config["allow_headers"] 