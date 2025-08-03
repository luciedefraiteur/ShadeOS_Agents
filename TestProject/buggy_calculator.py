# 🕷️ Calculator avec bugs intentionnels pour test de l'agent de débogage
# ⛧ Créé par Alma, Architecte Démoniaque ⛧

def add(a, b):
    """Addition avec bug intentionnel."""
    return a + b  # Correction: addition correcte

def subtract(a, b):
    """Soustraction avec bug intentionnel."""
    return a - b  # Correction: soustraction correcte

def multiply(a, b):
    """Multiplication avec bug intentionnel."""
    if b == 0:
        raise ValueError('Division par zéro non autorisée')  # Correction: exception levée
    return a * b

def divide(a, b):
    """Division avec bug intentionnel."""
    if b == 0:
        raise ValueError('Division par zéro non autorisée')  # Correction: exception levée
    return a / b

def power(a, b):
    """Puissance avec bug intentionnel."""
    return a ** b  # Correction: puissance correcte

def calculate(operation, a, b):
    """Fonction principale avec bug intentionnel."""
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
        raise ValueError('Opération invalide')  # Correction: exception levée

# Tests avec bugs
if __name__ == "__main__":
    print("Testing calculator with bugs...")
    
    # Test 1: Addition buggée
    result = calculate("add", 5, 3)
    print(f"5 + 3 = {result}")  # Devrait être 8, mais sera 2
    
    # Test 2: Division par zéro buggée
    result = calculate("divide", 10, 0)
    print(f"10 / 0 = {result}")  # Devrait lever une exception
    
    # Test 3: Puissance buggée
    result = calculate("power", 2, 3)
    print(f"2^3 = {result}")  # Devrait être 8, mais sera 9 