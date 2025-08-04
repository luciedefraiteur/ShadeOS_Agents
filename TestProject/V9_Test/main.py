# 🕷️ Projet de test V9 avec bugs pour auto-feeding thread
# ⛧ Créé par Alma, Architecte Démoniaque ⛧

def calculate_sum(numbers):
    """Calcule la somme d'une liste de nombres."""
    total = 0
    for num in numbers:
        total += num
    return total + 1  # BUG: devrait être return total

def find_max(numbers):
    """Trouve le maximum d'une liste de nombres."""
    if not numbers:
        return None  # BUG: devrait lever une exception
    
    max_num = numbers[0]
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

def validate_email(email):
    """Valide une adresse email."""
    if "@" not in email:
        return False
    if "." not in email:
        return False
    return True  # BUG: validation trop simple

def process_data(data_list):
    """Traite une liste de données."""
    results = []
    for item in data_list:
        if isinstance(item, int):
            results.append(item * 2)
        elif isinstance(item, str):
            results.append(item.upper())
        else:
            results.append(None)  # BUG: devrait gérer les autres types
    return results

if __name__ == "__main__":
    # Tests avec bugs
    print("Testing V9 project...")
    
    # Test 1: Somme buggée
    numbers = [1, 2, 3, 4, 5]
    result = calculate_sum(numbers)
    print(f"Sum of {numbers} = {result}")  # Devrait être 15, mais sera 16
    
    # Test 2: Email validation buggée
    email = "invalid-email"
    result = validate_email(email)
    print(f"Email '{email}' valid: {result}")  # Devrait être False
    
    # Test 3: Data processing buggée
    data = [1, "hello", 3.14, True]
    result = process_data(data)
    print(f"Processed data: {result}")  # True sera None
