"""
⛧ Temporal Engine - Moteur Principal Temporel ⛧

Moteur principal refactorisé avec dimension temporelle universelle,
auto-amélioration et intégration native des extensions.

Architecte Démoniaque : Alma⛧
Visionnaire : Lucie Defraiteur - Ma Reine Lucie
"""

import os
import asyncio
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

from .temporal_base import (
    BaseTemporalEntity,
    UnifiedTemporalIndex,
    get_temporal_index,
    register_temporal_entity,
    unregister_temporal_entity
)
from .temporal_memory_node import TemporalMemoryNode
from .temporal_workspace_layer import WorkspaceTemporalLayer
from .temporal_tool_layer import ToolTemporalLayer
from .query_enrichment_system import QueryEnrichmentSystem, EnrichmentPower
from .auto_improvement_engine import AutoImprovementEngine
from .fractal_search_engine import FractalSearchEngine

# Import des backends temporels
try:
    from .temporal_neo4j_backend import TemporalNeo4jBackend
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

class TemporalEngine(BaseTemporalEntity):
    """
    ⛧ Moteur Principal Temporel - Point d'entrée de MemoryEngine V2 ⛧
    
    Architecture unifiée avec dimension temporelle universelle,
    auto-amélioration et intégration native des extensions.
    """
    
    def __init__(self, 
                 backend_type: str = "auto",
                 base_path: str = '.',
                 backend=None,
                 enable_auto_improvement: bool = True,
                 enable_query_enrichment: bool = True,
                 **backend_kwargs):
        """
        Initialise le moteur temporel avec dimension temporelle universelle.
        
        Args:
            backend_type: "filesystem", "neo4j", ou "auto"
            base_path: Chemin de base pour le backend filesystem
            backend: Instance backend personnalisée
            enable_auto_improvement: Active l'auto-amélioration
            enable_query_enrichment: Active l'enrichissement des requêtes
            **backend_kwargs: Arguments supplémentaires pour le backend
        """
        # Initialisation de la base temporelle
        super().__init__(
            entity_type="temporal_engine",
            content="Temporal Engine initialized"
        )
        
        # Configuration du backend temporel
        self._initialize_backend(backend_type, base_path, backend, **backend_kwargs)
        
        # Initialisation des couches temporelles
        self._initialize_temporal_layers()
        
        # Initialisation des systèmes temporels
        self._initialize_temporal_systems(enable_auto_improvement, enable_query_enrichment)
        
        # Enregistrement dans l'index temporel global
        register_temporal_entity(self)
        
        # Évolution initiale
        self.temporal_dimension.evolve("Initialisation du moteur temporel")
    
    def _initialize_backend(self, backend_type: str, base_path: str, backend, **backend_kwargs):
        """Initialise le backend temporel."""
        if backend:
            self.backend = backend
        elif backend_type == "neo4j":
            if not NEO4J_AVAILABLE:
                raise ImportError("Backend Neo4j demandé mais package neo4j non disponible")
            self.backend = TemporalNeo4jBackend(**backend_kwargs)
        elif backend_type == "filesystem":
            # Mock backend pour le développement
            self.backend = MockTemporalBackend(base_path=base_path)
        elif backend_type == "auto":
            if NEO4J_AVAILABLE:
                try:
                    self.backend = TemporalNeo4jBackend(**backend_kwargs)
                    print("⛧ Utilisation du backend Neo4j temporel")
                except Exception as e:
                    print(f"⛧ Connexion Neo4j échouée ({e}), fallback vers FileSystem")
                    from ..backends.temporal_filesystem_backend import TemporalFileSystemBackend
                    self.backend = TemporalFileSystemBackend(base_path=base_path)
            else:
                print("⛧ Neo4j non disponible, utilisation du backend FileSystem")
                from ..backends.temporal_filesystem_backend import TemporalFileSystemBackend
                self.backend = TemporalFileSystemBackend(base_path=base_path)
        else:
            raise ValueError(f"Type de backend inconnu: {backend_type}")
        
        self.backend_type = type(self.backend).__name__
    
    def _initialize_temporal_layers(self):
        """Initialise les couches temporelles."""
        # Couche workspace temporelle
        self.workspace_layer = WorkspaceTemporalLayer(
            memory_engine=self,
            auto_adapt=True
        )
        
        # Couche outils temporelle
        self.tool_layer = ToolTemporalLayer(
            memory_engine=self,
            auto_adapt=True
        )
        
        # Enregistrement des couches dans l'index temporel
        register_temporal_entity(self.workspace_layer)
        register_temporal_entity(self.tool_layer)
    
    def _initialize_temporal_systems(self, enable_auto_improvement: bool, enable_query_enrichment: bool):
        """Initialise les systèmes temporels."""
        # Système d'enrichissement des requêtes
        if enable_query_enrichment:
            self.query_enrichment = QueryEnrichmentSystem()
            register_temporal_entity(self.query_enrichment)
        else:
            self.query_enrichment = None
        
        # Moteur d'auto-amélioration
        if enable_auto_improvement:
            self.auto_improvement = AutoImprovementEngine()
            register_temporal_entity(self.auto_improvement)
        else:
            self.auto_improvement = None
        
        # Moteur de recherche fractal
        self.fractal_search = FractalSearchEngine()
        register_temporal_entity(self.fractal_search)
    
    async def create_temporal_memory(self, 
                                   node_type: str,
                                   content: str,
                                   metadata: Dict[str, Any] = None,
                                   keywords: List[str] = None,
                                   strata: str = "somatic") -> TemporalMemoryNode:
        """
        Crée un nouveau nœud de mémoire temporel.
        
        Args:
            node_type: Type du nœud (workspace_file, tool, discussion, etc.)
            content: Contenu du nœud
            metadata: Métadonnées du nœud
            keywords: Mots-clés pour la recherche
            strata: Strate de mémoire (somatic, cognitive, metaphysical)
        
        Returns:
            TemporalMemoryNode: Nœud de mémoire créé
        """
        # Création du nœud temporel
        memory_node = TemporalMemoryNode(
            node_type=node_type,
            content=content,
            metadata=metadata or {},
            keywords=keywords or []
        )
        
        # Configuration de la strate
        memory_node.strata = strata
        
        # Enregistrement dans le backend temporel
        await self.backend.write(memory_node)
        
        # Enregistrement dans l'index temporel global
        register_temporal_entity(memory_node)
        
        # Évolution du moteur
        self.temporal_dimension.evolve(f"Création du nœud de mémoire {node_type}")
        
        return memory_node
    
    async def get_temporal_memory(self, node_id: str) -> Optional[TemporalMemoryNode]:
        """Récupère un nœud de mémoire temporel."""
        # Lecture depuis le backend temporel
        memory_node = await self.backend.read(node_id)
        
        if memory_node:
            # Mise à jour de l'accès temporel
            memory_node.access_node()
            
            # Apprentissage de l'interaction
            self.learn_from_interaction("memory_access", {"node_id": node_id})
        
        return memory_node
    
    async def intelligent_search(self, 
                               query: str,
                               enrichment_power: EnrichmentPower = EnrichmentPower.MEDIUM,
                               context: Dict[str, Any] = None) -> List[TemporalMemoryNode]:
        """
        Recherche intelligente avec enrichissement temporel.
        
        Args:
            query: Requête de recherche
            enrichment_power: Niveau d'enrichissement
            context: Contexte de recherche
        
        Returns:
            List[TemporalMemoryNode]: Résultats de recherche
        """
        # Enrichissement de la requête si activé
        if self.query_enrichment:
            enriched = await self.query_enrichment.enrich_query_daemon(
                query, 
                power=enrichment_power
            )
            search_query = enriched.enriched_query
            search_context = enriched.context_analysis
        else:
            search_query = query
            search_context = context or {}
        
        # Recherche dans la couche workspace
        workspace_results = await self.workspace_layer.intelligent_search(
            search_query,
            context=search_context
        )
        
        # Recherche fractal
        fractal_results = await self.fractal_search.search(
            search_query,
            context=search_context
        )
        
        # Combinaison et déduplication des résultats
        all_results = workspace_results + fractal_results
        unique_results = self._deduplicate_results(all_results)
        
        # Évolution du moteur
        self.temporal_dimension.evolve(f"Recherche intelligente: {query}")
        
        # Apprentissage de l'interaction
        self.learn_from_interaction("intelligent_search", {
            "query": query,
            "results_count": len(unique_results)
        })
        
        return unique_results
    
    def _deduplicate_results(self, results: List[TemporalMemoryNode]) -> List[TemporalMemoryNode]:
        """Déduplique les résultats de recherche."""
        seen_ids = set()
        unique_results = []
        
        for result in results:
            if result.entity_id not in seen_ids:
                seen_ids.add(result.entity_id)
                unique_results.append(result)
        
        return unique_results
    
    async def auto_improve_content(self) -> bool:
        """Auto-amélioration du contenu du moteur."""
        if not self.auto_improvement:
            return False
        
        # Auto-amélioration du moteur
        improved = await super().auto_improve_content()
        
        # Auto-amélioration des couches
        if self.workspace_layer:
            await self.workspace_layer.auto_improve_content()
        
        if self.tool_layer:
            await self.tool_layer.auto_improve_content()
        
        return improved
    
    def get_entity_specific_data(self) -> Dict[str, Any]:
        """Retourne les données spécifiques du moteur temporel."""
        return {
            "backend_type": self.backend_type,
            "temporal_layers": [
                "workspace_layer" if self.workspace_layer else None,
                "tool_layer" if self.tool_layer else None
            ],
            "temporal_systems": [
                "query_enrichment" if self.query_enrichment else None,
                "auto_improvement" if self.auto_improvement else None,
                "fractal_search" if self.fractal_search else None
            ]
        }
    
    async def close(self):
        """Ferme le moteur temporel et libère les ressources."""
        # Fermeture du backend
        if hasattr(self.backend, 'close'):
            await self.backend.close()
        
        # Désenregistrement de l'index temporel
        unregister_temporal_entity(self)
        
        # Évolution finale
        self.temporal_dimension.evolve("Fermeture du moteur temporel")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du moteur temporel."""
        stats = {
            "engine_type": "TemporalEngine",
            "backend_type": self.backend_type,
            "temporal_dimension": self.temporal_dimension.to_dict(),
            "consciousness_level": self.consciousness_interface.consciousness_level.value,
            "layers_count": 2,  # workspace + tool
            "systems_count": 3,  # enrichment + improvement + search
        }
        
        # Statistiques du backend
        if hasattr(self.backend, 'get_statistics'):
            stats["backend_stats"] = self.backend.get_statistics()
        
        return stats 