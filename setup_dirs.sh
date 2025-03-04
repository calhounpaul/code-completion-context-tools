#!/bin/bash

# Create necessary directory structure for the code analysis tool

# Create libs directory if it doesn't exist
mkdir -p libs

# Move Python modules to libs directory
if [ -f "abbreviator.py" ] && [ ! -f "libs/abbreviator.py" ]; then
    echo "Moving abbreviator.py to libs/"
    cp abbreviator.py libs/
fi

if [ -f "pydeps_tools.py" ] && [ ! -f "libs/pydeps_tools.py" ]; then
    echo "Moving pydeps_tools.py to libs/"
    cp pydeps_tools.py libs/
fi

# Create data directory structure
mkdir -p data/output/dependencies
mkdir -p data/output/abbreviations
mkdir -p data/output/summaries
mkdir -p data/db
mkdir -p data/logs
mkdir -p data/repos

# Create db directory
if [ -f "libs/schema.sql" ]; then
    echo "Initializing database from schema..."
    sqlite3 data/db/code_analysis.db < libs/schema.sql
else
    echo "Schema file not found. Database will be created by app.py"
    # Just create the empty directory, don't create the database file
    # as app.py will create it with the right schema
fi

# Create logs directory and initial log file
touch data/logs/app.log

echo "Directory structure created successfully."
echo "Run ./run.sh to start the application."