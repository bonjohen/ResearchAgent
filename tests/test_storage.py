"""
Tests for the storage utility module.
"""

import os
from pathlib import Path

import pytest

from src.utils.storage import setup_storage, get_storage_path, save_report

class TestStorage:
    """
    Tests for the storage utility module.
    """
    
    def test_setup_storage(self):
        """Test setup_storage function."""
        # Set up storage
        storage_path = setup_storage()
        
        # Check that the storage path exists
        assert storage_path.exists()
        assert storage_path.is_dir()
        
        # Check that subdirectories were created
        for subdir in ["reports", "cache", "vector_db", "search_results"]:
            assert (storage_path / subdir).exists()
            assert (storage_path / subdir).is_dir()
    
    def test_get_storage_path(self):
        """Test get_storage_path function."""
        # Set up storage first
        setup_storage()
        
        # Get storage path
        storage_path = get_storage_path()
        
        # Check that it matches the environment variable
        assert str(storage_path) == os.environ["RESEARCH_DATA_PATH"]
    
    def test_get_storage_path_with_subdir(self):
        """Test get_storage_path function with a subdirectory."""
        # Set up storage first
        setup_storage()
        
        # Get storage path with subdirectory
        subdir_path = get_storage_path("test_subdir")
        
        # Check that it's a subdirectory of the storage path
        assert subdir_path.parent == Path(os.environ["RESEARCH_DATA_PATH"])
        assert subdir_path.name == "test_subdir"
        assert subdir_path.exists()
        assert subdir_path.is_dir()
    
    def test_save_report(self):
        """Test save_report function."""
        # Set up storage first
        setup_storage()
        
        # Create a test report
        report_content = "# Test Report\n\nThis is a test report."
        topic = "Test Topic"
        
        # Save the report
        report_path = save_report(report_content, topic)
        
        # Check that the report was saved
        assert report_path.exists()
        assert report_path.is_file()
        
        # Check the content
        assert report_path.read_text() == report_content
        
        # Check the path
        assert report_path.parent == get_storage_path("reports")
        assert report_path.name.startswith("Test_Topic_")
        assert report_path.suffix == ".md"
