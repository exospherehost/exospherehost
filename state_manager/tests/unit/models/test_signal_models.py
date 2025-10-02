import pytest
from pydantic import ValidationError

from app.models.signal_models import PruneRequestModel, ReEnqueueAfterRequestModel, SignalResponseModel
from app.models.state_status_enum import StateStatusEnum


class TestPruneRequestModel:
    """Test cases for PruneRequestModel"""

    def test_prune_request_model_valid_data(self):
        """Test PruneRequestModel with valid data"""
        # Arrange & Act
        data = {"key": "value", "nested": {"data": "test"}}
        model = PruneRequestModel(data=data)
        
        # Assert
        assert model.data == data

    def test_prune_request_model_empty_data(self):
        """Test PruneRequestModel with empty data"""
        # Arrange & Act
        data = {}
        model = PruneRequestModel(data=data)
        
        # Assert
        assert model.data == data

    def test_prune_request_model_complex_data(self):
        """Test PruneRequestModel with complex nested data"""
        # Arrange & Act
        data = {
            "string": "test",
            "number": 42,
            "boolean": True,
            "list": [1, 2, 3],
            "nested": {
                "object": {
                    "deep": "value"
                }
            }
        }
        model = PruneRequestModel(data=data)
        
        # Assert
        assert model.data == data

    def test_prune_request_model_missing_data(self):
        """Test PruneRequestModel with missing data field"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            PruneRequestModel() # type: ignore
        
        assert "data" in str(exc_info.value)

    def test_prune_request_model_none_data(self):
        """Test PruneRequestModel with None data"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            PruneRequestModel(data=None) # type: ignore
        
        assert "data" in str(exc_info.value)


class TestReEnqueueAfterRequestModel:
    """Test cases for ReEnqueueAfterRequestModel"""

    def test_re_enqueue_after_request_model_valid_delay(self):
        """Test ReEnqueueAfterRequestModel with valid delay"""
        # Arrange & Act
        delay = 5000
        model = ReEnqueueAfterRequestModel(enqueue_after=delay)
        
        # Assert
        assert model.enqueue_after == delay

    def test_re_enqueue_after_request_model_zero_delay(self):
        """Test ReEnqueueAfterRequestModel with zero delay"""
        # Arrange & Act
        with pytest.raises(Exception):
            ReEnqueueAfterRequestModel(enqueue_after=0)

    def test_re_enqueue_after_request_model_negative_delay(self):
        """Test ReEnqueueAfterRequestModel with negative delay"""
        # Arrange & Act
        with pytest.raises(Exception):
            ReEnqueueAfterRequestModel(enqueue_after=-5000)
    
    def test_re_enqueue_after_request_model_large_delay(self):
        """Test ReEnqueueAfterRequestModel with large delay"""
        # Arrange & Act
        delay = 86400000  # 24 hours
        model = ReEnqueueAfterRequestModel(enqueue_after=delay)
        
        # Assert
        assert model.enqueue_after == delay

    def test_re_enqueue_after_request_model_missing_enqueue_after(self):
        """Test ReEnqueueAfterRequestModel with missing enqueue_after field"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ReEnqueueAfterRequestModel() # type: ignore
        
        assert "enqueue_after" in str(exc_info.value)

    def test_re_enqueue_after_request_model_none_enqueue_after(self):
        """Test ReEnqueueAfterRequestModel with None enqueue_after"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ReEnqueueAfterRequestModel(enqueue_after=None) # type: ignore
        
        assert "enqueue_after" in str(exc_info.value)

    def test_re_enqueue_after_request_model_string_enqueue_after(self):
        """Test ReEnqueueAfterRequestModel with string enqueue_after (should convert)"""
        # Arrange & Act
        delay = "5000"
        model = ReEnqueueAfterRequestModel(enqueue_after=delay) # type: ignore
        
        # Assert
        assert model.enqueue_after == 5000

    def test_re_enqueue_after_request_model_float_enqueue_after(self):
        """Test ReEnqueueAfterRequestModel with float enqueue_after (should convert)"""
        # Arrange & Act
        delay = 5000.0
        model = ReEnqueueAfterRequestModel(enqueue_after=delay) # type: ignore
        
        # Assert
        assert model.enqueue_after == 5000


class TestSignalResponseModel:
    """Test cases for SignalResponseModel"""

    def test_signal_response_model_valid_data(self):
        """Test SignalResponseModel with valid data"""
        # Arrange & Act
        enqueue_after = 1234567890
        status = StateStatusEnum.PRUNED
        model = SignalResponseModel(enqueue_after=enqueue_after, status=status)
        
        # Assert
        assert model.enqueue_after == enqueue_after
        assert model.status == status

    def test_signal_response_model_created_status(self):
        """Test SignalResponseModel with CREATED status"""
        # Arrange & Act
        enqueue_after = 1234567890
        status = StateStatusEnum.CREATED
        model = SignalResponseModel(enqueue_after=enqueue_after, status=status)
        
        # Assert
        assert model.enqueue_after == enqueue_after
        assert model.status == status

    def test_signal_response_model_zero_enqueue_after(self):
        """Test SignalResponseModel with zero enqueue_after"""
        # Arrange & Act
        enqueue_after = 0
        status = StateStatusEnum.PRUNED
        model = SignalResponseModel(enqueue_after=enqueue_after, status=status)
        
        # Assert
        assert model.enqueue_after == enqueue_after
        assert model.status == status

    def test_signal_response_model_large_enqueue_after(self):
        """Test SignalResponseModel with large enqueue_after"""
        # Arrange & Act
        enqueue_after = 9999999999999
        status = StateStatusEnum.CREATED
        model = SignalResponseModel(enqueue_after=enqueue_after, status=status)
        
        # Assert
        assert model.enqueue_after == enqueue_after
        assert model.status == status

    def test_signal_response_model_missing_enqueue_after(self):
        """Test SignalResponseModel with missing enqueue_after field"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            SignalResponseModel(status=StateStatusEnum.PRUNED) # type: ignore
        
        assert "enqueue_after" in str(exc_info.value)

    def test_signal_response_model_missing_status(self):
        """Test SignalResponseModel with missing status field"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            SignalResponseModel(enqueue_after=1234567890) # type: ignore
        
        assert "status" in str(exc_info.value)

    def test_signal_response_model_none_enqueue_after(self):
        """Test SignalResponseModel with None enqueue_after"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            SignalResponseModel(enqueue_after=None, status=StateStatusEnum.PRUNED) # type: ignore
        
        assert "enqueue_after" in str(exc_info.value)

    def test_signal_response_model_none_status(self):
        """Test SignalResponseModel with None status"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            SignalResponseModel(enqueue_after=1234567890, status=None) # type: ignore
        
        assert "status" in str(exc_info.value)

    def test_signal_response_model_string_enqueue_after(self):
        """Test SignalResponseModel with string enqueue_after (should convert)"""
        # Arrange & Act
        enqueue_after = "1234567890"
        status = StateStatusEnum.PRUNED
        model = SignalResponseModel(enqueue_after=enqueue_after, status=status) # type: ignore
        
        # Assert
        assert model.enqueue_after == 1234567890
        assert model.status == status

    def test_signal_response_model_all_status_enum_values(self):
        """Test SignalResponseModel with all possible status enum values"""
        # Arrange
        enqueue_after = 1234567890
        all_statuses = [
            StateStatusEnum.CREATED,
            StateStatusEnum.QUEUED,
            StateStatusEnum.EXECUTED,
            StateStatusEnum.ERRORED,
            StateStatusEnum.SUCCESS,
            StateStatusEnum.NEXT_CREATED_ERROR,
            StateStatusEnum.PRUNED
        ]
        
        for status in all_statuses:
            # Act
            model = SignalResponseModel(enqueue_after=enqueue_after, status=status)
            
            # Assert
            assert model.enqueue_after == enqueue_after
            assert model.status == status

    def test_signal_response_model_json_serialization(self):
        """Test SignalResponseModel JSON serialization"""
        # Arrange
        enqueue_after = 1234567890
        status = StateStatusEnum.PRUNED
        model = SignalResponseModel(enqueue_after=enqueue_after, status=status)
        
        # Act
        json_data = model.model_dump()
        
        # Assert
        assert json_data["enqueue_after"] == enqueue_after
        assert json_data["status"] == status.value

    def test_signal_response_model_json_deserialization(self):
        """Test SignalResponseModel JSON deserialization"""
        # Arrange
        json_data = {
            "enqueue_after": 1234567890,
            "status": "PRUNED"
        }
        
        # Act
        model = SignalResponseModel(**json_data)
        
        # Assert
        assert model.enqueue_after == 1234567890
        assert model.status == StateStatusEnum.PRUNED 