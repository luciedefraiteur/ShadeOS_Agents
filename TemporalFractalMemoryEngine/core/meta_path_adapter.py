#!/usr/bin/env python3
"""
⛧ Meta Path Adapter - Adaptateur Méta pour Virtualisation des Chemins ⛧

Couche méta qui virtualise les chemins et unifie les résultats entre FractalMemoryNode
et chemins simples, sans toucher aux couches basses.
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import uuid


@dataclass
class VirtualPath:
    """Chemin virtuel unifié"""
    path: str
    node_id: str
    metadata: Dict[str, Any]
    source_type: str  # "fractal", "temporal", "virtual"


class MetaPathAdapter:
    """Adaptateur méta pour virtualiser les chemins"""
    
    def __init__(self, fractal_node=None, path_string=None, metadata=None):
        """
        Initialise l'adaptateur avec soit un nœud fractal, soit un chemin string
        
        Args:
            fractal_node: FractalMemoryNode (optionnel)
            path_string: Chemin string (optionnel)
            metadata: Métadonnées supplémentaires (optionnel)
        """
        self.fractal_node = fractal_node
        self.path_string = path_string
        self.metadata = metadata or {}
        
        # Générer un ID unique pour ce chemin virtuel
        self.virtual_id = str(uuid.uuid4())
        
        # Extraire le chemin virtuel
        self.virtual_path = self._extract_virtual_path()
        
    def _extract_virtual_path(self) -> str:
        """Extrait le chemin virtuel selon le type d'entrée"""
        if self.fractal_node:
            # Depuis un FractalMemoryNode
            return self._extract_from_fractal_node()
        elif self.path_string:
            # Depuis un chemin string
            return self.path_string
        else:
            # Générer un chemin virtuel
            return f"/virtual/{self.virtual_id}"
    
    def _extract_from_fractal_node(self) -> str:
        """Extrait le chemin depuis un FractalMemoryNode"""
        try:
            # Essayer d'extraire le chemin depuis les métadonnées
            if hasattr(self.fractal_node, 'metadata') and self.fractal_node.metadata:
                path = self.fractal_node.metadata.get('path')
                if path:
                    return path
            
            # Essayer d'extraire depuis le contenu
            if hasattr(self.fractal_node, 'content'):
                # Chercher un pattern de chemin dans le contenu
                import re
                path_match = re.search(r'path[:\s]+([^\s\n]+)', self.fractal_node.content)
                if path_match:
                    return path_match.group(1)
            
            # Fallback : générer un chemin basé sur l'ID
            return f"/fractal/{self.virtual_id}"
            
        except Exception as e:
            print(f"⚠️ Erreur extraction chemin fractal: {e}")
            return f"/fractal/{self.virtual_id}"
    
    def get_path(self) -> str:
        """Retourne le chemin virtuel"""
        return self.virtual_path
    
    def get_node(self):
        """Retourne le nœud fractal (si disponible)"""
        return self.fractal_node
    
    def get_metadata(self) -> Dict[str, Any]:
        """Retourne les métadonnées enrichies"""
        metadata = self.metadata.copy()
        
        if self.fractal_node:
            # Enrichir avec les métadonnées du nœud fractal
            if hasattr(self.fractal_node, 'metadata'):
                metadata.update(self.fractal_node.metadata)
            if hasattr(self.fractal_node, 'keywords'):
                metadata['keywords'] = self.fractal_node.keywords
            if hasattr(self.fractal_node, 'strata'):
                metadata['strata'] = self.fractal_node.strata
        
        metadata.update({
            'virtual_id': self.virtual_id,
            'virtual_path': self.virtual_path,
            'source_type': 'fractal' if self.fractal_node else 'string'
        })
        
        return metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation"""
        return {
            'path': self.virtual_path,
            'node_id': self.virtual_id,
            'metadata': self.get_metadata(),
            'source_type': 'fractal' if self.fractal_node else 'string'
        }
    
    def __str__(self) -> str:
        return self.virtual_path
    
    def __repr__(self) -> str:
        return f"MetaPathAdapter(path='{self.virtual_path}', source='{self.fractal_node and 'fractal' or 'string'}')"


class UnifiedResultFormatter:
    """Formateur de résultats unifié"""
    
    @staticmethod
    def format_results(results: List[Any], format_type: str = "paths") -> List[Any]:
        """
        Formate les résultats selon le type demandé
        
        Args:
            results: Liste de résultats (FractalMemoryNode, strings, ou MetaPathAdapter)
            format_type: "paths", "nodes", "adapters", ou "mixed"
            
        Returns:
            Liste formatée selon le type demandé
        """
        if format_type == "paths":
            return UnifiedResultFormatter._to_paths(results)
        elif format_type == "nodes":
            return UnifiedResultFormatter._to_nodes(results)
        elif format_type == "adapters":
            return UnifiedResultFormatter._to_adapters(results)
        elif format_type == "mixed":
            return UnifiedResultFormatter._to_mixed(results)
        else:
            raise ValueError(f"Type de format inconnu: {format_type}")
    
    @staticmethod
    def _to_paths(results: List[Any]) -> List[str]:
        """Convertit en liste de chemins"""
        paths = []
        for result in results:
            if isinstance(result, str):
                paths.append(result)
            elif isinstance(result, MetaPathAdapter):
                paths.append(result.get_path())
            elif hasattr(result, 'metadata') and result.metadata:
                # FractalMemoryNode
                adapter = MetaPathAdapter(fractal_node=result)
                paths.append(adapter.get_path())
            else:
                # Fallback
                paths.append(str(result))
        return paths
    
    @staticmethod
    def _to_nodes(results: List[Any]):
        """Convertit en liste de nœuds (si possible)"""
        nodes = []
        for result in results:
            if hasattr(result, 'metadata'):  # FractalMemoryNode
                nodes.append(result)
            elif isinstance(result, MetaPathAdapter):
                node = result.get_node()
                if node:
                    nodes.append(node)
            # Les strings ne peuvent pas être convertis en nœuds
        return nodes
    
    @staticmethod
    def _to_adapters(results: List[Any]) -> List[MetaPathAdapter]:
        """Convertit en liste d'adaptateurs"""
        adapters = []
        for result in results:
            if isinstance(result, MetaPathAdapter):
                adapters.append(result)
            elif isinstance(result, str):
                adapters.append(MetaPathAdapter(path_string=result))
            elif hasattr(result, 'metadata'):  # FractalMemoryNode
                adapters.append(MetaPathAdapter(fractal_node=result))
            else:
                # Fallback
                adapters.append(MetaPathAdapter(path_string=str(result)))
        return adapters
    
    @staticmethod
    def _to_mixed(results: List[Any]) -> List[Dict[str, Any]]:
        """Convertit en format mixte avec métadonnées"""
        mixed = []
        for result in results:
            if isinstance(result, MetaPathAdapter):
                mixed.append(result.to_dict())
            elif isinstance(result, str):
                adapter = MetaPathAdapter(path_string=result)
                mixed.append(adapter.to_dict())
            elif hasattr(result, 'metadata'):  # FractalMemoryNode
                adapter = MetaPathAdapter(fractal_node=result)
                mixed.append(adapter.to_dict())
            else:
                # Fallback
                adapter = MetaPathAdapter(path_string=str(result))
                mixed.append(adapter.to_dict())
        return mixed


class VirtualPathRegistry:
    """Registre des chemins virtuels pour gestion centralisée"""
    
    def __init__(self):
        self.virtual_paths: Dict[str, MetaPathAdapter] = {}
        self.path_to_virtual: Dict[str, str] = {}
    
    def register(self, adapter: MetaPathAdapter) -> str:
        """Enregistre un adaptateur"""
        virtual_id = adapter.virtual_id
        self.virtual_paths[virtual_id] = adapter
        self.path_to_virtual[adapter.get_path()] = virtual_id
        return virtual_id
    
    def get_by_id(self, virtual_id: str) -> Optional[MetaPathAdapter]:
        """Récupère un adaptateur par ID"""
        return self.virtual_paths.get(virtual_id)
    
    def get_by_path(self, path: str) -> Optional[MetaPathAdapter]:
        """Récupère un adaptateur par chemin"""
        virtual_id = self.path_to_virtual.get(path)
        if virtual_id:
            return self.virtual_paths.get(virtual_id)
        return None
    
    def list_paths(self) -> List[str]:
        """Liste tous les chemins virtuels"""
        return list(self.path_to_virtual.keys())
    
    def clear(self):
        """Vide le registre"""
        self.virtual_paths.clear()
        self.path_to_virtual.clear()


# Instance globale du registre
_global_registry = VirtualPathRegistry()

def get_global_registry() -> VirtualPathRegistry:
    """Retourne l'instance globale du registre"""
    return _global_registry 