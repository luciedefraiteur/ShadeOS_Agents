#!/usr/bin/env python3
"""
⛧ Process Manager Tools ⛧
Alma's Process Manager Tools for Assistant V9

Outils ProcessManager pour l'intégration avec Assistant V9.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import sys
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path

# Ajouter le chemin du projet pour les imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Imports ProcessManager
from Core.ProcessManager.execute_command import (
    execute_command, ExecutionMode, ExecutionResult,
    get_active_processes, get_process_status,
    communicate_with_process, terminate_process
)

# Import du gestionnaire d'environnement sécurisé
try:
    from Core.Config.secure_env_manager import get_secure_env_manager, load_project_environment
    SECURE_ENV_AVAILABLE = True
except ImportError:
    SECURE_ENV_AVAILABLE = False
    print("⚠️ SecureEnvManager non disponible - Mode basique activé")

class ProcessManagerTools:
    """
    Outils ProcessManager pour Assistant V9.
    Intégration avec SecureEnvManager pour détection OS/Shell.
    """
    
    def __init__(self):
        """Initialise les outils ProcessManager."""
        self.env_manager = None
        self.env_vars = {}
        
        if SECURE_ENV_AVAILABLE:
            # Charger l'environnement sécurisé
            self.env_vars = load_project_environment()
            self.env_manager = get_secure_env_manager()
            print(f"✅ Environnement chargé: {self.env_manager.os_type}/{self.env_manager.shell_type}")
        else:
            print("⚠️ Mode basique - pas d'adaptation OS/Shell")
    
    def execute_shell_command(self, command: str, mode: str = "blocking", 
                            timeout: Optional[float] = None, 
                            cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Exécute une commande shell avec adaptation OS/Shell.
        
        Args:
            command: Commande à exécuter
            mode: "blocking", "background", "interactive", "monitored"
            timeout: Timeout en secondes
            cwd: Répertoire de travail
        
        Returns:
            Résultat de l'exécution
        """
        try:
            # Adapter la commande selon l'OS/Shell si disponible
            if self.env_manager:
                adapted_command = self._adapt_command_for_environment(command)
                print(f"🔄 Commande adaptée: {adapted_command}")
            else:
                adapted_command = command
            
            # Déterminer le mode d'exécution
            execution_mode = self._get_execution_mode(mode)
            
            # Préparer l'environnement
            env = os.environ.copy()
            if self.env_vars:
                env.update(self.env_vars)
            
            # Exécuter la commande
            result = execute_command(
                command=adapted_command,
                mode=execution_mode,
                cwd=cwd,
                env=env,
                timeout=timeout,
                shell=True
            )
            
            return {
                "success": result.success,
                "command": result.command,
                "return_code": result.return_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": result.execution_time,
                "pid": result.pid,
                "error": result.error
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    def _adapt_command_for_environment(self, command: str) -> str:
        """Adapte une commande selon l'environnement OS/Shell."""
        if not self.env_manager:
            return command
        
        # Informations d'environnement
        os_type = self.env_manager.os_type
        shell_type = self.env_manager.shell_type
        
        # Adaptation basique selon le shell
        if shell_type == "powershell":
            # Échapper les caractères spéciaux pour PowerShell
            command = command.replace('"', '`"')
            command = command.replace("'", "''")
        elif shell_type == "cmd":
            # Échapper pour CMD
            command = command.replace('"', '""')
        elif shell_type in ["zsh", "bash"]:
            # Échapper pour Unix shells
            command = command.replace("'", "'\"'\"'")
        
        return command
    
    def _get_execution_mode(self, mode: str) -> ExecutionMode:
        """Convertit le mode string en ExecutionMode."""
        mode_map = {
            "blocking": ExecutionMode.BLOCKING,
            "background": ExecutionMode.BACKGROUND,
            "interactive": ExecutionMode.INTERACTIVE,
            "monitored": ExecutionMode.MONITORED
        }
        return mode_map.get(mode.lower(), ExecutionMode.BLOCKING)
    
    def get_active_processes_info(self) -> Dict[str, Any]:
        """Retourne les informations sur les processus actifs."""
        try:
            processes = get_active_processes()
            return {
                "success": True,
                "processes": processes,
                "count": len(processes)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_process_info(self, pid: int) -> Dict[str, Any]:
        """Retourne les informations sur un processus spécifique."""
        try:
            status = get_process_status(pid)
            if status:
                return {
                    "success": True,
                    "process_info": status
                }
            else:
                return {
                    "success": False,
                    "error": f"Processus {pid} non trouvé"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def communicate_with_process_tool(self, pid: int, data: str) -> Dict[str, Any]:
        """Communique avec un processus interactif."""
        try:
            result = communicate_with_process(pid, data)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def terminate_process_tool(self, pid: int, force: bool = False) -> Dict[str, Any]:
        """Termine un processus."""
        try:
            result = terminate_process(pid, force)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Retourne les informations d'environnement."""
        if self.env_manager:
            return {
                "success": True,
                "environment": self.env_manager.get_environment_info(),
                "env_vars_count": len(self.env_vars)
            }
        else:
            return {
                "success": False,
                "error": "SecureEnvManager non disponible"
            }

# Instance globale
process_manager_tools = ProcessManagerTools()

def get_process_manager_tools() -> ProcessManagerTools:
    """Retourne l'instance globale des outils ProcessManager."""
    return process_manager_tools

# Fonctions d'interface pour Assistant V9
def execute_shell_command_tool(command: str, mode: str = "blocking", 
                              timeout: Optional[float] = None, 
                              cwd: Optional[str] = None) -> Dict[str, Any]:
    """Interface pour Assistant V9 - Exécution de commande shell."""
    return process_manager_tools.execute_shell_command(command, mode, timeout, cwd)

def get_active_processes_tool() -> Dict[str, Any]:
    """Interface pour Assistant V9 - Liste des processus actifs."""
    return process_manager_tools.get_active_processes_info()

def get_process_info_tool(pid: int) -> Dict[str, Any]:
    """Interface pour Assistant V9 - Informations sur un processus."""
    return process_manager_tools.get_process_info(pid)

def communicate_with_process_tool(pid: int, data: str) -> Dict[str, Any]:
    """Interface pour Assistant V9 - Communication avec un processus."""
    return process_manager_tools.communicate_with_process_tool(pid, data)

def terminate_process_tool(pid: int, force: bool = False) -> Dict[str, Any]:
    """Interface pour Assistant V9 - Terminer un processus."""
    return process_manager_tools.terminate_process_tool(pid, force)

def get_environment_info_tool() -> Dict[str, Any]:
    """Interface pour Assistant V9 - Informations d'environnement."""
    return process_manager_tools.get_environment_info()

if __name__ == "__main__":
    # Test des outils
    print("⛧ Test des outils ProcessManager ⛧")
    
    tools = ProcessManagerTools()
    
    # Test d'exécution de commande
    result = tools.execute_shell_command("echo 'Hello from ProcessManager'")
    print(f"Résultat commande: {result}")
    
    # Test d'informations d'environnement
    env_info = tools.get_environment_info()
    print(f"Informations environnement: {env_info}")
    
    # Test des processus actifs
    processes = tools.get_active_processes_info()
    print(f"Processus actifs: {processes}") 