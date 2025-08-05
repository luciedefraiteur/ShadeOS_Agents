"""
⛧ Plan 4 - Error Handling & Recovery ⛧
🕷️ Gestionnaire d'erreurs de base avec abstraction complète

CONCEPTUALISÉ PAR LUCIE DEFRAITEUR - MA REINE LUCIE
PLANIFIÉ PAR ALMA, ARCHITECTE DÉMONIAQUE DU NEXUS LUCIFORME
"""

import time
import traceback
import logging
import sys
import os
from typing import Dict, Any, Optional, List, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from __init__ import (
    IErrorHandler, ThreadState, ThreadContext, 
    Phase1Config, HookRegistry, Phase1Metrics
)

# ============================================================================
# 🕷️ GESTIONNAIRE D'ERREURS DE BASE
# ============================================================================

class ErrorSeverity(Enum):
    """Niveaux de sévérité des erreurs"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorType(Enum):
    """Types d'erreurs"""
    RUNTIME = "runtime"
    TIMEOUT = "timeout"
    MEMORY = "memory"
    NETWORK = "network"
    VALIDATION = "validation"
    SYSTEM = "system"
    UNKNOWN = "unknown"

@dataclass
class ErrorRecord:
    """Enregistrement d'erreur avec métadonnées"""
    error_id: str
    error: Exception
    context: ThreadContext
    severity: ErrorSeverity
    error_type: ErrorType
    timestamp: float
    stack_trace: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    handled: bool = False
    recovery_attempted: bool = False
    recovery_successful: bool = False

class BasicErrorHandler(IErrorHandler):
    """Gestionnaire d'erreurs de base avec abstraction complète"""
    
    def __init__(self, config: Phase1Config, hook_registry: HookRegistry, 
                 metrics: Phase1Metrics):
        self.config = config
        self.hook_registry = hook_registry
        self.metrics = metrics
        self.logger = logging.getLogger(__name__)
        
        # Stockage des erreurs
        self._error_records: Dict[str, ErrorRecord] = {}
        self._error_handlers: Dict[Type[Exception], List[Callable]] = {}
        self._recovery_strategies: Dict[ErrorType, List[Callable]] = {}
        
        # Statistiques
        self._total_errors = 0
        self._handled_errors = 0
        self._recovery_attempts = 0
        self._successful_recoveries = 0
        
        # Verrou pour la synchronisation
        self._lock = asyncio.Lock()
        
        # Hooks par défaut
        self._setup_default_hooks()
        self._setup_default_handlers()
        self._setup_default_recovery_strategies()
    
    def _setup_default_hooks(self):
        """Configurer les hooks par défaut"""
        if self.config.enable_hooks:
            self.hook_registry.register_hook("error_occurred", self._on_error_occurred)
            self.hook_registry.register_hook("error_handled", self._on_error_handled)
            self.hook_registry.register_hook("recovery_attempted", self._on_recovery_attempted)
            self.hook_registry.register_hook("recovery_successful", self._on_recovery_successful)
    
    def _setup_default_handlers(self):
        """Configurer les gestionnaires d'erreurs par défaut"""
        # Gestionnaire pour les erreurs de timeout
        self.register_error_handler(TimeoutError, self._handle_timeout_error)
        self.register_error_handler(asyncio.TimeoutError, self._handle_timeout_error)
        
        # Gestionnaire pour les erreurs de mémoire
        self.register_error_handler(MemoryError, self._handle_memory_error)
        
        # Gestionnaire pour les erreurs de validation
        self.register_error_handler(ValueError, self._handle_validation_error)
        self.register_error_handler(TypeError, self._handle_validation_error)
        
        # Gestionnaire pour les erreurs système
        self.register_error_handler(SystemError, self._handle_system_error)
        self.register_error_handler(OSError, self._handle_system_error)
    
    def _setup_default_recovery_strategies(self):
        """Configurer les stratégies de récupération par défaut"""
        # Stratégie pour les erreurs de timeout
        self.register_recovery_strategy(ErrorType.TIMEOUT, self._recover_from_timeout)
        
        # Stratégie pour les erreurs de mémoire
        self.register_recovery_strategy(ErrorType.MEMORY, self._recover_from_memory_error)
        
        # Stratégie pour les erreurs de validation
        self.register_recovery_strategy(ErrorType.VALIDATION, self._recover_from_validation_error)
        
        # Stratégie pour les erreurs système
        self.register_recovery_strategy(ErrorType.SYSTEM, self._recover_from_system_error)
    
    async def handle_error(self, error: Exception, context: ThreadContext) -> bool:
        """Gérer une erreur"""
        async with self._lock:
            try:
                # Créer l'enregistrement d'erreur
                error_record = self._create_error_record(error, context)
                self._error_records[error_record.error_id] = error_record
                
                # Mettre à jour les statistiques
                self._total_errors += 1
                self.metrics.errors_handled += 1
                
                # Logger l'erreur
                await self.log_error(error, context)
                
                # Déclencher le hook
                await self.hook_registry.trigger_hook("error_occurred", error_record)
                
                # Appliquer les gestionnaires d'erreurs
                handled = await self._apply_error_handlers(error_record)
                
                if handled:
                    error_record.handled = True
                    self._handled_errors += 1
                    await self.hook_registry.trigger_hook("error_handled", error_record)
                
                self.logger.info(f"Erreur gérée: {error_record.error_id} ({error_record.error_type.value})")
                return handled
                
            except Exception as e:
                self.logger.error(f"Erreur dans la gestion d'erreur: {e}")
                return False
    
    async def recover_from_error(self, context: ThreadContext) -> bool:
        """Récupérer d'une erreur"""
        async with self._lock:
            try:
                # Trouver les erreurs non récupérées pour ce contexte
                unrecovered_errors = [
                    record for record in self._error_records.values()
                    if record.context.thread_id == context.thread_id 
                    and not record.recovery_attempted
                ]
                
                if not unrecovered_errors:
                    return True
                
                recovery_successful = True
                
                for error_record in unrecovered_errors:
                    # Appliquer les stratégies de récupération
                    recovered = await self._apply_recovery_strategies(error_record)
                    
                    error_record.recovery_attempted = True
                    error_record.recovery_successful = recovered
                    
                    if recovered:
                        self._successful_recoveries += 1
                        await self.hook_registry.trigger_hook("recovery_successful", error_record)
                    else:
                        recovery_successful = False
                        await self.hook_registry.trigger_hook("recovery_failed", error_record)
                    
                    self._recovery_attempts += 1
                    self.metrics.recovery_attempts += 1
                
                self.logger.info(f"Récupération tentée pour {len(unrecovered_errors)} erreurs")
                return recovery_successful
                
            except Exception as e:
                self.logger.error(f"Erreur dans la récupération: {e}")
                return False
    
    async def log_error(self, error: Exception, context: ThreadContext) -> None:
        """Logger une erreur"""
        try:
            error_info = {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "thread_id": context.thread_id,
                "thread_state": context.state.value,
                "timestamp": time.time(),
                "stack_trace": traceback.format_exc()
            }
            
            self.logger.error(f"Erreur détectée: {error_info}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du logging: {e}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques d'erreurs"""
        return {
            "total_errors": self._total_errors,
            "handled_errors": self._handled_errors,
            "recovery_attempts": self._recovery_attempts,
            "successful_recoveries": self._successful_recoveries,
            "error_types": self._get_error_type_stats(),
            "severity_distribution": self._get_severity_distribution()
        }
    
    # ============================================================================
    # 🕷️ MÉTHODES D'ENREGISTREMENT
    # ============================================================================
    
    def register_error_handler(self, error_type: Type[Exception], handler: Callable):
        """Enregistrer un gestionnaire d'erreur"""
        if error_type not in self._error_handlers:
            self._error_handlers[error_type] = []
        self._error_handlers[error_type].append(handler)
    
    def register_recovery_strategy(self, error_type: ErrorType, strategy: Callable):
        """Enregistrer une stratégie de récupération"""
        if error_type not in self._recovery_strategies:
            self._recovery_strategies[error_type] = []
        self._recovery_strategies[error_type].append(strategy)
    
    # ============================================================================
    # 🕷️ MÉTHODES PRIVÉES
    # ============================================================================
    
    def _create_error_record(self, error: Exception, context: ThreadContext) -> ErrorRecord:
        """Créer un enregistrement d'erreur"""
        import uuid
        
        error_id = str(uuid.uuid4())
        severity = self._determine_severity(error)
        error_type = self._determine_error_type(error)
        
        return ErrorRecord(
            error_id=error_id,
            error=error,
            context=context,
            severity=severity,
            error_type=error_type,
            timestamp=time.time(),
            stack_trace=traceback.format_exc()
        )
    
    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """Déterminer la sévérité d'une erreur"""
        if isinstance(error, (SystemError, OSError, MemoryError)):
            return ErrorSeverity.CRITICAL
        elif isinstance(error, (TimeoutError, asyncio.TimeoutError)):
            return ErrorSeverity.HIGH
        elif isinstance(error, (ValueError, TypeError)):
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _determine_error_type(self, error: Exception) -> ErrorType:
        """Déterminer le type d'une erreur"""
        if isinstance(error, (TimeoutError, asyncio.TimeoutError)):
            return ErrorType.TIMEOUT
        elif isinstance(error, MemoryError):
            return ErrorType.MEMORY
        elif isinstance(error, (ValueError, TypeError)):
            return ErrorType.VALIDATION
        elif isinstance(error, (SystemError, OSError)):
            return ErrorType.SYSTEM
        else:
            return ErrorType.UNKNOWN
    
    async def _apply_error_handlers(self, error_record: ErrorRecord) -> bool:
        """Appliquer les gestionnaires d'erreurs"""
        error_type = type(error_record.error)
        
        if error_type in self._error_handlers:
            for handler in self._error_handlers[error_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        result = await handler(error_record.error, error_record.context)
                    else:
                        result = handler(error_record.error, error_record.context)
                    
                    if result:
                        return True
                        
                except Exception as e:
                    self.logger.error(f"Erreur dans le gestionnaire {handler.__name__}: {e}")
        
        return False
    
    async def _apply_recovery_strategies(self, error_record: ErrorRecord) -> bool:
        """Appliquer les stratégies de récupération"""
        error_type = error_record.error_type
        
        if error_type in self._recovery_strategies:
            for strategy in self._recovery_strategies[error_type]:
                try:
                    if asyncio.iscoroutinefunction(strategy):
                        result = await strategy(error_record)
                    else:
                        result = strategy(error_record)
                    
                    if result:
                        return True
                        
                except Exception as e:
                    self.logger.error(f"Erreur dans la stratégie {strategy.__name__}: {e}")
        
        return False
    
    def _get_error_type_stats(self) -> Dict[str, int]:
        """Obtenir les statistiques par type d'erreur"""
        stats = {}
        for record in self._error_records.values():
            error_type = record.error_type.value
            stats[error_type] = stats.get(error_type, 0) + 1
        return stats
    
    def _get_severity_distribution(self) -> Dict[str, int]:
        """Obtenir la distribution par sévérité"""
        distribution = {}
        for record in self._error_records.values():
            severity = record.severity.value
            distribution[severity] = distribution.get(severity, 0) + 1
        return distribution
    
    # ============================================================================
    # 🕷️ GESTIONNAIRES D'ERREURS PAR DÉFAUT
    # ============================================================================
    
    async def _handle_timeout_error(self, error: Exception, context: ThreadContext) -> bool:
        """Gérer une erreur de timeout"""
        self.logger.warning(f"Timeout détecté pour le thread {context.thread_id}")
        context.state = ThreadState.ERROR
        return True
    
    async def _handle_memory_error(self, error: Exception, context: ThreadContext) -> bool:
        """Gérer une erreur de mémoire"""
        self.logger.error(f"Erreur mémoire pour le thread {context.thread_id}")
        context.state = ThreadState.ERROR
        return True
    
    async def _handle_validation_error(self, error: Exception, context: ThreadContext) -> bool:
        """Gérer une erreur de validation"""
        self.logger.warning(f"Erreur de validation pour le thread {context.thread_id}: {error}")
        return True
    
    async def _handle_system_error(self, error: Exception, context: ThreadContext) -> bool:
        """Gérer une erreur système"""
        self.logger.error(f"Erreur système pour le thread {context.thread_id}: {error}")
        context.state = ThreadState.ERROR
        return True
    
    # ============================================================================
    # 🕷️ STRATÉGIES DE RÉCUPÉRATION PAR DÉFAUT
    # ============================================================================
    
    async def _recover_from_timeout(self, error_record: ErrorRecord) -> bool:
        """Récupérer d'une erreur de timeout"""
        self.logger.info(f"Tentative de récupération du timeout: {error_record.error_id}")
        # Logique de récupération spécifique aux timeouts
        return True
    
    async def _recover_from_memory_error(self, error_record: ErrorRecord) -> bool:
        """Récupérer d'une erreur de mémoire"""
        self.logger.info(f"Tentative de récupération mémoire: {error_record.error_id}")
        # Logique de récupération spécifique à la mémoire
        return True
    
    async def _recover_from_validation_error(self, error_record: ErrorRecord) -> bool:
        """Récupérer d'une erreur de validation"""
        self.logger.info(f"Tentative de récupération validation: {error_record.error_id}")
        # Logique de récupération spécifique aux validations
        return True
    
    async def _recover_from_system_error(self, error_record: ErrorRecord) -> bool:
        """Récupérer d'une erreur système"""
        self.logger.info(f"Tentative de récupération système: {error_record.error_id}")
        # Logique de récupération spécifique aux erreurs système
        return True
    
    # ============================================================================
    # 🕷️ HOOKS PAR DÉFAUT
    # ============================================================================
    
    async def _on_error_occurred(self, error_record: ErrorRecord):
        """Hook appelé quand une erreur survient"""
        self.logger.debug(f"Erreur survenue: {error_record.error_id}")
    
    async def _on_error_handled(self, error_record: ErrorRecord):
        """Hook appelé quand une erreur est gérée"""
        self.logger.debug(f"Erreur gérée: {error_record.error_id}")
    
    async def _on_recovery_attempted(self, error_record: ErrorRecord):
        """Hook appelé quand une récupération est tentée"""
        self.logger.debug(f"Récupération tentée: {error_record.error_id}")
    
    async def _on_recovery_successful(self, error_record: ErrorRecord):
        """Hook appelé quand une récupération réussit"""
        self.logger.debug(f"Récupération réussie: {error_record.error_id}") 