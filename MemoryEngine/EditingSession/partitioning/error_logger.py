"""
📝 Système de Logging d'Erreurs pour Partitionnement

Gestion centralisée des erreurs et warnings du système de partitionnement.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import logging
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
from dataclasses import dataclass, field
from .partition_schemas import PartitionMethod


@dataclass
class ErrorInfo:
    """Information détaillée sur une erreur."""
    
    error_type: str
    message: str
    file_path: str
    strategy: Optional[PartitionMethod]
    timestamp: datetime
    traceback_info: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    severity: str = "ERROR"  # ERROR, WARNING, INFO
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour logging."""
        return {
            'error_type': self.error_type,
            'message': self.message,
            'file_path': self.file_path,
            'strategy': self.strategy.value if self.strategy else None,
            'timestamp': self.timestamp.isoformat(),
            'traceback': self.traceback_info,
            'context': self.context,
            'severity': self.severity
        }


class PartitioningErrorLogger:
    """Logger spécialisé pour les erreurs de partitionnement."""
    
    def __init__(self, logger_name: str = "partitioning"):
        self.logger = logging.getLogger(logger_name)
        self.error_history: List[ErrorInfo] = []
        self.error_stats = defaultdict(int)
        self.strategy_stats = defaultdict(lambda: defaultdict(int))
        
        # Configuration du logger si pas déjà fait
        if not self.logger.handlers:
            self._setup_logger()
    
    def _setup_logger(self):
        """Configure le logger avec formatage approprié."""
        
        # Handler pour fichier
        file_handler = logging.FileHandler('partitioning_errors.log')
        file_handler.setLevel(logging.DEBUG)
        
        # Handler pour console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Format détaillé
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.DEBUG)
    
    def log_error(self, error_type: str, message: str, file_path: str,
                  strategy: Optional[PartitionMethod] = None,
                  context: Dict[str, Any] = None,
                  exception: Optional[Exception] = None) -> ErrorInfo:
        """Log une erreur avec contexte complet."""
        
        # Création de l'info d'erreur
        error_info = ErrorInfo(
            error_type=error_type,
            message=message,
            file_path=file_path,
            strategy=strategy,
            timestamp=datetime.now(),
            context=context or {},
            severity="ERROR"
        )
        
        # Ajout du traceback si exception fournie
        if exception:
            error_info.traceback_info = traceback.format_exc()
        
        # Stockage dans l'historique
        self.error_history.append(error_info)
        
        # Mise à jour des statistiques
        self.error_stats[error_type] += 1
        if strategy:
            self.strategy_stats[strategy.value][error_type] += 1
        
        # Logging effectif (évite le conflit avec 'message')
        log_data = {
            'error_type': error_info.error_type,
            'error_message': error_info.message,  # Renommé pour éviter conflit
            'file_path': error_info.file_path,
            'strategy': error_info.strategy.value if error_info.strategy else None,
            'timestamp': error_info.timestamp.isoformat(),
            'context': error_info.context,
            'severity': error_info.severity
        }
        self.logger.error(f"Partitioning error: {error_type}", extra=log_data)
        
        return error_info
    
    def log_warning(self, warning_type: str, message: str, file_path: str,
                   strategy: Optional[PartitionMethod] = None,
                   context: Dict[str, Any] = None) -> ErrorInfo:
        """Log un avertissement."""
        
        warning_info = ErrorInfo(
            error_type=warning_type,
            message=message,
            file_path=file_path,
            strategy=strategy,
            timestamp=datetime.now(),
            context=context or {},
            severity="WARNING"
        )
        
        self.error_history.append(warning_info)
        self.error_stats[warning_type] += 1
        
        if strategy:
            self.strategy_stats[strategy.value][warning_type] += 1

        log_data = {
            'error_type': warning_info.error_type,
            'error_message': warning_info.message,
            'file_path': warning_info.file_path,
            'strategy': warning_info.strategy.value if warning_info.strategy else None,
            'timestamp': warning_info.timestamp.isoformat(),
            'context': warning_info.context,
            'severity': warning_info.severity
        }
        self.logger.warning(f"Partitioning warning: {warning_type}", extra=log_data)
        
        return warning_info
    
    def log_info(self, info_type: str, message: str, file_path: str,
                strategy: Optional[PartitionMethod] = None,
                context: Dict[str, Any] = None) -> ErrorInfo:
        """Log une information."""
        
        info = ErrorInfo(
            error_type=info_type,
            message=message,
            file_path=file_path,
            strategy=strategy,
            timestamp=datetime.now(),
            context=context or {},
            severity="INFO"
        )
        
        self.error_history.append(info)

        log_data = {
            'error_type': info.error_type,
            'error_message': info.message,
            'file_path': info.file_path,
            'strategy': info.strategy.value if info.strategy else None,
            'timestamp': info.timestamp.isoformat(),
            'context': info.context,
            'severity': info.severity
        }
        self.logger.info(f"Partitioning info: {info_type}", extra=log_data)
        
        return info
    
    def log_strategy_fallback(self, failed_strategy: PartitionMethod,
                             fallback_strategy: PartitionMethod,
                             file_path: str, reason: str):
        """Log un fallback de stratégie."""
        
        context = {
            'failed_strategy': failed_strategy.value,
            'fallback_strategy': fallback_strategy.value,
            'reason': reason
        }
        
        self.log_warning(
            "strategy_fallback",
            f"Fallback from {failed_strategy.value} to {fallback_strategy.value}: {reason}",
            file_path,
            failed_strategy,
            context
        )
    
    def log_performance_issue(self, file_path: str, processing_time: float,
                             strategy: PartitionMethod, file_size: int):
        """Log un problème de performance."""
        
        context = {
            'processing_time': processing_time,
            'file_size': file_size,
            'strategy': strategy.value
        }
        
        if processing_time > 10.0:  # Plus de 10 secondes
            self.log_warning(
                "performance_slow",
                f"Slow partitioning: {processing_time:.2f}s for {file_size} chars",
                file_path,
                strategy,
                context
            )
        elif processing_time > 30.0:  # Plus de 30 secondes
            self.log_error(
                "performance_critical",
                f"Critical slow partitioning: {processing_time:.2f}s for {file_size} chars",
                file_path,
                strategy,
                context
            )
    
    def get_error_report(self, last_hours: int = 24) -> Dict[str, Any]:
        """Génère un rapport d'erreurs."""
        
        # Filtrage par période
        cutoff_time = datetime.now().timestamp() - (last_hours * 3600)
        recent_errors = [
            error for error in self.error_history
            if error.timestamp.timestamp() > cutoff_time
        ]
        
        # Statistiques par type
        error_types = defaultdict(int)
        severity_counts = defaultdict(int)
        strategy_issues = defaultdict(int)
        
        for error in recent_errors:
            error_types[error.error_type] += 1
            severity_counts[error.severity] += 1
            if error.strategy:
                strategy_issues[error.strategy.value] += 1
        
        # Fichiers les plus problématiques
        file_issues = defaultdict(int)
        for error in recent_errors:
            file_issues[error.file_path] += 1
        
        most_problematic = sorted(
            file_issues.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'period_hours': last_hours,
            'total_errors': len(recent_errors),
            'error_types': dict(error_types),
            'severity_distribution': dict(severity_counts),
            'strategy_issues': dict(strategy_issues),
            'most_problematic_files': most_problematic,
            'recent_errors': [error.to_dict() for error in recent_errors[-10:]]
        }
    
    def get_strategy_success_rates(self) -> Dict[str, Dict[str, float]]:
        """Calcule les taux de succès par stratégie."""
        
        strategy_totals = defaultdict(int)
        strategy_errors = defaultdict(int)
        
        for error in self.error_history:
            if error.strategy and error.severity == "ERROR":
                strategy_totals[error.strategy.value] += 1
                strategy_errors[error.strategy.value] += 1
            elif error.strategy:
                strategy_totals[error.strategy.value] += 1
        
        success_rates = {}
        for strategy, total in strategy_totals.items():
            errors = strategy_errors[strategy]
            success_rate = ((total - errors) / total) * 100 if total > 0 else 0
            success_rates[strategy] = {
                'total_attempts': total,
                'errors': errors,
                'success_rate': success_rate
            }
        
        return success_rates
    
    def clear_old_errors(self, days: int = 30):
        """Nettoie les erreurs anciennes."""
        
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        
        self.error_history = [
            error for error in self.error_history
            if error.timestamp.timestamp() > cutoff_time
        ]
        
        self.log_info(
            "cleanup",
            f"Cleared errors older than {days} days",
            "system"
        )
    
    def export_errors_to_file(self, file_path: str, format: str = "json"):
        """Exporte les erreurs vers un fichier."""
        
        import json
        
        if format == "json":
            data = {
                'export_timestamp': datetime.now().isoformat(),
                'total_errors': len(self.error_history),
                'errors': [error.to_dict() for error in self.error_history]
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        
        elif format == "csv":
            import csv
            
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'severity', 'error_type', 'message',
                    'file_path', 'strategy'
                ])
                
                for error in self.error_history:
                    writer.writerow([
                        error.timestamp.isoformat(),
                        error.severity,
                        error.error_type,
                        error.message,
                        error.file_path,
                        error.strategy.value if error.strategy else ''
                    ])
        
        self.log_info(
            "export",
            f"Exported {len(self.error_history)} errors to {file_path}",
            "system"
        )


# Instance globale pour usage simple
global_error_logger = PartitioningErrorLogger()


def log_partitioning_error(error_type: str, message: str, file_path: str,
                          strategy: Optional[PartitionMethod] = None,
                          context: Dict[str, Any] = None,
                          exception: Optional[Exception] = None) -> ErrorInfo:
    """Fonction utilitaire pour logger une erreur."""
    return global_error_logger.log_error(
        error_type, message, file_path, strategy, context, exception
    )


def log_partitioning_warning(warning_type: str, message: str, file_path: str,
                            strategy: Optional[PartitionMethod] = None,
                            context: Dict[str, Any] = None) -> ErrorInfo:
    """Fonction utilitaire pour logger un avertissement."""
    return global_error_logger.log_warning(
        warning_type, message, file_path, strategy, context
    )
