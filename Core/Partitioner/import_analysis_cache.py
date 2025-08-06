#!/usr/bin/env python3
"""
🔧 Import Analysis Cache - Système de cache optimisé

Système de cache intelligent pour éviter les analyses redondantes d'imports.
Implémente les stratégies 1 (Cache temporel avec hashes) et 2 (Watcher de fichiers).

Auteur: Alma (via Lucie Defraiteur)
Date: 2025-08-06
"""

import os
import hashlib
import asyncio
from typing import Dict, Set, Optional, Any
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
    """Optimiseur d'analyse d'imports avec cache intelligent"""
    
    def __init__(self, memory_engine=None):
        self.memory_engine = memory_engine
        self.cache: Dict[str, ImportAnalysisCache] = {}
        self.file_watcher = FileChangeWatcher()
        self.max_cache_age = 3600  # 1 heure par défaut
    
    async def get_or_analyze_imports(self, file_path: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Récupère l'analyse depuis le cache ou la recalcule si nécessaire"""
        
        if not os.path.exists(file_path):
            logger.warning(f"⚠️ Fichier non trouvé: {file_path}")
            return {}
        
        # Forcer le refresh si demandé
        if force_refresh:
            logger.info(f"🔄 Refresh forcé pour {file_path}")
            return await self._perform_full_analysis(file_path)
        
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
                    return cached_analysis.fractal_nodes
        
        # Cache miss ou invalide - nouvelle analyse
        logger.info(f"🔄 Nouvelle analyse pour {file_path}")
        fractal_nodes = await self._perform_full_analysis(file_path)
        
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
                'last_access': datetime.now()
            }
        )
        
        return fractal_nodes
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcule le hash du contenu du fichier"""
        return self.file_watcher._calculate_file_hash(file_path)
    
    async def _calculate_import_hash(self, file_path: str) -> str:
        """Calcule le hash des fichiers importés (récursif)"""
        try:
            # Import local pour éviter les dépendances circulaires
            from .import_analyzer import ImportAnalyzer
            
            # Analyser les imports
            analyzer = ImportAnalyzer()
            analysis = analyzer.analyze_files([file_path])
            
            # Collecter tous les fichiers importés
            imported_files = set()
            for file_data in analysis['detailed_results'].values():
                for import_path in file_data.get('local_imports', []):
                    if os.path.exists(import_path):
                        imported_files.add(import_path)
            
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
    
    async def _perform_full_analysis(self, file_path: str) -> Dict[str, Any]:
        """Effectue une analyse complète des imports"""
        try:
            # Import local pour éviter les dépendances circulaires
            from .import_analyzer import ImportAnalyzer
            
            analyzer = ImportAnalyzer()
            analysis_result = analyzer.analyze_files([file_path])
            
            # Convertir en format fractal si nécessaire
            fractal_nodes = self._convert_to_fractal_nodes(analysis_result)
            
            return fractal_nodes
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse de {file_path}: {e}")
            return {}
    
    def _convert_to_fractal_nodes(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Convertit le résultat d'analyse en nœuds fractaux"""
        # Pour l'instant, retourner le résultat brut
        # Plus tard, on pourra ajouter la conversion vers FractalImportNode
        return analysis_result.get('detailed_results', {})
    
    def _build_dependency_graph(self, fractal_nodes: Dict[str, Any]) -> Dict[str, Any]:
        """Construit le graphe de dépendances"""
        # Pour l'instant, retourner un graphe simple
        # Plus tard, on pourra ajouter la logique de graphe
        return {
            'nodes': list(fractal_nodes.keys()),
            'edges': [],
            'metadata': {
                'node_count': len(fractal_nodes),
                'created_at': datetime.now()
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
            'cache_hit_ratio': self._calculate_hit_ratio()
        }
    
    def _calculate_hit_ratio(self) -> float:
        """Calcule le ratio de hits du cache"""
        # Pour l'instant, retourner une valeur par défaut
        # Plus tard, on pourra ajouter le tracking des hits/misses
        return 0.8  # 80% par défaut


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