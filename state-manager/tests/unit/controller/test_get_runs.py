import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.controller.get_runs import get_runs, get_run_status, get_run_info
from app.models.db.run import Run
from app.models.run_models import RunsResponse, RunListItem, RunStatusEnum


class TestGetRunStatus:
    """Test cases for get_run_status function"""

    @pytest.mark.asyncio
    async def test_get_run_status_failed(self):
        """Test get_run_status returns FAILED when there are errored states"""
        run_id = "test_run_id"
        
        with patch('app.controller.get_runs.State') as mock_state_class:
            # Mock count to return > 0 for errored states
            mock_state_class.find.return_value.count = AsyncMock(return_value=1)
            
            result = await get_run_status(run_id)
            
            assert result == RunStatusEnum.FAILED
            mock_state_class.find.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_run_status_success(self):
        """Test get_run_status returns SUCCESS when all states are completed"""
        run_id = "test_run_id"
        
        with patch('app.controller.get_runs.State') as mock_state_class:
            # Mock count to return 0 for errored states and 0 for pending states
            mock_state_class.find.side_effect = [
                MagicMock(count=AsyncMock(return_value=0)),  # First call for errored states
                MagicMock(count=AsyncMock(return_value=0))   # Second call for pending states
            ]
            
            result = await get_run_status(run_id)
            
            assert result == RunStatusEnum.SUCCESS
            assert mock_state_class.find.call_count == 2

    @pytest.mark.asyncio
    async def test_get_run_status_pending(self):
        """Test get_run_status returns PENDING when there are pending states"""
        run_id = "test_run_id"
        
        with patch('app.controller.get_runs.State') as mock_state_class:
            # Mock count to return 0 for errored states but > 0 for pending states
            mock_state_class.find.side_effect = [
                MagicMock(count=AsyncMock(return_value=0)),  # First call for errored states
                MagicMock(count=AsyncMock(return_value=1))   # Second call for pending states
            ]
            
            result = await get_run_status(run_id)
            
            assert result == RunStatusEnum.PENDING
            assert mock_state_class.find.call_count == 2

    @pytest.mark.asyncio
    async def test_get_run_status_multiple_errored_states(self):
        """Test get_run_status with multiple errored states"""
        run_id = "test_run_id"
        
        with patch('app.controller.get_runs.State') as mock_state_class:
            mock_state_class.find.return_value.count = AsyncMock(return_value=5)
            
            result = await get_run_status(run_id)
            
            assert result == RunStatusEnum.FAILED

    @pytest.mark.asyncio
    async def test_get_run_status_mixed_states(self):
        """Test get_run_status with mixed state statuses"""
        run_id = "test_run_id"
        
        with patch('app.controller.get_runs.State') as mock_state_class:
            # Mock count to return 0 for errored states but > 0 for pending states
            mock_state_class.find.side_effect = [
                MagicMock(count=AsyncMock(return_value=0)),  # First call for errored states
                MagicMock(count=AsyncMock(return_value=3))   # Second call for pending states
            ]
            
            result = await get_run_status(run_id)
            
            assert result == RunStatusEnum.PENDING


class TestGetRunInfo:
    """Test cases for get_run_info function"""

    @pytest.fixture
    def mock_run(self):
        """Create a mock Run object"""
        run = MagicMock(spec=Run)
        run.run_id = "test_run_id"
        run.graph_name = "test_graph"
        run.created_at = datetime.now()
        return run

    @pytest.mark.asyncio
    async def test_get_run_info_success(self, mock_run):
        """Test get_run_info returns correct RunListItem"""
        with patch('app.controller.get_runs.State') as mock_state_class:
            # Mock different count queries
            mock_state_class.find.side_effect = [
                MagicMock(count=AsyncMock(return_value=5)),  # success_count
                MagicMock(count=AsyncMock(return_value=2)),  # pending_count
                MagicMock(count=AsyncMock(return_value=0)),  # errored_count
                MagicMock(count=AsyncMock(return_value=1)),  # retried_count
                MagicMock(count=AsyncMock(return_value=8)),  # total_count
            ]
            
            with patch('app.controller.get_runs.get_run_status') as mock_get_status:
                mock_get_status.return_value = RunStatusEnum.SUCCESS
                
                result = await get_run_info(mock_run)
                
                assert isinstance(result, RunListItem)
                assert result.run_id == "test_run_id"
                assert result.graph_name == "test_graph"
                assert result.success_count == 5
                assert result.pending_count == 2
                assert result.errored_count == 0
                assert result.retried_count == 1
                assert result.total_count == 8
                assert result.status == RunStatusEnum.SUCCESS
                assert result.created_at == mock_run.created_at

    @pytest.mark.asyncio
    async def test_get_run_info_with_errored_states(self, mock_run):
        """Test get_run_info with errored states"""
        with patch('app.controller.get_runs.State') as mock_state_class:
            mock_state_class.find.side_effect = [
                MagicMock(count=AsyncMock(return_value=3)),  # success_count
                MagicMock(count=AsyncMock(return_value=1)),  # pending_count
                MagicMock(count=AsyncMock(return_value=2)),  # errored_count
                MagicMock(count=AsyncMock(return_value=0)),  # retried_count
                MagicMock(count=AsyncMock(return_value=6)),  # total_count
            ]
            
            with patch('app.controller.get_runs.get_run_status') as mock_get_status:
                mock_get_status.return_value = RunStatusEnum.FAILED
                
                result = await get_run_info(mock_run)
                
                assert result.errored_count == 2
                assert result.status == RunStatusEnum.FAILED

    @pytest.mark.asyncio
    async def test_get_run_info_with_pending_states(self, mock_run):
        """Test get_run_info with pending states"""
        with patch('app.controller.get_runs.State') as mock_state_class:
            mock_state_class.find.side_effect = [
                MagicMock(count=AsyncMock(return_value=2)),  # success_count
                MagicMock(count=AsyncMock(return_value=4)),  # pending_count
                MagicMock(count=AsyncMock(return_value=0)),  # errored_count
                MagicMock(count=AsyncMock(return_value=1)),  # retried_count
                MagicMock(count=AsyncMock(return_value=7)),  # total_count
            ]
            
            with patch('app.controller.get_runs.get_run_status') as mock_get_status:
                mock_get_status.return_value = RunStatusEnum.PENDING
                
                result = await get_run_info(mock_run)
                
                assert result.pending_count == 4
                assert result.status == RunStatusEnum.PENDING

    @pytest.mark.asyncio
    async def test_get_run_info_zero_counts(self, mock_run):
        """Test get_run_info with zero counts"""
        with patch('app.controller.get_runs.State') as mock_state_class:
            mock_state_class.find.side_effect = [
                MagicMock(count=AsyncMock(return_value=0)),  # success_count
                MagicMock(count=AsyncMock(return_value=0)),  # pending_count
                MagicMock(count=AsyncMock(return_value=0)),  # errored_count
                MagicMock(count=AsyncMock(return_value=0)),  # retried_count
                MagicMock(count=AsyncMock(return_value=0)),  # total_count
            ]
            
            with patch('app.controller.get_runs.get_run_status') as mock_get_status:
                mock_get_status.return_value = RunStatusEnum.SUCCESS
                
                result = await get_run_info(mock_run)
                
                assert result.success_count == 0
                assert result.pending_count == 0
                assert result.errored_count == 0
                assert result.retried_count == 0
                assert result.total_count == 0


class TestGetRuns:
    """Test cases for get_runs function"""

    @pytest.fixture
    def mock_request_id(self):
        return "test_request_id"

    @pytest.fixture
    def mock_namespace(self):
        return "test_namespace"

    @pytest.fixture
    def mock_runs(self):
        """Create mock Run objects"""
        runs = []
        for i in range(3):
            run = MagicMock(spec=Run)
            run.run_id = f"run_{i}"
            run.graph_name = f"graph_{i}"
            run.created_at = datetime.now()
            runs.append(run)
        return runs

    @pytest.mark.asyncio
    async def test_get_runs_success(self, mock_namespace, mock_request_id, mock_runs):
        """Test successful retrieval of runs"""
        page = 1
        size = 10
        
        with patch('app.controller.get_runs.Run') as mock_run_class, \
             patch('app.controller.get_runs.get_run_info') as mock_get_run_info, \
             patch('app.controller.get_runs.logger') as mock_logger:
            
            # Mock the entire query chain for runs list
            mock_query_chain = MagicMock()
            mock_query_chain.to_list = AsyncMock(return_value=mock_runs)
            mock_run_class.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_query_chain
            
            # Mock the count query separately
            mock_count_query = MagicMock()
            mock_count_query.count = AsyncMock(return_value=25)
            # Use side_effect to return different mocks for different calls
            mock_run_class.find.side_effect = [
                mock_run_class.find.return_value,  # First call for runs list
                mock_count_query  # Second call for count
            ]
            
            # Mock get_run_info for each run
            mock_run_items = []
            for i, run in enumerate(mock_runs):
                mock_item = MagicMock(spec=RunListItem)
                mock_item.run_id = run.run_id
                mock_item.graph_name = run.graph_name
                mock_run_items.append(mock_item)
            
            mock_get_run_info.side_effect = mock_run_items
            
            result = await get_runs(mock_namespace, page, size, mock_request_id)
            
            # Verify result
            assert isinstance(result, RunsResponse)
            assert result.namespace == mock_namespace
            assert result.total == 25
            assert result.page == page
            assert result.size == size
            assert len(result.runs) == 3
            
            # Verify logging
            mock_logger.info.assert_called_once_with(
                f"Getting runs for namespace {mock_namespace}",
                x_exosphere_request_id=mock_request_id
            )

    @pytest.mark.asyncio
    async def test_get_runs_pagination(self, mock_namespace, mock_request_id, mock_runs):
        """Test get_runs with different pagination parameters"""
        page = 2
        size = 5
        
        with patch('app.controller.get_runs.Run') as mock_run_class, \
             patch('app.controller.get_runs.get_run_info') as mock_get_run_info, \
             patch('app.controller.get_runs.logger') as _:
            
            # Mock the entire query chain for runs list
            mock_query_chain = MagicMock()
            mock_query_chain.to_list = AsyncMock(return_value=mock_runs)
            mock_run_class.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_query_chain
            
            # Mock the count query separately
            mock_count_query = MagicMock()
            mock_count_query.count = AsyncMock(return_value=15)
            mock_run_class.find.side_effect = [
                mock_run_class.find.return_value,  # First call for runs list
                mock_count_query  # Second call for count
            ]
            
            mock_get_run_info.side_effect = [MagicMock(spec=RunListItem) for _ in mock_runs]
            
            result = await get_runs(mock_namespace, page, size, mock_request_id)
            
            assert result.page == page
            assert result.size == size
            assert result.total == 15

    @pytest.mark.asyncio
    async def test_get_runs_empty_result(self, mock_namespace, mock_request_id):
        """Test get_runs when no runs are found"""
        page = 1
        size = 10
        
        with patch('app.controller.get_runs.Run') as mock_run_class, \
             patch('app.controller.get_runs.logger') as _:
            
            # Mock the entire query chain for runs list
            mock_query_chain = MagicMock()
            mock_query_chain.to_list = AsyncMock(return_value=[])
            mock_run_class.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_query_chain
            
            # Mock the count query separately
            mock_count_query = MagicMock()
            mock_count_query.count = AsyncMock(return_value=0)
            mock_run_class.find.side_effect = [
                mock_run_class.find.return_value,  # First call for runs list
                mock_count_query  # Second call for count
            ]
            
            result = await get_runs(mock_namespace, page, size, mock_request_id)
            
            assert result.runs == []
            assert result.total == 0

    @pytest.mark.asyncio
    async def test_get_runs_exception_handling(self, mock_namespace, mock_request_id):
        """Test get_runs exception handling"""
        page = 1
        size = 10
        
        with patch('app.controller.get_runs.Run') as mock_run_class, \
             patch('app.controller.get_runs.logger') as mock_logger:
            
            # Simulate database error
            mock_run_class.find.side_effect = Exception("Database connection error")
            
            with pytest.raises(Exception, match="Database connection error"):
                await get_runs(mock_namespace, page, size, mock_request_id)
            
            # Verify error logging
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args
            assert f"Error getting runs for namespace {mock_namespace}" in str(error_call)

    @pytest.mark.asyncio
    async def test_get_runs_different_namespaces(self, mock_request_id):
        """Test get_runs with different namespace values"""
        page = 1
        size = 10
        namespaces = ["prod", "staging", "dev", "test-123", ""]
        
        for namespace in namespaces:
            with patch('app.controller.get_runs.Run') as mock_run_class, \
                 patch('app.controller.get_runs.get_run_info') as _, \
                 patch('app.controller.get_runs.logger') as _:
                
                # Mock the entire query chain for runs list
                mock_query_chain = MagicMock()
                mock_query_chain.to_list = AsyncMock(return_value=[])
                mock_run_class.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_query_chain

                # Mock the count query separately
                mock_count_query = MagicMock()
                mock_count_query.count = AsyncMock(return_value=0)
                mock_run_class.find.side_effect = [
                    mock_run_class.find.return_value,  # First call for runs list
                    mock_count_query  # Second call for count
                ]
                
                result = await get_runs(namespace, page, size, mock_request_id)
                
                assert result.namespace == namespace
                assert result.total == 0

    @pytest.mark.asyncio
    async def test_get_runs_large_page_size(self, mock_namespace, mock_request_id):
        """Test get_runs with large page size"""
        page = 1
        size = 1000
        
        # Create many mock runs
        large_runs_list = []
        for i in range(1000):
            run = MagicMock(spec=Run)
            run.run_id = f"run_{i}"
            run.graph_name = f"graph_{i}"
            run.created_at = datetime.now()
            large_runs_list.append(run)
        
        with patch('app.controller.get_runs.Run') as mock_run_class, \
             patch('app.controller.get_runs.get_run_info') as mock_get_run_info, \
             patch('app.controller.get_runs.logger') as _:
            
                        # Mock the entire query chain for runs list
            mock_query_chain = MagicMock()
            mock_query_chain.to_list = AsyncMock(return_value=large_runs_list)
            mock_run_class.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_query_chain

            # Mock the count query separately
            mock_count_query = MagicMock()
            mock_count_query.count = AsyncMock(return_value=1000)
            mock_run_class.find.side_effect = [
                mock_run_class.find.return_value,  # First call for runs list
                mock_count_query  # Second call for count
            ]
            
            mock_get_run_info.side_effect = [MagicMock(spec=RunListItem) for _ in large_runs_list]
            
            result = await get_runs(mock_namespace, page, size, mock_request_id)
            
            assert len(result.runs) == 1000
            assert result.total == 1000

    @pytest.mark.asyncio
    async def test_get_runs_edge_case_page_zero(self, mock_namespace, mock_request_id):
        """Test get_runs with edge case page=0 (should be treated as page=1)"""
        page = 0
        size = 10
        
        with patch('app.controller.get_runs.Run') as mock_run_class, \
             patch('app.controller.get_runs.get_run_info') as _, \
             patch('app.controller.get_runs.logger') as _:
            
            # Mock the entire query chain for runs list
            mock_query_chain = MagicMock()
            mock_query_chain.to_list = AsyncMock(return_value=[])
            mock_run_class.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_query_chain

            # Mock the count query separately
            mock_count_query = MagicMock()
            mock_count_query.count = AsyncMock(return_value=0)
            mock_run_class.find.side_effect = [
                mock_run_class.find.return_value,  # First call for runs list
                mock_count_query  # Second call for count
            ]
            
            result = await get_runs(mock_namespace, page, size, mock_request_id)
            
            assert result.page == page
            assert result.size == size

    @pytest.mark.asyncio
    async def test_get_runs_edge_case_size_zero(self, mock_namespace, mock_request_id):
        """Test get_runs with edge case size=0"""
        page = 1
        size = 0
        
        with patch('app.controller.get_runs.Run') as mock_run_class, \
             patch('app.controller.get_runs.get_run_info') as _, \
             patch('app.controller.get_runs.logger') as _:
            
            # Mock the entire query chain for runs list
            mock_query_chain = MagicMock()
            mock_query_chain.to_list = AsyncMock(return_value=[])
            mock_run_class.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_query_chain

            # Mock the count query separately
            mock_count_query = MagicMock()
            mock_count_query.count = AsyncMock(return_value=0)
            mock_run_class.find.side_effect = [
                mock_run_class.find.return_value,  # First call for runs list
                mock_count_query  # Second call for count
            ]
            
            result = await get_runs(mock_namespace, page, size, mock_request_id)
            
            assert result.page == page
            assert result.size == size 