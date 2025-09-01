import pytest
from app.models.store_config_model import StoreConfig


class TestStoreConfig:
    """Test cases for StoreConfig model"""

    def test_store_config_creation_defaults(self):
        """Test creating StoreConfig with default values"""
        config = StoreConfig()
        assert config.required_keys == []
        assert config.default_values == {}

    def test_store_config_creation_with_values(self):
        """Test creating StoreConfig with provided values"""
        config = StoreConfig(
            required_keys=["key1", "key2"],
            default_values={"default_key": "default_value"}
        )
        assert config.required_keys == ["key1", "key2"]
        assert config.default_values == {"default_key": "default_value"}

    def test_validate_required_keys_valid(self):
        """Test validation of valid required keys"""
        valid_keys = ["key1", "key2", "key3"]
        result = StoreConfig.validate_required_keys(valid_keys) # type: ignore
        assert result == valid_keys

    def test_validate_required_keys_with_whitespace(self):
        """Test validation trims whitespace from keys"""
        keys_with_whitespace = [" key1 ", "  key2  ", "key3"]
        result = StoreConfig.validate_required_keys(keys_with_whitespace) # type: ignore
        assert result == ["key1", "key2", "key3"]

    def test_validate_required_keys_empty_string(self):
        """Test validation fails for empty string keys"""
        invalid_keys = ["key1", "", "key3"]
        with pytest.raises(ValueError, match="Key cannot be empty or contain only whitespace"):
            StoreConfig.validate_required_keys(invalid_keys) # type: ignore

    def test_validate_required_keys_whitespace_only(self):
        """Test validation fails for whitespace-only keys"""
        invalid_keys = ["key1", "   ", "key3"]
        with pytest.raises(ValueError, match="Key cannot be empty or contain only whitespace"):
            StoreConfig.validate_required_keys(invalid_keys) # type: ignore

    def test_validate_required_keys_none_value(self):
        """Test validation fails for None keys"""
        invalid_keys = ["key1", None, "key3"]
        with pytest.raises(ValueError, match="Key cannot be empty or contain only whitespace"):
            StoreConfig.validate_required_keys(invalid_keys) # type: ignore

    def test_validate_required_keys_dot_character(self):
        """Test validation fails for keys containing dot character"""
        invalid_keys = ["key1", "key.with.dot", "key3"]
        with pytest.raises(ValueError, match="Key 'key.with.dot' cannot contain '.' character"):
            StoreConfig.validate_required_keys(invalid_keys) # type: ignore

    def test_validate_required_keys_duplicates(self):
        """Test validation fails for duplicate keys"""
        invalid_keys = ["key1", "key2", "key1"]
        with pytest.raises(ValueError, match="Key 'key1' is duplicated"):
            StoreConfig.validate_required_keys(invalid_keys) # type: ignore

    def test_validate_required_keys_duplicates_after_trim(self):
        """Test validation fails for duplicate keys after trimming"""
        invalid_keys = ["key1", " key1 ", "key2"]
        with pytest.raises(ValueError, match="Key 'key1' is duplicated"):
            StoreConfig.validate_required_keys(invalid_keys) # type: ignore

    def test_validate_required_keys_multiple_errors(self):
        """Test validation collects multiple errors"""
        invalid_keys = ["", "key.dot", "key1", "key1", "   "]
        with pytest.raises(ValueError) as exc_info:
            StoreConfig.validate_required_keys(invalid_keys) # type: ignore
        
        error_message = str(exc_info.value)
        assert "Key cannot be empty or contain only whitespace" in error_message
        assert "Key 'key.dot' cannot contain '.' character" in error_message
        assert "Key 'key1' is duplicated" in error_message

    def test_validate_default_values_valid(self):
        """Test validation of valid default values"""
        valid_values = {"key1": "value1", "key2": "value2"}
        result = StoreConfig.validate_default_values(valid_values) # type: ignore
        assert result == valid_values

    def test_validate_default_values_with_whitespace(self):
        """Test validation trims whitespace from keys"""
        values_with_whitespace = {" key1 ": "value1", "  key2  ": "value2"}
        result = StoreConfig.validate_default_values(values_with_whitespace) # type: ignore
        assert result == {"key1": "value1", "key2": "value2"}

    def test_validate_default_values_empty_key(self):
        """Test validation fails for empty string keys"""
        invalid_values = {"key1": "value1", "": "value2"}
        with pytest.raises(ValueError, match="Key cannot be empty or contain only whitespace"):
            StoreConfig.validate_default_values(invalid_values) # type: ignore

    def test_validate_default_values_whitespace_only_key(self):
        """Test validation fails for whitespace-only keys"""
        invalid_values = {"key1": "value1", "   ": "value2"}
        with pytest.raises(ValueError, match="Key cannot be empty or contain only whitespace"):
            StoreConfig.validate_default_values(invalid_values) # type: ignore

    def test_validate_default_values_none_key(self):
        """Test validation fails for None keys"""
        invalid_values = {"key1": "value1", None: "value2"}
        with pytest.raises(ValueError, match="Key cannot be empty or contain only whitespace"):
            StoreConfig.validate_default_values(invalid_values) # type: ignore

    def test_validate_default_values_dot_character(self):
        """Test validation fails for keys containing dot character"""
        invalid_values = {"key1": "value1", "key.with.dot": "value2"}
        with pytest.raises(ValueError, match="Key 'key.with.dot' cannot contain '.' character"):
            StoreConfig.validate_default_values(invalid_values) # type: ignore

    def test_validate_default_values_duplicates_after_trim(self):
        """Test validation fails for duplicate keys after trimming"""
        values_with_duplicates_after_trim = {" key1 ": "value1", "key1": "value2"}
        with pytest.raises(ValueError, match="Key 'key1' is duplicated"):
            StoreConfig.validate_default_values(values_with_duplicates_after_trim) # type: ignore

    def test_validate_default_values_multiple_errors(self):
        """Test validation collects multiple errors"""
        invalid_values = {"": "value1", "key.dot": "value2", " key1 ": "value3", "key1": "duplicate"}
        with pytest.raises(ValueError) as exc_info:
            StoreConfig.validate_default_values(invalid_values) # type: ignore
        
        error_message = str(exc_info.value)
        assert "Key cannot be empty or contain only whitespace" in error_message
        assert "Key 'key.dot' cannot contain '.' character" in error_message
        assert "Key 'key1' is duplicated" in error_message

    def test_store_config_integration(self):
        """Test creating StoreConfig with validation"""
        # Test successful creation
        config = StoreConfig(
            required_keys=["  key1  ", "key2"],
            default_values={"  default1  ": "value1", "default2": "value2"}
        )
        assert config.required_keys == ["key1", "key2"]
        assert config.default_values == {"default1": "value1", "default2": "value2"}

        # Test failure case
        with pytest.raises(ValueError):
            StoreConfig(
                required_keys=["key1", "key.invalid"],
                default_values={"valid": "value"}
            )
