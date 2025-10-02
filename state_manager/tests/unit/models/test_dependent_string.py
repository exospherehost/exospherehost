import pytest
from app.models.dependent_string import DependentString, Dependent


class TestDependentString:
    """Additional test cases for DependentString model to improve coverage"""

    def test_generate_string_with_unset_dependent_value(self):
        """Test generate_string method fails when dependent value is not set"""
        dependent_string = DependentString(
            head="prefix_",
            dependents={
                0: Dependent(identifier="node1", field="output1", tail="_suffix", value=None)
            }
        )
        
        with pytest.raises(ValueError, match="Dependent value is not set for:"):
            dependent_string.generate_string()

    def test_build_mapping_key_to_dependent_already_built(self):
        """Test _build_mapping_key_to_dependent when mapping already exists"""
        dependent_string = DependentString(
            head="prefix_",
            dependents={
                0: Dependent(identifier="node1", field="output1", tail="_suffix")
            }
        )
        
        # Build mapping first time
        dependent_string._build_mapping_key_to_dependent()
        original_mapping = dependent_string._mapping_key_to_dependent.copy()
        
        # Call again - should not rebuild
        dependent_string._build_mapping_key_to_dependent()
        assert dependent_string._mapping_key_to_dependent == original_mapping

    def test_set_value_multiple_dependents_same_key(self):
        """Test set_value method with multiple dependents having same identifier and field"""
        dependent1 = Dependent(identifier="node1", field="output1", tail="_suffix1")
        dependent2 = Dependent(identifier="node1", field="output1", tail="_suffix2")
        
        dependent_string = DependentString(
            head="prefix_",
            dependents={0: dependent1, 1: dependent2}
        )
        
        dependent_string.set_value("node1", "output1", "test_value")
        
        assert dependent1.value == "test_value"
        assert dependent2.value == "test_value"

    def test_get_identifier_field_multiple_mappings(self):
        """Test get_identifier_field method with multiple identifier-field mappings"""
        dependent_string = DependentString(
            head="prefix_",
            dependents={
                0: Dependent(identifier="node1", field="output1", tail="_suffix1"),
                1: Dependent(identifier="node2", field="output2", tail="_suffix2"),
                2: Dependent(identifier="node1", field="output3", tail="_suffix3")
            }
        )
        
        identifier_fields = dependent_string.get_identifier_field()
        
        # Should have 3 unique identifier-field pairs
        expected_pairs = [("node1", "output1"), ("node2", "output2"), ("node1", "output3")]
        assert len(identifier_fields) == 3
        assert set(identifier_fields) == set(expected_pairs)


    def test_create_dependent_string_with_store_dependency(self):
        """Test create_dependent_string method with store dependency"""
        syntax_string = "prefix_${{store.config_key}}_suffix"
        
        dependent_string = DependentString.create_dependent_string(syntax_string)
        
        assert dependent_string.head == "prefix_"
        assert len(dependent_string.dependents) == 1
        assert 0 in dependent_string.dependents
        
        dependent = dependent_string.dependents[0]
        assert dependent.identifier == "store"
        assert dependent.field == "config_key"
        assert dependent.tail == "_suffix"
        assert dependent.value is None
