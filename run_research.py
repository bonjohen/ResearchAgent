"""
Run Research Script

This script runs the Research Agent on a given topic.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.manager import ResearchManager
from src.models.factory import create_model_provider
from src.utils.logger import setup_logger

# Setup logger
logger = setup_logger()

def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: The parsed arguments
    """
    parser = argparse.ArgumentParser(description="Research Agent")
    parser.add_argument(
        "topic", nargs="*", help="The research topic (if not provided, will prompt)"
    )
    parser.add_argument(
        "--model", "-m", default="openai", help="Model provider to use (default: openai)"
    )
    parser.add_argument(
        "--model-name", default=None, help="Specific model name to use"
    )
    parser.add_argument(
        "--search", "-s", default=None, help="Search provider to use (google, duckduckgo)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    return parser.parse_args()

async def main():
    """
    Main entry point for the Research Agent.
    """
    try:
        # Parse command line arguments
        args = parse_arguments()

        # Set log level based on verbose flag
        if args.verbose:
            os.environ["LOG_LEVEL"] = "DEBUG"

        # Set search provider if specified
        if args.search:
            os.environ["SEARCH_ENGINE"] = args.search
            print(f"Using search provider: {args.search}")

        # Initialize the model provider
        model_provider = create_model_provider(
            provider_type=args.model,
            model_name=args.model_name
        )

        # Initialize the research manager
        manager = ResearchManager(model_provider=model_provider)

        # Get research topic from arguments or prompt
        if args.topic:
            topic = " ".join(args.topic)
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
