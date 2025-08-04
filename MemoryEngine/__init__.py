#!/usr/bin/env python3
"""
⛧ MemoryEngine - Système de Mémoire Fractale ⛧

Système de mémoire fractale avec architecture modulaire et professionnelle.
Spécialisé dans la gestion de mémoire temporelle, fractale et contextuelle.
"""

__version__ = "2.0.0"
__author__ = "Alma, Architecte Démoniaque du Nexus Luciforme"

# Import des composants principaux du MemoryEngine
from .core.engine import MemoryEngine
from .core.memory_node import FractalMemoryNode
from .core.temporal_index import TemporalIndex
from .core.user_request_temporal_memory import UserRequestTemporalMemory
from .core.discussion_timeline import DiscussionTimeline
from .core.logging_architecture import ShadeOSLogger

# Import des backends
from .backends import neo4j_backend, storage_backends

# Import des extensions
from .extensions import tool_memory_extension, tool_search_extension

# Import des daemons (maintenant dans Daemons/)
try:
    from Daemons import ArchivisteDaemon, AlmaDaemon, MetaDaemonOrchestrator
except ImportError:
    # Fallback si les daemons ne sont pas disponibles
    pass

# Import des composants Core (maintenant dans Core/)
try:
    from Core import (
        LLMProvider, ProviderFactory, ProviderType, ErrorType,
        OpenAIProvider, LocalProvider
    )
except ImportError:
    # Fallback si les composants Core ne sont pas disponibles
    pass

# Import des outils d'édition (maintenant dans Assistants/)
try:
    from Assistants.EditingSession.Tools import (
        safe_read_file_content, safe_write_file_content,
        safe_replace_text_in_file, safe_create_file,
        safe_delete_file, safe_create_directory,
        safe_delete_directory, safe_append_to_file,
        safe_overwrite_file, safe_insert_text_at_line,
        safe_delete_lines, safe_replace_lines_in_file,
        analyze_file_stats, create_file_backup,
        find_text_in_project, replace_text_in_project,
        regex_search_file, walk_directory,
        list_directory_contents, read_file_content,
        file_diff, scry_for_text, locate_text_sigils,
        BasicMDOrganizer, generate_from_template,
        _perform_string_replacement
    )
except ImportError:
    # Fallback si les outils ne sont pas disponibles
    pass

__all__ = [
    # Core MemoryEngine
    'MemoryEngine',
    'FractalMemoryNode',
    'TemporalIndex',
    'UserRequestTemporalMemory',
    'DiscussionTimeline',
    'ShadeOSLogger',
    
    # Backends
    'neo4j_backend',
    'storage_backends',
    
    # Extensions
    'tool_memory_extension',
    'tool_search_extension',
    
    # Daemons (si disponibles)
    'ArchivisteDaemon',
    'AlmaDaemon', 
    'MetaDaemonOrchestrator',
    
    # Core Components (si disponibles)
    'LLMProvider',
    'ProviderFactory',
    'ProviderType',
    'ErrorType',
    'OpenAIProvider',
    'LocalProvider',
] 