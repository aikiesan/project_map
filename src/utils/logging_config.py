"""
CP2B Maps V2 - Logging Configuration
Professional logging setup for development and production
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from config.settings import settings


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up professional logging configuration

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file to write logs to

    Returns:
        Configured logger instance
    """
    # Use settings level if not specified
    log_level = level or settings.LOG_LEVEL

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=settings.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            *([] if log_file is None else [logging.FileHandler(log_file)])
        ]
    )

    # Create main logger
    logger = logging.getLogger("cp2b_maps_v2")

    # Log startup information
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting")
    logger.info(f"Log level: {log_level.upper()}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with consistent configuration

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f"cp2b_maps_v2.{name}")


# Default logger for the application
logger = setup_logging()