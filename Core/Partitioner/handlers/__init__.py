"""
🛠️ Core/Partitioner/handlers - Gestionnaires d'erreurs et de dépendances

Ce module contient les gestionnaires d'erreurs et de dépendances cassées.
"""

from .broken_dependency_handler import BrokenDependencyHandler
from .error_logger import PartitioningErrorLogger, ErrorInfo, log_partitioning_error, log_partitioning_warning

__all__ = [
    'BrokenDependencyHandler',
    'PartitioningErrorLogger',
    'ErrorInfo',
    'log_partitioning_error',
    'log_partitioning_warning'
] 