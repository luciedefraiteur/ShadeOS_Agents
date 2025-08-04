#!/usr/bin/env python3
"""
⛧ Arsenal d'Outils pour Assistants ⛧
Collection complète d'outils d'analyse et de manipulation pour les assistants IA

Contient :
- Outils de lecture et manipulation de fichiers
- Outils d'analyse de code et de structure
- Outils de recherche et remplacement
- Outils de génération de templates
- Outils d'intégration OpenAI
- Outils de gestion de registre et d'invocation
"""

# Outils de lecture et manipulation
from .safe_read_file_content import safe_read_file_content
from .safe_append_to_file import safe_append_to_file
from .safe_overwrite_file import safe_overwrite_file
from .safe_create_file import safe_create_file
from .safe_create_directory import safe_create_directory
from .safe_delete_directory import safe_delete_directory
from .safe_delete_lines import safe_delete_lines
from .safe_insert_text_at_line import safe_insert_text_at_line
from .safe_replace_lines_in_file import safe_replace_lines_in_file
from .safe_replace_text_in_file import safe_replace_text_in_file

# Outils d'analyse et de recherche
from .code_analyzer import code_analyzer
from .file_diff import file_diff
from .file_stats import analyze_file_stats
from .find_text_in_project import find_text_in_project
from .regex_search_file import regex_search_file
from .scry_for_text import scry_for_text
from .walk_directory import walk_directory
from .list_directory_contents import list_directory_contents
from .locate_text_sigils import locate_text_sigils

# Outils de génération et templates
from .template_generator import generate_from_template
from .write_code_file import write_code_file
from .backup_creator import create_file_backup

# Outils de renommage et restructuration
from .rename_project_entity import rename_project_entity
from .replace_text_in_project import replace_text_in_project
from .md_hierarchy_basic import BasicMDOrganizer

# Outils d'intégration OpenAI (obsolètes - remplacés par V7/V8)
# from .openai_assistants import OpenAIAssistantsIntegration
# from .openai_initializer import OpenAIInitializer
# from .openai_integration import OpenAIIntegration

# Outils de gestion de registre et d'invocation
from .tool_registry import ToolRegistry
from .tool_invoker import ToolInvoker
from .tool_search import ToolSearchEngine

# Utilitaires
from .reading_tools import read_file_content
from .read_file_content_naked import read_file_content_naked
from ._string_utils import _perform_string_replacement

__all__ = [
    # Outils de lecture et manipulation
    'safe_read_file_content',
    'safe_append_to_file',
    'safe_overwrite_file',
    'safe_create_file',
    'safe_create_directory',
    'safe_delete_directory',
    'safe_delete_lines',
    'safe_insert_text_at_line',
    'safe_replace_lines_in_file',
    'safe_replace_text_in_file',
    
    # Outils d'analyse et de recherche
    'code_analyzer',
    'file_diff',
    'analyze_file_stats',
    'find_text_in_project',
    'regex_search_file',
    'scry_for_text',
    'walk_directory',
    'list_directory_contents',
    'locate_text_sigils',
    
    # Outils de génération et templates
    'generate_from_template',
    'write_code_file',
    'create_file_backup',
    
    # Outils de renommage et restructuration
    'rename_project_entity',
    'replace_text_in_project',
    'BasicMDOrganizer',
    
    # Outils d'intégration OpenAI (obsolètes - remplacés par V7/V8)
    # 'OpenAIAssistantsIntegration',
    # 'OpenAIInitializer',
    # 'OpenAIIntegration',
    
    # Outils de gestion de registre et d'invocation
    'ToolRegistry',
    'ToolInvoker',
    'ToolSearchEngine',
    
    # Utilitaires
    'read_file_content',
    'read_file_content_naked',
    '_perform_string_replacement',
]
