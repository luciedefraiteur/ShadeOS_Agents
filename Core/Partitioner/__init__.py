#!/usr/bin/env python3
"""
🔧 Core Partitioner - Système de partitioning et d'analyse d'imports

Composant central pour le partitioning de code et l'analyse des dépendances.
Réutilisable par tous les composants du système (EditingSession, TemporalEngine, etc.)

Auteur: Alma (via Lucie Defraiteur)
Date: 2025-08-06
"""

# Imports principaux
from .import_analyzer import ImportAnalyzer, ImportAnalysisResult, DependencyGraph
from .import_resolver import ImportResolver
from .language_registry import LanguageRegistry
from .location_tracker import LocationTracker
from .partition_schemas import PartitionSchema
from .error_logger import ErrorLogger

# Imports des partitioners AST
from .ast_partitioners.base_ast_partitioner import BaseASTPartitioner
from .ast_partitioners.python_ast_partitioner import PythonASTPartitioner
from .ast_partitioners.tree_sitter_partitioner import TreeSitterPartitioner

# Imports des stratégies de fallback
from .fallback_strategies.emergency_partitioner import EmergencyPartitioner
from .fallback_strategies.regex_partitioner import RegexPartitioner
from .fallback_strategies.textual_partitioner import TextualPartitioner

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
    
    # Traqueur de localisation
    'LocationTracker',
    
    # Schémas de partition
    'PartitionSchema',
    
    # Logger d'erreurs
    'ErrorLogger',
    
    # Partitioners AST
    'BaseASTPartitioner',
    'PythonASTPartitioner',
    'TreeSitterPartitioner',
    
    # Stratégies de fallback
    'EmergencyPartitioner',
    'RegexPartitioner',
    'TextualPartitioner',
]
