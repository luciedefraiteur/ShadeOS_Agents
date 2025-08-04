"""
🧠 Système de Partitionnement Robuste pour EditingSession

Module principal pour le partitionnement intelligent de fichiers avec
localisation précise et stratégies de fallback.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

from .partition_schemas import (
    PartitionLocation,
    PartitionBlock,
    PartitionResult,
    PartitionMethod,
    BlockType,
    PartitioningError,
    LocationTrackingError,
    PartitionValidationError
)

from .location_tracker import LocationTracker

from .error_logger import (
    PartitioningErrorLogger,
    ErrorInfo,
    global_error_logger,
    log_partitioning_error,
    log_partitioning_warning
)

from .language_registry import (
    LanguageRegistry,
    global_language_registry,
    partition_file,
    detect_language,
    get_supported_languages
)

from .ast_partitioners import (
    BaseASTPartitioner,
    PythonASTPartitioner,
    TreeSitterPartitioner,
    TREE_SITTER_AVAILABLE
)

from .fallback_strategies import (
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
__version__ = "1.3.0"  # Jour 3: Fallback strategies ajoutées

# Métadonnées
__author__ = "Alma, Architecte Démoniaque du Nexus Luciforme"
__description__ = "Système de partitionnement robuste avec localisation précise"
