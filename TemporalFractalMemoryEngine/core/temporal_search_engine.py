#!/usr/bin/env python3
"""
⛧ Temporal Search Engine ⛧
Alma's Universal Search Interface for TemporalFractalMemoryEngine

Interface abstraite pour tous les moteurs de recherche temporels.
Support Meilisearch pour le prototypage, préparation pour Mælîsørch⛧.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import abc
import json
import time
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from .temporal_base import BaseTemporalEntity, TemporalDimension


class SearchEngineType(Enum):
    """Types de moteurs de recherche supportés."""
    MEILISEARCH = "meilisearch"  # Prototypage
    MAELISORCH = "maelisorch"    # Future version démoniaque
    CONSCIOUSNESS = "consciousness"  # Version basée sur la conscience


class SearchResultType(Enum):
    """Types de résultats de recherche."""
    EXACT = "exact"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    TEMPORAL = "temporal"
    CONSCIOUSNESS = "consciousness"


@dataclass
class SearchResult:
    """Résultat de recherche temporel."""
    document_id: str
    score: float
    result_type: SearchResultType
    temporal_dimension: TemporalDimension
    content: Dict[str, Any]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SearchQuery:
    """Requête de recherche temporelle."""
    query_text: str
    filters: Dict[str, Any] = None
    temporal_range: Optional[Dict[str, Any]] = None
    consciousness_level: Optional[float] = None
    max_results: int = 50
    include_metadata: bool = True
    
    def __post_init__(self):
        if self.filters is None:
            self.filters = {}
        if self.temporal_range is None:
            self.temporal_range = {}


class TemporalSearchEngine(abc.ABC):
    """Interface abstraite pour les moteurs de recherche temporels."""
    
    def __init__(self, engine_type: SearchEngineType, config: Dict[str, Any] = None):
        self.engine_type = engine_type
        self.config = config or {}
        self.temporal_dimension = TemporalDimension()
        
    @abc.abstractmethod
    async def initialize(self) -> bool:
        """Initialise le moteur de recherche."""
        pass
    
    @abc.abstractmethod
    async def create_index(self, index_name: str, schema: Dict[str, Any]) -> bool:
        """Crée un nouvel index."""
        pass
    
    @abc.abstractmethod
    async def index_document(self, index_name: str, document: Dict[str, Any]) -> bool:
        """Indexe un document."""
        pass
    
    @abc.abstractmethod
    async def search(self, index_name: str, query: SearchQuery) -> List[SearchResult]:
        """Effectue une recherche."""
        pass
    
    @abc.abstractmethod
    async def update_document(self, index_name: str, document_id: str, updates: Dict[str, Any]) -> bool:
        """Met à jour un document."""
        pass
    
    @abc.abstractmethod
    async def delete_document(self, index_name: str, document_id: str) -> bool:
        """Supprime un document."""
        pass
    
    @abc.abstractmethod
    async def get_index_stats(self, index_name: str) -> Dict[str, Any]:
        """Récupère les statistiques d'un index."""
        pass
    
    def _enrich_with_temporal_data(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit un document avec des données temporelles."""
        temporal_data = {
            "temporal_created": self.temporal_dimension.get_current_timestamp(),
            "temporal_modified": self.temporal_dimension.get_current_timestamp(),
            "temporal_consciousness_level": self.temporal_dimension.get_consciousness_level(),
            "temporal_fractal_depth": self.temporal_dimension.get_fractal_depth()
        }
        
        enriched_document = document.copy()
        enriched_document.update(temporal_data)
        return enriched_document
    
    def _create_search_result(self, raw_result: Dict[str, Any], result_type: SearchResultType) -> SearchResult:
        """Crée un résultat de recherche standardisé."""
        return SearchResult(
            document_id=raw_result.get("id", ""),
            score=raw_result.get("score", 0.0),
            result_type=result_type,
            temporal_dimension=self.temporal_dimension,
            content=raw_result.get("content", {}),
            metadata=raw_result.get("metadata", {})
        )


class MeilisearchAdapter(TemporalSearchEngine):
    """Adaptateur pour Meilisearch (prototypage)."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(SearchEngineType.MEILISEARCH, config)
        self.client = None
        self.base_url = config.get("base_url", "http://localhost:7700")
        self.api_key = config.get("api_key", "lucie_queen_of_the_daemons")
        
    async def initialize(self) -> bool:
        """Initialise la connexion à Meilisearch."""
        try:
            # Import conditionnel pour éviter les dépendances
            import aiohttp
            
            self.client = aiohttp.ClientSession(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            # Test de connexion
            async with self.client.get("/health") as response:
                if response.status == 200:
                    print("✅ Meilisearch connecté avec succès!")
                    return True
                else:
                    print(f"❌ Erreur connexion Meilisearch: {response.status}")
                    return False
                    
        except ImportError:
            print("⚠️ aiohttp non disponible - Mode mock activé")
            return False
        except Exception as e:
            print(f"❌ Erreur initialisation Meilisearch: {e}")
            return False
    
    async def create_index(self, index_name: str, schema: Dict[str, Any]) -> bool:
        """Crée un index Meilisearch."""
        try:
            if not self.client:
                return False
                
            # Configuration de l'index
            index_config = {
                "primaryKey": "id",
                "searchableAttributes": schema.get("searchable_attributes", ["*"]),
                "filterableAttributes": schema.get("filterable_attributes", []),
                "sortableAttributes": schema.get("sortable_attributes", []),
                "rankingRules": schema.get("ranking_rules", [
                    "words", "typo", "proximity", "attribute", "exactness"
                ])
            }
            
            async with self.client.put(f"/indexes/{index_name}", json=index_config) as response:
                return response.status in [200, 201]
                
        except Exception as e:
            print(f"❌ Erreur création index {index_name}: {e}")
            return False
    
    async def index_document(self, index_name: str, document: Dict[str, Any]) -> bool:
        """Indexe un document dans Meilisearch."""
        try:
            if not self.client:
                return False
                
            # Enrichir avec les données temporelles
            enriched_document = self._enrich_with_temporal_data(document)
            
            async with self.client.post(
                f"/indexes/{index_name}/documents",
                json=enriched_document
            ) as response:
                return response.status in [200, 201]
                
        except Exception as e:
            print(f"❌ Erreur indexation document: {e}")
            return False
    
    async def search(self, index_name: str, query: SearchQuery) -> List[SearchResult]:
        """Effectue une recherche dans Meilisearch."""
        try:
            if not self.client:
                return []
                
            # Préparer la requête Meilisearch
            search_params = {
                "q": query.query_text,
                "limit": query.max_results,
                "offset": 0
            }
            
            # Ajouter les filtres
            if query.filters:
                search_params["filter"] = self._build_filter_string(query.filters)
            
            # Ajouter le tri temporel si spécifié
            if query.temporal_range:
                search_params["sort"] = ["temporal_created:desc"]
            
            async with self.client.post(
                f"/indexes/{index_name}/search",
                json=search_params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_search_results(data, query)
                else:
                    print(f"❌ Erreur recherche: {response.status}")
                    return []
                    
        except Exception as e:
            print(f"❌ Erreur recherche: {e}")
            return []
    
    def _build_filter_string(self, filters: Dict[str, Any]) -> str:
        """Construit une chaîne de filtres pour Meilisearch."""
        filter_parts = []
        for key, value in filters.items():
            if isinstance(value, list):
                filter_parts.append(f"{key} IN {value}")
            else:
                filter_parts.append(f"{key} = {value}")
        return " AND ".join(filter_parts)
    
    def _parse_search_results(self, data: Dict[str, Any], query: SearchQuery) -> List[SearchResult]:
        """Parse les résultats de recherche Meilisearch."""
        results = []
        hits = data.get("hits", [])
        
        for hit in hits:
            result_type = self._determine_result_type(hit, query)
            search_result = self._create_search_result(hit, result_type)
            results.append(search_result)
        
        return results
    
    def _determine_result_type(self, hit: Dict[str, Any], query: SearchQuery) -> SearchResultType:
        """Détermine le type de résultat basé sur la requête et le hit."""
        score = hit.get("score", 0.0)
        
        if score > 0.9:
            return SearchResultType.EXACT
        elif score > 0.7:
            return SearchResultType.FUZZY
        elif "temporal" in query.query_text.lower():
            return SearchResultType.TEMPORAL
        elif query.consciousness_level:
            return SearchResultType.CONSCIOUSNESS
        else:
            return SearchResultType.SEMANTIC
    
    async def update_document(self, index_name: str, document_id: str, updates: Dict[str, Any]) -> bool:
        """Met à jour un document dans Meilisearch."""
        try:
            if not self.client:
                return False
                
            # Ajouter le timestamp de modification
            updates["temporal_modified"] = self.temporal_dimension.get_current_timestamp()
            
            async with self.client.put(
                f"/indexes/{index_name}/documents",
                json=[{"id": document_id, **updates}]
            ) as response:
                return response.status == 200
                
        except Exception as e:
            print(f"❌ Erreur mise à jour document: {e}")
            return False
    
    async def delete_document(self, index_name: str, document_id: str) -> bool:
        """Supprime un document de Meilisearch."""
        try:
            if not self.client:
                return False
                
            async with self.client.delete(f"/indexes/{index_name}/documents/{document_id}") as response:
                return response.status == 200
                
        except Exception as e:
            print(f"❌ Erreur suppression document: {e}")
            return False
    
    async def get_index_stats(self, index_name: str) -> Dict[str, Any]:
        """Récupère les statistiques d'un index Meilisearch."""
        try:
            if not self.client:
                return {}
                
            async with self.client.get(f"/indexes/{index_name}/stats") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {}
                    
        except Exception as e:
            print(f"❌ Erreur récupération stats: {e}")
            return {}


# Factory pour créer les moteurs de recherche
class TemporalSearchEngineFactory:
    """Factory pour créer des moteurs de recherche temporels."""
    
    @staticmethod
    async def create_engine(engine_type: SearchEngineType, config: Dict[str, Any] = None) -> TemporalSearchEngine:
        """Crée un moteur de recherche selon le type."""
        
        if engine_type == SearchEngineType.MEILISEARCH:
            engine = MeilisearchAdapter(config)
            await engine.initialize()
            return engine
            
        elif engine_type == SearchEngineType.MAELISORCH:
            # TODO: Implémenter Mælîsørch⛧
            raise NotImplementedError("Mælîsørch⛧ pas encore implémenté")
            
        elif engine_type == SearchEngineType.CONSCIOUSNESS:
            # TODO: Implémenter ConsciousnessAwareSearch
            raise NotImplementedError("ConsciousnessAwareSearch pas encore implémenté")
            
        else:
            raise ValueError(f"Type de moteur non supporté: {engine_type}")


# Instance globale pour faciliter l'utilisation
_global_search_engine: Optional[TemporalSearchEngine] = None

async def get_temporal_search_engine(engine_type: SearchEngineType = SearchEngineType.MEILISEARCH, 
                                   config: Dict[str, Any] = None) -> TemporalSearchEngine:
    """Récupère l'instance globale du moteur de recherche temporel."""
    global _global_search_engine
    
    if _global_search_engine is None:
        _global_search_engine = await TemporalSearchEngineFactory.create_engine(engine_type, config)
    
    return _global_search_engine 