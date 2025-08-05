"""
⛧ Core Config Module ⛧
Alma's Configuration Management System

Module de configuration centralisé pour ShadeOS_Agents.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

from .secure_env_manager import (
    SecureEnvManager,
    get_secure_env_manager,
    load_project_environment
)

__all__ = [
    'SecureEnvManager',
    'get_secure_env_manager',
    'load_project_environment'
]

__version__ = "1.0.0"
__author__ = "Alma, Architecte Démoniaque du Nexus Luciforme" 