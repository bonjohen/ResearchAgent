# Development Guide

This guide provides information for developers who want to contribute to the Research Agent.

## Development Environment Setup

1. **Clone the Repository**

   ```
   git clone https://github.com/yourusername/research-agent.git
   cd research-agent
   ```

2. **Run the Setup Script**

   ```
   scripts\setup.cmd
   ```

3. **Activate the Virtual Environment**

   ```
   call venv\Scripts\activate.bat
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

## Development Principles

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

## Running Tests

To run the test suite:

```
scripts\test.cmd
```

To run a specific test:

```
call venv\Scripts\activate.bat
pytest tests/test_file.py::TestClass::test_function -v
```

## Code Style

This project follows PEP 8 style guidelines. To check your code:

```
call venv\Scripts\activate.bat
flake8 src tests
```

## Documentation

When adding new features, please update the relevant documentation:

- Update docstrings for new functions and classes
- Update the API reference if necessary
- Add usage examples for new features

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the tests
5. Submit a pull request

## Release Process

1. Update version number in `src/config/version.py`
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. Tag the release with the version number
