import structlog
import pathlib
import os
import logging
from typing import Optional
from logging.handlers import RotatingFileHandler
from .SingletonDecorator import singleton


@singleton
class LogsManager:
    """
    This class is used to manage the logs for the application
    """

    def __init__(
        self,
        path: str = os.path.join(pathlib.Path(__file__).parent.parent.parent, "logs"),
        file_name: Optional[str] = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
    ):
        # Create the logs directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Set up rotating file handler
        file_handler = RotatingFileHandler(
            os.path.join(path, file_name if file_name else "logs.json5"),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )

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
        
        file_handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)

        self.logger = structlog.get_logger()

    def get_logger(self):
        return self.logger
