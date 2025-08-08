#!/usr/bin/env python3
"""
⛧ MemoryEngine V2 - Query Enrichment System ⛧

Système d'enrichissement universel des requêtes LLM dans MemoryEngine.
Hiérarchie d'utilisateurs avec puissance d'enrichissement graduée.
"""

import json
import re
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass

from Core.Providers.LLMProviders import LLMProvider


class EnrichmentPower(Enum):
    """Niveaux de puissance d'enrichissement"""
    LOW = "low"      # Mots-clés basiques
    MEDIUM = "medium" # Requête + mots-clés
    HIGH = "high"    # Requête + mots-clés + contexte
    FULL = "full"    # Assistant V9 - contrôle total
    CUSTOM = "custom" # Lib Users - personnalisation complète


@dataclass
class EnrichmentResult:
    """Résultat d'enrichissement de requête"""
    original_query: str
    enriched_query: str
    method_chosen: str
    additional_keywords: List[str]
    context_analysis: Dict[str, Any]
    enrichment_power: str
    modules_used: List[str]
    llm_calls_count: int


class QueryEnrichmentSystem:
    """Système d'enrichissement universel des requêtes"""
    
    def __init__(self, llm_provider: LLMProvider = None):
        self.llm_provider = llm_provider
        
        # Fragments modulaires hardcodés
        self.enrichment_fragments = {
            "method_choice": {
                "prompt": "Choisis la meilleure méthode de recherche",
                "response_format": "simple",
                "description": "Sélection de la méthode optimale"
            },
            "query_enrichment": {
                "prompt": "Enrichis la requête avec des mots-clés supplémentaires",
                "response_format": "json",
                "description": "Amélioration de la requête"
            },
            "context_analysis": {
                "prompt": "Analyse le contexte et ajoute des métadonnées",
                "response_format": "json",
                "description": "Analyse contextuelle"
            },
            "mixed_strategy": {
                "prompt": "Définis une stratégie de combinaison personnalisée",
                "response_format": "json",
                "description": "Stratégie de combinaison"
            }
        }
        
        # Combinaisons prédéfinies
        self.mixed_strategies = {
            "mixed_basic": ["grep", "fractal"],
            "mixed_global": ["grep", "fractal", "temporal"],
            "mixed_temporal_and_fractal": ["temporal", "fractal"],
            "mixed_temporal_and_grep": ["temporal", "grep"]
        }
        
        # Configuration par défaut
        self.default_config = {
            "enabled": True,
            "power": EnrichmentPower.MEDIUM.value,
            "modules": ["method_choice", "query_enrichment"]
        }
    
    async def enrich_query_daemon(self, query: str, power: str, context: Dict[str, Any] = None) -> EnrichmentResult:
        """Enrichissement pour daemons avec puissance prédéfinie"""
        
        context = context or {}
        llm_calls = 0
        
        if power == EnrichmentPower.LOW.value:
            # Un seul appel LLM simple
            method = await self._simple_method_choice(query)
            llm_calls = 1
            
            return EnrichmentResult(
                original_query=query,
                enriched_query=query,
                method_chosen=method,
                additional_keywords=[],
                context_analysis={},
                enrichment_power=power,
                modules_used=["method_choice"],
                llm_calls_count=llm_calls
            )
        
        elif power == EnrichmentPower.MEDIUM.value:
            # Deux appels LLM
            method = await self._simple_method_choice(query)
            enriched_data = await self._basic_query_enrichment(query)
            llm_calls = 2
            
            return EnrichmentResult(
                original_query=query,
                enriched_query=enriched_data.get("enriched_query", query),
                method_chosen=method,
                additional_keywords=enriched_data.get("additional_keywords", []),
                context_analysis={},
                enrichment_power=power,
                modules_used=["method_choice", "query_enrichment"],
                llm_calls_count=llm_calls
            )
        
        elif power == EnrichmentPower.HIGH.value:
            # Trois appels LLM
            method = await self._simple_method_choice(query)
            enriched_data = await self._basic_query_enrichment(query)
            context_analysis = await self._context_analysis(query, context)
            llm_calls = 3
            
            return EnrichmentResult(
                original_query=query,
                enriched_query=enriched_data.get("enriched_query", query),
                method_chosen=method,
                additional_keywords=enriched_data.get("additional_keywords", []),
                context_analysis=context_analysis,
                enrichment_power=power,
                modules_used=["method_choice", "query_enrichment", "context_analysis"],
                llm_calls_count=llm_calls
            )
        
        else:
            raise ValueError(f"Puissance d'enrichissement non supportée: {power}")
    
    async def enrich_query_v9(self, query: str, power: str, context: Dict[str, Any] = None) -> EnrichmentResult:
        """Enrichissement pour Assistant V9 (même système que les daemons pour l'instant)"""
        
        # Utilise le même système que les daemons
        return await self.enrich_query_daemon(query, power, context)
    
    async def enrich_query_custom(self, query: str, custom_config: Dict[str, Any]) -> EnrichmentResult:
        """Enrichissement personnalisé pour lib users"""
        
        # Configuration personnalisée
        custom_prompt = custom_config.get("prompt_template")
        custom_modules = custom_config.get("modules", [])
        custom_response_format = custom_config.get("response_format", "json")
        
        if custom_prompt:
            # Exécution avec prompt personnalisé
            response = await self.llm_provider.generate_response(custom_prompt)
            result = self._parse_custom_response(response, custom_response_format)
        else:
            # Exécution avec modules personnalisés
            result = await self._execute_custom_enrichment(query, custom_modules)
        
        return EnrichmentResult(
            original_query=query,
            enriched_query=result.get("enriched_query", query),
            method_chosen=result.get("method_chosen", "custom"),
            additional_keywords=result.get("additional_keywords", []),
            context_analysis=result.get("context_analysis", {}),
            enrichment_power=EnrichmentPower.CUSTOM.value,
            modules_used=custom_modules,
            llm_calls_count=result.get("llm_calls_count", 1)
        )
    
    def _build_enrichment_prompt(self, modules: List[str], query: str, context: Dict[str, Any]) -> str:
        """Construction dynamique du prompt selon les modules activés"""
        
        if len(modules) == 1:
            # Un seul module → prompt simple
            fragment = self.enrichment_fragments[modules[0]]
            return f"{fragment['prompt']} pour: {query}"
        
        else:
            # Plusieurs modules → prompt structuré
            prompt_parts = []
            response_format_parts = []
            
            for module in modules:
                if module in self.enrichment_fragments:
                    fragment = self.enrichment_fragments[module]
                    prompt_parts.append(f"- {fragment['description']}: {fragment['prompt']}")
                    response_format_parts.append(f'"{module}": "réponse"')
            
            structured_format = "{\n" + ",\n".join(response_format_parts) + "\n}"
            
            return f"""
Requête: {query}
Contexte: {context}

Exécute les tâches suivantes:
{chr(10).join(prompt_parts)}

Réponds de manière structurée:
{structured_format}
"""
    
    async def _simple_method_choice(self, query: str) -> str:
        """Choix simple de méthode"""
        if not self.llm_provider:
            return self._fallback_method_choice(query)
        
        prompt = f"""
Query: "{query}"

Choose the best search method:
- "grep" (exact patterns, code search, file content)
- "fractal" (conceptual relationships, abstract concepts)
- "temporal" (time-based, history, development flow)
- "mixed" (combine multiple methods)

Answer with just the method name.
"""
        
        try:
            response = await self.llm_provider.generate_response(prompt)
            method = response.content.strip().lower()
            
            # Validation de la méthode
            valid_methods = ["grep", "fractal", "temporal", "mixed"]
            if method not in valid_methods:
                method = "mixed"
            
            return method
        except Exception:
            return self._fallback_method_choice(query)
    
    async def _basic_query_enrichment(self, query: str) -> Dict[str, Any]:
        """Enrichissement basique de la requête"""
        if not self.llm_provider:
            return {"enriched_query": query, "additional_keywords": []}
        
        prompt = f"""
Query: "{query}"

Enrich this query and generate additional keywords for better search.

Respond in JSON format:
{{
    "enriched_query": "improved query",
    "additional_keywords": ["keyword1", "keyword2"]
}}
"""
        
        try:
            response = await self.llm_provider.generate_response(prompt)
            result = json.loads(response.content)
            return {
                "enriched_query": result.get("enriched_query", query),
                "additional_keywords": result.get("additional_keywords", [])
            }
        except Exception:
            return {"enriched_query": query, "additional_keywords": []}
    
    async def _context_analysis(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse contextuelle"""
        if not self.llm_provider:
            return {}
        
        prompt = f"""
Query: "{query}"
Context: {context}

Analyze the context and provide insights for better search.

Respond in JSON format:
{{
    "context_insights": "analysis",
    "suggestions": ["suggestion1", "suggestion2"],
    "priority_factors": ["factor1", "factor2"]
}}
"""
        
        try:
            response = await self.llm_provider.generate_response(prompt)
            result = json.loads(response.content)
            return result
        except Exception:
            return {}
    
    def _parse_structured_response(self, response: Any, modules: List[str], original_query: str) -> Dict[str, Any]:
        """Parse une réponse structurée"""
        try:
            # Tentative de parsing JSON
            result = json.loads(response.content)
            
            # Extraction des données selon les modules
            enriched_query = original_query
            method_chosen = "mixed"
            additional_keywords = []
            context_analysis = {}
            
            if "method_choice" in modules and "method_choice" in result:
                method_chosen = result["method_choice"]
            
            if "query_enrichment" in modules and "query_enrichment" in result:
                enrichment_data = result["query_enrichment"]
                if isinstance(enrichment_data, dict):
                    enriched_query = enrichment_data.get("enriched_query", original_query)
                    additional_keywords = enrichment_data.get("additional_keywords", [])
                elif isinstance(enrichment_data, str):
                    enriched_query = enrichment_data
            
            if "context_analysis" in modules and "context_analysis" in result:
                context_analysis = result["context_analysis"]
            
            return {
                "enriched_query": enriched_query,
                "method_chosen": method_chosen,
                "additional_keywords": additional_keywords,
                "context_analysis": context_analysis
            }
            
        except Exception:
            # Fallback en cas d'erreur de parsing
            return {
                "enriched_query": original_query,
                "method_chosen": "mixed",
                "additional_keywords": [],
                "context_analysis": {}
            }
    
    def _parse_custom_response(self, response: Any, response_format: str) -> Dict[str, Any]:
        """Parse une réponse personnalisée"""
        try:
            if response_format == "json":
                return json.loads(response.content)
            else:
                return {"custom_response": response.content}
        except Exception:
            return {"custom_response": str(response.content)}
    
    async def _execute_custom_enrichment(self, query: str, custom_modules: List[str]) -> Dict[str, Any]:
        """Exécution d'enrichissement personnalisé"""
        # Logique d'exécution personnalisée
        result = {
            "enriched_query": query,
            "method_chosen": "custom",
            "additional_keywords": [],
            "context_analysis": {},
            "llm_calls_count": len(custom_modules)
        }
        
        for module in custom_modules:
            if module == "method_choice":
                result["method_chosen"] = await self._simple_method_choice(query)
            elif module == "query_enrichment":
                enrichment = await self._basic_query_enrichment(query)
                result["enriched_query"] = enrichment.get("enriched_query", query)
                result["additional_keywords"] = enrichment.get("additional_keywords", [])
            elif module == "context_analysis":
                result["context_analysis"] = await self._context_analysis(query, {})
        
        return result
    
    def _fallback_method_choice(self, query: str) -> str:
        """Choix de méthode en fallback (sans LLM)"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["grep", "search", "find", "file", "content"]):
            return "grep"
        elif any(word in query_lower for word in ["concept", "relation", "abstract", "memory"]):
            return "fractal"
        elif any(word in query_lower for word in ["time", "history", "recent", "old", "new"]):
            return "temporal"
        else:
            return "mixed"
    
    def get_available_modules(self) -> List[str]:
        """Récupère la liste des modules disponibles"""
        return list(self.enrichment_fragments.keys())
    
    def get_mixed_strategies(self) -> Dict[str, List[str]]:
        """Récupère les stratégies mixed disponibles"""
        return self.mixed_strategies.copy()
    
    def validate_enrichment_config(self, config: Dict[str, Any]) -> bool:
        """Valide une configuration d'enrichissement"""
        if not config.get("enabled", True):
            return True
        
        power = config.get("power", "medium")
        if power not in [e.value for e in EnrichmentPower]:
            return False
        
        modules = config.get("modules", [])
        available_modules = self.get_available_modules()
        
        for module in modules:
            if module not in available_modules:
                return False
        
        return True 