# Code Completion Context Tools

This repository provides tools for analyzing Python code dependencies, simplifying complex code structures, and generating summaries using LLMs. It's designed to help developers better understand and maintain their codebases.

## Features

- **Dependency Analysis**: Visualize Python module dependencies with or without standard libraries.
- **Code Simplification**: Reduce code complexity by abbreviating deeply nested blocks.
- **LLM Integration**: Generate code summaries using Large Language Models (LLMs).
- **Database Storage**: Store analysis results in a SQLite database for tracking and future reference.

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/calhounpaul/code-completion-context-tools
   cd code-completion-context-tools
   ```

2. Set up the environment:
   ```bash
   chmod +x setup_dirs.sh
   ./setup_dirs.sh
   ```

3. Install dependencies and run the tool:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

## Usage

### Analyze Dependencies
```bash
./run.sh deps path/to/your/script.py [--with-stdlib]
```

### Simplify Code
```bash
./run.sh abbreviate path/to/your/script.py [--depth N] [--debug]
```

### Run All Tests
```bash
./run.sh test [--no-ensure-repo]
```

### View Database
```bash
./run.sh db --list
```

## Project Structure

```
code-completion-context-tools/
├── app.py                  # Main application
├── run.sh                  # Runner script
├── setup_dirs.sh           # Directory setup script
├── requirements.txt       # Python dependencies
├── test.sh                 # Test script
└── libs/                   # Python library modules
    ├── abbreviator.py      # Code abbreviation module
    ├── enhance_dependencies.py # Dependency enhancement
    ├── pydeps_tools.py     # Dependency analysis
    ├── query_llm.py        # LLM integration
    ├── schema.sql          # Database schema
    └── prompts/           # LLM prompt templates
```

## How It Works

1. **Dependency Analysis**: Uses `pydeps` to analyze module dependencies.
2. **Code Simplification**: Uses `libcst` to parse and abbreviate nested code blocks.
3. **LLM Integration**: Generates code summaries using configured LLM endpoints.

## Requirements

- Python 3.7+
- See `requirements.txt` for dependencies
