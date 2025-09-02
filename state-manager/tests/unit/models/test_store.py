import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.models.db.store import Store


class TestStore:
    """Test cases for Store model"""

    def test_store_settings_indexes(self):
        """Test Store model has correct indexes defined"""
        indexes = Store.Settings.indexes
        assert len(indexes) == 1
        
        index = indexes[0]
        assert index.document["unique"]
        assert index.document["name"] == "uniq_run_id_namespace_graph_name_key"

    @pytest.mark.asyncio
    async def test_get_value_found(self):
        """Test get_value method when store entry is found"""
        # Create mock store instance
        mock_store = MagicMock()
        mock_store.value = "test_value"
        
        # Mock the entire Store class and its find_one method
        with patch('app.models.db.store.Store') as mock_store_class:
            mock_store_class.find_one = AsyncMock(return_value=mock_store)
            
            # Call the actual static method
            result = await Store.get_value("test_run", "test_ns", "test_graph", "test_key")
            
            assert result == "test_value"

    @pytest.mark.asyncio
    async def test_get_value_not_found(self):
        """Test get_value method when store entry is not found"""
        # Mock the entire Store class and its find_one method
        with patch('app.models.db.store.Store') as mock_store_class:
            mock_store_class.find_one = AsyncMock(return_value=None)
            
            # Call the actual static method
            result = await Store.get_value("test_run", "test_ns", "test_graph", "nonexistent_key")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_value_with_different_parameters(self):
        """Test get_value method with various parameter combinations"""
        test_cases = [
            ("run1", "ns1", "graph1", "key1", "value1"),
            ("run2", "ns2", "graph2", "key2", "value2"),
            ("", "", "", "", ""),  # Edge case with empty strings
        ]
        
        for run_id, namespace, graph_name, key, expected_value in test_cases:
            mock_store = MagicMock()
            mock_store.value = expected_value
            
            with patch('app.models.db.store.Store') as mock_store_class:
                mock_store_class.find_one = AsyncMock(return_value=mock_store)
                
                result = await Store.get_value(run_id, namespace, graph_name, key)
                
                assert result == expected_value
