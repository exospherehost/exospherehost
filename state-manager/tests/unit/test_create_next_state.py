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