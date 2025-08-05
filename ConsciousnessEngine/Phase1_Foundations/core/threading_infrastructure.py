"""
⛧ Plan 1 - Core Threading Infrastructure ⛧
🕷️ Infrastructure de threading de base avec abstraction complète

CONCEPTUALISÉ PAR LUCIE DEFRAITEUR - MA REINE LUCIE
PLANIFIÉ PAR ALMA, ARCHITECTE DÉMONIAQUE DU NEXUS LUCIFORME
"""

import asyncio
import time
import uuid
import logging
import sys
import os
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from __init__ import (
    IThreadable, ThreadState, ThreadContext, 
    Phase1Config, HookRegistry, Phase1Metrics
)

# ============================================================================
# 🕷️ INFRASTRUCTURE DE THREADING DE BASE
# ============================================================================

@dataclass
class ThreadInfo:
    """Informations détaillées sur un thread"""
    thread_id: str
    name: str
    state: ThreadState
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_count: int = 0
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    task: Optional[Callable] = None
    result: Optional[Any] = None
    error: Optional[Exception] = None

class CoreThreadingInfrastructure(IThreadable):
    """Infrastructure de threading de base avec abstraction complète"""
    
    def __init__(self, config: Phase1Config, hook_registry: HookRegistry, 
                 metrics: Phase1Metrics):
        self.config = config
        self.hook_registry = hook_registry
        self.metrics = metrics
        self.logger = logging.getLogger(__name__)
        
        # État du système
        self._state = ThreadState.IDLE
        self._context = ThreadContext(
            thread_id=str(uuid.uuid4()),
            state=ThreadState.IDLE,
            metadata={"type": "threading_infrastructure"},
            created_at=time.time(),
            updated_at=time.time()
        )
        
        # Gestion des threads
        self._threads: Dict[str, ThreadInfo] = {}
        self._thread_tasks: Dict[str, asyncio.Task] = {}
        self._running = False
        self._lock = asyncio.Lock()
        
        # Hooks par défaut
        self._setup_default_hooks()
    
    def _setup_default_hooks(self):
        """Configurer les hooks par défaut"""
        if self.config.enable_hooks:
            self.hook_registry.register_hook("thread_created", self._on_thread_created)
            self.hook_registry.register_hook("thread_started", self._on_thread_started)
            self.hook_registry.register_hook("thread_completed", self._on_thread_completed)
            self.hook_registry.register_hook("thread_failed", self._on_thread_failed)
    
    async def start(self) -> bool:
        """Démarrer l'infrastructure de threading"""
        async with self._lock:
            if self._running:
                return True
            
            try:
                self._running = True
                self._state = ThreadState.RUNNING
                self._context.state = ThreadState.RUNNING
                self._context.updated_at = time.time()
                
                await self.hook_registry.trigger_hook("infrastructure_started", self)
                self.logger.info("Infrastructure de threading démarrée")
                
                self.metrics.threads_created += 1
                return True
                
            except Exception as e:
                self.logger.error(f"Erreur au démarrage: {e}")
                self._state = ThreadState.ERROR
                self._context.state = ThreadState.ERROR
                return False
    
    async def stop(self) -> bool:
        """Arrêter l'infrastructure de threading"""
        async with self._lock:
            if not self._running:
                return True
            
            try:
                self._running = False
                self._state = ThreadState.TERMINATED
                self._context.state = ThreadState.TERMINATED
                self._context.updated_at = time.time()
                
                # Arrêter tous les threads actifs
                await self._stop_all_threads()
                
                await self.hook_registry.trigger_hook("infrastructure_stopped", self)
                self.logger.info("Infrastructure de threading arrêtée")
                return True
                
            except Exception as e:
                self.logger.error(f"Erreur à l'arrêt: {e}")
                return False
    
    async def pause(self) -> bool:
        """Mettre en pause l'infrastructure"""
        async with self._lock:
            if self._state != ThreadState.RUNNING:
                return False
            
            try:
                self._state = ThreadState.PAUSED
                self._context.state = ThreadState.PAUSED
                self._context.updated_at = time.time()
                
                # Mettre en pause tous les threads
                await self._pause_all_threads()
                
                await self.hook_registry.trigger_hook("infrastructure_paused", self)
                self.logger.info("Infrastructure de threading mise en pause")
                return True
                
            except Exception as e:
                self.logger.error(f"Erreur à la pause: {e}")
                return False
    
    async def resume(self) -> bool:
        """Reprendre l'infrastructure"""
        async with self._lock:
            if self._state != ThreadState.PAUSED:
                return False
            
            try:
                self._state = ThreadState.RUNNING
                self._context.state = ThreadState.RUNNING
                self._context.updated_at = time.time()
                
                # Reprendre tous les threads
                await self._resume_all_threads()
                
                await self.hook_registry.trigger_hook("infrastructure_resumed", self)
                self.logger.info("Infrastructure de threading reprise")
                return True
                
            except Exception as e:
                self.logger.error(f"Erreur à la reprise: {e}")
                return False
    
    def get_state(self) -> ThreadState:
        """Obtenir l'état actuel"""
        return self._state
    
    def get_context(self) -> ThreadContext:
        """Obtenir le contexte actuel"""
        return self._context
    
    # ============================================================================
    # 🕷️ GESTION DES THREADS
    # ============================================================================
    
    async def create_thread(self, name: str, task: Callable, 
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """Créer un nouveau thread"""
        if not self._running:
            raise RuntimeError("Infrastructure non démarrée")
        
        thread_id = str(uuid.uuid4())
        thread_info = ThreadInfo(
            thread_id=thread_id,
            name=name,
            state=ThreadState.IDLE,
            created_at=time.time(),
            task=task,
            metadata=metadata or {}
        )
        
        self._threads[thread_id] = thread_info
        await self.hook_registry.trigger_hook("thread_created", thread_info)
        
        self.logger.info(f"Thread créé: {name} ({thread_id})")
        return thread_id
    
    async def start_thread(self, thread_id: str) -> bool:
        """Démarrer un thread"""
        if thread_id not in self._threads:
            return False
        
        thread_info = self._threads[thread_id]
        if thread_info.state != ThreadState.IDLE:
            return False
        
        try:
            thread_info.state = ThreadState.RUNNING
            thread_info.started_at = time.time()
            
            # Créer la tâche asyncio
            task = asyncio.create_task(self._run_thread(thread_info))
            self._thread_tasks[thread_id] = task
            
            await self.hook_registry.trigger_hook("thread_started", thread_info)
            self.logger.info(f"Thread démarré: {thread_info.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur au démarrage du thread {thread_id}: {e}")
            thread_info.state = ThreadState.ERROR
            thread_info.error = e
            return False
    
    async def stop_thread(self, thread_id: str) -> bool:
        """Arrêter un thread"""
        if thread_id not in self._threads:
            return False
        
        thread_info = self._threads[thread_id]
        if thread_info.state in [ThreadState.COMPLETED, ThreadState.TERMINATED]:
            return True
        
        try:
            # Annuler la tâche asyncio
            if thread_id in self._thread_tasks:
                self._thread_tasks[thread_id].cancel()
                del self._thread_tasks[thread_id]
            
            thread_info.state = ThreadState.TERMINATED
            thread_info.completed_at = time.time()
            
            self.logger.info(f"Thread arrêté: {thread_info.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur à l'arrêt du thread {thread_id}: {e}")
            return False
    
    async def get_thread_info(self, thread_id: str) -> Optional[ThreadInfo]:
        """Obtenir les informations d'un thread"""
        return self._threads.get(thread_id)
    
    async def list_threads(self, state: Optional[ThreadState] = None) -> List[ThreadInfo]:
        """Lister les threads"""
        threads = list(self._threads.values())
        if state:
            threads = [t for t in threads if t.state == state]
        return threads
    
    # ============================================================================
    # 🕷️ MÉTHODES PRIVÉES
    # ============================================================================
    
    async def _run_thread(self, thread_info: ThreadInfo):
        """Exécuter un thread"""
        try:
            if asyncio.iscoroutinefunction(thread_info.task):
                result = await thread_info.task()
            else:
                result = thread_info.task()
            
            thread_info.result = result
            thread_info.state = ThreadState.COMPLETED
            thread_info.completed_at = time.time()
            
            await self.hook_registry.trigger_hook("thread_completed", thread_info)
            self.metrics.threads_completed += 1
            
        except asyncio.CancelledError:
            thread_info.state = ThreadState.TERMINATED
            thread_info.completed_at = time.time()
            
        except Exception as e:
            thread_info.state = ThreadState.ERROR
            thread_info.error = e
            thread_info.error_count += 1
            thread_info.completed_at = time.time()
            
            await self.hook_registry.trigger_hook("thread_failed", thread_info, e)
            self.metrics.threads_failed += 1
            self.logger.error(f"Erreur dans le thread {thread_info.name}: {e}")
        
        finally:
            # Nettoyer la tâche
            if thread_info.thread_id in self._thread_tasks:
                del self._thread_tasks[thread_info.thread_id]
    
    async def _stop_all_threads(self):
        """Arrêter tous les threads"""
        for thread_id in list(self._threads.keys()):
            await self.stop_thread(thread_id)
    
    async def _pause_all_threads(self):
        """Mettre en pause tous les threads"""
        for thread_info in self._threads.values():
            if thread_info.state == ThreadState.RUNNING:
                thread_info.state = ThreadState.PAUSED
    
    async def _resume_all_threads(self):
        """Reprendre tous les threads"""
        for thread_info in self._threads.values():
            if thread_info.state == ThreadState.PAUSED:
                thread_info.state = ThreadState.RUNNING
    
    # ============================================================================
    # 🕷️ HOOKS PAR DÉFAUT
    # ============================================================================
    
    async def _on_thread_created(self, thread_info: ThreadInfo):
        """Hook appelé quand un thread est créé"""
        self.logger.debug(f"Thread créé: {thread_info.name}")
    
    async def _on_thread_started(self, thread_info: ThreadInfo):
        """Hook appelé quand un thread démarre"""
        self.logger.debug(f"Thread démarré: {thread_info.name}")
    
    async def _on_thread_completed(self, thread_info: ThreadInfo):
        """Hook appelé quand un thread se termine"""
        self.logger.debug(f"Thread terminé: {thread_info.name}")
    
    async def _on_thread_failed(self, thread_info: ThreadInfo, error: Exception):
        """Hook appelé quand un thread échoue"""
        self.logger.debug(f"Thread échoué: {thread_info.name} - {error}") 