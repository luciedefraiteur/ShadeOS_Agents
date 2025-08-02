#!/usr/bin/env python3
"""
🧠 Memory Engine Introspector - MD Hierarchy Analyzer Daemon V2 ⛧

Introspecteur spécialisé pour l'analyse du MemoryEngine et de ses capacités.
Permet au daemon de comprendre et documenter automatiquement le système de mémoire fractale.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import inspect
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class MemoryIntrospectionResult:
    """Résultat de l'introspection du MemoryEngine."""
    
    architecture: Dict[str, Any] = field(default_factory=dict)
    backends: Dict[str, Any] = field(default_factory=dict)
    strata: Dict[str, Any] = field(default_factory=dict)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    methods: Dict[str, Any] = field(default_factory=dict)
    performance_analysis: Dict[str, Any] = field(default_factory=dict)
    integration_points: List[str] = field(default_factory=list)
    introspection_timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MemoryMethodAnalysis:
    """Analyse détaillée d'une méthode du MemoryEngine."""
    
    method_name: str
    signature: str
    is_async: bool
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    return_type: str = "unknown"
    docstring: Optional[str] = None
    usage_examples: List[str] = field(default_factory=list)
    integration_category: str = "utility"

class MemoryEngineIntrospector:
    """Introspecteur spécialisé pour le MemoryEngine."""
    
    def __init__(self, memory_bridge=None):
        """
        Initialise l'introspecteur MemoryEngine.
        
        Args:
            memory_bridge: Instance du pont vers MemoryEngine
        """
        self.memory_bridge = memory_bridge
        self.memory_engine = None
        self.exploration_cache = {}
        self.introspection_depth = 3
        
        # Configuration d'introspection
        self.config = {
            "analyze_backend": True,
            "analyze_strata": True,
            "analyze_methods": True,
            "test_capabilities": True,
            "generate_examples": True
        }
        
        # Initialisation du MemoryEngine
        if memory_bridge and hasattr(memory_bridge, 'memory'):
            self.memory_engine = memory_bridge.memory
    
    async def introspect_memory_engine(self) -> MemoryIntrospectionResult:
        """
        Introspection complète du MemoryEngine.
        
        Returns:
            MemoryIntrospectionResult: Résultat complet de l'introspection
        """
        print("🧠 Démarrage de l'introspection MemoryEngine...")
        
        # Vérification de la disponibilité
        if not self._check_memory_availability():
            return self._create_unavailable_result()
        
        # 1. Analyse de l'architecture
        architecture_analysis = await self._analyze_memory_architecture()
        
        # 2. Exploration des backends
        backend_analysis = await self._explore_backends()
        
        # 3. Analyse des strates
        strata_analysis = await self._analyze_strata_system()
        
        # 4. Exploration des capacités
        capabilities_analysis = await self._explore_memory_capabilities()
        
        # 5. Auto-documentation des méthodes
        methods_documentation = await self._document_memory_methods()
        
        # 6. Analyse de performance
        performance_analysis = await self._analyze_performance_characteristics()
        
        # 7. Points d'intégration
        integration_points = await self._identify_integration_points()
        
        result = MemoryIntrospectionResult(
            architecture=architecture_analysis,
            backends=backend_analysis,
            strata=strata_analysis,
            capabilities=capabilities_analysis,
            methods=methods_documentation,
            performance_analysis=performance_analysis,
            integration_points=integration_points
        )
        
        print(f"✅ Introspection MemoryEngine terminée")
        return result
    
    def _check_memory_availability(self) -> bool:
        """Vérifie la disponibilité du MemoryEngine."""
        
        if self.memory_engine is None:
            print("⚠️ MemoryEngine non disponible")
            return False
        
        return True
    
    def _create_unavailable_result(self) -> MemoryIntrospectionResult:
        """Crée un résultat pour MemoryEngine non disponible."""
        
        return MemoryIntrospectionResult(
            architecture={"status": "unavailable"},
            backends={"status": "unavailable"},
            strata={"status": "unavailable"},
            capabilities={"status": "unavailable"},
            methods={"status": "unavailable"}
        )
    
    async def _analyze_memory_architecture(self) -> Dict[str, Any]:
        """Analyse l'architecture du MemoryEngine."""
        
        architecture = {
            "engine_class": type(self.memory_engine).__name__,
            "engine_module": self.memory_engine.__class__.__module__,
            "backend_type": getattr(self.memory_engine, 'backend_type', 'unknown'),
            "backend_class": type(self.memory_engine.backend).__name__ if hasattr(self.memory_engine, 'backend') else 'unknown',
            "backend_module": self.memory_engine.backend.__class__.__module__ if hasattr(self.memory_engine, 'backend') else 'unknown'
        }
        
        # Analyse des attributs principaux
        architecture["main_attributes"] = [
            attr for attr in dir(self.memory_engine)
            if not attr.startswith('_') and not callable(getattr(self.memory_engine, attr))
        ]
        
        # Analyse des méthodes principales
        architecture["main_methods"] = [
            method for method in dir(self.memory_engine)
            if not method.startswith('_') and callable(getattr(self.memory_engine, method))
        ]
        
        # Support des fonctionnalités avancées
        architecture["advanced_features"] = {
            "strata_support": hasattr(self.memory_engine.backend, 'find_by_strata') if hasattr(self.memory_engine, 'backend') else False,
            "transcendence_support": hasattr(self.memory_engine.backend, 'traverse_transcendence_path') if hasattr(self.memory_engine, 'backend') else False,
            "immanence_support": hasattr(self.memory_engine.backend, 'traverse_immanence_path') if hasattr(self.memory_engine, 'backend') else False,
            "neo4j_backend": 'Neo4j' in architecture["backend_class"],
            "filesystem_backend": 'FileSystem' in architecture["backend_class"]
        }
        
        return architecture
    
    async def _explore_backends(self) -> Dict[str, Any]:
        """Exploration des backends disponibles."""
        
        backend_info = {
            "current_backend": {
                "type": getattr(self.memory_engine, 'backend_type', 'unknown'),
                "class": type(self.memory_engine.backend).__name__ if hasattr(self.memory_engine, 'backend') else 'unknown',
                "status": "active"
            },
            "backend_capabilities": {},
            "backend_methods": []
        }
        
        if hasattr(self.memory_engine, 'backend'):
            backend = self.memory_engine.backend
            
            # Méthodes du backend
            backend_info["backend_methods"] = [
                method for method in dir(backend)
                if not method.startswith('_') and callable(getattr(backend, method))
            ]
            
            # Capacités spécifiques au backend
            if 'Neo4j' in type(backend).__name__:
                backend_info["backend_capabilities"]["neo4j"] = {
                    "graph_operations": True,
                    "cypher_queries": hasattr(backend, 'driver'),
                    "relationship_traversal": True,
                    "advanced_queries": True
                }
            elif 'FileSystem' in type(backend).__name__:
                backend_info["backend_capabilities"]["filesystem"] = {
                    "file_operations": True,
                    "json_storage": True,
                    "hierarchical_structure": True,
                    "simple_queries": True
                }
        
        return backend_info
    
    async def _analyze_strata_system(self) -> Dict[str, Any]:
        """Analyse du système de strates."""
        
        strata_analysis = {
            "supported_strata": ["somatic", "cognitive", "metaphysical"],
            "strata_capabilities": {},
            "strata_methods": [],
            "strata_usage_patterns": {}
        }
        
        # Vérification du support des strates
        if hasattr(self.memory_engine, 'find_by_strata'):
            strata_analysis["strata_methods"].append("find_by_strata")
        
        if hasattr(self.memory_engine.backend, 'find_by_strata'):
            strata_analysis["strata_methods"].append("backend.find_by_strata")
        
        # Analyse des capacités par strate
        for strata in strata_analysis["supported_strata"]:
            strata_analysis["strata_capabilities"][strata] = {
                "description": self._get_strata_description(strata),
                "typical_content": self._get_strata_content_types(strata),
                "search_supported": len(strata_analysis["strata_methods"]) > 0
            }
        
        # Patterns d'usage recommandés
        strata_analysis["strata_usage_patterns"] = {
            "somatic": "Détails concrets, exemples spécifiques, données factuelles",
            "cognitive": "Logique, patterns, structures, relations",
            "metaphysical": "Concepts abstraits, philosophie, vision globale"
        }
        
        return strata_analysis
    
    def _get_strata_description(self, strata: str) -> str:
        """Retourne la description d'une strate."""
        
        descriptions = {
            "somatic": "Strate des détails concrets et des données factuelles",
            "cognitive": "Strate de la logique, des patterns et des structures",
            "metaphysical": "Strate des concepts abstraits et de la vision globale"
        }
        
        return descriptions.get(strata, "Strate inconnue")
    
    def _get_strata_content_types(self, strata: str) -> List[str]:
        """Retourne les types de contenu typiques d'une strate."""
        
        content_types = {
            "somatic": ["exemples_code", "données_factuelles", "détails_techniques"],
            "cognitive": ["patterns_design", "structures_logiques", "relations_concepts"],
            "metaphysical": ["philosophie_projet", "vision_globale", "concepts_abstraits"]
        }
        
        return content_types.get(strata, [])
    
    async def _explore_memory_capabilities(self) -> Dict[str, Any]:
        """Explore les capacités du MemoryEngine."""
        
        capabilities = {
            "basic_operations": {},
            "advanced_operations": {},
            "query_capabilities": {},
            "maintenance_operations": {}
        }
        
        # Opérations de base
        basic_ops = [
            "create_memory", "get_memory_node", "find_memories_by_keyword", 
            "list_children", "delete_memory"
        ]
        
        for op in basic_ops:
            capabilities["basic_operations"][op] = hasattr(self.memory_engine, op)
        
        # Opérations avancées
        advanced_ops = [
            "find_by_strata", "traverse_transcendence_path", "traverse_immanence_path",
            "cleanup_broken_links", "get_memory_statistics"
        ]
        
        for op in advanced_ops:
            capabilities["advanced_operations"][op] = hasattr(self.memory_engine, op)
        
        # Capacités de requête
        capabilities["query_capabilities"] = {
            "keyword_search": hasattr(self.memory_engine, 'find_memories_by_keyword'),
            "strata_filtering": hasattr(self.memory_engine, 'find_by_strata'),
            "path_navigation": hasattr(self.memory_engine, 'get_memory_node'),
            "hierarchical_listing": hasattr(self.memory_engine, 'list_children')
        }
        
        # Opérations de maintenance
        capabilities["maintenance_operations"] = {
            "link_cleanup": hasattr(self.memory_engine, 'cleanup_broken_links'),
            "statistics": hasattr(self.memory_engine, 'get_memory_statistics'),
            "validation": hasattr(self.memory_engine, 'validate_memory_integrity')
        }
        
        return capabilities
    
    async def _document_memory_methods(self) -> Dict[str, MemoryMethodAnalysis]:
        """Documentation automatique des méthodes MemoryEngine."""
        
        methods_doc = {}
        
        # Méthodes principales à documenter
        important_methods = [
            "create_memory", "get_memory_node", "find_memories_by_keyword",
            "list_children", "find_by_strata", "traverse_transcendence_path"
        ]
        
        for method_name in important_methods:
            if hasattr(self.memory_engine, method_name):
                method = getattr(self.memory_engine, method_name)
                analysis = await self._analyze_method(method_name, method)
                methods_doc[method_name] = analysis
        
        return methods_doc
    
    async def _analyze_method(self, method_name: str, method: callable) -> MemoryMethodAnalysis:
        """Analyse détaillée d'une méthode."""
        
        # Signature de la méthode
        try:
            signature = str(inspect.signature(method))
        except (ValueError, TypeError):
            signature = "signature_unavailable"
        
        # Paramètres
        parameters = []
        try:
            sig = inspect.signature(method)
            for param_name, param in sig.parameters.items():
                param_info = {
                    "name": param_name,
                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                    "default": str(param.default) if param.default != inspect.Parameter.empty else None,
                    "required": param.default == inspect.Parameter.empty
                }
                parameters.append(param_info)
        except:
            pass
        
        # Type de retour
        try:
            sig = inspect.signature(method)
            return_type = str(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else "unknown"
        except:
            return_type = "unknown"
        
        # Docstring
        docstring = inspect.getdoc(method)
        
        # Catégorie d'intégration
        integration_category = self._categorize_method_integration(method_name)
        
        # Exemples d'usage
        usage_examples = await self._generate_method_examples(method_name)
        
        return MemoryMethodAnalysis(
            method_name=method_name,
            signature=signature,
            is_async=asyncio.iscoroutinefunction(method),
            parameters=parameters,
            return_type=return_type,
            docstring=docstring,
            usage_examples=usage_examples,
            integration_category=integration_category
        )
    
    def _categorize_method_integration(self, method_name: str) -> str:
        """Catégorise une méthode selon son rôle d'intégration."""
        
        categories = {
            "creation": ["create", "write", "store"],
            "retrieval": ["get", "find", "search", "list"],
            "navigation": ["traverse", "navigate", "path"],
            "maintenance": ["cleanup", "delete", "validate"],
            "analysis": ["statistics", "analyze", "inspect"]
        }
        
        method_lower = method_name.lower()
        
        for category, keywords in categories.items():
            if any(keyword in method_lower for keyword in keywords):
                return category
        
        return "utility"
    
    async def _generate_method_examples(self, method_name: str) -> List[str]:
        """Génère des exemples d'usage pour une méthode."""
        
        examples = {
            "create_memory": [
                'memory.create_memory("/docs/readme", content, "README analysis", ["markdown", "docs"])',
                'memory.create_memory("/patterns/hierarchy", pattern_data, "Hierarchy pattern", ["pattern"], strata="cognitive")'
            ],
            "get_memory_node": [
                'node = memory.get_memory_node("/docs/readme")',
                'node = memory.get_memory_node("/patterns/hierarchy")'
            ],
            "find_memories_by_keyword": [
                'results = memory.find_memories_by_keyword("markdown")',
                'docs = memory.find_memories_by_keyword("documentation")'
            ],
            "find_by_strata": [
                'cognitive_memories = memory.find_by_strata("cognitive")',
                'somatic_data = memory.find_by_strata("somatic")'
            ],
            "traverse_transcendence_path": [
                'path = memory.traverse_transcendence_path("/specific/concept", max_depth=3)',
                'abstractions = memory.traverse_transcendence_path("/concrete/example")'
            ]
        }
        
        return examples.get(method_name, [f"# Exemple d'usage pour {method_name}", f"result = memory.{method_name}(...)"])
    
    async def _analyze_performance_characteristics(self) -> Dict[str, Any]:
        """Analyse les caractéristiques de performance."""
        
        performance = {
            "backend_performance": {},
            "operation_complexity": {},
            "scalability_factors": {},
            "optimization_recommendations": []
        }
        
        # Performance selon le backend
        backend_type = getattr(self.memory_engine, 'backend_type', 'unknown')
        
        if 'neo4j' in backend_type.lower():
            performance["backend_performance"] = {
                "query_speed": "high",
                "relationship_traversal": "excellent",
                "complex_queries": "very_good",
                "scalability": "excellent"
            }
        elif 'filesystem' in backend_type.lower():
            performance["backend_performance"] = {
                "query_speed": "medium",
                "relationship_traversal": "limited",
                "complex_queries": "basic",
                "scalability": "limited"
            }
        
        # Complexité des opérations
        performance["operation_complexity"] = {
            "create_memory": "O(1)",
            "get_memory_node": "O(1)",
            "find_memories_by_keyword": "O(n)",
            "traverse_transcendence_path": "O(depth * connections)"
        }
        
        # Recommandations d'optimisation
        if 'filesystem' in backend_type.lower():
            performance["optimization_recommendations"].append("Consider Neo4j backend for better performance")
        
        performance["optimization_recommendations"].extend([
            "Use specific keywords for faster searches",
            "Limit transcendence traversal depth",
            "Cache frequently accessed memories"
        ])
        
        return performance
    
    async def _identify_integration_points(self) -> List[str]:
        """Identifie les points d'intégration avec d'autres systèmes."""
        
        integration_points = []
        
        # Points d'intégration standard
        standard_points = [
            "memory_bridge -> daemon_conductor",
            "strata_system -> contextual_analysis",
            "keyword_search -> tool_discovery",
            "transcendence_navigation -> concept_exploration",
            "memory_creation -> documentation_storage"
        ]
        
        integration_points.extend(standard_points)
        
        # Points d'intégration spécifiques au backend
        backend_type = getattr(self.memory_engine, 'backend_type', 'unknown')
        
        if 'neo4j' in backend_type.lower():
            integration_points.extend([
                "neo4j_queries -> advanced_analytics",
                "graph_relationships -> semantic_mapping",
                "cypher_queries -> custom_analysis"
            ])
        
        return integration_points
    
    async def generate_memory_usage_guide(self, 
                                        introspection_result: MemoryIntrospectionResult) -> str:
        """Génère un guide d'usage du MemoryEngine."""
        
        guide_sections = []
        
        # En-tête
        guide_sections.append("# 🧠 Guide d'Usage MemoryEngine - Auto-Généré")
        guide_sections.append(f"**Généré le :** {introspection_result.introspection_timestamp}")
        guide_sections.append("")
        
        # Architecture
        arch = introspection_result.architecture
        guide_sections.append("## 🏗️ Architecture")
        guide_sections.append(f"- **Backend actuel :** {arch.get('backend_type', 'unknown')}")
        guide_sections.append(f"- **Classe backend :** {arch.get('backend_class', 'unknown')}")
        guide_sections.append(f"- **Support strates :** {'✅' if arch.get('advanced_features', {}).get('strata_support') else '❌'}")
        guide_sections.append("")
        
        # Méthodes principales
        guide_sections.append("## 🔧 Méthodes Principales")
        for method_name, method_analysis in introspection_result.methods.items():
            guide_sections.append(f"### {method_name}")
            guide_sections.append(f"**Signature :** `{method_analysis.signature}`")
            guide_sections.append(f"**Type :** {'Async' if method_analysis.is_async else 'Sync'}")
            
            if method_analysis.usage_examples:
                guide_sections.append("**Exemples :**")
                for example in method_analysis.usage_examples:
                    guide_sections.append(f"```python\n{example}\n```")
            guide_sections.append("")
        
        # Système de strates
        guide_sections.append("## 🌟 Système de Strates")
        strata_info = introspection_result.strata
        for strata, info in strata_info.get("strata_capabilities", {}).items():
            guide_sections.append(f"### {strata.title()}")
            guide_sections.append(f"- **Description :** {info.get('description', 'N/A')}")
            guide_sections.append(f"- **Usage :** {strata_info.get('strata_usage_patterns', {}).get(strata, 'N/A')}")
            guide_sections.append("")
        
        return "\n".join(guide_sections)

# Fonction utilitaire pour l'introspection standalone
async def introspect_memory_engine_standalone(memory_bridge=None) -> MemoryIntrospectionResult:
    """
    Fonction utilitaire pour l'introspection standalone du MemoryEngine.
    
    Args:
        memory_bridge: Instance optionnelle du pont mémoire
        
    Returns:
        MemoryIntrospectionResult: Résultat de l'introspection
    """
    
    introspector = MemoryEngineIntrospector(memory_bridge)
    return await introspector.introspect_memory_engine()

if __name__ == "__main__":
    # Test standalone
    async def test_memory_introspection():
        print("🧠 Test de l'introspecteur MemoryEngine...")
        
        introspector = MemoryEngineIntrospector()
        result = await introspector.introspect_memory_engine()
        
        print(f"✅ Introspection terminée :")
        print(f"   - Architecture : {result.architecture.get('status', 'analyzed')}")
        print(f"   - Backends : {result.backends.get('status', 'analyzed')}")
        print(f"   - Méthodes : {len(result.methods)}")
        
        # Génération du guide
        guide = await introspector.generate_memory_usage_guide(result)
        print(f"📚 Guide généré : {len(guide)} caractères")
    
    asyncio.run(test_memory_introspection())
