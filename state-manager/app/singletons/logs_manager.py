import structlog
import logging
import os
import sys
from .SingletonDecorator import singleton


@singleton
class LogsManager:
    """
    This class is used to manage the logs for the application
    """

    def __init__(self):
        handler = logging.StreamHandler()

        structlog.configure(
            processors=[
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
        )

        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
        )
        
        handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(handler)
        
        # Check if running in development mode
        # Development mode is determined by the --mode argument passed to run.py
        is_development = self._is_development_mode()
        
        if is_development:
            # In development mode, set level to WARNING to disable INFO logs
            logger.setLevel(logging.INFO)
        else:
            # In production mode, keep INFO level
            logger.setLevel(logging.INFO)

        self.logger = structlog.get_logger()

    def _is_development_mode(self) -> bool:
        """
        Check if the application is running in development mode.
        Development mode is determined by checking if '--mode' 'development' 
        is in the command line arguments.
        """
        # Check command line arguments for development mode
        if '--mode' in sys.argv:
            try:
                mode_index = sys.argv.index('--mode')
                if mode_index + 1 < len(sys.argv) and sys.argv[mode_index + 1] == 'development':
                    return True
            except (ValueError, IndexError):
                pass
        
        # Fallback: check environment variable
        return os.getenv('MODE', '').lower() == 'development'

    def get_logger(self):
        return self.logger
