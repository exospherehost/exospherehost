import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from beanie import PydanticObjectId
from typing import cast
from app.tasks.create_next_states import (
    mark_success_states,
    check_unites_satisfied,
    get_dependents,
    validate_dependencies,
    Dependent,
    DependentString
)
from app.models.db.state import State
from app.models.state_status_enum import StateStatusEnum
from app.models.node_template_model import NodeTemplate, Unites
from pydantic import BaseModel


class TestDependent:
    """Test cases for Dependent model"""

    def test_dependent_creation(self):
        """Test creating a Dependent instance"""
        dependent = Dependent(
            identifier="test_node",
            field="output_field",
            tail="remaining_text"
        )
        
        assert dependent.identifier == "test_node"
        assert dependent.field == "output_field"
        assert dependent.tail == "remaining_text"
        assert dependent.value is None

    def test_dependent_with_value(self):
        """Test creating a Dependent instance with a value"""
        dependent = Dependent(
            identifier="test_node",
            field="output_field",
            tail="remaining_text",
            value="test_value"
        )
        
        assert dependent.value == "test_value"


class TestDependentString:
    """Test cases for DependentString model"""

    def test_dependent_string_creation_empty(self):
        """Test creating an empty DependentString"""
        dependent_string = DependentString(head="base_text", dependents={})
        
        assert dependent_string.head == "base_text"
        assert dependent_string.dependents == {}

    def test_dependent_string_creation_with_dependents(self):
        """Test creating a DependentString with dependents"""
        dependents = {
            0: Dependent(identifier="node1", field="field1", tail="tail1", value="value1"),
            1: Dependent(identifier="node2", field="field2", tail="tail2", value="value2")
        }
        dependent_string = DependentString(head="base_text", dependents=dependents)
        
        assert dependent_string.head == "base_text"
        assert len(dependent_string.dependents) == 2

    def test_generate_string_success(self):
        """Test successful string generation"""
        dependents = {
            0: Dependent(identifier="node1", field="field1", tail="_middle_", value="value1"),
            1: Dependent(identifier="node2", field="field2", tail="_end", value="value2")
        }
        dependent_string = DependentString(head="start_", dependents=dependents)
        
        result = dependent_string.generate_string()
        assert result == "start_value1_middle_value2_end"

    def test_generate_string_with_none_value(self):
        """Test string generation with None value raises error"""
        dependents = {
            0: Dependent(identifier="node1", field="field1", tail="_end", value=None)
        }
        dependent_string = DependentString(head="start_", dependents=dependents)
        
        with pytest.raises(ValueError, match="Dependent value is not set"):
            dependent_string.generate_string()

    def test_generate_string_empty_dependents(self):
        """Test string generation with no dependents"""
        dependent_string = DependentString(head="base_text", dependents={})
        
        result = dependent_string.generate_string()
        assert result == "base_text"

    def test_generate_string_ordered_dependents(self):
        """Test that dependents are processed in order"""
        dependents = {
            2: Dependent(identifier="node3", field="field3", tail="_third", value="value3"),
            0: Dependent(identifier="node1", field="field1", tail="_first", value="value1"),
            1: Dependent(identifier="node2", field="field2", tail="_second", value="value2")
        }
        dependent_string = DependentString(head="start_", dependents=dependents)
        
        result = dependent_string.generate_string()
        assert result == "start_value1_firstvalue2_secondvalue3_third"


class TestMarkSuccessStates:
    """Test cases for mark_success_states function"""

    @pytest.mark.asyncio
    async def test_mark_success_states_success(self):
        """Test successful marking of states as success"""
        state_ids = [
            PydanticObjectId("507f1f77bcf86cd799439011"),
            PydanticObjectId("507f1f77bcf86cd799439012")
        ]

        # Mock the query chain
        mock_query = MagicMock()
        mock_query.set = AsyncMock()

        # Mock the entire State class
        with patch('app.tasks.create_next_states.State') as mock_state_class:
            mock_state_class.find = MagicMock(return_value=mock_query)
            # Mock the id field as a property
            type(mock_state_class).id = MagicMock()

            await mark_success_states(state_ids)

            mock_query.set.assert_called_once_with({"status": StateStatusEnum.SUCCESS})

    @pytest.mark.asyncio
    async def test_mark_success_states_empty_list(self):
        """Test marking success states with empty list"""
        state_ids = []

        # Mock the query chain
        mock_query = MagicMock()
        mock_query.set = AsyncMock()

        # Mock the entire State class
        with patch('app.tasks.create_next_states.State') as mock_state_class:
            mock_state_class.find = MagicMock(return_value=mock_query)
            # Mock the id field as a property
            type(mock_state_class).id = MagicMock()

            await mark_success_states(state_ids)

            mock_query.set.assert_called_once_with({"status": StateStatusEnum.SUCCESS})


class TestCheckUnitesSatisfied:
    """Test cases for check_unites_satisfied function"""

    @pytest.mark.asyncio
    async def test_check_unites_satisfied_no_unites(self):
        """Test when node has no unites"""
        node_template = NodeTemplate(
            identifier="test_node",
            node_name="test_node",
            namespace="test",
            inputs={},
            next_nodes=[],
            unites=None
        )
        parents = {"parent1": PydanticObjectId("507f1f77bcf86cd799439011")}
        
        result = await check_unites_satisfied("test_namespace", "test_graph", node_template, parents)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_check_unites_satisfied_unites_not_in_parents(self):
        """Test when unites identifier is not in parents"""
        node_template = NodeTemplate(
            identifier="test_node",
            node_name="test_node",
            namespace="test",
            inputs={},
            next_nodes=[],
            unites=Unites(identifier="missing_parent")
        )
        parents = {"parent1": PydanticObjectId("507f1f77bcf86cd799439011")}
        
        with pytest.raises(ValueError, match="Unit identifier not found in parents"):
            await check_unites_satisfied("test_namespace", "test_graph", node_template, parents)

    @pytest.mark.asyncio
    async def test_check_unites_satisfied_no_pending_states(self):
        """Test when no pending states exist for unites"""
        node_template = NodeTemplate(
            identifier="test_node",
            node_name="test_node",
            namespace="test",
            inputs={},
            next_nodes=[],
            unites=Unites(identifier="parent1")
        )
        parents = {"parent1": PydanticObjectId("507f1f77bcf86cd799439011")}

        # Mock the query chain
        mock_query = MagicMock()
        mock_query.count = AsyncMock(return_value=0)

        # Mock the entire State class
        with patch('app.tasks.create_next_states.State') as mock_state_class:
            mock_state_class.find = MagicMock(return_value=mock_query)
            # Mock the required fields
            type(mock_state_class).namespace_name = MagicMock()
            type(mock_state_class).graph_name = MagicMock()
            type(mock_state_class).status = MagicMock()

            result = await check_unites_satisfied("test_namespace", "test_graph", node_template, parents)

            assert result is True

    @pytest.mark.asyncio
    async def test_check_unites_satisfied_pending_states_exist(self):
        """Test when pending states exist for unites"""
        node_template = NodeTemplate(
            identifier="test_node",
            node_name="test_node",
            namespace="test",
            inputs={},
            next_nodes=[],
            unites=Unites(identifier="parent1")
        )
        parents = {"parent1": PydanticObjectId("507f1f77bcf86cd799439011")}

        # Mock the query chain
        mock_query = MagicMock()
        mock_query.count = AsyncMock(return_value=1)

        # Mock the entire State class
        with patch('app.tasks.create_next_states.State') as mock_state_class:
            mock_state_class.find = MagicMock(return_value=mock_query)
            # Mock the required fields
            type(mock_state_class).namespace_name = MagicMock()
            type(mock_state_class).graph_name = MagicMock()
            type(mock_state_class).status = MagicMock()

            result = await check_unites_satisfied("test_namespace", "test_graph", node_template, parents)

            assert result is False


class TestGetDependents:
    """Test cases for get_dependents function"""

    def test_get_dependents_no_placeholders(self):
        """Test string with no placeholders"""
        syntax_string = "simple_text_without_placeholders"
        
        result = get_dependents(syntax_string)
        
        assert result.head == syntax_string
        assert result.dependents == {}

    def test_get_dependents_single_placeholder(self):
        """Test string with single placeholder"""
        syntax_string = "start_${{node1.outputs.field1}}_end"
        
        result = get_dependents(syntax_string)
        
        assert result.head == "start_"
        assert len(result.dependents) == 1
        assert result.dependents[0].identifier == "node1"
        assert result.dependents[0].field == "field1"
        assert result.dependents[0].tail == "_end"

    def test_get_dependents_multiple_placeholders(self):
        """Test string with multiple placeholders"""
        syntax_string = "start_${{node1.outputs.field1}}_middle_${{node2.outputs.field2}}_end"
        
        result = get_dependents(syntax_string)
        
        assert result.head == "start_"
        assert len(result.dependents) == 2
        assert result.dependents[0].identifier == "node1"
        assert result.dependents[0].field == "field1"
        assert result.dependents[0].tail == "_middle_"
        assert result.dependents[1].identifier == "node2"
        assert result.dependents[1].field == "field2"
        assert result.dependents[1].tail == "_end"

    def test_get_dependents_placeholder_at_start(self):
        """Test placeholder at the beginning of string"""
        syntax_string = "${{node1.outputs.field1}}_end"
        
        result = get_dependents(syntax_string)
        
        assert result.head == ""
        assert len(result.dependents) == 1
        assert result.dependents[0].identifier == "node1"
        assert result.dependents[0].field == "field1"
        assert result.dependents[0].tail == "_end"

    def test_get_dependents_placeholder_at_end(self):
        """Test placeholder at the end of string"""
        syntax_string = "start_${{node1.outputs.field1}}"
        
        result = get_dependents(syntax_string)
        
        assert result.head == "start_"
        assert len(result.dependents) == 1
        assert result.dependents[0].identifier == "node1"
        assert result.dependents[0].field == "field1"
        assert result.dependents[0].tail == ""

    def test_get_dependents_invalid_syntax_unclosed_placeholder(self):
        """Test invalid syntax with unclosed placeholder"""
        syntax_string = "start_${{node1.outputs.field1"
        
        with pytest.raises(ValueError, match="Invalid syntax string placeholder"):
            get_dependents(syntax_string)

    def test_get_dependents_invalid_syntax_wrong_format(self):
        """Test invalid syntax with wrong format"""
        syntax_string = "start_${{node1.inputs.field1}}_end"
        
        with pytest.raises(ValueError, match="Invalid syntax string placeholder"):
            get_dependents(syntax_string)

    def test_get_dependents_invalid_syntax_too_many_parts(self):
        """Test invalid syntax with too many parts"""
        syntax_string = "start_${{node1.outputs.field1.extra}}_end"
        
        with pytest.raises(ValueError, match="Invalid syntax string placeholder"):
            get_dependents(syntax_string)

    def test_get_dependents_invalid_syntax_too_few_parts(self):
        """Test invalid syntax with too few parts"""
        syntax_string = "start_${{node1.outputs}}_end"
        
        with pytest.raises(ValueError, match="Invalid syntax string placeholder"):
            get_dependents(syntax_string)

    def test_get_dependents_with_whitespace(self):
        """Test placeholder with whitespace"""
        syntax_string = "start_${{  node1  .  outputs  .  field1  }}_end"
        
        result = get_dependents(syntax_string)
        
        assert result.head == "start_"
        assert len(result.dependents) == 1
        assert result.dependents[0].identifier == "node1"
        assert result.dependents[0].field == "field1"
        assert result.dependents[0].tail == "_end"


class TestValidateDependencies:
    """Test cases for validate_dependencies function"""

    def test_validate_dependencies_success(self):
        """Test successful dependency validation"""
        class TestInputModel(BaseModel):
            field1: str
            field2: str
        
        node_template = NodeTemplate(
            identifier="test_node",
            node_name="test_node",
            namespace="test",
            inputs={
                "field1": "${{parent1.outputs.field1}}",
                "field2": "${{parent2.outputs.field2}}"
            },
            next_nodes=[],
            unites=None
        )
        
        # Create mock State objects and cast them to State type
        mock_parent1 = cast(State, MagicMock(spec=State))
        mock_parent1.outputs = {"field1": "value1"}
        mock_parent2 = cast(State, MagicMock(spec=State))
        mock_parent2.outputs = {"field2": "value2"}
        
        parents = {
            "parent1": mock_parent1,
            "parent2": mock_parent2
        }
        
        # Should not raise any exceptions
        validate_dependencies(node_template, TestInputModel, "test_node", parents)

    def test_validate_dependencies_missing_field(self):
        """Test validation with missing field in inputs"""
        class TestInputModel(BaseModel):
            field1: str
            field2: str
        
        node_template = NodeTemplate(
            identifier="test_node",
            node_name="test_node",
            namespace="test",
            inputs={
                "field1": "${{parent1.outputs.field1}}"
                # field2 is missing
            },
            next_nodes=[],
            unites=None
        )
        
        mock_parent1 = cast(State, MagicMock(spec=State))
        mock_parent1.outputs = {"field1": "value1"}
        parents = {"parent1": mock_parent1}
        
        with pytest.raises(ValueError, match="Field 'field2' not found in inputs"):
            validate_dependencies(node_template, TestInputModel, "test_node", parents)

    def test_validate_dependencies_missing_parent(self):
        """Test validation with missing parent identifier"""
        class TestInputModel(BaseModel):
            field1: str
        
        node_template = NodeTemplate(
            identifier="test_node",
            node_name="test_node",
            namespace="test",
            inputs={
                "field1": "${{missing_parent.outputs.field1}}"
            },
            next_nodes=[],
            unites=None
        )
        
        mock_parent1 = cast(State, MagicMock(spec=State))
        mock_parent1.outputs = {"field1": "value1"}
        parents = {"parent1": mock_parent1}
        
        with pytest.raises(KeyError, match="Identifier 'missing_parent' not found in parents"):
            validate_dependencies(node_template, TestInputModel, "test_node", parents)

    def test_validate_dependencies_current_identifier(self):
        """Test validation with current identifier (should be skipped)"""
        class TestInputModel(BaseModel):
            field1: str
        
        node_template = NodeTemplate(
            identifier="test_node",
            node_name="test_node",
            namespace="test",
            inputs={
                "field1": "${{test_node.outputs.field1}}"
            },
            next_nodes=[],
            unites=None
        )
        
        mock_parent1 = cast(State, MagicMock(spec=State))
        mock_parent1.outputs = {"field1": "value1"}
        parents = {"parent1": mock_parent1}
        
        # Should not raise any exceptions for current identifier
        validate_dependencies(node_template, TestInputModel, "test_node", parents)

    def test_validate_dependencies_complex_inputs(self):
        """Test validation with complex input patterns"""
        class TestInputModel(BaseModel):
            field1: str
            field2: str
            field3: str
        
        node_template = NodeTemplate(
            identifier="test_node",
            node_name="test_node",
            namespace="test",
            inputs={
                "field1": "static_text_${{parent1.outputs.field1}}_end",
                "field2": "${{parent2.outputs.field2}}_static",
                "field3": "start_${{parent3.outputs.field3}}_middle_${{parent4.outputs.field4}}_end"
            },
            next_nodes=[],
            unites=None
        )
        
        # Create mock State objects and cast them to State type
        mock_parent1 = cast(State, MagicMock(spec=State))
        mock_parent1.outputs = {"field1": "value1"}
        mock_parent2 = cast(State, MagicMock(spec=State))
        mock_parent2.outputs = {"field2": "value2"}
        mock_parent3 = cast(State, MagicMock(spec=State))
        mock_parent3.outputs = {"field3": "value3"}
        mock_parent4 = cast(State, MagicMock(spec=State))
        mock_parent4.outputs = {"field4": "value4"}
        
        parents = {
            "parent1": mock_parent1,
            "parent2": mock_parent2,
            "parent3": mock_parent3,
            "parent4": mock_parent4
        }
        
        # Should not raise any exceptions
        validate_dependencies(node_template, TestInputModel, "test_node", parents)

    def test_validate_dependencies_empty_inputs(self):
        """Test validation with empty inputs"""
        class TestInputModel(BaseModel):
            pass
        
        node_template = NodeTemplate(
            identifier="test_node",
            node_name="test_node",
            namespace="test",
            inputs={},
            next_nodes=[],
            unites=None
        )
        
        parents = {}
        
        # Should not raise any exceptions
        validate_dependencies(node_template, TestInputModel, "test_node", parents)

    def test_validate_dependencies_invalid_syntax_in_input(self):
        """Test validation with invalid syntax in input"""
        class TestInputModel(BaseModel):
            field1: str
        
        node_template = NodeTemplate(
            identifier="test_node",
            node_name="test_node",
            namespace="test",
            inputs={
                "field1": "${{invalid_syntax}}"
            },
            next_nodes=[],
            unites=None
        )
        
        parents = {}
        
        with pytest.raises(ValueError, match="Invalid syntax string placeholder"):
            validate_dependencies(node_template, TestInputModel, "test_node", parents)