#!/usr/bin/env python3
"""
🧠 Self Discovery Engine - MD Hierarchy Analyzer Daemon V2 ⛧

Moteur d'auto-découverte des capacités du daemon avec introspection mystique.
Permet au daemon de se connaître lui-même et de s'auto-documenter.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import inspect
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class SelfDiscoveryResult:
    """Résultat de l'auto-découverte des capacités."""
    
    core_components: Dict[str, Any] = field(default_factory=dict)
    discovered_methods: Dict[str, Any] = field(default_factory=dict)
    introspection_depth: int = 0
    discovery_timestamp: datetime = field(default_factory=datetime.now)
    capabilities_summary: Dict[str, Any] = field(default_factory=dict)
    integration_analysis: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComponentAnalysis:
    """Analyse détaillée d'un composant."""
    
    component_name: str
    class_name: str
    module_path: str
    methods: List[str] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    integration_points: List[str] = field(default_factory=list)

class SelfDiscoveryEngine:
    """Moteur d'auto-découverte des capacités du daemon."""
    
    def __init__(self, daemon_conductor=None):
        """
        Initialise le moteur d'auto-découverte.
        
        Args:
            daemon_conductor: Instance du chef d'orchestre principal
        """
        self.daemon = daemon_conductor
        self.discovery_cache = {}
        self.introspection_depth = 3
        self.recursive_exploration = True
        self.auto_documentation = True
        
        # Configuration d'introspection
        self.introspection_config = {
            "analyze_methods": True,
            "analyze_attributes": True,
            "analyze_integrations": True,
            "generate_documentation": True,
            "cache_results": True
        }
    
    async def discover_self_capabilities(self) -> SelfDiscoveryResult:
        """
        Découvre automatiquement les capacités du daemon.
        
        Returns:
            SelfDiscoveryResult: Résultat complet de l'auto-découverte
        """
        print("🧠 Démarrage de l'auto-découverte des capacités...")
        
        # 1. Introspection des composants principaux
        core_capabilities = await self._introspect_core_components()
        
        # 2. Exploration des méthodes disponibles
        method_analysis = await self._analyze_available_methods()
        
        # 3. Analyse des intégrations
        integration_analysis = await self._analyze_integrations()
        
        # 4. Synthèse des capacités
        capabilities_summary = await self._synthesize_capabilities(
            core_capabilities, method_analysis, integration_analysis
        )
        
        # 5. Génération du résultat
        result = SelfDiscoveryResult(
            core_components=core_capabilities,
            discovered_methods=method_analysis,
            introspection_depth=self.introspection_depth,
            capabilities_summary=capabilities_summary,
            integration_analysis=integration_analysis
        )
        
        # Cache du résultat
        if self.introspection_config["cache_results"]:
            self.discovery_cache["last_discovery"] = result
        
        print(f"✅ Auto-découverte terminée : {len(core_capabilities)} composants analysés")
        return result
    
    async def _introspect_core_components(self) -> Dict[str, ComponentAnalysis]:
        """Introspection des composants centraux du daemon."""
        
        components = {}
        
        if self.daemon is None:
            print("⚠️ Aucun daemon fourni, introspection limitée")
            return components
        
        # Analyse du chef d'orchestre principal
        conductor_analysis = await self._analyze_component(
            "daemon_conductor", self.daemon
        )
        components["daemon_conductor"] = conductor_analysis
        
        # Analyse des sous-composants
        for attr_name in dir(self.daemon):
            if not attr_name.startswith('_'):
                attr_value = getattr(self.daemon, attr_name, None)
                
                if attr_value and hasattr(attr_value, '__class__'):
                    # Éviter les méthodes et se concentrer sur les objets
                    if not callable(attr_value):
                        component_analysis = await self._analyze_component(
                            attr_name, attr_value
                        )
                        components[attr_name] = component_analysis
        
        return components
    
    async def _analyze_component(self, component_name: str, 
                               component: Any) -> ComponentAnalysis:
        """
        Analyse détaillée d'un composant.
        
        Args:
            component_name: Nom du composant
            component: Instance du composant
            
        Returns:
            ComponentAnalysis: Analyse détaillée
        """
        
        # Informations de base
        class_name = type(component).__name__
        module_path = component.__class__.__module__
        
        # Analyse des méthodes
        methods = []
        if self.introspection_config["analyze_methods"]:
            methods = [
                method for method in dir(component)
                if not method.startswith('_') and callable(getattr(component, method))
            ]
        
        # Analyse des attributs
        attributes = []
        if self.introspection_config["analyze_attributes"]:
            attributes = [
                attr for attr in dir(component)
                if not attr.startswith('_') and not callable(getattr(component, attr))
            ]
        
        # Analyse des capacités
        capabilities = await self._analyze_component_capabilities(component)
        
        # Points d'intégration
        integration_points = await self._identify_integration_points(component)
        
        return ComponentAnalysis(
            component_name=component_name,
            class_name=class_name,
            module_path=module_path,
            methods=methods,
            attributes=attributes,
            capabilities=capabilities,
            integration_points=integration_points
        )
    
    async def _analyze_component_capabilities(self, component: Any) -> Dict[str, Any]:
        """Analyse les capacités spécifiques d'un composant."""
        
        capabilities = {
            "async_methods": [],
            "sync_methods": [],
            "properties": [],
            "special_capabilities": []
        }
        
        # Analyse des méthodes async/sync
        for method_name in dir(component):
            if not method_name.startswith('_'):
                method = getattr(component, method_name, None)
                if callable(method):
                    if asyncio.iscoroutinefunction(method):
                        capabilities["async_methods"].append(method_name)
                    else:
                        capabilities["sync_methods"].append(method_name)
        
        # Détection de capacités spéciales
        special_indicators = {
            "memory_integration": ["memory", "create_memory", "get_memory"],
            "tool_integration": ["tools", "find_tools", "tool_"],
            "editing_integration": ["editing", "partition", "scope"],
            "prompt_generation": ["prompt", "generate", "template"],
            "orchestration": ["orchestrate", "coordinate", "conduct"]
        }
        
        for capability, indicators in special_indicators.items():
            for indicator in indicators:
                if any(indicator in method.lower() for method in capabilities["async_methods"] + capabilities["sync_methods"]):
                    capabilities["special_capabilities"].append(capability)
                    break
        
        return capabilities
    
    async def _identify_integration_points(self, component: Any) -> List[str]:
        """Identifie les points d'intégration d'un composant."""
        
        integration_points = []
        
        # Recherche d'attributs d'intégration
        integration_indicators = [
            "memory", "engine", "bridge", "manager", "analyzer", 
            "orchestrator", "tools", "extension", "session"
        ]
        
        for attr_name in dir(component):
            if not attr_name.startswith('_'):
                for indicator in integration_indicators:
                    if indicator in attr_name.lower():
                        integration_points.append(f"{attr_name} -> {indicator}")
        
        return integration_points
    
    async def _analyze_available_methods(self) -> Dict[str, Any]:
        """Analyse toutes les méthodes disponibles dans le daemon."""
        
        method_analysis = {
            "total_methods": 0,
            "async_methods": 0,
            "sync_methods": 0,
            "method_categories": {},
            "method_signatures": {}
        }
        
        if self.daemon is None:
            return method_analysis
        
        # Analyse récursive des méthodes
        all_methods = await self._collect_all_methods(self.daemon)
        
        method_analysis["total_methods"] = len(all_methods)
        
        # Catégorisation des méthodes
        for method_name, method_info in all_methods.items():
            # Comptage async/sync
            if method_info.get("is_async", False):
                method_analysis["async_methods"] += 1
            else:
                method_analysis["sync_methods"] += 1
            
            # Catégorisation par nom
            category = self._categorize_method(method_name)
            if category not in method_analysis["method_categories"]:
                method_analysis["method_categories"][category] = []
            method_analysis["method_categories"][category].append(method_name)
            
            # Signature de la méthode
            method_analysis["method_signatures"][method_name] = method_info.get("signature", "")
        
        return method_analysis
    
    async def _collect_all_methods(self, obj: Any, prefix: str = "") -> Dict[str, Any]:
        """Collecte récursivement toutes les méthodes disponibles."""
        
        methods = {}
        
        for attr_name in dir(obj):
            if not attr_name.startswith('_'):
                attr_value = getattr(obj, attr_name, None)
                
                if callable(attr_value):
                    full_name = f"{prefix}.{attr_name}" if prefix else attr_name
                    
                    # Analyse de la signature
                    try:
                        signature = str(inspect.signature(attr_value))
                    except (ValueError, TypeError):
                        signature = "signature_unavailable"
                    
                    methods[full_name] = {
                        "is_async": asyncio.iscoroutinefunction(attr_value),
                        "signature": signature,
                        "module": getattr(attr_value, "__module__", "unknown"),
                        "component": prefix or "root"
                    }
                
                elif hasattr(attr_value, '__class__') and not attr_name.startswith('_'):
                    # Exploration récursive des sous-composants
                    if self.recursive_exploration and len(prefix.split('.')) < self.introspection_depth:
                        sub_prefix = f"{prefix}.{attr_name}" if prefix else attr_name
                        sub_methods = await self._collect_all_methods(attr_value, sub_prefix)
                        methods.update(sub_methods)
        
        return methods
    
    def _categorize_method(self, method_name: str) -> str:
        """Catégorise une méthode selon son nom."""
        
        categories = {
            "memory": ["memory", "create", "get", "find", "store"],
            "analysis": ["analyze", "process", "examine", "inspect"],
            "orchestration": ["orchestrate", "coordinate", "conduct", "manage"],
            "generation": ["generate", "create", "build", "synthesize"],
            "discovery": ["discover", "explore", "search", "detect"],
            "integration": ["inject", "bridge", "connect", "integrate"],
            "configuration": ["config", "setup", "init", "configure"]
        }
        
        method_lower = method_name.lower()
        
        for category, keywords in categories.items():
            if any(keyword in method_lower for keyword in keywords):
                return category
        
        return "utility"
    
    async def _analyze_integrations(self) -> Dict[str, Any]:
        """Analyse les intégrations avec les systèmes externes."""
        
        integration_analysis = {
            "memory_engine_integration": await self._check_memory_integration(),
            "editing_session_integration": await self._check_editing_integration(),
            "tool_extension_integration": await self._check_tool_integration(),
            "prompt_system_integration": await self._check_prompt_integration()
        }
        
        return integration_analysis
    
    async def _check_memory_integration(self) -> Dict[str, Any]:
        """Vérifie l'intégration avec MemoryEngine."""
        
        integration = {
            "available": False,
            "backend_type": "unknown",
            "capabilities": [],
            "connection_status": "unknown"
        }
        
        if self.daemon and hasattr(self.daemon, 'memory'):
            integration["available"] = True
            
            memory_component = getattr(self.daemon, 'memory', None)
            if memory_component and hasattr(memory_component, 'memory'):
                memory_engine = memory_component.memory
                integration["backend_type"] = getattr(memory_engine, 'backend_type', 'unknown')
                
                # Test des capacités
                capabilities = []
                test_methods = ['create_memory', 'get_memory_node', 'find_memories_by_keyword']
                for method in test_methods:
                    if hasattr(memory_engine, method):
                        capabilities.append(method)
                
                integration["capabilities"] = capabilities
                integration["connection_status"] = "connected"
        
        return integration
    
    async def _check_editing_integration(self) -> Dict[str, Any]:
        """Vérifie l'intégration avec EditingSession."""
        
        integration = {
            "available": False,
            "partitioning_support": False,
            "navigation_support": False,
            "capabilities": []
        }
        
        if self.daemon and hasattr(self.daemon, 'analyzer'):
            analyzer = getattr(self.daemon, 'analyzer', None)
            if analyzer:
                integration["available"] = True
                
                # Test des capacités d'édition
                if hasattr(analyzer, 'analyze_with_context'):
                    integration["capabilities"].append("contextual_analysis")
                
                if hasattr(analyzer, 'editing'):
                    integration["partitioning_support"] = True
                    integration["navigation_support"] = True
        
        return integration
    
    async def _check_tool_integration(self) -> Dict[str, Any]:
        """Vérifie l'intégration avec ToolMemoryExtension."""
        
        integration = {
            "available": False,
            "indexed": False,
            "tool_count": 0,
            "categories": []
        }
        
        if self.daemon and hasattr(self.daemon, 'tools'):
            tools_component = getattr(self.daemon, 'tools', None)
            if tools_component and hasattr(tools_component, 'tools'):
                tool_extension = tools_component.tools
                integration["available"] = True
                integration["indexed"] = getattr(tool_extension, 'indexed', False)
                
                # Tentative de comptage des outils
                try:
                    if hasattr(tool_extension, '_tool_cache'):
                        integration["tool_count"] = len(tool_extension._tool_cache)
                except:
                    pass
        
        return integration
    
    async def _check_prompt_integration(self) -> Dict[str, Any]:
        """Vérifie l'intégration avec le système de prompts."""
        
        integration = {
            "available": False,
            "dynamic_generation": False,
            "template_support": False,
            "evolution_tracking": False
        }
        
        if self.daemon and hasattr(self.daemon, 'prompts'):
            prompt_component = getattr(self.daemon, 'prompts', None)
            if prompt_component:
                integration["available"] = True
                
                # Test des capacités de prompts
                if hasattr(prompt_component, 'generate_contextual_prompt'):
                    integration["dynamic_generation"] = True
                
                if hasattr(prompt_component, 'prompt_templates'):
                    integration["template_support"] = True
                
                if hasattr(prompt_component, 'evolution_tracker'):
                    integration["evolution_tracking"] = True
        
        return integration
    
    async def _synthesize_capabilities(self, 
                                     core_components: Dict,
                                     method_analysis: Dict,
                                     integration_analysis: Dict) -> Dict[str, Any]:
        """Synthèse finale des capacités découvertes."""
        
        synthesis = {
            "component_count": len(core_components),
            "total_methods": method_analysis.get("total_methods", 0),
            "async_capability": method_analysis.get("async_methods", 0) > 0,
            "integration_score": self._calculate_integration_score(integration_analysis),
            "capability_categories": list(method_analysis.get("method_categories", {}).keys()),
            "strengths": [],
            "areas_for_improvement": [],
            "overall_maturity": "developing"
        }
        
        # Identification des forces
        if synthesis["integration_score"] > 0.7:
            synthesis["strengths"].append("strong_integration")
        
        if synthesis["total_methods"] > 20:
            synthesis["strengths"].append("rich_functionality")
        
        if synthesis["async_capability"]:
            synthesis["strengths"].append("async_support")
        
        # Identification des améliorations
        if synthesis["integration_score"] < 0.5:
            synthesis["areas_for_improvement"].append("improve_integrations")
        
        if len(synthesis["capability_categories"]) < 5:
            synthesis["areas_for_improvement"].append("expand_capabilities")
        
        # Évaluation de la maturité
        maturity_score = (
            synthesis["integration_score"] * 0.4 +
            min(synthesis["total_methods"] / 50, 1.0) * 0.3 +
            len(synthesis["capability_categories"]) / 10 * 0.3
        )
        
        if maturity_score > 0.8:
            synthesis["overall_maturity"] = "mature"
        elif maturity_score > 0.6:
            synthesis["overall_maturity"] = "advanced"
        elif maturity_score > 0.4:
            synthesis["overall_maturity"] = "developing"
        else:
            synthesis["overall_maturity"] = "early"
        
        return synthesis
    
    def _calculate_integration_score(self, integration_analysis: Dict) -> float:
        """Calcule un score d'intégration basé sur les analyses."""
        
        total_integrations = len(integration_analysis)
        successful_integrations = 0
        
        for integration_name, integration_data in integration_analysis.items():
            if integration_data.get("available", False):
                successful_integrations += 1
        
        return successful_integrations / total_integrations if total_integrations > 0 else 0.0
    
    async def generate_self_documentation(self, 
                                        discovery_result: SelfDiscoveryResult) -> str:
        """Génère une documentation automatique basée sur l'auto-découverte."""
        
        if not self.auto_documentation:
            return ""
        
        doc_sections = []
        
        # En-tête
        doc_sections.append("# 🧠 Auto-Documentation - MD Hierarchy Analyzer Daemon V2")
        doc_sections.append(f"**Générée automatiquement le :** {discovery_result.discovery_timestamp}")
        doc_sections.append("")
        
        # Résumé des capacités
        doc_sections.append("## 📊 Résumé des Capacités")
        summary = discovery_result.capabilities_summary
        doc_sections.append(f"- **Composants analysés :** {summary.get('component_count', 0)}")
        doc_sections.append(f"- **Méthodes disponibles :** {summary.get('total_methods', 0)}")
        doc_sections.append(f"- **Support asynchrone :** {'✅' if summary.get('async_capability') else '❌'}")
        doc_sections.append(f"- **Score d'intégration :** {summary.get('integration_score', 0):.2f}")
        doc_sections.append(f"- **Maturité globale :** {summary.get('overall_maturity', 'unknown')}")
        doc_sections.append("")
        
        # Composants découverts
        doc_sections.append("## 🏗️ Composants Découverts")
        for comp_name, comp_data in discovery_result.core_components.items():
            doc_sections.append(f"### {comp_name}")
            doc_sections.append(f"- **Classe :** {comp_data.class_name}")
            doc_sections.append(f"- **Module :** {comp_data.module_path}")
            doc_sections.append(f"- **Méthodes :** {len(comp_data.methods)}")
            doc_sections.append(f"- **Attributs :** {len(comp_data.attributes)}")
            doc_sections.append("")
        
        # Analyse des intégrations
        doc_sections.append("## 🔗 État des Intégrations")
        for integration_name, integration_data in discovery_result.integration_analysis.items():
            status = "✅" if integration_data.get("available", False) else "❌"
            doc_sections.append(f"- **{integration_name} :** {status}")
        doc_sections.append("")
        
        return "\n".join(doc_sections)

# Fonction utilitaire pour l'auto-découverte standalone
async def perform_self_discovery(daemon_conductor=None) -> SelfDiscoveryResult:
    """
    Fonction utilitaire pour effectuer une auto-découverte standalone.
    
    Args:
        daemon_conductor: Instance optionnelle du daemon
        
    Returns:
        SelfDiscoveryResult: Résultat de l'auto-découverte
    """
    
    discovery_engine = SelfDiscoveryEngine(daemon_conductor)
    return await discovery_engine.discover_self_capabilities()

if __name__ == "__main__":
    # Test standalone
    async def test_self_discovery():
        print("🧠 Test du moteur d'auto-découverte...")
        
        discovery_engine = SelfDiscoveryEngine()
        result = await discovery_engine.discover_self_capabilities()
        
        print(f"✅ Découverte terminée :")
        print(f"   - Composants : {len(result.core_components)}")
        print(f"   - Méthodes : {result.discovered_methods.get('total_methods', 0)}")
        print(f"   - Profondeur : {result.introspection_depth}")
        
        # Génération de documentation
        documentation = await discovery_engine.generate_self_documentation(result)
        print(f"📚 Documentation générée : {len(documentation)} caractères")
    
    asyncio.run(test_self_discovery())
