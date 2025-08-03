#!/usr/bin/env python3
"""Test script with deeply nested classes and methods."""

import abc
from typing import Any, Optional
from dataclasses import dataclass

@dataclass
class Configuration:
    """Configuration dataclass."""
    host: str = "localhost"
    port: int = 8080
    debug: bool = False

class BaseProcessor(abc.ABC):
    """Abstract base processor class."""
    
    def __init__(self, config: Configuration):
        self.config = config
        self.data = []
    
    @abc.abstractmethod
    def process(self, item: Any) -> Any:
        """Process an item."""
        pass
    
    class InternalValidator:
        """Internal validator class."""
        
        def __init__(self):
            self.rules = []
        
        def add_rule(self, rule):
            """Add a validation rule."""
            self.rules.append(rule)
        
        def validate(self, data):
            """Validate data against all rules."""
            for rule in self.rules:
                if not rule(data):
                    return False
            return True
        
        class NestedRuleEngine:
            """Deeply nested rule engine."""
            
            def __init__(self):
                self.engine_rules = {}
            
            def register(self, name, func):
                """Register a rule function."""
                self.engine_rules[name] = func
            
            def execute(self, name, data):
                """Execute a named rule."""
                if name in self.engine_rules:
                    return self.engine_rules[name](data)
                return None
            
            class DeeplyNestedAnalyzer:
                """Even more deeply nested analyzer."""
                
                def __init__(self):
                    self.analysis_cache = {}
                
                def analyze(self, input_data):
                    """Perform deep analysis."""
                    if id(input_data) in self.analysis_cache:
                        return self.analysis_cache[id(input_data)]
                    
                    result = {
                        'type': type(input_data).__name__,
                        'size': len(str(input_data)),
                        'hash': hash(str(input_data))
                    }
                    
                    self.analysis_cache[id(input_data)] = result
                    return result
                
                def clear_cache(self):
                    """Clear the analysis cache."""
                    self.analysis_cache.clear()

class DataProcessor(BaseProcessor):
    """Concrete implementation of processor."""
    
    def __init__(self, config: Configuration):
        super().__init__(config)
        self.validator = self.InternalValidator()
        self.setup_validators()
    
    def setup_validators(self):
        """Set up validation rules."""
        self.validator.add_rule(lambda x: x is not None)
        self.validator.add_rule(lambda x: len(str(x)) > 0)
    
    def process(self, item: Any) -> Optional[Any]:
        """Process an item with validation."""
        if self.validator.validate(item):
            processed = str(item).upper()
            self.data.append(processed)
            return processed
        return None
    
    def process_batch(self, items: list) -> list:
        """Process a batch of items."""
        results = []
        for item in items:
            result = self.process(item)
            if result:
                results.append(result)
        return results

def main():
    """Main function to test the nested classes."""
    config = Configuration(debug=True)
    processor = DataProcessor(config)
    
    test_items = ["hello", "world", "", None, "python"]
    results = processor.process_batch(test_items)
    
    print(f"Processed {len(results)} items successfully")
    print(f"Results: {results}")
    
    # Test the deeply nested classes
    validator = processor.InternalValidator()
    engine = validator.NestedRuleEngine()
    analyzer = engine.DeeplyNestedAnalyzer()
    
    analysis = analyzer.analyze(results)
    print(f"Analysis: {analysis}")

if __name__ == "__main__":
    main()