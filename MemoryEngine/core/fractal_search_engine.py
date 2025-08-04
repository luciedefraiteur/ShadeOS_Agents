#!/usr/bin/env python3
"""
⛧ Fractal Search Engine - Moteur de Recherche Fractal Unifié ⛧

Moteur de recherche unifié pour MemoryEngine avec détection automatique du type de recherche.
Sépare clairement la recherche fractale pure et la recherche temporelle.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

from Core.LLMProviders import LLMProvider
from .meta_path_adapter import MetaPathAdapter, UnifiedResultFormatter


class SearchType(Enum):
    """Types de recherche supportés"""
    FRACTAL_PURE = "fractal_pure"      # Recherche par relations de nœuds
    TEMPORAL = "temporal"              # Recherche temporelle
    MIXED = "mixed"                    # Combinaison des deux (futur)


@dataclass
class SearchQuery:
    """Requête de recherche normalisée"""
    original_query: str
    search_type: SearchType
    fractal_params: Dict[str, Any]
    temporal_params: Dict[str, Any]
    confidence: float


@dataclass
class SearchResult:
    """Résultat de recherche unifié"""
    query: SearchQuery
    fractal_results: List[Any]
    temporal_results: List[Any]
    combined_results: List[Any]
    search_duration: float
    metadata: Dict[str, Any]


class FractalSearchEngine:
    """Moteur de recherche fractal unifié"""
    
    def __init__(self, memory_engine, llm_provider: LLMProvider):
        self.memory_engine = memory_engine
        self.llm_provider = llm_provider
        
    async def search(self, query: str, **kwargs) -> SearchResult:
        """
        Recherche unifiée avec détection automatique du type
        
        Args:
            query: Requête utilisateur (ex: "cache", "2025-08-04", "architecture")
            **kwargs: Paramètres supplémentaires
            
        Returns:
            SearchResult avec tous les résultats
        """
        start_time = time.time()
        
        # 1. Détection du type de recherche avec LLM
        search_query = await self._detect_search_type(query)
        
        # 2. Exécution de la recherche selon le type
        fractal_results = []
        temporal_results = []
        
        if search_query.search_type in [SearchType.FRACTAL_PURE, SearchType.MIXED]:
            fractal_results = await self._execute_fractal_search(search_query)
            
        if search_query.search_type in [SearchType.TEMPORAL, SearchType.MIXED]:
            temporal_results = await self._execute_temporal_search(search_query)
        
        # 3. Combinaison des résultats (pour l'instant simple)
        combined_results = fractal_results + temporal_results
        
        duration = time.time() - start_time
        
        return SearchResult(
            query=search_query,
            fractal_results=fractal_results,
            temporal_results=temporal_results,
            combined_results=combined_results,
            search_duration=duration,
            metadata={
                "fractal_count": len(fractal_results),
                "temporal_count": len(temporal_results),
                "total_count": len(combined_results)
            }
        )
    
    async def _detect_search_type(self, query: str) -> SearchQuery:
        """
        Détection du type de recherche avec LLM simple
        
        Args:
            query: Requête utilisateur
            
        Returns:
            SearchQuery avec type détecté et paramètres
        """
        # Prompt simple pour la détection
        detection_prompt = f"""
Tu es un moteur de détection de type de recherche pour un système de mémoire fractale.

Analyse cette requête et détermine le type de recherche :

REQUÊTE: "{query}"

TYPES DISPONIBLES:
- FRACTAL_PURE: Recherche par mots-clés, concepts, relations entre nœuds
- TEMPORAL: Recherche par dates, périodes, chronologie, "récemment", "hier", etc.

Réponds UNIQUEMENT avec le type (FRACTAL_PURE ou TEMPORAL) et une confiance de 0.0 à 1.0.

Exemples:
- "cache" → FRACTAL_PURE (0.9)
- "2025-08-04" → TEMPORAL (0.95)
- "récemment" → TEMPORAL (0.8)
- "architecture" → FRACTAL_PURE (0.85)
"""
        
        try:
            response = await self.llm_provider.generate_response(detection_prompt)
            response_text = response.content.strip()
            
            # Parsing simple de la réponse
            if "FRACTAL_PURE" in response_text:
                search_type = SearchType.FRACTAL_PURE
                confidence = self._extract_confidence(response_text)
            elif "TEMPORAL" in response_text:
                search_type = SearchType.TEMPORAL
                confidence = self._extract_confidence(response_text)
            else:
                # Fallback: par défaut fractal
                search_type = SearchType.FRACTAL_PURE
                confidence = 0.5
                
        except Exception as e:
            # Fallback en cas d'erreur LLM
            print(f"⚠️ Erreur détection LLM: {e}, fallback fractal")
            search_type = SearchType.FRACTAL_PURE
            confidence = 0.5
        
        # Génération des paramètres selon le type
        fractal_params = {}
        temporal_params = {}
        
        if search_type == SearchType.FRACTAL_PURE:
            fractal_params = {
                "keyword": query,
                "strata": None,  # Toutes les strates
                "search_method": "keyword"
            }
        elif search_type == SearchType.TEMPORAL:
            temporal_params = {
                "query_type": "keywords",
                "query_value": query,
                "anchor_date": query if self._looks_like_date(query) else None
            }
        
        return SearchQuery(
            original_query=query,
            search_type=search_type,
            fractal_params=fractal_params,
            temporal_params=temporal_params,
            confidence=confidence
        )
    
    def _extract_confidence(self, response: str) -> float:
        """Extrait la confiance de la réponse LLM"""
        try:
            # Cherche un nombre entre parenthèses
            import re
            match = re.search(r'\(([0-9]*\.?[0-9]+)\)', response)
            if match:
                return float(match.group(1))
        except:
            pass
        return 0.7  # Confiance par défaut
    
    def _looks_like_date(self, query: str) -> bool:
        """Détecte si la requête ressemble à une date"""
        import re
        # Patterns de dates simples
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # 2025-08-04
            r'\d{2}/\d{2}/\d{4}',  # 04/08/2025
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # 4/8/25
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, query):
                return True
        return False
    
    async def _execute_fractal_search(self, search_query: SearchQuery) -> List[Any]:
        """Exécute une recherche fractale pure"""
        results = []
        
        try:
            # Recherche par mot-clé
            if search_query.fractal_params.get("keyword"):
                keyword_results = self.memory_engine.find_memories_by_keyword(
                    search_query.fractal_params["keyword"]
                )
                results.extend(keyword_results)
            
            # Recherche par strate si spécifiée
            if search_query.fractal_params.get("strata"):
                strata_results = self.memory_engine.find_by_strata(
                    search_query.fractal_params["strata"]
                )
                results.extend(strata_results)
                
        except Exception as e:
            print(f"❌ Erreur recherche fractale: {e}")
        
        return results
    
    async def _execute_temporal_search(self, search_query: SearchQuery) -> List[Any]:
        """Exécute une recherche temporelle"""
        results = []
        
        try:
            temporal_params = search_query.temporal_params
            
            # Recherche temporelle directe
            if temporal_params.get("query_type") and temporal_params.get("query_value"):
                temporal_results = self.memory_engine.temporal_index.search_temporal(
                    temporal_params["query_type"],
                    temporal_params["query_value"],
                    self.memory_engine
                )
                
                # Virtualisation des FractalMemoryNode en chemins avec MetaPathAdapter
                for result in temporal_results:
                    if hasattr(result, 'metadata'):  # C'est un FractalMemoryNode
                        adapter = MetaPathAdapter(fractal_node=result)
                        results.append(adapter.get_path())
                    else:
                        # C'est déjà un chemin string
                        results.append(str(result))
                
        except Exception as e:
            print(f"❌ Erreur recherche temporelle: {e}")
        
        return results
    
    # Méthodes spécialisées pour debug
    async def search_fractal_only(self, query: str) -> List[Any]:
        """Recherche fractale pure uniquement"""
        search_query = SearchQuery(
            original_query=query,
            search_type=SearchType.FRACTAL_PURE,
            fractal_params={"keyword": query, "strata": None, "search_method": "keyword"},
            temporal_params={},
            confidence=1.0
        )
        return await self._execute_fractal_search(search_query)
    
    async def search_temporal_only(self, query: str) -> List[Any]:
        """Recherche temporelle uniquement"""
        search_query = SearchQuery(
            original_query=query,
            search_type=SearchType.TEMPORAL,
            fractal_params={},
            temporal_params={"query_type": "keywords", "query_value": query},
            confidence=1.0
        )
        return await self._execute_temporal_search(search_query)
    
    def format_results(self, results: List[Any], format_type: str = "paths") -> List[Any]:
        """
        Formate les résultats selon le type demandé
        
        Args:
            results: Liste de résultats (FractalMemoryNode, strings, ou MetaPathAdapter)
            format_type: "paths", "nodes", "adapters", ou "mixed"
            
        Returns:
            Liste formatée selon le type demandé
        """
        return UnifiedResultFormatter.format_results(results, format_type)


# Notes pour le futur (MIXED):
"""
IDÉES POUR LA RECHERCHE MIXTE (FUTUR):

1. Recherche fractale → ancrage temporel → propagation temporelle
   - Trouver des nœuds fractaux liés au concept
   - Utiliser leurs timestamps comme ancres temporelles
   - Propager temporellement autour de ces ancres

2. Recherche temporelle → enrichissement fractal
   - Trouver des événements temporels
   - Enrichir avec leurs relations fractales
   - Explorer les strates et liens

3. Navigation hybride
   - Commencer par un type, basculer vers l'autre
   - Combiner les résultats avec pondération
   - Contextualisation temporelle des relations fractales

4. Métriques de pertinence combinées
   - Score fractal (liens, strates, respiration)
   - Score temporel (proximité temporelle)
   - Score combiné (moyenne pondérée)
""" 