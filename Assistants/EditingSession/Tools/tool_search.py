#!/usr/bin/env python3
"""
⛧ Tool Search Engine ⛧
Alma's Intelligent Tool Search

Moteur de recherche intelligent d'outils avec intégration MemoryEngine.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .tool_registry import ToolRegistry


class ToolSearchEngine:
    """Moteur de recherche intelligent d'outils."""
    
    def __init__(self, tool_registry: ToolRegistry):
        self.registry = tool_registry
        self.search_history = []
        
    def search_by_keyword(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Recherche d'outils par mot-clé."""
        results = []
        query_lower = query.lower()
        
        for tool_id, tool_info in self.registry.tools.items():
            lucidoc = tool_info.get("lucidoc", {})
            pacte = lucidoc.get("🜄pacte", {})
            essence = lucidoc.get("🜁essence", {})
            
            score = 0
            match_details = []
            
            # Recherche dans l'intention (score élevé)
            intent = pacte.get("intent", "").lower()
            if query_lower in intent:
                score += 10
                match_details.append(f"Intention: {pacte.get('intent')}")
            
            # Recherche dans les mots-clés (score moyen)
            keywords = essence.get("keywords", [])
            for keyword in keywords:
                if query_lower in keyword.lower():
                    score += 5
                    match_details.append(f"Mot-clé: {keyword}")
            
            # Recherche dans le contexte d'usage (score faible)
            usage_context = essence.get("usage_context", "").lower()
            if query_lower in usage_context:
                score += 2
                match_details.append("Contexte d'usage")
            
            # Recherche dans l'ID de l'outil (score très élevé)
            if query_lower in tool_id.lower():
                score += 15
                match_details.append("ID d'outil")
            
            if score > 0:
                results.append({
                    "tool_id": tool_id,
                    "score": score,
                    "match_details": match_details,
                    "type": pacte.get("type"),
                    "level": pacte.get("level"),
                    "intent": pacte.get("intent"),
                    "keywords": keywords,
                    "source": tool_info.get("source")
                })
        
        # Trier par score décroissant
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Enregistrer la recherche
        self._log_search(query, len(results), results[:limit])
        
        return results[:limit]
    
    def search_by_type(self, tool_type: str) -> List[Dict[str, Any]]:
        """Recherche d'outils par type."""
        results = []
        
        for tool_id, tool_info in self.registry.tools.items():
            lucidoc = tool_info.get("lucidoc", {})
            pacte = lucidoc.get("🜄pacte", {})
            
            if pacte.get("type") == tool_type:
                results.append({
                    "tool_id": tool_id,
                    "type": tool_type,
                    "level": pacte.get("level"),
                    "intent": pacte.get("intent"),
                    "source": tool_info.get("source")
                })
        
        return results
    
    def search_by_level(self, level: str) -> List[Dict[str, Any]]:
        """Recherche d'outils par niveau."""
        results = []
        
        for tool_id, tool_info in self.registry.tools.items():
            lucidoc = tool_info.get("lucidoc", {})
            pacte = lucidoc.get("🜄pacte", {})
            
            if pacte.get("level") == level:
                results.append({
                    "tool_id": tool_id,
                    "type": pacte.get("type"),
                    "level": level,
                    "intent": pacte.get("intent"),
                    "source": tool_info.get("source")
                })
        
        return results
    
    def search_by_intent(self, intent_query: str) -> List[Dict[str, Any]]:
        """Recherche d'outils par intention."""
        results = []
        intent_query_lower = intent_query.lower()
        
        for tool_id, tool_info in self.registry.tools.items():
            lucidoc = tool_info.get("lucidoc", {})
            pacte = lucidoc.get("🜄pacte", {})
            intent = pacte.get("intent", "").lower()
            
            if intent_query_lower in intent:
                results.append({
                    "tool_id": tool_id,
                    "type": pacte.get("type"),
                    "level": pacte.get("level"),
                    "intent": pacte.get("intent"),
                    "source": tool_info.get("source")
                })
        
        return results
    
    def advanced_search(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recherche avancée avec filtres multiples."""
        results = []
        
        for tool_id, tool_info in self.registry.tools.items():
            lucidoc = tool_info.get("lucidoc", {})
            pacte = lucidoc.get("🜄pacte", {})
            essence = lucidoc.get("🜁essence", {})
            
            # Appliquer les filtres
            matches_all_filters = True
            
            # Filtre par type
            if "type" in filters and pacte.get("type") != filters["type"]:
                matches_all_filters = False
            
            # Filtre par niveau
            if "level" in filters and pacte.get("level") != filters["level"]:
                matches_all_filters = False
            
            # Filtre par source
            if "source" in filters and tool_info.get("source") != filters["source"]:
                matches_all_filters = False
            
            # Filtre par mot-clé
            if "keyword" in filters:
                keyword = filters["keyword"].lower()
                intent = pacte.get("intent", "").lower()
                keywords = [kw.lower() for kw in essence.get("keywords", [])]
                
                if (keyword not in intent and 
                    not any(keyword in kw for kw in keywords)):
                    matches_all_filters = False
            
            if matches_all_filters:
                results.append({
                    "tool_id": tool_id,
                    "type": pacte.get("type"),
                    "level": pacte.get("level"),
                    "intent": pacte.get("intent"),
                    "keywords": essence.get("keywords", []),
                    "source": tool_info.get("source")
                })
        
        return results
    
    def get_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """Récupère des suggestions d'outils basées sur une requête partielle."""
        suggestions = []
        partial_lower = partial_query.lower()
        
        for tool_id in self.registry.tools.keys():
            if partial_lower in tool_id.lower():
                suggestions.append(tool_id)
                if len(suggestions) >= limit:
                    break
        
        return suggestions
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques des outils."""
        stats = {
            "total_tools": len(self.registry.tools),
            "by_type": {},
            "by_level": {},
            "by_source": {},
            "tools_with_keywords": 0,
            "tools_with_symbolic_layer": 0
        }
        
        for tool_id, tool_info in self.registry.tools.items():
            lucidoc = tool_info.get("lucidoc", {})
            pacte = lucidoc.get("🜄pacte", {})
            essence = lucidoc.get("🜁essence", {})
            
            # Compter par type
            tool_type = pacte.get("type", "unknown")
            stats["by_type"][tool_type] = stats["by_type"].get(tool_type, 0) + 1
            
            # Compter par niveau
            level = pacte.get("level", "unknown")
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
            
            # Compter par source
            source = tool_info.get("source", "unknown")
            stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
            
            # Compter les outils avec mots-clés
            if essence.get("keywords"):
                stats["tools_with_keywords"] += 1
            
            # Compter les outils avec couche symbolique
            if essence.get("symbolic_layer"):
                stats["tools_with_symbolic_layer"] += 1
        
        return stats
    
    def _log_search(self, query: str, total_results: int, 
                   top_results: List[Dict[str, Any]]) -> None:
        """Enregistre une recherche dans l'historique."""
        search_record = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "total_results": total_results,
            "top_results": [result["tool_id"] for result in top_results[:3]]
        }
        
        self.search_history.append(search_record)
        
        # Limiter l'historique à 100 recherches
        if len(self.search_history) > 100:
            self.search_history = self.search_history[-100:]
    
    def get_search_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Récupère l'historique des recherches."""
        return self.search_history[-limit:] if limit > 0 else self.search_history 