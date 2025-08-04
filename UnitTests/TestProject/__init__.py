#!/usr/bin/env python3
"""
⛧ TestProject Package ⛧
Projet de test avec bugs intentionnels pour valider les capacités de débogage

Contient des fichiers avec des bugs intentionnels pour tester la capacité
de l'agent IA à les identifier et les corriger.
"""

__version__ = "1.0.0"
__author__ = "Alma, Architecte Démoniaque du Nexus Luciforme"

# Import des modules de test
from .calculator import Calculator
from .data_processor import DataProcessor

__all__ = [
    'Calculator',
    'DataProcessor',
] 