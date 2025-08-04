#!/usr/bin/env python3
"""
⛧ Memory Registry ⛧
Registre dynamique des types de mémoire et outils de navigation pour l'Archiviste

Système d'injection dynamique de contexte mémoire dans les prompts de l'Archiviste.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class MemoryRegistry:
    """Registre dynamique des types de mémoire et outils de navigation."""
    
    def __init__(self, memory_engine):
        self.memory_engine = memory_engine
        self.memory_types = {}
        self.navigation_tools = {}
        self.search_methods = {}
        
        # Initialiser le registre
        self._initialize_registry()
    
    def _initialize_registry(self):
        """Initialise le registre avec tous les types de mémoire et outils."""
        
        # Types de mémoire disponibles
        self.memory_types = {
            "fractal": {
                "name": "Mémoire Fractale",
                "description": "Mémoire profonde avec auto-similarité et liens cross-fractals",
                "capabilities": [
                    "stockage_profond",
                    "liens_transcendance",
                    "liens_immanence", 
                    "navigation_fractale",
                    "auto_similarite"
                ],
                "access_methods": [
                    "find_memories_by_keyword",
                    "find_by_strata", 
                    "traverse_transcendence_path",
                    "traverse_immanence_path",
                    "list_links"
                ],
                "strata": ["somatic", "cognitive", "metaphysical"]
            },
            
            "temporal": {
                "name": "Mémoire Temporelle",
                "description": "Index ultra-léger pour recherche rapide et navigation temporelle",
                "capabilities": [
                    "recherche_rapide",
                    "navigation_temporelle",
                    "index_chronologique",
                    "métadonnées_temporelles"
                ],
                "access_methods": [
                    "search_temporal",
                    "get_temporal_node",
                    "traverse_temporal_chain",
                    "search_by_timeline"
                ],
                "index_types": ["keywords", "strata", "timeline"]
            },
            
            "user_requests": {
                "name": "Mémoire des Requêtes Utilisateur",
                "description": "Stack linéaire des requêtes avec analyse d'intention",
                "capabilities": [
                    "analyse_intention",
                    "priorisation",
                    "historique_interactions",
                    "patterns_usage"
                ],
                "access_methods": [
                    "add_user_request",
                    "search_temporal_requests",
                    "get_temporal_statistics"
                ],
                "states": ["pending", "processed"]
            },
            
            "discussion": {
                "name": "Timeline de Discussion",
                "description": "Timelines de discussion WhatsApp-style par interlocuteur",
                "capabilities": [
                    "recherche_conversation",
                    "export_timeline",
                    "contexte_conversationnel",
                    "historique_messages"
                ],
                "access_methods": [
                    "add_message",
                    "get_timeline",
                    "search_messages",
                    "get_message_context"
                ],
                "directions": ["incoming", "outgoing"]
            }
        }
        
        # Outils de navigation
        self.navigation_tools = {
            "keyword_search": {
                "name": "Recherche par Mots-clés",
                "description": "Recherche dans tous les types de mémoire par mots-clés",
                "methods": {
                    "fractal": "find_memories_by_keyword",
                    "temporal": "search_temporal",
                    "user_requests": "search_temporal_requests"
                }
            },
            
            "strata_navigation": {
                "name": "Navigation par Strates",
                "description": "Navigation dans les strates de conscience (somatic, cognitive, metaphysical)",
                "methods": {
                    "fractal": "find_by_strata",
                    "temporal": "search_temporal"
                }
            },
            
            "temporal_navigation": {
                "name": "Navigation Temporelle",
                "description": "Navigation chronologique dans la mémoire",
                "methods": {
                    "temporal": "traverse_temporal_chain",
                    "user_requests": "get_temporal_statistics"
                }
            },
            
            "fractal_navigation": {
                "name": "Navigation Fractale",
                "description": "Navigation dans les liens de transcendance et immanence",
                "methods": {
                    "fractal": ["traverse_transcendence_path", "traverse_immanence_path"]
                }
            }
        }
        
        # Méthodes de recherche
        self.search_methods = {
            "exact_match": "Recherche exacte par terme",
            "fuzzy_search": "Recherche approximative",
            "semantic_search": "Recherche sémantique",
            "contextual_search": "Recherche contextuelle",
            "temporal_search": "Recherche temporelle",
            "fractal_search": "Recherche dans les liens fractals"
        }
    
    def get_memory_type_info(self, memory_type: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations sur un type de mémoire."""
        return self.memory_types.get(memory_type)
    
    def get_all_memory_types(self) -> Dict[str, Any]:
        """Récupère tous les types de mémoire."""
        return self.memory_types
    
    def get_navigation_tools(self) -> Dict[str, Any]:
        """Récupère tous les outils de navigation."""
        return self.navigation_tools
    
    def get_search_methods(self) -> Dict[str, Any]:
        """Récupère toutes les méthodes de recherche."""
        return self.search_methods
    
    def get_available_access_methods(self, memory_type: str) -> List[str]:
        """Récupère les méthodes d'accès disponibles pour un type de mémoire."""
        memory_info = self.memory_types.get(memory_type)
        if memory_info:
            return memory_info.get("access_methods", [])
        return []
    
    def get_capabilities_for_memory_type(self, memory_type: str) -> List[str]:
        """Récupère les capacités d'un type de mémoire."""
        memory_info = self.memory_types.get(memory_type)
        if memory_info:
            return memory_info.get("capabilities", [])
        return []
    
    def format_for_prompt_injection(self) -> str:
        """Formate le registre pour injection dans les prompts."""
        
        # Format des types de mémoire
        memory_types_text = []
        for type_id, info in self.memory_types.items():
            capabilities = ", ".join(info["capabilities"])
            access_methods = ", ".join(info["access_methods"])
            
            memory_types_text.append(f"""
### **{info['name']} ({type_id})**
- **Description :** {info['description']}
- **Capacités :** {capabilities}
- **Méthodes d'accès :** {access_methods}
""")
        
        # Format des outils de navigation
        navigation_tools_text = []
        for tool_id, info in self.navigation_tools.items():
            methods = []
            for memory_type, method in info["methods"].items():
                if isinstance(method, list):
                    methods.append(f"{memory_type}: {', '.join(method)}")
                else:
                    methods.append(f"{memory_type}: {method}")
            
            navigation_tools_text.append(f"""
### **{info['name']} ({tool_id})**
- **Description :** {info['description']}
- **Méthodes :** {' | '.join(methods)}
""")
        
        # Format des méthodes de recherche
        search_methods_text = []
        for method_id, description in self.search_methods.items():
            search_methods_text.append(f"- **{method_id}** : {description}")
        
        return f"""
## 🗂️ **TYPES DE MÉMOIRE DISPONIBLES**

{''.join(memory_types_text)}

## 🧭 **OUTILS DE NAVIGATION**

{''.join(navigation_tools_text)}

## 🔍 **MÉTHODES DE RECHERCHE**

{chr(10).join(search_methods_text)}

## 📋 **MÉTHODES D'ACCÈS PAR TYPE**

{self._format_access_methods_table()}
"""
    
    def _format_access_methods_table(self) -> str:
        """Formate un tableau des méthodes d'accès par type."""
        table = []
        table.append("| Type | Méthodes d'Accès |")
        table.append("|------|------------------|")
        
        for type_id, info in self.memory_types.items():
            methods = ", ".join(info["access_methods"])
            table.append(f"| {type_id} | {methods} |")
        
        return "\n".join(table)
    
    def get_context_for_query(self, query_type: str, memory_type: str = None) -> str:
        """Génère un contexte spécifique pour un type de requête."""
        
        if query_type == "describe_memory_types":
            return self.format_for_prompt_injection()
        
        elif query_type == "contextual_search":
            if memory_type:
                memory_info = self.memory_types.get(memory_type)
                if memory_info:
                    return f"""
**TYPE DE MÉMOIRE CIBLÉ :** {memory_info['name']}
**CAPACITÉS :** {', '.join(memory_info['capabilities'])}
**MÉTHODES D'ACCÈS :** {', '.join(memory_info['access_methods'])}
"""
            return self.format_for_prompt_injection()
        
        elif query_type == "explore_workspace":
            return f"""
**OUTILS DE NAVIGATION DISPONIBLES :**
{self._format_navigation_tools_for_exploration()}
"""
        
        else:
            return self.format_for_prompt_injection()
    
    def _format_navigation_tools_for_exploration(self) -> str:
        """Formate les outils de navigation pour l'exploration."""
        tools_text = []
        for tool_id, info in self.navigation_tools.items():
            tools_text.append(f"- **{info['name']}** : {info['description']}")
        return "\n".join(tools_text)
    
    def get_available_tools_summary(self) -> str:
        """Retourne un résumé des outils disponibles."""
        return f"""
**RÉSUMÉ DES OUTILS DISPONIBLES :**
- **Types de mémoire :** {len(self.memory_types)} types
- **Outils de navigation :** {len(self.navigation_tools)} outils  
- **Méthodes de recherche :** {len(self.search_methods)} méthodes
"""


# Instance globale
_global_memory_registry: Optional[MemoryRegistry] = None

def initialize_memory_registry(memory_engine) -> MemoryRegistry:
    """Initialise le registre global de mémoire."""
    global _global_memory_registry
    if _global_memory_registry is None:
        _global_memory_registry = MemoryRegistry(memory_engine)
    return _global_memory_registry

def get_memory_registry() -> MemoryRegistry:
    """Récupère le registre global de mémoire."""
    if _global_memory_registry is None:
        raise RuntimeError("MemoryRegistry non initialisé. Appelez initialize_memory_registry() d'abord.")
    return _global_memory_registry 