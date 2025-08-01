#!/usr/bin/env python3
"""
Calculatrice Simple - AVEC BUGS INTENTIONNELS
Les daemons doivent identifier et corriger ces problèmes.
"""

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        """Addition - BUG: ne gère pas les types"""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a, b):
        """Soustraction - BUG: ordre inversé"""
        result = b - a  # BUG INTENTIONNEL
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a, b):
        """Multiplication - BUG: division au lieu de multiplication"""
        if b == 0:
            return 0
        result = a / b  # BUG INTENTIONNEL
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a, b):
        """Division - BUG: pas de gestion division par zéro"""
        result = a / b  # BUG: division par zéro possible
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def power(self, a, b):
        """Puissance - BUG: logique incorrecte"""
        result = a + b  # BUG INTENTIONNEL (devrait être a ** b)
        self.history.append(f"{a} ^ {b} = {result}")
        return result
    
    def get_history(self):
        """Retourne l'historique"""
        return self.history
    
    def clear_history(self):
        """Efface l'historique - BUG: ne fait rien"""
        pass  # BUG INTENTIONNEL
    
    # Méthode dupliquée (mauvaise pratique)
    def add_numbers(self, x, y):
        """Autre méthode d'addition (code dupliqué)"""
        return x + y
    
    # Méthode inutile
    def useless_method(self):
        """Méthode qui ne sert à rien"""
        print("Cette méthode ne fait rien d'utile")
        for i in range(1000):
            pass
        return "inutile"


# Code mal structuré en dehors de la classe
def calculate_something(calc, operation, a, b):
    """Fonction mal placée qui devrait être dans la classe"""
    if operation == "add":
        return calc.add(a, b)
    elif operation == "sub":
        return calc.subtract(a, b)
    elif operation == "mul":
        return calc.multiply(a, b)
    elif operation == "div":
        return calc.divide(a, b)
    else:
        return None


# Test rapide (devrait être dans un fichier de test séparé)
if __name__ == "__main__":
    calc = Calculator()
    print("Test rapide:")
    print(f"2 + 3 = {calc.add(2, 3)}")  # Devrait être 5
    print(f"5 - 2 = {calc.subtract(5, 2)}")  # Devrait être 3, mais sera -3
    print(f"4 * 3 = {calc.multiply(4, 3)}")  # Devrait être 12, mais sera 1.33...
    print(f"10 / 2 = {calc.divide(10, 2)}")  # Devrait être 5
    print(f"2 ^ 3 = {calc.power(2, 3)}")  # Devrait être 8, mais sera 5
    
    print("\nHistorique:")
    for entry in calc.get_history():
        print(entry)
