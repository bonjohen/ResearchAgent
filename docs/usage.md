# Usage Guide

This guide explains how to use the Research Agent.

## Basic Usage

1. **Start the Research Agent**

   ```
   scripts\run.cmd
   ```

2. **Enter a Research Topic**

   When prompted, enter the topic you want to research:

   ```
   What would you like to research? The impact of artificial intelligence on healthcare
   ```

3. **Wait for Results**

   The Research Agent will:
   - Plan the research approach
   - Execute web searches
   - Synthesize the information into a report

4. **View the Report**

   The report will be saved to the external storage location specified in your `.env` file:

   ```
   RESEARCH_DATA_PATH/reports/The_impact_of_artificial_intelligence_on_healthcare_YYYYMMDD_HHMMSS.md
   ```

## Advanced Usage

### Using OpenAI Models

By default, the Research Agent uses OpenAI models. Ensure your `.env` file has a valid OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### Using Local Models via Ollama

To use local models, ensure Ollama is installed and running, and configure your `.env` file:

```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:7b
```

### Customizing Search Behavior

You can customize the search behavior by setting environment variables:

```
SEARCH_ENGINE=google  # Options: google, bing, duckduckgo
SEARCH_API_KEY=your_search_api_key_here  # If required by the search engine
```

### Using Vector Database for RAG

To enable retrieval-augmented generation (RAG), configure your `.env` file:

```
VECTOR_DB_TYPE=chroma  # Options: chroma, faiss, qdrant
VECTOR_DB_PATH=${RESEARCH_DATA_PATH}/vector_db
```

## Command-Line Arguments

The Research Agent supports the following command-line arguments:

```
scripts\run.cmd [options]
```

Options:
- `--model <model>`: Specify the model to use (openai or ollama)
- `--topic <topic>`: Specify the research topic (skips the prompt)
- `--verbose`: Enable verbose logging

Example:
```
scripts\run.cmd --model ollama --topic "The impact of artificial intelligence on healthcare" --verbose
```

## Troubleshooting

If you encounter issues, check the log file:

```
logs\research_agent.log
```

Common issues:
- **API Key Issues**: Ensure your OpenAI API key is valid and has sufficient credits
- **Ollama Connection Issues**: Ensure Ollama is running and accessible at the configured URL
- **Storage Issues**: Ensure the external storage path exists and is writable
