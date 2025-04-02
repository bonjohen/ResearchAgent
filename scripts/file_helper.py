"""
File Helper

This module provides utilities for safely viewing and editing files.
"""

import os
from pathlib import Path


def get_file_content(file_path):
    """
    Get the complete content of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        The file content as a string
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def find_exact_line_numbers(file_path, search_text):
    """
    Find the exact line numbers for a given text in a file.
    
    Args:
        file_path: Path to the file
        search_text: Text to search for
        
    Returns:
        Tuple of (start_line, end_line) or None if not found
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Join the search text lines to normalize line endings
    search_lines = search_text.splitlines()
    
    for i in range(len(lines) - len(search_lines) + 1):
        # Check if the current line and subsequent lines match the search text
        match = True
        for j in range(len(search_lines)):
            # Strip to handle whitespace differences
            if search_lines[j].strip() != lines[i + j].strip():
                match = False
                break
        
        if match:
            return (i + 1, i + len(search_lines))
    
    return None


def safe_replace(file_path, old_text, new_text):
    """
    Safely replace text in a file by finding its exact location first.
    
    Args:
        file_path: Path to the file
        old_text: Text to replace
        new_text: New text
        
    Returns:
        Tuple of (success, message)
    """
    # Find the exact line numbers
    line_numbers = find_exact_line_numbers(file_path, old_text)
    
    if line_numbers is None:
        return (False, f"Could not find the exact text to replace in {file_path}")
    
    start_line, end_line = line_numbers
    
    # Create the replacement entry
    replacement = {
        "old_str": old_text,
        "new_str": new_text,
        "old_str_start_line_number": start_line,
        "old_str_end_line_number": end_line
    }
    
    return (True, replacement)
