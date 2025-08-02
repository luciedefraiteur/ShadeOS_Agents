#!/usr/bin/env python3
"""
🛠️ Tool Registry Explorer - MD Hierarchy Analyzer Daemon V2 ⛧

Explorateur récursif du registre d'outils avec analyse des dépendances et synergies.
Permet au daemon de s'auto-inventorier et de comprendre son écosystème d'outils.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

@dataclass
class ToolRegistryExploration:
    """Résultat de l'exploration du registre d'outils."""
    
    categories: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: Dict[str, Any] = field(default_factory=dict)
    synergies: Dict[str, Any] = field(default_factory=dict)
    orchestration_patterns: Dict[str, Any] = field(default_factory=dict)
    completeness_score: float = 0.0
    exploration_timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ToolAnalysis:
    """Analyse détaillée d'un outil."""
    
    tool_id: str
    tool_type: str
    intent: str
    level: str
    keywords: List[str] = field(default_factory=list)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    synergy_partners: List[str] = field(default_factory=list)
    usage_patterns: List[str] = field(default_factory=list)
    integration_points: List[str] = field(default_factory=list)

class ToolRegistryExplorer:
    """Explorateur récursif du registre d'outils."""
    
    def __init__(self, tool_memory_extension=None):
        """
        Initialise l'explorateur du registre d'outils.
        
        Args:
            tool_memory_extension: Instance de ToolMemoryExtension
        """
        self.tools = tool_memory_extension
        self.exploration_depth = 5
        self.recursive_discovery = True
        self.exploration_cache = {}
        
        # Configuration d'exploration
        self.config = {
            "analyze_dependencies": True,
            "analyze_synergies": True,
            "generate_patterns": True,
            "cache_results": True,
            "deep_analysis": True
        }
    
    async def explore_tool_registry(self) -> ToolRegistryExploration:
        """
        Exploration complète et récursive du registre d'outils.
        
        Returns:
            ToolRegistryExploration: Résultat complet de l'exploration
        """
        print("🛠️ Démarrage de l'exploration du registre d'outils...")
        
        # Vérification de la disponibilité
        if not self._check_tools_availability():
            return self._create_unavailable_result()
        
        # 1. Indexation complète des outils
        await self._ensure_tool_indexation()
        
        # 2. Exploration par catégories
        category_exploration = await self._explore_by_categories()
        
        # 3. Analyse des métadonnées
        metadata_analysis = await self._analyze_tool_metadata()
        
        # 4. Exploration récursive des dépendances
        dependency_exploration = await self._explore_tool_dependencies()
        
        # 5. Cartographie des synergies
        synergy_mapping = await self._map_tool_synergies()
        
        # 6. Analyse des patterns d'orchestration
        orchestration_patterns = await self._analyze_orchestration_patterns()
        
        # 7. Calcul du score de complétude
        completeness_score = await self._calculate_completeness_score(
            category_exploration, metadata_analysis, dependency_exploration
        )
        
        result = ToolRegistryExploration(
            categories=category_exploration,
            metadata=metadata_analysis,
            dependencies=dependency_exploration,
            synergies=synergy_mapping,
            orchestration_patterns=orchestration_patterns,
            completeness_score=completeness_score
        )
        
        # Cache du résultat
        if self.config["cache_results"]:
            self.exploration_cache["last_exploration"] = result
        
        print(f"✅ Exploration terminée : {len(category_exploration)} catégories analysées")
        return result
    
    def _check_tools_availability(self) -> bool:
        """Vérifie la disponibilité du système d'outils."""
        
        if self.tools is None:
            print("⚠️ ToolMemoryExtension non disponible")
            return False
        
        return True
    
    def _create_unavailable_result(self) -> ToolRegistryExploration:
        """Crée un résultat pour système d'outils non disponible."""
        
        return ToolRegistryExploration(
            categories={"status": "unavailable"},
            metadata={"status": "unavailable"},
            dependencies={"status": "unavailable"},
            synergies={"status": "unavailable"}
        )
    
    async def _ensure_tool_indexation(self):
        """S'assure que tous les outils sont indexés."""
        
        if not self.tools.indexed:
            print("🔄 Indexation des outils en cours...")
            self.tools.index_all_tools()
            print("✅ Indexation terminée")
    
    async def _explore_by_categories(self) -> Dict[str, Any]:
        """Exploration par catégories mystiques."""
        
        categories = {}
        
        # Découverte automatique des catégories
        all_tools = await self._get_all_tools()
        discovered_categories = set()
        
        for tool in all_tools:
            tool_type = tool.get('type', 'unknown')
            discovered_categories.add(tool_type)
        
        print(f"🗂️ Catégories découvertes : {list(discovered_categories)}")
        
        # Exploration de chaque catégorie
        for category in discovered_categories:
            category_tools = self.tools.find_tools_by_type(category)
            
            # Analyse détaillée des outils de la catégorie
            analyzed_tools = []
            for tool in category_tools:
                tool_analysis = await self._analyze_tool_detailed(tool)
                analyzed_tools.append(tool_analysis)
            
            categories[category] = {
                "tool_count": len(category_tools),
                "description": self._get_category_description(category),
                "tools": analyzed_tools,
                "category_capabilities": await self._analyze_category_capabilities(category_tools),
                "integration_patterns": await self._identify_category_integration_patterns(category)
            }
        
        return categories
    
    def _get_category_description(self, category: str) -> str:
        """Retourne la description d'une catégorie d'outils."""
        
        descriptions = {
            "divination": "Outils de recherche, analyse et découverte mystique",
            "transmutation": "Outils de transformation et génération de contenu",
            "protection": "Outils de sauvegarde, validation et sécurité",
            "invocation": "Outils d'orchestration et d'automation",
            "communication": "Outils d'interaction et de messaging",
            "analysis": "Outils d'analyse et d'inspection",
            "utility": "Outils utilitaires et de support"
        }
        
        return descriptions.get(category, f"Catégorie mystique : {category}")
    
    async def _analyze_tool_detailed(self, tool: Dict[str, Any]) -> ToolAnalysis:
        """Analyse détaillée d'un outil."""
        
        tool_id = tool.get('tool_id', 'unknown')
        
        # Analyse des capacités
        capabilities = await self._analyze_tool_capabilities(tool)
        
        # Analyse des dépendances
        dependencies = await self._analyze_tool_dependencies(tool)
        
        # Analyse des synergies
        synergy_partners = await self._identify_synergy_partners(tool)
        
        # Patterns d'usage
        usage_patterns = await self._identify_usage_patterns(tool)
        
        # Points d'intégration
        integration_points = await self._identify_tool_integration_points(tool)
        
        return ToolAnalysis(
            tool_id=tool_id,
            tool_type=tool.get('type', 'unknown'),
            intent=tool.get('intent', ''),
            level=tool.get('level', 'unknown'),
            keywords=tool.get('keywords', []),
            capabilities=capabilities,
            dependencies=dependencies,
            synergy_partners=synergy_partners,
            usage_patterns=usage_patterns,
            integration_points=integration_points
        )
    
    async def _analyze_tool_capabilities(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse les capacités d'un outil."""
        
        capabilities = {
            "primary_function": tool.get('intent', ''),
            "complexity_level": tool.get('level', 'unknown'),
            "input_types": [],
            "output_types": [],
            "special_features": []
        }
        
        # Analyse basée sur les mots-clés
        keywords = tool.get('keywords', [])
        
        # Détection des types d'entrée/sortie
        if any(kw in ['file', 'text', 'content'] for kw in keywords):
            capabilities["input_types"].append("text_content")
        
        if any(kw in ['search', 'find', 'locate'] for kw in keywords):
            capabilities["output_types"].append("search_results")
        
        if any(kw in ['generate', 'create', 'build'] for kw in keywords):
            capabilities["output_types"].append("generated_content")
        
        # Détection des fonctionnalités spéciales
        if 'regex' in keywords:
            capabilities["special_features"].append("regex_support")
        
        if 'recursive' in keywords:
            capabilities["special_features"].append("recursive_operation")
        
        if 'template' in keywords:
            capabilities["special_features"].append("template_based")
        
        return capabilities
    
    async def _analyze_tool_dependencies(self, tool: Dict[str, Any]) -> List[str]:
        """Analyse les dépendances d'un outil."""
        
        dependencies = []
        tool_type = tool.get('type', '')
        keywords = tool.get('keywords', [])
        
        # Dépendances basées sur le type
        type_dependencies = {
            "divination": ["file_system", "search_engine"],
            "transmutation": ["template_engine", "content_processor"],
            "protection": ["backup_system", "validation_engine"],
            "invocation": ["process_manager", "orchestration_engine"]
        }
        
        if tool_type in type_dependencies:
            dependencies.extend(type_dependencies[tool_type])
        
        # Dépendances basées sur les mots-clés
        if 'regex' in keywords:
            dependencies.append("regex_engine")
        
        if 'template' in keywords:
            dependencies.append("template_system")
        
        if 'file' in keywords:
            dependencies.append("file_system")
        
        return list(set(dependencies))  # Suppression des doublons
    
    async def _identify_synergy_partners(self, tool: Dict[str, Any]) -> List[str]:
        """Identifie les partenaires de synergie d'un outil."""
        
        synergy_partners = []
        tool_type = tool.get('type', '')
        keywords = tool.get('keywords', [])
        
        # Synergies basées sur le type
        type_synergies = {
            "divination": ["analysis", "transmutation"],
            "transmutation": ["divination", "protection"],
            "protection": ["transmutation", "utility"],
            "invocation": ["divination", "transmutation", "protection"]
        }
        
        if tool_type in type_synergies:
            # Recherche d'outils dans les catégories synergiques
            all_tools = await self._get_all_tools()
            for other_tool in all_tools:
                if other_tool.get('type') in type_synergies[tool_type]:
                    synergy_partners.append(other_tool.get('tool_id', ''))
        
        return synergy_partners[:5]  # Limite à 5 partenaires principaux
    
    async def _identify_usage_patterns(self, tool: Dict[str, Any]) -> List[str]:
        """Identifie les patterns d'usage d'un outil."""
        
        patterns = []
        tool_type = tool.get('type', '')
        intent = tool.get('intent', '').lower()
        
        # Patterns basés sur l'intention
        if 'search' in intent:
            patterns.append("search_and_discover")
        
        if 'generate' in intent or 'create' in intent:
            patterns.append("content_generation")
        
        if 'analyze' in intent:
            patterns.append("analysis_and_inspection")
        
        if 'backup' in intent or 'save' in intent:
            patterns.append("data_protection")
        
        # Patterns basés sur le type
        type_patterns = {
            "divination": ["exploratory_analysis", "information_gathering"],
            "transmutation": ["content_transformation", "format_conversion"],
            "protection": ["safety_first", "validation_workflow"],
            "invocation": ["orchestrated_execution", "automated_workflow"]
        }
        
        if tool_type in type_patterns:
            patterns.extend(type_patterns[tool_type])
        
        return list(set(patterns))
    
    async def _identify_tool_integration_points(self, tool: Dict[str, Any]) -> List[str]:
        """Identifie les points d'intégration d'un outil."""
        
        integration_points = []
        tool_type = tool.get('type', '')
        
        # Points d'intégration standard
        integration_points.append(f"tool_ecosystem -> {tool_type}_category")
        integration_points.append(f"orchestration_engine -> {tool.get('tool_id', 'unknown')}")
        
        # Points d'intégration spécifiques
        if tool_type == "divination":
            integration_points.extend([
                "memory_engine -> search_integration",
                "editing_session -> content_discovery"
            ])
        elif tool_type == "transmutation":
            integration_points.extend([
                "prompt_engine -> content_generation",
                "template_system -> transformation_pipeline"
            ])
        elif tool_type == "protection":
            integration_points.extend([
                "backup_system -> data_safety",
                "validation_engine -> quality_assurance"
            ])
        
        return integration_points
    
    async def _get_all_tools(self) -> List[Dict[str, Any]]:
        """Récupère tous les outils disponibles."""
        
        all_tools = []
        
        # Tentative de récupération via le cache
        if hasattr(self.tools, '_tool_cache') and self.tools._tool_cache:
            all_tools = list(self.tools._tool_cache.values())
        else:
            # Fallback : exploration manuelle
            print("🔍 Exploration manuelle des outils...")
            
            # Catégories connues
            known_categories = ["divination", "transmutation", "protection", "invocation", "utility"]
            
            for category in known_categories:
                try:
                    category_tools = self.tools.find_tools_by_type(category)
                    all_tools.extend(category_tools)
                except Exception as e:
                    print(f"⚠️ Erreur exploration catégorie {category}: {e}")
        
        return all_tools
    
    async def _analyze_category_capabilities(self, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse les capacités d'une catégorie d'outils."""
        
        capabilities = {
            "total_tools": len(tools),
            "complexity_distribution": {"basic": 0, "intermediate": 0, "advanced": 0},
            "common_keywords": {},
            "capability_coverage": []
        }
        
        # Distribution de complexité
        for tool in tools:
            level = tool.get('level', 'basic')
            if level in capabilities["complexity_distribution"]:
                capabilities["complexity_distribution"][level] += 1
        
        # Mots-clés communs
        all_keywords = []
        for tool in tools:
            all_keywords.extend(tool.get('keywords', []))
        
        # Comptage des mots-clés
        keyword_counts = {}
        for keyword in all_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Top 5 mots-clés
        capabilities["common_keywords"] = dict(
            sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        )
        
        return capabilities
    
    async def _identify_category_integration_patterns(self, category: str) -> List[str]:
        """Identifie les patterns d'intégration d'une catégorie."""
        
        patterns = {
            "divination": [
                "search_first_workflow",
                "discovery_driven_analysis",
                "information_gathering_pipeline"
            ],
            "transmutation": [
                "transformation_pipeline",
                "content_generation_workflow",
                "format_conversion_chain"
            ],
            "protection": [
                "safety_first_pattern",
                "backup_before_action",
                "validation_checkpoint"
            ],
            "invocation": [
                "orchestration_pattern",
                "automated_workflow",
                "coordination_hub"
            ]
        }
        
        return patterns.get(category, ["generic_integration_pattern"])
    
    async def _explore_tool_dependencies(self) -> Dict[str, Any]:
        """Exploration récursive des dépendances d'outils."""
        
        dependency_graph = {}
        all_tools = await self._get_all_tools()
        
        print(f"🔗 Analyse des dépendances pour {len(all_tools)} outils...")
        
        for tool in all_tools:
            tool_id = tool.get('tool_id', 'unknown')
            
            # Analyse des dépendances directes
            direct_deps = await self._analyze_tool_dependencies(tool)
            
            # Exploration récursive
            recursive_deps = await self._explore_recursive_dependencies(
                tool_id, depth=self.exploration_depth
            )
            
            # Analyse de la position dans le graphe
            dependency_analysis = await self._analyze_dependency_position(tool_id, direct_deps)
            
            dependency_graph[tool_id] = {
                "direct_dependencies": direct_deps,
                "recursive_dependencies": recursive_deps,
                "dependency_depth": len(recursive_deps),
                "is_leaf": len(direct_deps) == 0,
                "is_root": await self._is_root_tool(tool_id),
                "centrality_score": dependency_analysis.get("centrality", 0.0),
                "dependency_type": dependency_analysis.get("type", "intermediate")
            }
        
        return dependency_graph
    
    async def _explore_recursive_dependencies(self, tool_id: str, 
                                           depth: int, 
                                           visited: Set[str] = None) -> List[str]:
        """Explore récursivement les dépendances d'un outil."""
        
        if visited is None:
            visited = set()
        
        if depth <= 0 or tool_id in visited:
            return []
        
        visited.add(tool_id)
        recursive_deps = []
        
        # Récupération de l'outil
        tool = self.tools.get_tool_info(tool_id)
        if tool:
            direct_deps = await self._analyze_tool_dependencies(tool)
            
            for dep in direct_deps:
                if dep not in visited:
                    recursive_deps.append(dep)
                    # Exploration récursive
                    sub_deps = await self._explore_recursive_dependencies(
                        dep, depth - 1, visited.copy()
                    )
                    recursive_deps.extend(sub_deps)
        
        return list(set(recursive_deps))  # Suppression des doublons
    
    async def _analyze_dependency_position(self, tool_id: str, 
                                         dependencies: List[str]) -> Dict[str, Any]:
        """Analyse la position d'un outil dans le graphe de dépendances."""
        
        analysis = {
            "centrality": 0.0,
            "type": "intermediate"
        }
        
        # Calcul simple de centralité basé sur le nombre de dépendances
        dep_count = len(dependencies)
        
        if dep_count == 0:
            analysis["type"] = "leaf"
            analysis["centrality"] = 0.1
        elif dep_count > 5:
            analysis["type"] = "hub"
            analysis["centrality"] = 0.9
        else:
            analysis["type"] = "intermediate"
            analysis["centrality"] = dep_count / 10.0
        
        return analysis
    
    async def _is_root_tool(self, tool_id: str) -> bool:
        """Détermine si un outil est un outil racine."""
        
        # Un outil racine est un outil qui n'est dépendance d'aucun autre
        all_tools = await self._get_all_tools()
        
        for tool in all_tools:
            if tool.get('tool_id') != tool_id:
                deps = await self._analyze_tool_dependencies(tool)
                if tool_id in deps:
                    return False
        
        return True
    
    async def _map_tool_synergies(self) -> Dict[str, Any]:
        """Cartographie des synergies entre outils."""
        
        synergy_map = {
            "synergy_pairs": {},
            "synergy_clusters": {},
            "optimal_combinations": [],
            "synergy_strength": {}
        }
        
        all_tools = await self._get_all_tools()
        
        # Analyse des paires de synergie
        for i, tool1 in enumerate(all_tools):
            tool1_id = tool1.get('tool_id', '')
            synergy_map["synergy_pairs"][tool1_id] = []
            
            for j, tool2 in enumerate(all_tools[i+1:], i+1):
                tool2_id = tool2.get('tool_id', '')
                
                synergy_strength = await self._calculate_synergy_strength(tool1, tool2)
                
                if synergy_strength > 0.5:  # Seuil de synergie
                    synergy_map["synergy_pairs"][tool1_id].append({
                        "partner": tool2_id,
                        "strength": synergy_strength,
                        "synergy_type": await self._identify_synergy_type(tool1, tool2)
                    })
        
        return synergy_map
    
    async def _calculate_synergy_strength(self, tool1: Dict, tool2: Dict) -> float:
        """Calcule la force de synergie entre deux outils."""
        
        strength = 0.0
        
        # Synergie basée sur les types complémentaires
        type_synergies = {
            ("divination", "transmutation"): 0.8,
            ("divination", "analysis"): 0.7,
            ("transmutation", "protection"): 0.6,
            ("protection", "utility"): 0.5
        }
        
        type1, type2 = tool1.get('type', ''), tool2.get('type', '')
        strength += type_synergies.get((type1, type2), 0.0)
        strength += type_synergies.get((type2, type1), 0.0)
        
        # Synergie basée sur les mots-clés communs
        keywords1 = set(tool1.get('keywords', []))
        keywords2 = set(tool2.get('keywords', []))
        common_keywords = keywords1.intersection(keywords2)
        
        if common_keywords:
            strength += len(common_keywords) * 0.1
        
        return min(strength, 1.0)  # Limite à 1.0
    
    async def _identify_synergy_type(self, tool1: Dict, tool2: Dict) -> str:
        """Identifie le type de synergie entre deux outils."""
        
        type1, type2 = tool1.get('type', ''), tool2.get('type', '')
        
        synergy_types = {
            ("divination", "transmutation"): "discovery_to_creation",
            ("divination", "analysis"): "search_and_analyze",
            ("transmutation", "protection"): "create_and_protect",
            ("protection", "utility"): "safety_and_support"
        }
        
        return synergy_types.get((type1, type2), 
               synergy_types.get((type2, type1), "complementary"))
    
    async def _analyze_orchestration_patterns(self) -> Dict[str, Any]:
        """Analyse les patterns d'orchestration d'outils."""
        
        patterns = {
            "sequential_patterns": [],
            "parallel_patterns": [],
            "conditional_patterns": [],
            "feedback_patterns": []
        }
        
        # Patterns séquentiels communs
        patterns["sequential_patterns"] = [
            "search -> analyze -> transform",
            "discover -> validate -> protect",
            "generate -> review -> finalize"
        ]
        
        # Patterns parallèles
        patterns["parallel_patterns"] = [
            "multiple_search_strategies",
            "parallel_analysis_approaches",
            "concurrent_validation_checks"
        ]
        
        return patterns
    
    async def _calculate_completeness_score(self, categories: Dict, 
                                          metadata: Dict, 
                                          dependencies: Dict) -> float:
        """Calcule un score de complétude du registre d'outils."""
        
        score = 0.0
        
        # Score basé sur la diversité des catégories
        category_count = len(categories)
        score += min(category_count / 5.0, 1.0) * 0.3  # Max 5 catégories attendues
        
        # Score basé sur le nombre total d'outils
        total_tools = sum(cat.get('tool_count', 0) for cat in categories.values())
        score += min(total_tools / 20.0, 1.0) * 0.4  # Max 20 outils attendus
        
        # Score basé sur la richesse des dépendances
        dependency_richness = len(dependencies) / max(total_tools, 1)
        score += min(dependency_richness, 1.0) * 0.3
        
        return score

# Fonction utilitaire pour l'exploration standalone
async def explore_tool_registry_standalone(tool_memory_extension=None) -> ToolRegistryExploration:
    """
    Fonction utilitaire pour l'exploration standalone du registre d'outils.
    
    Args:
        tool_memory_extension: Instance optionnelle de ToolMemoryExtension
        
    Returns:
        ToolRegistryExploration: Résultat de l'exploration
    """
    
    explorer = ToolRegistryExplorer(tool_memory_extension)
    return await explorer.explore_tool_registry()

if __name__ == "__main__":
    # Test standalone
    async def test_tool_exploration():
        print("🛠️ Test de l'explorateur de registre d'outils...")
        
        explorer = ToolRegistryExplorer()
        result = await explorer.explore_tool_registry()
        
        print(f"✅ Exploration terminée :")
        print(f"   - Catégories : {len(result.categories)}")
        print(f"   - Score complétude : {result.completeness_score:.2f}")
        print(f"   - Timestamp : {result.exploration_timestamp}")
    
    asyncio.run(test_tool_exploration())
