# Research Agent

A research agent built using the OpenAI Agent SDK with support for both OpenAI models and local models via Ollama.

## Overview

This research agent helps users conduct comprehensive research on any topic by:
1. Planning and executing web searches to gather relevant information
2. Synthesizing the information into a comprehensive report
3. Providing follow-up questions for further research

The agent supports both OpenAI models and local models (like Llama3 7B) via Ollama, allowing for flexibility in deployment.

## Features

- Multi-agent architecture with planning, search, and writer agents
- Support for both OpenAI models and local models via Ollama
- Web search capabilities for information gathering
- Comprehensive report generation in markdown format
- Follow-up question generation for continued research
- Vector database integration for RAG operations (with local models)
- External file storage for data persistence

## Requirements

- Python 3.8+
- OpenAI API key (for OpenAI models)
- Ollama (for local models)
- Internet connection (for web search)

## Installation

1. Clone the repository
2. Run the setup script:
   ```
   setup.cmd
   ```
3. Configure your environment variables in the `.env` file

## Usage

Run the research agent:
```
run.cmd
```

Enter your research topic when prompted, and the agent will:
1. Plan the research approach
2. Execute web searches
3. Generate a comprehensive report

## Project Structure

- `src/` - Source code
  - `agents/` - Agent implementations
  - `models/` - Model providers (OpenAI, Ollama)
  - `tools/` - Tool implementations
  - `utils/` - Utility functions
  - `config/` - Configuration handling
- `tests/` - Test suite
- `scripts/` - CMD scripts for setup and execution
- `docs/` - Documentation
- `data/` - Default data directory (configurable)

## License

[MIT License](LICENSE)
