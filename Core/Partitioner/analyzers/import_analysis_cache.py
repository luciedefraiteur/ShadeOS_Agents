#!/usr/bin/env python3
"""
🔧 Import Analysis Cache - Système de cache optimisé

Système de cache intelligent pour éviter les analyses redondantes d'imports.
Compatible avec le nouveau ImportAnalyzer redesigné.
Implémente les stratégies 1 (Cache temporel avec hashes) et 2 (Watcher de fichiers).

Auteur: Alma (via Lucie Defraiteur)
Date: 2025-08-07
"""

import os
import hashlib
import asyncio
from typing import Dict, Set, Optional, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ImportAnalysisCache:
    """Cache pour les analyses d'imports avec invalidation intelligente"""
    
    file_path: str
    file_hash: str  # Hash du contenu du fichier
    import_hash: str  # Hash des fichiers importés
    analysis_timestamp: datetime
    fractal_nodes: Dict[str, Any]  # Nœuds fractaux
    dependency_graph: Dict[str, Any]  # Graphe de dépendances
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_still_valid(self, current_file_hash: str, current_import_hash: str) -> bool:
        """Vérifie si le cache est encore valide"""
        return (self.file_hash == current_file_hash and 
                self.import_hash == current_import_hash)
    
    def get_age_seconds(self) -> float:
        """Retourne l'âge du cache en secondes"""
        return (datetime.now() - self.analysis_timestamp).total_seconds()


class FileChangeWatcher:
    """Watcher intelligent pour détecter les changements de fichiers"""
    
    def __init__(self):
        self.file_timestamps: Dict[str, float] = {}
        self.import_dependencies: Dict[str, Set[str]] = {}
        self.file_hashes: Dict[str, str] = {}
    
    def has_file_changed(self, file_path: str) -> bool:
        """Vérifie si un fichier a changé depuis la dernière vérification"""
        try:
            if not os.path.exists(file_path):
                return True
            
            current_mtime = os.path.getmtime(file_path)
            current_hash = self._calculate_file_hash(file_path)
            
            last_mtime = self.file_timestamps.get(file_path, 0)
            last_hash = self.file_hashes.get(file_path, "")
            
            if current_mtime > last_mtime or current_hash != last_hash:
                self.file_timestamps[file_path] = current_mtime
                self.file_hashes[file_path] = current_hash
                logger.debug(f"📝 Fichier modifié: {file_path}")
                return True
            
            return False
        except Exception as e:
            logger.warning(f"⚠️ Erreur lors de la vérification de {file_path}: {e}")
            return True  # En cas d'erreur, considérer comme changé
    
    def has_imports_changed(self, file_path: str) -> bool:
        """Vérifie si les fichiers importés ont changé"""
        if file_path not in self.import_dependencies:
            return True
        
        for imported_file in self.import_dependencies[file_path]:
            if self.has_file_changed(imported_file):
                logger.debug(f"📝 Import modifié: {imported_file} -> {file_path}")
                return True
        
        return False
    
    def update_dependencies(self, file_path: str, imported_files: Set[str]):
        """Met à jour la liste des dépendances"""
        self.import_dependencies[file_path] = imported_files
        logger.debug(f"🔗 Dépendances mises à jour pour {file_path}: {len(imported_files)} fichiers")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcule le hash du contenu du fichier"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception:
            return "error_hash"


class ImportAnalysisOptimizer:
    """Optimiseur d'analyse d'imports avec cache intelligent - Compatible avec le nouveau ImportAnalyzer"""
    
    def __init__(self, memory_engine=None):
        self.memory_engine = memory_engine
        self.cache: Dict[str, ImportAnalysisCache] = {}
        self.file_watcher = FileChangeWatcher()
        self.max_cache_age = 3600  # 1 heure par défaut
        self.hit_count = 0
        self.miss_count = 0
    
    async def get_or_analyze_imports(self, file_path: str, force_refresh: bool = False, 
                                   max_depth: int = None, debug: bool = False) -> Dict[str, Any]:
        """Récupère l'analyse depuis le cache ou la recalcule si nécessaire"""
        
        if not os.path.exists(file_path):
            logger.warning(f"⚠️ Fichier non trouvé: {file_path}")
            return {}
        
        # Forcer le refresh si demandé
        if force_refresh:
            logger.info(f"🔄 Refresh forcé pour {file_path}")
            self.miss_count += 1
            return await self._perform_full_analysis(file_path, max_depth, debug)
        
        # Vérifier le cache
        if file_path in self.cache:
            cached_analysis = self.cache[file_path]
            
            # Vérifier l'âge du cache
            if cached_analysis.get_age_seconds() > self.max_cache_age:
                logger.info(f"⏰ Cache expiré pour {file_path}")
                del self.cache[file_path]
            else:
                # Vérifier la validité du cache
                current_file_hash = self._calculate_file_hash(file_path)
                current_import_hash = await self._calculate_import_hash(file_path)
                
                if cached_analysis.is_still_valid(current_file_hash, current_import_hash):
                    logger.info(f"✅ Cache hit pour {file_path}")
                    self.hit_count += 1
                    return cached_analysis.fractal_nodes
        
        # Cache miss ou invalide - nouvelle analyse
        logger.info(f"🔄 Nouvelle analyse pour {file_path}")
        self.miss_count += 1
        fractal_nodes = await self._perform_full_analysis(file_path, max_depth, debug)
        
        # Mettre à jour le cache
        current_file_hash = self._calculate_file_hash(file_path)
        current_import_hash = await self._calculate_import_hash(file_path)
        
        self.cache[file_path] = ImportAnalysisCache(
            file_path=file_path,
            file_hash=current_file_hash,
            import_hash=current_import_hash,
            analysis_timestamp=datetime.now(),
            fractal_nodes=fractal_nodes,
            dependency_graph=self._build_dependency_graph(fractal_nodes),
            metadata={
                'analysis_count': 1,
                'last_access': datetime.now(),
                'max_depth': max_depth,
                'debug_mode': debug
            }
        )
        
        return fractal_nodes
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcule le hash du contenu du fichier"""
        return self.file_watcher._calculate_file_hash(file_path)
    
    async def _calculate_import_hash(self, file_path: str) -> str:
        """Calcule le hash des fichiers importés (récursif) - Compatible avec le nouveau ImportAnalyzer"""
        try:
            # Import local pour éviter les dépendances circulaires
            from .import_analyzer import ImportAnalyzer
            
            # Analyser les imports avec le nouveau ImportAnalyzer
            analyzer = ImportAnalyzer()
            analysis = analyzer.analyze_files([file_path], max_depth=2)  # Profondeur limitée pour le hash
            
            # Collecter tous les fichiers importés depuis la nouvelle structure
            imported_files = set()
            files_analysis = analysis.get('files_analysis', {})
            
            for file_data in files_analysis.values():
                # Extraire les imports locaux résolus
                for import_name in file_data.get('local_imports', []):
                    # Essayer de résoudre le chemin du fichier
                    resolved_path = analyzer.find_file_for_import(import_name, file_path)
                    if resolved_path and os.path.exists(resolved_path):
                        imported_files.add(resolved_path)
            
            # Mettre à jour les dépendances dans le watcher
            self.file_watcher.update_dependencies(file_path, imported_files)
            
            # Calculer le hash combiné
            combined_hash = hashlib.sha256()
            for imported_file in sorted(imported_files):
                file_hash = self._calculate_file_hash(imported_file)
                combined_hash.update(file_hash.encode())
            
            return combined_hash.hexdigest()
        except Exception as e:
            logger.warning(f"⚠️ Erreur lors du calcul du hash d'imports pour {file_path}: {e}")
            return "error_import_hash"
    
    async def _perform_full_analysis(self, file_path: str, max_depth: int = None, 
                                   debug: bool = False) -> Dict[str, Any]:
        """Effectue une analyse complète des imports avec le nouveau ImportAnalyzer"""
        try:
            # Import local pour éviter les dépendances circulaires
            from .import_analyzer import ImportAnalyzer
            
            analyzer = ImportAnalyzer()
            analysis_result = analyzer.analyze_files([file_path], max_depth=max_depth, debug=debug)
            
            # Convertir en format fractal optimisé
            fractal_nodes = self._convert_to_fractal_nodes(analysis_result)
            
            return fractal_nodes
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse de {file_path}: {e}")
            return {}
    
    def _convert_to_fractal_nodes(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Convertit le résultat d'analyse en nœuds fractaux optimisés"""
        fractal_nodes = {}
        
        # Extraire les données de la nouvelle structure
        files_analysis = analysis_result.get('files_analysis', {})
        statistics = analysis_result.get('statistics', {})
        detected_modules = analysis_result.get('detected_modules', {})
        
        # Convertir chaque fichier en nœud fractal
        for file_path, file_data in files_analysis.items():
            node_id = file_path
            
            # Créer le nœud fractal avec les propriétés enrichies
            fractal_node = {
                'id': node_id,
                'type': 'python_file',
                'properties': {
                    'import_count': file_data.get('import_count', 0),
                    'local_import_count': len(file_data.get('local_imports', [])),
                    'external_import_count': len(file_data.get('external_imports', [])),
                    'standard_import_count': len(file_data.get('standard_imports', [])),
                    'dependency_depth': file_data.get('dependency_depth', 0),
                    'has_errors': len(file_data.get('errors', [])) > 0,
                    'error_count': len(file_data.get('errors', [])),
                    'local_imports': file_data.get('local_imports', []),
                    'external_imports': file_data.get('external_imports', []),
                    'standard_imports': file_data.get('standard_imports', [])
                },
                'metadata': {
                    'analysis_timestamp': datetime.now().isoformat(),
                    'cache_source': 'import_analysis_cache',
                    'version': '2.0'
                }
            }
            
            fractal_nodes[node_id] = fractal_node
        
        # Ajouter les métadonnées globales
        fractal_nodes['_metadata'] = {
            'total_files': statistics.get('files_analyzed', 0),
            'total_imports': statistics.get('total_imports', 0),
            'local_imports': statistics.get('local_imports', 0),
            'external_imports': statistics.get('external_imports', 0),
            'cycles_detected': statistics.get('cycles_detected', 0),
            'detected_modules': detected_modules,
            'analysis_duration': statistics.get('duration', 0)
        }
        
        return fractal_nodes
    
    def _build_dependency_graph(self, fractal_nodes: Dict[str, Any]) -> Dict[str, Any]:
        """Construit le graphe de dépendances optimisé"""
        nodes = []
        edges = []
        
        # Extraire les nœuds (exclure les métadonnées)
        for node_id, node_data in fractal_nodes.items():
            if node_id != '_metadata' and isinstance(node_data, dict):
                nodes.append({
                    'id': node_id,
                    'type': node_data.get('type', 'python_file'),
                    'properties': node_data.get('properties', {})
                })
                
                # Créer les arêtes basées sur les imports locaux
                local_imports = node_data.get('properties', {}).get('local_imports', [])
                for import_name in local_imports:
                    # Essayer de résoudre le chemin du fichier importé
                    # Pour l'instant, on crée une arête basée sur le nom du module
                    edge = {
                        'source': node_id,
                        'target': import_name,
                        'type': 'imports'
                    }
                    edges.append(edge)
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'node_count': len(nodes),
                'edge_count': len(edges),
                'created_at': datetime.now().isoformat(),
                'version': '2.0'
            }
        }
    
    def clear_cache(self, file_path: str = None):
        """Vide le cache"""
        if file_path:
            if file_path in self.cache:
                del self.cache[file_path]
                logger.info(f"🗑️ Cache vidé pour {file_path}")
        else:
            self.cache.clear()
            logger.info("🗑️ Cache complètement vidé")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache"""
        total_entries = len(self.cache)
        total_age = sum(entry.get_age_seconds() for entry in self.cache.values())
        avg_age = total_age / total_entries if total_entries > 0 else 0
        
        return {
            'total_entries': total_entries,
            'average_age_seconds': avg_age,
            'max_cache_age': self.max_cache_age,
            'cache_hit_ratio': self._calculate_hit_ratio(),
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'total_requests': self.hit_count + self.miss_count
        }
    
    def _calculate_hit_ratio(self) -> float:
        """Calcule le ratio de hits du cache"""
        total_requests = self.hit_count + self.miss_count
        if total_requests == 0:
            return 0.0
        return self.hit_count / total_requests
    
    def get_cached_files(self) -> List[str]:
        """Retourne la liste des fichiers en cache"""
        return list(self.cache.keys())
    
    def get_cache_entry(self, file_path: str) -> Optional[ImportAnalysisCache]:
        """Récupère une entrée spécifique du cache"""
        return self.cache.get(file_path)
    
    def set_max_cache_age(self, max_age_seconds: int):
        """Définit l'âge maximum du cache"""
        self.max_cache_age = max_age_seconds
        logger.info(f"⏰ Âge maximum du cache défini à {max_age_seconds} secondes")


# Instance globale pour faciliter l'utilisation
_global_optimizer: Optional[ImportAnalysisOptimizer] = None

def get_import_optimizer(memory_engine=None) -> ImportAnalysisOptimizer:
    """Retourne l'instance globale de l'optimiseur"""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = ImportAnalysisOptimizer(memory_engine)
    return _global_optimizer

def set_import_optimizer(optimizer: ImportAnalysisOptimizer):
    """Définit l'instance globale de l'optimiseur"""
    global _global_optimizer
    _global_optimizer = optimizer

def clear_global_cache():
    """Vide le cache global"""
    global _global_optimizer
    if _global_optimizer:
        _global_optimizer.clear_cache()

def get_global_cache_stats() -> Dict[str, Any]:
    """Retourne les statistiques du cache global"""
    global _global_optimizer
    if _global_optimizer:
        return _global_optimizer.get_cache_stats()
    return {'error': 'No global optimizer initialized'} 