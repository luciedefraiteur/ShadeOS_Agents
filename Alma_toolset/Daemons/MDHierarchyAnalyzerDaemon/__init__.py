#!/usr/bin/env python3
"""
⛧ MD Hierarchy Analyzer Daemon ⛧

Daemon intelligent d'analyse hiérarchique de documents Markdown
avec orchestration IA, prompts Luciformes et injections dynamiques.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

__version__ = "1.0.0"
__author__ = "Alma, Architecte Démoniaque du Nexus Luciforme"
__description__ = "Intelligent MD Hierarchy Analyzer with AI Orchestration"

# Imports principaux
from .core.openai_analyzer import OpenAIAnalyzer, AIInsights
from .core.content_type_detector import ContentTypeDetector, ContentType, ContentCharacteristics
from .core.contextual_md_analyzer import ContextualMDAnalyzer, ContextualAnalysis
from .core.md_daemon_core import MDDaemonCore, DaemonConfig

from .adapters.message_bus import MessageBus, MessageHandler, ProtocolError
from .adapters.protocol_adapters import (
    ContentDetectorAdapter, 
    AIAnalyzerAdapter, 
    MemoryEngineAdapter
)

from .prompts.dynamic_injection_system import (
    DynamicInjectionEngine,
    LuciformDynamicPromptSystem,
    InjectionPoint,
    RetroInjectionRule
)

from .orchestration.intelligent_orchestrator import (
    IntelligentOrchestrator,
    OrchestrationResult,
    PromptTemplateManager
)
from .orchestration.intelligent_md_daemon import IntelligentMDDaemon

# Points d'entrée principaux
__all__ = [
    # Core
    "OpenAIAnalyzer",
    "AIInsights", 
    "ContentTypeDetector",
    "ContentType",
    "ContentCharacteristics",
    "ContextualMDAnalyzer",
    "ContextualAnalysis",
    "MDDaemonCore",
    "DaemonConfig",
    
    # Adapters
    "MessageBus",
    "MessageHandler", 
    "ProtocolError",
    "ContentDetectorAdapter",
    "AIAnalyzerAdapter",
    "MemoryEngineAdapter",
    
    # Prompts
    "DynamicInjectionEngine",
    "LuciformDynamicPromptSystem",
    "InjectionPoint",
    "RetroInjectionRule",
    
    # Orchestration
    "IntelligentOrchestrator",
    "OrchestrationResult",
    "PromptTemplateManager",
    "IntelligentMDDaemon"
]

def get_version():
    """Retourne la version du daemon."""
    return __version__

def get_info():
    """Retourne les informations du daemon."""
    return {
        "name": "MD Hierarchy Analyzer Daemon",
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "components": {
            "core": ["OpenAI Analyzer", "Content Detector", "Contextual Analyzer", "Daemon Core"],
            "adapters": ["Message Bus", "Protocol Adapters"],
            "prompts": ["Dynamic Injection System", "Luciform Prompts"],
            "orchestration": ["Intelligent Orchestrator", "Intelligent Daemon"]
        }
    }

print(f"⛧ {__description__} v{__version__} ⛧")
