from time import sleep
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.controller.upsert_graph_template import upsert_graph_template
from app.models.graph_models import UpsertGraphTemplateRequest
from app.models.graph_template_validation_status import GraphTemplateValidationStatus
from app.models.node_template_model import NodeTemplate
from app.models.retry_policy_model import RetryPolicyModel
from app.models.store_config_model import StoreConfig


class TestUpsertGraphTemplate:
    """Test cases for upsert_graph_template function"""

    @pytest.fixture
    def mock_request_id(self):
        return "test-request-id"

    @pytest.fixture
    def mock_namespace(self):
        return "test_namespace"

    @pytest.fixture
    def mock_graph_name(self):
        return "test_graph"

    @pytest.fixture
    def mock_background_tasks(self):
        return MagicMock()

    @pytest.fixture
    def mock_nodes(self):
        return [
            NodeTemplate(
                identifier="node1",
                node_name="Test Node 1",
                namespace="test_namespace",
                inputs={},
                next_nodes=[],
                unites=None
            ),
            NodeTemplate(
                identifier="node2",
                node_name="Test Node 2",
                namespace="test_namespace",
                inputs={},
                next_nodes=[],
                unites=None
            )
        ]

    @pytest.fixture
    def mock_secrets(self):
        return {
            "api_key": "encrypted_api_key",
            "database_url": "encrypted_db_url"
        }

    @pytest.fixture
    def mock_upsert_request(self, mock_nodes, mock_secrets):
        return UpsertGraphTemplateRequest(
            nodes=mock_nodes,
            secrets=mock_secrets
        )

    @pytest.fixture
    def mock_existing_template(self, mock_nodes, mock_secrets):
        template = MagicMock()
        template.nodes = mock_nodes
        template.validation_status = GraphTemplateValidationStatus.VALID
        template.validation_errors = []
        template.secrets = mock_secrets
        template.created_at = datetime(2023, 1, 1, 12, 0, 0)
        template.updated_at = datetime(2023, 1, 2, 12, 0, 0)
        template.get_secrets.return_value = mock_secrets
        template.set_secrets.return_value = template
        
        # Add proper retry_policy using real RetryPolicyModel
        template.retry_policy = RetryPolicyModel(
            max_retries=3,
            backoff_factor=1000,
            max_delay=30000
        )
        
        # Add store_config
        template.store_config = StoreConfig()
        
        return template

    @patch('app.controller.upsert_graph_template.GraphTemplate')
    @patch('app.controller.upsert_graph_template.verify_graph')
    async def test_upsert_graph_template_update_existing(
        self,
        mock_verify_graph,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_upsert_request,
        mock_existing_template,
        mock_background_tasks,
        mock_request_id
    ):
        """Test successful update of existing graph template"""
        # Arrange

        mock_existing_template.save = AsyncMock()
        mock_existing_template.set_secrets = MagicMock(return_value=mock_existing_template)
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_existing_template)

        # Act
        result = await upsert_graph_template(
            mock_namespace,
            mock_graph_name,
            mock_upsert_request,
            mock_request_id,
            mock_background_tasks
        )

        sleep(1) # wait for the background task to complete

        # Assert
        assert result.nodes == mock_upsert_request.nodes
        assert result.validation_status == GraphTemplateValidationStatus.PENDING
        assert result.validation_errors == []
        assert result.secrets == {"api_key": True, "database_url": True}
        assert result.created_at == mock_existing_template.created_at
        assert result.updated_at == mock_existing_template.updated_at

        # Verify template was updated
        mock_existing_template.set_secrets.assert_called_once_with(mock_upsert_request.secrets)
        mock_existing_template.save.assert_called_once()
        
        # Verify background task was added - the old_triggers should be the original triggers before update
        # Since we're setting triggers in the test, we use the original triggers (which would be stored before the update)
        mock_background_tasks.add_task.assert_called_once()

    @patch('app.controller.upsert_graph_template.GraphTemplate')
    @patch('app.controller.upsert_graph_template.verify_graph')
    async def test_upsert_graph_template_create_new(
        self,
        mock_verify_graph,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_upsert_request,
        mock_background_tasks,
        mock_request_id
    ):
        """Test successful creation of new graph template"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(return_value=None)  # Template doesn't exist
        
        mock_new_template = MagicMock()
        mock_new_template.nodes = mock_upsert_request.nodes
        mock_new_template.validation_status = GraphTemplateValidationStatus.PENDING
        mock_new_template.validation_errors = []
        mock_new_template.secrets = mock_upsert_request.secrets
        mock_new_template.created_at = datetime(2023, 1, 1, 12, 0, 0)
        mock_new_template.updated_at = datetime(2023, 1, 1, 12, 0, 0)
        mock_new_template.get_secrets.return_value = mock_upsert_request.secrets
        mock_new_template.set_secrets.return_value = mock_new_template
        
        # Add proper retry_policy mock
        mock_retry_policy = RetryPolicyModel(
            max_retries=3,
            backoff_factor=1000,
            max_delay=30000
        )
        mock_new_template.retry_policy = mock_retry_policy
        
        # Add store_config
        mock_new_template.store_config = StoreConfig()
        
        mock_graph_template_class.insert = AsyncMock(return_value=mock_new_template)

        # Act
        result = await upsert_graph_template(
            mock_namespace,
            mock_graph_name,
            mock_upsert_request,
            mock_request_id,
            mock_background_tasks
        )

        # Assert
        assert result.nodes == mock_upsert_request.nodes
        assert result.validation_status == GraphTemplateValidationStatus.PENDING
        assert result.validation_errors == []
        assert result.secrets == {"api_key": True, "database_url": True}

        # Verify new template was created
        mock_graph_template_class.insert.assert_called_once()
        
        # Verify background task was added
        mock_background_tasks.add_task.assert_called_once_with(mock_verify_graph, mock_new_template, [])

    @patch('app.controller.upsert_graph_template.GraphTemplate')
    async def test_upsert_graph_template_database_error(
        self,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_upsert_request,
        mock_background_tasks,
        mock_request_id
    ):
        """Test handling of database errors"""
        # Arrange
        mock_graph_template_class.find_one = AsyncMock(side_effect=Exception("Database error"))

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await upsert_graph_template(
                mock_namespace,
                mock_graph_name,
                mock_upsert_request,
                mock_request_id,
                mock_background_tasks
            )
        
        assert str(exc_info.value) == "Database error"

    @patch('app.controller.upsert_graph_template.GraphTemplate')
    @patch('app.controller.upsert_graph_template.verify_graph')
    async def test_upsert_graph_template_with_empty_nodes(
        self,
        mock_verify_graph,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_background_tasks,
        mock_request_id
    ):
        """Test upsert with empty nodes list"""
        # Arrange
        upsert_request = UpsertGraphTemplateRequest(
            nodes=[],
            secrets={}
        )
        
        mock_existing_template = MagicMock()
        mock_existing_template.nodes = []
        mock_existing_template.validation_status = GraphTemplateValidationStatus.VALID
        mock_existing_template.validation_errors = []
        mock_existing_template.secrets = {}
        mock_existing_template.created_at = datetime(2023, 1, 1, 12, 0, 0)
        mock_existing_template.updated_at = datetime(2023, 1, 2, 12, 0, 0)
        mock_existing_template.get_secrets.return_value = {}
        mock_existing_template.set_secrets.return_value = mock_existing_template
        
                # Add proper retry_policy mock
        mock_retry_policy = RetryPolicyModel(
            max_retries=3,
            backoff_factor=1000,
            max_delay=30000
        )
        mock_existing_template.retry_policy = mock_retry_policy
        
        # Add store_config
        mock_existing_template.store_config = StoreConfig()

        mock_existing_template.save = AsyncMock()

        mock_graph_template_class.find_one = AsyncMock(return_value=mock_existing_template)

        # Act
        result = await upsert_graph_template(
            mock_namespace,
            mock_graph_name,
            upsert_request,
            mock_request_id,
            mock_background_tasks
        )
        
        sleep(1) # wait for the background task to complete
        # Assert
        assert result.nodes == []
        assert result.validation_status == GraphTemplateValidationStatus.PENDING
        assert result.validation_errors == []
        assert result.secrets == {}

    @patch('app.controller.upsert_graph_template.GraphTemplate')
    @patch('app.controller.upsert_graph_template.verify_graph')
    async def test_upsert_graph_template_with_validation_errors(
        self,
        mock_verify_graph,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_upsert_request,
        mock_background_tasks,
        mock_request_id
    ):
        """Test upsert with existing validation errors"""
        # Arrange
        mock_existing_template = MagicMock()
        mock_existing_template.nodes = mock_upsert_request.nodes
        mock_existing_template.validation_status = GraphTemplateValidationStatus.INVALID
        mock_existing_template.validation_errors = ["Previous error 1", "Previous error 2"]
        mock_existing_template.secrets = mock_upsert_request.secrets
        mock_existing_template.created_at = datetime(2023, 1, 1, 12, 0, 0)
        mock_existing_template.updated_at = datetime(2023, 1, 2, 12, 0, 0)
        mock_existing_template.get_secrets.return_value = mock_upsert_request.secrets
        mock_existing_template.set_secrets.return_value = mock_existing_template

        # Add proper retry_policy mock
        mock_retry_policy = RetryPolicyModel(
            max_retries=3,
            backoff_factor=1000,
            max_delay=30000
        )
        mock_existing_template.retry_policy = mock_retry_policy
        
        # Add store_config
        mock_existing_template.store_config = StoreConfig()

        mock_existing_template.save = AsyncMock()
        
        mock_graph_template_class.find_one = AsyncMock(return_value=mock_existing_template)

        # Act
        result = await upsert_graph_template(
            mock_namespace,
            mock_graph_name,
            mock_upsert_request,
            mock_request_id,
            mock_background_tasks
        )

        sleep(1) # wait for the background task to complete

        # Assert
        assert result.validation_status == GraphTemplateValidationStatus.PENDING
        assert result.validation_errors == []  # Should be reset to empty

    @patch('app.controller.upsert_graph_template.GraphTemplate')
    async def test_upsert_graph_template_validation_error(
        self,
        mock_graph_template_class,
        mock_namespace,
        mock_graph_name,
        mock_background_tasks,
        mock_request_id
    ):
        """Test upsert with validation error during template creation"""
        from fastapi import HTTPException
        
        # Arrange - Create a request with valid data
        valid_nodes = [
            NodeTemplate(
                identifier="node1",
                node_name="test_node",
                namespace="test_namespace",
                inputs={},
                next_nodes=[],
                unites=None
            )
        ]
        
        valid_request = UpsertGraphTemplateRequest(
            nodes=valid_nodes,
            secrets={"secret1": "value1"}
        )
        
        # Mock find_one to return None (new template creation)
        mock_graph_template_class.find_one = AsyncMock(return_value=None)
        
        # Mock insert to raise ValueError during validation (this simulates validation error in GraphTemplate)
        mock_graph_template_class.insert = AsyncMock(side_effect=ValueError("Node identifier node1 is not unique"))

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await upsert_graph_template(
                mock_namespace,
                mock_graph_name,
                valid_request,
                mock_request_id,
                mock_background_tasks
            )
        
        assert exc_info.value.status_code == 400
        assert "Error validating graph template: Node identifier node1 is not unique" in str(exc_info.value.detail)
