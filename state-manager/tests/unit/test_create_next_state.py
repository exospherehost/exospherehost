import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from beanie import PydanticObjectId

from app.tasks.create_next_state import create_next_state
from app.models.db.state import State
from app.models.db.graph_template_model import GraphTemplate
from app.models.db.registered_node import RegisteredNode
from app.models.graph_template_validation_status import GraphTemplateValidationStatus
from app.models.state_status_enum import StateStatusEnum


class TestCreateNextState:
    """Test cases for create_next_state function"""

    @pytest.fixture
    def mock_state(self):
        """Create a mock state object"""
        state = MagicMock(spec=State)
        state.id = PydanticObjectId()
        state.identifier = "test_node"
        state.namespace_name = "test_namespace"
        state.graph_name = "test_graph"
        state.run_id = "test_run_id"
        state.status = StateStatusEnum.EXECUTED
        state.inputs = {"input1": "value1"}
        state.outputs = {"output1": "result1"}
        state.error = None
        state.parents = {"parent_node": PydanticObjectId()}
        state.save = AsyncMock()
        return state

    @pytest.fixture
    def mock_graph_template(self):
        """Create a mock graph template"""
        template = MagicMock(spec=GraphTemplate)
        template.validation_status = GraphTemplateValidationStatus.VALID
        template.get_node_by_identifier = MagicMock()
        return template

    @pytest.fixture
    def mock_registered_node(self):
        """Create a mock registered node"""
        node = MagicMock(spec=RegisteredNode)
        node.inputs_schema = {
            "type": "object",
            "properties": {
                "field1": {"type": "string"},
                "field2": {"type": "string"}
            }
        }
        return node

    @patch('app.tasks.create_next_state.GraphTemplate')
    async def test_create_next_state_none_id(self, mock_graph_template_class):
        """Test create_next_state with state having None id"""
        # Arrange
        state_with_none_id = MagicMock()
        state_with_none_id.id = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="State is not valid"):
            await create_next_state(state_with_none_id)

    @patch('app.tasks.create_next_state.GraphTemplate')
    @patch('app.tasks.create_next_state.asyncio.sleep')
    async def test_create_next_state_wait_for_validation(
        self,
        mock_sleep,
        mock_graph_template_class,
        mock_state,
        mock_graph_template
    ):
        """Test waiting for graph template to become valid"""
        # Arrange
        # First call returns invalid template, second call returns valid
        invalid_template = MagicMock()
        invalid_template.validation_status = GraphTemplateValidationStatus.INVALID
        
        mock_graph_template_class.find_one = AsyncMock(side_effect=[invalid_template, mock_graph_template])
        
        # Mock node template with no next nodes
        node_template = MagicMock()
        node_template.next_nodes = None
        mock_graph_template.get_node_by_identifier.return_value = node_template
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        assert mock_graph_template_class.find_one.call_count == 2
        mock_sleep.assert_called_once_with(1)
        assert mock_state.status == StateStatusEnum.SUCCESS

    @patch('app.tasks.create_next_state.GraphTemplate')
    async def test_create_next_state_no_next_nodes(
        self,
        mock_graph_template_class,
        mock_state,
        mock_graph_template
    ):
        """Test when there are no next nodes"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        
        node_template = MagicMock()
        node_template.next_nodes = None
        mock_graph_template.get_node_by_identifier.return_value = node_template
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        assert mock_state.status == StateStatusEnum.SUCCESS

    @patch('app.tasks.create_next_state.GraphTemplate')
    async def test_create_next_state_general_exception(
        self,
        mock_graph_template_class,
        mock_state
    ):
        """Test general exception handling"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(side_effect=Exception("General error"))
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        assert mock_state.status == StateStatusEnum.ERRORED
        assert mock_state.error == "General error"
        mock_state.save.assert_called_once()

    @patch('app.tasks.create_next_state.GraphTemplate')
    @patch('app.tasks.create_next_state.time.time')
    @patch('app.tasks.create_next_state.asyncio.sleep')
    async def test_create_next_state_timeout_waiting_for_validation(
        self,
        mock_sleep,
        mock_time,
        mock_graph_template_class,
        mock_state
    ):
        """Test timeout when waiting for graph template validation"""
        # Arrange
        invalid_template = MagicMock()
        invalid_template.validation_status = GraphTemplateValidationStatus.INVALID
        mock_graph_template_class.find_one = AsyncMock(return_value=invalid_template)
        
        # Mock time progression to trigger timeout
        mock_time.side_effect = [0, 100, 400]  # Start time, check time, timeout time
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        assert mock_state.status == StateStatusEnum.ERRORED
        assert "Timeout waiting for graph template" in mock_state.error

    @patch('app.tasks.create_next_state.GraphTemplate')
    async def test_create_next_state_graph_template_not_found(
        self,
        mock_graph_template_class,
        mock_state
    ):
        """Test when graph template is not found"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=None)
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        assert mock_state.status == StateStatusEnum.ERRORED
        assert "Graph template test_graph not found" in mock_state.error

    @patch('app.tasks.create_next_state.GraphTemplate')
    async def test_create_next_state_node_template_not_found(
        self,
        mock_graph_template_class,
        mock_state,
        mock_graph_template
    ):
        """Test when node template is not found in graph"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        mock_graph_template.get_node_by_identifier.return_value = None
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        assert mock_state.status == StateStatusEnum.ERRORED
        assert "Node template test_node not found" in mock_state.error

    @patch('app.tasks.create_next_state.GraphTemplate')
    @patch('app.tasks.create_next_state.RegisteredNode')
    @patch('app.tasks.create_next_state.State')
    async def test_create_next_state_with_multiple_next_nodes(
        self,
        mock_state_class,
        mock_registered_node_class,
        mock_graph_template_class,
        mock_state,
        mock_graph_template,
        mock_registered_node
    ):
        """Test creating multiple next states"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        
        # Set up node template with multiple next nodes
        node_template = MagicMock()
        node_template.next_nodes = ["node1", "node2"]
        
        # Set up next node templates
        next_node1 = MagicMock()
        next_node1.identifier = "node1"
        next_node1.node_name = "registered_node1"
        next_node1.namespace = "test_namespace"
        next_node1.inputs = {"field1": "value1", "field2": "value2"}
        next_node1.unites = None
        
        next_node2 = MagicMock()
        next_node2.identifier = "node2"
        next_node2.node_name = "registered_node2"
        next_node2.namespace = "test_namespace"
        next_node2.inputs = {"field1": "value3", "field2": "value4"}
        next_node2.unites = None
        
        mock_graph_template.get_node_by_identifier.side_effect = lambda x: {
            "test_node": node_template,
            "node1": next_node1,
            "node2": next_node2
        }.get(x)
        
        mock_registered_node_class.find_one = AsyncMock(return_value=mock_registered_node)
        
        # Mock State creation and saving
        mock_new_state = MagicMock()
        mock_new_state.save = AsyncMock()
        mock_state_class.return_value = mock_new_state
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        assert mock_state_class.call_count == 2  # Two new states created
        assert mock_state.status == StateStatusEnum.SUCCESS

    @patch('app.tasks.create_next_state.GraphTemplate')
    @patch('app.tasks.create_next_state.RegisteredNode')
    @patch('app.tasks.create_next_state.State')
    async def test_create_next_state_registered_node_not_found(
        self,
        mock_state_class,
        mock_registered_node_class,
        mock_graph_template_class,
        mock_state,
        mock_graph_template
    ):
        """Test when registered node is not found"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        
        node_template = MagicMock()
        node_template.next_nodes = ["node1"]
        
        next_node = MagicMock()
        next_node.identifier = "node1"
        next_node.node_name = "missing_node"
        next_node.namespace = "test_namespace"
        next_node.unites = None
        
        mock_graph_template.get_node_by_identifier.side_effect = lambda x: {
            "test_node": node_template,
            "node1": next_node
        }.get(x)
        
        mock_registered_node_class.find_one = AsyncMock(return_value=None)
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        assert mock_state.status == StateStatusEnum.ERRORED
        assert "Registered node missing_node not found" in mock_state.error

    @patch('app.tasks.create_next_state.GraphTemplate')
    @patch('app.tasks.create_next_state.RegisteredNode')
    @patch('app.tasks.create_next_state.State')
    async def test_create_next_state_with_dependencies_satisfied(
        self,
        mock_state_class,
        mock_registered_node_class,
        mock_graph_template_class,
        mock_state,
        mock_graph_template,
        mock_registered_node
    ):
        """Test creating next state when dependencies are satisfied"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        
        node_template = MagicMock()
        node_template.next_nodes = ["node1"]
        
        # Create dependency
        dependency = MagicMock()
        dependency.identifier = "dep_node"
        
        next_node = MagicMock()
        next_node.identifier = "node1"
        next_node.node_name = "registered_node1"
        next_node.namespace = "test_namespace"
        next_node.inputs = {"field1": "value1"}
        next_node.unites = [dependency]
        
        mock_graph_template.get_node_by_identifier.side_effect = lambda x: {
            "test_node": node_template,
            "node1": next_node
        }.get(x)
        
        # Mock dependency satisfied (no pending states)
        mock_state_class.find = MagicMock(return_value=AsyncMock(count=AsyncMock(return_value=0)))
        mock_registered_node_class.find_one = AsyncMock(return_value=mock_registered_node)
        
        # Set up parents to include the dependency
        mock_state.parents = {"dep_node": PydanticObjectId()}
        
        # Mock State creation
        mock_new_state = MagicMock()
        mock_new_state.save = AsyncMock()
        mock_state_class.return_value = mock_new_state
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        assert mock_state_class.call_count == 1  # One new state created
        assert mock_state.status == StateStatusEnum.SUCCESS

    @patch('app.tasks.create_next_state.GraphTemplate')
    @patch('app.tasks.create_next_state.RegisteredNode')
    @patch('app.tasks.create_next_state.State')
    async def test_create_next_state_with_dependencies_unsatisfied(
        self,
        mock_state_class,
        mock_registered_node_class,
        mock_graph_template_class,
        mock_state,
        mock_graph_template
    ):
        """Test skipping next state creation when dependencies are not satisfied"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        
        node_template = MagicMock()
        node_template.next_nodes = ["node1"]
        
        # Create dependency
        dependency = MagicMock()
        dependency.identifier = "dep_node"
        
        next_node = MagicMock()
        next_node.identifier = "node1"
        next_node.node_name = "registered_node1"
        next_node.namespace = "test_namespace"
        next_node.unites = [dependency]
        
        mock_graph_template.get_node_by_identifier.side_effect = lambda x: {
            "test_node": node_template,
            "node1": next_node
        }.get(x)
        
        # Mock dependency not satisfied (has pending states)
        mock_state_class.find = MagicMock(return_value=AsyncMock(count=AsyncMock(return_value=1)))
        
        # Set up parents to include the dependency
        mock_state.parents = {"dep_node": PydanticObjectId()}
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        assert mock_state_class.call_count == 0  # No new states created
        assert mock_state.status == StateStatusEnum.SUCCESS

    @patch('app.tasks.create_next_state.GraphTemplate')
    @patch('app.tasks.create_next_state.RegisteredNode')
    @patch('app.tasks.create_next_state.State')
    async def test_create_next_state_dependency_root_parent_not_found(
        self,
        mock_state_class,
        mock_registered_node_class,
        mock_graph_template_class,
        mock_state,
        mock_graph_template
    ):
        """Test error when dependency root parent is not found"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        
        node_template = MagicMock()
        node_template.next_nodes = ["node1"]
        
        # Create dependency
        dependency = MagicMock()
        dependency.identifier = "missing_dep_node"
        
        next_node = MagicMock()
        next_node.identifier = "node1"
        next_node.node_name = "registered_node1"
        next_node.namespace = "test_namespace"
        next_node.unites = [dependency]
        
        mock_graph_template.get_node_by_identifier.side_effect = lambda x: {
            "test_node": node_template,
            "node1": next_node
        }.get(x)
        
        # Parents don't include the dependency
        mock_state.parents = {"other_node": PydanticObjectId()}
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        assert mock_state.status == StateStatusEnum.ERRORED
        assert "Root parent of missing_dep_node not found" in mock_state.error

    @patch('app.tasks.create_next_state.GraphTemplate')
    @patch('app.tasks.create_next_state.RegisteredNode')
    @patch('app.tasks.create_next_state.State')
    async def test_create_next_state_input_placeholder_substitution_simple(
        self,
        mock_state_class,
        mock_registered_node_class,
        mock_graph_template_class,
        mock_state,
        mock_graph_template,
        mock_registered_node
    ):
        """Test simple input placeholder substitution"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        
        node_template = MagicMock()
        node_template.next_nodes = ["node1"]
        
        next_node = MagicMock()
        next_node.identifier = "node1"
        next_node.node_name = "registered_node1"
        next_node.namespace = "test_namespace"
        next_node.inputs = {"field1": "${{parent_node.outputs.result}}"}
        next_node.unites = None
        
        mock_graph_template.get_node_by_identifier.side_effect = lambda x: {
            "test_node": node_template,
            "node1": next_node
        }.get(x)
        
        mock_registered_node_class.find_one = AsyncMock(return_value=mock_registered_node)
        
        # Set up parent state with outputs
        parent_id = PydanticObjectId()
        parent_state = MagicMock()
        parent_state.outputs = {"result": "success_value"}
        
        mock_state_class.get = AsyncMock(return_value=parent_state)
        mock_state.parents = {"parent_node": parent_id}
        
        # Mock State creation
        mock_new_state = MagicMock()
        mock_new_state.save = AsyncMock()
        mock_state_class.return_value = mock_new_state
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        state_creation_call = mock_state_class.call_args
        assert state_creation_call[1]['inputs'] == {"field1": "success_value"}
        assert mock_state.status == StateStatusEnum.SUCCESS

    @patch('app.tasks.create_next_state.GraphTemplate')
    @patch('app.tasks.create_next_state.RegisteredNode')
    @patch('app.tasks.create_next_state.State')
    async def test_create_next_state_input_placeholder_substitution_complex(
        self,
        mock_state_class,
        mock_registered_node_class,
        mock_graph_template_class,
        mock_state,
        mock_graph_template,
        mock_registered_node
    ):
        """Test complex input placeholder substitution with multiple placeholders"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        
        node_template = MagicMock()
        node_template.next_nodes = ["node1"]
        
        next_node = MagicMock()
        next_node.identifier = "node1"
        next_node.node_name = "registered_node1"
        next_node.namespace = "test_namespace"
        next_node.inputs = {
            "field1": "prefix_${{parent1.outputs.value1}}_${{parent2.outputs.value2}}_suffix",
            "field2": "${{parent1.outputs.complex_value}}"
        }
        next_node.unites = None
        
        mock_graph_template.get_node_by_identifier.side_effect = lambda x: {
            "test_node": node_template,
            "node1": next_node
        }.get(x)
        
        mock_registered_node_class.find_one = AsyncMock(return_value=mock_registered_node)
        
        # Set up parent states with outputs
        parent1_id = PydanticObjectId()
        parent1_state = MagicMock()
        parent1_state.outputs = {"value1": "first", "complex_value": "complex_result"}
        
        parent2_id = PydanticObjectId()
        parent2_state = MagicMock()
        parent2_state.outputs = {"value2": "second"}
        
        mock_state_class.get = AsyncMock(side_effect=lambda x: {
            parent1_id: parent1_state,
            parent2_id: parent2_state
        }[x])
        
        mock_state.parents = {"parent1": parent1_id, "parent2": parent2_id}
        
        # Mock State creation
        mock_new_state = MagicMock()
        mock_new_state.save = AsyncMock()
        mock_state_class.return_value = mock_new_state
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        state_creation_call = mock_state_class.call_args
        expected_inputs = {
            "field1": "prefix_first_second_suffix",
            "field2": "complex_result"
        }
        assert state_creation_call[1]['inputs'] == expected_inputs
        assert mock_state.status == StateStatusEnum.SUCCESS

    @patch('app.tasks.create_next_state.GraphTemplate')
    @patch('app.tasks.create_next_state.RegisteredNode')
    @patch('app.tasks.create_next_state.State')
    async def test_create_next_state_input_placeholder_no_substitution(
        self,
        mock_state_class,
        mock_registered_node_class,
        mock_graph_template_class,
        mock_state,
        mock_graph_template,
        mock_registered_node
    ):
        """Test input with no placeholder substitution needed"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        
        node_template = MagicMock()
        node_template.next_nodes = ["node1"]
        
        next_node = MagicMock()
        next_node.identifier = "node1"
        next_node.node_name = "registered_node1"
        next_node.namespace = "test_namespace"
        next_node.inputs = {"field1": "static_value", "field2": "another_static"}
        next_node.unites = None
        
        mock_graph_template.get_node_by_identifier.side_effect = lambda x: {
            "test_node": node_template,
            "node1": next_node
        }.get(x)
        
        mock_registered_node_class.find_one = AsyncMock(return_value=mock_registered_node)
        
        # Mock State creation
        mock_new_state = MagicMock()
        mock_new_state.save = AsyncMock()
        mock_state_class.return_value = mock_new_state
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        state_creation_call = mock_state_class.call_args
        assert state_creation_call[1]['inputs'] == {"field1": "static_value", "field2": "another_static"}
        assert mock_state.status == StateStatusEnum.SUCCESS

    @patch('app.tasks.create_next_state.GraphTemplate')
    @patch('app.tasks.create_next_state.RegisteredNode')
    @patch('app.tasks.create_next_state.State')
    async def test_create_next_state_input_placeholder_invalid_format(
        self,
        mock_state_class,
        mock_registered_node_class,
        mock_graph_template_class,
        mock_state,
        mock_graph_template,
        mock_registered_node
    ):
        """Test error handling for invalid input placeholder format"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        
        node_template = MagicMock()
        node_template.next_nodes = ["node1"]
        
        next_node = MagicMock()
        next_node.identifier = "node1"
        next_node.node_name = "registered_node1"
        next_node.namespace = "test_namespace"
        next_node.inputs = {"field1": "${{invalid.format}}"}  # Missing outputs part
        next_node.unites = None
        
        mock_graph_template.get_node_by_identifier.side_effect = lambda x: {
            "test_node": node_template,
            "node1": next_node
        }.get(x)
        
        mock_registered_node_class.find_one = AsyncMock(return_value=mock_registered_node)
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        assert mock_state.status == StateStatusEnum.ERRORED
        assert "Invalid input placeholder format" in mock_state.error

    @patch('app.tasks.create_next_state.GraphTemplate')
    @patch('app.tasks.create_next_state.RegisteredNode')
    @patch('app.tasks.create_next_state.State')
    async def test_create_next_state_input_placeholder_parent_not_found(
        self,
        mock_state_class,
        mock_registered_node_class,
        mock_graph_template_class,
        mock_state,
        mock_graph_template,
        mock_registered_node
    ):
        """Test error when placeholder references non-existent parent"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        
        node_template = MagicMock()
        node_template.next_nodes = ["node1"]
        
        next_node = MagicMock()
        next_node.identifier = "node1"
        next_node.node_name = "registered_node1"
        next_node.namespace = "test_namespace"
        next_node.inputs = {"field1": "${{nonexistent_parent.outputs.value}}"}
        next_node.unites = None
        
        mock_graph_template.get_node_by_identifier.side_effect = lambda x: {
            "test_node": node_template,
            "node1": next_node
        }.get(x)
        
        mock_registered_node_class.find_one = AsyncMock(return_value=mock_registered_node)
        
        # Parents don't include nonexistent_parent
        mock_state.parents = {"other_parent": PydanticObjectId()}
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        assert mock_state.status == StateStatusEnum.ERRORED
        assert "Parent identifier 'nonexistent_parent' not found in state parents" in mock_state.error

    @patch('app.tasks.create_next_state.GraphTemplate')
    @patch('app.tasks.create_next_state.RegisteredNode')
    @patch('app.tasks.create_next_state.State')
    async def test_create_next_state_input_placeholder_dependent_state_not_found(
        self,
        mock_state_class,
        mock_registered_node_class,
        mock_graph_template_class,
        mock_state,
        mock_graph_template,
        mock_registered_node
    ):
        """Test error when dependent state cannot be found"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        
        node_template = MagicMock()
        node_template.next_nodes = ["node1"]
        
        next_node = MagicMock()
        next_node.identifier = "node1"
        next_node.node_name = "registered_node1"
        next_node.namespace = "test_namespace"
        next_node.inputs = {"field1": "${{parent_node.outputs.value}}"}
        next_node.unites = None
        
        mock_graph_template.get_node_by_identifier.side_effect = lambda x: {
            "test_node": node_template,
            "node1": next_node
        }.get(x)
        
        mock_registered_node_class.find_one = AsyncMock(return_value=mock_registered_node)
        
        # Parent exists but state cannot be found
        parent_id = PydanticObjectId()
        mock_state.parents = {"parent_node": parent_id}
        mock_state_class.get = AsyncMock(return_value=None)
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        assert mock_state.status == StateStatusEnum.ERRORED
        assert "Dependent state parent_node not found" in mock_state.error

    @patch('app.tasks.create_next_state.GraphTemplate')
    @patch('app.tasks.create_next_state.RegisteredNode')
    @patch('app.tasks.create_next_state.State')
    async def test_create_next_state_input_placeholder_missing_output_field(
        self,
        mock_state_class,
        mock_registered_node_class,
        mock_graph_template_class,
        mock_state,
        mock_graph_template,
        mock_registered_node
    ):
        """Test error when output field doesn't exist in dependent state"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        
        node_template = MagicMock()
        node_template.next_nodes = ["node1"]
        
        next_node = MagicMock()
        next_node.identifier = "node1"
        next_node.node_name = "registered_node1"
        next_node.namespace = "test_namespace"
        next_node.inputs = {"field1": "${{parent_node.outputs.missing_field}}"}
        next_node.unites = None
        
        mock_graph_template.get_node_by_identifier.side_effect = lambda x: {
            "test_node": node_template,
            "node1": next_node
        }.get(x)
        
        mock_registered_node_class.find_one = AsyncMock(return_value=mock_registered_node)
        
        # Set up parent state with outputs that don't include missing_field
        parent_id = PydanticObjectId()
        parent_state = MagicMock()
        parent_state.outputs = {"existing_field": "value"}
        
        mock_state_class.get = AsyncMock(return_value=parent_state)
        mock_state.parents = {"parent_node": parent_id}
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        assert mock_state.status == StateStatusEnum.ERRORED
        assert "Input field missing_field not found in dependent state parent_node" in mock_state.error

    @patch('app.tasks.create_next_state.GraphTemplate')
    @patch('app.tasks.create_next_state.RegisteredNode')
    @patch('app.tasks.create_next_state.State')
    async def test_create_next_state_state_caching(
        self,
        mock_state_class,
        mock_registered_node_class,
        mock_graph_template_class,
        mock_state,
        mock_graph_template,
        mock_registered_node
    ):
        """Test that states are cached to avoid repeated database calls"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_graph_template)
        
        node_template = MagicMock()
        node_template.next_nodes = ["node1", "node2"]
        
        # Both next nodes reference the same parent
        next_node1 = MagicMock()
        next_node1.identifier = "node1"
        next_node1.node_name = "registered_node1"
        next_node1.namespace = "test_namespace"
        next_node1.inputs = {"field1": "${{parent_node.outputs.value}}"}
        next_node1.unites = None
        
        next_node2 = MagicMock()
        next_node2.identifier = "node2"
        next_node2.node_name = "registered_node2"
        next_node2.namespace = "test_namespace"
        next_node2.inputs = {"field1": "${{parent_node.outputs.value}}"}
        next_node2.unites = None
        
        mock_graph_template.get_node_by_identifier.side_effect = lambda x: {
            "test_node": node_template,
            "node1": next_node1,
            "node2": next_node2
        }.get(x)
        
        mock_registered_node_class.find_one = AsyncMock(return_value=mock_registered_node)
        
        # Set up parent state
        parent_id = PydanticObjectId()
        parent_state = MagicMock()
        parent_state.outputs = {"value": "cached_value"}
        
        mock_state_class.get = AsyncMock(return_value=parent_state)
        mock_state.parents = {"parent_node": parent_id}
        
        # Mock State creation
        mock_new_state = MagicMock()
        mock_new_state.save = AsyncMock()
        mock_state_class.return_value = mock_new_state
        
        # Act
        await create_next_state(mock_state)
        
        # Assert
        # State.get should only be called once due to caching
        assert mock_state_class.get.call_count == 1
        assert mock_state_class.call_count == 2  # Two new states created
        assert mock_state.status == StateStatusEnum.SUCCESS 