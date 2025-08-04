# 🕷️ Calculateur corrompu pour test de correction automatique
# ⛧ Créé par Alma, Architecte Démoniaque ⛧

def add(a, b):
    """Addition avec bug évident."""
    return a - b  # BUG: devrait être a + b

def subtract(a, b):
    """Soustraction avec bug évident."""
    return a + b  # BUG: devrait être a - b

def multiply(a, b):
    """Multiplication avec bug évident."""
    if b == 0:
        return None  # BUG: devrait lever une exception
    return a * b

def divide(a, b):
    """Division avec bug évident."""
    if b == 0:
        return 0  # BUG: devrait lever une exception
    return a / b

def power(a, b):
    """Puissance avec bug évident."""
    return a ** b + 1  # BUG: devrait être a ** b

def calculate(operation, a, b):
    """Fonction principale avec bug évident."""
    if operation == "add":
        return add(a, b)
    elif operation == "subtract":
        return subtract(a, b)
    elif operation == "multiply":
        return multiply(a, b)
    elif operation == "divide":
        return divide(a, b)
    elif operation == "power":
        return power(a, b)
    else:
        return "Invalid operation"  # BUG: devrait lever une exception

# Tests avec bugs
if __name__ == "__main__":
    print("Testing corrupted calculator...")
    
    # Test 1: Addition buggée
    result = calculate("add", 5, 3)
    print(f"5 + 3 = {result}")  # Devrait être 8, mais sera 2
    
    # Test 2: Division par zéro buggée
    result = calculate("divide", 10, 0)
    print(f"10 / 0 = {result}")  # Devrait lever une exception
    
    # Test 3: Puissance buggée
    result = calculate("power", 2, 3)
    print(f"2^3 = {result}")  # Devrait être 8, mais sera 9
