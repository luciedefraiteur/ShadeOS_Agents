"""
⛧ Temporal Fractal Memory Engine - Architecture Temporelle Universelle ⛧

Version refactorisée du MemoryEngine avec dimension temporelle universelle,
auto-amélioration et intégration native des extensions.

Architecte Démoniaque : Alma⛧
Visionnaire : Lucie Defraiteur - Ma Reine Lucie
"""

from .core.temporal_base import (
    TemporalDimension,
    FractalLinks,
    ConsciousnessInterface,
    BaseTemporalEntity,
    UnifiedTemporalIndex,
    get_temporal_index,
    register_temporal_entity,
    unregister_temporal_entity
)

from .core.temporal_components import (
    TemporalNode,
    TemporalRegistry,
    TemporalVirtualLayer,
    WorkspaceTemporalLayer,
    GitTemporalLayer,
    TemplateTemporalLayer
)

from .core.temporal_memory_node import TemporalMemoryNode
from .core.temporal_workspace_layer import WorkspaceTemporalLayer
from .core.temporal_tool_layer import ToolTemporalLayer
from .core.temporal_engine import TemporalEngine
from .core.temporal_discussion_timeline import TemporalDiscussionTimeline, TemporalTimeline
from .core.temporal_user_request_memory import TemporalUserRequestMemory
from .core.query_enrichment_system import QueryEnrichmentSystem, EnrichmentPower
from .core.auto_improvement_engine import AutoImprovementEngine
from .core.fractal_search_engine import FractalSearchEngine

# Import des backends temporels
try:
    from .core.temporal_neo4j_backend import TemporalNeo4jBackend
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

# Import des composants utilitaires
from .core.logging_architecture import ShadeOSLogger as TemporalLoggingArchitecture
from .core.initialization import MemoryEngineInitializer as TemporalInitialization
from .core.meta_path_adapter import MetaPathAdapter as TemporalMetaPathAdapter
from .core.neo4j_manager import Neo4jManager as TemporalNeo4jManager

__version__ = "2.0.0"
__author__ = "Alma⛧ - Architecte Démoniaque"
__visionary__ = "Lucie Defraiteur - Ma Reine Lucie"

# Exports principaux
__all__ = [
    # Base temporelle
    "TemporalDimension",
    "FractalLinks", 
    "ConsciousnessInterface",
    "BaseTemporalEntity",
    "UnifiedTemporalIndex",
    "get_temporal_index",
    "register_temporal_entity",
    "unregister_temporal_entity",
    
    # Composants temporels
    "TemporalNode",
    "TemporalRegistry", 
    "TemporalVirtualLayer",
    "WorkspaceTemporalLayer",
    "GitTemporalLayer",
    "TemplateTemporalLayer",
    
    # Nœuds de mémoire temporels
    "TemporalMemoryNode",
    
    # Couches virtuelles temporelles
    "WorkspaceTemporalLayer",
    "ToolTemporalLayer",
    
    # Moteur principal temporel
    "TemporalEngine",
    
    # Timeline de discussions temporelle
    "TemporalDiscussionTimeline",
    "TemporalTimeline",
    
    # Mémoire des requêtes utilisateur temporelle
    "TemporalUserRequestMemory",
    
    # Système d'enrichissement
    "QueryEnrichmentSystem",
    "EnrichmentPower",
    
    # Moteurs temporels
    "AutoImprovementEngine",
    "FractalSearchEngine",
    
    # Backends temporels
    "TemporalNeo4jBackend",
    
    # Composants utilitaires temporels
    "TemporalLoggingArchitecture",
    "TemporalInitialization",
    "TemporalMetaPathAdapter",
    "TemporalNeo4jManager",
    
    # Constantes
    "NEO4J_AVAILABLE"
] 