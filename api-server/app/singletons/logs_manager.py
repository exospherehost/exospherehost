import structlog
import pathlib
import os
import logging
from typing import Optional
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
        logger.setLevel(logging.INFO)

        self.logger = structlog.get_logger()

    def get_logger(self):
        return self.logger
