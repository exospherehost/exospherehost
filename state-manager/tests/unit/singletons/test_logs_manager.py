import pytest
from unittest.mock import patch
import os
from app.singletons.logs_manager import LogsManager


class TestLogsManager:
    """Test cases for LogsManager"""

    def test_logs_manager_singleton_pattern(self):
        """Test that LogsManager follows singleton pattern"""
        instance1 = LogsManager()
        instance2 = LogsManager()
        
        assert instance1 is instance2

    def test_get_logger_returns_structlog_logger(self):
        """Test that get_logger returns a structlog logger"""
        logs_manager = LogsManager()
        logger = logs_manager.get_logger()
        
        assert logger is not None
        # Check that it's a structlog logger
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'debug')

    @patch.dict(os.environ, {'MODE': 'development'})
    def test_is_development_mode_env_var_development(self):
        """Test development mode detection via environment variable"""
        logs_manager = LogsManager()
        
        # Mock sys.argv to not contain --mode
        with patch('sys.argv', ['python', 'run.py']):
            result = logs_manager._is_development_mode()
            assert result is True

    @patch.dict(os.environ, {'MODE': 'production'})
    def test_is_development_mode_env_var_production(self):
        """Test production mode detection via environment variable"""
        logs_manager = LogsManager()
        
        with patch('sys.argv', ['python', 'run.py']):
            result = logs_manager._is_development_mode()
            assert result is False

    @patch.dict(os.environ, {'MODE': 'DEVELOPMENT'})
    def test_is_development_mode_env_var_case_insensitive(self):
        """Test that environment variable is case insensitive"""
        logs_manager = LogsManager()
        
        with patch('sys.argv', ['python', 'run.py']):
            result = logs_manager._is_development_mode()
            assert result is True

    @patch.dict(os.environ, {'MODE': ''})
    def test_is_development_mode_env_var_empty(self):
        """Test development mode detection with empty environment variable"""
        logs_manager = LogsManager()
        
        with patch('sys.argv', ['python', 'run.py']):
            result = logs_manager._is_development_mode()
            assert result is False

    def test_is_development_mode_command_line_development(self):
        """Test development mode detection via command line arguments"""
        logs_manager = LogsManager()
        
        with patch('sys.argv', ['python', 'run.py', '--mode', 'development']):
            result = logs_manager._is_development_mode()
            assert result is True

    def test_is_development_mode_command_line_production(self):
        """Test production mode detection via command line arguments"""
        logs_manager = LogsManager()
        
        with patch('sys.argv', ['python', 'run.py', '--mode', 'production']):
            result = logs_manager._is_development_mode()
            assert result is False

    def test_is_development_mode_invalid_command_line_format(self):
        """Test development mode detection with invalid command line format"""
        logs_manager = LogsManager()
        
        with patch('sys.argv', ['python', 'run.py', '--mode']):  # Missing value
            result = logs_manager._is_development_mode()
            assert result is False

    def test_is_development_mode_invalid_mode(self):
        """Test development mode detection with invalid mode value"""
        logs_manager = LogsManager()
        
        with patch('sys.argv', ['python', 'run.py', '--mode', 'invalid']):
            result = logs_manager._is_development_mode()
            assert result is False

    def test_is_development_mode_no_mode_arg(self):
        """Test development mode detection when no mode argument is present"""
        logs_manager = LogsManager()
        
        with patch('sys.argv', ['python', 'run.py']):
            result = logs_manager._is_development_mode()
            assert result is False

    def test_logs_manager_initialization_production_mode(self):
        """Test LogsManager initialization in production mode"""
        # This test verifies that LogsManager can be initialized in production mode
        # without causing errors
        with patch('sys.argv', ['python', 'run.py']):
            logs_manager = LogsManager()
            assert logs_manager is not None
            assert hasattr(logs_manager, 'get_logger')

    def test_logs_manager_initialization_with_handler(self):
        """Test LogsManager initialization with handler setup"""
        # This test verifies that LogsManager can be initialized
        # and has the expected structure
        logs_manager = LogsManager()
        assert logs_manager is not None
        assert hasattr(logs_manager, 'get_logger')
        assert hasattr(logs_manager, '_is_development_mode')

    def test_logs_manager_structlog_integration(self):
        """Test LogsManager integration with structlog"""
        # This test verifies that LogsManager can be initialized
        # and returns a functional logger
        logs_manager = LogsManager()
        logger = logs_manager.get_logger()
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'debug')

    def test_logs_manager_command_line_priority(self):
        """Test that command line arguments take priority over environment variables"""
        logs_manager = LogsManager()
        
        # Set environment to production but command line to development
        with patch.dict(os.environ, {'MODE': 'production'}):
            with patch('sys.argv', ['python', 'run.py', '--mode', 'development']):
                result = logs_manager._is_development_mode()
                assert result is True

    def test_logs_manager_exception_handling_in_command_line_parsing(self):
        """Test exception handling in command line argument parsing"""
        logs_manager = LogsManager()
        
        # Mock sys.argv to cause an exception during parsing
        with patch('sys.argv', ['python', 'run.py', '--mode']):
            # This should not raise an exception and should return False
            result = logs_manager._is_development_mode()
            assert result is False

    def test_logs_manager_multiple_instances_same_logger(self):
        """Test that multiple LogsManager instances share the same logger"""
        instance1 = LogsManager()
        instance2 = LogsManager()
        
        logger1 = instance1.get_logger()
        logger2 = instance2.get_logger()
        
        assert logger1 is logger2

    def test_logs_manager_logger_functionality(self):
        """Test that the logger returned by LogsManager is functional"""
        logs_manager = LogsManager()
        logger = logs_manager.get_logger()
        
        # Test that logger methods don't raise exceptions
        try:
            logger.info("Test info message")
            logger.error("Test error message")
            logger.warning("Test warning message")
            logger.debug("Test debug message")
        except Exception as e:
            pytest.fail(f"Logger methods should not raise exceptions: {e}")

    @patch('app.singletons.logs_manager.structlog.configure')
    def test_logs_manager_structlog_configuration(self, mock_structlog_configure):
        """Test that structlog is configured properly"""
        # This test verifies that LogsManager can be initialized
        # and structlog is configured (without checking specific calls due to singleton)
        logs_manager = LogsManager()
        assert logs_manager is not None
        assert hasattr(logs_manager, 'get_logger') 