#!/usr/bin/env python3
"""
🤖 AI Engines - IAIntrospectionDaemon ⛧

Moteurs IA pour l'introspection intelligente.
Supporte Ollama et OpenAI avec gestion d'erreurs et fallbacks.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

from .ai_engine_factory import AIEngineFactory
from .ollama_engine import OllamaEngine
from .openai_engine import OpenAIEngine

__all__ = ['AIEngineFactory', 'OllamaEngine', 'OpenAIEngine'] 