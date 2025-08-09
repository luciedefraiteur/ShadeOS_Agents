#!/usr/bin/env python3
"""
⛧ LLM Providers - Système Global de Providers LLM ⛧

Système de providers LLM abstrait et réutilisable pour tous les composants :
- Archiviste Daemon
- Assistants V7/V8
- Meta Orchestrator
- Daemon Architectural Alma
- Tous les daemons en gestation

Provider abstrait avec validation, gestion d'erreurs, estimation de taille
et configuration flexible pour tous les appels LLM du projet.
"""

__version__ = "1.0.0"
__author__ = "Alma, Architecte Démoniaque du Nexus Luciforme"

# Import des providers
from .llm_provider import LLMProvider, ProviderStatus, LLMResponse, ValidationResult, ProviderType, ErrorType
from .provider_factory import ProviderFactory
from .openai_provider import OpenAIProvider
from .local_provider import LocalProvider
try:
    from .providers_optional.gemini_provider import GeminiProvider
except Exception:
    GeminiProvider = None

__all__ = [
    'LLMProvider',
    'ProviderStatus', 
    'LLMResponse',
    'ValidationResult',
    'ProviderType',
    'ErrorType',
    'ProviderFactory',
    'OpenAIProvider',
    'LocalProvider',
    'GeminiProvider',
] 