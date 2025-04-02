"""
Tests for the environment configuration module.
"""

import os
import pytest
from pathlib import Path

# Add the src directory to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.environment import load_environment, get_env

class TestEnvironment:
    """
    Tests for the environment configuration module.
    """
    
    def test_get_env_with_value(self):
        """Test get_env with a set environment variable."""
        # Set a test environment variable
        os.environ["TEST_VAR"] = "test_value"
        
        # Get the value
        value = get_env("TEST_VAR")
        
        # Check the value
        assert value == "test_value"
    
    def test_get_env_with_default(self):
        """Test get_env with a default value."""
        # Ensure the environment variable is not set
        if "TEST_VAR_2" in os.environ:
            del os.environ["TEST_VAR_2"]
        
        # Get the value with a default
        value = get_env("TEST_VAR_2", "default_value")
        
        # Check the value
        assert value == "default_value"
    
    def test_get_env_missing(self):
        """Test get_env with a missing environment variable."""
        # Ensure the environment variable is not set
        if "TEST_VAR_3" in os.environ:
            del os.environ["TEST_VAR_3"]
        
        # Check that it raises a ValueError
        with pytest.raises(ValueError):
            get_env("TEST_VAR_3")
    
    def test_load_environment_with_defaults(self, monkeypatch):
        """Test load_environment with default values."""
        # Set required environment variables
        monkeypatch.setenv("OPENAI_API_KEY", "test_api_key")
        monkeypatch.setenv("RESEARCH_DATA_PATH", "/tmp/research_data")
        
        # Remove optional environment variables
        for var in ["OLLAMA_BASE_URL", "OLLAMA_MODEL", "SEARCH_ENGINE", "VECTOR_DB_TYPE", "LOG_LEVEL"]:
            monkeypatch.delenv(var, raising=False)
        
        # Load environment
        env_vars = load_environment()
        
        # Check required variables
        assert env_vars["OPENAI_API_KEY"] == "test_api_key"
        assert env_vars["RESEARCH_DATA_PATH"] == "/tmp/research_data"
        
        # Check default values
        assert env_vars["OLLAMA_BASE_URL"] == "http://localhost:11434"
        assert env_vars["OLLAMA_MODEL"] == "llama3:7b"
        assert env_vars["SEARCH_ENGINE"] == "google"
        assert env_vars["VECTOR_DB_TYPE"] == "chroma"
        assert env_vars["LOG_LEVEL"] == "INFO"
        
        # Check derived values
        assert env_vars["VECTOR_DB_PATH"] == str(Path("/tmp/research_data") / "vector_db")
