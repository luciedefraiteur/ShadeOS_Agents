#!/usr/bin/env python3
# 🔨 Calculatrice Corrigée par Forge ⚡
# Maître Forgeron du Code - Bugs éliminés avec précision divine !

class Calculator:
    def __init__(self):
        self.history = []

    def add(self, a, b):
        # Addition avec validation des types
        try:
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                raise TypeError("Les arguments doivent être des nombres")

            result = a + b
            self.history.append(f"{a} + {b} = {result}")
            return result
        except Exception as e:
            self.history.append(f"Erreur addition: {e}")
            raise

    def subtract(self, a, b):
        # Soustraction corrigée (a - b)
        try:
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                raise TypeError("Les arguments doivent être des nombres")

            result = a - b  # CORRIGÉ: était b - a
            self.history.append(f"{a} - {b} = {result}")
            return result
        except Exception as e:
            self.history.append(f"Erreur soustraction: {e}")
            raise

    def multiply(self, a, b):
        # Multiplication corrigée (a * b)
        try:
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                raise TypeError("Les arguments doivent être des nombres")

            result = a * b  # CORRIGÉ: était a / b
            self.history.append(f"{a} * {b} = {result}")
            return result
        except Exception as e:
            self.history.append(f"Erreur multiplication: {e}")
            raise

    def divide(self, a, b):
        # Division avec gestion de la division par zéro
        try:
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                raise TypeError("Les arguments doivent être des nombres")

            if b == 0:  # CORRIGÉ: gestion division par zéro
                raise ZeroDivisionError("Division par zéro impossible")

            result = a / b
            self.history.append(f"{a} / {b} = {result}")
            return result
        except Exception as e:
            self.history.append(f"Erreur division: {e}")
            raise

    def power(self, a, b):
        # Puissance corrigée (a ** b)
        try:
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                raise TypeError("Les arguments doivent être des nombres")

            result = a ** b  # CORRIGÉ: était a + b
            self.history.append(f"{a} ^ {b} = {result}")
            return result
        except Exception as e:
            self.history.append(f"Erreur puissance: {e}")
            raise

    def get_history(self):
        # Retourne l historique des opérations
        return self.history.copy()

    def clear_history(self):
        # Efface l historique - CORRIGÉ
        self.history.clear()  # CORRIGÉ: était pass

# 🔨 Par la forge cosmique, les bugs sont CRISTALLISÉS en perfection ! ⚡
