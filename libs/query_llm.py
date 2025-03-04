import os
import logging
import glob
import time
from openai import OpenAI
from typing import List, Dict, Union, Optional, Tuple
import prompts.summarize_templates
import sys

# Add the libs directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs"))

# Import modules from libs directory
from abbreviator import abbreviate_code

def get_llm_response(
    messages: List[Dict[str, str]],
    model_name: str = "deepseek-ai/DeepSeek-V3",
    api_base: str = "https://api.hyperbolic.xyz/v1/",
    max_tokens: int = 2048,
    temperature: float = 0.7,
    top_p: float = 0.95,
    stream: bool = False,
    token_file: str = "secrets/hyperbolic_api_key.txt"
) -> Union[str, object]:
    """
    Send a formatted conversation to an LLM and get the response.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
                 Format: [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]
        model_name: Name of the model to use (default: DeepSeek-V3)
        api_base: Base URL for the API
        max_tokens: Maximum tokens in the response
        temperature: Sampling temperature (0.0 to 1.0)
        top_p: Nucleus sampling parameter
        stream: Whether to stream the response
        token_file: File containing the API token
        
    Returns:
        If stream=False: The text response from the LLM
        If stream=True: The streaming response object
    """
    # Read the API token
    try:
        with open(token_file, "r") as f:
            api_key = f.read().strip()
    except Exception as e:
        logging.error(f"Error reading token file {token_file}: {e}")
        raise
    
    # Initialize the client
    client = OpenAI(base_url=api_base, api_key=api_key)
    
    try:
        # Create a chat completion
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=stream
        )
        
        if stream:
            # Return the stream object for the caller to iterate
            return response
        else:
            # Return just the text content
            return response.choices[0].message.content
            
    except Exception as e:
        logging.error(f"Error getting LLM response: {e}")
        raise

def summarize_script(
    script: str,
    model_name: str = "deepseek-ai/DeepSeek-V3",
    api_base: str = "https://api.hyperbolic.xyz/v1/",):
    """
    Summarize a complete script using an LLM.
    
    Args:
        script: The content of the script to summarize
        model_name: Name of the model to use
        api_base: Base URL for the API
        
    Returns:
        A summary of the script
    """
    return get_llm_response(
        messages=[{"role": "user", "content": prompts.summarize_templates.ABBREVIATED_SCRIPT.format(script=script)}],
        model_name=model_name,
        api_base=api_base
    )

def summarize_code(
    dependencies: str,
    preceding_context: str,
    following_context: str,
    snippet: str,
    model_name: str = "deepseek-ai/DeepSeek-V3",
    api_base: str = "https://api.hyperbolic.xyz/v1/",
):
    """
    Summarize a code snippet with context using an LLM.
    
    Args:
        dependencies: Dependencies related to the code
        preceding_context: Code that comes before the snippet
        following_context: Code that comes after the snippet
        snippet: The code snippet to summarize
        model_name: Name of the model to use
        api_base: Base URL for the API
        
    Returns:
        A summary of the code snippet
    """
    return get_llm_response(
        messages=[{"role": "user", "content": prompts.summarize_templates.SNIPPET_WITH_ABBREVIATED_CONTEXT.format(
            dependencies=dependencies,
            preceding_context=preceding_context,
            following_context=following_context,
            snippet=snippet
        )}],
        model_name=model_name,
        api_base=api_base,
    )

def summarize_all_telegram_bot_scripts(
    repo_path: str = "data/repos/telegram_bot",
    depth: int = 2,
    preserve_chars: int = 90,
    preserve_lines: int = 2,
    min_char_count: int = 10,
    output_dir: str = "data/output/summaries",
    model_name: str = "deepseek-ai/DeepSeek-V3",
    api_base: str = "https://api.hyperbolic.xyz/v1/",
):
    """
    Summarize all Python scripts in the telegram_bot repository, after first abbreviating them.
    
    Args:
        repo_path: Path to the telegram_bot repository
        depth: Maximum nesting depth to preserve when abbreviating (default: 2)
        preserve_chars: Number of characters to preserve per line in abbreviation
        preserve_lines: Number of lines to preserve in abbreviation
        min_char_count: Minimum character count for a file to be summarized
        output_dir: Directory to save the summaries
        model_name: Name of the model to use
        api_base: Base URL for the API
        
    Returns:
        A dictionary mapping file paths to their summaries
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create abbreviations directory
    abbrev_dir = os.path.join("data", "output", "abbreviations")
    os.makedirs(abbrev_dir, exist_ok=True)
    
    # Find all Python files in the repository
    py_files = glob.glob(os.path.join(repo_path, "**/*.py"), recursive=True)
    
    if not py_files:
        print(f"No Python files found in {repo_path}")
        return {}
    
    print(f"Found {len(py_files)} Python files to process")
    
    summaries = {}
    
    for py_file in py_files:
        try:
            # Read the file
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Skip files that are too small
            if len(content) <= min_char_count:
                print(f"Skipping {py_file} - too small ({len(content)} chars)")
                continue
            
            print(f"\nProcessing {py_file} ({len(content)} chars)")
            
            # Abbreviate the code to depth 2
            abbreviated_code = abbreviate_code(content, depth, preserve_chars, preserve_lines)
            
            # Save the abbreviated code to a file, following project conventions
            base_name = os.path.basename(py_file)
            name, ext = os.path.splitext(base_name)
            timestamp = int(time.time())
            abbreviated_file = os.path.join(abbrev_dir, f"{name}_depth{depth}_{timestamp}{ext}")
            
            with open(abbreviated_file, "w", encoding="utf-8") as f:
                f.write(abbreviated_code)
            
            print(f"Abbreviated code written to {abbreviated_file} ({len(abbreviated_code)} chars)")
            
            # Summarize the abbreviated code
            summary = summarize_script(abbreviated_code, model_name, api_base)
            
            # Save the summary
            relative_path = os.path.relpath(py_file, repo_path)
            summary_file = os.path.join(output_dir, f"{relative_path}.summary.txt")
            
            # Create subdirectories if needed
            os.makedirs(os.path.dirname(summary_file), exist_ok=True)
            
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(summary)
            
            print(f"Summary saved to {summary_file}")
            
            # Store in results dictionary
            summaries[py_file] = summary
            
        except Exception as e:
            print(f"Error processing {py_file}: {e}")
    
    return summaries

# Example usage
if __name__ == "__main__":
    # Example conversation
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about quantum computing."}
    ]
    
    # Non-streaming example
    try:
        response = get_llm_response(conversation)
        print("\n--- LLM Response ---")
        print(response)
    except Exception as e:
        print(f"Error: {e}")
    
    # Streaming example
    try:
        print("\n--- Streaming Response ---")
        stream = get_llm_response(conversation, stream=True)
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta is not None:
                print(delta, end="")
    except Exception as e:
        print(f"Error in streaming: {e}")
    
    # Summarize all scripts in telegram_bot
    try:
        print("\n--- Summarizing All Scripts ---")
        summaries = summarize_all_telegram_bot_scripts()
        print(f"Successfully summarized {len(summaries)} scripts")
    except Exception as e:
        print(f"Error summarizing scripts: {e}")