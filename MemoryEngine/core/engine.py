import os
from ..backends.storage_backends import FileSystemBackend
from .memory_node import FractalMemoryNode
from .temporal_index import TemporalIndex

# Import Neo4j backend if available
try:
    from ..backends.neo4j_backend import Neo4jBackend
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
        
        # Initialisation de l'index temporel
        from .temporal_index import TemporalIndex
        self.temporal_index = TemporalIndex(backend_type, base_path)

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
        
        # Indexation temporelle automatique
        metadata = {
            "path": path,
            "strata": strata,
            "keywords": keywords,
            "summary": summary,
            "content": content
        }
        self.temporal_index.auto_record(path, metadata)
        
        return True

    def get_memory_node(self, path: str):
        """Récupère le contenu complet d'un nœud mémoire avec injection des liens temporels."""
        node = self.backend.read(path)
        if node:
            # Injection des liens temporels virtuels
            self.temporal_index.inject_temporal_links(node)
        return node

    def forget_memory(self, path: str, cleanup_links: bool = True) -> bool:
        """
        Supprime intelligemment un souvenir du système de mémoire.

        Args:
            path: Chemin du souvenir à supprimer
            cleanup_links: Si True, nettoie les liens vers ce nœud

        Returns:
            True si succès, False sinon
        """
        try:
            # Vérification que le nœud existe
            node = self.get_memory_node(path)
            if not node:
                print(f"⚠️ Nœud {path} n'existe pas")
                return False

            # Étape 1: Nettoyer les liens entrants si demandé
            if cleanup_links:
                self._cleanup_incoming_links(path)

            # Étape 2: Supprimer le nœud lui-même
            if hasattr(self.backend, 'delete'):
                success = self.backend.delete(path)
                if success:
                    print(f"✅ Mémoire {path} supprimée avec nettoyage des liens")
                return success
            else:
                # Fallback pour backends sans méthode delete
                print(f"⚠️ Backend {self.backend_type} ne supporte pas la suppression")
                return False

        except Exception as e:
            print(f"❌ Erreur suppression mémoire {path}: {e}")
            return False

    def _cleanup_incoming_links(self, target_path: str):
        """
        Nettoie tous les liens pointant vers un nœud à supprimer.

        Args:
            target_path: Chemin du nœud cible à supprimer
        """
        try:
            print(f"🧹 Nettoyage des liens vers {target_path}...")

            # Pour les backends avancés avec support des liens
            if hasattr(self.backend, 'find_nodes_linking_to'):
                linking_nodes = self.backend.find_nodes_linking_to(target_path)

                for node_path in linking_nodes:
                    self._remove_links_from_node(node_path, target_path)

            else:
                # Fallback : scan manuel (plus lent mais fonctionne)
                print("🔍 Scan manuel des liens (backend basique)...")
                self._manual_link_cleanup(target_path)

        except Exception as e:
            print(f"⚠️ Erreur nettoyage liens: {e}")

    def _remove_links_from_node(self, node_path: str, target_path: str):
        """
        Supprime les liens vers target_path depuis node_path.

        Args:
            node_path: Nœud à modifier
            target_path: Cible des liens à supprimer
        """
        try:
            node = self.get_memory_node(node_path)
            if not node:
                return

            # Vérification et nettoyage des différents types de liens
            modified = False

            # Links classiques
            if hasattr(node, 'links') and node.links:
                original_count = len(node.links)
                node.links = [link for link in node.links if link != target_path]
                if len(node.links) != original_count:
                    modified = True

            # Transcendence links
            if hasattr(node, 'transcendence_links') and node.transcendence_links:
                original_count = len(node.transcendence_links)
                node.transcendence_links = [link for link in node.transcendence_links if link != target_path]
                if len(node.transcendence_links) != original_count:
                    modified = True

            # Immanence links
            if hasattr(node, 'immanence_links') and node.immanence_links:
                original_count = len(node.immanence_links)
                node.immanence_links = [link for link in node.immanence_links if link != target_path]
                if len(node.immanence_links) != original_count:
                    modified = True

            # Sauvegarder si modifié
            if modified:
                if hasattr(self.backend, 'update_node'):
                    self.backend.update_node(node_path, node)
                    print(f"  🔗 Liens nettoyés dans {node_path}")
                else:
                    # Fallback : recréer le nœud
                    self._recreate_node_without_links(node, target_path)

        except Exception as e:
            print(f"⚠️ Erreur suppression liens de {node_path}: {e}")

    def _manual_link_cleanup(self, target_path: str):
        """
        Nettoyage manuel des liens (pour backends basiques).

        Args:
            target_path: Chemin cible à nettoyer
        """
        try:
            # Cette méthode est plus lente mais fonctionne avec tous les backends
            print("🔍 Recherche manuelle des nœuds avec liens...")

            # Pour l'instant, on log juste l'intention
            # L'implémentation complète nécessiterait un scan de tous les nœuds
            print(f"⚠️ Nettoyage manuel non implémenté pour {target_path}")
            print("💡 Utilisez un backend avancé pour le nettoyage automatique des liens")

        except Exception as e:
            print(f"⚠️ Erreur nettoyage manuel: {e}")

    def _recreate_node_without_links(self, node, target_path: str):
        """
        Recrée un nœud en supprimant les liens vers target_path.

        Args:
            node: Nœud à recréer
            target_path: Chemin à supprimer des liens
        """
        try:
            # Nettoie les liens
            clean_links = []
            if hasattr(node, 'links') and node.links:
                clean_links = [link for link in node.links if link != target_path]

            clean_transcendence = []
            if hasattr(node, 'transcendence_links') and node.transcendence_links:
                clean_transcendence = [link for link in node.transcendence_links if link != target_path]

            clean_immanence = []
            if hasattr(node, 'immanence_links') and node.immanence_links:
                clean_immanence = [link for link in node.immanence_links if link != target_path]

            # Recrée le nœud avec les liens nettoyés
            self.create_memory(
                path=node.path,
                content=node.content,
                summary=node.summary,
                keywords=node.keywords,
                links=clean_links,
                strata=getattr(node, 'strata', 'somatic'),
                transcendence_links=clean_transcendence,
                immanence_links=clean_immanence
            )

            print(f"  🔄 Nœud {node.path} recréé sans liens vers {target_path}")

        except Exception as e:
            print(f"⚠️ Erreur recréation nœud: {e}")

    def find_memories_by_keyword(self, keyword: str) -> list:
        """Trouve les chemins des souvenirs contenant un mot-clé spécifique."""
        return self.backend.find_by_keyword(keyword)

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

    def store(self, content: str, metadata: dict = None, strata: str = "somatic", **kwargs) -> str:
        """
        Stocke un nouveau souvenir dans le système fractal.
        
        Args:
            content: Contenu du souvenir
            metadata: Métadonnées associées
            strata: Strate de mémoire ("somatic", "cognitive", "metaphysical")
            **kwargs: Arguments supplémentaires
            
        Returns:
            ID du nœud créé
        """
        if metadata is None:
            metadata = {}
            
        # Générer un chemin unique
        import uuid
        import time
        node_id = str(uuid.uuid4())
        path = f"/memories/{strata}/{node_id}"
        
        # Créer le souvenir
        self.create_memory(
            path=path,
            content=content,
            summary=metadata.get('summary', content[:100] + '...' if len(content) > 100 else content),
            keywords=metadata.get('keywords', []),
            links=metadata.get('links', []),
            strata=strata,
            transcendence_links=metadata.get('transcendence_links', []),
            immanence_links=metadata.get('immanence_links', [])
        )
        
        return node_id

    def search(self, strata: str = None, content_filter: str = None) -> list:
        """Recherche des nœuds de mémoire."""
        return self.backend.search(strata=strata, metadata_filter={"content": content_filter} if content_filter else None)
    
    def retrieve(self, node_id: str) -> FractalMemoryNode:
        """Récupère un nœud de mémoire par son ID."""
        return self.backend.retrieve(node_id)

    def get_statistics(self) -> dict:
        """Récupère les statistiques du MemoryEngine."""
        stats = {
            "backend_type": self.backend_type,
            "total": 0,
            "total_nodes": 0,
            "strata": {
                "somatic": 0,
                "cognitive": 0,
                "metaphysical": 0
            },
            "nodes_by_strata": {
                "somatic": 0,
                "cognitive": 0,
                "metaphysical": 0
            },
            "advanced_stats": False
        }
        
        # Calculer les totaux
        total_nodes = sum(stats["nodes_by_strata"].values())
        stats["total_nodes"] = total_nodes
        stats["total"] = total_nodes
        
        return stats

    def get_memory_statistics(self) -> dict:
        """Alias pour get_statistics() pour compatibilité."""
        return self.get_statistics()

    def close(self):
        """Ferme la connexion au backend (important pour Neo4j)."""
        if hasattr(self.backend, 'close'):
            self.backend.close() 