import pytest
from app.models.node_template_model import NodeTemplate, Unites, UnitesStrategyEnum
from app.models.dependent_string import DependentString


class TestNodeTemplate:
    """Test cases for NodeTemplate model"""

    def test_validate_identifier_reserved_word_store(self):
        """Test validation fails for reserved word 'store' as identifier"""
        with pytest.raises(ValueError, match="Node identifier cannot be reserved word 'store'"):
            NodeTemplate(
                node_name="test_node",
                namespace="test_ns",
                identifier="store",
                inputs={"input1": "value1"},
                next_nodes=[],
                unites=None
            )

    def test_get_dependent_strings_with_non_string_input(self):
        """Test get_dependent_strings method with non-string input"""
        node = NodeTemplate(
            node_name="test_node",
            namespace="test_ns", 
            identifier="test_id",
            inputs={"input1": "valid_string", "input2": 123},
            next_nodes=[],
            unites=None
        )
        
        with pytest.raises(ValueError, match="Input 123 is not a string"):
            node.get_dependent_strings()

    def test_get_dependent_strings_valid(self):
        """Test get_dependent_strings method with valid string inputs"""
        node = NodeTemplate(
            node_name="test_node",
            namespace="test_ns",
            identifier="test_id", 
            inputs={
                "input1": "simple_string",
                "input2": "${{node1.outputs.field1}}",
                "input3": "prefix_${{store.key1}}_suffix"
            },
            next_nodes=[],
            unites=None
        )
        
        dependent_strings = node.get_dependent_strings()
        assert len(dependent_strings) == 3
        assert all(isinstance(ds, DependentString) for ds in dependent_strings)


class TestUnites:
    """Test cases for Unites model"""

    def test_unites_creation_default_strategy(self):
        """Test creating Unites with default strategy"""
        unites = Unites(identifier="test_id")
        assert unites.identifier == "test_id"
        assert unites.strategy == UnitesStrategyEnum.ALL_SUCCESS

    def test_unites_creation_custom_strategy(self):
        """Test creating Unites with custom strategy"""
        unites = Unites(identifier="test_id", strategy=UnitesStrategyEnum.ALL_DONE)
        assert unites.identifier == "test_id"
        assert unites.strategy == UnitesStrategyEnum.ALL_DONE


class TestUnitesStrategyEnum:
    """Test cases for UnitesStrategyEnum"""

    def test_enum_values(self):
        """Test enum values are correct"""
        assert UnitesStrategyEnum.ALL_SUCCESS == "ALL_SUCCESS"
        assert UnitesStrategyEnum.ALL_DONE == "ALL_DONE"
