"""
🔄 Stratégies de Fallback pour Partitionnement

Stratégies de secours pour partitionner les fichiers quand
l'analyse AST échoue ou n'est pas applicable.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

from .regex_partitioner import RegexPartitioner
from .textual_partitioner import TextualPartitioner
from .emergency_partitioner import EmergencyPartitioner

__all__ = [
    'RegexPartitioner',
    'TextualPartitioner',
    'EmergencyPartitioner'
]

__version__ = "1.0.0"
