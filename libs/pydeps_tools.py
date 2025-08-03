"""
Python Dependency Analyzer Module

This module provides functions to analyze and visualize Python module dependencies
using the pydeps package.
"""

import subprocess
import json
import os
from typing import Dict, Any, Optional


def run_pydeps(script_path: str, include_pylib: bool = False) -> Optional[Dict[str, Any]]:
    """Run pydeps on the given script and return parsed JSON output.
    
    Args:
        script_path: Path to the Python script to analyze
        include_pylib: Whether to include Python standard library modules
        
    Returns:
        Dictionary of dependencies or None if error occurred
    """
    # Check if we're in a virtual environment and use its pydeps
    venv_pydeps = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "venv", "bin", "pydeps")
    if os.path.exists(venv_pydeps):
        pydeps_cmd = venv_pydeps
    else:
        pydeps_cmd = "pydeps"
    
    command = [
        pydeps_cmd,
        "--show-deps",
        "--no-output",
        script_path
    ]
    if include_pylib:
        command.append("--pylib")

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        
        # Check if output is empty or just {}
        if not result.stdout or result.stdout.strip() == '{}':
            print(f"Warning: pydeps returned empty output for {script_path}")
            print(f"This may happen if the script has no analyzable imports or if dependencies are not installed.")
            # Return a minimal structure with just the script itself
            script_name = os.path.basename(script_path)
            return {script_name: {"bacon": 0, "name": script_name, "path": script_path}}
        
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running pydeps: {e.stderr}")
        # Try to provide a minimal response even on error
        script_name = os.path.basename(script_path)
        return {script_name: {"bacon": 0, "name": script_name, "path": script_path, "error": str(e)}}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON output from pydeps: {e}")
        print(f"Output was: {result.stdout[:500]}")  # Show first 500 chars for debugging
        return None


def make_paths_relative(dependencies: Dict[str, Any], base_dir: str) -> Dict[str, Any]:
    """Convert absolute paths in dependencies to relative paths based on the script's directory.
    
    Args:
        dependencies: Dictionary of dependencies from run_pydeps
        base_dir: Base directory for relative paths
        
    Returns:
        Modified dependencies dictionary with relative paths
    """
    for dep in dependencies.values():
        if "path" in dep and dep["path"]:
            if dep["path"].startswith(base_dir):
                dep["path"] = os.path.relpath(dep["path"], base_dir)
    return dependencies


def save_dependencies(script_path: str, output_file: str, include_pylib: bool = False) -> None:
    """Run pydeps, process paths, and save the output as JSON.
    
    Args:
        script_path: Path to the Python script to analyze
        output_file: Path to save the JSON output
        include_pylib: Whether to include Python standard library modules
    """
    dependencies = run_pydeps(script_path, include_pylib)
    if dependencies:
        script_dir = os.path.dirname(os.path.abspath(script_path))
        dependencies = make_paths_relative(dependencies, script_dir)
        with open(output_file, "w") as f:
            json.dump(dependencies, f, indent=2)
        print(f"Dependencies written to {output_file}")


def ensure_telegram_bot(repo_path: str = "./data/repos/telegram_bot") -> None:
    """Ensure the telegram_bot repository exists, cloning it if needed.
    
    Args:
        repo_path: Path where the telegram_bot repository should be located
    """
    if not os.path.exists(repo_path):
        # Create directory structure if it doesn't exist
        os.makedirs(os.path.dirname(repo_path), exist_ok=True)
        # Clone the repository to the specified location
        subprocess.run(["git", "clone", "https://github.com/calhounpaul/telegram_bot", repo_path])


def analyze_project(script_path: str = "./data/repos/telegram_bot/bot.py") -> None:
    """Analyze a project and save dependency information with and without stdlib.
    
    Args:
        script_path: Path to the main script to analyze
    """
    # Extract the directory from the script path to use for repo initialization
    repo_dir = os.path.dirname(script_path)
    if os.path.basename(repo_dir) == "telegram_bot":
        ensure_telegram_bot(repo_dir)
    else:
        ensure_telegram_bot()
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.join("data", "output"), exist_ok=True)
    
    # Save dependencies 
    save_dependencies(script_path, os.path.join("data", "output", "deps_min.json"))
    save_dependencies(script_path, os.path.join("data", "output", "deps_all.json"), include_pylib=True)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze Python dependencies.")
    parser.add_argument("script_path", nargs="?", default="./data/repos/telegram_bot/bot.py", 
                        help="Path to the script to analyze.")
    args = parser.parse_args()
    
    analyze_project(args.script_path)