#!/usr/bin/env python3
"""
⛧ V10 Assistant - Assistant Principal ⛧
Alma's Main Multi-Agent Assistant for V10

Assistant principal V10 qui orchestre les agents spécialisés.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from .temporal_integration import V10TemporalIntegration
from .dev_agent import V10DevAgent
from .tool_agent import V10ToolAgent


@dataclass
class V10Response:
    """Réponse de l'Assistant V10."""
    success: bool
    message: str
    data: Dict[str, Any]
    execution_time: float
    session_id: str
    agent_used: str


class V10Assistant:
    """Assistant principal V10 avec orchestration multi-agents."""
    
    def __init__(self):
        """Initialise l'Assistant V10."""
        self.temporal_integration = V10TemporalIntegration()
        self.dev_agent = V10DevAgent(self.temporal_integration)
        self.tool_agent = V10ToolAgent(self.temporal_integration)
        self.session_id = None
        self.user_id = None
    
    async def initialize(self, user_id: str) -> bool:
        """Initialise l'assistant pour un utilisateur."""
        try:
            self.user_id = user_id
            await self.dev_agent.initialize_session(user_id)
            self.session_id = self.dev_agent.session_id
            
            print(f"✅ Assistant V10 initialisé pour {user_id}")
            print(f"📝 Session ID: {self.session_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur initialisation Assistant V10: {e}")
            return False
    
    async def handle_request(self, user_request: str) -> V10Response:
        """Gère une requête utilisateur complète."""
        
        start_time = datetime.now()
        
        try:
            # 1. Enregistrement de la requête
            await self.temporal_integration.create_temporal_node(
                content=f"User Request: {user_request}",
                metadata={
                    "user_id": self.user_id,
                    "request": user_request,
                    "timestamp": start_time.isoformat(),
                    "assistant": "V10"
                },
                session_id=self.session_id
            )
            
            # 2. Analyse par Dev Agent
            print("🔍 Dev Agent: Analyse de la tâche...")
            task_analysis = await self.dev_agent.analyze_task(user_request)
            
            # 3. Création du plan d'exécution
            print("📋 Dev Agent: Création du plan...")
            execution_plan = await self.dev_agent.create_execution_plan(task_analysis)
            
            # 4. Exécution par Tool Agent
            print("⚙️ Tool Agent: Exécution des outils...")
            execution_results = await self.dev_agent.execute_plan(execution_plan)
            
            # 5. Synthèse des résultats
            print("📊 Dev Agent: Synthèse des résultats...")
            synthesis = await self.dev_agent.synthesize_results(execution_results.results)
            
            # 6. Création de la réponse
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            response = V10Response(
                success=execution_results.success,
                message=self._create_response_message(synthesis, execution_results),
                data={
                    "synthesis": synthesis,
                    "execution_results": execution_results.results,
                    "task_analysis": {
                        "task_type": task_analysis.task_type,
                        "complexity": task_analysis.estimated_complexity
                    },
                    "plan": {
                        "task_id": execution_plan.task_id,
                        "steps_count": len(execution_plan.steps)
                    }
                },
                execution_time=execution_time,
                session_id=self.session_id,
                agent_used="multi_agent"
            )
            
            # 7. Enregistrement de la réponse
            await self.temporal_integration.create_temporal_node(
                content=f"V10 Response: {response.success}",
                metadata={
                    "success": response.success,
                    "execution_time": execution_time,
                    "agent_used": response.agent_used,
                    "assistant": "V10"
                },
                session_id=self.session_id
            )
            
            print(f"✅ Assistant V10: Réponse générée en {execution_time:.2f}s")
            return response
            
        except Exception as e:
            # Gestion d'erreur globale
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            error_response = V10Response(
                success=False,
                message=f"Erreur lors du traitement: {str(e)}",
                data={"error": str(e)},
                execution_time=execution_time,
                session_id=self.session_id,
                agent_used="error_handler"
            )
            
            # Enregistrement de l'erreur
            await self.temporal_integration.create_temporal_node(
                content=f"V10 Error: {str(e)}",
                metadata={
                    "error": str(e),
                    "execution_time": execution_time,
                    "assistant": "V10"
                },
                session_id=self.session_id
            )
            
            print(f"❌ Assistant V10: Erreur après {execution_time:.2f}s")
            return error_response
    
    def _create_response_message(self, synthesis: Dict[str, Any], execution_results: Any) -> str:
        """Crée un message de réponse basé sur la synthèse."""
        success_rate = synthesis.get('success_rate', 0)
        total_results = synthesis.get('total_results', 0)
        successful_results = synthesis.get('successful_results', 0)
        
        if success_rate == 1.0:
            return f"✅ Toutes les opérations ont réussi ({total_results} opérations)"
        elif success_rate > 0.5:
            return f"⚠️ La plupart des opérations ont réussi ({successful_results}/{total_results})"
        elif success_rate > 0:
            return f"❌ Quelques opérations ont réussi ({successful_results}/{total_results})"
        else:
            return f"❌ Aucune opération n'a réussi ({total_results} échecs)"
    
    async def get_session_info(self) -> Dict[str, Any]:
        """Récupère les informations de session."""
        if not self.session_id:
            return {"error": "Session non initialisée"}
        
        session_stats = self.temporal_integration.get_session_stats()
        tool_stats = self.tool_agent.get_tool_statistics()
        
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "session_stats": session_stats,
            "tool_stats": tool_stats,
            "assistant_version": "V10"
        }
    
    async def cleanup_session(self) -> bool:
        """Nettoie la session actuelle."""
        try:
            if self.session_id:
                # Nettoyage des sessions expirées
                expired_count = await self.temporal_integration.cleanup_expired_sessions()
                print(f"🧹 {expired_count} sessions expirées nettoyées")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur nettoyage session: {e}")
            return False
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de performance."""
        session_info = await self.get_session_info()
        
        return {
            "session_info": session_info,
            "temporal_engine_available": session_info.get("session_stats", {}).get("temporal_engine_available", False),
            "active_sessions": session_info.get("session_stats", {}).get("active_sessions", 0),
            "local_tools": session_info.get("tool_stats", {}).get("local_tools_count", 0),
            "mcp_tools": session_info.get("tool_stats", {}).get("mcp_tools_count", 0)
        }


# Interface simplifiée pour utilisation directe
async def create_v10_assistant(user_id: str) -> V10Assistant:
    """Crée et initialise un Assistant V10."""
    assistant = V10Assistant()
    success = await assistant.initialize(user_id)
    
    if not success:
        raise RuntimeError("Échec de l'initialisation de l'Assistant V10")
    
    return assistant


async def handle_v10_request(assistant: V10Assistant, user_request: str) -> V10Response:
    """Gère une requête avec l'Assistant V10."""
    return await assistant.handle_request(user_request)


# Exemple d'utilisation
async def main():
    """Exemple d'utilisation de l'Assistant V10."""
    try:
        # Création de l'assistant
        assistant = await create_v10_assistant("user_123")
        
        # Exemple de requête
        response = await handle_v10_request(
            assistant,
            "Analyse le fichier main.py et liste les imports"
        )
        
        print(f"Réponse: {response.message}")
        print(f"Succès: {response.success}")
        print(f"Temps d'exécution: {response.execution_time:.2f}s")
        
        # Nettoyage
        await assistant.cleanup_session()
        
    except Exception as e:
        print(f"Erreur: {e}")


if __name__ == "__main__":
    asyncio.run(main())
