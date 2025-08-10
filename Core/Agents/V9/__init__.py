#!/usr/bin/env python3
"""
⛧ Generalist Assistants Package ⛧
Assistants généralistes pour le débogage et l'analyse de code

Contient :
- V8_generalist_assistant : Assistant avec système de providers LLM configurable
- V8_generalist_openai : Assistant OpenAI (maintenant intégré dans V8)

Système de providers supporté :
- OpenAI : GPT-4, GPT-3.5-turbo
- Local : Ollama (qwen2.5:7b-instruct, etc.)
"""

from .V8_generalist_assistant import GeneralistAssistant
from .V8_generalist_openai import GeneralistOpenAIAssistant

__all__ = [
    'GeneralistAssistant',
    'GeneralistOpenAIAssistant'
] 