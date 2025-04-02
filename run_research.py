"""
Run Research Script

This script runs the Research Agent on a given topic.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.manager import ResearchManager
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()

async def main():
    """
    Main entry point for the Research Agent.
    """
    try:
        # Initialize the research manager
        manager = ResearchManager()
        
        # Get research topic from user or command line
        if len(sys.argv) > 1:
            topic = " ".join(sys.argv[1:])
        else:
            print("\n===================================")
            print("Welcome to the Research Agent!")
            print("===================================\n")
            topic = input("What would you like to research? ")
        
        # Run the research process
        report = await manager.run(topic)
        
        print("\n===================================")
        print("Research completed successfully!")
        print("===================================\n")
        
        # Print the follow-up questions
        if report.follow_up_questions:
            print("Follow-up Questions:")
            for i, question in enumerate(report.follow_up_questions, 1):
                print(f"{i}. {question}")
            print()
        
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
