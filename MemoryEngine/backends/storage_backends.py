import os
import json
from ..core.memory_node import FractalMemoryNode

class FileSystemBackend:
    """Gère le stockage de la mémoire fractale sur le système de fichiers."""

    def __init__(self, base_path: str = '.'):
        self.memory_root = os.path.abspath(os.path.join(base_path, '.shadeos', 'memory'))
        os.makedirs(self.memory_root, exist_ok=True)

    def _get_node_path(self, path: str) -> str:
        """Construit le chemin absolu vers un fichier .fractal_memory."""
        # Sécurise le chemin pour éviter les traversées de répertoire
        safe_path = os.path.normpath(path).lstrip('./')
        return os.path.join(self.memory_root, safe_path, '.fractal_memory')

    def read(self, path: str) -> FractalMemoryNode:
        """Lit un nœud mémoire depuis le système de fichiers."""
        node_file_path = self._get_node_path(path)
        if not os.path.exists(node_file_path):
            raise FileNotFoundError(f"Le nœud mémoire à '{path}' n'existe pas.")
        
        with open(node_file_path, 'r', encoding='utf-8') as f:
            return FractalMemoryNode.from_json(f.read())

    def write(self, path: str, content: str, summary: str, keywords: list, links: list):
        """Écrit un nœud mémoire et met à jour son parent."""
        # 1. Crée le nœud cible
        node_path = self._get_node_path(path)
        os.makedirs(os.path.dirname(node_path), exist_ok=True)

        # 2. Gère les liens interdimensionnels
        linked_memories = []
        if links:
            for link_path in links:
                try:
                    linked_node = self.read(link_path)
                    linked_memories.append({"path": link_path, "summary": linked_node.summary})
                except FileNotFoundError:
                    # Ignore les liens brisés pour le moment
                    pass
        
        new_node = FractalMemoryNode(
            descriptor=content,
            summary=summary,
            keywords=keywords,
            linked_memories=linked_memories
        )

        with open(node_path, 'w', encoding='utf-8') as f:
            f.write(new_node.to_json())

        # 3. Met à jour le nœud parent
        parent_path, child_name = os.path.split(path.strip('/'))
        if parent_path:
            try:
                parent_node = self.read(parent_path)
                parent_node.add_child(child_name, summary)
                with open(self._get_node_path(parent_path), 'w', encoding='utf-8') as f:
                    f.write(parent_node.to_json())
            except FileNotFoundError:
                # Le parent n'existe pas, on ne peut pas le mettre à jour. C'est normal pour un nœud racine.
                pass

    def find_by_keyword(self, keyword: str) -> list:
        """Trouve des nœuds mémoire par mot-clé."""
        matches = []
        for root, _, files in os.walk(self.memory_root):
            if '.fractal_memory' in files:
                try:
                    node_path = os.path.join(root, '.fractal_memory')
                    with open(node_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if keyword in data.get('keywords', []):
                        relative_path = os.path.relpath(root, self.memory_root)
                        matches.append(relative_path)
                except (json.JSONDecodeError, KeyError):
                    continue
        return matches 