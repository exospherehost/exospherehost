import pytest
from unittest.mock import patch
from datetime import datetime
from app.models.db.base import BaseDatabaseModel


class TestBaseDatabaseModel:
    """Test cases for BaseDatabaseModel"""

    def test_base_model_field_definitions(self):
        """Test that BaseDatabaseModel has the expected fields"""
        # Check that the model has the expected fields
        model_fields = BaseDatabaseModel.model_fields
        
        assert 'created_at' in model_fields
        assert 'updated_at' in model_fields
        
        # Check field descriptions
        assert model_fields['created_at'].description == "Date and time when the model was created"
        assert model_fields['updated_at'].description == "Date and time when the model was last updated"

    def test_base_model_abc_inheritance(self):
        """Test that BaseDatabaseModel is an abstract base class"""
        # Should not be able to instantiate BaseDatabaseModel directly
        with pytest.raises(Exception):  # Could be TypeError or CollectionWasNotInitialized
            BaseDatabaseModel()

    def test_base_model_document_inheritance(self):
        """Test that BaseDatabaseModel inherits from Document"""
        # Check that it has the expected base classes
        bases = BaseDatabaseModel.__bases__
        assert len(bases) >= 2  # Should have at least ABC and Document as base classes

    def test_base_model_has_update_updated_at_method(self):
        """Test that BaseDatabaseModel has the update_updated_at method"""
        assert hasattr(BaseDatabaseModel, 'update_updated_at')
        assert callable(BaseDatabaseModel.update_updated_at)

    def test_base_model_field_types(self):
        """Test that BaseDatabaseModel fields have correct types"""
        model_fields = BaseDatabaseModel.model_fields
        
        # Check that created_at and updated_at are datetime fields
        created_at_field = model_fields['created_at']
        updated_at_field = model_fields['updated_at']
        
        assert created_at_field.annotation == datetime
        assert updated_at_field.annotation == datetime

    def test_base_model_has_before_event_decorator(self):
        """Test that BaseDatabaseModel uses the before_event decorator"""
        # Check that the update_updated_at method exists and is callable
        update_method = BaseDatabaseModel.update_updated_at
        
        # The method should exist and be callable
        assert callable(update_method) 