"""
Provider de logging spécialisé pour l'analyse d'imports.
Fournit des méthodes spécifiques pour l'analyse récursive des dépendances.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Set, Optional

from .base_logging_provider import BaseLoggingProvider


class ImportAnalyzerLoggingProvider(BaseLoggingProvider):
    """Provider de logging spécialisé pour l'analyse d'imports."""
    
    def __init__(self,
                 analysis_session_id: Optional[str] = None,
                 log_resolution_details: bool = True,
                 log_performance_metrics: bool = True,
                 log_directory: Optional[str] = None,
                 log_format: str = "json",
                 **kwargs):
        """
        Initialise le provider de logging spécialisé.
        
        Args:
            analysis_session_id: ID de session d'analyse
            log_resolution_details: Loguer les détails de résolution
            log_performance_metrics: Loguer les métriques de performance
            log_directory: Répertoire pour les logs (si fourni, utilise FileLoggingProvider)
            log_format: Format des logs ("json" ou "text")
        """
        # Si log_directory est fourni, configurer le logging fichier
        if log_directory:
            from .file_logging_provider import FileLoggingProvider
            # Créer un FileLoggingProvider temporaire pour copier sa configuration
            temp_file_provider = FileLoggingProvider(
                log_directory=log_directory,
                log_format=log_format,
                **kwargs
            )
            # Copier la configuration du logger
            super().__init__(**kwargs)
            self.logger.handlers = temp_file_provider.logger.handlers
            self.logger.setLevel(temp_file_provider.logger.level)
            # Copier aussi les attributs du FileLoggingProvider
            self.log_directory = temp_file_provider.log_directory
            self.log_format = temp_file_provider.log_format
        else:
            super().__init__(**kwargs)
            
        self.analysis_session_id = analysis_session_id or f"analysis_{int(time.time())}"
        self.log_resolution_details = log_resolution_details
        self.log_performance_metrics = log_performance_metrics
        
        # Statistiques d'analyse
        self.stats = {
            'files_analyzed': 0,
            'imports_resolved': 0,
            'resolution_time': 0.0,
            'start_time': time.time()
        }
    
    def _get_timestamp(self) -> str:
        """Retourne un timestamp formaté."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def log_info(self, message: str, **metadata) -> None:
        """Log un message d'information."""
        info_data = {
            'type': 'info',
            'message': message,
            'session_id': self.analysis_session_id
        }
        info_data.update(metadata)
        # Utiliser la méthode du parent pour éviter la récursion
        super().log_info(json.dumps(info_data, indent=2))
    
    def log_warning(self, message: str, **metadata) -> None:
        """Log un avertissement."""
        warning_data = {
            'type': 'warning',
            'message': message,
            'session_id': self.analysis_session_id
        }
        warning_data.update(metadata)
        # Utiliser la méthode du parent pour éviter la récursion
        super().log_warning(json.dumps(warning_data, indent=2))
    
    def log_debug(self, message: str, **metadata) -> None:
        """Log un message de debug."""
        debug_data = {
            'type': 'debug',
            'message': message,
            'session_id': self.analysis_session_id
        }
        debug_data.update(metadata)
        # Utiliser la méthode du parent pour éviter la récursion
        super().log_debug(json.dumps(debug_data, indent=2))
    
    def log_analysis_start(self, start_files: List[str], **metadata) -> None:
        """Log le début d'une analyse."""
        analysis_data = {
            'type': 'analysis_start',
            'session_id': self.analysis_session_id,
            'start_files': start_files,
            'start_time': self._get_timestamp(),
            'total_start_files': len(start_files)
        }
        analysis_data.update(metadata)
        
        self.log_info(json.dumps(analysis_data, indent=2))
        self.log_info(f"🚀 Début analyse session {self.analysis_session_id}")
        self.log_info(f"📁 Fichiers de départ: {len(start_files)}")
    
    def log_file_analysis_start(self, file_path: str, depth: int = 0, **metadata) -> None:
        """Log le début de l'analyse d'un fichier."""
        file_data = {
            'type': 'file_analysis_start',
            'file_path': file_path,
            'depth': depth,
            'session_id': self.analysis_session_id
        }
        file_data.update(metadata)
        
        self.log_info(json.dumps(file_data, indent=2))
        indent = '  ' * depth
        self.log_info(f"{indent}📁 Analyse: {file_path}")
    
    def log_import_resolution(self, 
                            import_name: str, 
                            current_file: str,
                            resolved_path: Optional[str],
                            resolution_time: float,
                            **metadata) -> None:
        """Log la résolution d'un import."""
        resolution_data = {
            'type': 'import_resolution',
            'import_name': import_name,
            'current_file': current_file,
            'resolved_path': resolved_path,
            'resolution_time': resolution_time,
            'session_id': self.analysis_session_id,
            'success': resolved_path is not None
        }
        resolution_data.update(metadata)
        
        self.log_info(json.dumps(resolution_data, indent=2))
        
        if self.log_resolution_details:
            if resolved_path:
                self.log_info(f"  ✅ {import_name} -> {resolved_path}")
            else:
                self.log_warning(f"  ❌ {import_name} -> Non résolu")
    
    def log_imports_summary(self, 
                           file_path: str,
                           local_imports: List[str],
                           standard_imports: List[str],
                           third_party_imports: List[str],
                           **metadata) -> None:
        """Log un résumé des imports d'un fichier."""
        summary_data = {
            'type': 'imports_summary',
            'file_path': file_path,
            'local_imports': local_imports,
            'standard_imports': standard_imports,
            'third_party_imports': third_party_imports,
            'session_id': self.analysis_session_id,
            'total_imports': len(local_imports) + len(standard_imports) + len(third_party_imports)
        }
        summary_data.update(metadata)
        
        self.log_info(json.dumps(summary_data, indent=2))
        self.log_info(f"📊 Résumé {file_path}: {len(local_imports)} locaux, {len(standard_imports)} standard, {len(third_party_imports)} tiers")
    
    def log_file_analysis_complete(self, 
                                 file_path: str,
                                 resolved_count: int,
                                 total_imports: int,
                                 **metadata) -> None:
        """Log la fin de l'analyse d'un fichier."""
        complete_data = {
            'type': 'file_analysis_complete',
            'file_path': file_path,
            'resolved_count': resolved_count,
            'total_imports': total_imports,
            'session_id': self.analysis_session_id,
            'resolution_rate': resolved_count / total_imports if total_imports > 0 else 0.0
        }
        complete_data.update(metadata)
        
        self.log_info(json.dumps(complete_data, indent=2))
        self.log_info(f"  📦 {file_path}: {resolved_count}/{total_imports} résolus")
    
    def log_recursive_analysis_complete(self, 
                                      all_dependencies: Set[str],
                                      unused_files: Set[str],
                                      **metadata) -> None:
        """Log la fin de l'analyse récursive."""
        complete_data = {
            'type': 'recursive_analysis_complete',
            'all_dependencies': list(all_dependencies),
            'unused_files': list(unused_files),
            'session_id': self.analysis_session_id,
            'total_dependencies': len(all_dependencies),
            'total_unused': len(unused_files)
        }
        complete_data.update(metadata)
        
        self.log_info(json.dumps(complete_data, indent=2))
        self.log_info(f"🎯 Analyse terminée: {len(all_dependencies)} dépendances, {len(unused_files)} non utilisés")
    
    def log_performance_metrics(self) -> None:
        """Log les métriques de performance."""
        total_time = time.time() - self.stats['start_time']
        
        metrics_data = {
            'type': 'performance_metrics',
            'session_id': self.analysis_session_id,
            'total_time': total_time,
            'files_per_second': self.stats['files_analyzed'] / total_time if total_time > 0 else 0,
            'imports_per_second': self.stats['imports_resolved'] / total_time if total_time > 0 else 0,
            'average_resolution_time': self.stats['resolution_time'] / self.stats['imports_resolved'] if self.stats['imports_resolved'] > 0 else 0,
            'stats': self.stats
        }
        
        self.log_structured(metrics_data)
    
    def log_error(self, message: str, **metadata) -> None:
        """Log une erreur avec contexte d'analyse."""
        # self.stats['imports_failed'] += 1 # This line was removed as per the new_code
        
        error_data = {
            'type': 'analysis_error',
            'message': message,
            'session_id': self.analysis_session_id
        }
        error_data.update(metadata)
        
        self.log_structured(error_data)
        super().log_error(message, **metadata)
    
    def get_analysis_report(self) -> Dict[str, Any]:
        """Retourne un rapport complet de l'analyse."""
        total_time = time.time() - self.stats['start_time']
        
        return {
            'session_id': self.analysis_session_id,
            'total_time': total_time,
            'stats': {
                'files_analyzed': self.stats['files_analyzed'],
                'imports_resolved': self.stats['imports_resolved'],
                'resolution_time': self.stats['resolution_time']
            }
        } 