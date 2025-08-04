"""
Temporal Index for MemoryEngine
Provides fast temporal search capabilities with fallback to fractal memory
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class SearchProvider:
    """Interface abstraite pour les providers de recherche."""
    
    # Méthodes de recherche
    def find_by_keyword(self, keyword: str) -> List[Any]:
        raise NotImplementedError
    
    def find_by_strata(self, strata: str) -> List[Any]:
        raise NotImplementedError
    
    def search(self, strata: str = None, content_filter: str = None) -> List[Any]:
        raise NotImplementedError
    
    # Méthodes de listing (liens fractals réels)
    def list_links(self, path: str = '.') -> List[Any]:
        raise NotImplementedError
    
    def list_transcendence_links(self, path: str = '.') -> List[Any]:
        raise NotImplementedError
    
    def list_immanence_links(self, path: str = '.') -> List[Any]:
        raise NotImplementedError
    
    # Méthodes de traversal (spéciales)
    def traverse_transcendence_path(self, path: str, max_depth: int = 5) -> List[Any]:
        raise NotImplementedError
    
    def traverse_immanence_path(self, path: str, max_depth: int = 5) -> List[Any]:
        raise NotImplementedError


class FractalSearchProvider(SearchProvider):
    """Provider pour la mémoire fractale."""
    
    def __init__(self, memory_engine):
        self.memory_engine = memory_engine
    
    def find_by_keyword(self, keyword: str) -> List[Any]:
        return self.memory_engine.find_memories_by_keyword(keyword)
    
    def find_by_strata(self, strata: str) -> List[Any]:
        return self.memory_engine.find_by_strata(strata)
    
    def search(self, strata: str = None, content_filter: str = None) -> List[Any]:
        return self.memory_engine.search(strata, content_filter)
    
    def list_links(self, path: str = '.') -> List[Any]:
        return self.memory_engine.list_links(path)
    
    def list_transcendence_links(self, path: str = '.') -> List[Any]:
        return self.memory_engine.list_transcendence_links(path)
    
    def list_immanence_links(self, path: str = '.') -> List[Any]:
        return self.memory_engine.list_immanence_links(path)
    
    def traverse_transcendence_path(self, path: str, max_depth: int = 5) -> List[Any]:
        return self.memory_engine.traverse_transcendence_path(path, max_depth)
    
    def traverse_immanence_path(self, path: str, max_depth: int = 5) -> List[Any]:
        return self.memory_engine.traverse_immanence_path(path, max_depth)


class TemporalSearchProvider(SearchProvider):
    """Provider pour la mémoire temporelle."""
    
    def __init__(self, temporal_index, memory_engine):
        self.temporal_index = temporal_index
        self.memory_engine = memory_engine
    
    def find_by_keyword(self, keyword: str) -> List[Any]:
        return self.temporal_index.search_temporal("keywords", keyword, self.memory_engine)
    
    def find_by_strata(self, strata: str) -> List[Any]:
        return self.temporal_index.search_temporal("strata", strata, self.memory_engine)
    
    def search(self, strata: str = None, content_filter: str = None) -> List[Any]:
        # Recherche temporelle avec filtres
        results = []
        if strata:
            results.extend(self.find_by_strata(strata))
        # TODO: Implémenter content_filter pour temporel
        return results
    
    def list_links(self, path: str = '.') -> List[Any]:
        # Pour temporel, on peut retourner les liens temporels
        temporal_node = self.temporal_index.get_temporal_by_fractal(path)
        if temporal_node:
            return [{"path": temporal_node.previous_temporal_uuid, "type": "previous"}] if temporal_node.previous_temporal_uuid else []
        return []
    
    def list_transcendence_links(self, path: str = '.') -> List[Any]:
        # Pour temporel, on peut faire une recherche par timeline ascendante
        return self.temporal_index.search_temporal("timeline", "ascending", self.memory_engine)
    
    def list_immanence_links(self, path: str = '.') -> List[Any]:
        # Pour temporel, on peut faire une recherche par timeline descendante
        return self.temporal_index.search_temporal("timeline", "descending", self.memory_engine)
    
    def traverse_transcendence_path(self, path: str, max_depth: int = 5) -> List[Any]:
        # Traverse la chaîne temporelle vers le passé
        temporal_node = self.temporal_index.get_temporal_by_fractal(path)
        if temporal_node:
            return self.temporal_index.traverse_temporal_chain(temporal_node.uuid, "previous", max_depth)
        return []
    
    def traverse_immanence_path(self, path: str, max_depth: int = 5) -> List[Any]:
        # Traverse la chaîne temporelle vers le futur
        temporal_node = self.temporal_index.get_temporal_by_fractal(path)
        if temporal_node:
            return self.temporal_index.traverse_temporal_chain(temporal_node.uuid, "next", max_depth)
        return []


class UnifiedSearchEngine:
    """Moteur de recherche unifié avec fallback intelligent."""
    
    def __init__(self, fractal_provider, temporal_provider):
        self.fractal_provider = fractal_provider
        self.temporal_provider = temporal_provider
    
    def search(self, method: str, **kwargs) -> List[Any]:
        """
        Recherche unifiée avec fallback intelligent.
        
        Args:
            method: Méthode de recherche ("keyword", "strata", "search", "list_links", "list_transcendence_links", "list_immanence_links", "traverse_transcendence_path", "traverse_immanence_path")
            **kwargs: Arguments spécifiques à la méthode
        """
        # Essayer d'abord la recherche temporelle (rapide)
        try:
            if method == "keyword":
                results = self.temporal_provider.find_by_keyword(kwargs["keyword"])
            elif method == "strata":
                results = self.temporal_provider.find_by_strata(kwargs["strata"])
            elif method == "search":
                results = self.temporal_provider.search(**kwargs)
            elif method == "list_links":
                results = self.temporal_provider.list_links(kwargs.get("path", "."))
            elif method == "list_transcendence_links":
                results = self.temporal_provider.list_transcendence_links(kwargs.get("path", "."))
            elif method == "list_immanence_links":
                results = self.temporal_provider.list_immanence_links(kwargs.get("path", "."))
            elif method == "traverse_transcendence_path":
                results = self.temporal_provider.traverse_transcendence_path(**kwargs)
            elif method == "traverse_immanence_path":
                results = self.temporal_provider.traverse_immanence_path(**kwargs)
            else:
                raise ValueError(f"Méthode inconnue: {method}")
            
            # Si on trouve des résultats en temporel, les retourner
            if results:
                return results
                
        except Exception as e:
            print(f"⚠️ Recherche temporelle échouée: {e}")
        
        # Fallback vers la recherche fractale (profonde)
        try:
            if method == "keyword":
                return self.fractal_provider.find_by_keyword(kwargs["keyword"])
            elif method == "strata":
                return self.fractal_provider.find_by_strata(kwargs["strata"])
            elif method == "search":
                return self.fractal_provider.search(**kwargs)
            elif method == "list_links":
                return self.fractal_provider.list_links(kwargs.get("path", "."))
            elif method == "list_transcendence_links":
                return self.fractal_provider.list_transcendence_links(kwargs.get("path", "."))
            elif method == "list_immanence_links":
                return self.fractal_provider.list_immanence_links(kwargs.get("path", "."))
            elif method == "traverse_transcendence_path":
                return self.fractal_provider.traverse_transcendence_path(**kwargs)
            elif method == "traverse_immanence_path":
                return self.fractal_provider.traverse_immanence_path(**kwargs)
            else:
                raise ValueError(f"Méthode inconnue: {method}")
                
        except Exception as e:
            print(f"⚠️ Recherche fractale échouée: {e}")
            return []


class TemporalIndex:
    """
    Index temporel minimal pour recherche rapide dans la mémoire fractale.
    Stocke seulement les chemins et métadonnées, récupération dynamique.
    """
    
    def __init__(self, backend_type: str, base_path: str):
        """
        Initialize the temporal index.
        
        Args:
            backend_type: Type of backend ("filesystem", "neo4j")
            base_path: Base path for storage
        """
        self.backend_type = backend_type
        self.base_path = Path(base_path)
        self.temporal_dir = self.base_path / "memory" / "temporal"
        self.temporal_dir.mkdir(parents=True, exist_ok=True)
        
        # Index files
        self.index_files = {
            "timeline": self.temporal_dir / "timeline.json",
            "intent_index": self.temporal_dir / "intent_index.json",
            "strata_index": self.temporal_dir / "strata_index.json",
            "keyword_index": self.temporal_dir / "keywords_index.json"
        }
        
        # Load existing indexes
        self.temporal_index = self._load_indexes()
        
        # Temporal nodes storage
        self.temporal_nodes = {}  # uuid → TemporalNode
        self.fractal_to_temporal = {}  # fractal_path → uuid
    
    def _load_indexes(self) -> Dict[str, Any]:
        """Load existing temporal indexes from files."""
        indexes = {
            "timeline": [],
            "intent_index": {},
            "strata_index": {},
            "keyword_index": {}
        }
        
        for index_name, file_path in self.index_files.items():
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        if index_name == "timeline":
                            indexes["timeline"] = json.load(f)
                        else:
                            indexes[index_name] = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"⚠️ Warning: Could not load {index_name} index: {e}")
        
        return indexes
    
    def _save_indexes(self):
        """Save temporal indexes to files."""
        for index_name, file_path in self.index_files.items():
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    if index_name == "timeline":
                        json.dump(self.temporal_index["timeline"], f, indent=2, ensure_ascii=False)
                    else:
                        json.dump(self.temporal_index[index_name], f, indent=2, ensure_ascii=False)
            except IOError as e:
                print(f"⚠️ Warning: Could not save {index_name} index: {e}")
    
    def auto_record(self, fractal_path: str, metadata: Dict[str, Any]):
        """
        Enregistrement automatique lors du stockage fractal.
        
        Args:
            fractal_path: Chemin du nœud fractal
            metadata: Métadonnées du nœud (intent, strata, keywords, etc.)
        """
        import uuid
        
        # Créer UUID temporel
        temporal_uuid = str(uuid.uuid4())
        
        # Créer nœud temporel
        temporal_node = TemporalNode(fractal_path, temporal_uuid, metadata)
        
        # Liens bidirectionnels
        if self.temporal_index["timeline"]:
            previous_uuid = self.temporal_index["timeline"][-1]["uuid"]
            temporal_node.previous_temporal_uuid = previous_uuid
            # Vérifier que le nœud précédent existe avant de le modifier
            if previous_uuid in self.temporal_nodes:
                self.temporal_nodes[previous_uuid].next_temporal_uuid = temporal_uuid
        
        # Stockage
        self.temporal_nodes[temporal_uuid] = temporal_node
        self.fractal_to_temporal[fractal_path] = temporal_uuid
        
        # Indexation temporelle
        temporal_entry = {
            "uuid": temporal_uuid,
            "fractal_path": fractal_path,
            "timestamp": temporal_node.timestamp,
            "intent": metadata.get("intent"),
            "strata": metadata.get("strata", "somatic"),
            "keywords": metadata.get("keywords", []),
            "previous_uuid": temporal_node.previous_temporal_uuid,
            "next_uuid": temporal_node.next_temporal_uuid
        }
        
        self.temporal_index["timeline"].append(temporal_entry)
        
        # Indexation par intent
        if temporal_entry["intent"]:
            if temporal_entry["intent"] not in self.temporal_index["intent_index"]:
                self.temporal_index["intent_index"][temporal_entry["intent"]] = []
            self.temporal_index["intent_index"][temporal_entry["intent"]].append(fractal_path)
        
        # Indexation par strata
        strata = temporal_entry["strata"]
        if strata not in self.temporal_index["strata_index"]:
            self.temporal_index["strata_index"][strata] = []
        self.temporal_index["strata_index"][strata].append(fractal_path)
        
        # Indexation par keywords
        for keyword in temporal_entry["keywords"]:
            if keyword not in self.temporal_index["keyword_index"]:
                self.temporal_index["keyword_index"][keyword] = []
            self.temporal_index["keyword_index"][keyword].append(fractal_path)
        
        # Sauvegarde des index
        self._save_indexes()
    
    def get_temporal_node(self, uuid: str) -> Optional['TemporalNode']:
        """Récupère un nœud temporel par UUID."""
        return self.temporal_nodes.get(uuid)
    
    def get_temporal_by_fractal(self, fractal_path: str) -> Optional['TemporalNode']:
        """Récupère un nœud temporel par chemin fractal."""
        uuid = self.fractal_to_temporal.get(fractal_path)
        return self.temporal_nodes.get(uuid) if uuid else None
    
    def inject_temporal_links(self, fractal_node):
        """Injecte les liens temporels virtuels dans un nœud fractal."""
        temporal_node = self.get_temporal_by_fractal(fractal_node.path)
        if temporal_node:
            fractal_node.temporal_uuid = temporal_node.uuid
            fractal_node.previous_temporal_uuid = temporal_node.previous_temporal_uuid
            fractal_node.next_temporal_uuid = temporal_node.next_temporal_uuid
    
    def traverse_temporal_chain(self, start_uuid: str, direction: str = "next", max_steps: int = 10):
        """Traverse la chaîne temporelle."""
        chain = []
        current_uuid = start_uuid
        steps = 0
        
        while current_uuid and steps < max_steps:
            temporal_node = self.get_temporal_node(current_uuid)
            if not temporal_node:
                break
                
            chain.append(temporal_node)
            
            if direction == "next":
                current_uuid = temporal_node.next_temporal_uuid
            else:
                current_uuid = temporal_node.previous_temporal_uuid
            
            steps += 1
        
        return chain
    
    def search_temporal(self, query_type: str, query_value: str, memory_engine=None) -> List[Any]:
        """
        Recherche rapide dans l'index temporel avec récupération dynamique.
        
        Args:
            query_type: Type de recherche ("intent", "strata", "keywords", "timeline")
            query_value: Valeur à rechercher
            memory_engine: Instance du MemoryEngine pour récupération dynamique
            
        Returns:
            Liste des nœuds mémoire trouvés
        """
        paths = []
        
        if query_type == "intent":
            paths = self.temporal_index["intent_index"].get(query_value, [])
        elif query_type == "strata":
            paths = self.temporal_index["strata_index"].get(query_value, [])
        elif query_type == "keywords":
            paths = self.search_by_keywords(query_value)
        elif query_type == "timeline":
            # Recherche par période temporelle
            paths = self.search_by_timeline(query_value)
        else:
            print(f"⚠️ Type de recherche inconnu: {query_type}")
            return []
        
        # Récupération dynamique depuis la mémoire fractale
        results = []
        if memory_engine and paths:
            for path in paths:
                try:
                    fractal_memory = memory_engine.get_memory_node(path)
                    if fractal_memory:
                        results.append(fractal_memory)
                except Exception as e:
                    print(f"⚠️ Erreur lors de la récupération de {path}: {e}")
        
        return results
    
    def search_by_keywords(self, keyword: str) -> List[str]:
        """Recherche par mot-clé avec correspondance partielle."""
        paths = set()
        keyword_lower = keyword.lower()
        
        for kw, path_list in self.temporal_index["keyword_index"].items():
            if keyword_lower in kw.lower() or kw.lower() in keyword_lower:
                paths.update(path_list)
        
        return list(paths)
    
    def search_by_timeline(self, time_period: str) -> List[str]:
        """Recherche par période temporelle."""
        # TODO: Implémenter la recherche par période
        # Pour l'instant, retourne les 10 derniers
        return [entry["fractal_path"] for entry in self.temporal_index["timeline"][-10:]]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de l'index temporel."""
        return {
            "total_entries": len(self.temporal_index["timeline"]),
            "intent_count": len(self.temporal_index["intent_index"]),
            "strata_count": len(self.temporal_index["strata_index"]),
            "keyword_count": len(self.temporal_index["keyword_index"]),
            "latest_entry": self.temporal_index["timeline"][-1] if self.temporal_index["timeline"] else None
        }
    
    def cleanup_orphaned_entries(self, memory_engine):
        """Nettoie les entrées orphelines (nœuds fractals supprimés)."""
        orphaned_paths = []
        
        for entry in self.temporal_index["timeline"]:
            path = entry["fractal_path"]
            if not memory_engine.get_memory_node(path):
                orphaned_paths.append(path)
        
        # Suppression des entrées orphelines
        for path in orphaned_paths:
            self._remove_from_all_indexes(path)
        
        if orphaned_paths:
            self._save_indexes()
            print(f"🧹 Nettoyé {len(orphaned_paths)} entrées orphelines")
    
    def _remove_from_all_indexes(self, path: str):
        """Supprime un chemin de tous les index."""
        # Timeline
        self.temporal_index["timeline"] = [
            entry for entry in self.temporal_index["timeline"] 
            if entry["fractal_path"] != path
        ]
        
        # Intent index
        for intent, paths in self.temporal_index["intent_index"].items():
            self.temporal_index["intent_index"][intent] = [p for p in paths if p != path]
        
        # Strata index
        for strata, paths in self.temporal_index["strata_index"].items():
            self.temporal_index["strata_index"][strata] = [p for p in paths if p != path]
        
        # Keyword index
        for keyword, paths in self.temporal_index["keyword_index"].items():
            self.temporal_index["keyword_index"][keyword] = [p for p in paths if p != path]


class TemporalNode:
    """Nœud temporel avec références miroir."""
    
    def __init__(self, fractal_path: str, uuid: str, metadata: dict):
        self.uuid = uuid
        self.fractal_path = fractal_path
        self.timestamp = datetime.now().isoformat()
        self.metadata = metadata
        self.previous_temporal_uuid = None
        self.next_temporal_uuid = None 