import json
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class FractalMemoryNode:
    """Représente la structure de données d'un nœud mémoire dans le système fractal."""
    
    descriptor: str
    summary: str
    keywords: List[str] = field(default_factory=list)
    children: List[Dict[str, str]] = field(default_factory=list)
    linked_memories: List[Dict[str, str]] = field(default_factory=list)

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