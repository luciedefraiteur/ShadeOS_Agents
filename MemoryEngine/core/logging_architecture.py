#!/usr/bin/env python3
"""
Architecture de Logging pour ShadeOS_Agents
Système de logs multi-niveaux avec séparation machine/humain
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import threading


class ShadeOSLogger:
    """
    Logger principal pour ShadeOS_Agents
    Gère la séparation des logs techniques et conversationnels
    """
    
    def __init__(self, daemon_name: str, base_path: str = "~/shadeos_memory/logs"):
        self.daemon_name = daemon_name
        self.base_path = Path(base_path).expanduser()
        
        # Date actuelle pour organisation
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Créer la structure de dossiers
        self._create_directory_structure()
        
        # Loggers spécialisés
        self.technical_logger = self._setup_technical_logger()
        self.conversation_logger = self._setup_conversation_logger()
        self.metrics_logger = self._setup_metrics_logger()
        
        # Thread lock pour écriture thread-safe
        self.lock = threading.Lock()
        
        # Métriques de logging
        self.log_metrics = {
            "technical_logs": 0,
            "conversation_logs": 0,
            "metrics_logs": 0,
            "errors": 0
        }
    
    def _create_directory_structure(self):
        """Crée la structure de dossiers pour les logs"""
        # Dossier principal pour la date
        date_dir = self.base_path / self.current_date
        
        # Dossiers pour ce daemon
        daemon_dir = date_dir / self.daemon_name
        technical_dir = daemon_dir / "technical"
        conversation_dir = daemon_dir / "conversations"
        metrics_dir = daemon_dir / "metrics"
        
        # Créer tous les dossiers
        for directory in [date_dir, daemon_dir, technical_dir, conversation_dir, metrics_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Créer le lien symbolique "current"
        current_link = self.base_path / "current"
        if current_link.exists():
            current_link.unlink()
        current_link.symlink_to(date_dir)
        
        self.log_paths = {
            "technical": technical_dir,
            "conversation": conversation_dir,
            "metrics": metrics_dir
        }
    
    def _setup_technical_logger(self) -> logging.Logger:
        """Configure le logger technique (pour machines/experts)"""
        logger = logging.getLogger(f"{self.daemon_name}_technical")
        logger.setLevel(logging.DEBUG)
        
        # Handler pour debug complet
        debug_file = self.log_paths["technical"] / "debug.log"
        debug_handler = logging.FileHandler(debug_file, encoding='utf-8')
        debug_handler.setLevel(logging.DEBUG)
        
        # Handler pour erreurs
        error_file = self.log_paths["technical"] / "errors.log"
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        
        # Handler pour performance
        perf_file = self.log_paths["technical"] / "performance.log"
        perf_handler = logging.FileHandler(perf_file, encoding='utf-8')
        perf_handler.setLevel(logging.INFO)
        
        # Format technique détaillé
        technical_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
        )
        
        debug_handler.setFormatter(technical_formatter)
        error_handler.setFormatter(technical_formatter)
        perf_handler.setFormatter(technical_formatter)
        
        logger.addHandler(debug_handler)
        logger.addHandler(error_handler)
        logger.addHandler(perf_handler)
        
        return logger
    
    def _setup_conversation_logger(self) -> logging.Logger:
        """Configure le logger conversationnel (pour humains)"""
        logger = logging.getLogger(f"{self.daemon_name}_conversation")
        logger.setLevel(logging.INFO)
        
        # Handler pour conversations générales
        general_file = self.log_paths["conversation"] / "general.log"
        general_handler = logging.FileHandler(general_file, encoding='utf-8')
        general_handler.setLevel(logging.INFO)
        
        # Format conversationnel lisible
        conversation_formatter = logging.Formatter(
            '%(asctime)s | %(message)s'
        )
        
        general_handler.setFormatter(conversation_formatter)
        logger.addHandler(general_handler)
        
        return logger
    
    def _setup_metrics_logger(self) -> logging.Logger:
        """Configure le logger pour métriques et statistiques"""
        logger = logging.getLogger(f"{self.daemon_name}_metrics")
        logger.setLevel(logging.INFO)
        
        # Handler pour métriques JSON
        metrics_file = self.log_paths["metrics"] / "daily_stats.json"
        
        # Créer le fichier s'il n'existe pas
        if not metrics_file.exists():
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "date": self.current_date,
                    "daemon": self.daemon_name,
                    "metrics": {},
                    "conversations": []
                }, f, indent=2)
        
        return logger
    
    def log_technical(self, level: str, message: str, **kwargs):
        """Log technique pour machines/experts"""
        with self.lock:
            self.log_metrics["technical_logs"] += 1
            
            if level.upper() == "DEBUG":
                self.technical_logger.debug(message)
            elif level.upper() == "INFO":
                self.technical_logger.info(message)
            elif level.upper() == "WARNING":
                self.technical_logger.warning(message)
            elif level.upper() == "ERROR":
                self.technical_logger.error(message)
                self.log_metrics["errors"] += 1
            elif level.upper() == "CRITICAL":
                self.technical_logger.critical(message)
                self.log_metrics["errors"] += 1
    
    def log_conversation(self, sender: str, message: str, direction: str = "incoming", **kwargs):
        """Log conversationnel pour humains"""
        with self.lock:
            self.log_metrics["conversation_logs"] += 1
            
            # Format lisible pour les humains
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if direction == "incoming":
                log_message = f"[{timestamp}] {sender}: {message}"
            else:
                log_message = f"[{timestamp}] {self.daemon_name}: {message}"
            
            self.conversation_logger.info(log_message)
            
            # Sauvegarder dans les métriques
            self._save_conversation_metric(sender, message, direction, timestamp)
    
    def log_metrics(self, metrics_data: Dict[str, Any]):
        """Log des métriques et statistiques"""
        with self.lock:
            self.log_metrics["metrics_logs"] += 1
            
            metrics_file = self.log_paths["metrics"] / "daily_stats.json"
            
            try:
                # Lire les métriques existantes
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Ajouter les nouvelles métriques
                timestamp = datetime.now().isoformat()
                data["metrics"][timestamp] = metrics_data
                
                # Sauvegarder
                with open(metrics_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
            except Exception as e:
                self.technical_logger.error(f"Erreur sauvegarde métriques: {e}")
    
    def _save_conversation_metric(self, sender: str, message: str, direction: str, timestamp: str):
        """Sauvegarde une conversation dans les métriques"""
        metrics_file = self.log_paths["metrics"] / "daily_stats.json"
        
        try:
            # Lire les métriques existantes
            with open(metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Ajouter la conversation
            conversation = {
                "timestamp": timestamp,
                "sender": sender,
                "message": message[:200] + "..." if len(message) > 200 else message,
                "direction": direction,
                "full_length": len(message)
            }
            
            data["conversations"].append(conversation)
            
            # Garder seulement les 1000 dernières conversations
            if len(data["conversations"]) > 1000:
                data["conversations"] = data["conversations"][-1000:]
            
            # Sauvegarder
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.technical_logger.error(f"Erreur sauvegarde conversation: {e}")
    
    def get_log_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des logs"""
        return {
            "daemon": self.daemon_name,
            "date": self.current_date,
            "log_paths": {
                "technical": str(self.log_paths["technical"]),
                "conversation": str(self.log_paths["conversation"]),
                "metrics": str(self.log_paths["metrics"])
            },
            "metrics": self.log_metrics
        }
    
    def cleanup_old_logs(self, days_to_keep: int = 7):
        """Nettoie les anciens logs"""
        try:
            current_time = time.time()
            cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)
            
            for date_dir in self.base_path.iterdir():
                if date_dir.is_dir() and date_dir.name != "current":
                    try:
                        dir_time = date_dir.stat().st_mtime
                        if dir_time < cutoff_time:
                            import shutil
                            shutil.rmtree(date_dir)
                            self.technical_logger.info(f"Ancien dossier supprimé: {date_dir}")
                    except Exception as e:
                        self.technical_logger.error(f"Erreur suppression {date_dir}: {e}")
                        
        except Exception as e:
            self.technical_logger.error(f"Erreur nettoyage logs: {e}")


# Fonction utilitaire pour créer un logger pour un daemon
def create_daemon_logger(daemon_name: str, base_path: str = "~/shadeos_memory/logs") -> ShadeOSLogger:
    """Crée un logger pour un daemon spécifique"""
    return ShadeOSLogger(daemon_name, base_path) 