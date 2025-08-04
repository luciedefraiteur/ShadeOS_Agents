#!/usr/bin/env python3
"""
⛧ MemoryEngine - Système de Mémoire Fractale ⛧

Système de mémoire fractale avec Archiviste Daemon, providers LLM globaux,
et architecture modulaire pour agents conscients.
"""

__version__ = "2.0.0"
__author__ = "Alma, Architecte Démoniaque du Nexus Luciforme"

# Import des composants principaux
from .core.engine import MemoryEngine
from .core.archiviste_daemon import ArchivisteDaemon
from .core.archiviste import IntrospectiveArchiviste

# Import des providers LLM globaux
from .core.llm_providers import (
    LLMProvider, ProviderFactory, ProviderType, ErrorType,
    OpenAIProvider, LocalProvider
)

# Import des extensions
from .extensions import tool_memory_extension, tool_search_extension

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
    'ArchivisteDaemon',
    'IntrospectiveArchiviste',
    
    # LLM Providers Globaux
    'LLMProvider',
    'ProviderFactory',
    'ProviderType',
    'ErrorType',
    'OpenAIProvider',
    'LocalProvider',
    
    # Extensions
    'tool_memory_extension',
    'tool_search_extension',
] 