import os
import base64
import pytest
from unittest.mock import patch, MagicMock

from app.utils.encrypter import Encrypter, get_encrypter

from dotenv import load_dotenv
load_dotenv()



class TestEncrypter:
    """Test cases for Encrypter class"""

    def setup_method(self):
        """Reset the global encrypter instance before each test"""
        import app.utils.encrypter
        app.utils.encrypter._encrypter_instance = None

    def teardown_method(self):
        """Clean up after each test"""
        import app.utils.encrypter
        app.utils.encrypter._encrypter_instance = None

    def test_generate_key_returns_valid_base64_key(self):
        """Test that generate_key returns a valid base64 encoded key"""
        key = Encrypter.generate_key()
        
        # Should be base64 encoded string
        assert isinstance(key, str)
        # Should be able to decode without exception
        decoded_key = base64.urlsafe_b64decode(key)
        # Should be 32 bytes (256 bits)
        assert len(decoded_key) == 32

    def test_generate_key_creates_different_keys(self):
        """Test that generate_key creates different keys each time"""
        key1 = Encrypter.generate_key()
        key2 = Encrypter.generate_key()
        
        assert key1 != key2

    @patch.dict(os.environ, {'SECRETS_ENCRYPTION_KEY': base64.urlsafe_b64encode(b'x' * 32).decode()})
    def test_encrypt_returns_base64_string(self):
        """Test that encrypt returns a base64 encoded string"""
        encrypter = Encrypter()
        secret = "my secret message"
        
        encrypted = encrypter.encrypt(secret)
        
        assert isinstance(encrypted, str)
        # Should be able to decode without exception
        base64.urlsafe_b64decode(encrypted)

    @patch.dict(os.environ, {'SECRETS_ENCRYPTION_KEY': base64.urlsafe_b64encode(b'x' * 32).decode()})
    def test_encrypt_different_secrets_produce_different_results(self):
        """Test that different secrets produce different encrypted results"""
        encrypter = Encrypter()
        
        encrypted1 = encrypter.encrypt("secret1")
        encrypted2 = encrypter.encrypt("secret2")
        
        assert encrypted1 != encrypted2

    @patch.dict(os.environ, {'SECRETS_ENCRYPTION_KEY': base64.urlsafe_b64encode(b'x' * 32).decode()})
    def test_encrypt_same_secret_produces_different_results(self):
        """Test that same secret produces different encrypted results due to nonce"""
        encrypter = Encrypter()
        secret = "same secret"
        
        encrypted1 = encrypter.encrypt(secret)
        encrypted2 = encrypter.encrypt(secret)
        
        # Should be different due to different nonces
        assert encrypted1 != encrypted2

    @patch.dict(os.environ, {'SECRETS_ENCRYPTION_KEY': base64.urlsafe_b64encode(b'x' * 32).decode()})
    def test_decrypt_returns_original_secret(self):
        """Test that decrypt returns the original secret"""
        encrypter = Encrypter()
        original_secret = "my secret message"
        
        encrypted = encrypter.encrypt(original_secret)
        decrypted = encrypter.decrypt(encrypted)
        
        assert decrypted == original_secret

    @patch.dict(os.environ, {'SECRETS_ENCRYPTION_KEY': base64.urlsafe_b64encode(b'x' * 32).decode()})
    def test_encrypt_decrypt_roundtrip_with_special_characters(self):
        """Test encrypt/decrypt with special characters"""
        encrypter = Encrypter()
        original_secret = "Special chars: !@#$%^&*()_+-={}[]|\\:;\"'<>?,./"
        
        encrypted = encrypter.encrypt(original_secret)
        decrypted = encrypter.decrypt(encrypted)
        
        assert decrypted == original_secret

    @patch.dict(os.environ, {'SECRETS_ENCRYPTION_KEY': base64.urlsafe_b64encode(b'x' * 32).decode()})
    def test_encrypt_decrypt_roundtrip_with_unicode(self):
        """Test encrypt/decrypt with unicode characters"""
        encrypter = Encrypter()
        original_secret = "Unicode: 你好世界 🌍 ñáéíóú"
        
        encrypted = encrypter.encrypt(original_secret)
        decrypted = encrypter.decrypt(encrypted)
        
        assert decrypted == original_secret

    @patch.dict(os.environ, {'SECRETS_ENCRYPTION_KEY': base64.urlsafe_b64encode(b'x' * 32).decode()})
    def test_encrypt_decrypt_empty_string(self):
        """Test encrypt/decrypt with empty string"""
        encrypter = Encrypter()
        original_secret = ""
        
        encrypted = encrypter.encrypt(original_secret)
        decrypted = encrypter.decrypt(encrypted)
        
        assert decrypted == original_secret

    @patch.dict(os.environ, {'SECRETS_ENCRYPTION_KEY': base64.urlsafe_b64encode(b'x' * 32).decode()})
    def test_decrypt_with_invalid_base64_raises_error(self):
        """Test decrypt with invalid base64 data raises exception"""
        encrypter = Encrypter()
        
        with pytest.raises(Exception):  # base64 decode error
            encrypter.decrypt("invalid-base64!@#")

    @patch.dict(os.environ, {'SECRETS_ENCRYPTION_KEY': base64.urlsafe_b64encode(b'x' * 32).decode()})
    def test_decrypt_with_corrupted_data_raises_error(self):
        """Test decrypt with corrupted encrypted data raises exception"""
        encrypter = Encrypter()
        
        # Create invalid encrypted data (too short)
        invalid_encrypted = base64.urlsafe_b64encode(b'too_short').decode()
        
        with pytest.raises(Exception):  # AESGCM decrypt error
            encrypter.decrypt(invalid_encrypted)


class TestGetEncrypter:
    """Test cases for get_encrypter function"""

    def setup_method(self):
        """Reset the global encrypter instance before each test"""
        import app.utils.encrypter
        app.utils.encrypter._encrypter_instance = None

    def teardown_method(self):
        """Clean up after each test"""
        import app.utils.encrypter
        app.utils.encrypter._encrypter_instance = None

    @patch.dict(os.environ, {'SECRETS_ENCRYPTION_KEY': base64.urlsafe_b64encode(b'x' * 32).decode()})
    def test_get_encrypter_returns_encrypter_instance(self):
        """Test get_encrypter returns an Encrypter instance"""
        encrypter = get_encrypter()
        
        assert isinstance(encrypter, Encrypter)

    @patch.dict(os.environ, {'SECRETS_ENCRYPTION_KEY': base64.urlsafe_b64encode(b'x' * 32).decode()})
    def test_get_encrypter_returns_same_instance_singleton(self):
        """Test get_encrypter returns the same instance (singleton pattern)"""
        encrypter1 = get_encrypter()
        encrypter2 = get_encrypter()
        
        assert encrypter1 is encrypter2

    @patch.dict(os.environ, {'SECRETS_ENCRYPTION_KEY': base64.urlsafe_b64encode(b'x' * 32).decode()})
    def test_get_encrypter_functional_test(self):
        """Test that get_encrypter returns a functional encrypter"""
        encrypter = get_encrypter()
        original_secret = "functional test secret"
        
        encrypted = encrypter.encrypt(original_secret)
        decrypted = encrypter.decrypt(encrypted)
        
        assert decrypted == original_secret

    @patch('app.utils.encrypter.Encrypter')
    @patch.dict(os.environ, {'SECRETS_ENCRYPTION_KEY': base64.urlsafe_b64encode(b'x' * 32).decode()})
    def test_get_encrypter_creates_instance_only_once(self, mock_encrypter_class):
        """Test that get_encrypter creates Encrypter instance only once"""
        mock_instance = MagicMock()
        mock_encrypter_class.return_value = mock_instance
        
        # Call get_encrypter multiple times
        result1 = get_encrypter()
        result2 = get_encrypter()
        result3 = get_encrypter()
        
        # Encrypter constructor should be called only once
        assert mock_encrypter_class.call_count == 1
        # All calls should return the same instance
        assert result1 is result2 is result3 is mock_instance