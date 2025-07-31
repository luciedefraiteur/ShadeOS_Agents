from .storage_backends import FileSystemBackend

class MemoryEngine:
    """Point d'entrée principal et API publique du moteur de mémoire."""

    def __init__(self, backend=None):
        # Permet d'injecter un backend différent pour les tests, sinon utilise FileSystemBackend par défaut.
        self.backend = backend if backend else FileSystemBackend()

    def create_memory(self, path: str, content: str, summary: str, keywords: list, links: list = None):
        """Crée un nouveau souvenir dans le système fractal."""
        self.backend.write(path, content, summary, keywords, links or [])
        return True

    def get_memory_node(self, path: str) -> dict:
        """Récupère le contenu complet d'un nœud mémoire sous forme de dictionnaire."""
        node = self.backend.read(path)
        return node.__dict__

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

# Instance globale pour un accès facile par les outils
memory_engine = MemoryEngine()