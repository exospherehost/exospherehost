import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from beanie import PydanticObjectId
from app.tasks.create_next_states import (
    mark_success_states,
    check_unites_satisfied,
    validate_dependencies,
    create_next_states
)
from app.models.dependent_string import Dependent, DependentString
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

    def test_create_dependent_string_no_placeholders(self):
        """Test creating DependentString from string with no placeholders"""
        result = DependentString.create_dependent_string("simple_text")
        
        assert result.head == "simple_text"
        assert result.dependents == {}

    def test_create_dependent_string_single_placeholder(self):
        """Test creating DependentString from string with single placeholder"""
        result = DependentString.create_dependent_string("prefix_${{node1.outputs.field1}}_suffix")
        
        assert result.head == "prefix_"
        assert len(result.dependents) == 1
        assert result.dependents[0].identifier == "node1"
        assert result.dependents[0].field == "field1"
        assert result.dependents[0].tail == "_suffix"

    def test_create_dependent_string_multiple_placeholders(self):
        """Test creating DependentString from string with multiple placeholders"""
        result = DependentString.create_dependent_string("${{node1.outputs.field1}}_${{node2.outputs.field2}}_end")
        
        assert result.head == ""
        assert len(result.dependents) == 2
        assert result.dependents[0].identifier == "node1"
        assert result.dependents[0].field == "field1"
        assert result.dependents[0].tail == "_"
        assert result.dependents[1].identifier == "node2"
        assert result.dependents[1].field == "field2"
        assert result.dependents[1].tail == "_end"

    def test_create_dependent_string_invalid_syntax(self):
        """Test creating DependentString with invalid syntax"""
        with pytest.raises(ValueError, match="Invalid syntax string placeholder"):
            DependentString.create_dependent_string("${{node1.outputs.field1")

    def test_create_dependent_string_invalid_placeholder_format(self):
        """Test creating DependentString with invalid placeholder format"""
        with pytest.raises(ValueError, match="Invalid syntax string placeholder"):
            DependentString.create_dependent_string("${{node1.field1}}")

    def test_set_value(self):
        """Test setting value for dependents"""
        dependent_string = DependentString.create_dependent_string("${{node1.outputs.field1}}_${{node1.outputs.field2}}")
        
        dependent_string.set_value("node1", "field1", "value1")
        dependent_string.set_value("node1", "field2", "value2")
        
        assert dependent_string.dependents[0].value == "value1"
        assert dependent_string.dependents[1].value == "value2"

    def test_get_identifier_field(self):
        """Test getting identifier-field pairs"""
        dependent_string = DependentString.create_dependent_string("${{node1.outputs.field1}}_${{node2.outputs.field2}}")
        
        result = dependent_string.get_identifier_field()
        
        assert len(result) == 2
        assert ("node1", "field1") in result
        assert ("node2", "field2") in result


class TestMarkSuccessStates:
    """Test cases for mark_success_states function"""

    @pytest.mark.asyncio
    async def test_mark_success_states(self):
        """Test marking states as successful"""
        state_ids = [PydanticObjectId(), PydanticObjectId()]
        
        with patch('app.tasks.create_next_states.State') as mock_state:
            mock_find = AsyncMock()
            mock_set = AsyncMock()
            mock_find.set.return_value = mock_set
            mock_state.find.return_value = mock_find
            
            await mark_success_states(state_ids)
            
            mock_state.find.assert_called_once()
            mock_find.set.assert_called_once_with({"status": StateStatusEnum.SUCCESS})


class TestCheckUnitesSatisfied:
    """Test cases for check_unites_satisfied function"""

    @pytest.mark.asyncio
    async def test_check_unites_satisfied_no_unites(self):
        """Test when node template has no unites"""
        node_template = NodeTemplate(
            node_name="test_node",
            identifier="test_id",
            namespace="test",
            inputs={},
            next_nodes=None,
            unites=None
        )
        parents = {"parent1": PydanticObjectId()}
        
        result = await check_unites_satisfied("test_namespace", "test_graph", node_template, parents)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_check_unites_satisfied_unites_not_in_parents(self):
        """Test when unites identifier is not in parents"""
        node_template = NodeTemplate(
            node_name="test_node",
            identifier="test_id",
            namespace="test",
            inputs={},
            next_nodes=None,
            unites=Unites(identifier="missing_parent")
        )
        parents = {"parent1": PydanticObjectId()}
        
        with pytest.raises(ValueError, match="Unit identifier not found in parents"):
            await check_unites_satisfied("test_namespace", "test_graph", node_template, parents)

    @pytest.mark.asyncio
    async def test_check_unites_satisfied_pending_states(self):
        """Test when there are pending states for the unites"""
        node_template = NodeTemplate(
            node_name="test_node",
            identifier="test_id",
            namespace="test",
            inputs={},
            next_nodes=None,
            unites=Unites(identifier="parent1")
        )
        parents = {"parent1": PydanticObjectId()}
        
        with patch('app.tasks.create_next_states.State') as mock_state:
            mock_find = AsyncMock()
            mock_find.count.return_value = 1
            mock_state.find.return_value = mock_find
            
            result = await check_unites_satisfied("test_namespace", "test_graph", node_template, parents)
            
            assert result is False

    @pytest.mark.asyncio
    async def test_check_unites_satisfied_no_pending_states(self):
        """Test when there are no pending states for the unites"""
        node_template = NodeTemplate(
            node_name="test_node",
            identifier="test_id",
            namespace="test",
            inputs={},
            next_nodes=None,
            unites=Unites(identifier="parent1")
        )
        parents = {"parent1": PydanticObjectId()}
        
        with patch('app.tasks.create_next_states.State') as mock_state:
            mock_find = AsyncMock()
            mock_find.count.return_value = 0
            mock_state.find.return_value = mock_find
            
            result = await check_unites_satisfied("test_namespace", "test_graph", node_template, parents)
            
            assert result is True


class TestValidateDependencies:
    """Test cases for validate_dependencies function"""

    def test_validate_dependencies_success(self):
        """Test successful dependency validation"""
        node_template = NodeTemplate(
            node_name="test_node",
            identifier="test_id",
            namespace="test",
            inputs={"input1": "{{parent1.outputs.field1}}"},
            next_nodes=None,
            unites=None
        )
        
        class TestInputModel(BaseModel):
            input1: str
        
        mock_parent = MagicMock()
        mock_parent.outputs = {"field1": "value1"}
        
        parents = {
            "parent1": mock_parent
        }
        
        # Should not raise any exception
        validate_dependencies(node_template, TestInputModel, "test_id", parents) # type: ignore

    def test_validate_dependencies_field_not_in_inputs(self):
        """Test when model field is not in node template inputs"""
        node_template = NodeTemplate(
            node_name="test_node",
            identifier="test_id",
            namespace="test",
            inputs={},  # Empty inputs
            next_nodes=None,
            unites=None
        )
        
        class TestInputModel(BaseModel):
            input1: str
        
        parents = {}
        
        with pytest.raises(ValueError, match="Field 'input1' not found in inputs"):
            validate_dependencies(node_template, TestInputModel, "test_id", parents)

    def test_validate_dependencies_identifier_not_in_parents(self):
        """Test when dependent identifier is not in parents"""
        node_template = NodeTemplate(
            node_name="test_node",
            identifier="test_id",
            namespace="test",
            inputs={"input1": "${{missing_parent.outputs.field1}}"},
            next_nodes=None,
            unites=None
        )
        
        class TestInputModel(BaseModel):
            input1: str
        
        parents = {}
        
        with pytest.raises(KeyError, match="Identifier 'missing_parent' not found in parents"):
            validate_dependencies(node_template, TestInputModel, "test_id", parents)

    def test_validate_dependencies_field_not_in_parent_outputs(self):
        """Test when dependent field is not in parent outputs"""
        node_template = NodeTemplate(
            node_name="test_node",
            identifier="test_id",
            namespace="test",
            inputs={"input1": "${{parent1.outputs.missing_field}}"},
            next_nodes=None,
            unites=None
        )
        
        class TestInputModel(BaseModel):
            input1: str
        
        mock_parent = MagicMock()
        mock_parent.outputs = {"field1": "value1"}  # missing_field not present
        
        parents = {
            "parent1": mock_parent
        }
        
        with pytest.raises(AttributeError, match="Output field 'missing_field' not found on state"):
            validate_dependencies(node_template, TestInputModel, "test_id", parents) # type: ignore


class TestCreateNextStates:
    """Test cases for create_next_states function"""

    @pytest.mark.asyncio
    async def test_create_next_states_empty_state_ids(self):
        """Test with empty state ids"""
        # Create a mock class that has the id attribute
        mock_state_class = MagicMock()
        mock_state_class.id = "id"
        mock_find = AsyncMock()
        mock_set = AsyncMock()
        mock_find.set.return_value = mock_set
        mock_state_class.find.return_value = mock_find
        
        with patch('app.tasks.create_next_states.State', mock_state_class):
            with pytest.raises(ValueError, match="State ids is empty"):
                await create_next_states([], "test_id", "test_namespace", "test_graph", {})

    @pytest.mark.asyncio
    async def test_create_next_states_no_next_nodes(self):
        """Test when current state has no next nodes"""
        state_ids = [PydanticObjectId()]
        
        with patch('app.tasks.create_next_states.GraphTemplate') as mock_graph_template:
            mock_template = MagicMock()
            mock_node = NodeTemplate(
                node_name="test_node",
                identifier="test_id",
                namespace="test",
                inputs={},
                next_nodes=None,  # No next nodes
                unites=None
            )
            mock_template.get_node_by_identifier.return_value = mock_node
            mock_graph_template.get_valid = AsyncMock(return_value=mock_template)
            
            # Create a mock class that has the id attribute
            mock_state_class = MagicMock()
            mock_state_class.id = "id"
            mock_find = AsyncMock()
            mock_set = AsyncMock()
            mock_find.set.return_value = mock_set
            mock_state_class.find.return_value = mock_find
            
            with patch('app.tasks.create_next_states.State', mock_state_class):
                
                await create_next_states(state_ids, "test_id", "test_namespace", "test_graph", {})
                
                # Should mark states as successful
                mock_state_class.find.assert_called()
                mock_find.set.assert_called_with({"status": StateStatusEnum.SUCCESS})

    @pytest.mark.asyncio
    async def test_create_next_states_node_template_not_found(self):
        """Test when current state node template is not found"""
        state_ids = [PydanticObjectId()]
        
        with patch('app.tasks.create_next_states.GraphTemplate') as mock_graph_template:
            mock_template = MagicMock()
            mock_template.get_node_by_identifier.return_value = None
            mock_graph_template.get_valid = AsyncMock(return_value=mock_template)
            
            # Create a mock class that has the id attribute
            mock_state_class = MagicMock()
            mock_state_class.id = "id"
            mock_find = AsyncMock()
            mock_set = AsyncMock()
            mock_find.set.return_value = mock_set
            mock_state_class.find.return_value = mock_find
            
            with patch('app.tasks.create_next_states.State', mock_state_class):
                with pytest.raises(ValueError, match="Current state node template not found"):
                    await create_next_states(state_ids, "test_id", "test_namespace", "test_graph", {})

    @pytest.mark.asyncio
    async def test_create_next_states_next_node_template_not_found(self):
        """Test when next state node template is not found"""
        state_ids = [PydanticObjectId()]
        
        with patch('app.tasks.create_next_states.GraphTemplate') as mock_graph_template:
            mock_template = MagicMock()
            current_node = NodeTemplate(
                node_name="test_node",
                identifier="test_id",
                namespace="test",
                inputs={},
                next_nodes=["next_node"],
                unites=None
            )
            mock_template.get_node_by_identifier.side_effect = [current_node, None]
            mock_graph_template.get_valid = AsyncMock(return_value=mock_template)
            
            # Create a mock class that has the id attribute
            mock_state_class = MagicMock()
            mock_state_class.id = "id"
            mock_find = AsyncMock()
            mock_set = AsyncMock()
            mock_find.set.return_value = mock_set
            mock_state_class.find.return_value = mock_find
            
            with patch('app.tasks.create_next_states.State', mock_state_class):
                with pytest.raises(ValueError, match="Next state node template not found"):
                    await create_next_states(state_ids, "test_id", "test_namespace", "test_graph", {})

    @pytest.mark.asyncio
    async def test_create_next_states_registered_node_not_found(self):
        """Test when registered node is not found"""
        state_ids = [PydanticObjectId()]
        
        with patch('app.tasks.create_next_states.GraphTemplate') as mock_graph_template:
            mock_template = MagicMock()
            current_node = NodeTemplate(
                node_name="test_node",
                identifier="test_id",
                namespace="test",
                inputs={},
                next_nodes=["next_node"],
                unites=None
            )
            next_node = NodeTemplate(
                node_name="next_node",
                identifier="next_node",
                namespace="test",
                inputs={},
                next_nodes=None,
                unites=None
            )
            mock_template.get_node_by_identifier.side_effect = [current_node, next_node]
            mock_graph_template.get_valid = AsyncMock(return_value=mock_template)
            
            # Create a mock class that has the id attribute
            mock_state_class = MagicMock()
            mock_state_class.id = "id"
            mock_find = AsyncMock()
            mock_set = AsyncMock()
            mock_find.set.return_value = mock_set
            mock_state_class.find.return_value = mock_find
            
            with patch('app.tasks.create_next_states.State', mock_state_class):
                with patch('app.tasks.create_next_states.RegisteredNode') as mock_registered_node:
                    mock_registered_node.get_by_name_and_namespace = AsyncMock(return_value=None)
                    
                    with pytest.raises(ValueError, match="Registered node not found"):
                        await create_next_states(state_ids, "test_id", "test_namespace", "test_graph", {})

    @pytest.mark.asyncio
    async def test_create_next_states_success(self):
        """Test successful creation of next states"""
        state_ids = [PydanticObjectId()]
        
        with patch('app.tasks.create_next_states.GraphTemplate') as mock_graph_template:
            mock_template = MagicMock()
            current_node = NodeTemplate(
                node_name="test_node",
                identifier="test_id",
                namespace="test",
                inputs={},
                next_nodes=["next_node"],
                unites=None
            )
            next_node = NodeTemplate(
                node_name="next_node",
                identifier="next_node",
                namespace="test",
                inputs={"input1": "${{test_id.outputs.field1}}"},
                next_nodes=None,
                unites=None
            )
            mock_template.get_node_by_identifier.side_effect = [current_node, next_node]
            mock_graph_template.get_valid = AsyncMock(return_value=mock_template)
            
            with patch('app.tasks.create_next_states.RegisteredNode') as mock_registered_node:
                mock_registered_node_instance = MagicMock()
                mock_registered_node_instance.inputs_schema = {"input1": {"type": "string"}}
                mock_registered_node.get_by_name_and_namespace = AsyncMock(return_value=mock_registered_node_instance)
                
                # Create a mock class that has the id attribute for the State mock
                mock_state_class = MagicMock()
                mock_state_class.id = "id"
                mock_find = AsyncMock()
                mock_set = AsyncMock()
                mock_insert_many = AsyncMock()
                mock_state_class.insert_many = mock_insert_many
                mock_current_state = MagicMock()
                mock_current_state.node_name = "test_node"
                mock_current_state.identifier = "test_id"
                mock_current_state.namespace_name = "test"
                mock_current_state.graph_name = "test_graph"
                mock_current_state.status = StateStatusEnum.CREATED
                mock_current_state.parents = {}
                mock_current_state.inputs = {}
                mock_current_state.outputs = {"field1": "value1"}
                mock_current_state.does_unites = False
                mock_current_state.run_id = "test_run"
                mock_current_state.error = None
                mock_find.to_list.return_value = [mock_current_state]
                mock_find.set.return_value = mock_set
                mock_state_class.find.return_value = mock_find
                
                with patch('app.tasks.create_next_states.State', mock_state_class):
                    with patch('app.tasks.create_next_states.create_model') as mock_create_model:
                        mock_input_model = MagicMock()
                        mock_input_model.model_fields = {"input1": MagicMock(annotation=str)}
                        mock_create_model.return_value = mock_input_model
                        
                        await create_next_states(state_ids, "test_id", "test_namespace", "test_graph", {})
                        
                        # Should insert new states and mark current states as successful
                        mock_insert_many.assert_called_once()
                        mock_find.set.assert_called_with({"status": StateStatusEnum.SUCCESS})

    @pytest.mark.asyncio
    async def test_create_next_states_exception_handling(self):
        """Test exception handling during next states creation"""
        state_ids = [PydanticObjectId()]
        
        with patch('app.tasks.create_next_states.GraphTemplate') as mock_graph_template:
            mock_graph_template.get_valid.side_effect = Exception("Graph template error")
            
            # Create a mock class that has the id attribute
            mock_state_class = MagicMock()
            mock_state_class.id = "id"
            mock_find = AsyncMock()
            mock_set = AsyncMock()
            mock_find.set.return_value = mock_set
            mock_state_class.find.return_value = mock_find
            
            with patch('app.tasks.create_next_states.State', mock_state_class):
                with pytest.raises(Exception, match="Graph template error"):
                    await create_next_states(state_ids, "test_id", "test_namespace", "test_graph", {})
                
                # Should mark states as error
                mock_find.set.assert_called_with({
                    "status": StateStatusEnum.NEXT_CREATED_ERROR,
                    "error": "Graph template error"
                })