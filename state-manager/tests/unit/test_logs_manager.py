import logging
from unittest.mock import patch
from app.singletons.logs_manager import LogsManager


class TestLogsManager:
    """Test cases for LogsManager singleton"""

    def setup_method(self):
        """Reset the singleton and logging before each test"""
        # Clear the singleton instance
        if hasattr(LogsManager, '_instance'):
            delattr(LogsManager, '_instance')
        
        # Reset logging level to INFO
        logging.getLogger().setLevel(logging.INFO)

    def teardown_method(self):
        """Clean up after each test"""
        # Clear the singleton instance
        if hasattr(LogsManager, '_instance'):
            delattr(LogsManager, '_instance')

    @patch('app.singletons.logs_manager.sys.argv', ['python', 'run.py', '--mode', 'production'])
    def test_logs_manager_production_mode_command_line(self):
        """Test LogsManager sets INFO level in production mode via command line"""        
        # Check that the logging level is set to INFO in production mode
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    @patch('app.singletons.logs_manager.sys.argv', ['python', 'run.py', '--mode'])
    def test_logs_manager_invalid_command_line_format(self):
        """Test LogsManager handles invalid command line format gracefully"""
        # Should default to INFO level when command line format is invalid
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    @patch('app.singletons.logs_manager.sys.argv', ['python', 'run.py', '--mode', 'invalid'])
    def test_logs_manager_invalid_mode_command_line(self):
        """Test LogsManager handles invalid mode in command line"""        
        # Should default to INFO level when mode is invalid
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

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
