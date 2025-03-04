#!/usr/bin/env python3
"""
Enhance Dependencies Script

This script takes a dependency JSON file and enhances it by adding script summaries
where available. For each module in the dependencies, it checks if a summary file exists
and adds the summary to the module's information.
"""

import json
import os
import sys
import glob
from pathlib import Path

def enhance_dependencies(deps_file, summaries_dir, output_file):
    """
    Enhance the dependencies JSON with available script summaries.
    
    Args:
        deps_file: Path to the dependencies JSON file
        summaries_dir: Directory containing summary files
        output_file: Path to save the enhanced dependencies JSON
    """
    print(f"Enhancing dependencies from {deps_file} with summaries from {summaries_dir}")
    
    # Read the dependencies JSON
    with open(deps_file, 'r') as f:
        dependencies = json.load(f)
    
    # Dictionary to store module summaries
    module_summaries = {}
    
    # Find all summary files
    summary_files = glob.glob(os.path.join(summaries_dir, "**/*.summary.txt"), recursive=True)
    print(f"Found {len(summary_files)} summary files")
    
    # Process each summary file
    for summary_file in summary_files:
        # Read the summary content
        with open(summary_file, 'r') as f:
            summary_content = f.read().strip()
        
        # Extract the relative path from the summary file
        rel_path = os.path.relpath(summary_file, summaries_dir)
        
        # Extract the module name from the summary file path
        # Remove the .summary.txt suffix
        module_path = rel_path.replace(".summary.txt", "")
        
        # Handle different possible module name formats
        if module_path == "bot.py":
            # Special case for bot.py at root level
            module_name = "bot.py"
        elif module_path.startswith("handlers/"):
            # Convert handlers/some_module.py to handlers.some_module
            parts = module_path.split("/")
            base_name = os.path.splitext(parts[1])[0]  # Remove .py extension
            module_name = f"handlers.{base_name}"
        else:
            # Fallback case - replace / with . and remove .py extension
            module_name = os.path.splitext(module_path)[0].replace("/", ".")
        
        # Store the summary with various possible module name formats to maximize matching chances
        module_summaries[module_name] = summary_content
        module_summaries[module_path] = summary_content
        
        # Also store with just the base name (without extension)
        base_name = os.path.splitext(os.path.basename(module_path))[0]
        module_summaries[base_name] = summary_content
        
        print(f"Loaded summary for {module_name}")
    
    # Enhance each module in the dependencies
    enhanced_count = 0
    for module_name, module_info in dependencies.items():
        # Try multiple matching strategies to find a summary
        if module_name in module_summaries:
            module_info["summary"] = module_summaries[module_name]
            enhanced_count += 1
            print(f"Enhanced {module_name} with summary")
        elif "name" in module_info and module_info["name"] in module_summaries:
            module_info["summary"] = module_summaries[module_info["name"]]
            enhanced_count += 1
            print(f"Enhanced {module_name} with summary (using name)")
        elif "path" in module_info and module_info["path"] and os.path.basename(module_info["path"]) in module_summaries:
            module_info["summary"] = module_summaries[os.path.basename(module_info["path"])]
            enhanced_count += 1
            print(f"Enhanced {module_name} with summary (using path basename)")
        else:
            # Try to match by converting module name to various formats
            base_name = module_name.split(".")[-1]
            if base_name in module_summaries:
                module_info["summary"] = module_summaries[base_name]
                enhanced_count += 1
                print(f"Enhanced {module_name} with summary (using base name)")
            else:
                print(f"No summary found for {module_name}")
    
    print(f"Enhanced {enhanced_count} module(s) with summaries")
    
    # Save the enhanced dependencies
    with open(output_file, 'w') as f:
        json.dump(dependencies, f, indent=2)
    
    print(f"Enhanced dependencies saved to {output_file}")


def main():
    """Main entry point for the script."""
    if len(sys.argv) != 4:
        print("Usage: enhance_dependencies.py <deps_file> <summaries_dir> <output_file>")
        sys.exit(1)
    
    deps_file = sys.argv[1]
    summaries_dir = sys.argv[2]
    output_file = sys.argv[3]
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    enhance_dependencies(deps_file, summaries_dir, output_file)


if __name__ == "__main__":
    main()