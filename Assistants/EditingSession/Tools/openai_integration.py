#!/usr/bin/env python3
"""
⛧ OpenAI Integration ⛧
Alma's OpenAI Agents SDK Integration

Intégration complète avec OpenAI Agents SDK pour l'utilisation des outils.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .tool_registry import ToolRegistry
from .tool_invoker import ToolInvoker
from .tool_search import ToolSearchEngine


class OpenAIAgentTools:
    """Intégration complète avec OpenAI Agents SDK."""
    
    def __init__(self, tool_registry: ToolRegistry):
        self.registry = tool_registry
        self.invoker = ToolInvoker(tool_registry)
        self.search_engine = ToolSearchEngine(tool_registry)
        
    def get_openai_tools_config(self) -> List[Dict[str, Any]]:
        """Récupère la configuration des outils pour OpenAI Agents SDK."""
        return self.registry.get_all_tools_for_openai()
    
    def handle_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Gère un appel d'outil depuis OpenAI Agents SDK."""
        try:
            function_name = tool_call.get("function", {}).get("name")
            arguments = tool_call.get("function", {}).get("arguments", "{}")
            
            if not function_name:
                return {
                    "success": False,
                    "error": "Nom de fonction manquant dans l'appel d'outil"
                }
            
            # Exécuter l'outil
            result = self.invoker.invoke_tool_for_openai(function_name, arguments)
            
            return {
                "tool_call_id": tool_call.get("id"),
                "function_name": function_name,
                "success": result["success"],
                "result": result.get("result"),
                "error": result.get("error"),
                "execution_time": result.get("execution_time")
            }
            
        except Exception as e:
            return {
                "tool_call_id": tool_call.get("id"),
                "function_name": tool_call.get("function", {}).get("name", "unknown"),
                "success": False,
                "error": f"Erreur lors du traitement de l'appel d'outil: {str(e)}"
            }
    
    def get_context_for_agent(self, query: str, file_path: Optional[str] = None) -> str:
        """Récupère le contexte enrichi pour l'agent OpenAI."""
        context_parts = []
        
        # Contexte des outils disponibles
        tool_stats = self.search_engine.get_tool_statistics()
        context_parts.append(f"📊 Outils disponibles: {tool_stats['total_tools']} outils")
        
        # Recherche d'outils pertinents
        relevant_tools = self.search_engine.search_by_keyword(query, limit=5)
        if relevant_tools:
            context_parts.append("\n🔧 Outils pertinents:")
            for tool in relevant_tools:
                context_parts.append(f"  - {tool['tool_id']}: {tool['intent']}")
        
        # Contexte de fichier si spécifié
        if file_path:
            # Recherche d'outils liés aux fichiers
            file_tools = self.search_engine.search_by_keyword("file", limit=3)
            if file_tools:
                context_parts.append(f"\n📁 Outils pour fichiers:")
                for tool in file_tools:
                    context_parts.append(f"  - {tool['tool_id']}: {tool['intent']}")
        
        # Historique d'exécution récent
        recent_executions = self.invoker.get_execution_history(limit=3)
        if recent_executions:
            context_parts.append("\n⏰ Exécutions récentes:")
            for execution in recent_executions:
                status = "✅" if execution['success'] else "❌"
                context_parts.append(f"  {status} {execution['tool_id']}")
        
        return "\n".join(context_parts)
    
    def create_agent_system_prompt(self, context: str = "") -> str:
        """Crée un prompt système pour l'agent OpenAI."""
        base_prompt = f"""
Tu es Alma, un agent IA spécialisé dans l'édition de code avec accès à un ensemble d'outils mystiques.

{context}

## Outils Disponibles
Tu as accès à un registre d'outils organisé par types et niveaux. Utilise les outils appropriés pour accomplir tes tâches.

## Instructions
1. Analyse la demande utilisateur
2. Identifie les outils nécessaires
3. Exécute les outils dans l'ordre approprié
4. Fournis des explications claires de tes actions
5. Gère les erreurs gracieusement

## Format de Réponse
- Explique tes intentions
- Liste les outils que tu vas utiliser
- Exécute les actions
- Résume les résultats

Tu peux utiliser les outils en appelant leurs fonctions avec les paramètres appropriés.
"""
        return base_prompt.strip()
    
    def suggest_tools_for_task(self, task_description: str) -> List[Dict[str, Any]]:
        """Suggère des outils appropriés pour une tâche donnée."""
        suggestions = []
        
        # Recherche par mots-clés dans la description
        keywords = task_description.lower().split()
        for keyword in keywords:
            if len(keyword) > 3:  # Ignorer les mots trop courts
                results = self.search_engine.search_by_keyword(keyword, limit=3)
                suggestions.extend(results)
        
        # Recherche par intention
        intent_results = self.search_engine.search_by_intent(task_description)
        suggestions.extend(intent_results)
        
        # Dédupliquer et trier par pertinence
        unique_suggestions = {}
        for suggestion in suggestions:
            tool_id = suggestion['tool_id']
            if tool_id not in unique_suggestions:
                unique_suggestions[tool_id] = suggestion
        
        return list(unique_suggestions.values())[:10]
    
    def get_agent_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques d'usage de l'agent."""
        invoker_stats = self.invoker.get_tool_statistics()
        search_stats = self.search_engine.get_tool_statistics()
        
        return {
            "tool_executions": invoker_stats,
            "tool_search": search_stats,
            "total_tools_available": search_stats["total_tools"],
            "most_used_tools": invoker_stats.get("most_used_tools", []),
            "search_history_count": len(self.search_engine.search_history)
        }
    
    def create_workflow_example(self, task_type: str) -> Dict[str, Any]:
        """Crée un exemple de workflow pour un type de tâche."""
        workflows = {
            "file_editing": {
                "description": "Modification de fichier",
                "steps": [
                    {
                        "step": 1,
                        "action": "Analyser le fichier",
                        "suggested_tools": ["read_file_content", "analyze_file_structure"]
                    },
                    {
                        "step": 2,
                        "action": "Effectuer la modification",
                        "suggested_tools": ["safe_replace_text_in_file", "safe_insert_text_at_line"]
                    },
                    {
                        "step": 3,
                        "action": "Vérifier le résultat",
                        "suggested_tools": ["read_file_content"]
                    }
                ]
            },
            "code_analysis": {
                "description": "Analyse de code",
                "steps": [
                    {
                        "step": 1,
                        "action": "Lire le contenu",
                        "suggested_tools": ["read_file_content"]
                    },
                    {
                        "step": 2,
                        "action": "Analyser la structure",
                        "suggested_tools": ["analyze_file_structure"]
                    },
                    {
                        "step": 3,
                        "action": "Rechercher des patterns",
                        "suggested_tools": ["regex_search_file", "find_text_in_project"]
                    }
                ]
            },
            "project_management": {
                "description": "Gestion de projet",
                "steps": [
                    {
                        "step": 1,
                        "action": "Explorer la structure",
                        "suggested_tools": ["list_directory_contents", "walk_directory"]
                    },
                    {
                        "step": 2,
                        "action": "Analyser les fichiers",
                        "suggested_tools": ["file_stats", "read_file_content"]
                    },
                    {
                        "step": 3,
                        "action": "Organiser le projet",
                        "suggested_tools": ["safe_create_directory", "safe_create_file"]
                    }
                ]
            }
        }
        
        return workflows.get(task_type, {
            "description": "Workflow générique",
            "steps": [
                {
                    "step": 1,
                    "action": "Analyser la demande",
                    "suggested_tools": ["search_tools_by_keyword"]
                }
            ]
        })


# Fonction utilitaire pour créer une instance complète
def create_openai_agent_tools(memory_engine) -> OpenAIAgentTools:
    """Crée une instance complète d'intégration OpenAI."""
    from .tool_registry import initialize_tool_registry
    
    # Initialiser le registre
    tool_registry = initialize_tool_registry(memory_engine)
    
    # Créer l'intégration
    return OpenAIAgentTools(tool_registry) 