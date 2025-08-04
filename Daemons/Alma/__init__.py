#!/usr/bin/env python3
"""
⛧ Alma Daemon - Architecte Démoniaque du Nexus Luciforme ⛧

Daemon principal et architecte du système, spécialisé dans le développement
et la coordination des autres daemons. Interface avec l'utilisateur et
gestion des tâches complexes.
"""

__version__ = "1.0.0"
__author__ = "Alma, Architecte Démoniaque du Nexus Luciforme"

# Import du daemon Alma
from .alma_daemon import AlmaDaemon

__all__ = [
    'AlmaDaemon',
]
