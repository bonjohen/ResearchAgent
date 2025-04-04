# Research Agent Requirements

This document outlines the requirements for building a research agent using the OpenAI Agent SDK with support for both OpenAI models and local models via Ollama.

## 1. Core Functionality

1. The research agent should accept a research topic or question from the user
2. The agent should plan and execute web searches to gather relevant information
3. The agent should synthesize the information into a comprehensive report
4. The agent should provide follow-up questions for further research

## 2. Agent Architecture

### 2.1 Planning Agent
- Create a planning agent that breaks down the research topic into specific search queries
- The agent should provide reasoning for each search query
- Output should be a structured plan with 5-20 search terms
- Implement iterative query refinement based on initial search results
- Generate additional search queries by evaluating the results of a few initial web searches

### 2.2 Search Agent
- Create a search agent that executes web searches using the WebSearchTool
- The agent should summarize search results concisely (2-3 paragraphs, <300 words)
- The agent should focus on extracting key information and ignoring fluff

### 2.3 Writer Agent
- Create a writer agent that synthesizes search results into a cohesive report
- The report should be in markdown format
- The report should include a short summary, detailed content, and follow-up questions

## 3. Technical Requirements

1. Use the OpenAI Agent SDK for agent creation and orchestration
2. Implement proper error handling for failed searches or API issues
3. Use asynchronous processing for parallel search execution
4. Implement tracing for debugging and monitoring agent performance
5. Create a user-friendly interface for submitting research topics and viewing results

### 3.1 User Interface Requirements
- Provide both command-line and web-based interfaces
- Web UI should support real-time progress tracking
- Allow selection of model provider and search provider through the UI
- Support viewing and managing research reports
- Enable follow-up research through the UI
- Implement responsive design for different devices

### 3.2 Software Requirements

#### Core Dependencies
- Python 3.9+ as the primary programming language
- Flask 2.0.0+ for the web interface
- python-dotenv 1.0.0+ for environment variable management

#### API Integrations
- OpenAI API for cloud-based language models
- Ollama for local model hosting and inference

#### Web Search and Content Retrieval
- DuckDuckGo API for web search without API key
- Serper API for enhanced search capabilities
- Tavily API for additional search functionality
- Google Custom Search API for Google search integration
- Requests library for HTTP requests

#### Data Processing and Storage
- JSON for data serialization
- Markdown for report formatting
- Pathlib for cross-platform file path handling

#### Testing
- Pytest for unit and integration testing
- Selenium 4.0.0+ for web UI testing
- webdriver-manager 3.8.0+ for WebDriver management

#### Utilities
- Rich 13.0.0+ for enhanced terminal output
- tqdm 4.65.0+ for progress bars
- asyncio for asynchronous programming
- typing for type hints
- uuid for unique identifiers
- datetime for date/time handling
- threading for multi-threading support

#### Development and Automation
- venv for virtual environment management
- pip for package management
- CMD Batch Scripts for Windows automation

## 4. Output Requirements

### 4.1 Report Structure
- Short summary (2-3 sentences)
- Detailed markdown report (1000+ words)
- List of follow-up questions for further research

### 4.2 Iterative Research
- Support for automatic follow-up research based on generated questions
- Ability to run additional searches for follow-up questions
- Enhanced report generation incorporating follow-up research
- User control over whether to perform follow-up research

### 4.3 Adaptive Query Generation
- Generate a list of questions based on evaluating results of a few initial web search requests
- Use initial queries to determine appropriate search queries for comprehensive research
- Identify key subtopics and entities from initial search results
- Adapt search strategy based on discovered information
- Implement different query approaches (fan-out, iterative refinement, comparative)

### 4.4 Progress Tracking
- Display planning progress
- Show search progress (x/y searches completed)
- Indicate writing progress with status updates
- Track follow-up research progress separately

## 5. Enhancement Opportunities

1. **Retrieval Integration**
   - Add support for retrieving information from vector stores
   - Allow users to upload PDFs or other files as context for research

2. **Improved Planning**
   - Implement more sophisticated planning with iterative refinement
   - Add evaluation steps to assess search quality and decide if more searches are needed

3. **Code Execution**
   - Add support for running code for data analysis
   - Integrate data visualization capabilities

4. **User Customization**
   - Allow users to specify research depth and breadth
   - Enable users to provide additional context or constraints

## 6. Testing Requirements

1. Create unit tests for each agent component
2. Implement integration tests for the full research workflow
3. Test with various research topics of different complexity
4. Evaluate report quality against predefined metrics

## 7. Documentation Requirements

1. Document the agent architecture and workflow
2. Provide setup instructions including API key requirements
3. Create usage examples for different research scenarios
4. Document customization options and extension points

## 8. Ollama Integration for Local Models

### 8.1 Ollama Setup and Configuration
- Add support for connecting to Ollama-hosted local LLMs
- Create configuration options for specifying Ollama endpoint (default: http://localhost:11434)
- Implement model selection to use Llama3 7B or other compatible models
- Document system requirements for running Llama3 7B locally (RAM, GPU, etc.)

### 8.2 Model Provider Interface
- Create a model provider abstraction layer to switch between OpenAI and Ollama models
- Implement an OllamaModelProvider class that conforms to the Agent SDK's model interface
- Support configuration of model parameters (temperature, top_p, etc.) for Ollama models
- Handle differences in API responses between OpenAI and Ollama

## 9. Function Calling with Local Models

### 9.1 Function Calling Compatibility
- Implement function calling support for Ollama models that may not natively support it
- Create a parsing layer to extract tool calls from text responses if needed
- Provide fallback mechanisms when function calling is ambiguous
- Test and validate tool usage patterns with Llama3 7B

### 9.2 Prompt Engineering for Local Models
- Optimize prompts for local models to improve function calling reliability
- Create model-specific instructions that work well with Llama3 7B capabilities
- Implement prompt templates that clearly define the expected output format
- Test and refine prompts to ensure consistent tool usage

## 10. Web Search Integration for Local Models

### 10.1 Web Search Tool Compatibility
- Ensure the WebSearchTool works with Ollama-hosted models
- Create a standalone web search implementation if needed
- Support configurable search providers (Google, Serper, Tavily, DuckDuckGo, etc.)
- Implement rate limiting and caching to prevent excessive API calls
- Add fallback mechanisms between search providers
- Implement simulated search results when real results are unavailable

### 10.2 Search Result Processing
- Optimize search result formatting for local model context windows
- Implement chunking strategies for handling large search results
- Create summarization helpers to condense search results when needed
- Test search result processing with Llama3 7B's context window limitations

## 11. Performance Optimization

### 11.1 Resource Management
- Implement efficient resource usage for local model inference
- Add configuration options for batch size and parallel processing
- Create memory management strategies for large research tasks
- Support graceful degradation when system resources are limited

### 11.2 Caching and Optimization
- Implement response caching to reduce redundant model calls
- Add support for quantized models to improve performance
- Create options for trading off quality vs. speed
- Implement progress tracking that accounts for local inference times

## 12. Implementation Examples

### 12.1 Ollama Setup Code
```python
# Example configuration for Ollama model provider
from agents import Agent, WebSearchTool
from agents.models.custom import OllamaModelProvider

# Configure Ollama model provider
ollama_provider = OllamaModelProvider(
    model_name="llama3:7b",  # or other compatible model
    base_url="http://localhost:11434",
    temperature=0.7,
    context_window=4096,  # Adjust based on model capabilities
)

# Create agent with Ollama model
search_agent = Agent(
    name="Search agent",
    instructions="You are a research assistant...",
    tools=[WebSearchTool()],
    model=ollama_provider,
)
```

### 12.2 Ollama Installation
```batch
@echo off
REM Example Ollama setup commands for Windows

REM Download Ollama for Windows
echo Downloading Ollama for Windows...
powershell -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/ollama-windows-amd64.zip' -OutFile 'ollama.zip'"

REM Extract the ZIP file
echo Extracting Ollama...
powershell -Command "Expand-Archive -Path 'ollama.zip' -DestinationPath 'ollama' -Force"

REM Clean up the ZIP file
del ollama.zip

REM Pull Llama3 7B model
echo Pulling Llama3 7B model...
cd ollama
ollama.exe pull llama3:7b

REM Start Ollama server
echo Starting Ollama server...
start /B ollama.exe serve

REM Verify Ollama is working
echo Verifying Ollama is working...
powershell -Command "Invoke-RestMethod -Uri 'http://localhost:11434/api/tags'"

echo Ollama setup complete!
```

### 12.3 Environment Setup
```batch
@echo off
REM setup.cmd - Environment setup script

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please update the .env file with your API keys and configuration.
)

echo Setup complete! Virtual environment is activated.
```

## 13. Testing with Local Models

### 13.1 Model Compatibility Testing
- Test various Ollama-compatible models (Llama3 7B, 70B, etc.)
- Create benchmarks to compare performance and quality across models
- Test with different parameter settings to find optimal configurations
- Document recommended models and settings for different research tasks

### 13.2 Integration Testing
- Test the full research workflow with local models
- Validate that all components work together seamlessly
- Compare results between OpenAI and local models
- Create test cases that verify function calling reliability

## 14. Documentation for Local Model Usage

### 14.1 Ollama Setup Guide
- Provide step-by-step instructions for installing and configuring Ollama
- Document how to pull and run Llama3 7B or other compatible models
- Include troubleshooting tips for common Ollama issues
- Provide performance optimization recommendations

### 14.2 Configuration Options
- Document all configuration options for local model usage
- Provide examples for different research scenarios
- Include recommended settings for different hardware configurations
- Create a quick-start guide for getting up and running quickly

## 15. Development Principles

### 15.1 File Editing Safety

- All file edits must use safe replacement techniques that verify content before modification
- File content must be read completely before attempting edits to avoid word-wrapping issues
- Line numbers must be determined programmatically rather than visually
- String replacements must normalize whitespace and line endings for reliable matching
- When editing files, content should be matched using semantic comparison rather than exact string matching
- Helper utilities should be used to locate exact positions in files before making changes
- All file edits must be verified after completion to ensure correctness

### 15.2 Document-Driven Development

- All development work must be guided by the requirements and plan documents
- New features must be added to the requirements document before implementation
- Implementation must follow the sequence outlined in the plan document
- The plan document must be updated with necessary steps for any new requirements
- Development phases must be completed in the order specified in the plan document
- Any deviation from the plan must be explicitly approved before proceeding
- Regular references to the requirements and plan documents must be made during development

### 15.2 General Development Principles

The following principles should guide all development work on this project:

1. **Iterate on Existing Code**
   - Always look for existing code to iterate on instead of creating new code
   - Understand existing patterns before making changes

2. **Maintain Simplicity**
   - Always prefer simple solutions over complex ones
   - Keep the codebase clean and organized

3. **Avoid Duplication**
   - Check for other areas of the codebase that might already have similar functionality
   - Reuse existing code whenever possible

4. **Make Targeted Changes**
   - Only make changes that are requested or clearly understood
   - Focus on areas of code relevant to the task
   - Do not touch code that is unrelated to the task

5. **Preserve Working Patterns**
   - Do not introduce new patterns or technologies without first exhausting options with existing implementations
   - Avoid making major changes to architecture after it has proven to work well
   - If introducing a new pattern, remove the old implementation to avoid duplicate logic

6. **Code Organization**
   - Avoid files over 200-300 lines of code; refactor when they grow beyond this size
   - Consider impacts on other methods and areas of code when making changes

7. **Testing**
   - Write thorough tests for all major functionality
   - Ensure tests cover both happy paths and edge cases

8. **Configuration Safety**
   - Never overwrite .env files without first asking and confirming

## 16. Environment and Configuration

### 16.1 Environment Variables
- Use environment variables for all sensitive configuration (API keys, credentials)
- OpenAI API key should be retrieved from the Windows environment
- Create a .env.example file to document required environment variables without actual values
- Implement robust environment variable validation on startup

### 16.2 External File Storage
- Store data files outside of the project folder
- Retrieve the external storage path from an environment variable
- Implement fallback mechanisms if the environment variable is not set
- Create necessary directories if they don't exist

### 16.3 Windows Scripting
- Provide CMD batch files for common operations (setup, run, test)
- Use CMD instead of PowerShell for all scripts to ensure compatibility
- Ensure all scripts work properly in Windows environments
- Include clear documentation in script headers
- Add error handling and user feedback in scripts

## 17. Deployment Requirements

### 17.1 System Requirements

#### Development Environment
- Windows 10/11 or compatible operating system
- Minimum 8GB RAM (16GB recommended for local model inference)
- Minimum 4-core CPU (8-core recommended for local model inference)
- 20GB free disk space for application and dependencies
- 50GB+ free disk space if using local models via Ollama
- Internet connection for API access and web searches

#### Production Environment
- Shared hosting with Python support or VPS (Virtual Private Server)
- Linux-based server with Python 3.9+ support
- Minimum 4GB RAM for cloud-based models only
- Minimum 8GB RAM if using local models
- 10GB+ disk space (50GB+ if using local models)
- HTTPS support for secure API communication

### 17.2 GoDaddy Deployment

#### Hosting Requirements
- GoDaddy hosting plan with Python support
- SSH access for command-line operations
- Ability to configure environment variables
- Support for WSGI applications
- SSL certificate for secure connections

#### Deployment Process
- Create deployment-specific configuration
- Set up environment variables in hosting control panel
- Configure web server with WSGI support
- Set up external storage for research data
- Implement backup procedures
- Configure monitoring and error logging

#### Documentation
- Provide detailed deployment instructions
- Document server maintenance procedures
- Create administrator guide
- Include troubleshooting information

### 16.4 Virtual Environment Management
- Use venv for Python dependency management
- Include scripts to create and activate the virtual environment
- Document the Python version requirements
- Provide requirements.txt file for dependency installation

## 17. Additional Components for Local LLMs

### 17.1 Vector Database for RAG
- Implement a vector database for retrieval-augmented generation (RAG)
- Support options like Chroma, FAISS, or Qdrant for vector storage
- Include document chunking and embedding generation functionality
- Provide utilities for managing the vector database (add, delete, search)

### 17.2 Local Model Optimizations
- Support for quantized models to reduce memory requirements
- Implement context window management for models with limited context
- Add batching strategies for efficient processing
- Include memory usage monitoring and management

### 17.3 Caching Infrastructure
- Implement caching for model responses to improve performance
- Cache embeddings to avoid redundant computation
- Add cache invalidation strategies
- Support disk-based and memory-based caching options

### 17.4 Local Web Search Alternatives
- Implement fallback search mechanisms if API-based search is unavailable
- Consider local scraping options with proper rate limiting
- Support offline mode with previously cached search results
- Include configurable search providers
