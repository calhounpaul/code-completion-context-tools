#!/bin/bash

# Setup constants
VENV_DIR="venv"
FLAGFILE_INSTALL="${VENV_DIR}/.completed_installation"
REQUIREMENTS_FILE="requirements.txt"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Code Analysis Tool Runner${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Make sure python3-venv is installed."
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created successfully.${NC}"
fi

# Install or update requirements if needed
if [ ! -f "$FLAGFILE_INSTALL" ] || [ "$REQUIREMENTS_FILE" -nt "$FLAGFILE_INSTALL" ]; then
    echo -e "${YELLOW}Installing/updating dependencies...${NC}"
    $VENV_DIR/bin/pip install --upgrade pip
    $VENV_DIR/bin/pip install -U -r $REQUIREMENTS_FILE
    
    if [ $? -eq 0 ]; then
        touch $FLAGFILE_INSTALL
        echo -e "${GREEN}Dependencies installed successfully.${NC}"
    else
        echo "Failed to install dependencies."
        exit 1
    fi
fi

# Create necessary directories
mkdir -p data/output
mkdir -p data/output/summaries

# Run the application
echo -e "${YELLOW}Running application...${NC}"

# Run the app with all arguments
$VENV_DIR/bin/python app.py "$@"