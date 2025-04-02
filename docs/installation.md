# Installation Guide

This guide explains how to install and set up the Research Agent.

## Prerequisites

- Python 3.8 or higher
- Windows operating system
- Internet connection
- OpenAI API key (for OpenAI models)
- Ollama (for local models)

## Installation Steps

1. **Clone the Repository**

   ```
   git clone https://github.com/yourusername/research-agent.git
   cd research-agent
   ```

2. **Run the Setup Script**

   ```
   scripts\setup.cmd
   ```

   This script will:
   - Create a virtual environment
   - Install dependencies
   - Create a `.env` file from the template

3. **Configure Environment Variables**

   Edit the `.env` file and set the required environment variables:

   ```
   # OpenAI API Configuration
   OPENAI_API_KEY=your_openai_api_key_here

   # External Storage Path (outside project folder)
   RESEARCH_DATA_PATH=C:/path/to/external/storage
   ```

4. **Install Ollama (Optional, for Local Models)**

   To use local models, you need to install Ollama:

   ```
   scripts\install_ollama.cmd
   ```

   This script will:
   - Download and install Ollama
   - Pull the Llama3 7B model
   - Start the Ollama server

## Verification

To verify that the installation was successful, run:

```
scripts\test.cmd
```

This will run the test suite to ensure everything is working correctly.

## Next Steps

Once the installation is complete, you can:

- [Use the Research Agent](usage.md)
- [Explore the API](api.md)
- [Contribute to development](development.md)
