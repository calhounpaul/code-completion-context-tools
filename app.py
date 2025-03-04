#!/usr/bin/env python3
"""
Code Analysis Tool

This script combines the functionality of pydeps_module and code_abbreviator_module to:
1. Analyze Python dependencies of a target script
2. Abbreviate Python code by reducing nesting depth
3. Summarize Python code using LLM queries
4. Enhance dependency data with script summaries

It can be used to analyze and simplify complex Python code structures.
Results are stored in a SQLite database for tracking and future reference.
"""

import argparse
import os
import sys
import glob
import hashlib
import json
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

# Add the libs directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs"))

# Import modules from libs directory
import pydeps_tools as pydeps
from abbreviator import abbreviate_code

# Import optional modules if they exist
try:
    import query_llm
    HAS_QUERY_LLM = True
except ImportError:
    HAS_QUERY_LLM = False

try:
    import enhance_dependencies
    HAS_ENHANCE_DEPS = True
except ImportError:
    HAS_ENHANCE_DEPS = False


def setup_database() -> sqlite3.Connection:
    """
    Create and set up the SQLite database for storing analysis results.
    
    Returns:
        A connection to the SQLite database
    """
    # Updated to use data/db directory for database
    db_path = os.path.join("data", "db", "code_analysis.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT,
        file_size INTEGER,
        file_md5 TEXT,
        modified_date TEXT,
        analysis_date TEXT,
        analysis_type TEXT,
        parameters TEXT,
        output_path TEXT,
        characters_saved INTEGER,
        percent_saved REAL
    )
    ''')
    
    conn.commit()
    return conn


def calculate_md5(file_path: str) -> str:
    """
    Calculate MD5 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MD5 hash as a hexadecimal string
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def analyze_dependencies(
    conn: sqlite3.Connection, 
    script_path: str = "./data/repos/telegram_bot/bot.py", 
    with_stdlib: bool = False
) -> str:
    """
    Analyze dependencies of a Python script and save to database.
    
    Args:
        conn: Database connection
        script_path: Path to the script to analyze
        with_stdlib: Whether to include standard library dependencies
        
    Returns:
        Path to the output file
    """
    print(f"\n{'='*60}")
    print(f"Analyzing dependencies for {script_path}")
    print(f"{'='*60}")
    
    # Create dependencies directory if it doesn't exist
    deps_dir = os.path.join("data", "output", "dependencies")
    os.makedirs(deps_dir, exist_ok=True)
    
    output_file = os.path.join(deps_dir, f"deps_{'all' if with_stdlib else 'min'}_{int(time.time())}.json")
    
    # Run analysis
    pydeps.save_dependencies(script_path, output_file, with_stdlib)
    
    # Save metadata to database
    cursor = conn.cursor()
    
    try:
        file_size = os.path.getsize(script_path)
        file_md5 = calculate_md5(script_path)
        modified_date = datetime.fromtimestamp(os.path.getmtime(script_path)).isoformat()
        
        cursor.execute(
            '''
            INSERT INTO analysis_results 
            (file_path, file_size, file_md5, modified_date, analysis_date, 
             analysis_type, parameters, output_path, characters_saved, percent_saved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                script_path, 
                file_size, 
                file_md5, 
                modified_date,
                datetime.now().isoformat(),
                "dependency_analysis",
                json.dumps({"with_stdlib": with_stdlib}),
                output_file,
                0,  # No characters saved for dependency analysis
                0.0  # No percentage saved for dependency analysis
            )
        )
        conn.commit()
    except Exception as e:
        print(f"Error saving to database: {e}")
    
    return output_file


def abbreviate_code_file(
    conn: sqlite3.Connection,
    input_file: str, 
    depth: int,
    preserve_chars: int = 30,
    preserve_lines: int = 2, 
    debug: bool = False
) -> str:
    """
    Abbreviate code in a file and save metadata to database.
    
    Args:
        conn: Database connection
        input_file: Path to the input file
        depth: Maximum nesting depth to preserve
        preserve_chars: Number of characters to preserve per line (default: 10)
        preserve_lines: Number of lines to preserve (default: 2)
        debug: Whether to enable debug output
        
    Returns:
        Path to the output file
    """
    print(f"\n{'='*60}")
    print(f"Abbreviating code in {input_file} (max depth: {depth}, preserve_chars: {preserve_chars}, preserve_lines: {preserve_lines})")
    print(f"{'='*60}")
    
    # Read the input file
    with open(input_file, "r", encoding="utf-8") as f:
        code = f.read()
    
    # Abbreviate the code
    abbreviated_code = abbreviate_code(code, depth, preserve_chars, preserve_lines, debug)
    
    # Generate the output file name in data/output/abbreviations directory
    base_name = os.path.basename(input_file)
    name, ext = os.path.splitext(base_name)
    timestamp = int(time.time())
    
    # Create abbreviations directory if it doesn't exist
    abbrev_dir = os.path.join("data", "output", "abbreviations")
    os.makedirs(abbrev_dir, exist_ok=True)
    
    output_file = os.path.join(abbrev_dir, f"{name}_depth{depth}_{timestamp}{ext}")
    
    # Write the abbreviated code to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(abbreviated_code)
    
    # Calculate statistics
    original_chars = len(code)
    abbreviated_chars = len(abbreviated_code)
    chars_saved = original_chars - abbreviated_chars
    percent_saved = (chars_saved / original_chars) * 100 if original_chars > 0 else 0
    
    print(f"Abbreviated code written to {output_file}")
    print(f"Original file: {original_chars} characters")
    print(f"Abbreviated file: {abbreviated_chars} characters")
    print(f"Characters saved: {chars_saved} ({percent_saved:.2f}%)")
    
    # Save metadata to database
    cursor = conn.cursor()
    
    try:
        file_size = os.path.getsize(input_file)
        file_md5 = calculate_md5(input_file)
        modified_date = datetime.fromtimestamp(os.path.getmtime(input_file)).isoformat()
        
        cursor.execute(
            '''
            INSERT INTO analysis_results 
            (file_path, file_size, file_md5, modified_date, analysis_date, 
             analysis_type, parameters, output_path, characters_saved, percent_saved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                input_file, 
                file_size, 
                file_md5, 
                modified_date,
                datetime.now().isoformat(),
                "code_abbreviation",
                json.dumps({"depth": depth, "preserve_chars": preserve_chars, "preserve_lines": preserve_lines, "debug": debug}),
                output_file,
                chars_saved,
                percent_saved
            )
        )
        conn.commit()
    except Exception as e:
        print(f"Error saving to database: {e}")
    
    return output_file


def summarize_abbreviated_code(
    repo_path: str,
    output_dir: str = "data/output/summaries", 
    depth: int = 2,
    min_char_count: int = 10
) -> Dict[str, str]:
    """
    Summarize all the abbreviated Python files using the query_llm module.
    
    Args:
        repo_path: Path to the repository containing Python files
        output_dir: Directory to save the summaries
        depth: Maximum nesting depth used in abbreviation
        min_char_count: Minimum character count for a file to be summarized
        
    Returns:
        Dictionary mapping file paths to their summaries
    """
    if not HAS_QUERY_LLM:
        print("\nSummarization skipped: query_llm module not available")
        return {}
    
    print(f"\n{'='*60}")
    print(f"Summarizing Python scripts in {repo_path}")
    print(f"{'='*60}")
    
    try:
        summaries = query_llm.summarize_all_telegram_bot_scripts(
            repo_path=repo_path,
            depth=depth,
            min_char_count=min_char_count
        )
        print(f"Successfully summarized {len(summaries)} scripts")
        return summaries
    except Exception as e:
        print(f"Error summarizing scripts: {e}")
        import traceback
        traceback.print_exc()
        return {}


def enhance_dependencies_with_summaries(
    deps_file: str,
    summaries_dir: str = "data/output/summaries",
    output_dir: str = "data/output/enhanced_dependencies"
) -> str:
    """
    Enhance the dependencies JSON with script summaries.
    
    Args:
        deps_file: Path to the dependencies JSON file
        summaries_dir: Directory containing script summaries
        output_dir: Directory to save the enhanced dependencies
        
    Returns:
        Path to the enhanced dependencies file
    """
    if not HAS_ENHANCE_DEPS:
        print("\nEnhancing dependencies skipped: enhance_dependencies module not available")
        return deps_file
    
    print(f"\n{'='*60}")
    print(f"Enhancing dependencies with script summaries")
    print(f"{'='*60}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output file with timestamp
    timestamp = int(time.time())
    output_file = os.path.join(output_dir, f"deps_enhanced_{timestamp}.json")
    
    try:
        # Call the enhance_dependencies function
        enhance_dependencies.enhance_dependencies(deps_file, summaries_dir, output_file)
        print(f"Enhanced dependencies saved to {output_file}")
        return output_file
    except Exception as e:
        print(f"Error enhancing dependencies: {e}")
        import traceback
        traceback.print_exc()
        return deps_file


def run_all_tests(
    conn: sqlite3.Connection, 
    ensure_repo: bool = True, 
    with_summarization: bool = True,
    with_enhancement: bool = True
) -> None:
    """
    Run all tests on all Python files in the telegram_bot folder.
    
    Args:
        conn: Database connection
        ensure_repo: Whether to ensure the telegram_bot repo exists
        with_summarization: Whether to run summarization after abbreviation
        with_enhancement: Whether to enhance dependencies with summaries
    """
    # Updated path for the telegram_bot repository
    repo_path = os.path.join("data", "repos", "telegram_bot")
    
    # Make sure the telegram bot repository exists if requested
    if ensure_repo:
        pydeps.ensure_telegram_bot(repo_path)
    
    # 1. Analyze dependencies with updated paths
    deps_min_file = analyze_dependencies(conn, os.path.join(repo_path, "bot.py"), False)  # Without stdlib
    analyze_dependencies(conn, os.path.join(repo_path, "bot.py"), True)   # With stdlib
    
    # Find all Python files in the telegram_bot folder
    py_files = glob.glob(os.path.join(repo_path, "**/*.py"), recursive=True)
    if not py_files:
        print(f"No Python files found in the {repo_path} folder.")
        return
    
    print(f"\nFound {len(py_files)} Python files to process.")
    
    # 2. Abbreviate each Python file with depth=1
    for py_file in py_files:
        try:
            abbreviate_code_file(conn, py_file, 1, 90, 2, True)
        except Exception as e:
            print(f"Error abbreviating {py_file} with depth 1: {e}")
    
    # 3. Abbreviate each Python file with depth=2
    for py_file in py_files:
        try:
            abbreviate_code_file(conn, py_file, 2, 90, 2, True)
        except Exception as e:
            print(f"Error abbreviating {py_file} with depth 2: {e}")
    
    # 4. Run summarization if requested and available
    summaries = {}
    if with_summarization and HAS_QUERY_LLM:
        summaries = summarize_abbreviated_code(repo_path)
    
    # 5. Enhance dependencies with summaries if requested and available
    if with_enhancement and HAS_ENHANCE_DEPS and summaries:
        enhance_dependencies_with_summaries(deps_min_file)


def main():
    """Main entry point for the script."""
    # Set up the database
    conn = setup_database()
    
    parser = argparse.ArgumentParser(
        description="Combined tool for Python dependency analysis and code abbreviation"
    )
    
    # Create subparsers for different modes
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Dependencies parser
    deps_parser = subparsers.add_parser("deps", help="Analyze Python dependencies")
    deps_parser.add_argument("script_path", help="Path to the script to analyze")
    deps_parser.add_argument("--with-stdlib", action="store_true", 
                            help="Include standard library dependencies")
    
    # Abbreviate parser
    abbr_parser = subparsers.add_parser("abbreviate", help="Abbreviate Python code")
    abbr_parser.add_argument("input_file", help="Path to the Python file to abbreviate")
    abbr_parser.add_argument("--depth", type=int, default=2,
                           help="Maximum nesting depth to preserve (default: 2)")
    abbr_parser.add_argument("--preserve-chars", type=int, default=90,
                           help="Number of characters to preserve per line (default: 90)")
    abbr_parser.add_argument("--preserve-lines", type=int, default=2,
                           help="Number of lines to preserve (default: 2)")
    abbr_parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    # Summarize parser
    if HAS_QUERY_LLM:
        summ_parser = subparsers.add_parser("summarize", help="Summarize Python code")
        summ_parser.add_argument("repo_path", nargs="?", default="data/repos/telegram_bot", 
                               help="Path to the repository containing Python files")
        summ_parser.add_argument("--depth", type=int, default=2,
                               help="Depth used for abbreviation (default: 2)")
        summ_parser.add_argument("--min-chars", type=int, default=10,
                               help="Minimum character count for summarization (default: 10)")
    
    # Enhance dependencies parser
    if HAS_ENHANCE_DEPS:
        enhance_parser = subparsers.add_parser("enhance", help="Enhance dependencies with summaries")
        enhance_parser.add_argument("deps_file", help="Path to the dependencies JSON file")
        enhance_parser.add_argument("--summaries-dir", default="data/output/summaries",
                                 help="Directory containing script summaries")
        enhance_parser.add_argument("--output-dir", default="data/output/enhanced_dependencies",
                                 help="Directory to save the enhanced dependencies")
    
    # Test parser (runs all tools in sequence)
    test_parser = subparsers.add_parser("test", help="Run all tests on all Python files in telegram_bot")
    test_parser.add_argument("--no-ensure-repo", action="store_true",
                          help="Skip ensuring the telegram_bot repo exists")
    test_parser.add_argument("--no-summarization", action="store_true",
                          help="Skip summarization step")
    test_parser.add_argument("--no-enhancement", action="store_true",
                          help="Skip dependency enhancement step")
    
    # Database parser
    db_parser = subparsers.add_parser("db", help="Database operations")
    db_parser.add_argument("--list", action="store_true", help="List all analysis results")
    
    args = parser.parse_args()
    
    # If no command is specified, show help
    if not args.command:
        parser.print_help()
        conn.close()
        return
    
    # Handle commands
    try:
        if args.command == "deps":
            analyze_dependencies(conn, args.script_path, args.with_stdlib)
        elif args.command == "abbreviate":
            preserve_chars = getattr(args, 'preserve_chars', 90)
            preserve_lines = getattr(args, 'preserve_lines', 2)
            abbreviate_code_file(conn, args.input_file, args.depth, preserve_chars, preserve_lines, args.debug)
        elif args.command == "summarize" and HAS_QUERY_LLM:
            summarize_abbreviated_code(args.repo_path, depth=args.depth, min_char_count=args.min_chars)
        elif args.command == "enhance" and HAS_ENHANCE_DEPS:
            enhance_dependencies_with_summaries(args.deps_file, args.summaries_dir, args.output_dir)
        elif args.command == "test":
            run_all_tests(conn, not args.no_ensure_repo, not args.no_summarization, not args.no_enhancement)
        elif args.command == "db" and args.list:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, file_path, analysis_type, analysis_date, parameters, characters_saved, percent_saved 
                FROM analysis_results 
                ORDER BY analysis_date DESC
            ''')
            results = cursor.fetchall()
            
            if not results:
                print("No analysis results found in the database.")
            else:
                print("\nAnalysis Results:")
                print(f"{'ID':<5} {'File':<30} {'Type':<20} {'Date':<25} {'Params':<20} {'Chars Saved':<15} {'Percent':<10}")
                print("-" * 110)
                
                for row in results:
                    id, file_path, analysis_type, analysis_date, parameters, chars_saved, percent_saved = row
                    file_name = os.path.basename(file_path)
                    params = json.loads(parameters)
                    params_str = ", ".join(f"{k}={v}" for k, v in params.items())
                    
                    print(f"{id:<5} {file_name:<30} {analysis_type:<20} {analysis_date:<25} {params_str:<20} {chars_saved:<15} {percent_saved:<10.2f}%")
    finally:
        # Close the database connection
        conn.close()

if __name__ == "__main__":
    main()