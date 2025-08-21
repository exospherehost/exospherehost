import pytest
from unittest.mock import MagicMock, patch
import base64
from app.models.db.graph_template_model import GraphTemplate
from app.models.graph_template_validation_status import GraphTemplateValidationStatus


class TestGraphTemplate:
    """Test cases for GraphTemplate model"""

    def test_validate_secrets_valid(self):
        """Test validation of valid secrets"""
        valid_secrets = {
            "secret1": "valid_encrypted_string_that_is_long_enough_for_testing_32_chars",
            "secret2": "another_valid_encrypted_string_that_is_long_enough_for_testing_32",
        }
        
        # Mock base64 decoding to succeed
        with patch("base64.urlsafe_b64decode", return_value=b"x" * 20):
            result = GraphTemplate.validate_secrets(valid_secrets)
            
            assert result == valid_secrets

    def test_validate_secrets_empty_name(self):
        """Test validation with empty secret name"""
        invalid_secrets = {"": "valid_value"}
        
        with pytest.raises(ValueError, match="Secrets cannot be empty"):
            GraphTemplate.validate_secrets(invalid_secrets)

    def test_validate_secrets_empty_value(self):
        """Test validation with empty secret value"""
        invalid_secrets = {"secret1": ""}
        
        with pytest.raises(ValueError, match="Secrets cannot be empty"):
            GraphTemplate.validate_secrets(invalid_secrets)

    def test_validate_secret_value_too_short(self):
        """Test validation of secret value that's too short"""
        short_value = "short"
        
        with pytest.raises(ValueError, match="Value appears to be too short for an encrypted string"):
            GraphTemplate._validate_secret_value(short_value)

    def test_validate_secret_value_invalid_base64(self):
        """Test validation of secret value with invalid base64"""
        invalid_base64 = "invalid_base64_string_that_is_long_enough_but_not_valid_base64"
        
        with pytest.raises(ValueError, match="Value is not valid URL-safe base64 encoded"):
            GraphTemplate._validate_secret_value(invalid_base64)

    def test_validate_secret_value_valid(self):
        """Test validation of valid secret value"""
        # Create a valid base64 string that decodes to at least 12 bytes and is long enough
        valid_bytes = b"x" * 20
        valid_base64 = base64.urlsafe_b64encode(valid_bytes).decode()
        # Pad to make it at least 32 characters
        padded_base64 = valid_base64 + "x" * (32 - len(valid_base64))
        
        # Should not raise any exception
        GraphTemplate._validate_secret_value(padded_base64)

    def test_validate_secrets_with_long_valid_strings(self):
        """Test validation with properly long secret values"""
        long_secrets = {
            "secret1": "x" * 50,  # 50 characters
            "secret2": "y" * 100,  # 100 characters
        }
        
        # Mock base64 decoding to succeed
        with patch("base64.urlsafe_b64decode", return_value=b"x" * 20):
            result = GraphTemplate.validate_secrets(long_secrets)
            
            assert result == long_secrets

    def test_validate_secret_value_exactly_32_chars(self):
        """Test validation with exactly 32 character string"""
        exactly_32 = "x" * 32
        
        # Mock base64 decoding to succeed
        with patch("base64.urlsafe_b64decode", return_value=b"x" * 20):
            # Should not raise exception
            GraphTemplate._validate_secret_value(exactly_32)

    def test_validate_secret_value_31_chars_fails(self):
        """Test validation with 31 character string fails"""
        exactly_31 = "x" * 31
        
        with pytest.raises(ValueError, match="Value appears to be too short for an encrypted string"):
            GraphTemplate._validate_secret_value(exactly_31)

    def test_validate_secret_value_base64_decode_exception(self):
        """Test validation when base64 decoding raises exception"""
        invalid_base64 = "invalid_base64_string_that_is_long_enough_but_not_valid_base64"
        
        with pytest.raises(ValueError, match="Value is not valid URL-safe base64 encoded"):
            GraphTemplate._validate_secret_value(invalid_base64)

    def test_validate_secret_value_decoded_exactly_12_bytes(self):
        """Test validation with decoded value exactly 12 bytes"""
        # Create a valid base64 string that decodes to exactly 12 bytes and is long enough
        exactly_12_bytes = b"x" * 12
        base64_string = base64.urlsafe_b64encode(exactly_12_bytes).decode()
        # Pad to make it at least 32 characters
        padded_base64 = base64_string + "x" * (32 - len(base64_string))
        
        # Should not raise exception
        GraphTemplate._validate_secret_value(padded_base64)