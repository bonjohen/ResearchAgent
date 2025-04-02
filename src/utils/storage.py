"""
Storage Utility Module

This module handles external storage for the Research Agent.
"""

import os
from pathlib import Path
from typing import Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)

def setup_storage() -> Path:
    """
    Set up external storage for the Research Agent.

    Returns:
        Path: Path to the external storage directory

    Raises:
        ValueError: If the storage path is invalid or cannot be created
    """
    # Get storage path from environment
    storage_path_str = os.environ.get("RESEARCH_DATA_PATH")
    if not storage_path_str:
        error_msg = "RESEARCH_DATA_PATH environment variable is not set"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Convert to Path object
    storage_path = Path(storage_path_str)

    # Create directory if it doesn't exist
    try:
        storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"External storage path: {storage_path}")

        # Create subdirectories
        create_subdirectories(storage_path)

        return storage_path
    except Exception as e:
        error_msg = f"Failed to create external storage directory: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg)

def create_subdirectories(base_path: Path) -> None:
    """
    Create subdirectories in the external storage.

    Args:
        base_path (Path): Base path for external storage
    """
    subdirs = [
        "reports",
        "cache",
        "vector_db",
        "search_results"
    ]

    for subdir in subdirs:
        path = base_path / subdir
        path.mkdir(exist_ok=True)
        logger.debug(f"Created directory: {path}")

def get_storage_path(subdir: Optional[str] = None) -> Path:
    """
    Get the path to the external storage or a subdirectory.

    Args:
        subdir (Optional[str], optional): Subdirectory name. Defaults to None.

    Returns:
        Path: Path to the storage directory

    Raises:
        ValueError: If the storage path is not set or invalid
    """
    # Try to get the storage path from environment
    storage_path_str = os.environ.get("RESEARCH_DATA_PATH")

    # If not set, use a default path in the current directory
    if not storage_path_str:
        storage_path_str = "./temp_data"
        logger.warning(f"RESEARCH_DATA_PATH not set, using default: {storage_path_str}")

    storage_path = Path(storage_path_str)

    # Create the directory if it doesn't exist
    try:
        storage_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured storage path exists: {storage_path}")
    except Exception as e:
        error_msg = f"Failed to create storage directory: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if subdir:
        subdir_path = storage_path / subdir
        subdir_path.mkdir(exist_ok=True)
        return subdir_path

    return storage_path

def save_report(report_content: str, topic: str, format: str = "md") -> Path:
    """
    Save a research report to external storage.

    Args:
        report_content (str): Report content
        topic (str): Research topic
        format (str, optional): File format. Defaults to "md".

    Returns:
        Path: Path to the saved report
    """
    # Sanitize topic for filename
    safe_topic = "".join(c if c.isalnum() else "_" for c in topic)
    safe_topic = safe_topic[:50]  # Limit length

    # Get reports directory
    reports_dir = get_storage_path("reports")

    # Create filename
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_topic}_{timestamp}.{format}"

    # Save report
    report_path = reports_dir / filename
    report_path.write_text(report_content, encoding="utf-8")
    logger.info(f"Saved report to {report_path}")

    return report_path
