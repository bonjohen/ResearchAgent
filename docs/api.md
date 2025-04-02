# API Reference

This document provides a reference for the Research Agent API.

## ResearchManager

The `ResearchManager` class is the main entry point for the Research Agent.

```python
from src.agents.manager import ResearchManager

# Initialize the manager
manager = ResearchManager()

# Run research on a topic
await manager.run("The impact of artificial intelligence on healthcare")
```

### Methods

#### `__init__()`

Initialize the ResearchManager.

#### `async run(query: str) -> None`

Run the research process for the given query.

- **Parameters**:
  - `query` (str): The research topic or question
- **Returns**: None

## Environment Configuration

The `environment` module handles loading and validating environment variables.

```python
from src.config.environment import load_environment, get_env

# Load environment variables
env_vars = load_environment()

# Get a specific environment variable
api_key = get_env("OPENAI_API_KEY")
```

### Functions

#### `load_environment() -> Dict[str, str]`

Load environment variables from .env file and validate them.

- **Returns**: Dictionary of environment variables
- **Raises**: ValueError if required environment variables are missing

#### `get_env(key: str, default: Optional[str] = None) -> str`

Get an environment variable with an optional default value.

- **Parameters**:
  - `key` (str): The environment variable key
  - `default` (Optional[str], optional): Default value if not set. Defaults to None.
- **Returns**: The environment variable value or default
- **Raises**: ValueError if the environment variable is not set and no default is provided

## Storage Utilities

The `storage` module handles external storage for the Research Agent.

```python
from src.utils.storage import setup_storage, get_storage_path, save_report

# Set up external storage
storage_path = setup_storage()

# Get path to a subdirectory
reports_dir = get_storage_path("reports")

# Save a report
report_path = save_report("# Report Content", "Research Topic")
```

### Functions

#### `setup_storage() -> Path`

Set up external storage for the Research Agent.

- **Returns**: Path to the external storage directory
- **Raises**: ValueError if the storage path is invalid or cannot be created

#### `get_storage_path(subdir: Optional[str] = None) -> Path`

Get the path to the external storage or a subdirectory.

- **Parameters**:
  - `subdir` (Optional[str], optional): Subdirectory name. Defaults to None.
- **Returns**: Path to the storage directory
- **Raises**: ValueError if the storage path is not set or invalid

#### `save_report(report_content: str, topic: str, format: str = "md") -> Path`

Save a research report to external storage.

- **Parameters**:
  - `report_content` (str): Report content
  - `topic` (str): Research topic
  - `format` (str, optional): File format. Defaults to "md".
- **Returns**: Path to the saved report

## Logging Utilities

The `logger` module provides logging functionality for the Research Agent.

```python
from src.utils.logger import setup_logger, get_logger

# Set up the root logger
logger = setup_logger()

# Get a logger for a specific module
module_logger = get_logger(__name__)
```

### Functions

#### `setup_logger(name: Optional[str] = None, level: Optional[str] = None, log_format: str = DEFAULT_LOG_FORMAT) -> logging.Logger`

Set up and configure a logger.

- **Parameters**:
  - `name` (Optional[str], optional): Logger name. Defaults to None (root logger).
  - `level` (Optional[str], optional): Log level. Defaults to None (from environment or INFO).
  - `log_format` (str, optional): Log format. Defaults to DEFAULT_LOG_FORMAT.
- **Returns**: Configured logger

#### `get_logger(name: str) -> logging.Logger`

Get a logger with the specified name.

- **Parameters**:
  - `name` (str): Logger name
- **Returns**: Logger instance
