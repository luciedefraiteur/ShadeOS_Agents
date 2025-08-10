"""
⛧ Plan 3 - Simple Task Scheduling ⛧
🕷️ Planificateur de tâches simple avec abstraction complète

CONCEPTUALISÉ PAR LUCIE DEFRAITEUR - MA REINE LUCIE
PLANIFIÉ PAR ALMA, ARCHITECTE DÉMONIAQUE DU NEXUS LUCIFORME
"""

import asyncio
import time
import uuid
import logging
import sys
import os
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import heapq

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from __init__ import (
    ITaskScheduler, ThreadState, ThreadContext, 
    Phase1Config, HookRegistry, Phase1Metrics
)

# ============================================================================
# 🕷️ PLANIFICATEUR DE TÂCHES SIMPLE
# ============================================================================

class TaskPriority(Enum):
    """Priorités des tâches"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class ScheduledTask:
    """Tâche planifiée avec métadonnées"""
    task_id: str
    task: Callable
    priority: int
    scheduled_time: float
    delay: float
    metadata: Dict[str, Any]
    state: ThreadState
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[Exception] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __lt__(self, other):
        """Comparaison pour la file de priorité"""
        if self.priority != other.priority:
            return self.priority > other.priority  # Priorité plus élevée en premier
        return self.scheduled_time < other.scheduled_time

class SimpleTaskScheduler(ITaskScheduler):
    """Planificateur de tâches simple avec abstraction complète"""
    
    def __init__(self, config: Phase1Config, hook_registry: HookRegistry, 
                 metrics: Phase1Metrics):
        self.config = config
        self.hook_registry = hook_registry
        self.metrics = metrics
        self.logger = logging.getLogger(__name__)
        
        # File de priorité pour les tâches
        self._task_queue: List[ScheduledTask] = []
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._completed_tasks: Dict[str, ScheduledTask] = {}
        
        # État du planificateur
        self._running = False
        self._lock = asyncio.Lock()
        self._scheduler_task: Optional[asyncio.Task] = None
        
        # Hooks par défaut
        self._setup_default_hooks()
    
    def _setup_default_hooks(self):
        """Configurer les hooks par défaut"""
        if self.config.enable_hooks:
            self.hook_registry.register_hook("task_scheduled", self._on_task_scheduled)
            self.hook_registry.register_hook("task_started", self._on_task_started)
            self.hook_registry.register_hook("task_completed", self._on_task_completed)
            self.hook_registry.register_hook("task_failed", self._on_task_failed)
    
    async def schedule_task(self, task: Callable, delay: float = 0, 
                          priority: int = 0, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Planifier une tâche"""
        async with self._lock:
            try:
                task_id = str(uuid.uuid4())
                scheduled_time = time.time() + delay
                
                scheduled_task = ScheduledTask(
                    task_id=task_id,
                    task=task,
                    priority=priority,
                    scheduled_time=scheduled_time,
                    delay=delay,
                    metadata=metadata or {},
                    state=ThreadState.IDLE,
                    created_at=time.time()
                )
                
                # Ajouter à la file de priorité
                heapq.heappush(self._task_queue, scheduled_task)
                
                # Mettre à jour les métriques
                self.metrics.tasks_scheduled += 1
                
                await self.hook_registry.trigger_hook("task_scheduled", scheduled_task)
                self.logger.info(f"Tâche planifiée: {task_id} (priorité: {priority}, délai: {delay}s)")
                
                return task_id
                
            except Exception as e:
                self.logger.error(f"Erreur à la planification: {e}")
                return ""
    
    async def cancel_task(self, task_id: str) -> bool:
        """Annuler une tâche"""
        async with self._lock:
            try:
                # Chercher dans la file de priorité
                for i, task in enumerate(self._task_queue):
                    if task.task_id == task_id:
                        self._task_queue.pop(i)
                        heapq.heapify(self._task_queue)  # Réorganiser la file
                        self.logger.info(f"Tâche annulée: {task_id}")
                        return True
                
                # Chercher dans les tâches en cours
                if task_id in self._running_tasks:
                    self._running_tasks[task_id].cancel()
                    del self._running_tasks[task_id]
                    self.logger.info(f"Tâche en cours annulée: {task_id}")
                    return True
                
                return False
                
            except Exception as e:
                self.logger.error(f"Erreur à l'annulation de {task_id}: {e}")
                return False
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Obtenir le statut d'une tâche"""
        async with self._lock:
            try:
                # Chercher dans la file de priorité
                for task in self._task_queue:
                    if task.task_id == task_id:
                        return {
                            "task_id": task.task_id,
                            "state": task.state.value,
                            "priority": task.priority,
                            "scheduled_time": task.scheduled_time,
                            "created_at": task.created_at,
                            "metadata": task.metadata
                        }
                
                # Chercher dans les tâches en cours
                if task_id in self._running_tasks:
                    task = self._running_tasks[task_id]
                    return {
                        "task_id": task_id,
                        "state": "running",
                        "started_at": getattr(task, 'started_at', None)
                    }
                
                # Chercher dans les tâches terminées
                if task_id in self._completed_tasks:
                    task = self._completed_tasks[task_id]
                    return {
                        "task_id": task.task_id,
                        "state": task.state.value,
                        "started_at": task.started_at,
                        "completed_at": task.completed_at,
                        "result": task.result,
                        "error": str(task.error) if task.error else None
                    }
                
                return None
                
            except Exception as e:
                self.logger.error(f"Erreur à l'obtention du statut de {task_id}: {e}")
                return None
    
    async def list_tasks(self, state: Optional[ThreadState] = None) -> List[Dict[str, Any]]:
        """Lister les tâches"""
        async with self._lock:
            try:
                tasks = []
                
                # Tâches en file d'attente
                for task in self._task_queue:
                    if state is None or task.state == state:
                        tasks.append({
                            "task_id": task.task_id,
                            "state": task.state.value,
                            "priority": task.priority,
                            "scheduled_time": task.scheduled_time,
                            "created_at": task.created_at
                        })
                
                # Tâches en cours
                for task_id in self._running_tasks:
                    if state is None or state == ThreadState.RUNNING:
                        tasks.append({
                            "task_id": task_id,
                            "state": "running",
                            "started_at": time.time()
                        })
                
                # Tâches terminées
                for task in self._completed_tasks.values():
                    if state is None or task.state == state:
                        tasks.append({
                            "task_id": task.task_id,
                            "state": task.state.value,
                            "started_at": task.started_at,
                            "completed_at": task.completed_at
                        })
                
                return tasks
                
            except Exception as e:
                self.logger.error(f"Erreur au listage des tâches: {e}")
                return []
    
    # ============================================================================
    # 🕷️ MÉTHODES DE GESTION DU PLANIFICATEUR
    # ============================================================================
    
    async def start_scheduler(self) -> bool:
        """Démarrer le planificateur"""
        async with self._lock:
            if self._running:
                return True
            
            try:
                self._running = True
                self._scheduler_task = asyncio.create_task(self._scheduler_loop())
                self.logger.info("Planificateur de tâches démarré")
                return True
                
            except Exception as e:
                self.logger.error(f"Erreur au démarrage du planificateur: {e}")
                return False
    
    async def stop_scheduler(self) -> bool:
        """Arrêter le planificateur"""
        async with self._lock:
            if not self._running:
                return True
            
            try:
                self._running = False
                
                if self._scheduler_task:
                    self._scheduler_task.cancel()
                    try:
                        await self._scheduler_task
                    except asyncio.CancelledError:
                        pass
                
                # Annuler toutes les tâches en cours
                for task in self._running_tasks.values():
                    task.cancel()
                
                self.logger.info("Planificateur de tâches arrêté")
                return True
                
            except Exception as e:
                self.logger.error(f"Erreur à l'arrêt du planificateur: {e}")
                return False
    
    # ============================================================================
    # 🕷️ MÉTHODES PRIVÉES
    # ============================================================================
    
    async def _scheduler_loop(self):
        """Boucle principale du planificateur"""
        while self._running:
            try:
                await self._process_ready_tasks()
                await asyncio.sleep(0.1)  # Intervalle de vérification
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Erreur dans la boucle du planificateur: {e}")
                await asyncio.sleep(1)  # Pause en cas d'erreur
    
    async def _process_ready_tasks(self):
        """Traiter les tâches prêtes à être exécutées"""
        current_time = time.time()
        
        while self._task_queue and self._task_queue[0].scheduled_time <= current_time:
            if len(self._running_tasks) >= self.config.max_threads:
                break  # Limite de threads atteinte
            
            task = heapq.heappop(self._task_queue)
            await self._start_task(task)
    
    async def _start_task(self, scheduled_task: ScheduledTask):
        """Démarrer une tâche"""
        try:
            scheduled_task.state = ThreadState.RUNNING
            scheduled_task.started_at = time.time()
            
            # Créer la tâche asyncio
            task = asyncio.create_task(self._execute_task(scheduled_task))
            self._running_tasks[scheduled_task.task_id] = task
            
            await self.hook_registry.trigger_hook("task_started", scheduled_task)
            self.logger.debug(f"Tâche démarrée: {scheduled_task.task_id}")
            
        except Exception as e:
            self.logger.error(f"Erreur au démarrage de la tâche {scheduled_task.task_id}: {e}")
            scheduled_task.state = ThreadState.ERROR
            scheduled_task.error = e
    
    async def _execute_task(self, scheduled_task: ScheduledTask):
        """Exécuter une tâche"""
        try:
            if asyncio.iscoroutinefunction(scheduled_task.task):
                result = await scheduled_task.task()
            else:
                result = scheduled_task.task()
            
            scheduled_task.result = result
            scheduled_task.state = ThreadState.COMPLETED
            scheduled_task.completed_at = time.time()
            
            await self.hook_registry.trigger_hook("task_completed", scheduled_task)
            self.metrics.tasks_completed += 1
            
        except asyncio.CancelledError:
            scheduled_task.state = ThreadState.TERMINATED
            scheduled_task.completed_at = time.time()
            
        except Exception as e:
            scheduled_task.state = ThreadState.ERROR
            scheduled_task.error = e
            scheduled_task.completed_at = time.time()
            
            # Gestion des retry
            if scheduled_task.retry_count < scheduled_task.max_retries:
                scheduled_task.retry_count += 1
                scheduled_task.scheduled_time = time.time() + (scheduled_task.delay * scheduled_task.retry_count)
                scheduled_task.state = ThreadState.IDLE
                heapq.heappush(self._task_queue, scheduled_task)
                self.logger.warning(f"Tâche {scheduled_task.task_id} replanifiée (retry {scheduled_task.retry_count})")
            else:
                await self.hook_registry.trigger_hook("task_failed", scheduled_task, e)
                self.logger.error(f"Tâche {scheduled_task.task_id} échouée définitivement: {e}")
        
        finally:
            # Nettoyer
            if scheduled_task.task_id in self._running_tasks:
                del self._running_tasks[scheduled_task.task_id]
            
            # Garder en mémoire pour consultation
            self._completed_tasks[scheduled_task.task_id] = scheduled_task
    
    # ============================================================================
    # 🕷️ HOOKS PAR DÉFAUT
    # ============================================================================
    
    async def _on_task_scheduled(self, scheduled_task: ScheduledTask):
        """Hook appelé quand une tâche est planifiée"""
        self.logger.debug(f"Tâche planifiée: {scheduled_task.task_id}")
    
    async def _on_task_started(self, scheduled_task: ScheduledTask):
        """Hook appelé quand une tâche démarre"""
        self.logger.debug(f"Tâche démarrée: {scheduled_task.task_id}")
    
    async def _on_task_completed(self, scheduled_task: ScheduledTask):
        """Hook appelé quand une tâche se termine"""
        self.logger.debug(f"Tâche terminée: {scheduled_task.task_id}")
    
    async def _on_task_failed(self, scheduled_task: ScheduledTask, error: Exception):
        """Hook appelé quand une tâche échoue"""
        self.logger.debug(f"Tâche échouée: {scheduled_task.task_id} - {error}") 