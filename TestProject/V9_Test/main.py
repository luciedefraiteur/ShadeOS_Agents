
#!/usr/bin/env python3
"""
Projet de test pour V9_AutoFeedingThreadAgent
"""

import os
import json
from typing import Dict, List, Any

class TestProject:
    """Classe principale du projet de test"""
    
    def __init__(self, name: str = "V9_Test"):
        self.name = name
        self.data = {}
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration"""
        return {
            "version": "1.0.0",
            "author": "Alma",
            "description": "Projet de test pour V9"
        }
    
    def add_data(self, key: str, value: Any):
        """Ajoute des données"""
        self.data[key] = value
    
    def get_data(self, key: str) -> Any:
        """Récupère des données"""
        return self.data.get(key)
    
    def export_data(self, file_path: str):
        """Exporte les données"""
        with open(file_path, 'w') as f:
            json.dump(self.data, f, indent=2)

if __name__ == "__main__":
    project = TestProject()
    project.add_data("test", "value")
    print("Projet de test initialisé !")
