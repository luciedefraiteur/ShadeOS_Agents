#!/usr/bin/env python3
"""
⛧ Assistants Package ⛧
Package principal pour tous les assistants IA du système

Contient :
- EditingSession : Intégration OpenAI et outils d'édition
- Generalist : Assistants généralistes (V8)
- Specialist : Assistants spécialistes (V7)
"""

from .EditingSession.Tools import ToolRegistry
from .Generalist.V8_generalist_assistant import GeneralistAssistant
from .Specialist.V7_safe import LocalLLMAssistantV7Phase2Enhanced

__all__ = [
    'ToolRegistry',
    'GeneralistAssistant', 
    'LocalLLMAssistantV7Phase2Enhanced'
] 