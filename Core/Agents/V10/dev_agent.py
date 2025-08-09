#!/usr/bin/env python3
"""
⛧ V10 Dev Agent ⛧
Alma's Developer Agent for V10

Agent spécialisé dans le raisonnement métier et la logique de développement.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from .temporal_integration import V10TemporalIntegration
from .llm_provider_decorator import mock_llm_provider, mock_configurator

# LLM provider DI and feature flags
try:
    from Core.Config.feature_flags import get_llm_mode
except Exception:
    def get_llm_mode() -> str:
        return "mock"

try:
    from Core.Providers.LLMProviders.provider_factory import ProviderFactory
except Exception:
    ProviderFactory = None  # Sera testé à l'usage


@dataclass
class TaskAnalysis:
    """Analyse d'une tâche utilisateur."""
    task_type: str
    required_tools: List[str]
    execution_steps: List[Dict[str, Any]]
    estimated_complexity: int
    priority: str = "normal"


@dataclass
class TaskPlan:
    """Plan d'exécution d'une tâche."""
    task_id: str
    steps: List[Dict[str, Any]]
    estimated_duration: float
    dependencies: List[str]
    fallback_plan: Optional[List[Dict[str, Any]]] = None


@dataclass
class ExecutionResult:
    """Résultat d'exécution d'une tâche."""
    success: bool
    results: List[Dict[str, Any]]
    execution_time: float
    errors: List[str]
    metadata: Dict[str, Any]


class V10DevAgent:
    """Agent spécialisé dans le raisonnement métier et la logique de développement."""
    
    def __init__(self, temporal_integration: V10TemporalIntegration, llm_provider: Any = None):
        """Initialise l'agent développeur."""
        self.temporal_integration = temporal_integration
        self.context_manager = V10ContextManager()
        self.planning_engine = V10PlanningEngine()
        self.session_id = None
        # LLM wiring
        self._llm_mode = get_llm_mode()
        self.llm_provider = llm_provider
        self._llm_ready = llm_provider is not None
    
    async def initialize_session(self, user_id: str) -> None:
        """Initialise une session pour l'utilisateur."""
        session = await self.temporal_integration.initialize_session(user_id)
        self.session_id = session.session_id
        print(f"✅ Session Dev Agent initialisée: {self.session_id}")

    async def _ensure_llm_provider(self) -> None:
        """Crée et valide un provider LLM si mode réel et pas encore prêt."""
        if self._llm_ready or self._llm_mode == "mock":
            return
        if ProviderFactory is None:
            print("⚠️ ProviderFactory indisponible - mode réel impossible, fallback mock")
            self._llm_mode = "mock"
            return
        try:
            # Map mode → provider_type factory
            provider_type = {
                "openai": "openai",
                "local_http": "local",
                "local_subprocess": "local_subprocess",
            }.get(self._llm_mode, "local")
            # Config de base minimale
            default_cfg = ProviderFactory.create_default_config(provider_type)
            self.llm_provider, validation = await ProviderFactory.create_and_validate_provider(provider_type, **default_cfg)
            if not validation.valid:
                print(f"⚠️ Validation provider échouée: {validation.error} ({validation.provider_type}) - fallback mock")
                self.llm_provider = None
                self._llm_mode = "mock"
                return
            self._llm_ready = True
            print(f"✅ Provider LLM prêt: {validation.provider_type.value}")
        except Exception as e:
            print(f"⚠️ Erreur création provider LLM ({self._llm_mode}): {e} - fallback mock")
            self.llm_provider = None
            self._llm_mode = "mock"
    
    @mock_llm_provider
    async def analyze_task(self, user_request: str, prompt: str = "", model: str = "gpt-4", temperature: float = 0.7) -> TaskAnalysis:
        """Analyse la tâche utilisateur et crée un plan d'action."""
        
        # Enregistrement de la requête
        await self.temporal_integration.create_temporal_node(
            content=f"User Request: {user_request}",
            metadata={
                "request_type": "user_task",
                "timestamp": datetime.now().isoformat(),
                "agent": "dev_agent"
            },
            session_id=self.session_id
        )
        
        # Analyse contextuelle avec mémoire temporelle
        context = await self.temporal_integration.get_relevant_context(
            user_request, self.session_id
        )

        # Optionnel: appel LLM réel pour enrichir l'analyse (si disponible)
        await self._ensure_llm_provider()
        if self.llm_provider is not None and self._llm_mode != "mock":
            try:
                llm_prompt = prompt or f"""
Tu es un agent développeur. Analyse la requête suivante et propose un type de tâche, une complexité estimée (1-3) et une liste d'outils nécessaires (parmi: read_file, write_file, list_directory, code_analyzer, import_analyzer, execute_command).
REQUÊTE: {user_request}
CONTEXTE: {context}
"""
                resp = await self.llm_provider.generate_text(llm_prompt, max_tokens=256)
                # Pour l’instant, on n’exige pas de parsing strict; trace seulement
                await self.temporal_integration.create_temporal_node(
                    content="LLM Enrichment (analyze_task)",
                    metadata={"provider": "real", "excerpt": getattr(resp, 'content', '')[:200]},
                    session_id=self.session_id
                )
            except Exception as e:
                await self.temporal_integration.create_temporal_node(
                    content="LLM Enrichment Error (analyze_task)",
                    metadata={"error": str(e)},
                    session_id=self.session_id
                )
        
        # Planification des actions
        plan = await self.planning_engine.create_plan(user_request, context)
        
        # Création de l'analyse de tâche
        task_analysis = TaskAnalysis(
            task_type=plan.task_type,
            required_tools=plan.required_tools,
            execution_steps=plan.steps,
            estimated_complexity=plan.complexity
        )
        
        # Enregistrement de l'analyse
        await self.temporal_integration.create_temporal_node(
            content=f"Task Analysis: {task_analysis.task_type}",
            metadata={
                "task_type": task_analysis.task_type,
                "required_tools": task_analysis.required_tools,
                "complexity": task_analysis.estimated_complexity,
                "agent": "dev_agent"
            },
            session_id=self.session_id
        )
        
        return task_analysis
    
    @mock_llm_provider
    async def create_execution_plan(self, task_analysis: TaskAnalysis, prompt: str = "", model: str = "gpt-4", temperature: float = 0.7) -> TaskPlan:
        """Crée un plan d'exécution détaillé."""
        
        plan = await self.planning_engine.create_execution_plan(task_analysis)

        # Optionnel: appel LLM réel pour ajuster le plan (trace uniquement pour l’instant)
        await self._ensure_llm_provider()
        if self.llm_provider is not None and self._llm_mode != "mock":
            try:
                llm_prompt = prompt or f"Refine this plan steps for: {task_analysis.task_type}."
                resp = await self.llm_provider.generate_text(llm_prompt, max_tokens=200)
                await self.temporal_integration.create_temporal_node(
                    content="LLM Enrichment (create_execution_plan)",
                    metadata={"provider": "real", "excerpt": getattr(resp, 'content', '')[:200]},
                    session_id=self.session_id
                )
            except Exception as e:
                await self.temporal_integration.create_temporal_node(
                    content="LLM Enrichment Error (create_execution_plan)",
                    metadata={"error": str(e)},
                    session_id=self.session_id
                )
        
        # Enregistrement du plan
        await self.temporal_integration.create_temporal_node(
            content=f"Execution Plan: {plan.task_id}",
            metadata={
                "task_id": plan.task_id,
                "steps_count": len(plan.steps),
                "estimated_duration": plan.estimated_duration,
                "agent": "dev_agent"
            },
            session_id=self.session_id
        )
        
        return plan
    
    async def execute_plan(self, plan: TaskPlan) -> ExecutionResult:
        """Exécute le plan via le Tool Agent."""
        
        start_time = datetime.now()
        results = []
        errors = []
        
        # Enregistrement du début d'exécution
        execution_node_id = await self.temporal_integration.create_temporal_node(
            content=f"Plan Execution Started: {plan.task_id}",
            metadata={
                "task_id": plan.task_id,
                "start_time": start_time.isoformat(),
                "agent": "dev_agent"
            },
            session_id=self.session_id
        )
        
        try:
            # Import dynamique pour éviter les dépendances circulaires
            from .tool_agent import V10ToolAgent
            tool_agent = V10ToolAgent(self.temporal_integration)
            
            for i, step in enumerate(plan.steps):
                try:
                    # Enregistrement de l'étape
                    step_node_id = await self.temporal_integration.create_temporal_node(
                        content=f"Executing Step {i+1}: {step.get('tool_name', 'unknown')}",
                        metadata={
                            "step_index": i,
                            "step_data": step,
                            "agent": "dev_agent"
                        },
                        session_id=self.session_id
                    )
                    
                    # Exécution de l'étape
                    result = await tool_agent.execute_tool(
                        step.get('tool_name'),
                        step.get('parameters', {}),
                        self.session_id
                    )
                    
                    results.append(result)
                    
                    # Lien temporel entre l'étape et son résultat
                    if step_node_id and result.get('node_id'):
                        await self.temporal_integration.create_temporal_link(
                            step_node_id, result['node_id'], "step_result", self.session_id
                        )
                    
                    # Vérification de la réussite
                    if not result.get('success', False):
                        errors.append(f"Step {i+1} failed: {result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    error_msg = f"Step {i+1} exception: {str(e)}"
                    errors.append(error_msg)
                    results.append({"success": False, "error": error_msg})
            
            # Enregistrement de la fin d'exécution
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            await self.temporal_integration.create_temporal_node(
                content=f"Plan Execution Completed: {plan.task_id}",
                metadata={
                    "task_id": plan.task_id,
                    "end_time": end_time.isoformat(),
                    "execution_time": execution_time,
                    "success_count": len([r for r in results if r.get('success', False)]),
                    "error_count": len(errors),
                    "agent": "dev_agent"
                },
                session_id=self.session_id
            )
            
            return ExecutionResult(
                success=len(errors) == 0,
                results=results,
                execution_time=execution_time,
                errors=errors,
                metadata={
                    "task_id": plan.task_id,
                    "total_steps": len(plan.steps),
                    "successful_steps": len([r for r in results if r.get('success', False)])
                }
            )
            
        except Exception as e:
            # Gestion d'erreur globale
            error_msg = f"Plan execution failed: {str(e)}"
            errors.append(error_msg)
            
            await self.temporal_integration.create_temporal_node(
                content=f"Plan Execution Failed: {plan.task_id}",
                metadata={
                    "task_id": plan.task_id,
                    "error": error_msg,
                    "agent": "dev_agent"
                },
                session_id=self.session_id
            )
            
            return ExecutionResult(
                success=False,
                results=results,
                execution_time=(datetime.now() - start_time).total_seconds(),
                errors=errors,
                metadata={"task_id": plan.task_id}
            )
    
    @mock_llm_provider
    async def synthesize_results(self, results: List[Dict[str, Any]], prompt: str = "", model: str = "gpt-4", temperature: float = 0.7) -> Dict[str, Any]:
        """Synthétise les résultats d'exécution."""
        
        # Analyse des résultats
        successful_results = [r for r in results if r.get('success', False)]
        failed_results = [r for r in results if not r.get('success', False)]
        
        # Création de la synthèse
        synthesis = {
            "total_results": len(results),
            "successful_results": len(successful_results),
            "failed_results": len(failed_results),
            "success_rate": len(successful_results) / len(results) if results else 0,
            "summary": self._create_summary(successful_results, failed_results),
            "recommendations": self._generate_recommendations(results)
        }
        
        # Enregistrement de la synthèse
        await self.temporal_integration.create_temporal_node(
            content=f"Results Synthesis: {synthesis['success_rate']:.2%} success rate",
            metadata={
                "synthesis": synthesis,
                "agent": "dev_agent"
            },
            session_id=self.session_id
        )

        # Optionnel: LLM réel pour produire un résumé textuel riche
        await self._ensure_llm_provider()
        if self.llm_provider is not None and self._llm_mode != "mock":
            try:
                llm_prompt = prompt or f"Synthétise en 3 phrases clés ces résultats: {synthesis}"
                resp = await self.llm_provider.generate_text(llm_prompt, max_tokens=180)
                await self.temporal_integration.create_temporal_node(
                    content="LLM Enrichment (synthesize_results)",
                    metadata={"provider": "real", "excerpt": getattr(resp, 'content', '')[:200]},
                    session_id=self.session_id
                )
            except Exception as e:
                await self.temporal_integration.create_temporal_node(
                    content="LLM Enrichment Error (synthesize_results)",
                    metadata={"error": str(e)},
                    session_id=self.session_id
                )
        
        return synthesis
    
    def _create_summary(self, successful_results: List[Dict], failed_results: List[Dict]) -> str:
        """Crée un résumé des résultats."""
        if not successful_results and not failed_results:
            return "Aucun résultat à synthétiser"
        
        summary_parts = []
        
        if successful_results:
            summary_parts.append(f"✅ {len(successful_results)} opérations réussies")
        
        if failed_results:
            summary_parts.append(f"❌ {len(failed_results)} opérations échouées")
        
        return " | ".join(summary_parts)
    
    def _generate_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """Génère des recommandations basées sur les résultats."""
        recommendations = []
        
        failed_count = len([r for r in results if not r.get('success', False)])
        
        if failed_count > 0:
            recommendations.append("Vérifiez les erreurs et réessayez les opérations échouées")
        
        if failed_count > len(results) * 0.5:
            recommendations.append("Considérez une approche différente pour cette tâche")
        
        if all(r.get('success', False) for r in results):
            recommendations.append("Toutes les opérations ont réussi - tâche terminée")
        
        return recommendations


class V10ContextManager:
    """Gestionnaire de contexte pour l'agent développeur."""
    
    def __init__(self):
        """Initialise le gestionnaire de contexte."""
        self.context_cache = {}
    
    async def get_context(self, query: str) -> Dict[str, Any]:
        """Récupère le contexte pertinent."""
        # Implémentation simplifiée
        return {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "context_type": "dev_agent"
        }


class V10PlanningEngine:
    """Moteur de planification pour l'agent développeur."""
    
    def __init__(self):
        """Initialise le moteur de planification."""
        self.task_patterns = self._load_task_patterns()
    
    def _load_task_patterns(self) -> Dict[str, Any]:
        """Charge les patterns de tâches."""
        return {
            "file_operation": {
                "tools": ["read_file", "write_file", "list_directory"],
                "complexity": 1
            },
            "code_analysis": {
                "tools": ["code_analyzer", "import_analyzer"],
                "complexity": 2
            },
            "execution": {
                "tools": ["execute_command"],
                "complexity": 2
            },
            "complex_task": {
                "tools": ["multiple_tools"],
                "complexity": 3
            }
        }
    
    async def create_plan(self, user_request: str, context: List[Dict[str, Any]]) -> TaskPlan:
        """Crée un plan basé sur la requête utilisateur."""
        
        # Analyse simple de la requête
        task_type = self._determine_task_type(user_request)
        required_tools = self.task_patterns.get(task_type, {}).get("tools", [])
        complexity = self.task_patterns.get(task_type, {}).get("complexity", 1)
        
        # Création des étapes
        steps = []
        for tool in required_tools:
            steps.append({
                "tool_name": tool,
                "parameters": self._extract_parameters(user_request, tool),
                "description": f"Execute {tool}"
            })
        
        return TaskPlan(
            task_id=f"task_{int(datetime.now().timestamp())}",
            steps=steps,
            estimated_duration=complexity * 2.0,  # 2 secondes par niveau de complexité
            dependencies=[],
            task_type=task_type,
            required_tools=required_tools,
            complexity=complexity
        )
    
    def _determine_task_type(self, user_request: str) -> str:
        """Détermine le type de tâche basé sur la requête."""
        request_lower = user_request.lower()
        
        if any(word in request_lower for word in ["file", "read", "write", "list"]):
            return "file_operation"
        elif any(word in request_lower for word in ["analyze", "code", "import"]):
            return "code_analysis"
        elif any(word in request_lower for word in ["execute", "run", "command"]):
            return "execution"
        else:
            return "complex_task"
    
    def _extract_parameters(self, user_request: str, tool_name: str) -> Dict[str, Any]:
        """Extrait les paramètres pour un outil donné."""
        # Implémentation simplifiée
        return {
            "request": user_request,
            "tool": tool_name
        }
    
    async def create_execution_plan(self, task_analysis: TaskAnalysis) -> TaskPlan:
        """Crée un plan d'exécution détaillé."""
        
        steps = []
        for i, tool in enumerate(task_analysis.required_tools):
            steps.append({
                "step_id": f"step_{i+1}",
                "tool_name": tool,
                "parameters": {},
                "description": f"Execute {tool}",
                "order": i+1
            })
        
        return TaskPlan(
            task_id=f"exec_plan_{int(datetime.now().timestamp())}",
            steps=steps,
            estimated_duration=task_analysis.estimated_complexity * 1.5,
            dependencies=[],
            task_type=task_analysis.task_type,
            required_tools=task_analysis.required_tools,
            complexity=task_analysis.estimated_complexity
        )
