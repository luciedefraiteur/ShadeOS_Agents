#!/usr/bin/env python3
"""
⛧ MemoryEngine V2 - TemporalMemoryNode ⛧

Migration de FractalMemoryNode vers l'architecture temporelle universelle.
Compatibilité totale avec l'existant + dimension temporelle.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from .temporal_base import TemporalDimension, FractalLinks, ConsciousnessInterface
from .temporal_components import TemporalNode


class TemporalMemoryNode(TemporalNode):
    """Migration de FractalMemoryNode vers l'architecture temporelle universelle"""
    
    def __init__(self, content: str, metadata: Dict[str, Any] = None, 
                 strata: str = "somatic", **kwargs):
        # Initialisation de la base temporelle
        super().__init__(content, "memory", metadata)
        
        # Propriétés héritées de FractalMemoryNode
        self.strata = strata
        self.keywords = kwargs.get('keywords', [])
        self.linked_memories = kwargs.get('linked_memories', [])
        self.transcendence_links = kwargs.get('transcendence_links', [])
        self.immanence_links = kwargs.get('immanence_links', [])
        
        # Champs de compatibilité avec l'ancienne interface
        self.descriptor = content
        self.summary = metadata.get('summary', content[:100] + '...' if len(content) > 100 else content)
        
        # Validation des strates
        valid_strata = ["somatic", "cognitive", "metaphysical"]
        if self.strata not in valid_strata:
            self.strata = "somatic"
        
        # Migration des liens vers FractalLinks
        self._migrate_links_to_fractal()
        
        # Évolution temporelle de la création
        self.temporal_dimension.evolve("memory_node_created", {
            "strata": self.strata,
            "keywords_count": len(self.keywords),
            "links_count": len(self.linked_memories),
            "transcendence_links_count": len(self.transcendence_links),
            "immanence_links_count": len(self.immanence_links)
        })
    
    def _migrate_links_to_fractal(self):
        """Migration des liens vers la structure FractalLinks"""
        for link in self.linked_memories:
            self.fractal_links.add_sibling_link(link['path'])
        
        for link in self.transcendence_links:
            self.fractal_links.add_parent_link(link['path'])
        
        for link in self.immanence_links:
            self.fractal_links.add_child_link(link['path'])
    
    def add_link(self, path: str, summary: str):
        """Ajoute un lien interdimensionnel avec évolution temporelle"""
        # Évite les doublons
        if not any(link['path'] == path for link in self.linked_memories):
            self.linked_memories.append({"path": path, "summary": summary})
            self.fractal_links.add_sibling_link(path)
            
            # Évolution temporelle
            self.temporal_dimension.evolve("link_added", {
                "link_path": path,
                "link_summary": summary,
                "link_type": "sibling"
            })
    
    def add_transcendence_link(self, path: str, summary: str):
        """Ajoute un lien de transcendance avec évolution temporelle"""
        if not any(link['path'] == path for link in self.transcendence_links):
            self.transcendence_links.append({"path": path, "summary": summary})
            self.fractal_links.add_parent_link(path)
            
            # Évolution temporelle
            self.temporal_dimension.evolve("transcendence_link_added", {
                "link_path": path,
                "link_summary": summary,
                "link_type": "transcendence"
            })
    
    def add_immanence_link(self, path: str, summary: str):
        """Ajoute un lien d'immanence avec évolution temporelle"""
        if not any(link['path'] == path for link in self.immanence_links):
            self.immanence_links.append({"path": path, "summary": summary})
            self.fractal_links.add_child_link(path)
            
            # Évolution temporelle
            self.temporal_dimension.evolve("immanence_link_added", {
                "link_path": path,
                "link_summary": summary,
                "link_type": "immanence"
            })
    
    def get_strata_symbol(self) -> str:
        """Retourne le symbole mystique correspondant à la strate"""
        symbols = {
            "somatic": "🜃",      # Corps - Terre
            "cognitive": "🜁",    # Esprit - Air
            "metaphysical": "🜂"  # Âme - Feu
        }
        return symbols.get(self.strata, "🜄")  # Eau par défaut
    
    def auto_improve_content(self):
        """Auto-amélioration du contenu avec conscience de strate"""
        if self.consciousness.can_improve():
            # Amélioration basée sur la strate
            improved_content = self._improve_by_strata(self.content)
            self.evolve_content(improved_content, "auto_improvement_strata_based")
            return True
        return False
    
    def _improve_by_strata(self, content: str) -> str:
        """Améliore le contenu selon la strate"""
        if self.strata == "somatic":
            # Amélioration pour le corps - plus concret
            return self._improve_somatic_content(content)
        elif self.strata == "cognitive":
            # Amélioration pour l'esprit - plus structuré
            return self._improve_cognitive_content(content)
        elif self.strata == "metaphysical":
            # Amélioration pour l'âme - plus profond
            return self._improve_metaphysical_content(content)
        return content
    
    def _improve_somatic_content(self, content: str) -> str:
        """Améliore le contenu somatique (concret)"""
        # Logique d'amélioration somatique
        improved = content.strip()
        if not improved.endswith('.'):
            improved += '.'
        return improved
    
    def _improve_cognitive_content(self, content: str) -> str:
        """Améliore le contenu cognitif (structuré)"""
        # Logique d'amélioration cognitive
        lines = content.split('\n')
        improved_lines = []
        for line in lines:
            if line.strip():
                improved_lines.append(line.strip())
        return '\n'.join(improved_lines)
    
    def _improve_metaphysical_content(self, content: str) -> str:
        """Améliore le contenu métaphysique (profond)"""
        # Logique d'amélioration métaphysique
        improved = content.strip()
        if not improved.startswith('⛧'):
            improved = f"⛧ {improved}"
        return improved
    
    def learn_from_interaction(self, interaction: Dict[str, Any]):
        """Apprentissage depuis une interaction avec conscience de strate"""
        # Apprentissage de base
        super().learn_from_interaction(interaction)
        
        # Apprentissage spécifique à la strate
        if interaction.get("type") == "memory_access":
            self._learn_memory_access_pattern(interaction)
        elif interaction.get("type") == "link_creation":
            self._learn_link_creation_pattern(interaction)
    
    def _learn_memory_access_pattern(self, interaction: Dict[str, Any]):
        """Apprend des patterns d'accès mémoire"""
        access_type = interaction.get("access_type", "read")
        if access_type == "write":
            # Augmentation de la conscience pour les écritures
            self.consciousness.consciousness_level = min(1.0, self.consciousness.consciousness_level + 0.1)
        elif access_type == "read":
            # Augmentation modérée pour les lectures
            self.consciousness.consciousness_level = min(1.0, self.consciousness.consciousness_level + 0.05)
    
    def _learn_link_creation_pattern(self, interaction: Dict[str, Any]):
        """Apprend des patterns de création de liens"""
        link_type = interaction.get("link_type", "sibling")
        if link_type == "transcendence":
            # Augmentation significative pour les liens de transcendance
            self.consciousness.consciousness_level = min(1.0, self.consciousness.consciousness_level + 0.15)
        elif link_type == "immanence":
            # Augmentation modérée pour les liens d'immanence
            self.consciousness.consciousness_level = min(1.0, self.consciousness.consciousness_level + 0.08)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire avec compatibilité FractalMemoryNode"""
        base_dict = super().to_dict()
        
        # Ajout des propriétés spécifiques à FractalMemoryNode
        base_dict.update({
            'strata': self.strata,
            'keywords': self.keywords,
            'linked_memories': self.linked_memories,
            'transcendence_links': self.transcendence_links,
            'immanence_links': self.immanence_links,
            'descriptor': self.descriptor,
            'summary': self.summary,
            'strata_symbol': self.get_strata_symbol()
        })
        
        return base_dict
    
    def to_json(self) -> str:
        """Sérialise l'objet en une chaîne JSON joliment formatée"""
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)
    
    @classmethod
    def from_fractal_memory_node(cls, fractal_node) -> 'TemporalMemoryNode':
        """Crée un TemporalMemoryNode depuis un FractalMemoryNode existant"""
        return cls(
            content=fractal_node.content,
            metadata=fractal_node.metadata,
            strata=fractal_node.strata,
            keywords=fractal_node.keywords,
            linked_memories=fractal_node.linked_memories,
            transcendence_links=fractal_node.transcendence_links,
            immanence_links=fractal_node.immanence_links
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemporalMemoryNode':
        """Crée un TemporalMemoryNode depuis un dictionnaire"""
        return cls(
            content=data.get('content', ''),
            metadata=data.get('metadata', {}),
            strata=data.get('strata', 'somatic'),
            keywords=data.get('keywords', []),
            linked_memories=data.get('linked_memories', []),
            transcendence_links=data.get('transcendence_links', []),
            immanence_links=data.get('immanence_links', [])
        )
    
    def get_entity_specific_data(self) -> Dict[str, Any]:
        """Données spécifiques au nœud mémoire temporel"""
        return {
            "strata": self.strata,
            "strata_symbol": self.get_strata_symbol(),
            "keywords_count": len(self.keywords),
            "linked_memories_count": len(self.linked_memories),
            "transcendence_links_count": len(self.transcendence_links),
            "immanence_links_count": len(self.immanence_links),
            "descriptor": self.descriptor,
            "summary": self.summary
        } 