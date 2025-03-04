# Code Analysis Tool

A combined tool for Python dependency analysis and code abbreviation. This tool can analyze your Python code dependencies and simplify complex code structures by reducing nesting depth.

## Features

- **Dependency Analysis**: Analyze Python module dependencies with or without standard library modules.
- **Code Abbreviation**: Simplify code by abbreviating deeply nested blocks to reduce code complexity.
- **Database Storage**: All analysis results are stored in a SQLite database for future reference.
- **Command-line Interface**: Easy-to-use CLI for different analysis tasks.

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd code-analysis-tool
```

2. Run the setup script to create the directory structure:
```bash
chmod +x setup_dirs.sh
./setup_dirs.sh
```

3. Use the run script to set up the environment and run the tool:
```bash
chmod +x run.sh
./run.sh
```

The setup script will automatically create a virtual environment, install dependencies, and set up the database.

## Usage

The tool provides several commands:

### Analyze Dependencies

```bash
./run.sh deps path/to/your/script.py [--with-stdlib]
```

### Abbreviate Code

```bash
./run.sh abbreviate path/to/your/script.py [--depth N] [--debug]
```

### Run All Tests on Sample Code

```bash
./run.sh test [--no-ensure-repo]
```

### Database Operations

```bash
./run.sh db --list
```

## Project Structure

```
code-analysis-tool/
├── app.py                  # Main application
├── run.sh                  # Runner script
├── setup_dirs.sh           # Directory setup script
├── requirements.txt        # Python dependencies
├── schema.sql              # Database schema
├── data/                   # Data directory
│   ├── db/                 # Database files
│   ├── logs/               # Log files
│   └── output/             # Analysis output files
└── libs/                   # Python library modules
    ├── abbreviator.py      # Code abbreviation module
    └── pydeps_tools.py     # Dependency analysis module
```

## How It Works

### Dependency Analysis

The tool uses the `pydeps` package to analyze Python module dependencies. It can include or exclude standard library modules based on your needs.

### Code Abbreviation

The code abbreviation feature uses `libcst` to parse a Python file and abbreviate nested code blocks beyond a specified depth, replacing them with ellipsis comments and pass statements. It only abbreviates sections if doing so actually reduces the character count.

## License

[MIT License](LICENSE)
