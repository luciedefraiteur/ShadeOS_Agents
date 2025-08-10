#!/usr/bin/env python3
"""
⛧ Execute Command ⛧
Alma's Meta-Tool for Command Execution

Meta-outil d'exécution de commandes avec gestion avancée des processus.
Intégration avec SecureEnvManager pour détection OS/Shell.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import sys
import subprocess
import psutil
import time
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum

# Import des autres composants ProcessManager
from .process_reader import read_from_process
from .process_writer import write_to_process, send_signal_to_process
from .process_killer import kill_process

# Import du gestionnaire d'environnement sécurisé
try:
    from Core.Config.secure_env_manager import get_secure_env_manager
    SECURE_ENV_AVAILABLE = True
except ImportError:
    SECURE_ENV_AVAILABLE = False
    print("⚠️ SecureEnvManager non disponible - Mode basique activé")


class ExecutionMode(Enum):
    """Modes d'exécution des commandes."""
    BLOCKING = "blocking"           # Bloquant, attend la fin
    BACKGROUND = "background"       # Arrière-plan, retourne immédiatement
    INTERACTIVE = "interactive"     # Interactif avec communication
    MONITORED = "monitored"         # Surveillé avec callbacks


@dataclass
class ExecutionResult:
    """Résultat d'exécution d'une commande."""
    success: bool
    command: str
    pid: Optional[int]
    return_code: Optional[int]
    stdout: str
    stderr: str
    execution_time: float
    mode: ExecutionMode
    error: Optional[str] = None


class CommandExecutor:
    """Exécuteur de commandes avec gestion avancée."""
    
    def __init__(self):
        """Initialise l'exécuteur."""
        self.active_processes = {}  # pid -> process_info
        self.process_callbacks = {}  # pid -> callbacks
    
    def execute_command(
        self,
        command: str,
        mode: ExecutionMode = ExecutionMode.BLOCKING,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        input_data: Optional[str] = None,
        capture_output: bool = True,
        shell: bool = True,
        on_output: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        on_complete: Optional[Callable[[ExecutionResult], None]] = None
    ) -> ExecutionResult:
        """
        Exécute une commande selon le mode spécifié avec détection OS/Shell.
        
        Args:
            command: Commande à exécuter
            mode: Mode d'exécution
            cwd: Répertoire de travail
            env: Variables d'environnement
            timeout: Timeout en secondes
            input_data: Données à envoyer en entrée
            capture_output: Capturer stdout/stderr
            shell: Utiliser le shell
            on_output: Callback pour stdout
            on_error: Callback pour stderr
            on_complete: Callback de fin d'exécution
        
        Returns:
            Résultat d'exécution
        """
        # Charger l'environnement sécurisé si disponible
        if SECURE_ENV_AVAILABLE:
            try:
                env_manager = get_secure_env_manager()
                secure_env = env_manager.load_env_variables()
                
                # Fusionner avec l'environnement fourni
                if env is None:
                    env = {}
                env.update(secure_env)
                
                # Adapter la commande selon le shell détecté
                if shell:
                    command = env_manager.get_shell_command(command)
                    
            except Exception as e:
                print(f"⚠️ Erreur chargement environnement sécurisé: {e}")
        
        start_time = time.time()
        """
        Exécute une commande selon le mode spécifié.
        
        Args:
            command: Commande à exécuter
            mode: Mode d'exécution
            cwd: Répertoire de travail
            env: Variables d'environnement
            timeout: Timeout en secondes
            input_data: Données à envoyer en entrée
            capture_output: Capturer stdout/stderr
            shell: Utiliser le shell
            on_output: Callback pour stdout
            on_error: Callback pour stderr
            on_complete: Callback de fin d'exécution
        
        Returns:
            Résultat d'exécution
        """
        start_time = time.time()
        
        try:
            if mode == ExecutionMode.BLOCKING:
                return self._execute_blocking(
                    command, cwd, env, timeout, input_data, capture_output, shell
                )
            elif mode == ExecutionMode.BACKGROUND:
                return self._execute_background(
                    command, cwd, env, capture_output, shell
                )
            elif mode == ExecutionMode.INTERACTIVE:
                return self._execute_interactive(
                    command, cwd, env, on_output, on_error, shell
                )
            elif mode == ExecutionMode.MONITORED:
                return self._execute_monitored(
                    command, cwd, env, timeout, on_output, on_error, on_complete, shell
                )
            else:
                raise ValueError(f"Mode d'exécution non supporté: {mode}")
                
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                command=command,
                pid=None,
                return_code=None,
                stdout="",
                stderr="",
                execution_time=execution_time,
                mode=mode,
                error=str(e)
            )
    
    def _execute_blocking(
        self,
        command: str,
        cwd: Optional[str],
        env: Optional[Dict[str, str]],
        timeout: Optional[float],
        input_data: Optional[str],
        capture_output: bool,
        shell: bool
    ) -> ExecutionResult:
        """Exécution bloquante."""
        start_time = time.time()
        
        try:
            # Configuration du processus
            kwargs = {
                'shell': shell,
                'cwd': cwd,
                'env': env,
                'text': True
            }
            
            if capture_output:
                kwargs.update({
                    'stdout': subprocess.PIPE,
                    'stderr': subprocess.PIPE
                })
            
            if input_data:
                kwargs['stdin'] = subprocess.PIPE
            
            # Exécution
            process = subprocess.Popen(command, **kwargs)
            
            # Enregistrement du processus actif
            self.active_processes[process.pid] = {
                'process': process,
                'command': command,
                'start_time': start_time,
                'mode': ExecutionMode.BLOCKING
            }
            
            try:
                stdout, stderr = process.communicate(input=input_data, timeout=timeout)
                return_code = process.returncode
                
                execution_time = time.time() - start_time
                
                return ExecutionResult(
                    success=return_code == 0,
                    command=command,
                    pid=process.pid,
                    return_code=return_code,
                    stdout=stdout or "",
                    stderr=stderr or "",
                    execution_time=execution_time,
                    mode=ExecutionMode.BLOCKING
                )
                
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                execution_time = time.time() - start_time
                
                return ExecutionResult(
                    success=False,
                    command=command,
                    pid=process.pid,
                    return_code=None,
                    stdout=stdout or "",
                    stderr=stderr or "",
                    execution_time=execution_time,
                    mode=ExecutionMode.BLOCKING,
                    error=f"Timeout après {timeout}s"
                )
            
            finally:
                # Nettoyage
                if process.pid in self.active_processes:
                    del self.active_processes[process.pid]
                
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                command=command,
                pid=None,
                return_code=None,
                stdout="",
                stderr="",
                execution_time=execution_time,
                mode=ExecutionMode.BLOCKING,
                error=str(e)
            )
    
    def _execute_background(
        self,
        command: str,
        cwd: Optional[str],
        env: Optional[Dict[str, str]],
        capture_output: bool,
        shell: bool
    ) -> ExecutionResult:
        """Exécution en arrière-plan."""
        start_time = time.time()
        
        try:
            # Configuration du processus
            kwargs = {
                'shell': shell,
                'cwd': cwd,
                'env': env,
                'text': True
            }
            
            if capture_output:
                kwargs.update({
                    'stdout': subprocess.PIPE,
                    'stderr': subprocess.PIPE
                })
            else:
                kwargs.update({
                    'stdout': subprocess.DEVNULL,
                    'stderr': subprocess.DEVNULL
                })
            
            # Lancement du processus
            process = subprocess.Popen(command, **kwargs)
            
            # Enregistrement du processus actif
            self.active_processes[process.pid] = {
                'process': process,
                'command': command,
                'start_time': start_time,
                'mode': ExecutionMode.BACKGROUND
            }
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=True,
                command=command,
                pid=process.pid,
                return_code=None,  # Pas encore terminé
                stdout="",
                stderr="",
                execution_time=execution_time,
                mode=ExecutionMode.BACKGROUND
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                command=command,
                pid=None,
                return_code=None,
                stdout="",
                stderr="",
                execution_time=execution_time,
                mode=ExecutionMode.BACKGROUND,
                error=str(e)
            )
    
    def _execute_interactive(
        self,
        command: str,
        cwd: Optional[str],
        env: Optional[Dict[str, str]],
        on_output: Optional[Callable[[str], None]],
        on_error: Optional[Callable[[str], None]],
        shell: bool
    ) -> ExecutionResult:
        """Exécution interactive."""
        start_time = time.time()
        
        try:
            # Configuration du processus
            process = subprocess.Popen(
                command,
                shell=shell,
                cwd=cwd,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Enregistrement du processus actif
            self.active_processes[process.pid] = {
                'process': process,
                'command': command,
                'start_time': start_time,
                'mode': ExecutionMode.INTERACTIVE
            }
            
            # Enregistrement des callbacks
            if on_output or on_error:
                self.process_callbacks[process.pid] = {
                    'on_output': on_output,
                    'on_error': on_error
                }
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=True,
                command=command,
                pid=process.pid,
                return_code=None,  # Processus en cours
                stdout="",
                stderr="",
                execution_time=execution_time,
                mode=ExecutionMode.INTERACTIVE
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                command=command,
                pid=None,
                return_code=None,
                stdout="",
                stderr="",
                execution_time=execution_time,
                mode=ExecutionMode.INTERACTIVE,
                error=str(e)
            )
    
    def _execute_monitored(
        self,
        command: str,
        cwd: Optional[str],
        env: Optional[Dict[str, str]],
        timeout: Optional[float],
        on_output: Optional[Callable[[str], None]],
        on_error: Optional[Callable[[str], None]],
        on_complete: Optional[Callable[[ExecutionResult], None]],
        shell: bool
    ) -> ExecutionResult:
        """Exécution surveillée avec callbacks."""
        # Pour l'instant, similaire à interactive mais avec monitoring
        # Peut être étendu pour surveillance avancée
        return self._execute_interactive(command, cwd, env, on_output, on_error, shell)
    
    def get_active_processes(self) -> Dict[int, Dict[str, Any]]:
        """Retourne la liste des processus actifs."""
        return self.active_processes.copy()
    
    def get_process_status(self, pid: int) -> Optional[Dict[str, Any]]:
        """Récupère le statut d'un processus."""
        if pid in self.active_processes:
            proc_info = self.active_processes[pid].copy()
            
            # Ajout du statut actuel
            try:
                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    proc_info.update({
                        'status': process.status(),
                        'cpu_percent': process.cpu_percent(),
                        'memory_info': process.memory_info()._asdict(),
                        'is_running': process.is_running()
                    })
                else:
                    proc_info['status'] = 'terminated'
                    proc_info['is_running'] = False
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                proc_info['status'] = 'unknown'
                proc_info['is_running'] = False
            
            return proc_info
        
        return None
    
    def communicate_with_process(self, pid: int, data: str) -> Dict[str, Any]:
        """Communique avec un processus interactif."""
        if pid not in self.active_processes:
            return {'success': False, 'error': f'Processus {pid} non trouvé'}
        
        proc_info = self.active_processes[pid]
        if proc_info['mode'] != ExecutionMode.INTERACTIVE:
            return {'success': False, 'error': f'Processus {pid} non interactif'}
        
        # Utilise le process_writer
        return write_to_process(pid, data)
    
    def terminate_process(self, pid: int, force: bool = False) -> Dict[str, Any]:
        """Termine un processus géré."""
        if pid not in self.active_processes:
            return {'success': False, 'error': f'Processus {pid} non trouvé'}
        
        # Utilise le process_killer
        result = kill_process(pid, force)
        
        # Nettoyage
        if pid in self.active_processes:
            del self.active_processes[pid]
        if pid in self.process_callbacks:
            del self.process_callbacks[pid]
        
        return result
    
    def cleanup_finished_processes(self):
        """Nettoie les processus terminés."""
        finished_pids = []
        
        for pid, proc_info in self.active_processes.items():
            try:
                if not psutil.pid_exists(pid):
                    finished_pids.append(pid)
                else:
                    process = psutil.Process(pid)
                    if not process.is_running():
                        finished_pids.append(pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                finished_pids.append(pid)
        
        for pid in finished_pids:
            if pid in self.active_processes:
                del self.active_processes[pid]
            if pid in self.process_callbacks:
                del self.process_callbacks[pid]
        
        return len(finished_pids)


# Instance globale
_executor = CommandExecutor()

def execute_command(*args, **kwargs) -> ExecutionResult:
    """Interface simplifiée pour l'exécution de commandes (synchrone)."""
    return _executor.execute_command(*args, **kwargs)

async def execute_command_async(*args, **kwargs) -> ExecutionResult:
    """Interface asynchrone pour l'exécution de commandes."""
    # Pour l'instant, on utilise la version synchrone dans un thread
    import asyncio
    loop = asyncio.get_event_loop()
    
    def _execute_sync():
        return _executor.execute_command(*args, **kwargs)
    
    return await loop.run_in_executor(None, _execute_sync)

def get_active_processes() -> Dict[int, Dict[str, Any]]:
    """Retourne les processus actifs."""
    return _executor.get_active_processes()

def get_process_status(pid: int) -> Optional[Dict[str, Any]]:
    """Récupère le statut d'un processus."""
    return _executor.get_process_status(pid)

def communicate_with_process(pid: int, data: str) -> Dict[str, Any]:
    """Communique avec un processus."""
    return _executor.communicate_with_process(pid, data)

def terminate_process(pid: int, force: bool = False) -> Dict[str, Any]:
    """Termine un processus."""
    return _executor.terminate_process(pid, force)

def cleanup_finished_processes() -> int:
    """Nettoie les processus terminés."""
    return _executor.cleanup_finished_processes()


def main():
    """Test du meta-outil execute_command."""
    if len(sys.argv) < 2:
        print("⛧ Execute Command - Alma's Meta-Tool ⛧")
        print()
        print("Usage:")
        print("  python3 execute_command.py <command> [--mode <mode>] [--timeout <seconds>]")
        print()
        print("Modes:")
        print("  blocking     : Bloquant (défaut)")
        print("  background   : Arrière-plan")
        print("  interactive  : Interactif")
        print("  monitored    : Surveillé")
        print()
        print("Exemples:")
        print("  python3 execute_command.py 'ls -la'")
        print("  python3 execute_command.py 'sleep 10' --mode background")
        print("  python3 execute_command.py 'python3 -i' --mode interactive")
        return
    
    # Parsing des arguments
    command = sys.argv[1]
    mode = ExecutionMode.BLOCKING
    timeout = None
    
    args = sys.argv[2:]
    if '--mode' in args:
        mode_idx = args.index('--mode')
        if mode_idx + 1 < len(args):
            mode_str = args[mode_idx + 1]
            try:
                mode = ExecutionMode(mode_str)
            except ValueError:
                print(f"❌ Mode invalide: {mode_str}")
                return
    
    if '--timeout' in args:
        timeout_idx = args.index('--timeout')
        if timeout_idx + 1 < len(args):
            try:
                timeout = float(args[timeout_idx + 1])
            except ValueError:
                print("❌ Timeout invalide")
                return
    
    print(f"⛧ Exécution: {command}")
    print(f"⚙️ Mode: {mode.value}")
    if timeout:
        print(f"⏰ Timeout: {timeout}s")
    print()
    
    # Exécution
    result = execute_command(command, mode=mode, timeout=timeout)
    
    # Affichage du résultat
    print("📊 Résultat:")
    print(f"  Succès: {result.success}")
    print(f"  PID: {result.pid}")
    print(f"  Code retour: {result.return_code}")
    print(f"  Temps d'exécution: {result.execution_time:.2f}s")
    
    if result.stdout:
        print(f"  Stdout: {result.stdout[:200]}...")
    if result.stderr:
        print(f"  Stderr: {result.stderr[:200]}...")
    if result.error:
        print(f"  Erreur: {result.error}")


if __name__ == "__main__":
    main()
