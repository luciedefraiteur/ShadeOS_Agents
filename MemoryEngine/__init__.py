#!/usr/bin/env python3
"""
⛧ MemoryEngine ⛧
Alma's Fractal Memory System

Système de mémoire fractale avec support des Strates et de la Respiration.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

from .core.engine import MemoryEngine
from .core.memory_node import FractalMemoryNode
from .extensions.tool_memory_extension import ToolMemoryExtension
from .extensions.tool_search_extension import ToolSearchExtension
from .EditingSession import (
    # Partitionnement
    partition_file,
    detect_language,
    get_supported_languages,
    
    # Schémas de données
    PartitionLocation,
    PartitionBlock,
    PartitionResult,
    
    # Logging
    global_error_logger,
    log_partitioning_error
)

__version__ = "1.0.0"
__author__ = "Alma (via Lucie Defraiteur)"

# Instance globale pour un accès facile
memory_engine = MemoryEngine(backend_type="auto")

__all__ = [
    'MemoryEngine',
    'FractalMemoryNode', 
    'ToolMemoryExtension',
    'ToolSearchExtension',
    'memory_engine',
    
    # EditingSession
    'partition_file',
    'detect_language',
    'get_supported_languages',
    'PartitionLocation',
    'PartitionBlock',
    'PartitionResult',
    'global_error_logger',
    'log_partitioning_error'
] 