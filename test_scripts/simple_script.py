#!/usr/bin/env python3
"""Simple test script with basic imports and functions."""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional

def process_data(data: List[Dict]) -> Dict:
    """Process a list of dictionaries and return summary statistics."""
    result = {
        'count': len(data),
        'timestamp': datetime.now().isoformat(),
        'items': []
    }
    
    for item in data:
        if 'id' in item and 'value' in item:
            processed = {
                'id': item['id'],
                'value': item['value'] * 2,
                'processed': True
            }
            result['items'].append(processed)
    
    return result

def save_to_file(data: Dict, filename: str) -> bool:
    """Save data to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False

def main():
    """Main function."""
    test_data = [
        {'id': 1, 'value': 10},
        {'id': 2, 'value': 20},
        {'id': 3, 'value': 30}
    ]
    
    result = process_data(test_data)
    print(f"Processed {result['count']} items")
    
    if save_to_file(result, 'output.json'):
        print("Data saved successfully")
    else:
        print("Failed to save data")

if __name__ == "__main__":
    main()