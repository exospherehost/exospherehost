import logging
from unittest.mock import patch
from app.singletons.logs_manager import LogsManager


class TestLogsManagerSimple:
    """Simplified test cases for LogsManager singleton"""

    def setup_method(self):
        """Reset logging before each test"""
        # Reset logging level to INFO
        logging.getLogger().setLevel(logging.INFO)

    def test_logs_manager_singleton_pattern(self):
        """Test LogsManager follows singleton pattern"""
        logs_manager1 = LogsManager()
        logs_manager2 = LogsManager()
        
        # Both instances should be the same object
        assert logs_manager1 is logs_manager2

    def test_get_logger_returns_structlog_logger(self):
        """Test get_logger returns a structlog logger"""
        logs_manager = LogsManager()
        logger = logs_manager.get_logger()
        
        # Should return a structlog logger
        assert logger is not None
        # Check that it's a structlog logger by checking for structlog-specific attributes
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')

    def test_is_development_mode_command_line_development(self):
        """Test _is_development_mode with development command line argument"""
        with patch('sys.argv', ['python', 'run.py', '--mode', 'development']):
            logs_manager = LogsManager()
            # Access the private method through the instance
            result = logs_manager._is_development_mode()
            assert result is True

    def test_is_development_mode_command_line_production(self):
        """Test _is_development_mode with production command line argument"""
        with patch('sys.argv', ['python', 'run.py', '--mode', 'production']):
            logs_manager = LogsManager()
            result = logs_manager._is_development_mode()
            assert result is False

    def test_is_development_mode_env_var_development(self):
        """Test _is_development_mode with development environment variable"""
        with patch('sys.argv', ['python', 'run.py']):
            with patch('os.getenv', return_value='development'):
                logs_manager = LogsManager()
                result = logs_manager._is_development_mode()
                assert result is True

    def test_is_development_mode_env_var_production(self):
        """Test _is_development_mode with production environment variable"""
        with patch('sys.argv', ['python', 'run.py']):
            with patch('os.getenv', return_value='production'):
                logs_manager = LogsManager()
                result = logs_manager._is_development_mode()
                assert result is False

    def test_is_development_mode_env_var_case_insensitive(self):
        """Test _is_development_mode with case insensitive environment variable"""
        with patch('sys.argv', ['python', 'run.py']):
            with patch('os.getenv', return_value='DEVELOPMENT'):
                logs_manager = LogsManager()
                result = logs_manager._is_development_mode()
                assert result is True

    def test_is_development_mode_env_var_empty(self):
        """Test _is_development_mode with empty environment variable"""
        with patch('sys.argv', ['python', 'run.py']):
            with patch('os.getenv', return_value=''):
                logs_manager = LogsManager()
                result = logs_manager._is_development_mode()
                assert result is False

    def test_is_development_mode_invalid_command_line_format(self):
        """Test _is_development_mode with invalid command line format"""
        with patch('sys.argv', ['python', 'run.py', '--mode']):
            logs_manager = LogsManager()
            result = logs_manager._is_development_mode()
            assert result is False

    def test_is_development_mode_invalid_mode(self):
        """Test _is_development_mode with invalid mode"""
        with patch('sys.argv', ['python', 'run.py', '--mode', 'invalid']):
            logs_manager = LogsManager()
            result = logs_manager._is_development_mode()
            assert result is False

    def test_is_development_mode_no_mode_arg(self):
        """Test _is_development_mode with no mode argument"""
        with patch('sys.argv', ['python', 'run.py']):
            with patch('os.getenv', return_value=''):
                logs_manager = LogsManager()
                result = logs_manager._is_development_mode()
                assert result is False 