"""
Research Agent - Main Entry Point

This module serves as the entry point for the Research Agent application.
It initializes the environment, sets up the agents, and handles the user interaction.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.environment import load_environment
from src.utils.logger import setup_logger
from src.utils.storage import setup_storage
from src.agents.manager import ResearchManager

# Setup logger
logger = setup_logger()

async def main():
    """
    Main entry point for the Research Agent.
    """
    try:
        # Load environment variables
        logger.info("Initializing Research Agent...")
        load_environment()
        
        # Setup storage
        setup_storage()
        
        # Initialize the research manager
        manager = ResearchManager()
        
        # Get research topic from user
        print("\n===================================")
        print("Welcome to the Research Agent!")
        print("===================================\n")
        
        query = input("What would you like to research? ")
        
        # Run the research process
        await manager.run(query)
        
        print("\n===================================")
        print("Research completed successfully!")
        print("===================================\n")
        
    except KeyboardInterrupt:
        logger.info("Research Agent interrupted by user.")
        print("\nResearch Agent interrupted. Exiting...")
    except Exception as e:
        logger.error(f"Error in Research Agent: {e}", exc_info=True)
        print(f"\nAn error occurred: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
