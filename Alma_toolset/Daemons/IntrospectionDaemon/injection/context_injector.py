#!/usr/bin/env python3
"""
💉 Context Injector - IntrospectionDaemon ⛧

Injecteur contextuel intelligent pour l'enrichissement de prompts.
Injecte des données pertinentes du MemoryEngine, ToolRegistry et autres sources.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class InjectionContext:
    """Contexte d'injection avec métadonnées."""
    
    injection_type: str
    source_data: Dict[str, Any] = field(default_factory=dict)
    relevance_score: float = 0.0
    injection_points: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InjectionResult:
    """Résultat d'une injection contextuelle."""
    
    enriched_prompt: str
    injections_applied: List[str] = field(default_factory=list)
    relevance_scores: Dict[str, float] = field(default_factory=dict)
    injection_metadata: Dict[str, Any] = field(default_factory=dict)
    total_injections: int = 0

class ContextInjector:
    """Injecteur contextuel intelligent pour prompts d'introspection."""
    
    def __init__(self, ecosystem_components: Optional[Dict] = None):
        """
        Initialise l'injecteur contextuel.
        
        Args:
            ecosystem_components: Composants de l'écosystème disponibles
        """
        self.ecosystem_components = ecosystem_components or {}
        self.injection_cache = {}
        self.relevance_tracking = {}
        
        # Configuration d'injection
        self.config = {
            "max_injection_size": 2000,  # Caractères max par injection
            "relevance_threshold": 0.3,
            "cache_duration": 300,  # 5 minutes
            "smart_filtering": True,
            "context_optimization": True
        }
        
        # Patterns d'injection
        self.injection_patterns = {
            "memory_context": r"::INJECT_MEMORY_CONTEXT::",
            "tool_context": r"::INJECT_TOOL_CONTEXT::",
            "component_context": r"::INJECT_COMPONENT_CONTEXT::",
            "capability_context": r"::INJECT_CAPABILITY_CONTEXT::",
            "performance_context": r"::INJECT_PERFORMANCE_CONTEXT::"
        }
        
        # Initialisation des injecteurs spécialisés
        self._initialize_specialized_injectors()
    
    def _initialize_specialized_injectors(self):
        """Initialise les injecteurs spécialisés."""
        
        try:
            from .memory_bridge_injector import MemoryBridgeInjector
            from .tool_registry_injector import ToolRegistryInjector
            from .data_aggregator import DataAggregator
            
            self.memory_injector = MemoryBridgeInjector()
            self.tool_injector = ToolRegistryInjector()
            self.data_aggregator = DataAggregator()
            
            print("✅ Injecteurs spécialisés initialisés")
            
        except ImportError as e:
            print(f"⚠️ Injecteurs spécialisés non disponibles, mode simulation : {e}")
            self._initialize_simulation_injectors()
    
    def _initialize_simulation_injectors(self):
        """Initialise des injecteurs de simulation."""
        
        self.memory_injector = SimulatedMemoryInjector()
        self.tool_injector = SimulatedToolInjector()
        self.data_aggregator = SimulatedDataAggregator()
    
    async def inject_comprehensive_context(self, 
                                         prompt: str,
                                         components_data: Dict[str, Any],
                                         capabilities_data: Dict[str, Any]) -> str:
        """
        Injecte un contexte complet dans un prompt.
        
        Args:
            prompt: Prompt de base
            components_data: Données des composants
            capabilities_data: Données des capacités
            
        Returns:
            str: Prompt enrichi avec contexte complet
        """
        print("💉 Injection de contexte complet...")
        
        # Agrégation des données contextuelles
        aggregated_data = await self.data_aggregator.aggregate_comprehensive_data(
            components_data, capabilities_data, self.ecosystem_components
        )
        
        # Injection séquentielle des différents contextes
        enriched_prompt = prompt
        injection_results = []
        
        # 1. Injection du contexte mémoire
        if await self._should_inject_memory_context(prompt, aggregated_data):
            memory_result = await self._inject_memory_context(enriched_prompt, aggregated_data)
            enriched_prompt = memory_result.enriched_prompt
            injection_results.append(memory_result)
        
        # 2. Injection du contexte d'outils
        if await self._should_inject_tool_context(prompt, aggregated_data):
            tool_result = await self._inject_tool_context(enriched_prompt, aggregated_data)
            enriched_prompt = tool_result.enriched_prompt
            injection_results.append(tool_result)
        
        # 3. Injection du contexte de composants
        component_result = await self._inject_component_context(
            enriched_prompt, components_data
        )
        enriched_prompt = component_result.enriched_prompt
        injection_results.append(component_result)
        
        # 4. Injection du contexte de capacités
        capability_result = await self._inject_capability_context(
            enriched_prompt, capabilities_data
        )
        enriched_prompt = capability_result.enriched_prompt
        injection_results.append(capability_result)
        
        # 5. Optimisation finale
        if self.config["context_optimization"]:
            enriched_prompt = await self._optimize_injected_context(
                enriched_prompt, injection_results
            )
        
        print(f"✅ Contexte complet injecté : {len(injection_results)} injections")
        return enriched_prompt
    
    async def inject_targeted_context(self, 
                                    prompt: str,
                                    focus: str,
                                    context_data: Dict[str, Any]) -> str:
        """
        Injecte un contexte ciblé pour une analyse focalisée.
        
        Args:
            prompt: Prompt de base
            focus: Focus de l'analyse
            context_data: Données contextuelles
            
        Returns:
            str: Prompt enrichi avec contexte ciblé
        """
        print(f"💉 Injection de contexte ciblé : {focus}")
        
        # Filtrage des données pertinentes au focus
        relevant_data = await self._filter_relevant_data(focus, context_data)
        
        # Injection spécialisée selon le focus
        if focus.startswith("memory"):
            return await self._inject_memory_focused_context(prompt, relevant_data)
        elif focus.startswith("tool"):
            return await self._inject_tool_focused_context(prompt, relevant_data)
        elif focus.startswith("component"):
            return await self._inject_component_focused_context(prompt, relevant_data)
        else:
            return await self._inject_generic_focused_context(prompt, focus, relevant_data)
    
    async def inject_contextual_data(self, 
                                   prompt: str,
                                   injection_type: str,
                                   source_components: Dict[str, Any]) -> str:
        """
        Injecte des données contextuelles spécifiques.
        
        Args:
            prompt: Prompt de base
            injection_type: Type d'injection
            source_components: Composants sources
            
        Returns:
            str: Prompt enrichi
        """
        print(f"💉 Injection de données : {injection_type}")
        
        # Sélection de la stratégie d'injection
        if injection_type == "memory_analysis":
            return await self._inject_memory_analysis_data(prompt, source_components)
        elif injection_type == "tool_inventory":
            return await self._inject_tool_inventory_data(prompt, source_components)
        elif injection_type == "performance_metrics":
            return await self._inject_performance_data(prompt, source_components)
        elif injection_type == "capability_assessment":
            return await self._inject_capability_data(prompt, source_components)
        else:
            return await self._inject_generic_data(prompt, injection_type, source_components)
    
    async def _inject_memory_context(self, 
                                   prompt: str, 
                                   aggregated_data: Dict) -> InjectionResult:
        """Injecte le contexte mémoire."""
        
        memory_data = await self.memory_injector.extract_memory_context(aggregated_data)
        
        # Formatage du contexte mémoire
        memory_context = self._format_memory_context(memory_data)
        
        # Injection dans le prompt
        enriched_prompt = prompt.replace(
            "::INJECT_MEMORY_CONTEXT::",
            memory_context
        )
        
        # Si pas de pattern spécifique, injection générique
        if "::INJECT_MEMORY_CONTEXT::" not in prompt:
            enriched_prompt = self._inject_generic_memory_context(prompt, memory_context)
        
        return InjectionResult(
            enriched_prompt=enriched_prompt,
            injections_applied=["memory_context"],
            relevance_scores={"memory_context": memory_data.get("relevance", 0.5)},
            total_injections=1
        )
    
    async def _inject_tool_context(self, 
                                 prompt: str, 
                                 aggregated_data: Dict) -> InjectionResult:
        """Injecte le contexte d'outils."""
        
        tool_data = await self.tool_injector.extract_tool_context(aggregated_data)
        
        # Formatage du contexte d'outils
        tool_context = self._format_tool_context(tool_data)
        
        # Injection dans le prompt
        enriched_prompt = prompt.replace(
            "::INJECT_TOOL_CONTEXT::",
            tool_context
        )
        
        if "::INJECT_TOOL_CONTEXT::" not in prompt:
            enriched_prompt = self._inject_generic_tool_context(prompt, tool_context)
        
        return InjectionResult(
            enriched_prompt=enriched_prompt,
            injections_applied=["tool_context"],
            relevance_scores={"tool_context": tool_data.get("relevance", 0.5)},
            total_injections=1
        )
    
    async def _inject_component_context(self, 
                                      prompt: str, 
                                      components_data: Dict) -> InjectionResult:
        """Injecte le contexte des composants."""
        
        # Formatage des données de composants
        component_context = self._format_component_context(components_data)
        
        # Injection
        enriched_prompt = prompt.replace(
            "::INJECT_COMPONENT_CONTEXT::",
            component_context
        )
        
        if "::INJECT_COMPONENT_CONTEXT::" not in prompt:
            enriched_prompt = self._inject_generic_component_context(prompt, component_context)
        
        return InjectionResult(
            enriched_prompt=enriched_prompt,
            injections_applied=["component_context"],
            relevance_scores={"component_context": 0.8},
            total_injections=1
        )
    
    async def _inject_capability_context(self, 
                                       prompt: str, 
                                       capabilities_data: Dict) -> InjectionResult:
        """Injecte le contexte des capacités."""
        
        # Formatage des données de capacités
        capability_context = self._format_capability_context(capabilities_data)
        
        # Injection
        enriched_prompt = prompt.replace(
            "::INJECT_CAPABILITY_CONTEXT::",
            capability_context
        )
        
        if "::INJECT_CAPABILITY_CONTEXT::" not in prompt:
            enriched_prompt = self._inject_generic_capability_context(prompt, capability_context)
        
        return InjectionResult(
            enriched_prompt=enriched_prompt,
            injections_applied=["capability_context"],
            relevance_scores={"capability_context": 0.7},
            total_injections=1
        )
    
    def _format_memory_context(self, memory_data: Dict) -> str:
        """Formate le contexte mémoire pour injection."""
        
        if not memory_data:
            return "Contexte mémoire : Non disponible"
        
        formatted = "CONTEXTE MÉMOIRE INJECTÉ :\n"
        
        # Strates disponibles
        if "strata" in memory_data:
            formatted += f"- Strates actives : {', '.join(memory_data['strata'])}\n"
        
        # Backend utilisé
        if "backend_type" in memory_data:
            formatted += f"- Backend : {memory_data['backend_type']}\n"
        
        # Capacités mémoire
        if "capabilities" in memory_data:
            formatted += f"- Capacités : {len(memory_data['capabilities'])} identifiées\n"
        
        # Métriques
        if "metrics" in memory_data:
            formatted += f"- Métriques : {memory_data['metrics']}\n"
        
        return formatted
    
    def _format_tool_context(self, tool_data: Dict) -> str:
        """Formate le contexte d'outils pour injection."""
        
        if not tool_data:
            return "Contexte outils : Non disponible"
        
        formatted = "CONTEXTE OUTILS INJECTÉ :\n"
        
        # Catégories d'outils
        if "categories" in tool_data:
            formatted += f"- Catégories : {', '.join(tool_data['categories'])}\n"
        
        # Nombre total d'outils
        if "total_tools" in tool_data:
            formatted += f"- Total outils : {tool_data['total_tools']}\n"
        
        # Outils actifs
        if "active_tools" in tool_data:
            formatted += f"- Outils actifs : {len(tool_data['active_tools'])}\n"
        
        return formatted
    
    def _format_component_context(self, components_data: Dict) -> str:
        """Formate le contexte des composants pour injection."""
        
        formatted = "CONTEXTE COMPOSANTS INJECTÉ :\n"
        
        for comp_name, comp_data in components_data.items():
            status = comp_data.get("status", "unknown")
            health = comp_data.get("health", 0.0)
            formatted += f"- {comp_name} : {status} (santé: {health:.2f})\n"
        
        return formatted
    
    def _format_capability_context(self, capabilities_data: Dict) -> str:
        """Formate le contexte des capacités pour injection."""
        
        formatted = "CONTEXTE CAPACITÉS INJECTÉ :\n"
        
        for cap_name, cap_score in capabilities_data.items():
            formatted += f"- {cap_name} : {cap_score:.2f}\n"
        
        return formatted
    
    async def _should_inject_memory_context(self, prompt: str, data: Dict) -> bool:
        """Détermine si l'injection de contexte mémoire est nécessaire."""
        
        # Vérification de la présence de patterns mémoire
        memory_indicators = ["memory", "mémoire", "strata", "backend", "fractal"]
        
        return any(indicator in prompt.lower() for indicator in memory_indicators)
    
    async def _should_inject_tool_context(self, prompt: str, data: Dict) -> bool:
        """Détermine si l'injection de contexte d'outils est nécessaire."""
        
        tool_indicators = ["tool", "outil", "registry", "registre", "divination", "transmutation"]
        
        return any(indicator in prompt.lower() for indicator in tool_indicators)
    
    async def _filter_relevant_data(self, focus: str, context_data: Dict) -> Dict:
        """Filtre les données pertinentes pour un focus donné."""
        
        relevant_data = {}
        
        # Filtrage basé sur le focus
        focus_lower = focus.lower()
        
        for key, value in context_data.items():
            if focus_lower in key.lower() or any(
                focus_word in key.lower() for focus_word in focus_lower.split("_")
            ):
                relevant_data[key] = value
        
        return relevant_data
    
    async def _optimize_injected_context(self, 
                                       prompt: str, 
                                       injection_results: List[InjectionResult]) -> str:
        """Optimise le contexte injecté pour éviter la redondance."""
        
        # Simplification : suppression des doublons évidents
        optimized_prompt = prompt
        
        # Suppression des lignes dupliquées
        lines = optimized_prompt.split('\n')
        unique_lines = []
        seen_lines = set()
        
        for line in lines:
            line_clean = line.strip()
            if line_clean and line_clean not in seen_lines:
                unique_lines.append(line)
                seen_lines.add(line_clean)
            elif not line_clean:  # Garde les lignes vides
                unique_lines.append(line)
        
        return '\n'.join(unique_lines)
    
    # Méthodes d'injection génériques (fallback)
    def _inject_generic_memory_context(self, prompt: str, context: str) -> str:
        return f"{prompt}\n\n{context}"
    
    def _inject_generic_tool_context(self, prompt: str, context: str) -> str:
        return f"{prompt}\n\n{context}"
    
    def _inject_generic_component_context(self, prompt: str, context: str) -> str:
        return f"{prompt}\n\n{context}"
    
    def _inject_generic_capability_context(self, prompt: str, context: str) -> str:
        return f"{prompt}\n\n{context}"
    
    # Méthodes d'injection focalisée (simplifiées)
    async def _inject_memory_focused_context(self, prompt: str, data: Dict) -> str:
        return f"{prompt}\n\nCONTEXTE MÉMOIRE FOCALISÉ : {json.dumps(data, indent=2)}"
    
    async def _inject_tool_focused_context(self, prompt: str, data: Dict) -> str:
        return f"{prompt}\n\nCONTEXTE OUTILS FOCALISÉ : {json.dumps(data, indent=2)}"
    
    async def _inject_component_focused_context(self, prompt: str, data: Dict) -> str:
        return f"{prompt}\n\nCONTEXTE COMPOSANT FOCALISÉ : {json.dumps(data, indent=2)}"
    
    async def _inject_generic_focused_context(self, prompt: str, focus: str, data: Dict) -> str:
        return f"{prompt}\n\nCONTEXTE FOCALISÉ ({focus}) : {json.dumps(data, indent=2)}"
    
    # Méthodes d'injection de données spécifiques (simplifiées)
    async def _inject_memory_analysis_data(self, prompt: str, components: Dict) -> str:
        return f"{prompt}\n\nDONNÉES ANALYSE MÉMOIRE : [À implémenter]"
    
    async def _inject_tool_inventory_data(self, prompt: str, components: Dict) -> str:
        return f"{prompt}\n\nDONNÉES INVENTAIRE OUTILS : [À implémenter]"
    
    async def _inject_performance_data(self, prompt: str, components: Dict) -> str:
        return f"{prompt}\n\nDONNÉES PERFORMANCE : [À implémenter]"
    
    async def _inject_capability_data(self, prompt: str, components: Dict) -> str:
        return f"{prompt}\n\nDONNÉES CAPACITÉS : [À implémenter]"
    
    async def _inject_generic_data(self, prompt: str, injection_type: str, components: Dict) -> str:
        return f"{prompt}\n\nDONNÉES GÉNÉRIQUES ({injection_type}) : [À implémenter]"

# Classes de simulation
class SimulatedMemoryInjector:
    async def extract_memory_context(self, data: Dict) -> Dict:
        await asyncio.sleep(0.1)
        return {
            "strata": ["somatic", "cognitive", "metaphysical"],
            "backend_type": "neo4j",
            "capabilities": ["create", "search", "traverse"],
            "relevance": 0.8
        }

class SimulatedToolInjector:
    async def extract_tool_context(self, data: Dict) -> Dict:
        await asyncio.sleep(0.1)
        return {
            "categories": ["divination", "transmutation", "protection"],
            "total_tools": 23,
            "active_tools": ["regex_search", "template_generator"],
            "relevance": 0.7
        }

class SimulatedDataAggregator:
    async def aggregate_comprehensive_data(self, components: Dict, capabilities: Dict, ecosystem: Dict) -> Dict:
        await asyncio.sleep(0.1)
        return {
            "aggregated_components": components,
            "aggregated_capabilities": capabilities,
            "ecosystem_data": ecosystem,
            "aggregation_timestamp": datetime.now()
        }

if __name__ == "__main__":
    # Test de l'injecteur contextuel
    async def test_context_injector():
        print("💉 Test de l'injecteur contextuel...")
        
        injector = ContextInjector()
        
        # Test d'injection complète
        prompt = "Analyse-toi ::INJECT_MEMORY_CONTEXT:: et ::INJECT_TOOL_CONTEXT::"
        components = {"memory": {"status": "active", "health": 0.9}}
        capabilities = {"introspection": 0.8}
        
        enriched = await injector.inject_comprehensive_context(
            prompt, components, capabilities
        )
        
        print(f"✅ Prompt enrichi : {len(enriched)} caractères")
        print(f"📊 Injection réussie")
    
    asyncio.run(test_context_injector())
