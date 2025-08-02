#!/usr/bin/env python3
"""
⛧ Tool Invoker ⛧
Alma's Tool Execution Engine

Moteur d'exécution d'outils avec intégration MemoryEngine et support OpenAI Agents SDK.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import json
import traceback
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

from .tool_registry import ToolRegistry


class ToolInvoker:
    """Moteur d'invocation d'outils avec gestion d'erreurs et logging."""
    
    def __init__(self, tool_registry: ToolRegistry):
        self.registry = tool_registry
        self.execution_history = []
        
    def invoke_tool(self, tool_id: str, **kwargs) -> Dict[str, Any]:
        """Invoque un outil avec gestion d'erreurs complète."""
        
        execution_record = {
            "tool_id": tool_id,
            "arguments": kwargs,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "result": None,
            "error": None,
            "execution_time": None
        }
        
        start_time = datetime.now()
        
        try:
            # Récupérer l'outil
            tool_info = self.registry.get_tool(tool_id)
            if not tool_info:
                raise ValueError(f"Outil '{tool_id}' non trouvé dans le registre")
            
            # Vérifier les paramètres requis
            lucidoc = tool_info.get("lucidoc", {})
            invocation = lucidoc.get("🜂invocation", {})
            required_params = invocation.get("requires", [])
            
            missing_params = [param for param in required_params if param not in kwargs]
            if missing_params:
                raise ValueError(f"Paramètres requis manquants: {missing_params}")
            
            # Exécuter l'outil
            tool_function = tool_info["function"]
            result = tool_function(**kwargs)
            
            # Enregistrer le succès
            execution_record.update({
                "success": True,
                "result": result,
                "execution_time": (datetime.now() - start_time).total_seconds()
            })
            
            # Stocker dans MemoryEngine si disponible
            self._store_execution_in_memory(execution_record)
            
        except Exception as e:
            # Enregistrer l'erreur
            execution_record.update({
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "execution_time": (datetime.now() - start_time).total_seconds()
            })
            
            print(f"❌ Erreur d'exécution de {tool_id}: {e}")
        
        # Ajouter à l'historique
        self.execution_history.append(execution_record)
        
        return execution_record
    
    def _store_execution_in_memory(self, execution_record: Dict[str, Any]) -> None:
        """Stocke l'exécution dans MemoryEngine."""
        try:
            memory_engine = self.registry.memory_engine
            
            # Créer un résumé de l'exécution
            summary = f"""
            Exécution d'outil: {execution_record['tool_id']}
            Succès: {execution_record['success']}
            Temps d'exécution: {execution_record['execution_time']}s
            Arguments: {json.dumps(execution_record['arguments'], indent=2)}
            """
            
            if execution_record['success']:
                summary += f"\nRésultat: {str(execution_record['result'])[:200]}..."
            else:
                summary += f"\nErreur: {execution_record['error']}"
            
            # Stocker dans la mémoire
            memory_engine.store(
                content=summary,
                metadata={
                    "type": "tool_execution",
                    "tool_id": execution_record['tool_id'],
                    "success": execution_record['success'],
                    "execution_time": execution_record['execution_time'],
                    "timestamp": execution_record['timestamp']
                },
                strata="cognitive"
            )
            
        except Exception as e:
            print(f"⚠️  Impossible de stocker l'exécution en mémoire: {e}")
    
    def invoke_tool_for_openai(self, tool_id: str, arguments_json: str) -> Dict[str, Any]:
        """Invoque un outil depuis OpenAI Agents SDK."""
        try:
            # Parser les arguments JSON
            if arguments_json:
                kwargs = json.loads(arguments_json)
                if not isinstance(kwargs, dict):
                    raise ValueError("Les arguments doivent être un objet JSON")
            else:
                kwargs = {}
            
            # Exécuter l'outil
            result = self.invoke_tool(tool_id, **kwargs)
            
            # Formater la réponse pour OpenAI
            if result['success']:
                return {
                    "success": True,
                    "result": result['result'],
                    "execution_time": result['execution_time']
                }
            else:
                return {
                    "success": False,
                    "error": result['error'],
                    "execution_time": result['execution_time']
                }
                
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Erreur de parsing JSON: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur d'invocation: {e}"
            }
    
    def get_execution_history(self, tool_id: Optional[str] = None, 
                             limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère l'historique d'exécution."""
        history = self.execution_history
        
        if tool_id:
            history = [record for record in history if record['tool_id'] == tool_id]
        
        return history[-limit:] if limit > 0 else history
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques d'usage des outils."""
        stats = {
            "total_executions": len(self.execution_history),
            "successful_executions": 0,
            "failed_executions": 0,
            "tools_used": {},
            "average_execution_time": 0.0,
            "most_used_tools": []
        }
        
        if not self.execution_history:
            return stats
        
        execution_times = []
        
        for record in self.execution_history:
            if record['success']:
                stats['successful_executions'] += 1
            else:
                stats['failed_executions'] += 1
            
            tool_id = record['tool_id']
            stats['tools_used'][tool_id] = stats['tools_used'].get(tool_id, 0) + 1
            
            if record['execution_time']:
                execution_times.append(record['execution_time'])
        
        # Calculer les moyennes
        if execution_times:
            stats['average_execution_time'] = sum(execution_times) / len(execution_times)
        
        # Outils les plus utilisés
        sorted_tools = sorted(stats['tools_used'].items(), 
                            key=lambda x: x[1], reverse=True)
        stats['most_used_tools'] = sorted_tools[:10]
        
        return stats 