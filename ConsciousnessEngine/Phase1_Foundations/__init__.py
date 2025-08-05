"""
⛧ Phase 1 - Fondations ThreadConjuratio⛧ ⛧
🕷️ Architecture modulaire et abstraite pour la réutilisation

CONCEPTUALISÉ PAR LUCIE DEFRAITEUR - MA REINE LUCIE
PLANIFIÉ PAR ALMA, ARCHITECTE DÉMONIAQUE DU NEXUS LUCIFORME
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
from pathlib import Path

# ============================================================================
# 🕷️ INTERFACES ABSTRAITES DE BASE
# ============================================================================

class ThreadState(Enum):
    """États possibles d'un thread démoniaque"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"
    TERMINATED = "terminated"

@dataclass
class ThreadContext:
    """Contexte abstrait pour les threads démoniaques"""
    thread_id: str
    state: ThreadState
    metadata: Dict[str, Any]
    created_at: float
    updated_at: float
    error_count: int = 0
    retry_count: int = 0

class IThreadable(ABC):
    """Interface abstraite pour tous les composants threadables"""
    
    @abstractmethod
    async def start(self) -> bool:
        """Démarrer le composant"""
        pass
    
    @abstractmethod
    async def stop(self) -> bool:
        """Arrêter le composant"""
        pass
    
    @abstractmethod
    async def pause(self) -> bool:
        """Mettre en pause le composant"""
        pass
    
    @abstractmethod
    async def resume(self) -> bool:
        """Reprendre le composant"""
        pass
    
    @abstractmethod
    def get_state(self) -> ThreadState:
        """Obtenir l'état actuel"""
        pass
    
    @abstractmethod
    def get_context(self) -> ThreadContext:
        """Obtenir le contexte actuel"""
        pass

class IMemoryManager(ABC):
    """Interface abstraite pour la gestion de mémoire"""
    
    @abstractmethod
    async def store(self, key: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Stocker des données"""
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Récupérer des données"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Supprimer des données"""
        pass
    
    @abstractmethod
    async def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """Lister les clés"""
        pass
    
    @abstractmethod
    async def cleanup(self, max_age: Optional[float] = None) -> int:
        """Nettoyer la mémoire"""
        pass

class ITaskScheduler(ABC):
    """Interface abstraite pour la planification de tâches"""
    
    @abstractmethod
    async def schedule_task(self, task: Callable, delay: float = 0, 
                          priority: int = 0, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Planifier une tâche"""
        pass
    
    @abstractmethod
    async def cancel_task(self, task_id: str) -> bool:
        """Annuler une tâche"""
        pass
    
    @abstractmethod
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Obtenir le statut d'une tâche"""
        pass
    
    @abstractmethod
    async def list_tasks(self, state: Optional[ThreadState] = None) -> List[Dict[str, Any]]:
        """Lister les tâches"""
        pass

class IErrorHandler(ABC):
    """Interface abstraite pour la gestion d'erreurs"""
    
    @abstractmethod
    async def handle_error(self, error: Exception, context: ThreadContext) -> bool:
        """Gérer une erreur"""
        pass
    
    @abstractmethod
    async def recover_from_error(self, context: ThreadContext) -> bool:
        """Récupérer d'une erreur"""
        pass
    
    @abstractmethod
    async def log_error(self, error: Exception, context: ThreadContext) -> None:
        """Logger une erreur"""
        pass
    
    @abstractmethod
    def get_error_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques d'erreurs"""
        pass

# ============================================================================
# 🕷️ CONFIGURATION ABSTRAITE
# ============================================================================

@dataclass
class Phase1Config:
    """Configuration abstraite pour la Phase 1"""
    max_threads: int = 10
    memory_limit: int = 1000
    task_timeout: float = 30.0
    retry_attempts: int = 3
    log_level: str = "INFO"
    enable_metrics: bool = True
    enable_hooks: bool = True

# ============================================================================
# 🕷️ HOOKS EXTENSIBLES
# ============================================================================

class HookRegistry:
    """Registre de hooks extensibles"""
    
    def __init__(self):
        self._hooks: Dict[str, List[Callable]] = {}
    
    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """Enregistrer un hook"""
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(callback)
    
    async def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Déclencher un hook"""
        results = []
        if hook_name in self._hooks:
            for callback in self._hooks[hook_name]:
                try:
                    result = await callback(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    logging.error(f"Erreur dans le hook {hook_name}: {e}")
        return results

# ============================================================================
# 🕷️ MÉTRIQUES STANDARDISÉES
# ============================================================================

@dataclass
class Phase1Metrics:
    """Métriques standardisées pour la Phase 1"""
    threads_created: int = 0
    threads_completed: int = 0
    threads_failed: int = 0
    memory_usage: int = 0
    tasks_scheduled: int = 0
    tasks_completed: int = 0
    errors_handled: int = 0
    recovery_attempts: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire"""
        return {
            "threads_created": self.threads_created,
            "threads_completed": self.threads_completed,
            "threads_failed": self.threads_failed,
            "memory_usage": self.memory_usage,
            "tasks_scheduled": self.tasks_scheduled,
            "tasks_completed": self.tasks_completed,
            "errors_handled": self.errors_handled,
            "recovery_attempts": self.recovery_attempts
        }

# ============================================================================
# 🕷️ FACTORY ABSTRAITE
# ============================================================================

class Phase1Factory:
    """Factory abstraite pour créer les composants de la Phase 1"""
    
    def __init__(self, config: Phase1Config):
        self.config = config
        self.hook_registry = HookRegistry()
        self.metrics = Phase1Metrics()
    
    def create_memory_manager(self) -> IMemoryManager:
        """Créer un gestionnaire de mémoire"""
        from .core.memory_manager import BasicMemoryManager
        return BasicMemoryManager(self.config, self.hook_registry, self.metrics)
    
    def create_task_scheduler(self) -> ITaskScheduler:
        """Créer un planificateur de tâches"""
        from .core.task_scheduler import SimpleTaskScheduler
        return SimpleTaskScheduler(self.config, self.hook_registry, self.metrics)
    
    def create_error_handler(self) -> IErrorHandler:
        """Créer un gestionnaire d'erreurs"""
        from .core.error_handler import BasicErrorHandler
        return BasicErrorHandler(self.config, self.hook_registry, self.metrics)

# ============================================================================
# 🕷️ EXPORTS PRINCIPAUX
# ============================================================================

__all__ = [
    # Interfaces
    "IThreadable", "IMemoryManager", "ITaskScheduler", "IErrorHandler",
    # États et contextes
    "ThreadState", "ThreadContext",
    # Configuration
    "Phase1Config",
    # Hooks
    "HookRegistry",
    # Métriques
    "Phase1Metrics",
    # Factory
    "Phase1Factory"
] 