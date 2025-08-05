"""
⛧ Plan 2 - Basic Memory Management ⛧
🕷️ Gestionnaire de mémoire de base avec abstraction complète

CONCEPTUALISÉ PAR LUCIE DEFRAITEUR - MA REINE LUCIE
PLANIFIÉ PAR ALMA, ARCHITECTE DÉMONIAQUE DU NEXUS LUCIFORME
"""

import time
import json
import pickle
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from pathlib import Path
import asyncio

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from __init__ import (
    IMemoryManager, ThreadState, ThreadContext, 
    Phase1Config, HookRegistry, Phase1Metrics
)

# ============================================================================
# 🕷️ GESTIONNAIRE DE MÉMOIRE DE BASE
# ============================================================================

@dataclass
class MemoryEntry:
    """Entrée de mémoire avec métadonnées"""
    key: str
    data: Any
    metadata: Dict[str, Any]
    created_at: float
    updated_at: float
    access_count: int = 0
    size_bytes: int = 0
    ttl: Optional[float] = None  # Time To Live en secondes
    
    def is_expired(self) -> bool:
        """Vérifier si l'entrée a expiré"""
        if self.ttl is None:
            return False
        return time.time() > self.created_at + self.ttl
    
    def update_access(self):
        """Mettre à jour les statistiques d'accès"""
        self.access_count += 1
        self.updated_at = time.time()

class BasicMemoryManager(IMemoryManager):
    """Gestionnaire de mémoire de base avec abstraction complète"""
    
    def __init__(self, config: Phase1Config, hook_registry: HookRegistry, 
                 metrics: Phase1Metrics):
        self.config = config
        self.hook_registry = hook_registry
        self.metrics = metrics
        self.logger = logging.getLogger(__name__)
        
        # Stockage en mémoire
        self._memory: Dict[str, MemoryEntry] = {}
        self._lock = asyncio.Lock()
        
        # Statistiques
        self._total_size = 0
        self._hit_count = 0
        self._miss_count = 0
        
        # Hooks par défaut
        self._setup_default_hooks()
    
    def _setup_default_hooks(self):
        """Configurer les hooks par défaut"""
        if self.config.enable_hooks:
            self.hook_registry.register_hook("memory_stored", self._on_memory_stored)
            self.hook_registry.register_hook("memory_retrieved", self._on_memory_retrieved)
            self.hook_registry.register_hook("memory_deleted", self._on_memory_deleted)
            self.hook_registry.register_hook("memory_cleaned", self._on_memory_cleaned)
    
    async def store(self, key: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Stocker des données en mémoire"""
        async with self._lock:
            try:
                # Vérifier la limite de mémoire
                if len(self._memory) >= self.config.memory_limit:
                    await self._evict_oldest()
                
                # Calculer la taille
                size_bytes = self._calculate_size(data)
                
                # Créer l'entrée
                entry = MemoryEntry(
                    key=key,
                    data=data,
                    metadata=metadata or {},
                    created_at=time.time(),
                    updated_at=time.time(),
                    size_bytes=size_bytes
                )
                
                # Stocker
                self._memory[key] = entry
                self._total_size += size_bytes
                
                # Mettre à jour les métriques
                self.metrics.memory_usage = len(self._memory)
                
                await self.hook_registry.trigger_hook("memory_stored", key, entry)
                self.logger.debug(f"Données stockées: {key} ({size_bytes} bytes)")
                
                return True
                
            except Exception as e:
                self.logger.error(f"Erreur au stockage de {key}: {e}")
                return False
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """Récupérer des données de la mémoire"""
        async with self._lock:
            try:
                if key not in self._memory:
                    self._miss_count += 1
                    return None
                
                entry = self._memory[key]
                
                # Vérifier l'expiration
                if entry.is_expired():
                    await self.delete(key)
                    self._miss_count += 1
                    return None
                
                # Mettre à jour les statistiques
                entry.update_access()
                self._hit_count += 1
                
                await self.hook_registry.trigger_hook("memory_retrieved", key, entry)
                self.logger.debug(f"Données récupérées: {key}")
                
                return entry.data
                
            except Exception as e:
                self.logger.error(f"Erreur à la récupération de {key}: {e}")
                return None
    
    async def delete(self, key: str) -> bool:
        """Supprimer des données de la mémoire"""
        async with self._lock:
            try:
                if key not in self._memory:
                    return False
                
                entry = self._memory[key]
                self._total_size -= entry.size_bytes
                del self._memory[key]
                
                # Mettre à jour les métriques
                self.metrics.memory_usage = len(self._memory)
                
                await self.hook_registry.trigger_hook("memory_deleted", key, entry)
                self.logger.debug(f"Données supprimées: {key}")
                
                return True
                
            except Exception as e:
                self.logger.error(f"Erreur à la suppression de {key}: {e}")
                return False
    
    async def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """Lister les clés en mémoire"""
        async with self._lock:
            try:
                keys = list(self._memory.keys())
                
                if pattern:
                    import fnmatch
                    keys = [k for k in keys if fnmatch.fnmatch(k, pattern)]
                
                return keys
                
            except Exception as e:
                self.logger.error(f"Erreur au listage des clés: {e}")
                return []
    
    async def cleanup(self, max_age: Optional[float] = None) -> int:
        """Nettoyer la mémoire"""
        async with self._lock:
            try:
                current_time = time.time()
                cleaned_count = 0
                
                keys_to_delete = []
                
                for key, entry in self._memory.items():
                    should_delete = False
                    
                    # Vérifier l'expiration TTL
                    if entry.is_expired():
                        should_delete = True
                    
                    # Vérifier l'âge maximum
                    if max_age and (current_time - entry.created_at) > max_age:
                        should_delete = True
                    
                    if should_delete:
                        keys_to_delete.append(key)
                
                # Supprimer les entrées
                for key in keys_to_delete:
                    await self.delete(key)
                    cleaned_count += 1
                
                await self.hook_registry.trigger_hook("memory_cleaned", cleaned_count)
                self.logger.info(f"Mémoire nettoyée: {cleaned_count} entrées supprimées")
                
                return cleaned_count
                
            except Exception as e:
                self.logger.error(f"Erreur au nettoyage: {e}")
                return 0
    
    # ============================================================================
    # 🕷️ MÉTHODES AVANCÉES
    # ============================================================================
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques de mémoire"""
        async with self._lock:
            return {
                "total_entries": len(self._memory),
                "total_size_bytes": self._total_size,
                "hit_count": self._hit_count,
                "miss_count": self._miss_count,
                "hit_ratio": self._hit_count / (self._hit_count + self._miss_count) if (self._hit_count + self._miss_count) > 0 else 0,
                "memory_limit": self.config.memory_limit,
                "usage_percentage": (len(self._memory) / self.config.memory_limit) * 100
            }
    
    async def set_ttl(self, key: str, ttl_seconds: float) -> bool:
        """Définir un TTL pour une clé"""
        async with self._lock:
            if key not in self._memory:
                return False
            
            self._memory[key].ttl = ttl_seconds
            self.logger.debug(f"TTL défini pour {key}: {ttl_seconds}s")
            return True
    
    async def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Obtenir les informations d'une entrée"""
        async with self._lock:
            if key not in self._memory:
                return None
            
            entry = self._memory[key]
            return {
                "key": entry.key,
                "created_at": entry.created_at,
                "updated_at": entry.updated_at,
                "access_count": entry.access_count,
                "size_bytes": entry.size_bytes,
                "ttl": entry.ttl,
                "is_expired": entry.is_expired(),
                "metadata": entry.metadata
            }
    
    # ============================================================================
    # 🕷️ MÉTHODES PRIVÉES
    # ============================================================================
    
    def _calculate_size(self, data: Any) -> int:
        """Calculer la taille approximative des données"""
        try:
            if isinstance(data, (str, bytes)):
                return len(data)
            elif isinstance(data, (int, float, bool)):
                return 8
            elif isinstance(data, (list, tuple)):
                return sum(self._calculate_size(item) for item in data)
            elif isinstance(data, dict):
                return sum(self._calculate_size(v) for v in data.values())
            else:
                # Estimation pour les objets complexes
                return len(str(data))
        except:
            return 100  # Taille par défaut
    
    async def _evict_oldest(self):
        """Évincer l'entrée la plus ancienne"""
        if not self._memory:
            return
        
        # Trouver l'entrée la plus ancienne
        oldest_key = min(self._memory.keys(), 
                        key=lambda k: self._memory[k].created_at)
        
        await self.delete(oldest_key)
        self.logger.debug(f"Entrée évincée: {oldest_key}")
    
    # ============================================================================
    # 🕷️ HOOKS PAR DÉFAUT
    # ============================================================================
    
    async def _on_memory_stored(self, key: str, entry: MemoryEntry):
        """Hook appelé quand des données sont stockées"""
        self.logger.debug(f"Données stockées: {key}")
    
    async def _on_memory_retrieved(self, key: str, entry: MemoryEntry):
        """Hook appelé quand des données sont récupérées"""
        self.logger.debug(f"Données récupérées: {key}")
    
    async def _on_memory_deleted(self, key: str, entry: MemoryEntry):
        """Hook appelé quand des données sont supprimées"""
        self.logger.debug(f"Données supprimées: {key}")
    
    async def _on_memory_cleaned(self, cleaned_count: int):
        """Hook appelé quand la mémoire est nettoyée"""
        self.logger.debug(f"Mémoire nettoyée: {cleaned_count} entrées") 