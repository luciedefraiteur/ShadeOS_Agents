"""
Provider de logging pour fichiers.
Gère la rotation des logs et la séparation par type.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler

from .base_logging_provider import BaseLoggingProvider


class FileLoggingProvider(BaseLoggingProvider):
    """Provider de logging pour fichiers avec rotation."""
    
    def __init__(self,
                 log_directory: str = "logs",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 log_format: str = "json",  # "json" ou "text"
                 **kwargs):
        """
        Initialise le provider de logging fichier.
        
        Args:
            log_directory: Répertoire des logs
            max_file_size: Taille max des fichiers en bytes
            backup_count: Nombre de fichiers de backup
            log_format: Format des logs ("json" ou "text")
        """
        super().__init__(**kwargs)
        self.log_directory = Path(log_directory)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.log_format = log_format
        
        # Créer le répertoire de logs
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Configurer les handlers pour différents types de logs
        self._setup_file_handlers()
    
    def _setup_file_handlers(self) -> None:
        """Configure les handlers de fichiers."""
        # Handler principal
        main_handler = RotatingFileHandler(
            self.log_directory / "main.log",
            maxBytes=self.max_file_size,
            backupCount=self.backup_count
        )
        main_handler.setLevel(self.log_level)
        
        # Handler pour les erreurs
        error_handler = RotatingFileHandler(
            self.log_directory / "errors.log",
            maxBytes=self.max_file_size,
            backupCount=self.backup_count
        )
        error_handler.setLevel(logging.ERROR)
        
        # Handler pour les warnings
        warning_handler = RotatingFileHandler(
            self.log_directory / "warnings.log",
            maxBytes=self.max_file_size,
            backupCount=self.backup_count
        )
        warning_handler.setLevel(logging.WARNING)
        
        # Formatters
        if self.log_format == "json":
            formatter = logging.Formatter('%(message)s')  # JSON déjà formaté
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        main_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        warning_handler.setFormatter(formatter)
        
        # Ajouter les handlers
        self.logger.addHandler(main_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(warning_handler)
    
    def _write_to_file(self, filename: str, content: str) -> None:
        """Écrit dans un fichier spécifique."""
        file_path = self.log_directory / filename
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content + '\n')
    
    def log_info(self, message: str, **metadata) -> None:
        """Log un message d'information."""
        if self.log_format == "json":
            log_data = self._create_metadata(level="INFO", message=message, **metadata)
            self.logger.info(json.dumps(log_data))
        else:
            self.logger.info(message)
    
    def log_warning(self, message: str, **metadata) -> None:
        """Log un avertissement."""
        if self.log_format == "json":
            log_data = self._create_metadata(level="WARNING", message=message, **metadata)
            self.logger.warning(json.dumps(log_data))
        else:
            self.logger.warning(message)
    
    def log_error(self, message: str, **metadata) -> None:
        """Log une erreur."""
        if self.log_format == "json":
            log_data = self._create_metadata(level="ERROR", message=message, **metadata)
            self.logger.error(json.dumps(log_data))
        else:
            self.logger.error(message)
    
    def log_debug(self, message: str, **metadata) -> None:
        """Log un message de debug."""
        if self.log_format == "json":
            log_data = self._create_metadata(level="DEBUG", message=message, **metadata)
            self.logger.debug(json.dumps(log_data))
        else:
            self.logger.debug(message)
    
    def log_to_specific_file(self, filename: str, message: str, **metadata) -> None:
        """Log dans un fichier spécifique."""
        if self.log_format == "json":
            log_data = self._create_metadata(message=message, **metadata)
            content = json.dumps(log_data)
        else:
            content = f"{self._get_timestamp()} - {message}"
        
        self._write_to_file(filename, content)
    
    def log_imports_analysis(self, 
                           local_imports: Dict[str, Any],
                           standard_imports: Dict[str, Any],
                           third_party_imports: Dict[str, Any],
                           **metadata) -> None:
        """Log spécialisé pour l'analyse d'imports."""
        # Log des imports locaux
        self.log_to_specific_file(
            "imports_local.log",
            "Local imports analysis",
            imports=local_imports,
            **metadata
        )
        
        # Log des imports standard
        self.log_to_specific_file(
            "imports_standard.log", 
            "Standard library imports analysis",
            imports=standard_imports,
            **metadata
        )
        
        # Log des imports tiers
        self.log_to_specific_file(
            "imports_third_party.log",
            "Third-party imports analysis", 
            imports=third_party_imports,
            **metadata
        )
    
    def get_log_files(self) -> Dict[str, Path]:
        """Retourne la liste des fichiers de logs."""
        return {
            'main': self.log_directory / "main.log",
            'errors': self.log_directory / "errors.log",
            'warnings': self.log_directory / "warnings.log",
            'imports_local': self.log_directory / "imports_local.log",
            'imports_standard': self.log_directory / "imports_standard.log",
            'imports_third_party': self.log_directory / "imports_third_party.log"
        } 