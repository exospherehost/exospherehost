import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.controller.get_runs import get_runs
from app.models.db.run import Run
from app.models.run_models import RunsResponse, RunStatusEnum
from app.models.state_status_enum import StateStatusEnum


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
            run.created_at = datetime(2024, 1, 15, 10 + i, 30, 0)
            runs.append(run)
        return runs

    @pytest.fixture
    def mock_aggregation_data(self):
        """Create mock aggregation data that matches the MongoDB aggregation pipeline output"""
        return [
            {
                "_id": "run_0",
                "total_count": 8,
                "success_count": 5,
                "pending_count": 2,
                "errored_count": 0,
                "retried_count": 1
            },
            {
                "_id": "run_1",
                "total_count": 6,
                "success_count": 3,
                "pending_count": 0,
                "errored_count": 2,
                "retried_count": 1
            },
            {
                "_id": "run_2",
                "total_count": 4,
                "success_count": 4,
                "pending_count": 0,
                "errored_count": 0,
                "retried_count": 0
            }
        ]

    @pytest.mark.asyncio
    async def test_get_runs_success(self, mock_namespace, mock_request_id, mock_runs, mock_aggregation_data):
        """Test successful retrieval of runs with aggregation data"""
        page = 1
        size = 10
        
        with patch('app.controller.get_runs.Run') as mock_run_class, \
             patch('app.controller.get_runs.State') as mock_state_class, \
             patch('app.controller.get_runs.logger') as mock_logger:
            
            # Mock the Run query chain for the main runs list
            mock_query_chain = MagicMock()
            mock_query_chain.to_list = AsyncMock(return_value=mock_runs)
            mock_run_class.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_query_chain
            
            # Mock the count query for total calculation
            mock_count_query = MagicMock()
            mock_count_query.count = AsyncMock(return_value=25)
            mock_run_class.find.side_effect = [
                mock_run_class.find.return_value,  # First call for runs list
                mock_count_query  # Second call for count
            ]
            
            # Mock the State aggregation pipeline with cursor approach
            mock_collection = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.to_list = AsyncMock(return_value=mock_aggregation_data)
            # Mock aggregate to return an awaitable cursor since source code awaits the entire expression
            mock_collection.aggregate = AsyncMock(return_value=mock_cursor)
            # Mock get_pymongo_collection to return a mock collection
            mock_state_class.get_pymongo_collection = MagicMock(return_value=mock_collection)
            
            result = await get_runs(mock_namespace, page, size, mock_request_id)
            
            # Verify result
            assert isinstance(result, RunsResponse)
            assert result.namespace == mock_namespace
            assert result.total == 25
            assert result.page == page
            assert result.size == size
            assert len(result.runs) == 3
            
            # Verify the runs are sorted by created_at in descending order
            assert result.runs[0].created_at == mock_runs[2].created_at  # Most recent first
            assert result.runs[2].created_at == mock_runs[0].created_at  # Oldest last
            
            # Verify aggregation pipeline was called correctly
            mock_collection.aggregate.assert_called_once()
            aggregate_call = mock_collection.aggregate.call_args[0][0]
            assert len(aggregate_call) == 2
            assert aggregate_call[0]["$match"]["run_id"]["$in"] == ["run_0", "run_1", "run_2"]
            
            # Verify logging
            mock_logger.info.assert_called_once_with(
                f"Getting runs for namespace {mock_namespace}",
                x_exosphere_request_id=mock_request_id
            )

    @pytest.mark.asyncio
    async def test_get_runs_empty_result(self, mock_namespace, mock_request_id):
        """Test get_runs when no runs are found"""
        page = 1
        size = 10
        
        with patch('app.controller.get_runs.Run') as mock_run_class, \
             patch('app.controller.get_runs.logger') as _:
            
            # Mock the Run query chain to return empty list
            mock_query_chain = MagicMock()
            mock_query_chain.to_list = AsyncMock(return_value=[])
            mock_run_class.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_query_chain

            # Mock the count query for total calculation when no runs are found
            mock_count_query = MagicMock()
            mock_count_query.count = AsyncMock(return_value=0)
            mock_run_class.find.side_effect = [
                mock_run_class.find.return_value,  # First call for runs list
                mock_count_query  # Second call for count
            ]
            
            result = await get_runs(mock_namespace, page, size, mock_request_id)
            
            assert result.runs == []
            assert result.total == 0
            assert result.namespace == mock_namespace
            assert result.page == page
            assert result.size == size

    @pytest.mark.asyncio
    async def test_get_runs_pagination(self, mock_namespace, mock_request_id, mock_runs, mock_aggregation_data):
        """Test get_runs with different pagination parameters"""
        page = 2
        size = 5
        
        with patch('app.controller.get_runs.Run') as mock_run_class, \
             patch('app.controller.get_runs.State') as mock_state_class, \
             patch('app.controller.get_runs.logger') as _:
            
            # Mock the Run query chain
            mock_query_chain = MagicMock()
            mock_query_chain.to_list = AsyncMock(return_value=mock_runs)
            mock_run_class.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_query_chain
            
            # Mock the count query
            mock_count_query = MagicMock()
            mock_count_query.count = AsyncMock(return_value=15)
            mock_run_class.find.side_effect = [
                mock_run_class.find.return_value,  # First call for runs list
                mock_count_query  # Second call for count
            ]
            
            # Mock the State aggregation pipeline with cursor approach
            mock_collection = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.to_list = AsyncMock(return_value=mock_aggregation_data)
            # Mock aggregate to return an awaitable cursor since source code awaits the entire expression
            mock_collection.aggregate = AsyncMock(return_value=mock_cursor)
            # Mock get_pymongo_collection to return a mock collection
            mock_state_class.get_pymongo_collection = MagicMock(return_value=mock_collection)
            
            result = await get_runs(mock_namespace, page, size, mock_request_id)
            
            assert result.page == page
            assert result.size == size
            assert result.total == 15
            assert len(result.runs) == 3

    @pytest.mark.asyncio
    async def test_get_runs_with_missing_states(self, mock_namespace, mock_request_id, mock_runs):
        """Test get_runs when some runs have no states in the aggregation"""
        page = 1
        size = 10
        
        # Only first two runs have aggregation data
        mock_aggregation_data = [
            {
                "_id": "run_0",
                "total_count": 5,
                "success_count": 3,
                "pending_count": 1,
                "errored_count": 0,
                "retried_count": 1
            },
            {
                "_id": "run_1",
                "total_count": 3,
                "success_count": 2,
                "pending_count": 0,
                "errored_count": 1,
                "retried_count": 0
            }
            # run_2 has no aggregation data
        ]
        
        with patch('app.controller.get_runs.Run') as mock_run_class, \
             patch('app.controller.get_runs.State') as mock_state_class, \
             patch('app.controller.get_runs.logger') as _:
            
            # Mock the Run query chain
            mock_query_chain = MagicMock()
            mock_query_chain.to_list = AsyncMock(return_value=mock_runs)
            mock_run_class.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_query_chain
            
            # Mock the count query
            mock_count_query = MagicMock()
            mock_count_query.count = AsyncMock(return_value=15)
            mock_run_class.find.side_effect = [
                mock_run_class.find.return_value,  # First call for runs list
                mock_count_query  # Second call for count
            ]
            
            # Mock the State aggregation pipeline with cursor approach
            mock_collection = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.to_list = AsyncMock(return_value=mock_aggregation_data)
            # Mock aggregate to return an awaitable cursor since source code awaits the entire expression
            mock_collection.aggregate = AsyncMock(return_value=mock_cursor)
            # Mock get_pymongo_collection to return a mock collection
            mock_state_class.get_pymongo_collection = MagicMock(return_value=mock_collection)
            
            result = await get_runs(mock_namespace, page, size, mock_request_id)
            
            assert len(result.runs) == 3
            
            # Check that runs with aggregation data have correct counts
            run_0 = next(r for r in result.runs if r.run_id == "run_0")
            assert run_0.total_count == 5
            assert run_0.success_count == 3
            assert run_0.pending_count == 1
            assert run_0.errored_count == 0
            assert run_0.retried_count == 1
            assert run_0.status == RunStatusEnum.PENDING  # Has pending states
            
            run_1 = next(r for r in result.runs if r.run_id == "run_1")
            assert run_1.total_count == 3
            assert run_1.success_count == 2
            assert run_1.pending_count == 0
            assert run_1.errored_count == 1
            assert run_1.retried_count == 0
            assert run_1.status == RunStatusEnum.FAILED  # Has errored states
            
            # Check that run_2 (no aggregation data) has zero counts and FAILED status
            run_2 = next(r for r in result.runs if r.run_id == "run_2")
            assert run_2.total_count == 0
            assert run_2.success_count == 0
            assert run_2.pending_count == 0
            assert run_2.errored_count == 0
            assert run_2.retried_count == 0
            assert run_2.status == RunStatusEnum.FAILED

    @pytest.mark.asyncio
    async def test_get_runs_status_calculation(self, mock_namespace, mock_request_id, mock_runs):
        """Test that run status is calculated correctly based on state counts"""
        page = 1
        size = 10
        
        # Test different status scenarios
        mock_aggregation_data = [
            {
                "_id": "run_0",
                "total_count": 5,
                "success_count": 5,
                "pending_count": 0,
                "errored_count": 0,
                "retried_count": 0
            },
            {
                "_id": "run_1",
                "total_count": 3,
                "success_count": 1,
                "pending_count": 2,
                "errored_count": 0,
                "retried_count": 0
            },
            {
                "_id": "run_2",
                "total_count": 4,
                "success_count": 2,
                "pending_count": 0,
                "errored_count": 2,
                "retried_count": 0
            }
        ]
        
        with patch('app.controller.get_runs.Run') as mock_run_class, \
             patch('app.controller.get_runs.State') as mock_state_class, \
             patch('app.controller.get_runs.logger') as _:
            
            # Mock the Run query chain
            mock_query_chain = MagicMock()
            mock_query_chain.to_list = AsyncMock(return_value=mock_runs)
            mock_run_class.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_query_chain
            
            # Mock the count query
            mock_count_query = MagicMock()
            mock_count_query.count = AsyncMock(return_value=15)
            mock_run_class.find.side_effect = [
                mock_run_class.find.return_value,  # First call for runs list
                mock_count_query  # Second call for count
            ]
            
            # Mock the State aggregation pipeline with cursor approach
            mock_collection = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.to_list = AsyncMock(return_value=mock_aggregation_data)
            # Mock aggregate to return an awaitable cursor since source code awaits the entire expression
            mock_collection.aggregate = AsyncMock(return_value=mock_cursor)
            # Mock get_pymongo_collection to return a mock collection
            mock_state_class.get_pymongo_collection = MagicMock(return_value=mock_collection)
            
            result = await get_runs(mock_namespace, page, size, mock_request_id)
            
            # Verify status calculations
            run_0 = next(r for r in result.runs if r.run_id == "run_0")
            assert run_0.status == RunStatusEnum.SUCCESS  # All states successful
            
            run_1 = next(r for r in result.runs if r.run_id == "run_1")
            assert run_1.status == RunStatusEnum.PENDING  # Has pending states
            
            run_2 = next(r for r in result.runs if r.run_id == "run_2")
            assert run_2.status == RunStatusEnum.FAILED  # Has errored states

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
                 patch('app.controller.get_runs.logger') as _:
                
                # Mock the Run query chain to return empty list
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
            run.created_at = datetime(2024, 1, 15, 10, 30, 0)
            large_runs_list.append(run)
        
        # Create corresponding aggregation data
        large_aggregation_data = []
        for i in range(1000):
            large_aggregation_data.append({
                "_id": f"run_{i}",
                "total_count": 5,
                "success_count": 3,
                "pending_count": 1,
                "errored_count": 0,
                "retried_count": 1
            })
        
        with patch('app.controller.get_runs.Run') as mock_run_class, \
             patch('app.controller.get_runs.State') as mock_state_class, \
             patch('app.controller.get_runs.logger') as _:
            
            # Mock the Run query chain
            mock_query_chain = MagicMock()
            mock_query_chain.to_list = AsyncMock(return_value=large_runs_list)
            mock_run_class.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_query_chain

            # Mock the count query
            mock_count_query = MagicMock()
            mock_count_query.count = AsyncMock(return_value=1000)
            mock_run_class.find.side_effect = [
                mock_run_class.find.return_value,  # First call for runs list
                mock_count_query  # Second call for count
            ]
            
            # Mock the State aggregation pipeline with cursor approach
            mock_collection = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.to_list = AsyncMock(return_value=large_aggregation_data)
            # Mock aggregate to return an awaitable cursor since source code awaits the entire expression
            mock_collection.aggregate = AsyncMock(return_value=mock_cursor)
            # Mock get_pymongo_collection to return a mock collection
            mock_state_class.get_pymongo_collection = MagicMock(return_value=mock_collection)
            
            result = await get_runs(mock_namespace, page, size, mock_request_id)
            
            assert len(result.runs) == 1000
            assert result.total == 1000

    @pytest.mark.asyncio
    async def test_get_runs_edge_case_page_zero(self, mock_namespace, mock_request_id):
        """Test get_runs with edge case page=0 (should be treated as page=1)"""
        page = 0
        size = 10
        
        with patch('app.controller.get_runs.Run') as mock_run_class, \
             patch('app.controller.get_runs.logger') as _:
            
            # Mock the Run query chain to return empty list
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
             patch('app.controller.get_runs.logger') as _:
            
            # Mock the Run query chain to return empty list
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
    async def test_get_runs_aggregation_pipeline_structure(self, mock_namespace, mock_request_id, mock_runs):
        """Test that the MongoDB aggregation pipeline is structured correctly"""
        page = 1
        size = 10
        
        with patch('app.controller.get_runs.Run') as mock_run_class, \
             patch('app.controller.get_runs.State') as mock_state_class, \
             patch('app.controller.get_runs.logger') as _:
            
            # Mock the Run query chain
            mock_query_chain = MagicMock()
            mock_query_chain.to_list = AsyncMock(return_value=mock_runs)
            mock_run_class.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_query_chain
            
            # Mock the count query
            mock_count_query = MagicMock()
            mock_count_query.count = AsyncMock(return_value=15)
            mock_run_class.find.side_effect = [
                mock_run_class.find.return_value,  # First call for runs list
                mock_count_query  # Second call for count
            ]
            
            # Mock the State aggregation pipeline with cursor approach
            mock_collection = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.to_list = AsyncMock(return_value=[])
            # Mock aggregate to return an awaitable cursor since source code awaits the entire expression
            mock_collection.aggregate = AsyncMock(return_value=mock_cursor)
            # Mock get_pymongo_collection to return a mock collection
            mock_state_class.get_pymongo_collection = MagicMock(return_value=mock_collection)
            
            await get_runs(mock_namespace, page, size, mock_request_id)
            
            # Verify aggregation pipeline structure
            mock_collection.aggregate.assert_called_once()
            pipeline = mock_collection.aggregate.call_args[0][0]
            
            # Check $match stage
            assert pipeline[0]["$match"]["run_id"]["$in"] == ["run_0", "run_1", "run_2"]
            
            # Check $group stage
            group_stage = pipeline[1]["$group"]
            assert group_stage["_id"] == "$run_id"
            assert "total_count" in group_stage
            assert "success_count" in group_stage
            assert "pending_count" in group_stage
            assert "errored_count" in group_stage
            assert "retried_count" in group_stage
            
            # Check that the aggregation conditions use the correct StateStatusEnum values
            success_condition = group_stage["success_count"]["$sum"]["$cond"]["if"]["$in"][1]
            assert StateStatusEnum.SUCCESS in success_condition
            assert StateStatusEnum.PRUNED in success_condition
            
            pending_condition = group_stage["pending_count"]["$sum"]["$cond"]["if"]["$in"][1]
            assert StateStatusEnum.CREATED in pending_condition
            assert StateStatusEnum.QUEUED in pending_condition
            assert StateStatusEnum.EXECUTED in pending_condition
            
            errored_condition = group_stage["errored_count"]["$sum"]["$cond"]["if"]["$in"][1]
            assert StateStatusEnum.ERRORED in errored_condition
            assert StateStatusEnum.NEXT_CREATED_ERROR in errored_condition
            
            retried_condition = group_stage["retried_count"]["$sum"]["$cond"]["if"]["$eq"][1]
            assert retried_condition == StateStatusEnum.RETRY_CREATED 