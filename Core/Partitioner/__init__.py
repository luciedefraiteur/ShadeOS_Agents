#!/usr/bin/env python3
"""
🔧 Core Partitioner - Système de partitioning et d'analyse d'imports

Composant central pour le partitioning de code et l'analyse des dépendances.
Réutilisable par tous les composants du système (EditingSession, TemporalEngine, etc.)

Auteur: Alma (via Lucie Defraiteur)
Date: 2025-08-06
"""

from typing import List

# Imports principaux
from .import_analyzer import ImportAnalyzer, ImportAnalysisResult, DependencyGraph
from .import_resolver import ImportResolver
from .language_registry import LanguageRegistry, global_language_registry
from .location_tracker import LocationTracker
from .partition_schemas import PartitionResult, PartitionBlock, PartitionLocation, PartitionMethod, BlockType, PartitioningError, LocationTrackingError, PartitionValidationError
from .error_logger import PartitioningErrorLogger, ErrorInfo, log_partitioning_error, log_partitioning_warning

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

__version__ = "1.0.0"
__author__ = "Alma (via Lucie Defraiteur)"

# Exports publics
__all__ = [
    # Analyseur d'imports
    'ImportAnalyzer',
    'ImportAnalysisResult', 
    'DependencyGraph',
    
    # Résolveur d'imports
    'ImportResolver',
    
    # Registre de langages
    'LanguageRegistry',
    'global_language_registry',
    
    # Traqueur de localisation
    'LocationTracker',
    
    # Schémas de partition
    'PartitionResult',
    'PartitionBlock',
    'PartitionLocation',
    'PartitionMethod',
    'BlockType',
    'PartitioningError',
    'LocationTrackingError',
    'PartitionValidationError',
    
    # Logger d'erreurs
    'ErrorLogger',
    'PartitioningErrorLogger',
    'ErrorInfo',
    'global_error_logger',
    'log_partitioning_error',
    'log_partitioning_warning',
    
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
