import os
import json
from pathlib import Path
from ..core.memory_node import FractalMemoryNode

class FileSystemBackend:
    """Gère le stockage de la mémoire fractale sur le système de fichiers."""

    def __init__(self, base_path: str = '.'):
        self.base_path = Path(base_path)
        self.memory_root = self.base_path / '.shadeos' / 'memory'
        self.memory_root.mkdir(parents=True, exist_ok=True)

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

    def write(self, path: str, content: str, summary: str, keywords: list, links: list, 
              strata: str = "somatic", transcendence_links: list = None, immanence_links: list = None):
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
        
        # 3. Crée le nœud avec la nouvelle interface
        new_node = FractalMemoryNode(
            content=content,
            metadata={
                'path': path,  # Ajout du chemin dans les métadonnées
                'summary': summary,
                'keywords': keywords,
                'strata': strata,
                'transcendence_links': transcendence_links or [],
                'immanence_links': immanence_links or []
            },
            strata=strata,
            keywords=keywords,
            linked_memories=linked_memories
        )

        with open(node_path, 'w', encoding='utf-8') as f:
            f.write(new_node.to_json())

        # 4. Met à jour le nœud parent
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

    def store(self, node: FractalMemoryNode) -> str:
        """Stocke un nœud mémoire (interface pour compatibilité avec les tests)."""
        # Génère un chemin unique basé sur le contenu
        import hashlib
        content_hash = hashlib.md5(node.content.encode()).hexdigest()[:8]
        path = f"/memories/{node.strata}/{content_hash}"
        
        # Utilise la méthode write existante
        self.write(
            path=path,
            content=node.content,
            summary=node.metadata.get('summary', node.content[:100] + '...' if len(node.content) > 100 else node.content),
            keywords=node.keywords,
            links=node.metadata.get('links', []),
            strata=node.strata,
            transcendence_links=node.metadata.get('transcendence_links', []),
            immanence_links=node.metadata.get('immanence_links', [])
        )
        
        return content_hash

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

    def close(self):
        """Ferme la connexion au backend (pas d'action nécessaire pour FileSystem)."""
        pass

    def search(self, strata: str = None, metadata_filter: dict = None) -> list:
        """Recherche des nœuds de mémoire."""
        results = []
        try:
            for strata_dir in self.memory_root.iterdir():
                if not strata_dir.is_dir():
                    continue
                if strata and strata_dir.name != strata:
                    continue
                    
                for node_file in strata_dir.rglob("*.json"):
                    try:
                        with open(node_file, 'r', encoding='utf-8') as f:
                            node_data = json.load(f)
                            
                        # Filtrer par métadonnées si spécifié
                        if metadata_filter:
                            node_metadata = node_data.get('metadata', {})
                            if not all(node_metadata.get(k) == v for k, v in metadata_filter.items()):
                                continue
                                
                        results.append(node_data)
                    except Exception as e:
                        print(f"Erreur lecture {node_file}: {e}")
                        
        except Exception as e:
            print(f"Erreur recherche: {e}")
            
        return results
    
    def retrieve(self, node_id: str) -> FractalMemoryNode:
        """Récupère un nœud de mémoire par son ID."""
        try:
            for strata_dir in self.memory_root.iterdir():
                if not strata_dir.is_dir():
                    continue
                    
                for node_file in strata_dir.rglob("*.json"):
                    try:
                        with open(node_file, 'r', encoding='utf-8') as f:
                            node_data = json.load(f)
                            
                        if node_data.get('id') == node_id:
                            return FractalMemoryNode.from_dict(node_data)
                    except Exception as e:
                        print(f"Erreur lecture {node_file}: {e}")
                        
        except Exception as e:
            print(f"Erreur récupération: {e}")
            
        return None 