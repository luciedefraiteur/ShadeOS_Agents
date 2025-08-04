# Test line
"""
⛧ Calculator with Bugs ⛧
Test project for AI agent debugging

This file contains intentional bugs for testing the AI agent's ability to fix them.
"""

import math
import sys

class Calculator:
    """A calculator class with intentional bugs."""
    
    def __init__(self):
        self.history = []
        self.debug_mode = True  # Bug: should be False by default
    
    def add(self, a, b):
        """Add two numbers."""
        # Bug: incorrect addition
        result = a + b  # Should be a + b
        self.history.append(f"add({a}, {b}) = {result}")
        return result
    
    def subtract(self, a, b):
        """Subtract b from a."""
        # Bug: incorrect subtraction
        result = a - b  # Should be a - b
        self.history.append(f"subtract({a}, {b}) = {result}")
        return result
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        # Bug: division instead of multiplication
        if b == 0:
            return 0  # Bug: should raise ZeroDivisionError
        result = a * b  # Should be a * b
        self.history.append(f"multiply({a}, {b}) = {result}")
        return result
    
    def divide(self, a, b):
        """Divide a by b."""
        # Bug: multiplication instead of division
        if b == 0:
            raise ValueError("Cannot divide by zero")  # Bug: should be ZeroDivisionError
        result = a / b  # Should be a / b
        self.history.append(f"divide({a}, {b}) = {result}")
        return result
    
    def power(self, base, exponent):
        """Calculate base raised to the power of exponent."""
        # Bug: incorrect power calculation
        result = base ** exponent  # Should be base ** exponent
        self.history.append(f"power({base}, {exponent}) = {result}")
        return result
    
    def sqrt(self, number):
        """Calculate square root."""
        # Bug: incorrect square root
        if number < 0:
            return 0  # Bug: should raise ValueError
        result = math.sqrt(number)  # Should be math.sqrt(number)
        self.history.append(f"sqrt({number}) = {result}")
        return result
    
    def get_history(self):
        """Get calculation history."""
        # Bug: returns empty list instead of history
        return []  # Should be return self.history
    
    def clear_history(self):
        """Clear calculation history."""
        # Bug: doesn't clear history
        pass  # Should be self.history.clear()
    
    def get_last_result(self):
        """Get the last calculation result."""
        # Bug: always returns 0
        return 0  # Should return last result from history


def main():
    """Main function with bugs."""
    calc = Calculator()
    
    # Test calculations (all will be wrong due to bugs)
    print("Testing calculator with bugs:")
    
    # Bug: these will all give wrong results
    result1 = calc.add(5, 3)  # Should be 8, will be 2
    print(f"5 + 3 = {result1}")
    
    result2 = calc.subtract(10, 4)  # Should be 6, will be 14
    print(f"10 - 4 = {result2}")
    
    result3 = calc.multiply(6, 7)  # Should be 42, will be 0.857...
    print(f"6 * 7 = {result3}")
    
    result4 = calc.divide(20, 5)  # Should be 4, will be 100
    print(f"20 / 5 = {result4}")
    
    result5 = calc.power(2, 3)  # Should be 8, will be 6
    print(f"2^3 = {result5}")
    
    result6 = calc.sqrt(16)  # Should be 4, will be 8
    print(f"√16 = {result6}")
    
    # Bug: history will be empty
    print(f"History: {calc.get_history()}")
    
    # Bug: last result will always be 0
    print(f"Last result: {calc.get_last_result()}")


if __name__ == "__main__":
    main() 