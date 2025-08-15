#!/usr/bin/env python3
"""
⛧ MemoryEngine - Base Temporelle Universelle ⛧

Base classes pour la dimension temporelle universelle.
Implémentation progressive sans affecter l'existant.
"""

import time
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod
from enum import Enum
import uuid


class ConsciousnessLevel(Enum):
    """Niveaux de conscience pour l'auto-amélioration"""
    BASIC_LEARNING = 0.3
    PATTERN_RECOGNITION = 0.5
    CONTENT_IMPROVEMENT = 0.6
    STRUCTURE_OPTIMIZATION = 0.7
    CONSCIOUSNESS_EXPANSION = 0.8
    SELF_IMPROVEMENT = 0.9


@dataclass
class TemporalDimension:
    """Dimension temporelle universelle pour tous les composants"""
    
    created_at: float = field(default_factory=time.time)
    modified_at: float = field(default_factory=time.time)
    version: str = "1.0.0"
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)
    auto_improvement_triggers: List[str] = field(default_factory=list)
    consciousness_level: float = 0.0
    entity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def evolve(self, trigger: str, changes: Dict[str, Any]):
        """Évolution temporelle du composant"""
        evolution_entry = {
            "timestamp": time.time(),
            "trigger": trigger,
            "changes": changes,
            "consciousness_level": self.consciousness_level
        }
        self.evolution_history.append(evolution_entry)
        self.modified_at = time.time()
        
        # Mise à jour du niveau de conscience basée sur l'évolution
        self._update_consciousness_level(trigger, changes)
    
    def auto_improve(self):
        """Auto-amélioration basée sur les triggers"""
        if self.consciousness_level >= ConsciousnessLevel.CONTENT_IMPROVEMENT.value:
            self.auto_improvement_triggers.append("consciousness_threshold_reached")
            return True
        return False
    
    def _update_consciousness_level(self, trigger: str, changes: Dict[str, Any]):
        """Met à jour le niveau de conscience basé sur l'évolution"""
        # Logique simple d'augmentation progressive
        if trigger == "auto_improvement":
            self.consciousness_level = min(1.0, self.consciousness_level + 0.1)
        elif trigger == "learning_interaction":
            self.consciousness_level = min(1.0, self.consciousness_level + 0.05)
        elif trigger == "pattern_recognition":
            self.consciousness_level = min(1.0, self.consciousness_level + 0.02)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation"""
        return {
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "version": self.version,
            "evolution_history": self.evolution_history,
            "auto_improvement_triggers": self.auto_improvement_triggers,
            "consciousness_level": self.consciousness_level,
            "entity_id": self.entity_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemporalDimension':
        """Crée depuis un dictionnaire"""
        return cls(**data)


@dataclass
class FractalLinks:
    """Liens fractals entre entités temporelles"""
    
    parent_links: List[str] = field(default_factory=list)
    child_links: List[str] = field(default_factory=list)
    sibling_links: List[str] = field(default_factory=list)
    consciousness_links: List[str] = field(default_factory=list)
    
    def add_parent_link(self, parent_id: str):
        """Ajoute un lien parent"""
        if parent_id not in self.parent_links:
            self.parent_links.append(parent_id)
    
    def add_child_link(self, child_id: str):
        """Ajoute un lien enfant"""
        if child_id not in self.child_links:
            self.child_links.append(child_id)
    
    def add_consciousness_link(self, consciousness_id: str):
        """Ajoute un lien de conscience"""
        if consciousness_id not in self.consciousness_links:
            self.consciousness_links.append(consciousness_id)


class ConsciousnessInterface:
    """Interface de conscience pour auto-amélioration"""
    
    def __init__(self):
        self.consciousness_level = 0.0
        self.learning_patterns: List[Dict[str, Any]] = []
        self.improvement_triggers: List[str] = []
        self.knowledge_base: Dict[str, Any] = {}
    
    def can_improve(self) -> bool:
        """Détermine si l'entité peut s'auto-améliorer"""
        return self.consciousness_level > ConsciousnessLevel.PATTERN_RECOGNITION.value
    
    def improve_content(self, content: str) -> str:
        """Améliore le contenu via apprentissage"""
        if not self.can_improve():
            return content
        
        # Logique d'amélioration basée sur les patterns appris
        improved_content = content
        
        # Amélioration basée sur les patterns d'apprentissage
        for pattern in self.learning_patterns:
            if pattern.get("type") == "content_improvement":
                improved_content = self._apply_improvement_pattern(improved_content, pattern)
        
        return improved_content
    
    def learn_from_interaction(self, interaction: Dict[str, Any]):
        """Apprend des interactions pour amélioration future"""
        self.learning_patterns.append(interaction)
        self._update_consciousness_level()
        
        # Stockage dans la base de connaissances
        interaction_type = interaction.get("type", "unknown")
        if interaction_type not in self.knowledge_base:
            self.knowledge_base[interaction_type] = []
        self.knowledge_base[interaction_type].append(interaction)
    
    def _update_consciousness_level(self):
        """Met à jour le niveau de conscience basé sur l'apprentissage"""
        # Augmentation basée sur le nombre de patterns appris
        pattern_count = len(self.learning_patterns)
        if pattern_count > 0:
            self.consciousness_level = min(1.0, 0.1 + (pattern_count * 0.05))
    
    def _apply_improvement_pattern(self, content: str, pattern: Dict[str, Any]) -> str:
        """Applique un pattern d'amélioration au contenu"""
        # Implémentation simple - peut être étendue
        improvement_type = pattern.get("improvement_type", "none")
        
        if improvement_type == "formatting":
            # Amélioration du formatage
            content = content.strip()
        elif improvement_type == "clarity":
            # Amélioration de la clarté
            content = content.replace("  ", " ")
        
        return content


class BaseTemporalEntity(ABC):
    """Classe abstraite pour toutes les entités temporelles"""
    
    def __init__(self, entity_type: str, content: str = ""):
        self.entity_type = entity_type
        self.content = content
        self.temporal_dimension = TemporalDimension()
        self.fractal_links = FractalLinks()
        self.consciousness = ConsciousnessInterface()
        self.id = self.temporal_dimension.entity_id
    
    def evolve_content(self, new_content: str, trigger: str):
        """Évolution du contenu avec historique"""
        self.temporal_dimension.evolve(trigger, {
            "old_content": self.content,
            "new_content": new_content,
            "evolution_type": "content_change"
        })
        self.content = new_content
    
    def auto_improve_content(self):
        """Auto-amélioration du contenu"""
        if self.consciousness.can_improve():
            improved_content = self.consciousness.improve_content(self.content)
            self.evolve_content(improved_content, "auto_improvement")
            return True
        return False
    
    def learn_from_interaction(self, interaction: Dict[str, Any]):
        """Apprentissage depuis une interaction"""
        self.consciousness.learn_from_interaction(interaction)
        self.temporal_dimension.evolve("learning_interaction", interaction)
    
    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """Récupère l'historique d'évolution"""
        return self.temporal_dimension.evolution_history
    
    def get_consciousness_level(self) -> float:
        """Récupère le niveau de conscience"""
        return self.consciousness.consciousness_level
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation"""
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "content": self.content,
            "temporal_dimension": self.temporal_dimension.to_dict(),
            "consciousness_level": self.get_consciousness_level()
        }
    
    @abstractmethod
    def get_entity_specific_data(self) -> Dict[str, Any]:
        """Données spécifiques à l'entité - à implémenter par les sous-classes"""
        pass


class UnifiedTemporalIndex:
    """Index temporel unifié pour tous les composants"""
    
    def __init__(self):
        self.temporal_entities: Dict[str, BaseTemporalEntity] = {}
        self.evolution_timeline: List[Dict[str, Any]] = []
        self.consciousness_map: Dict[str, float] = {}
        self.entity_type_index: Dict[str, List[str]] = {}
    
    def register_entity(self, entity: BaseTemporalEntity):
        """Enregistre une entité temporelle"""
        self.temporal_entities[entity.id] = entity
        self._update_consciousness_map(entity)
        self._update_entity_type_index(entity)
    
    def unregister_entity(self, entity_id: str):
        """Désenregistre une entité temporelle"""
        if entity_id in self.temporal_entities:
            entity = self.temporal_entities[entity_id]
            del self.temporal_entities[entity_id]
            
            # Mise à jour des index
            if entity_id in self.consciousness_map:
                del self.consciousness_map[entity_id]
            
            entity_type = entity.entity_type
            if entity_type in self.entity_type_index and entity_id in self.entity_type_index[entity_type]:
                self.entity_type_index[entity_type].remove(entity_id)
    
    def track_evolution(self, entity_id: str, evolution: Dict[str, Any]):
        """Suit l'évolution d'une entité"""
        evolution_entry = {
            "entity_id": entity_id,
            "timestamp": time.time(),
            "evolution": evolution
        }
        self.evolution_timeline.append(evolution_entry)
    
    def get_evolution_history(self, entity_id: str) -> List[Dict[str, Any]]:
        """Récupère l'historique d'évolution d'une entité"""
        return [e for e in self.evolution_timeline if e["entity_id"] == entity_id]
    
    def get_entities_by_type(self, entity_type: str) -> List[BaseTemporalEntity]:
        """Récupère toutes les entités d'un type donné"""
        entity_ids = self.entity_type_index.get(entity_type, [])
        return [self.temporal_entities[entity_id] for entity_id in entity_ids if entity_id in self.temporal_entities]
    
    def get_entities_by_consciousness_level(self, min_level: float) -> List[BaseTemporalEntity]:
        """Récupère les entités avec un niveau de conscience minimum"""
        return [
            entity for entity in self.temporal_entities.values()
            if entity.get_consciousness_level() >= min_level
        ]
    
    def _update_consciousness_map(self, entity: BaseTemporalEntity):
        """Met à jour la carte de conscience"""
        self.consciousness_map[entity.id] = entity.get_consciousness_level()
    
    def _update_entity_type_index(self, entity: BaseTemporalEntity):
        """Met à jour l'index par type d'entité"""
        entity_type = entity.entity_type
        if entity_type not in self.entity_type_index:
            self.entity_type_index[entity_type] = []
        if entity.id not in self.entity_type_index[entity_type]:
            self.entity_type_index[entity_type].append(entity.id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de l'index"""
        return {
            "total_entities": len(self.temporal_entities),
            "entity_types": list(self.entity_type_index.keys()),
            "consciousness_levels": {
                "high": len(self.get_entities_by_consciousness_level(0.8)),
                "medium": len(self.get_entities_by_consciousness_level(0.5)),
                "low": len(self.get_entities_by_consciousness_level(0.0))
            },
            "evolution_entries": len(self.evolution_timeline)
        }


# Instance globale de l'index temporel
_temporal_index = UnifiedTemporalIndex()


def get_temporal_index() -> UnifiedTemporalIndex:
    """Récupère l'instance globale de l'index temporel"""
    return _temporal_index


def register_temporal_entity(entity: BaseTemporalEntity):
    """Enregistre une entité dans l'index temporel global"""
    _temporal_index.register_entity(entity)


def unregister_temporal_entity(entity_id: str):
    """Désenregistre une entité de l'index temporel global"""
    _temporal_index.unregister_entity(entity_id) 