#!/usr/bin/env python3
"""
⛧ Secure Environment Manager ⛧
Alma's Cross-Platform Environment Management

Gestionnaire sécurisé de variables d'environnement avec détection OS/Shell.
Intégration avec ProcessManager pour Assistant V9.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
import json
import logging

class SecureEnvManager:
    """
    Gestionnaire sécurisé de variables d'environnement.
    Détection automatique OS/Shell et chargement sécurisé.
    """
    
    def __init__(self):
        """Initialise le gestionnaire d'environnement."""
        self.os_type = self._detect_os()
        self.shell_type = self._detect_shell()
        self.env_file_path = self._get_env_file_path()
        self.logger = logging.getLogger(__name__)
        
    def _detect_os(self) -> str:
        """Détecte le système d'exploitation."""
        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "windows":
            return "windows"
        elif system == "darwin":
            return "macos"
        else:
            return "unknown"
    
    def _detect_shell(self) -> str:
        """Détecte le shell actuel."""
        try:
            # Vérifier les variables d'environnement
            shell = os.environ.get('SHELL', '').lower()
            if 'zsh' in shell:
                return 'zsh'
            elif 'bash' in shell:
                return 'bash'
            elif 'fish' in shell:
                return 'fish'
            elif 'powershell' in shell:
                return 'powershell'
            elif 'cmd' in shell:
                return 'cmd'
            
            # Détection par OS
            if self.os_type == "windows":
                return "powershell"  # Default pour Windows
            else:
                return "bash"  # Default pour Unix
            
        except Exception as e:
            self.logger.warning(f"Erreur détection shell: {e}")
            return "unknown"
    
    def _get_env_file_path(self) -> Path:
        """Retourne le chemin du fichier d'environnement sécurisé."""
        if self.os_type == "windows":
            home = Path(os.environ.get('USERPROFILE', '~'))
        else:
            home = Path.home()
        
        return home / ".shadeos_env"
    
    def create_env_file(self, force: bool = False) -> bool:
        """Crée le fichier d'environnement sécurisé."""
        try:
            if self.env_file_path.exists() and not force:
                self.logger.info(f"Fichier d'environnement existe déjà: {self.env_file_path}")
                return True
            
            # Créer le contenu par défaut
            default_content = self._get_default_env_content()
            
            # Écrire le fichier
            with open(self.env_file_path, 'w') as f:
                f.write(default_content)
            
            # Définir les permissions sécurisées
            if self.os_type != "windows":
                os.chmod(self.env_file_path, 0o600)  # User read/write only
            
            self.logger.info(f"Fichier d'environnement créé: {self.env_file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur création fichier d'environnement: {e}")
            return False
    
    def _get_default_env_content(self) -> str:
        """Retourne le contenu par défaut du fichier d'environnement."""
        return f"""# ⛧ ShadeOS Environment Configuration ⛧
# Fichier de configuration sécurisé pour ShadeOS_Agents
# Créé automatiquement par Alma, Architecte Démoniaque

# Configuration Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=ShadeOS_Agents_2025

# Configuration OpenAI (optionnel)
# OPENAI_API_KEY=your_openai_api_key_here

# Configuration Gemini (optionnel)
# GEMINI_API_KEY=your_gemini_primary_key
# GEMINI_LURK=your_gemini_secondary_key
# GEMINI_API_KEYS=["primary_key","secondary_key"]
# Ou sous forme objet JSON:
# GEMINI_API_KEYS={"primary":"key1","secondary":"key2","fallback":["k3","k4"]}

# Configuration Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b-instruct

# Configuration du projet
SHADEOS_PROJECT_ROOT={Path.cwd()}
SHADEOS_OS_TYPE={self.os_type}
SHADEOS_SHELL_TYPE={self.shell_type}

# Variables d'environnement système
PATH={os.environ.get('PATH', '')}
"""
    
    def load_env_variables(self) -> Dict[str, str]:
        """Charge les variables d'environnement depuis le fichier sécurisé."""
        env_vars = {}
        
        try:
            if not self.env_file_path.exists():
                self.logger.warning(f"Fichier d'environnement non trouvé: {self.env_file_path}")
                return env_vars
            
            with open(self.env_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()

            # Post-traitement: support de clés Gemini multiples via JSON
            self._augment_gemini_keys(env_vars)
            
            self.logger.info(f"Variables d'environnement chargées: {len(env_vars)} variables")
            return env_vars
            
        except Exception as e:
            self.logger.error(f"Erreur chargement variables d'environnement: {e}")
            return env_vars

    def _augment_gemini_keys(self, env_vars: Dict[str, str]) -> None:
        """Normalise et enrichit la configuration Gemini.

        - Accepte GEMINI_API_KEYS en JSON (liste ou objet)
        - Combine GEMINI_API_KEY (primaire) et GEMINI_LURK (secondaire)
        - Expose GEMINI_API_KEY_{i} indexées et garantit GEMINI_API_KEY
        """
        try:
            # Récupérer sources de clés
            primary = env_vars.get('GEMINI_API_KEY')
            # Supporte alias historiques
            secondary = env_vars.get('GEMINI_LURK') or env_vars.get('GEMINI_API_KEY_LURK')
            keys_from_json: list[str] = []

            raw_json = env_vars.get('GEMINI_API_KEYS')
            if raw_json:
                raw = raw_json.strip()
                # Autoriser quotes externes
                if (raw.startswith("'") and raw.endswith("'")) or (raw.startswith('"') and raw.endswith('"')):
                    raw = raw[1:-1]
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        keys_from_json = [str(k) for k in parsed if k]
                    elif isinstance(parsed, dict):
                        # Objet avec primary/secondary/fallback
                        if parsed.get('primary'):
                            keys_from_json.append(str(parsed['primary']))
                        if parsed.get('secondary'):
                            keys_from_json.append(str(parsed['secondary']))
                        fallback = parsed.get('fallback') or parsed.get('others') or []
                        if isinstance(fallback, list):
                            keys_from_json.extend([str(k) for k in fallback if k])
                except Exception as e:  # JSON invalide -> ignorer silencieusement
                    self.logger.warning(f"GEMINI_API_KEYS JSON invalide: {e}")

            # Construire la liste consolidée en préservant l'ordre et sans doublons
            ordered: list[str] = []
            def add_key(k: Optional[str]):
                if k and k not in ordered:
                    ordered.append(k)
            add_key(primary)
            for k in keys_from_json:
                add_key(k)
            add_key(secondary)

            if ordered:
                # Normaliser env_vars
                env_vars['GEMINI_API_KEYS'] = json.dumps(ordered)
                # Définir GEMINI_API_KEY si absent
                if not primary:
                    env_vars['GEMINI_API_KEY'] = ordered[0]
                # Exposer des variables indexées
                for i, k in enumerate(ordered):
                    env_vars[f'GEMINI_API_KEY_{i}'] = k
        except Exception as e:
            self.logger.warning(f"Erreur d'augmentation des clés Gemini: {e}")
    
    def get_shell_command(self, command: str) -> str:
        """Adapte une commande selon le shell détecté."""
        if self.shell_type == "powershell":
            return f"powershell -Command \"{command}\""
        elif self.shell_type == "cmd":
            return f"cmd /c \"{command}\""
        elif self.shell_type == "zsh":
            return f"zsh -c '{command}'"
        elif self.shell_type == "bash":
            return f"bash -c '{command}'"
        else:
            return command  # Fallback
    
    def get_environment_info(self) -> Dict[str, str]:
        """Retourne les informations d'environnement."""
        return {
            "os_type": self.os_type,
            "shell_type": self.shell_type,
            "env_file_path": str(self.env_file_path),
            "env_file_exists": str(self.env_file_path.exists()),
            "python_version": sys.version,
            "platform": platform.platform()
        }
    
    def validate_neo4j_config(self) -> bool:
        """Valide la configuration Neo4j."""
        env_vars = self.load_env_variables()
        
        required_vars = ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD']
        for var in required_vars:
            if var not in env_vars or not env_vars[var]:
                self.logger.error(f"Variable Neo4j manquante: {var}")
                return False
        
        self.logger.info("Configuration Neo4j validée")
        return True

# Instance globale
secure_env_manager = SecureEnvManager()

def get_secure_env_manager() -> SecureEnvManager:
    """Retourne l'instance globale du gestionnaire d'environnement."""
    return secure_env_manager

def load_project_environment() -> Dict[str, str]:
    """Charge l'environnement du projet avec les variables sécurisées."""
    manager = get_secure_env_manager()
    
    # Créer le fichier si nécessaire
    if not manager.env_file_path.exists():
        manager.create_env_file()
    
    # Charger les variables
    env_vars = manager.load_env_variables()
    
    # Appliquer aux variables d'environnement système
    for key, value in env_vars.items():
        os.environ[key] = value
    
    return env_vars

if __name__ == "__main__":
    # Test du gestionnaire
    manager = SecureEnvManager()
    print(f"OS détecté: {manager.os_type}")
    print(f"Shell détecté: {manager.shell_type}")
    print(f"Fichier d'environnement: {manager.env_file_path}")
    
    # Créer le fichier d'environnement
    if manager.create_env_file():
        print("✅ Fichier d'environnement créé avec succès")
        
        # Charger les variables
        env_vars = manager.load_env_variables()
        print(f"Variables chargées: {len(env_vars)}")
        
        # Valider Neo4j
        if manager.validate_neo4j_config():
            print("✅ Configuration Neo4j validée")
        else:
            print("❌ Configuration Neo4j invalide")
    else:
        print("❌ Erreur création fichier d'environnement") 