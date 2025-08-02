#!/usr/bin/env python3
"""
⛧ Data Processor with Bugs ⛧
Test project for AI agent debugging

This file contains intentional bugs for testing the AI agent's ability to fix them.
"""

import json
import csv
from typing import List, Dict, Any

class DataProcessor:
    """A data processing class with intentional bugs."""
    
    def __init__(self):
        self.data = []
        self.errors = []
        self.processed_count = 0
    
    def load_json_data(self, file_path: str) -> bool:
        """Load data from JSON file."""
        try:
            # Bug: incorrect file opening
            with open(file_path, 'w') as f:  # Should be 'r'
                self.data = json.load(f)
            return True
        except Exception as e:
            # Bug: doesn't append to errors list
            print(f"Error loading JSON: {e}")  # Should be self.errors.append(str(e))
            return False
    
    def load_csv_data(self, file_path: str) -> bool:
        """Load data from CSV file."""
        try:
            # Bug: incorrect CSV reading
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                self.data = list(reader)
                # Bug: incorrect count
                self.processed_count = len(self.data) + 1  # Should be len(self.data)
            return True
        except Exception as e:
            self.errors.append(str(e))
            return False
    
    def filter_data(self, key: str, value: Any) -> List[Dict]:
        """Filter data by key-value pair."""
        # Bug: incorrect filtering logic
        filtered = []
        for item in self.data:
            if key in item and item[key] != value:  # Should be item[key] == value
                filtered.append(item)
        return filtered
    
    def sort_data(self, key: str, reverse: bool = False) -> List[Dict]:
        """Sort data by key."""
        # Bug: incorrect sorting
        if not self.data:
            return []
        
        # Bug: incorrect sort logic
        sorted_data = sorted(self.data, key=lambda x: x.get(key, 0), reverse=not reverse)  # Should be reverse=reverse
        return sorted_data
    
    def aggregate_data(self, group_key: str, value_key: str, operation: str = 'sum') -> Dict:
        """Aggregate data by group."""
        # Bug: incorrect aggregation
        result = {}
        
        for item in self.data:
            group = item.get(group_key, 'unknown')
            value = item.get(value_key, 0)
            
            if group not in result:
                result[group] = 0
            
            # Bug: incorrect operation
            if operation == 'sum':
                result[group] = result[group] - value  # Should be result[group] + value
            elif operation == 'count':
                result[group] = result[group] - 1  # Should be result[group] + 1
            elif operation == 'average':
                result[group] = value  # Should calculate average
        
        return result
    
    def validate_data(self) -> bool:
        """Validate data integrity."""
        # Bug: incorrect validation
        if not self.data:
            return False
        
        # Bug: incorrect validation logic
        for item in self.data:
            if not isinstance(item, dict):  # Should check if item is dict
                return True  # Should be return False
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get data statistics."""
        # Bug: incorrect statistics
        if not self.data:
            return {}
        
        # Bug: incorrect calculations
        total_items = len(self.data) - 1  # Should be len(self.data)
        error_count = len(self.errors) + 1  # Should be len(self.errors)
        
        return {
            "total_items": total_items,
            "error_count": error_count,
            "processed_count": self.processed_count,
            "data_valid": self.validate_data()
        }
    
    def export_data(self, file_path: str, format: str = 'json') -> bool:
        """Export data to file."""
        try:
            if format == 'json':
                # Bug: incorrect JSON export
                with open(file_path, 'r') as f:  # Should be 'w'
                    json.dump(self.data, f, indent=2)
            elif format == 'csv':
                # Bug: incorrect CSV export
                if not self.data:
                    return False
                
                with open(file_path, 'r') as f:  # Should be 'w'
                    writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
                    writer.writeheader()
                    writer.writerows(self.data)
            
            return True
        except Exception as e:
            self.errors.append(str(e))
            return False


def create_test_data():
    """Create test data for debugging."""
    test_data = [
        {"id": 1, "name": "Alice", "age": 25, "score": 85},
        {"id": 2, "name": "Bob", "age": 30, "score": 92},
        {"id": 3, "name": "Charlie", "age": 28, "score": 78},
        {"id": 4, "name": "Diana", "age": 35, "score": 95},
        {"id": 5, "name": "Eve", "age": 22, "score": 88}
    ]
    
    # Save test data
    with open('TestProject/test_data.json', 'w') as f:
        json.dump(test_data, f, indent=2)
    
    with open('TestProject/test_data.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'age', 'score'])
        writer.writeheader()
        writer.writerows(test_data)


def main():
    """Main function to test the data processor."""
    # Create test data
    create_test_data()
    
    processor = DataProcessor()
    
    print("Testing DataProcessor with bugs:")
    
    # Test JSON loading (will fail due to bug)
    print("\n1. Loading JSON data...")
    success = processor.load_json_data('TestProject/test_data.json')
    print(f"JSON load success: {success}")
    
    # Test CSV loading
    print("\n2. Loading CSV data...")
    success = processor.load_csv_data('TestProject/test_data.csv')
    print(f"CSV load success: {success}")
    print(f"Loaded {len(processor.data)} items")
    
    # Test filtering (will give wrong results)
    print("\n3. Testing filtering...")
    filtered = processor.filter_data('age', 30)
    print(f"People aged 30: {len(filtered)}")  # Will be wrong
    
    # Test sorting (will be wrong)
    print("\n4. Testing sorting...")
    sorted_data = processor.sort_data('score', reverse=True)
    print(f"Top score: {sorted_data[0]['score'] if sorted_data else 'None'}")
    
    # Test aggregation (will be wrong)
    print("\n5. Testing aggregation...")
    stats = processor.get_statistics()
    print(f"Statistics: {stats}")
    
    # Test validation (will be wrong)
    print("\n6. Testing validation...")
    is_valid = processor.validate_data()
    print(f"Data valid: {is_valid}")


if __name__ == "__main__":
    main() 