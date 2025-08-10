"""
Provider de logging pour console.
Affichage coloré et format compact pour le debug.
"""

import json
import logging
from typing import Dict, Any
from colorama import Fore, Back, Style, init

from .base_logging_provider import BaseLoggingProvider

# Initialiser colorama pour les couleurs
init(autoreset=True)


class ConsoleLoggingProvider(BaseLoggingProvider):
    """Provider de logging pour console avec couleurs."""
    
    def __init__(self,
                 use_colors: bool = True,
                 compact_format: bool = False,
                 show_timestamps: bool = True,
                 **kwargs):
        """
        Initialise le provider de logging console.
        
        Args:
            use_colors: Utiliser les couleurs
            compact_format: Format compact
            show_timestamps: Afficher les timestamps
        """
        super().__init__(**kwargs)
        self.use_colors = use_colors
        self.compact_format = compact_format
        self.show_timestamps = show_timestamps
        
        # Configurer le logger console
        self._setup_console_logger()
    
    def _setup_console_logger(self) -> None:
        """Configure le logger pour la console."""
        # Supprimer les handlers existants
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        
        # Formatter personnalisé
        formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def _get_color(self, level: str) -> str:
        """Retourne la couleur pour un niveau de log."""
        if not self.use_colors:
            return ""
        
        colors = {
            'DEBUG': Fore.CYAN,
            'INFO': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Fore.RED + Back.WHITE
        }
        return colors.get(level, "")
    
    def _format_message(self, level: str, message: str, **metadata) -> str:
        """Formate un message pour la console."""
        color = self._get_color(level)
        
        if self.compact_format:
            # Format compact
            if self.show_timestamps:
                timestamp = self._get_timestamp()
                formatted = f"{color}[{level}] {timestamp} - {message}"
            else:
                formatted = f"{color}[{level}] {message}"
        else:
            # Format détaillé
            if self.show_timestamps:
                timestamp = self._get_timestamp()
                formatted = f"{color}[{level}] {timestamp} - {message}"
            else:
                formatted = f"{color}[{level}] {message}"
            
            # Ajouter les métadonnées si présentes
            if metadata:
                metadata_str = json.dumps(metadata, indent=2)
                formatted += f"\n{Fore.BLUE}Metadata: {metadata_str}"
        
        return formatted + Style.RESET_ALL
    
    def log_info(self, message: str, **metadata) -> None:
        """Log un message d'information."""
        formatted_message = self._format_message("INFO", message, **metadata)
        print(formatted_message)
    
    def log_warning(self, message: str, **metadata) -> None:
        """Log un avertissement."""
        formatted_message = self._format_message("WARNING", message, **metadata)
        print(formatted_message)
    
    def log_error(self, message: str, **metadata) -> None:
        """Log une erreur."""
        formatted_message = self._format_message("ERROR", message, **metadata)
        print(formatted_message)
    
    def log_debug(self, message: str, **metadata) -> None:
        """Log un message de debug."""
        formatted_message = self._format_message("DEBUG", message, **metadata)
        print(formatted_message)
    
    def log_success(self, message: str, **metadata) -> None:
        """Log un message de succès."""
        formatted_message = self._format_message("SUCCESS", message, **metadata)
        print(formatted_message)
    
    def log_imports_analysis(self, 
                           local_imports: Dict[str, Any],
                           standard_imports: Dict[str, Any],
                           third_party_imports: Dict[str, Any],
                           **metadata) -> None:
        """Log spécialisé pour l'analyse d'imports."""
        print(f"{Fore.MAGENTA}📊 ANALYSE D'IMPORTS{Style.RESET_ALL}")
        print("=" * 50)
        
        # Imports locaux
        if local_imports:
            print(f"{Fore.GREEN}📁 IMPORTS LOCAUX:{Style.RESET_ALL}")
            for import_name, file_path in local_imports.items():
                print(f"  ✅ {import_name} -> {file_path}")
            print()
        
        # Imports standard
        if standard_imports:
            print(f"{Fore.BLUE}📚 IMPORTS STANDARD:{Style.RESET_ALL}")
            for import_name, file_path in standard_imports.items():
                print(f"  📖 {import_name} -> {file_path}")
            print()
        
        # Imports tiers
        if third_party_imports:
            print(f"{Fore.YELLOW}📦 IMPORTS TIERS:{Style.RESET_ALL}")
            for import_name, file_path in third_party_imports.items():
                print(f"  📦 {import_name} -> {file_path}")
            print()
        
        # Statistiques
        stats = {
            'local_count': len(local_imports),
            'standard_count': len(standard_imports),
            'third_party_count': len(third_party_imports),
            'total_count': len(local_imports) + len(standard_imports) + len(third_party_imports)
        }
        
        print(f"{Fore.CYAN}📈 STATISTIQUES:{Style.RESET_ALL}")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    def log_progress(self, current: int, total: int, message: str = "Progress") -> None:
        """Log une barre de progression."""
        percentage = (current / total) * 100
        bar_length = 30
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        progress_message = f"{message}: [{bar}] {percentage:.1f}% ({current}/{total})"
        print(f"{Fore.BLUE}{progress_message}{Style.RESET_ALL}")
    
    def log_separator(self, title: str = "") -> None:
        """Log un séparateur."""
        if title:
            print(f"{Fore.MAGENTA}{'=' * 20} {title} {'=' * 20}{Style.RESET_ALL}")
        else:
            print(f"{Fore.MAGENTA}{'=' * 50}{Style.RESET_ALL}") 