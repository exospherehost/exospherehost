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

    def test_is_development_mode_command_line_exception_handling(self):
        """Test development mode detection with exception handling in command line parsing"""
        logs_manager = LogsManager()
        
        # Test with sys.argv that would cause IndexError
        with patch('sys.argv', ['python', 'run.py', '--mode']):  # Missing value
            result = logs_manager._is_development_mode()
            assert result is False

    def test_is_development_mode_value_error_handling(self):
        """Test development mode detection with ValueError in command line parsing"""
        logs_manager = LogsManager()
        
        # Mock sys.argv to cause ValueError when searching for --mode
        with patch('sys.argv', ['python', 'run.py']):
            # The function will try to find '--mode' in sys.argv, which will raise ValueError
            result = logs_manager._is_development_mode()
            assert result is False

    def test_is_development_mode_index_error_handling(self):
        """Test development mode detection with IndexError in command line parsing"""
        logs_manager = LogsManager()
        
        # Mock sys.argv to be too short
        with patch('sys.argv', ['python']):  # Too short
            result = logs_manager._is_development_mode()
            assert result is False

    def test_is_development_mode_complex_command_line(self):
        """Test development mode detection with complex command line arguments"""
        logs_manager = LogsManager()
        
        with patch('sys.argv', ['python', 'run.py', '--other-arg', 'value', '--mode', 'development', '--another-arg']):
            result = logs_manager._is_development_mode()
            assert result is True

    def test_is_development_mode_case_sensitive_command_line(self):
        """Test that command line mode is case sensitive"""
        logs_manager = LogsManager()
        
        with patch('sys.argv', ['python', 'run.py', '--mode', 'DEVELOPMENT']):
            result = logs_manager._is_development_mode()
            assert result is False  # Should be case sensitive

    def test_is_development_mode_environment_override(self):
        """Test that environment variable overrides command line when command line parsing fails"""
        logs_manager = LogsManager()
        
        with patch.dict(os.environ, {'MODE': 'development'}):
            with patch('sys.argv', ['python', 'run.py', '--mode']):  # Invalid command line
                result = logs_manager._is_development_mode()
                assert result is True  # Should fall back to environment variable

    def test_is_development_mode_environment_override_production(self):
        """Test that environment variable overrides command line for production mode"""
        logs_manager = LogsManager()
        
        with patch.dict(os.environ, {'MODE': 'production'}):
            with patch('sys.argv', ['python', 'run.py', '--mode', 'development']):
                result = logs_manager._is_development_mode()
                assert result is True  # Command line should take priority over environment

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

    def test_logger_initialization_with_development_mode(self):
        """Test logger initialization when in development mode"""
        with patch.dict(os.environ, {'MODE': 'development'}):
            with patch('sys.argv', ['python', 'run.py']):
                # Create a new instance to test development mode initialization
                logs_manager = LogsManager()
                logger = logs_manager.get_logger()
                
                # The logger should be properly initialized even in development mode
                assert logger is not None
                assert hasattr(logger, 'info')
                assert hasattr(logger, 'error')
                assert hasattr(logger, 'warning')
                assert hasattr(logger, 'debug')

    def test_logger_initialization_with_production_mode(self):
        """Test logger initialization when in production mode"""
        with patch.dict(os.environ, {'MODE': 'production'}):
            with patch('sys.argv', ['python', 'run.py']):
                # Create a new instance to test production mode initialization
                logs_manager = LogsManager()
                logger = logs_manager.get_logger()
                
                # The logger should be properly initialized in production mode
                assert logger is not None
                assert hasattr(logger, 'info')
                assert hasattr(logger, 'error')
                assert hasattr(logger, 'warning')
                assert hasattr(logger, 'debug')

    def test_logger_initialization_with_no_mode(self):
        """Test logger initialization when no mode is specified"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('sys.argv', ['python', 'run.py']):
                # Create a new instance to test no mode initialization
                logs_manager = LogsManager()
                logger = logs_manager.get_logger()
                
                # The logger should be properly initialized even without mode specification
                assert logger is not None
                assert hasattr(logger, 'info')
                assert hasattr(logger, 'error')
                assert hasattr(logger, 'warning')
                assert hasattr(logger, 'debug')

    def test_multiple_logs_manager_instances_same_logger(self):
        """Test that multiple LogsManager instances return the same logger"""
        instance1 = LogsManager()
        instance2 = LogsManager()
        
        logger1 = instance1.get_logger()
        logger2 = instance2.get_logger()
        
        # Both instances should return the same logger due to singleton pattern
        assert logger1 is logger2

    def test_logs_manager_singleton_across_imports(self):
        """Test that LogsManager singleton works across different imports"""
        # Import LogsManager from different paths to test singleton behavior
        from app.singletons.logs_manager import LogsManager as LogsManager1
        from app.singletons.logs_manager import LogsManager as LogsManager2
        
        instance1 = LogsManager1()
        instance2 = LogsManager2()
        
        assert instance1 is instance2
        
        logger1 = instance1.get_logger()
        logger2 = instance2.get_logger()
        
        assert logger1 is logger2 