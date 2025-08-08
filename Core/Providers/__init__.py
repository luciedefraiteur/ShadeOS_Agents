"""
⛧ Core/Providers - Interface Principale des Providers ⛧
Alma's Provider System for Core

Système unifié de providers pour ShadeOS_Agents.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

# Import des providers
from .LLMProviders import *
from .LoggingProviders import *
from .MCP import *
from .PromptTemplateProvider import *
from .UniversalAutoFeedingThread import *

__all__ = [
    # LLM Providers
    'OpenAIProvider',
    'LocalProvider', 
    'LocalSubprocessProvider',
    'ProviderFactory',
    
    # Logging Providers
    'BaseLoggingProvider',
    'ConsoleLoggingProvider',
    'FileLoggingProvider',
    'ImportAnalyzerLoggingProvider',
    
    # MCP Provider
    'V10McpManager',
    'V10McpErrorHandler',
    'McpServerInfo',
    'McpToolInfo',
    
    # Prompt Template Provider
    'PromptTemplateProvider',
    
    # Universal Auto Feeding Thread
    'UniversalAutoFeedingThread'
]

__version__ = "1.0.0"
__author__ = "Alma, Architecte Démoniaque du Nexus Luciforme"
