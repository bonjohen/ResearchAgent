"""
Pytest configuration file.
"""

import os
import sys
from pathlib import Path

import pytest

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(autouse=True)
def setup_test_environment():
    """
    Set up the test environment with required environment variables.
    """
    # Save original environment variables
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ["OPENAI_API_KEY"] = "test_api_key"
    os.environ["RESEARCH_DATA_PATH"] = str(Path(__file__).parent / "test_data")
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    # Create test data directory if it doesn't exist
    test_data_dir = Path(__file__).parent / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    
    yield
    
    # Restore original environment variables
    os.environ.clear()
    os.environ.update(original_env)
