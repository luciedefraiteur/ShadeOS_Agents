#!/usr/bin/env python3
"""
⛧ MemoryEngine - Composants Temporels ⛧

Composants temporels : TemporalNode, TemporalRegistry, TemporalVirtualLayer
Implémentation progressive sans affecter l'existant.
"""

import time
import json
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod
from pathlib import Path

from .temporal_base import (
    BaseTemporalEntity, TemporalDimension, FractalLinks, 
    ConsciousnessInterface, UnifiedTemporalIndex, register_temporal_entity
)


class TemporalNode(BaseTemporalEntity):
    """Nœud fractal avec dimension temporelle universelle"""
    
    def __init__(self, content: str, node_type: str, metadata: Dict[str, Any] = None):
        super().__init__(f"temporal_node_{node_type}", content)
        self.node_type = node_type
        self.metadata = metadata or {}
        self.usage_count = 0
        self.last_accessed = time.time()
        
        # Enregistrement automatique dans l'index temporel
        register_temporal_entity(self)
    
    def access_node(self):
        """Accès au nœud avec tracking temporel"""
        self.usage_count += 1
        self.last_accessed = time.time()
        
        # Évolution basée sur l'usage
        self.temporal_dimension.evolve("node_accessed", {
            "usage_count": self.usage_count,
            "access_timestamp": self.last_accessed
        })
    
    def update_metadata(self, new_metadata: Dict[str, Any]):
        """Mise à jour des métadonnées avec évolution temporelle"""
        old_metadata = self.metadata.copy()
        self.metadata.update(new_metadata)
        
        self.temporal_dimension.evolve("metadata_updated", {
            "old_metadata": old_metadata,
            "new_metadata": self.metadata
        })
    
    def get_entity_specific_data(self) -> Dict[str, Any]:
        """Données spécifiques au nœud temporel"""
        return {
            "node_type": self.node_type,
            "metadata": self.metadata,
            "usage_count": self.usage_count,
            "last_accessed": self.last_accessed
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire avec données spécifiques"""
        base_dict = super().to_dict()
        base_dict.update(self.get_entity_specific_data())
        return base_dict


class TemporalRegistry(BaseTemporalEntity):
    """Registre avec dimension temporelle et auto-organisation"""
    
    def __init__(self, registry_type: str, auto_organize: bool = True):
        super().__init__(f"temporal_registry_{registry_type}", "")
        self.registry_type = registry_type
        self.entities: Dict[str, TemporalNode] = {}
        self.auto_organization_rules: List[Dict[str, Any]] = []
        self.auto_organize = auto_organize
        self.organization_stats = {
            "last_organized": None,
            "organization_count": 0,
            "entities_added": 0,
            "entities_removed": 0
        }
        
        # Enregistrement automatique dans l'index temporel
        register_temporal_entity(self)
    
    def add_entity(self, entity_id: str, entity: TemporalNode):
        """Ajout d'entité avec évolution temporelle"""
        self.temporal_dimension.evolve("entity_added", {
            "entity_id": entity_id,
            "entity_type": entity.node_type,
            "registry_type": self.registry_type
        })
        
        self.entities[entity_id] = entity
        self.organization_stats["entities_added"] += 1
        
        # Auto-organisation si activée
        if self.auto_organize and len(self.entities) % 10 == 0:
            self.auto_organize()
    
    def remove_entity(self, entity_id: str):
        """Suppression d'entité avec évolution temporelle"""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            self.temporal_dimension.evolve("entity_removed", {
                "entity_id": entity_id,
                "entity_type": entity.node_type
            })
            
            del self.entities[entity_id]
            self.organization_stats["entities_removed"] += 1
    
    def get_entity(self, entity_id: str) -> Optional[TemporalNode]:
        """Récupère une entité avec tracking d'accès"""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            entity.access_node()
            return entity
        return None
    
    def get_entities_by_type(self, node_type: str) -> List[TemporalNode]:
        """Récupère toutes les entités d'un type donné"""
        return [
            entity for entity in self.entities.values()
            if entity.node_type == node_type
        ]
    
    def get_entities_by_consciousness_level(self, min_level: float) -> List[TemporalNode]:
        """Récupère les entités avec un niveau de conscience minimum"""
        return [
            entity for entity in self.entities.values()
            if entity.get_consciousness_level() >= min_level
        ]
    
    def auto_organize(self):
        """Auto-organisation du registre"""
        if self.temporal_dimension.consciousness_level > 0.7:
            self._apply_auto_organization_rules()
            self._optimize_structure()
            
            self.organization_stats["last_organized"] = time.time()
            self.organization_stats["organization_count"] += 1
            
            self.temporal_dimension.evolve("registry_organized", {
                "organization_stats": self.organization_stats.copy()
            })
    
    def _apply_auto_organization_rules(self):
        """Applique les règles d'auto-organisation"""
        for rule in self.auto_organization_rules:
            rule_type = rule.get("type")
            if rule_type == "consciousness_based":
                self._organize_by_consciousness(rule)
            elif rule_type == "usage_based":
                self._organize_by_usage(rule)
            elif rule_type == "type_based":
                self._organize_by_type(rule)
    
    def _organize_by_consciousness(self, rule: Dict[str, Any]):
        """Organisation basée sur le niveau de conscience"""
        threshold = rule.get("threshold", 0.5)
        high_consciousness_entities = self.get_entities_by_consciousness_level(threshold)
        
        # Logique d'organisation spécifique
        for entity in high_consciousness_entities:
            entity.auto_improve_content()
    
    def _organize_by_usage(self, rule: Dict[str, Any]):
        """Organisation basée sur l'usage"""
        min_usage = rule.get("min_usage", 5)
        frequently_used = [
            entity for entity in self.entities.values()
            if entity.usage_count >= min_usage
        ]
        
        # Optimisation des entités fréquemment utilisées
        for entity in frequently_used:
            entity.learn_from_interaction({
                "type": "frequent_usage",
                "usage_count": entity.usage_count
            })
    
    def _organize_by_type(self, rule: Dict[str, Any]):
        """Organisation basée sur le type"""
        target_type = rule.get("target_type")
        if target_type:
            type_entities = self.get_entities_by_type(target_type)
            # Logique d'organisation spécifique au type
    
    def _optimize_structure(self):
        """Optimisation de la structure du registre"""
        # Suppression des entités obsolètes
        current_time = time.time()
        obsolete_threshold = current_time - (30 * 24 * 3600)  # 30 jours
        
        obsolete_entities = [
            entity_id for entity_id, entity in self.entities.items()
            if entity.last_accessed < obsolete_threshold and entity.usage_count < 3
        ]
        
        for entity_id in obsolete_entities:
            self.remove_entity(entity_id)
    
    def add_organization_rule(self, rule: Dict[str, Any]):
        """Ajoute une règle d'auto-organisation"""
        self.auto_organization_rules.append(rule)
        self.temporal_dimension.evolve("organization_rule_added", rule)
    
    def get_entity_specific_data(self) -> Dict[str, Any]:
        """Données spécifiques au registre temporel"""
        return {
            "registry_type": self.registry_type,
            "entity_count": len(self.entities),
            "auto_organize": self.auto_organize,
            "organization_stats": self.organization_stats,
            "organization_rules_count": len(self.auto_organization_rules)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du registre"""
        return {
            **self.get_entity_specific_data(),
            "consciousness_levels": {
                "high": len(self.get_entities_by_consciousness_level(0.8)),
                "medium": len(self.get_entities_by_consciousness_level(0.5)),
                "low": len(self.get_entities_by_consciousness_level(0.0))
            },
            "entity_types": list(set(entity.node_type for entity in self.entities.values()))
        }


class TemporalVirtualLayer(BaseTemporalEntity):
    """Couche virtuelle avec dimension temporelle et adaptation"""
    
    def __init__(self, layer_type: str, memory_engine=None, auto_adapt: bool = True):
        super().__init__(f"temporal_virtual_layer_{layer_type}", "")
        self.layer_type = layer_type
        self.memory_engine = memory_engine
        self.auto_adapt = auto_adapt
        self.adaptation_patterns: List[Dict[str, Any]] = []
        self.usage_metrics = {
            "access_count": 0,
            "last_accessed": None,
            "adaptation_count": 0,
            "performance_metrics": {}
        }
        
        # Enregistrement automatique dans l'index temporel
        register_temporal_entity(self)
    
    def access_layer(self, access_type: str = "general"):
        """Accès à la couche avec tracking temporel"""
        self.usage_metrics["access_count"] += 1
        self.usage_metrics["last_accessed"] = time.time()
        
        self.temporal_dimension.evolve("layer_accessed", {
            "access_type": access_type,
            "access_count": self.usage_metrics["access_count"],
            "access_timestamp": self.usage_metrics["last_accessed"]
        })
    
    def adapt_to_usage(self, usage_pattern: Dict[str, Any]):
        """Adaptation de la couche selon les patterns d'usage"""
        self.temporal_dimension.evolve("usage_adaptation", usage_pattern)
        self._update_adaptation_patterns(usage_pattern)
        
        if self.auto_adapt:
            self._apply_adaptation_patterns(usage_pattern)
    
    def _update_adaptation_patterns(self, usage_pattern: Dict[str, Any]):
        """Met à jour les patterns d'adaptation"""
        pattern_type = usage_pattern.get("type", "unknown")
        
        # Recherche d'un pattern existant
        existing_pattern = None
        for pattern in self.adaptation_patterns:
            if pattern.get("type") == pattern_type:
                existing_pattern = pattern
                break
        
        if existing_pattern:
            # Mise à jour du pattern existant
            existing_pattern["count"] = existing_pattern.get("count", 0) + 1
            existing_pattern["last_used"] = time.time()
            existing_pattern["data"].update(usage_pattern.get("data", {}))
        else:
            # Création d'un nouveau pattern
            new_pattern = {
                "type": pattern_type,
                "count": 1,
                "created_at": time.time(),
                "last_used": time.time(),
                "data": usage_pattern.get("data", {})
            }
            self.adaptation_patterns.append(new_pattern)
    
    def _apply_adaptation_patterns(self, usage_pattern: Dict[str, Any]):
        """Applique les patterns d'adaptation"""
        pattern_type = usage_pattern.get("type")
        
        for pattern in self.adaptation_patterns:
            if pattern["type"] == pattern_type and pattern["count"] > 5:
                # Application du pattern d'adaptation
                self._apply_specific_adaptation(pattern)
                self.usage_metrics["adaptation_count"] += 1
    
    def _apply_specific_adaptation(self, pattern: Dict[str, Any]):
        """Applique une adaptation spécifique"""
        adaptation_type = pattern.get("type")
        
        if adaptation_type == "performance_optimization":
            self._optimize_performance(pattern["data"])
        elif adaptation_type == "memory_optimization":
            self._optimize_memory(pattern["data"])
        elif adaptation_type == "structure_optimization":
            self._optimize_structure(pattern["data"])
    
    def _optimize_performance(self, data: Dict[str, Any]):
        """Optimisation des performances"""
        # Logique d'optimisation des performances
        self.usage_metrics["performance_metrics"]["optimized"] = True
        self.usage_metrics["performance_metrics"]["optimization_timestamp"] = time.time()
    
    def _optimize_memory(self, data: Dict[str, Any]):
        """Optimisation de la mémoire"""
        # Logique d'optimisation de la mémoire
        pass
    
    def _optimize_structure(self, data: Dict[str, Any]):
        """Optimisation de la structure"""
        # Logique d'optimisation de la structure
        pass
    
    def auto_optimize(self):
        """Auto-optimisation basée sur les patterns"""
        if self.temporal_dimension.consciousness_level > 0.8:
            self._apply_optimization_patterns()
            self.temporal_dimension.evolve("layer_optimized", {
                "optimization_timestamp": time.time(),
                "consciousness_level": self.temporal_dimension.consciousness_level
            })
    
    def _apply_optimization_patterns(self):
        """Applique les patterns d'optimisation"""
        # Application des patterns d'optimisation basés sur la conscience
        for pattern in self.adaptation_patterns:
            if pattern["count"] > 10:  # Pattern bien établi
                self._apply_specific_adaptation(pattern)
    
    def get_entity_specific_data(self) -> Dict[str, Any]:
        """Données spécifiques à la couche virtuelle temporelle"""
        return {
            "layer_type": self.layer_type,
            "auto_adapt": self.auto_adapt,
            "adaptation_patterns_count": len(self.adaptation_patterns),
            "usage_metrics": self.usage_metrics
        }
    
    def get_adaptation_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques d'adaptation"""
        return {
            "total_patterns": len(self.adaptation_patterns),
            "frequent_patterns": [
                pattern for pattern in self.adaptation_patterns
                if pattern["count"] > 5
            ],
            "adaptation_count": self.usage_metrics["adaptation_count"],
            "last_adaptation": max(
                [pattern["last_used"] for pattern in self.adaptation_patterns],
                default=None
            )
        }


# Classes spécialisées pour les différents types de couches

class WorkspaceTemporalLayer(TemporalVirtualLayer):
    """Couche temporelle pour l'espace de travail"""
    
    def __init__(self, memory_engine=None):
        super().__init__("workspace", memory_engine)
        self.workspace_patterns = {}
    
    def track_file_access(self, file_path: str, access_type: str):
        """Tracking de l'accès aux fichiers"""
        self.access_layer("file_access")
        
        if file_path not in self.workspace_patterns:
            self.workspace_patterns[file_path] = {
                "access_count": 0,
                "access_types": [],
                "last_accessed": None
            }
        
        self.workspace_patterns[file_path]["access_count"] += 1
        self.workspace_patterns[file_path]["access_types"].append(access_type)
        self.workspace_patterns[file_path]["last_accessed"] = time.time()
        
        self.adapt_to_usage({
            "type": "file_access",
            "data": {
                "file_path": file_path,
                "access_type": access_type,
                "access_count": self.workspace_patterns[file_path]["access_count"]
            }
        })


class GitTemporalLayer(TemporalVirtualLayer):
    """Couche temporelle pour Git"""
    
    def __init__(self, memory_engine=None):
        super().__init__("git", memory_engine)
        self.git_operations = []
    
    def track_git_operation(self, operation: str, details: Dict[str, Any]):
        """Tracking des opérations Git"""
        self.access_layer("git_operation")
        
        git_op = {
            "operation": operation,
            "details": details,
            "timestamp": time.time()
        }
        self.git_operations.append(git_op)
        
        self.adapt_to_usage({
            "type": "git_operation",
            "data": {
                "operation": operation,
                "operation_count": len(self.git_operations)
            }
        })


class TemplateTemporalLayer(TemporalVirtualLayer):
    """Couche temporelle pour les templates"""
    
    def __init__(self, memory_engine=None):
        super().__init__("template", memory_engine)
        self.template_usage = {}
    
    def track_template_usage(self, template_name: str, usage_context: Dict[str, Any]):
        """Tracking de l'usage des templates"""
        self.access_layer("template_usage")
        
        if template_name not in self.template_usage:
            self.template_usage[template_name] = {
                "usage_count": 0,
                "contexts": [],
                "last_used": None
            }
        
        self.template_usage[template_name]["usage_count"] += 1
        self.template_usage[template_name]["contexts"].append(usage_context)
        self.template_usage[template_name]["last_used"] = time.time()
        
        self.adapt_to_usage({
            "type": "template_usage",
            "data": {
                "template_name": template_name,
                "usage_count": self.template_usage[template_name]["usage_count"]
            }
        })


class ToolTemporalLayer(TemporalVirtualLayer):
    """Couche temporelle pour les outils"""
    
    def __init__(self, memory_engine=None):
        super().__init__("tool", memory_engine)
        self.tool_registry = TemporalRegistry("tool_registry")
        self.tool_usage = {}
    
    def track_tool_usage(self, tool_id: str, usage_context: Dict[str, Any]):
        """Tracking de l'usage des outils"""
        self.access_layer("tool_usage")
        
        if tool_id not in self.tool_usage:
            self.tool_usage[tool_id] = {
                "usage_count": 0,
                "contexts": [],
                "last_used": None
            }
        
        self.tool_usage[tool_id]["usage_count"] += 1
        self.tool_usage[tool_id]["contexts"].append(usage_context)
        self.tool_usage[tool_id]["last_used"] = time.time()
        
        self.adapt_to_usage({
            "type": "tool_usage",
            "data": {
                "tool_id": tool_id,
                "usage_count": self.tool_usage[tool_id]["usage_count"]
            }
        }) 