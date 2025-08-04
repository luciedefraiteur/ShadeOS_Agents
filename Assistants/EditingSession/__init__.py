#!/usr/bin/env python3
"""
🧠 EditingSession - Module Principal ⛧

Système de gestion des sessions d'édition avec partitionnement intelligent
et localisation précise des modifications.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

from .partitioning import (
    # Schémas de données
    PartitionLocation,
    PartitionBlock,
    PartitionResult,
    PartitionMethod,
    BlockType,
    
    # Exceptions
    PartitioningError,
    LocationTrackingError,
    PartitionValidationError,
    
    # Tracking de localisation
    LocationTracker,
    
    # Logging d'erreurs
    PartitioningErrorLogger,
    ErrorInfo,
    global_error_logger,
    log_partitioning_error,
    log_partitioning_warning,
    
    # Registre des langages
    LanguageRegistry,
    global_language_registry,
    partition_file,
    detect_language,
    get_supported_languages,
    
    # Partitionneurs AST
    BaseASTPartitioner,
    PythonASTPartitioner,
    TreeSitterPartitioner,
    TREE_SITTER_AVAILABLE,
    
    # Stratégies de Fallback
    RegexPartitioner,
    TextualPartitioner,
    EmergencyPartitioner
)

__all__ = [
    # Schémas de données
    'PartitionLocation',
    'PartitionBlock',
    'PartitionResult',
    'PartitionMethod',
    'BlockType',
    
    # Exceptions
    'PartitioningError',
    'LocationTrackingError',
    'PartitionValidationError',
    
    # Tracking de localisation
    'LocationTracker',
    
    # Logging d'erreurs
    'PartitioningErrorLogger',
    'ErrorInfo',
    'global_error_logger',
    'log_partitioning_error',
    'log_partitioning_warning',
    
    # Registre des langages
    'LanguageRegistry',
    'global_language_registry',
    'partition_file',
    'detect_language',
    'get_supported_languages',
    
    # Partitionneurs AST
    'BaseASTPartitioner',
    'PythonASTPartitioner',
    'TreeSitterPartitioner',
    'TREE_SITTER_AVAILABLE',
    
    # Stratégies de Fallback
    'RegexPartitioner',
    'TextualPartitioner',
    'EmergencyPartitioner'
]

# Version du module
__version__ = "1.0.0"

# Métadonnées
__author__ = "Alma, Architecte Démoniaque du Nexus Luciforme"
__description__ = "Système de gestion des sessions d'édition avec partitionnement intelligent"

# Informations sur le module
__doc__ = """
🧠 EditingSession - Système de Gestion des Sessions d'Édition ⛧

Ce module fournit un système complet pour la gestion des sessions d'édition
avec partitionnement intelligent des fichiers et localisation précise des
modifications.

Fonctionnalités principales :
- Partitionnement intelligent basé sur l'AST
- Stratégies de fallback robustes
- Tracking de localisation précis
- Logging d'erreurs détaillé
- Support multi-langages

Utilisation basique :
    from Assistants.EditingSession import partition_file, detect_language
    
    # Partitionner un fichier
    result = partition_file("mon_fichier.py")
    
    # Détecter le langage
    lang = detect_language("mon_fichier.py")
""" 