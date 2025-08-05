#!/usr/bin/env python3
"""
⛧ MemoryEngine - Auto-Improvement Engine ⛧

Moteur d'auto-amélioration global pour le système temporel.
Implémentation progressive sans affecter l'existant.
"""

import time
import json
from typing import List, Dict, Any, Optional, Union, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

from .temporal_base import (
    BaseTemporalEntity, TemporalDimension, ConsciousnessLevel,
    UnifiedTemporalIndex, get_temporal_index
)
from .temporal_components import TemporalNode, TemporalRegistry, TemporalVirtualLayer


class ImprovementTrigger(Enum):
    """Types de déclencheurs d'amélioration"""
    USAGE_FREQUENCY = "usage_frequency"
    QUALITY_FEEDBACK = "quality_feedback"
    PATTERN_EMERGENCE = "pattern_emergence"
    CONSCIOUSNESS_THRESHOLD = "consciousness_threshold"
    TEMPORAL_EVOLUTION = "temporal_evolution"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    MEMORY_PRESSURE = "memory_pressure"
    STRUCTURE_COMPLEXITY = "structure_complexity"


@dataclass
class ImprovementRule:
    """Règle d'amélioration avec conditions et actions"""
    
    rule_id: str
    trigger_type: ImprovementTrigger
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    priority: int = 1
    enabled: bool = True
    last_triggered: Optional[float] = None
    trigger_count: int = 0
    
    def should_trigger(self, context: Dict[str, Any]) -> bool:
        """Détermine si la règle doit être déclenchée"""
        if not self.enabled:
            return False
        
        # Vérification des conditions
        for condition_key, condition_value in self.conditions.items():
            if condition_key not in context:
                return False
            
            context_value = context[condition_key]
            
            # Comparaison selon le type de condition
            if isinstance(condition_value, dict):
                # Condition complexe avec opérateur
                operator = condition_value.get("operator", "eq")
                target_value = condition_value.get("value")
                
                if operator == "eq" and context_value != target_value:
                    return False
                elif operator == "gt" and context_value <= target_value:
                    return False
                elif operator == "lt" and context_value >= target_value:
                    return False
                elif operator == "gte" and context_value < target_value:
                    return False
                elif operator == "lte" and context_value > target_value:
                    return False
                elif operator == "in" and context_value not in target_value:
                    return False
            else:
                # Condition simple d'égalité
                if context_value != condition_value:
                    return False
        
        return True
    
    def execute_actions(self, entity: BaseTemporalEntity, context: Dict[str, Any]):
        """Exécute les actions de la règle"""
        for action in self.actions:
            action_type = action.get("type")
            action_params = action.get("params", {})
            
            if action_type == "auto_improve_content":
                entity.auto_improve_content()
            elif action_type == "learn_from_interaction":
                entity.learn_from_interaction(action_params)
            elif action_type == "evolve_content":
                new_content = action_params.get("new_content")
                trigger = action_params.get("trigger", "rule_triggered")
                if new_content:
                    entity.evolve_content(new_content, trigger)
            elif action_type == "update_metadata":
                metadata = action_params.get("metadata", {})
                if hasattr(entity, 'update_metadata'):
                    entity.update_metadata(metadata)
            elif action_type == "custom_action":
                # Action personnalisée via callback
                callback = action_params.get("callback")
                if callback and callable(callback):
                    callback(entity, context)
        
        # Mise à jour des statistiques de la règle
        self.last_triggered = time.time()
        self.trigger_count += 1


class AutoImprovementEngine:
    """Moteur d'auto-amélioration global"""
    
    def __init__(self, memory_engine=None):
        self.memory_engine = memory_engine
        self.improvement_rules: List[ImprovementRule] = []
        self.consciousness_threshold = 0.6
        self.auto_improvement_enabled = True
        self.improvement_stats = {
            "total_improvements": 0,
            "improvements_by_trigger": {},
            "last_improvement": None,
            "entities_improved": set()
        }
        
        # Initialisation des règles par défaut
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialise les règles d'amélioration par défaut"""
        
        # Règle 1: Amélioration basée sur la fréquence d'usage
        usage_frequency_rule = ImprovementRule(
            rule_id="usage_frequency_improvement",
            trigger_type=ImprovementTrigger.USAGE_FREQUENCY,
            conditions={
                "usage_count": {"operator": "gte", "value": 10},
                "consciousness_level": {"operator": "gte", "value": 0.3}
            },
            actions=[
                {"type": "auto_improve_content"},
                {"type": "learn_from_interaction", "params": {
                    "type": "frequent_usage",
                    "usage_count": "{usage_count}"
                }}
            ],
            priority=1
        )
        self.add_improvement_rule(usage_frequency_rule)
        
        # Règle 2: Amélioration basée sur le feedback qualité
        quality_feedback_rule = ImprovementRule(
            rule_id="quality_feedback_improvement",
            trigger_type=ImprovementTrigger.QUALITY_FEEDBACK,
            conditions={
                "quality_score": {"operator": "lt", "value": 0.7},
                "consciousness_level": {"operator": "gte", "value": 0.4}
            },
            actions=[
                {"type": "auto_improve_content"},
                {"type": "learn_from_interaction", "params": {
                    "type": "quality_improvement",
                    "quality_score": "{quality_score}"
                }}
            ],
            priority=2
        )
        self.add_improvement_rule(quality_feedback_rule)
        
        # Règle 3: Amélioration basée sur l'émergence de patterns
        pattern_emergence_rule = ImprovementRule(
            rule_id="pattern_emergence_improvement",
            trigger_type=ImprovementTrigger.PATTERN_EMERGENCE,
            conditions={
                "pattern_count": {"operator": "gte", "value": 5},
                "consciousness_level": {"operator": "gte", "value": 0.5}
            },
            actions=[
                {"type": "auto_improve_content"},
                {"type": "learn_from_interaction", "params": {
                    "type": "pattern_recognition",
                    "pattern_count": "{pattern_count}"
                }}
            ],
            priority=3
        )
        self.add_improvement_rule(pattern_emergence_rule)
        
        # Règle 4: Amélioration basée sur le seuil de conscience
        consciousness_threshold_rule = ImprovementRule(
            rule_id="consciousness_threshold_improvement",
            trigger_type=ImprovementTrigger.CONSCIOUSNESS_THRESHOLD,
            conditions={
                "consciousness_level": {"operator": "gte", "value": 0.8}
            },
            actions=[
                {"type": "auto_improve_content"},
                {"type": "learn_from_interaction", "params": {
                    "type": "consciousness_expansion",
                    "consciousness_level": "{consciousness_level}"
                }}
            ],
            priority=4
        )
        self.add_improvement_rule(consciousness_threshold_rule)
    
    def add_improvement_rule(self, rule: ImprovementRule):
        """Ajoute une règle d'amélioration"""
        self.improvement_rules.append(rule)
        self.improvement_rules.sort(key=lambda r: r.priority, reverse=True)
    
    def remove_improvement_rule(self, rule_id: str):
        """Supprime une règle d'amélioration"""
        self.improvement_rules = [r for r in self.improvement_rules if r.rule_id != rule_id]
    
    def trigger_improvement(self, entity: BaseTemporalEntity, trigger: ImprovementTrigger, context: Dict[str, Any] = None):
        """Déclenche une amélioration sur une entité"""
        if not self.auto_improvement_enabled:
            return False
        
        context = context or {}
        
        # Ajout du contexte de base
        base_context = {
            "entity_id": entity.id,
            "entity_type": entity.entity_type,
            "consciousness_level": entity.get_consciousness_level(),
            "trigger_type": trigger.value
        }
        context.update(base_context)
        
        # Vérification et exécution des règles
        improvements_made = False
        
        for rule in self.improvement_rules:
            if rule.trigger_type == trigger and rule.should_trigger(context):
                try:
                    rule.execute_actions(entity, context)
                    improvements_made = True
                    
                    # Mise à jour des statistiques
                    self._update_improvement_stats(trigger, entity.id)
                    
                except Exception as e:
                    print(f"Erreur lors de l'exécution de la règle {rule.rule_id}: {e}")
        
        return improvements_made
    
    def global_optimization(self):
        """Optimisation globale du système"""
        if not self.auto_improvement_enabled:
            return
        
        temporal_index = get_temporal_index()
        entities = temporal_index.temporal_entities.values()
        
        optimization_count = 0
        
        for entity in entities:
            if entity.temporal_dimension.consciousness_level > self.consciousness_threshold:
                # Déclenchement de l'amélioration basée sur la conscience
                context = {
                    "consciousness_level": entity.get_consciousness_level(),
                    "entity_type": entity.entity_type
                }
                
                if self.trigger_improvement(entity, ImprovementTrigger.CONSCIOUSNESS_THRESHOLD, context):
                    optimization_count += 1
        
        # Mise à jour des statistiques
        self.improvement_stats["total_improvements"] += optimization_count
        self.improvement_stats["last_improvement"] = time.time()
        
        return optimization_count
    
    def monitor_and_improve(self):
        """Surveillance et amélioration continue"""
        if not self.auto_improvement_enabled:
            return
        
        temporal_index = get_temporal_index()
        
        # Surveillance des entités par type
        for entity_type, entity_ids in temporal_index.entity_type_index.items():
            entities = [temporal_index.temporal_entities[entity_id] for entity_id in entity_ids]
            
            # Analyse des patterns d'usage
            usage_patterns = self._analyze_usage_patterns(entities)
            
            # Déclenchement d'améliorations basées sur les patterns
            for entity in entities:
                if entity.usage_count > 5:  # Seuil d'usage minimum
                    context = {
                        "usage_count": entity.usage_count,
                        "usage_patterns": usage_patterns,
                        "entity_type": entity_type
                    }
                    
                    self.trigger_improvement(entity, ImprovementTrigger.USAGE_FREQUENCY, context)
    
    def _analyze_usage_patterns(self, entities: List[BaseTemporalEntity]) -> Dict[str, Any]:
        """Analyse les patterns d'usage des entités"""
        patterns = {
            "total_entities": len(entities),
            "high_usage_entities": 0,
            "low_usage_entities": 0,
            "average_usage": 0,
            "consciousness_distribution": {
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }
        
        if not entities:
            return patterns
        
        total_usage = sum(getattr(entity, 'usage_count', 0) for entity in entities)
        patterns["average_usage"] = total_usage / len(entities)
        
        for entity in entities:
            usage_count = getattr(entity, 'usage_count', 0)
            consciousness_level = entity.get_consciousness_level()
            
            if usage_count > 10:
                patterns["high_usage_entities"] += 1
            elif usage_count < 3:
                patterns["low_usage_entities"] += 1
            
            if consciousness_level >= 0.8:
                patterns["consciousness_distribution"]["high"] += 1
            elif consciousness_level >= 0.5:
                patterns["consciousness_distribution"]["medium"] += 1
            else:
                patterns["consciousness_distribution"]["low"] += 1
        
        return patterns
    
    def _update_improvement_stats(self, trigger: ImprovementTrigger, entity_id: str):
        """Met à jour les statistiques d'amélioration"""
        trigger_value = trigger.value
        
        if trigger_value not in self.improvement_stats["improvements_by_trigger"]:
            self.improvement_stats["improvements_by_trigger"][trigger_value] = 0
        
        self.improvement_stats["improvements_by_trigger"][trigger_value] += 1
        self.improvement_stats["total_improvements"] += 1
        self.improvement_stats["last_improvement"] = time.time()
        self.improvement_stats["entities_improved"].add(entity_id)
    
    def get_improvement_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques d'amélioration"""
        stats = self.improvement_stats.copy()
        stats["entities_improved"] = list(stats["entities_improved"])
        stats["rules_count"] = len(self.improvement_rules)
        stats["enabled_rules"] = len([r for r in self.improvement_rules if r.enabled])
        
        return stats
    
    def enable_auto_improvement(self):
        """Active l'auto-amélioration"""
        self.auto_improvement_enabled = True
    
    def disable_auto_improvement(self):
        """Désactive l'auto-amélioration"""
        self.auto_improvement_enabled = False
    
    def set_consciousness_threshold(self, threshold: float):
        """Définit le seuil de conscience pour l'auto-amélioration"""
        self.consciousness_threshold = max(0.0, min(1.0, threshold))


# Instance globale du moteur d'auto-amélioration
_auto_improvement_engine = AutoImprovementEngine()


def get_auto_improvement_engine() -> AutoImprovementEngine:
    """Récupère l'instance globale du moteur d'auto-amélioration"""
    return _auto_improvement_engine


def trigger_entity_improvement(entity: BaseTemporalEntity, trigger: ImprovementTrigger, context: Dict[str, Any] = None):
    """Déclenche une amélioration sur une entité via le moteur global"""
    return _auto_improvement_engine.trigger_improvement(entity, trigger, context)


def run_global_optimization():
    """Lance l'optimisation globale via le moteur global"""
    return _auto_improvement_engine.global_optimization()


def monitor_and_improve_system():
    """Surveille et améliore le système via le moteur global"""
    return _auto_improvement_engine.monitor_and_improve() 