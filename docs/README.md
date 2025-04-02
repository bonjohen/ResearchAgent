# Research Agent Documentation

This directory contains documentation for the Research Agent.

## Contents

- [Installation Guide](installation.md) (Coming soon)
- [Usage Guide](usage.md) (Coming soon)
- [API Reference](api.md) (Coming soon)
- [Development Guide](development.md) (Coming soon)

## Overview

The Research Agent is a tool for conducting comprehensive research on any topic. It uses a multi-agent architecture to:

1. Plan the research approach
2. Execute web searches to gather information
3. Synthesize the information into a comprehensive report

The agent supports both OpenAI models and local models via Ollama, allowing for flexibility in deployment.

## Architecture

The Research Agent consists of three main components:

1. **Planning Agent**: Breaks down the research topic into specific search queries
2. **Search Agent**: Executes web searches and summarizes the results
3. **Writer Agent**: Synthesizes the search results into a comprehensive report

## Configuration

The Research Agent is configured using environment variables. See the `.env.example` file in the root directory for available options.
