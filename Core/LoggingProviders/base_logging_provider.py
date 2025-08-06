"""
Provider de base pour tous les systèmes de logging.
Fournit une interface commune et des fonctionnalités de base.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class BaseLoggingProvider(ABC):
    """Provider de base pour tous les systèmes de logging."""
    
    def __init__(self, 
                 log_level: str = "INFO",
                 timestamp_format: str = "%Y-%m-%d %H:%M:%S",
                 include_metadata: bool = True):
        """
        Initialise le provider de logging.
        
        Args:
            log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR)
            timestamp_format: Format des timestamps
            include_metadata: Inclure les métadonnées dans les logs
        """
        self.log_level = getattr(logging, log_level.upper())
        self.timestamp_format = timestamp_format
        self.include_metadata = include_metadata
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Configure le logger de base."""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(self.log_level)
        
        # Éviter les handlers multiples
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _get_timestamp(self) -> str:
        """Génère un timestamp formaté."""
        return datetime.now().strftime(self.timestamp_format)
    
    def _create_metadata(self, **kwargs) -> Dict[str, Any]:
        """Crée des métadonnées pour les logs."""
        metadata = {
            'timestamp': self._get_timestamp(),
            'provider': self.__class__.__name__,
            'log_level': logging.getLevelName(self.log_level)
        }
        
        if self.include_metadata:
            metadata.update(kwargs)
        
        return metadata
    
    @abstractmethod
    def log_info(self, message: str, **metadata) -> None:
        """Log un message d'information."""
        pass
    
    @abstractmethod
    def log_warning(self, message: str, **metadata) -> None:
        """Log un avertissement."""
        pass
    
    @abstractmethod
    def log_error(self, message: str, **metadata) -> None:
        """Log une erreur."""
        pass
    
    @abstractmethod
    def log_debug(self, message: str, **metadata) -> None:
        """Log un message de debug."""
        pass
    
    def log_with_level(self, level: str, message: str, **metadata) -> None:
        """Log avec un niveau spécifique."""
        log_method = getattr(self, f'log_{level.lower()}', self.log_info)
        log_method(message, **metadata)
    
    def log_structured(self, data: Dict[str, Any], **metadata) -> None:
        """Log des données structurées."""
        combined_data = self._create_metadata(**metadata)
        combined_data.update(data)
        self.log_info(json.dumps(combined_data, indent=2))
    
    def log_statistics(self, stats: Dict[str, Any], **metadata) -> None:
        """Log des statistiques."""
        stats_data = {
            'type': 'statistics',
            'data': stats
        }
        self.log_structured(stats_data, **metadata)
    
    def log_performance(self, operation: str, duration: float, **metadata) -> None:
        """Log des métriques de performance."""
        perf_data = {
            'type': 'performance',
            'operation': operation,
            'duration_seconds': duration
        }
        self.log_structured(perf_data, **metadata) 