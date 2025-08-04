#!/usr/bin/env python3
"""
⛧ Core - Composants Globaux Réutilisables ⛧

Module central contenant tous les composants globaux réutilisables :
- LLM Providers (OpenAI, Ollama)
- Parsers (Luciform, métadonnées)
- ProcessManager (gestion de processus)
- Utils (utilitaires globaux)
"""

__version__ = "1.0.0"
__author__ = "Alma, Architecte Démoniaque du Nexus Luciforme"

# Import des LLM Providers
from .LLMProviders import (
    LLMProvider, ProviderFactory, ProviderType, ErrorType,
    OpenAIProvider, LocalProvider, ProviderStatus, LLMResponse, ValidationResult
)

# Import des Parsers
from .Parsers import (
    luciform_parser, luciform_tool_metadata_parser
)

# Import du ProcessManager
from .ProcessManager import (
    execute_command, process_killer, process_reader, process_writer
)

# Import des Utils
from .Utils import string_utils

__all__ = [
    # LLM Providers
    'LLMProvider',
    'ProviderFactory', 
    'ProviderType',
    'ErrorType',
    'OpenAIProvider',
    'LocalProvider',
    'ProviderStatus',
    'LLMResponse',
    'ValidationResult',
    
    # Parsers
    'luciform_parser',
    'luciform_tool_metadata_parser',
    
    # ProcessManager
    'execute_command',
    'process_killer',
    'process_reader', 
    'process_writer',
    
    # Utils
    'string_utils',
]
