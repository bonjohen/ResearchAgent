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
- Web search capabilities with support for multiple search providers (Google, Serper, Tavily, DuckDuckGo)
- Web content fetching and processing for deeper research
- Comprehensive report generation in markdown format
- Follow-up question generation for continued research
- Vector database integration for RAG operations (with local models)
- External file storage for data persistence

## Requirements

- Python 3.8+
- OpenAI API key (for OpenAI models)
- Ollama (for local models)
- Internet connection (for web search)
- One of the following search API keys (optional):
  - Google Custom Search API key + Custom Search Engine ID
  - Serper API key
  - Tavily API key
  - DuckDuckGo (no API key required, used as fallback)

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

### Command-line Options

```
run.cmd [options] [topic]
```

Options:
- `--model`, `-m`: Model provider to use (default: openai)
- `--model-name`: Specific model name to use
- `--search`, `-s`: Search provider to use (google, serper, tavily, duckduckgo)
- `--verbose`, `-v`: Enable verbose logging

Examples:
```
run.cmd "artificial intelligence"
run.cmd --search duckduckgo "quantum computing"
run.cmd --search serper "machine learning"
run.cmd --search tavily "blockchain technology"
run.cmd --model openai --model-name gpt-4 "climate change"
```

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
