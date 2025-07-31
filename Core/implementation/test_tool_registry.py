import sys
import os
import pprint
import unittest

# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Core.implementation.tool_registry import ALL_TOOLS, initialize_tool_registry

class TestToolRegistry(unittest.TestCase):

    def test_registry_loading(self):
        """Vérifie que le registre se charge et n'est pas vide."""
        self.assertTrue(len(ALL_TOOLS) > 0, "Le registre d'outils ne devrait pas être vide.")

    def test_specific_tool_documentation(self):
        """Vérifie que la documentation d'un outil spécifique est correctement chargée."""
        tool_id = "read_file_content"
        self.assertIn(tool_id, ALL_TOOLS, f"L'outil '{tool_id}' devrait être dans le registre.")
        
        lucidoc = ALL_TOOLS[tool_id].get("lucidoc")
        self.assertIsNotNone(lucidoc, f"La documentation pour '{tool_id}' ne devrait pas être nulle.")
        
        # Vérifie la présence des sections clés
        self.assertIn("pacte", lucidoc)
        self.assertIn("invocation", lucidoc)
        self.assertIn("essence", lucidoc)

        # Vérifie une valeur spécifique
        self.assertEqual(lucidoc["pacte"].get("type"), "reading", "Le type du pacte est incorrect.")

if __name__ == "__main__":
    initialize_tool_registry() # Initialise le registre avant d'exécuter les tests
    print("--- Test du Registre d'Outils ---")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    print("\n--- Contenu du Registre Complet ---")
    pprint.pprint(ALL_TOOLS)
    print(f"\nTotal d'outils enregistrés : {len(ALL_TOOLS)}")
