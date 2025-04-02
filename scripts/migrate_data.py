"""
Migrate Data Script

This script migrates data from the old temp_data directory to the new external storage location.
"""

import os
import shutil
from pathlib import Path

def main():
    """
    Main function to migrate data.
    """
    print("Migrating data from temp_data to external storage...")
    
    # Get the source directory (temp_data)
    source_dir = Path("temp_data")
    if not source_dir.exists():
        print(f"Source directory {source_dir} does not exist. Nothing to migrate.")
        return
    
    # Get the destination directory
    # Use the user's documents folder
    user_home = Path.home()
    documents_path = user_home / "Documents"
    
    # Create a dedicated folder for research data
    dest_dir = documents_path / "ResearchAgentData"
    
    # Check if the destination directory exists
    if not dest_dir.exists():
        print(f"Creating destination directory: {dest_dir}")
        dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Migrate the data
    print(f"Migrating data from {source_dir} to {dest_dir}...")
    
    # Migrate reports
    migrate_subdirectory(source_dir, dest_dir, "reports")
    
    # Migrate search results
    migrate_subdirectory(source_dir, dest_dir, "search_results")
    
    print("Migration complete!")

def migrate_subdirectory(source_dir, dest_dir, subdir):
    """
    Migrate a subdirectory from source to destination.
    
    Args:
        source_dir (Path): Source directory
        dest_dir (Path): Destination directory
        subdir (str): Subdirectory name
    """
    source_subdir = source_dir / subdir
    dest_subdir = dest_dir / subdir
    
    if not source_subdir.exists():
        print(f"Source subdirectory {source_subdir} does not exist. Skipping.")
        return
    
    # Create the destination subdirectory if it doesn't exist
    if not dest_subdir.exists():
        print(f"Creating destination subdirectory: {dest_subdir}")
        dest_subdir.mkdir(parents=True, exist_ok=True)
    
    # Copy all files from source to destination
    file_count = 0
    for file_path in source_subdir.glob("*"):
        if file_path.is_file():
            dest_file = dest_subdir / file_path.name
            if not dest_file.exists():
                shutil.copy2(file_path, dest_file)
                file_count += 1
    
    print(f"Migrated {file_count} files from {source_subdir} to {dest_subdir}")

if __name__ == "__main__":
    main()
