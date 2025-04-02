"""
Check Environment Variables

This script checks if we can access environment variables, particularly the OpenAI API key.
"""

import os
import sys
from pathlib import Path
# Try to import from python-dotenv
try:
    from dotenv import load_dotenv
except ImportError:
    # Define a simple load_dotenv function if the package is not available
    def load_dotenv(dotenv_path=None):
        """Simple implementation to load .env file"""
        if dotenv_path and Path(dotenv_path).exists():
            with open(dotenv_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    key, value = line.split('=', 1)
                    os.environ[key] = value
            return True
        return False

def main():
    """
    Main function to check environment variables.
    """
    print("Checking environment variables...")

    # Try to load from .env file
    env_path = Path(".env")
    if env_path.exists():
        print(f"Loading environment from {env_path}")
        load_dotenv(dotenv_path=env_path)
    else:
        print(f".env file not found at {env_path}")

    # Check for OpenAI API key
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key:
        # Mask the key for security
        masked_key = openai_api_key[:4] + "..." + openai_api_key[-4:] if len(openai_api_key) > 8 else "***"
        print(f"OPENAI_API_KEY found: {masked_key}")
    else:
        print("OPENAI_API_KEY not found in environment variables")

    # Check for other environment variables
    print("\nAll environment variables:")
    env_count = 0
    for key, value in os.environ.items():
        env_count += 1
        # Skip displaying sensitive information
        if "KEY" in key or "SECRET" in key or "PASSWORD" in key or "TOKEN" in key:
            masked_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            print(f"{key}: {masked_value}")
        else:
            print(f"{key}: {value}")

    print(f"\nTotal environment variables: {env_count}")

if __name__ == "__main__":
    main()
