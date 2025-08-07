#!/usr/bin/env python3
"""
🔧 Broken Dependency Handler - Gestionnaire de dépendances brisées

Système de gestion intelligent des dépendances brisées avec détection,
isolation et stratégies de récupération.

Auteur: Alma (via Lucie Defraiteur)
Date: 2025-08-06
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class BrokenDependencyInfo:
    """Informations sur une dépendance brisée"""
    
    file_path: str
    broken_import: str
    error_message: str
    first_detected: datetime
    last_attempt: datetime
    retry_count: int = 0
    status: str = "active"  # active, resolved, permanent_failure
    resolution_attempts: List[Dict[str, Any]] = field(default_factory=list)


class BrokenDependencyHandler:
    """Gestionnaire de dépendances brisées avec stratégies de récupération"""
    
    def __init__(self, max_retry_attempts: int = 3, backoff_delay: int = 60):
        self.broken_dependencies: Dict[str, BrokenDependencyInfo] = {}
        self.retry_attempts: Dict[str, int] = {}
        self.max_retry_attempts = max_retry_attempts
        self.backoff_delay = backoff_delay
        self.degraded_files: Set[str] = set()
        self.recovery_attempts: Dict[str, datetime] = {}
        
        logger.info(f"🔧 BrokenDependencyHandler initialisé (max_retries: {max_retry_attempts}, backoff: {backoff_delay}s)")
    
    async def handle_broken_import(self, file_path: str, broken_import: str, error: Exception) -> Dict[str, Any]:
        """Gère une dépendance brisée détectée"""
        
        retry_key = f"{file_path}:{broken_import}"
        current_time = datetime.now()
        
        # Vérifier si c'est une nouvelle dépendance brisée
        if retry_key not in self.broken_dependencies:
            # Nouvelle dépendance brisée
            self.broken_dependencies[retry_key] = BrokenDependencyInfo(
                file_path=file_path,
                broken_import=broken_import,
                error_message=str(error),
                first_detected=current_time,
                last_attempt=current_time,
                retry_count=1
            )
            
            logger.warning(f"⚠️ Nouvelle dépendance brisée détectée: {broken_import} dans {file_path}")
            
        else:
            # Dépendance brisée existante
            dependency_info = self.broken_dependencies[retry_key]
            dependency_info.last_attempt = current_time
            dependency_info.retry_count += 1
            
            logger.warning(f"⚠️ Dépendance brisée persistante: {broken_import} dans {file_path} (tentative {dependency_info.retry_count})")
        
        # Incrémenter les tentatives
        self.retry_attempts[retry_key] = self.retry_attempts.get(retry_key, 0) + 1
        
        # Décider de l'action
        if self.retry_attempts[retry_key] <= self.max_retry_attempts:
            return await self._handle_retry(file_path, broken_import, retry_key)
        else:
            return await self._handle_permanent_failure(file_path, broken_import, retry_key)
    
    async def _handle_retry(self, file_path: str, broken_import: str, retry_key: str) -> Dict[str, Any]:
        """Gère une nouvelle tentative de résolution"""
        
        dependency_info = self.broken_dependencies[retry_key]
        
        # Enregistrer la tentative
        dependency_info.resolution_attempts.append({
            'timestamp': datetime.now(),
            'action': 'retry_scheduled',
            'delay': self.backoff_delay
        })
        
        # Activer le mode dégradé pour ce fichier
        self.degraded_files.add(file_path)
        
        return {
            'action': 'retry_later',
            'delay': self.backoff_delay,
            'message': f'Retry scheduled for {broken_import} in {file_path}',
            'degraded_mode': True,
            'retry_count': dependency_info.retry_count
        }
    
    async def _handle_permanent_failure(self, file_path: str, broken_import: str, retry_key: str) -> Dict[str, Any]:
        """Gère un échec permanent de résolution"""
        
        dependency_info = self.broken_dependencies[retry_key]
        dependency_info.status = "permanent_failure"
        
        # Enregistrer l'échec permanent
        dependency_info.resolution_attempts.append({
            'timestamp': datetime.now(),
            'action': 'permanent_failure',
            'reason': 'max_retries_exceeded'
        })
        
        logger.error(f"❌ Échec permanent pour {broken_import} dans {file_path}")
        
        return {
            'action': 'skip_analysis',
            'message': f'Permanent failure for {broken_import} in {file_path}',
            'fallback': 'use_cached_data',
            'degraded_mode': True,
            'permanent_failure': True
        }
    
    def is_in_degraded_mode(self, file_path: str) -> bool:
        """Vérifie si un fichier est en mode dégradé"""
        return file_path in self.degraded_files
    
    def get_broken_dependencies_for_file(self, file_path: str) -> List[BrokenDependencyInfo]:
        """Récupère toutes les dépendances brisées pour un fichier"""
        broken_deps = []
        for retry_key, dependency_info in self.broken_dependencies.items():
            if dependency_info.file_path == file_path and dependency_info.status == "active":
                broken_deps.append(dependency_info)
        return broken_deps
    
    async def attempt_recovery(self, file_path: str) -> bool:
        """Tente de récupérer du mode dégradé pour un fichier"""
        
        if file_path not in self.degraded_files:
            return True
        
        broken_deps = self.get_broken_dependencies_for_file(file_path)
        all_fixed = True
        
        for dependency_info in broken_deps:
            if not await self._is_import_available(dependency_info.broken_import):
                all_fixed = False
                break
        
        if all_fixed:
            await self.exit_degraded_mode(file_path)
            logger.info(f"✅ Récupération réussie pour {file_path}")
            return True
        
        return False
    
    async def exit_degraded_mode(self, file_path: str):
        """Sort du mode dégradé pour un fichier"""
        
        self.degraded_files.discard(file_path)
        
        # Marquer les dépendances comme résolues
        for retry_key, dependency_info in self.broken_dependencies.items():
            if dependency_info.file_path == file_path:
                dependency_info.status = "resolved"
                dependency_info.resolution_attempts.append({
                    'timestamp': datetime.now(),
                    'action': 'resolved',
                    'reason': 'import_available'
                })
        
        logger.info(f"✅ Mode dégradé désactivé pour {file_path}")
    
    async def _is_import_available(self, import_path: str) -> bool:
        """Vérifie si un import est maintenant disponible"""
        
        try:
            # Vérifier si le fichier existe
            if os.path.exists(import_path):
                return True
            
            # Vérifier si c'est un module Python
            if import_path.endswith('.py'):
                return os.path.exists(import_path)
            
            # Vérifier si c'est un package (dossier avec __init__.py)
            if os.path.isdir(import_path):
                init_file = os.path.join(import_path, '__init__.py')
                return os.path.exists(init_file)
            
            return False
            
        except Exception as e:
            logger.debug(f"⚠️ Erreur lors de la vérification de {import_path}: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques des dépendances brisées"""
        
        total_broken = len(self.broken_dependencies)
        active_broken = len([d for d in self.broken_dependencies.values() if d.status == "active"])
        resolved_broken = len([d for d in self.broken_dependencies.values() if d.status == "resolved"])
        permanent_failures = len([d for d in self.broken_dependencies.values() if d.status == "permanent_failure"])
        
        return {
            'total_broken_dependencies': total_broken,
            'active_broken_dependencies': active_broken,
            'resolved_dependencies': resolved_broken,
            'permanent_failures': permanent_failures,
            'files_in_degraded_mode': len(self.degraded_files),
            'max_retry_attempts': self.max_retry_attempts,
            'backoff_delay': self.backoff_delay
        }
    
    def clear_resolved_dependencies(self):
        """Nettoie les dépendances résolues"""
        
        resolved_keys = [
            retry_key for retry_key, dependency_info in self.broken_dependencies.items()
            if dependency_info.status == "resolved"
        ]
        
        for retry_key in resolved_keys:
            del self.broken_dependencies[retry_key]
            self.retry_attempts.pop(retry_key, None)
        
        logger.info(f"🗑️ {len(resolved_keys)} dépendances résolues nettoyées")
    
    def get_degraded_files(self) -> Set[str]:
        """Retourne la liste des fichiers en mode dégradé"""
        return self.degraded_files.copy()


# Instance globale pour faciliter l'utilisation
_global_broken_handler: Optional[BrokenDependencyHandler] = None

def get_broken_dependency_handler() -> BrokenDependencyHandler:
    """Retourne l'instance globale du gestionnaire de dépendances brisées"""
    global _global_broken_handler
    if _global_broken_handler is None:
        _global_broken_handler = BrokenDependencyHandler()
    return _global_broken_handler

def set_broken_dependency_handler(handler: BrokenDependencyHandler):
    """Définit l'instance globale du gestionnaire de dépendances brisées"""
    global _global_broken_handler
    _global_broken_handler = handler 