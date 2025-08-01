import json
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class FractalMemoryNode:
    """
    Représente la structure de données d'un nœud mémoire dans le système fractal.
    Supporte les Strates (Somatic, Cognitive, Metaphysical) et la Respiration (Transcendance/Immanence).
    """

    descriptor: str
    summary: str
    keywords: List[str] = field(default_factory=list)

    # Strate de mémoire : "somatic", "cognitive", "metaphysical"
    strata: str = "somatic"

    # Relations hiérarchiques et associatives
    children: List[Dict[str, str]] = field(default_factory=list)
    linked_memories: List[Dict[str, str]] = field(default_factory=list)

    # Relations verticales de la Respiration
    transcendence_links: List[Dict[str, str]] = field(default_factory=list)  # Vers l'abstraction ↑
    immanence_links: List[Dict[str, str]] = field(default_factory=list)      # Vers la concrétisation ↓

    def to_json(self) -> str:
        """Sérialise l'objet en une chaîne JSON joliment formatée."""
        return json.dumps(self.__dict__, indent=4, ensure_ascii=False)

    @staticmethod
    def from_json(json_str: str) -> 'FractalMemoryNode':
        """Crée une instance de FractalMemoryNode à partir d'une chaîne JSON."""
        data = json.loads(json_str)
        return FractalMemoryNode(**data)

    def add_child(self, path: str, summary: str):
        """Ajoute un descripteur d'enfant à la liste."""
        # Évite les doublons
        if not any(child['path'] == path for child in self.children):
            self.children.append({"path": path, "summary": summary})

    def add_link(self, path: str, summary: str):
        """Ajoute un lien interdimensionnel à la liste."""
        # Évite les doublons
        if not any(link['path'] == path for link in self.linked_memories):
            self.linked_memories.append({"path": path, "summary": summary})

    def add_transcendence_link(self, path: str, summary: str):
        """Ajoute un lien de transcendance (vers l'abstraction) à la liste."""
        if not any(link['path'] == path for link in self.transcendence_links):
            self.transcendence_links.append({"path": path, "summary": summary})

    def add_immanence_link(self, path: str, summary: str):
        """Ajoute un lien d'immanence (vers la concrétisation) à la liste."""
        if not any(link['path'] == path for link in self.immanence_links):
            self.immanence_links.append({"path": path, "summary": summary})

    def get_strata_symbol(self) -> str:
        """Retourne le symbole mystique correspondant à la strate."""
        symbols = {
            "somatic": "🜃",      # Corps - Terre
            "cognitive": "🜁",    # Esprit - Air
            "metaphysical": "🜂"  # Âme - Feu
        }
        return symbols.get(self.strata, "🜄")  # Eau par défaut