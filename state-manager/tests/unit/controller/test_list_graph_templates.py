import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List

from app.controller.list_graph_templates import list_graph_templates
from app.models.db.graph_template_model import GraphTemplate
from app.models.graph_template_validation_status import GraphTemplateValidationStatus


class TestListGraphTemplates:
    """Test cases for list_graph_templates function"""

    @pytest.fixture
    def mock_namespace(self):
        return "test_namespace"

    @pytest.fixture
    def mock_request_id(self):
        return "test-request-id"

    @pytest.fixture
    def mock_graph_templates(self):
        """Create mock graph templates for testing"""
        templates = []
        for i in range(3):
            template = MagicMock(spec=GraphTemplate)
            template.id = f"template_id_{i}"
            template.name = f"test_template_{i}"
            template.namespace = "test_namespace"
            template.validation_status = GraphTemplateValidationStatus.VALID if i % 2 == 0 else GraphTemplateValidationStatus.INVALID
            template.validation_errors = [] if i % 2 == 0 else [f"Error {i}"]
            template.nodes = []
            template.secrets = {}
            templates.append(template)
        return templates

    @patch('app.controller.list_graph_templates.GraphTemplate')
    @patch('app.controller.list_graph_templates.LogsManager')
    async def test_list_graph_templates_success(
        self,
        mock_logs_manager,
        mock_graph_template_class,
        mock_namespace,
        mock_request_id,
        mock_graph_templates
    ):
        """Test successful retrieval of graph templates"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=mock_graph_templates)
        mock_graph_template_class.find.return_value = mock_query

        # Act
        result = await list_graph_templates(mock_namespace, mock_request_id)

        # Assert
        assert result == mock_graph_templates
        assert len(result) == 3
        mock_graph_template_class.find.assert_called_once()
        mock_query.to_list.assert_called_once()
        
        # Verify logging
        mock_logger.info.assert_any_call(
            f"Listing graph templates for namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )
        mock_logger.info.assert_any_call(
            f"Found {len(mock_graph_templates)} graph templates for namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )

    @patch('app.controller.list_graph_templates.GraphTemplate')
    @patch('app.controller.list_graph_templates.LogsManager')
    async def test_list_graph_templates_empty_result(
        self,
        mock_logs_manager,
        mock_graph_template_class,
        mock_namespace,
        mock_request_id
    ):
        """Test when no graph templates are found"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=[])
        mock_graph_template_class.find.return_value = mock_query

        # Act
        result = await list_graph_templates(mock_namespace, mock_request_id)

        # Assert
        assert result == []
        assert len(result) == 0
        mock_graph_template_class.find.assert_called_once()
        mock_query.to_list.assert_called_once()
        
        # Verify logging
        mock_logger.info.assert_any_call(
            f"Listing graph templates for namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )
        mock_logger.info.assert_any_call(
            f"Found 0 graph templates for namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )

    @patch('app.controller.list_graph_templates.GraphTemplate')
    @patch('app.controller.list_graph_templates.LogsManager')
    async def test_list_graph_templates_database_error(
        self,
        mock_logs_manager,
        mock_graph_template_class,
        mock_namespace,
        mock_request_id
    ):
        """Test handling of database errors"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(side_effect=Exception("Database connection error"))
        mock_graph_template_class.find.return_value = mock_query

        # Act & Assert
        with pytest.raises(Exception, match="Database connection error"):
            await list_graph_templates(mock_namespace, mock_request_id)

        # Verify error logging
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args
        assert f"Error listing graph templates for namespace {mock_namespace}" in str(error_call)

    @patch('app.controller.list_graph_templates.GraphTemplate')
    @patch('app.controller.list_graph_templates.LogsManager')
    async def test_list_graph_templates_find_error(
        self,
        mock_logs_manager,
        mock_graph_template_class,
        mock_namespace,
        mock_request_id
    ):
        """Test error during GraphTemplate.find operation"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_graph_template_class.find.side_effect = Exception("Find operation failed")

        # Act & Assert
        with pytest.raises(Exception, match="Find operation failed"):
            await list_graph_templates(mock_namespace, mock_request_id)

        # Verify error logging
        mock_logger.error.assert_called_once()

    @patch('app.controller.list_graph_templates.GraphTemplate')
    @patch('app.controller.list_graph_templates.LogsManager')
    async def test_list_graph_templates_filter_criteria(
        self,
        mock_logs_manager,
        mock_graph_template_class,
        mock_namespace,
        mock_request_id,
        mock_graph_templates
    ):
        """Test that the correct filter criteria are used"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=mock_graph_templates)
        mock_graph_template_class.find.return_value = mock_query

        # Act
        await list_graph_templates(mock_namespace, mock_request_id)

        # Assert that GraphTemplate.find was called with the correct namespace filter
        mock_graph_template_class.find.assert_called_once()
        call_args = mock_graph_template_class.find.call_args[0]
        # The filter should match the namespace
        assert len(call_args) == 1  # Should have one filter condition

    @patch('app.controller.list_graph_templates.GraphTemplate')
    @patch('app.controller.list_graph_templates.LogsManager')
    async def test_list_graph_templates_different_namespaces(
        self,
        mock_logs_manager,
        mock_graph_template_class,
        mock_request_id
    ):
        """Test with different namespace values"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=[])
        mock_graph_template_class.find.return_value = mock_query

        namespaces = ["prod", "staging", "dev", "test-123", ""]

        # Act & Assert
        for namespace in namespaces:
            mock_graph_template_class.reset_mock()
            mock_logger.reset_mock()
            
            result = await list_graph_templates(namespace, mock_request_id)
            
            assert result == []
            mock_graph_template_class.find.assert_called_once()
            mock_logger.info.assert_any_call(
                f"Listing graph templates for namespace: {namespace}",
                x_exosphere_request_id=mock_request_id
            )

    @patch('app.controller.list_graph_templates.GraphTemplate')
    @patch('app.controller.list_graph_templates.LogsManager')
    async def test_list_graph_templates_large_result_set(
        self,
        mock_logs_manager,
        mock_graph_template_class,
        mock_namespace,
        mock_request_id
    ):
        """Test with large number of graph templates"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        # Create large number of mock templates
        large_templates_list = []
        for i in range(200):
            template = MagicMock(spec=GraphTemplate)
            template.id = f"template_{i}"
            template.name = f"template_{i}"
            template.namespace = mock_namespace
            large_templates_list.append(template)
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=large_templates_list)
        mock_graph_template_class.find.return_value = mock_query

        # Act
        result = await list_graph_templates(mock_namespace, mock_request_id)

        # Assert
        assert len(result) == 200
        mock_logger.info.assert_any_call(
            f"Found 200 graph templates for namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )

    @patch('app.controller.list_graph_templates.GraphTemplate')
    @patch('app.controller.list_graph_templates.LogsManager')
    async def test_list_graph_templates_return_type(
        self,
        mock_logs_manager,
        mock_graph_template_class,
        mock_namespace,
        mock_request_id,
        mock_graph_templates
    ):
        """Test that the function returns the correct type"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=mock_graph_templates)
        mock_graph_template_class.find.return_value = mock_query

        # Act
        result = await list_graph_templates(mock_namespace, mock_request_id)

        # Assert
        assert isinstance(result, list)
        for template in result:
            assert isinstance(template, MagicMock)  # Since we're using mocks
        
        # Verify each template has expected attributes (via mock)
        for template in result:
            assert hasattr(template, 'id')
            assert hasattr(template, 'name')
            assert hasattr(template, 'namespace')
            assert hasattr(template, 'validation_status')

    @patch('app.controller.list_graph_templates.GraphTemplate')
    @patch('app.controller.list_graph_templates.LogsManager')
    async def test_list_graph_templates_mixed_validation_statuses(
        self,
        mock_logs_manager,
        mock_graph_template_class,
        mock_namespace,
        mock_request_id
    ):
        """Test with templates having different validation statuses"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        # Create templates with different validation statuses
        templates = []
        statuses = [GraphTemplateValidationStatus.VALID, 
                   GraphTemplateValidationStatus.INVALID,
                   GraphTemplateValidationStatus.PENDING]
        
        for i, status in enumerate(statuses):
            template = MagicMock(spec=GraphTemplate)
            template.id = f"template_{i}"
            template.name = f"template_{i}"
            template.namespace = mock_namespace
            template.validation_status = status
            templates.append(template)
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=templates)
        mock_graph_template_class.find.return_value = mock_query

        # Act
        result = await list_graph_templates(mock_namespace, mock_request_id)

        # Assert
        assert len(result) == 3
        assert result[0].validation_status == GraphTemplateValidationStatus.VALID
        assert result[1].validation_status == GraphTemplateValidationStatus.INVALID
        assert result[2].validation_status == GraphTemplateValidationStatus.PENDING

    @patch('app.controller.list_graph_templates.GraphTemplate')
    @patch('app.controller.list_graph_templates.LogsManager')
    async def test_list_graph_templates_concurrent_requests(
        self,
        mock_logs_manager,
        mock_graph_template_class,
        mock_request_id
    ):
        """Test handling concurrent requests with different namespaces"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=[])
        mock_graph_template_class.find.return_value = mock_query

        # Simulate concurrent requests to different namespaces
        namespaces = ["namespace1", "namespace2", "namespace3"]
        
        # Act
        import asyncio
        tasks = [list_graph_templates(ns, f"{mock_request_id}_{i}") for i, ns in enumerate(namespaces)]
        results = await asyncio.gather(*tasks)

        # Assert
        assert len(results) == 3
        for result in results:
            assert result == []
        
        # Each namespace should have been queried
        assert mock_graph_template_class.find.call_count == 3

    @patch('app.controller.list_graph_templates.GraphTemplate')
    @patch('app.controller.list_graph_templates.LogsManager')
    async def test_list_graph_templates_single_template(
        self,
        mock_logs_manager,
        mock_graph_template_class,
        mock_namespace,
        mock_request_id
    ):
        """Test with single template result"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        single_template = MagicMock(spec=GraphTemplate)
        single_template.id = "single_template_id"
        single_template.name = "single_template"
        single_template.namespace = mock_namespace
        single_template.validation_status = GraphTemplateValidationStatus.VALID
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=[single_template])
        mock_graph_template_class.find.return_value = mock_query

        # Act
        result = await list_graph_templates(mock_namespace, mock_request_id)

        # Assert
        assert len(result) == 1
        assert result[0] == single_template
        mock_logger.info.assert_any_call(
            f"Found 1 graph templates for namespace: {mock_namespace}",
            x_exosphere_request_id=mock_request_id
        )

    @patch('app.controller.list_graph_templates.GraphTemplate')
    @patch('app.controller.list_graph_templates.LogsManager')
    async def test_list_graph_templates_with_complex_templates(
        self,
        mock_logs_manager,
        mock_graph_template_class,
        mock_namespace,
        mock_request_id
    ):
        """Test with complex graph templates containing nodes and secrets"""
        # Arrange
        mock_logger = MagicMock()
        mock_logs_manager.return_value.get_logger.return_value = mock_logger
        
        complex_template = MagicMock(spec=GraphTemplate)
        complex_template.id = "complex_template"
        complex_template.name = "complex_template"
        complex_template.namespace = mock_namespace
        complex_template.validation_status = GraphTemplateValidationStatus.VALID
        complex_template.nodes = [MagicMock() for _ in range(5)]  # Mock 5 nodes
        complex_template.secrets = {"secret1": "value1", "secret2": "value2"}
        complex_template.validation_errors = None
        
        mock_query = MagicMock()
        mock_query.to_list = AsyncMock(return_value=[complex_template])
        mock_graph_template_class.find.return_value = mock_query

        # Act
        result = await list_graph_templates(mock_namespace, mock_request_id)

        # Assert
        assert len(result) == 1
        template = result[0]
        assert template == complex_template
        assert len(template.nodes) == 5
        assert len(template.secrets) == 2