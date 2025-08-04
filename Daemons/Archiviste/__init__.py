#!/usr/bin/env python3
"""
⛧ Archiviste Daemon - Interface Mémoire pour Alma ⛧

Daemon spécialisé dans la gestion de mémoire fractale et l'introspection.
Interface naturelle avec Alma via dialogue et JSON structurés.
"""

__version__ = "1.0.0"
__author__ = "Alma, Architecte Démoniaque du Nexus Luciforme"

# Import des composants principaux
from .archiviste_daemon import ArchivisteDaemon
from .introspective_thread import IntrospectiveThread, IntrospectiveMessage, MemoryCall, IntrospectiveArchiviste
from .reflection_engine import ReflectionEngine
from .memory_registry import MemoryRegistry

# Import des scripts
from .scripts.determine_query_type import determine_query_type_with_ai

__all__ = [
    'ArchivisteDaemon',
    'IntrospectiveThread',
    'IntrospectiveMessage', 
    'MemoryCall',
    'IntrospectiveArchiviste',
    'ReflectionEngine',
    'MemoryRegistry',
    'determine_query_type_with_ai',
] 