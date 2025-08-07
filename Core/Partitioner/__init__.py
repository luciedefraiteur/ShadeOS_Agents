#!/usr/bin/env python3
"""
🔧 Core Partitioner - Système de partitioning et d'analyse d'imports

Composant central pour le partitioning de code et l'analyse des dépendances.
Réutilisable par tous les composants du système (EditingSession, TemporalEngine, etc.)

Structure organisée :
- analyzers/ : Analyseurs d'imports et de dépendances
- resolvers/ : Résolveurs d'imports
- handlers/ : Gestionnaires d'erreurs et de dépendances
- schemas/ : Schémas et registres de langages
- trackers/ : Suiveurs de localisation
- ast_partitioners/ : Partitioners basés sur AST
- fallback_strategies/ : Stratégies de fallback

Auteur: Alma (via Lucie Defraiteur)
Date: 2025-08-07
"""

from typing import List

# Imports des analyseurs
from .analyzers import ImportAnalyzer, ImportAnalysisResult, DependencyGraph
from .analyzers import ImportAnalysisCache, ImportAnalysisOptimizer

# Imports des résolveurs
from .resolvers import ImportResolver

# Imports des gestionnaires
from .handlers import BrokenDependencyHandler, PartitioningErrorLogger
from .handlers import ErrorInfo, log_partitioning_error, log_partitioning_warning

# Imports des schémas
from .schemas import LanguageRegistry, global_language_registry
from .schemas import PartitionResult, PartitionBlock, PartitionLocation, PartitionMethod, BlockType
from .schemas import PartitioningError, LocationTrackingError, PartitionValidationError

# Imports des trackers
from .trackers import LocationTracker

# Imports des partitioners AST
from .ast_partitioners.base_ast_partitioner import BaseASTPartitioner
from .ast_partitioners.python_ast_partitioner import PythonASTPartitioner
from .ast_partitioners.tree_sitter_partitioner import TreeSitterPartitioner

# Imports des stratégies de fallback
from .fallback_strategies.emergency_partitioner import EmergencyPartitioner
from .fallback_strategies.regex_partitioner import RegexPartitioner
from .fallback_strategies.textual_partitioner import TextualPartitioner

# Variables globales
global_error_logger = PartitioningErrorLogger()
TREE_SITTER_AVAILABLE = False  # TODO: Vérifier la disponibilité réelle

# Fonctions utilitaires
def partition_file(file_path: str, **kwargs):
    """Fonction utilitaire pour partitionner un fichier"""
    return global_language_registry.partition_file(file_path, **kwargs)

def detect_language(file_path: str) -> str:
    """Fonction utilitaire pour détecter le langage"""
    return global_language_registry.detect_language(file_path)

def get_supported_languages() -> List[str]:
    """Fonction utilitaire pour obtenir les langages supportés"""
    return global_language_registry.get_supported_languages()

__version__ = "2.0.0"
__author__ = "Alma (via Lucie Defraiteur)"

# Exports publics
__all__ = [
    # Analyseurs d'imports
    'ImportAnalyzer',
    'ImportAnalysisResult', 
    'DependencyGraph',
    'ImportAnalysisCache',
    'ImportAnalysisOptimizer',
    
    # Résolveurs d'imports
    'ImportResolver',
    
    # Gestionnaires
    'BrokenDependencyHandler',
    'PartitioningErrorLogger',
    'ErrorInfo',
    'global_error_logger',
    'log_partitioning_error',
    'log_partitioning_warning',
    
    # Registre de langages et schémas
    'LanguageRegistry',
    'global_language_registry',
    'PartitionResult',
    'PartitionBlock',
    'PartitionLocation',
    'PartitionMethod',
    'BlockType',
    'PartitioningError',
    'LocationTrackingError',
    'PartitionValidationError',
    
    # Traqueur de localisation
    'LocationTracker',
    
    # Partitioners AST
    'BaseASTPartitioner',
    'PythonASTPartitioner',
    'TreeSitterPartitioner',
    'TREE_SITTER_AVAILABLE',
    
    # Stratégies de fallback
    'EmergencyPartitioner',
    'RegexPartitioner',
    'TextualPartitioner',
    
    # Fonctions utilitaires
    'partition_file',
    'detect_language',
    'get_supported_languages',
]
