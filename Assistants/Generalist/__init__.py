#!/usr/bin/env python3
"""
⛧ Generalist Assistants Package ⛧
Assistants généralistes pour le débogage et l'analyse de code

Contient :
- V8_generalist_assistant : Assistant local avec LLMs
- V8_generalist_openai : Assistant OpenAI
"""

from .V8_generalist_assistant import GeneralistAssistant
from .V8_generalist_openai import GeneralistOpenAIAssistant

__all__ = [
    'GeneralistAssistant',
    'GeneralistOpenAIAssistant'
] 