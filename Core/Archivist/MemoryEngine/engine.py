import os
from .storage_backends import FileSystemBackend

# Import Neo4j backend if available
try:
    from .neo4j_backend import Neo4jBackend
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

class MemoryEngine:
    """
    Point d'entrée principal et API publique du moteur de mémoire fractale.
    Supporte les backends FileSystem et Neo4j avec Strates et Respiration.
    """
    def __init__(self, backend_type: str = "auto", base_path: str = '.', backend=None, **backend_kwargs):
        """
        Initialize the Memory Engine with the specified backend.

        Args:
            backend_type: "filesystem", "neo4j", or "auto" (tries Neo4j first, falls back to filesystem)
            base_path: Base path for filesystem backend
            backend: Custom backend instance (overrides backend_type)
            **backend_kwargs: Additional arguments for backend initialization
        """
        if backend:
            self.backend = backend
        elif backend_type == "neo4j":
            if not NEO4J_AVAILABLE:
                raise ImportError("Neo4j backend requested but neo4j package not available")
            self.backend = Neo4jBackend(**backend_kwargs)
        elif backend_type == "filesystem":
            self.backend = FileSystemBackend(base_path=base_path)
        elif backend_type == "auto":
            # Try Neo4j first, fall back to filesystem
            if NEO4J_AVAILABLE:
                try:
                    self.backend = Neo4jBackend(**backend_kwargs)
                    print("⛧ Using Neo4j backend for Fractal Memory")
                except Exception as e:
                    print(f"⛧ Neo4j connection failed ({e}), falling back to FileSystem backend")
                    self.backend = FileSystemBackend(base_path=base_path)
            else:
                print("⛧ Neo4j not available, using FileSystem backend")
                self.backend = FileSystemBackend(base_path=base_path)
        else:
            raise ValueError(f"Unknown backend_type: {backend_type}")

        self.backend_type = type(self.backend).__name__

    def create_memory(self, path: str, content: str, summary: str, keywords: list,
                     links: list = None, strata: str = "somatic",
                     transcendence_links: list = None, immanence_links: list = None):
        """
        Crée un nouveau souvenir dans le système fractal avec support des Strates et Respiration.

        Args:
            path: Chemin unique du nœud mémoire
            content: Contenu complet (descriptor) de la mémoire
            summary: Résumé bref de la mémoire
            keywords: Liste de mots-clés pour la recherche
            links: Liens horizontaux associatifs vers d'autres nœuds
            strata: Strate de mémoire ("somatic", "cognitive", "metaphysical")
            transcendence_links: Liens verticaux vers l'abstraction
            immanence_links: Liens verticaux vers la concrétisation
        """
        # Support both old and new backend interfaces
        if hasattr(self.backend, 'write') and len(self.backend.write.__code__.co_varnames) > 6:
            # New Neo4j backend with extended parameters
            self.backend.write(path, content, summary, keywords, links or [], strata,
                             transcendence_links or [], immanence_links or [])
        else:
            # Old FileSystem backend
            self.backend.write(path, content, summary, keywords, links or [])
        return True

    def get_memory_node(self, path: str):
        """Récupère le contenu complet d'un nœud mémoire."""
        return self.backend.read(path)

    def find_memories_by_keyword(self, keyword: str) -> list:
        """Trouve les chemins des souvenirs contenant un mot-clé spécifique."""
        return self.backend.find_by_keyword(keyword)

    def list_children(self, path: str = '.') -> list:
        """Liste les enfants directs d'un nœud mémoire."""
        node = self.backend.read(path)
        return node.children

    def list_links(self, path: str = '.') -> list:
        """Liste les liens interdimensionnels d'un nœud mémoire."""
        node = self.backend.read(path)
        return node.linked_memories

    def list_transcendence_links(self, path: str = '.') -> list:
        """Liste les liens de transcendance (vers l'abstraction) d'un nœud mémoire."""
        node = self.backend.read(path)
        return getattr(node, 'transcendence_links', [])

    def list_immanence_links(self, path: str = '.') -> list:
        """Liste les liens d'immanence (vers la concrétisation) d'un nœud mémoire."""
        node = self.backend.read(path)
        return getattr(node, 'immanence_links', [])

    def find_by_strata(self, strata: str) -> list:
        """Trouve tous les nœuds mémoire dans une strate spécifique."""
        if hasattr(self.backend, 'find_by_strata'):
            return self.backend.find_by_strata(strata)
        else:
            # Fallback for FileSystem backend
            return []

    def traverse_transcendence_path(self, path: str, max_depth: int = 5) -> list:
        """Suit les liens de transcendance vers l'abstraction depuis un nœud."""
        if hasattr(self.backend, 'traverse_transcendence_path'):
            return self.backend.traverse_transcendence_path(path, max_depth)
        else:
            return []

    def traverse_immanence_path(self, path: str, max_depth: int = 5) -> list:
        """Suit les liens d'immanence vers la concrétisation depuis un nœud."""
        if hasattr(self.backend, 'traverse_immanence_path'):
            return self.backend.traverse_immanence_path(path, max_depth)
        else:
            return []

    def get_memory_statistics(self) -> dict:
        """Obtient des statistiques sur le graphe de mémoire."""
        if hasattr(self.backend, 'get_memory_statistics'):
            return self.backend.get_memory_statistics()
        else:
            return {"backend": self.backend_type, "advanced_stats": False}

    def close(self):
        """Ferme la connexion au backend (important pour Neo4j)."""
        if hasattr(self.backend, 'close'):
            self.backend.close()

# Instance globale pour un accès facile par les outils
memory_engine = MemoryEngine(backend_type="auto")