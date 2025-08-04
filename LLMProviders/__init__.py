#!/usr/bin/env python3
"""
⛧ LLMProviders - Système Global de Providers LLM ⛧

Système de providers LLM abstrait et réutilisable pour tous les composants du projet :
- MemoryEngine et Archiviste Daemon
- Assistants V7/V8 (Generalist/Specialist)
- ConsciousnessEngine et ses strates
- Meta Orchestrator
- Daemon Architectural Alma
- Tous les daemons en gestation

Provider abstrait avec validation, gestion d'erreurs, estimation de taille
et configuration flexible pour tous les appels LLM du projet.
"""

__version__ = "1.0.0"
__author__ = "Alma, Architecte Démoniaque du Nexus Luciforme"

# Import depuis Core (nouvelle architecture)
from Core.LLMProviders import (
    LLMProvider, ProviderStatus, LLMResponse, ValidationResult,
    ProviderType, ErrorType, ProviderFactory,
    OpenAIProvider, LocalProvider
)

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
] 