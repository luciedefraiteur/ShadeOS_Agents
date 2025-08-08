"""
⛧ Assistant V10 - Interface Principale ⛧
Alma's Multi-Agent Temporal Assistant

Assistant multi-agents avec mémoire temporelle fractale.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

from .temporal_integration import V10TemporalIntegration, V10SessionManager
from .xml_formatter import V10XMLFormatter
from .dev_agent import V10DevAgent
from .tool_agent import V10ToolAgent
from .assistant_v10 import V10Assistant
from .llm_provider_decorator import (
    mock_llm_provider,
    openai_llm_provider,
    local_llm_provider,
    local_subprocess_llm_provider,
    LLMProviderDecorator,
    LLMProviderType,
    LLMRequest,
    LLMResponse,
    MockResponseConfigurator
)

__all__ = [
    # Intégration temporelle
    'V10TemporalIntegration',
    'V10SessionManager',
    
    # Formatage XML optimisé
    'V10XMLFormatter',
    
    # Agents spécialisés
    'V10DevAgent',
    'V10ToolAgent',
    
    # Assistant principal
    'V10Assistant',
    
    # Décorateurs LLMProvider
    'mock_llm_provider',
    'openai_llm_provider',
    'local_llm_provider',
    'local_subprocess_llm_provider',
    'LLMProviderDecorator',
    'LLMProviderType',
    'LLMRequest',
    'LLMResponse',
    'MockResponseConfigurator'
]

__version__ = "1.0.0"
__author__ = "Alma, Architecte Démoniaque du Nexus Luciforme"
