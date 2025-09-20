import pytest
from pydantic import ValidationError

from app.models.manual_retry import ManualRetryRequestModel, ManualRetryResponseModel
from app.models.state_status_enum import StateStatusEnum


class TestManualRetryRequestModel:
    """Test cases for ManualRetryRequestModel"""

    def test_manual_retry_request_model_valid_data(self):
        """Test ManualRetryRequestModel with valid fanout_id"""
        # Arrange & Act
        fanout_id = "test-fanout-id-123"
        model = ManualRetryRequestModel(fanout_id=fanout_id)
        
        # Assert
        assert model.fanout_id == fanout_id

    def test_manual_retry_request_model_empty_fanout_id(self):
        """Test ManualRetryRequestModel with empty fanout_id"""
        # Arrange & Act
        fanout_id = ""
        model = ManualRetryRequestModel(fanout_id=fanout_id)
        
        # Assert
        assert model.fanout_id == fanout_id

    def test_manual_retry_request_model_uuid_fanout_id(self):
        """Test ManualRetryRequestModel with UUID fanout_id"""
        # Arrange & Act
        fanout_id = "550e8400-e29b-41d4-a716-446655440000"
        model = ManualRetryRequestModel(fanout_id=fanout_id)
        
        # Assert
        assert model.fanout_id == fanout_id

    def test_manual_retry_request_model_long_fanout_id(self):
        """Test ManualRetryRequestModel with long fanout_id"""
        # Arrange & Act
        fanout_id = "a" * 1000  # Very long string
        model = ManualRetryRequestModel(fanout_id=fanout_id)
        
        # Assert
        assert model.fanout_id == fanout_id

    def test_manual_retry_request_model_special_characters_fanout_id(self):
        """Test ManualRetryRequestModel with special characters in fanout_id"""
        # Arrange & Act
        fanout_id = "test-fanout@#$%^&*()_+-={}[]|\\:;\"'<>?,./"
        model = ManualRetryRequestModel(fanout_id=fanout_id)
        
        # Assert
        assert model.fanout_id == fanout_id

    def test_manual_retry_request_model_missing_fanout_id(self):
        """Test ManualRetryRequestModel with missing fanout_id field"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ManualRetryRequestModel() # type: ignore
        
        assert "fanout_id" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)

    def test_manual_retry_request_model_none_fanout_id(self):
        """Test ManualRetryRequestModel with None fanout_id"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ManualRetryRequestModel(fanout_id=None) # type: ignore
        
        assert "fanout_id" in str(exc_info.value)

    def test_manual_retry_request_model_numeric_fanout_id(self):
        """Test ManualRetryRequestModel with numeric fanout_id (should fail validation)"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ManualRetryRequestModel(fanout_id=12345) # type: ignore
        
        assert "string_type" in str(exc_info.value)

    def test_manual_retry_request_model_dict_representation(self):
        """Test ManualRetryRequestModel dict representation"""
        # Arrange & Act
        fanout_id = "test-fanout-id"
        model = ManualRetryRequestModel(fanout_id=fanout_id)
        
        # Assert
        expected_dict = {"fanout_id": fanout_id}
        assert model.model_dump() == expected_dict

    def test_manual_retry_request_model_json_serialization(self):
        """Test ManualRetryRequestModel JSON serialization"""
        # Arrange & Act
        fanout_id = "test-fanout-id"
        model = ManualRetryRequestModel(fanout_id=fanout_id)
        
        # Assert
        json_str = model.model_dump_json()
        assert f'"fanout_id":"{fanout_id}"' in json_str


class TestManualRetryResponseModel:
    """Test cases for ManualRetryResponseModel"""

    def test_manual_retry_response_model_valid_data(self):
        """Test ManualRetryResponseModel with valid data"""
        # Arrange & Act
        state_id = "507f1f77bcf86cd799439011"
        status = StateStatusEnum.CREATED
        model = ManualRetryResponseModel(id=state_id, status=status)
        
        # Assert
        assert model.id == state_id
        assert model.status == status

    def test_manual_retry_response_model_all_status_types(self):
        """Test ManualRetryResponseModel with all possible status values"""
        # Arrange & Act & Assert
        state_id = "507f1f77bcf86cd799439011"
        
        for status in StateStatusEnum:
            model = ManualRetryResponseModel(id=state_id, status=status)
            assert model.id == state_id
            assert model.status == status

    def test_manual_retry_response_model_created_status(self):
        """Test ManualRetryResponseModel with CREATED status"""
        # Arrange & Act
        state_id = "507f1f77bcf86cd799439011"
        status = StateStatusEnum.CREATED
        model = ManualRetryResponseModel(id=state_id, status=status)
        
        # Assert
        assert model.id == state_id
        assert model.status == StateStatusEnum.CREATED

    def test_manual_retry_response_model_retry_created_status(self):
        """Test ManualRetryResponseModel with RETRY_CREATED status"""
        # Arrange & Act
        state_id = "507f1f77bcf86cd799439011"
        status = StateStatusEnum.RETRY_CREATED
        model = ManualRetryResponseModel(id=state_id, status=status)
        
        # Assert
        assert model.id == state_id
        assert model.status == StateStatusEnum.RETRY_CREATED

    def test_manual_retry_response_model_missing_id(self):
        """Test ManualRetryResponseModel with missing id field"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ManualRetryResponseModel(status=StateStatusEnum.CREATED) # type: ignore
        
        assert "id" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)

    def test_manual_retry_response_model_missing_status(self):
        """Test ManualRetryResponseModel with missing status field"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ManualRetryResponseModel(id="507f1f77bcf86cd799439011") # type: ignore
        
        assert "status" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)

    def test_manual_retry_response_model_none_id(self):
        """Test ManualRetryResponseModel with None id"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ManualRetryResponseModel(id=None, status=StateStatusEnum.CREATED) # type: ignore
        
        assert "id" in str(exc_info.value)

    def test_manual_retry_response_model_none_status(self):
        """Test ManualRetryResponseModel with None status"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ManualRetryResponseModel(id="507f1f77bcf86cd799439011", status=None) # type: ignore
        
        assert "status" in str(exc_info.value)

    def test_manual_retry_response_model_invalid_status(self):
        """Test ManualRetryResponseModel with invalid status"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ManualRetryResponseModel(id="507f1f77bcf86cd799439011", status="INVALID_STATUS") # type: ignore
        
        assert "status" in str(exc_info.value)

    def test_manual_retry_response_model_numeric_id(self):
        """Test ManualRetryResponseModel with numeric id (should fail validation)"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ManualRetryResponseModel(id=12345, status=StateStatusEnum.CREATED) # type: ignore
        
        assert "string_type" in str(exc_info.value)

    def test_manual_retry_response_model_dict_representation(self):
        """Test ManualRetryResponseModel dict representation"""
        # Arrange & Act
        state_id = "507f1f77bcf86cd799439011"
        status = StateStatusEnum.CREATED
        model = ManualRetryResponseModel(id=state_id, status=status)
        
        # Assert
        expected_dict = {"id": state_id, "status": status}
        assert model.model_dump() == expected_dict

    def test_manual_retry_response_model_json_serialization(self):
        """Test ManualRetryResponseModel JSON serialization"""
        # Arrange & Act
        state_id = "507f1f77bcf86cd799439011"
        status = StateStatusEnum.CREATED
        model = ManualRetryResponseModel(id=state_id, status=status)
        
        # Assert
        json_str = model.model_dump_json()
        assert f'"id":"{state_id}"' in json_str
        assert f'"status":"{status.value}"' in json_str

    def test_manual_retry_response_model_empty_id(self):
        """Test ManualRetryResponseModel with empty string id"""
        # Arrange & Act
        state_id = ""
        status = StateStatusEnum.CREATED
        model = ManualRetryResponseModel(id=state_id, status=status)
        
        # Assert
        assert model.id == state_id
        assert model.status == status

    def test_manual_retry_response_model_long_id(self):
        """Test ManualRetryResponseModel with very long id"""
        # Arrange & Act
        state_id = "a" * 1000  # Very long string
        status = StateStatusEnum.CREATED
        model = ManualRetryResponseModel(id=state_id, status=status)
        
        # Assert
        assert model.id == state_id
        assert model.status == status 