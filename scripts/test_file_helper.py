"""
Test File Helper

This script tests the file helper utilities.
"""

import os
import sys
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from file_helper import get_file_content, find_exact_line_numbers, safe_replace


def test_file_helper():
    """Test the file helper functions."""
    # Create a test file
    test_file = "test_file.txt"
    with open(test_file, "w") as f:
        f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
    
    # Test get_file_content
    content = get_file_content(test_file)
    print(f"File content: {content}")
    
    # Test find_exact_line_numbers
    search_text = "Line 2\nLine 3"
    line_numbers = find_exact_line_numbers(test_file, search_text)
    print(f"Line numbers for '{search_text}': {line_numbers}")
    
    # Test safe_replace
    success, result = safe_replace(test_file, search_text, "New Line 2\nNew Line 3")
    print(f"Safe replace result: {success}, {result}")
    
    # Clean up
    os.remove(test_file)


if __name__ == "__main__":
    test_file_helper()
