"""
Logger Utility Module

This module provides logging functionality for the Research Agent.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setup_logger(
    name: Optional[str] = None,
    level: Optional[str] = None,
    log_format: str = DEFAULT_LOG_FORMAT
) -> logging.Logger:
    """
    Set up and configure a logger.
    
    Args:
        name (Optional[str], optional): Logger name. Defaults to None (root logger).
        level (Optional[str], optional): Log level. Defaults to None (from environment or INFO).
        log_format (str, optional): Log format. Defaults to DEFAULT_LOG_FORMAT.
    
    Returns:
        logging.Logger: Configured logger
    """
    # Get log level from environment or use default
    if level is None:
        level = os.environ.get("LOG_LEVEL", "INFO").upper()
    
    # Convert string level to logging level
    numeric_level = getattr(logging, level, logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(get_log_file_path())
        ]
    )
    
    # Get logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name (str): Logger name
    
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)

def get_log_file_path() -> str:
    """
    Get the path to the log file.
    
    Returns:
        str: Path to the log file
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).parent.parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Return path to log file
    return str(logs_dir / "research_agent.log")
