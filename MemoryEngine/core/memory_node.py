import json
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class FractalMemoryNode:
    """
    Représente la structure de données d'un nœud mémoire dans le système fractal.
    Supporte les Strates (Somatic, Cognitive, Metaphysical) et la Respiration (Transcendance/Immanence).
    """

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    strata: str = "somatic"
    
    # Identifiants uniques
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Champs de compatibilité avec l'ancienne interface
    descriptor: str = field(init=False)
    summary: str = field(init=False)
    keywords: List[str] = field(default_factory=list)

    # Relations hiérarchiques et associatives
    children: List[Dict[str, str]] = field(default_factory=list)
    linked_memories: List[Dict[str, str]] = field(default_factory=list)

    # Relations verticales de la Respiration
    transcendence_links: List[Dict[str, str]] = field(default_factory=list)  # Vers l'abstraction ↑
    immanence_links: List[Dict[str, str]] = field(default_factory=list)      # Vers la concrétisation ↓

    def __post_init__(self):
        """Initialisation post-création pour la compatibilité."""
        # Compatibilité avec l'ancienne interface
        self.descriptor = self.content
        self.summary = self.metadata.get('summary', self.content[:100] + '...' if len(self.content) > 100 else self.content)
        
        # Validation des strates
        valid_strata = ["somatic", "cognitive", "metaphysical"]
        if self.strata not in valid_strata:
            self.strata = "somatic"  # Valeur par défaut

    def to_json(self) -> str:
        """Sérialise l'objet en une chaîne JSON joliment formatée."""
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire pour sérialisation."""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'content': self.content,
            'metadata': self.metadata,
            'strata': self.strata,
            'keywords': self.keywords,
            'children': self.children,
            'linked_memories': self.linked_memories,
            'transcendence_links': self.transcendence_links,
            'immanence_links': self.immanence_links
        }

    @staticmethod
    def from_json(json_str: str) -> 'FractalMemoryNode':
        """Crée une instance de FractalMemoryNode à partir d'une chaîne JSON."""
        data = json.loads(json_str)
        return FractalMemoryNode.from_dict(data)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'FractalMemoryNode':
        """Crée une instance de FractalMemoryNode à partir d'un dictionnaire."""
        return FractalMemoryNode(
            content=data.get('content', ''),
            metadata=data.get('metadata', {}),
            strata=data.get('strata', 'somatic'),
            id=data.get('id', str(uuid.uuid4())),
            timestamp=data.get('timestamp', datetime.now().isoformat()),
            keywords=data.get('keywords', []),
            children=data.get('children', []),
            linked_memories=data.get('linked_memories', []),
            transcendence_links=data.get('transcendence_links', []),
            immanence_links=data.get('immanence_links', [])
        )

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