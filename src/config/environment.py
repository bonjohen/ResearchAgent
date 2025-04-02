"""
Environment Configuration Module

This module handles loading and validating environment variables for the Research Agent.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Required environment variables
REQUIRED_VARS = [
    "OPENAI_API_KEY",
    "RESEARCH_DATA_PATH"
]

# Optional environment variables with default values
DEFAULT_VARS = {
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "OLLAMA_MODEL": "llama3:7b",
    "SEARCH_ENGINE": "google",
    "VECTOR_DB_TYPE": "chroma",
    "LOG_LEVEL": "INFO"
}

def load_environment() -> Dict[str, str]:
    """
    Load environment variables from .env file and validate them.
    
    Returns:
        Dict[str, str]: Dictionary of environment variables
    
    Raises:
        ValueError: If required environment variables are missing
    """
    # Load .env file if it exists
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        logger.info(f"Loading environment from {env_path}")
        load_dotenv(dotenv_path=env_path)
    else:
        logger.warning(f".env file not found at {env_path}")
    
    # Check for required environment variables
    missing_vars = [var for var in REQUIRED_VARS if not os.environ.get(var)]
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Set default values for optional variables if not set
    for var, default_value in DEFAULT_VARS.items():
        if not os.environ.get(var):
            logger.info(f"Setting default value for {var}: {default_value}")
            os.environ[var] = default_value
    
    # Set VECTOR_DB_PATH if not set
    if not os.environ.get("VECTOR_DB_PATH"):
        research_data_path = os.environ.get("RESEARCH_DATA_PATH")
        vector_db_path = str(Path(research_data_path) / "vector_db")
        logger.info(f"Setting VECTOR_DB_PATH to {vector_db_path}")
        os.environ["VECTOR_DB_PATH"] = vector_db_path
    
    # Return all environment variables as a dictionary
    return {key: os.environ.get(key) for key in set(REQUIRED_VARS + list(DEFAULT_VARS.keys()) + ["VECTOR_DB_PATH"])}

def get_env(key: str, default: Optional[str] = None) -> str:
    """
    Get an environment variable with an optional default value.
    
    Args:
        key (str): The environment variable key
        default (Optional[str], optional): Default value if not set. Defaults to None.
    
    Returns:
        str: The environment variable value or default
    
    Raises:
        ValueError: If the environment variable is not set and no default is provided
    """
    value = os.environ.get(key, default)
    if value is None:
        error_msg = f"Environment variable {key} is not set and no default provided"
        logger.error(error_msg)
        raise ValueError(error_msg)
    return value
