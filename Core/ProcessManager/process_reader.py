#!/usr/bin/env python3
"""
⛧ Read From Process ⛧
Alma's Process Reading Tool

Lit la sortie d'un processus en cours d'exécution.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import sys
import psutil
import subprocess
import time
from typing import Optional, Dict, Any


class ProcessReader:
    """Classe pour lire la sortie d'un processus."""
    
    def __init__(self, pid: int):
        """
        Initialise le lecteur de processus.
        
        Args:
            pid: ID du processus à surveiller
        """
        self.pid = pid
        self.process = None
        self._init_process()
    
    def _init_process(self):
        """Initialise la connexion au processus."""
        try:
            self.process = psutil.Process(self.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            raise ValueError(f"Impossible d'accéder au processus {self.pid}: {e}")
    
    def read_output(self, timeout: int = 5, max_lines: int = 100) -> Dict[str, Any]:
        """
        Lit la sortie du processus.
        
        Args:
            timeout: Timeout en secondes
            max_lines: Nombre maximum de lignes
            
        Returns:
            Dictionnaire avec le résultat
        """
        return read_from_process(self.pid, timeout, max_lines)
    
    def get_process_info(self) -> Dict[str, Any]:
        """
        Obtient les informations du processus.
        
        Returns:
            Dictionnaire avec les informations
        """
        try:
            return {
                'pid': self.pid,
                'name': self.process.name(),
                'status': self.process.status(),
                'cmdline': ' '.join(self.process.cmdline()) if self.process.cmdline() else 'N/A',
                'create_time': self.process.create_time(),
                'cpu_percent': self.process.cpu_percent(),
                'memory_info': self.process.memory_info()._asdict()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return {
                'pid': self.pid,
                'error': str(e)
            }


def read_from_process(pid: int, timeout: int = 5, max_lines: int = 100) -> Dict[str, Any]:
    """
    Lit la sortie d'un processus en cours d'exécution.
    
    Args:
        pid: ID du processus à lire
        timeout: Timeout en secondes pour la lecture
        max_lines: Nombre maximum de lignes à lire
    
    Returns:
        Dict avec le résultat de la lecture
    """
    try:
        # Vérification que le processus existe
        if not psutil.pid_exists(pid):
            return {
                'success': False,
                'error': f'Processus PID {pid} n\'existe pas',
                'output': '',
                'lines': []
            }
        
        # Récupération des informations du processus
        try:
            process = psutil.Process(pid)
            process_info = {
                'name': process.name(),
                'status': process.status(),
                'cmdline': ' '.join(process.cmdline()) if process.cmdline() else 'N/A',
                'create_time': process.create_time()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return {
                'success': False,
                'error': f'Impossible d\'accéder au processus {pid}: {e}',
                'output': '',
                'lines': []
            }
        
        # Tentative de lecture via /proc (Linux)
        if os.name == 'posix':
            output = _read_from_proc_fd(pid, timeout, max_lines)
            if output:
                lines = output.split('\n')[:max_lines]
                return {
                    'success': True,
                    'pid': pid,
                    'process_info': process_info,
                    'output': output,
                    'lines': lines,
                    'line_count': len(lines),
                    'method': 'proc_fd'
                }
        
        # Fallback : tentative de lecture via strace/ptrace
        output = _read_via_strace(pid, timeout, max_lines)
        if output:
            lines = output.split('\n')[:max_lines]
            return {
                'success': True,
                'pid': pid,
                'process_info': process_info,
                'output': output,
                'lines': lines,
                'line_count': len(lines),
                'method': 'strace'
            }
        
        # Si aucune méthode ne fonctionne
        return {
            'success': False,
            'error': f'Impossible de lire la sortie du processus {pid}',
            'pid': pid,
            'process_info': process_info,
            'output': '',
            'lines': [],
            'note': 'Le processus peut ne pas avoir de sortie accessible ou être protégé'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Erreur lecture processus {pid}: {str(e)}',
            'output': '',
            'lines': []
        }


def _read_from_proc_fd(pid: int, timeout: int, max_lines: int) -> Optional[str]:
    """
    Lit depuis les file descriptors du processus via /proc.
    
    Args:
        pid: ID du processus
        timeout: Timeout en secondes
        max_lines: Nombre maximum de lignes
    
    Returns:
        Sortie lue ou None
    """
    try:
        # Chemins des file descriptors
        fd_paths = [
            f'/proc/{pid}/fd/1',  # stdout
            f'/proc/{pid}/fd/2',  # stderr
        ]
        
        output_lines = []
        
        for fd_path in fd_paths:
            if os.path.exists(fd_path):
                try:
                    # Lecture non-bloquante
                    with open(fd_path, 'r', errors='ignore') as f:
                        lines = f.readlines()
                        output_lines.extend(lines[:max_lines])
                        
                        if len(output_lines) >= max_lines:
                            break
                            
                except (PermissionError, OSError):
                    # Pas d'accès à ce fd, continue
                    continue
        
        if output_lines:
            return ''.join(output_lines)
        
        return None
        
    except Exception:
        return None


def _read_via_strace(pid: int, timeout: int, max_lines: int) -> Optional[str]:
    """
    Lit la sortie via strace (méthode alternative).
    
    Args:
        pid: ID du processus
        timeout: Timeout en secondes
        max_lines: Nombre maximum de lignes
    
    Returns:
        Sortie lue ou None
    """
    try:
        # Commande strace pour capturer les écritures
        cmd = [
            'strace', '-p', str(pid), '-e', 'write',
            '-s', '1024', '-q', '-o', '/dev/stdout'
        ]
        
        # Exécution avec timeout
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            
            if stdout:
                # Parse la sortie strace pour extraire les données écrites
                output_lines = []
                for line in stdout.split('\n'):
                    if 'write(' in line and '"' in line:
                        # Extrait le contenu entre guillemets
                        start = line.find('"')
                        end = line.rfind('"')
                        if start != -1 and end != -1 and start < end:
                            content = line[start+1:end]
                            # Décode les séquences d'échappement
                            content = content.replace('\\n', '\n').replace('\\t', '\t')
                            output_lines.append(content)
                            
                            if len(output_lines) >= max_lines:
                                break
                
                if output_lines:
                    return '\n'.join(output_lines)
            
            return None
            
        except subprocess.TimeoutExpired:
            process.kill()
            return None
            
    except (FileNotFoundError, PermissionError):
        # strace non disponible ou pas de permissions
        return None
    except Exception:
        return None


def get_process_output_info(pid: int) -> Dict[str, Any]:
    """
    Récupère des informations sur les sorties d'un processus.
    
    Args:
        pid: ID du processus
    
    Returns:
        Dict avec informations sur les sorties
    """
    try:
        if not psutil.pid_exists(pid):
            return {'error': f'Processus {pid} n\'existe pas'}
        
        process = psutil.Process(pid)
        
        info = {
            'pid': pid,
            'name': process.name(),
            'status': process.status(),
            'cmdline': ' '.join(process.cmdline()) if process.cmdline() else 'N/A',
            'cwd': process.cwd() if hasattr(process, 'cwd') else 'N/A',
            'open_files': [],
            'connections': []
        }
        
        # Fichiers ouverts
        try:
            for f in process.open_files():
                info['open_files'].append({
                    'path': f.path,
                    'fd': f.fd,
                    'mode': getattr(f, 'mode', 'unknown')
                })
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            info['open_files'] = ['Access denied']
        
        # Connexions réseau
        try:
            for conn in process.connections():
                info['connections'].append({
                    'fd': conn.fd,
                    'family': conn.family.name if hasattr(conn.family, 'name') else str(conn.family),
                    'type': conn.type.name if hasattr(conn.type, 'name') else str(conn.type),
                    'laddr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    'raddr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    'status': conn.status
                })
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            info['connections'] = ['Access denied']
        
        return info
        
    except Exception as e:
        return {'error': f'Erreur récupération info processus {pid}: {str(e)}'}


def main():
    """Test de l'outil read_from_process."""
    if len(sys.argv) != 2:
        print("⛧ Read From Process - Alma's Tool ⛧")
        print()
        print("Usage: python3 read_from_process.py <PID>")
        print("Exemple: python3 read_from_process.py 1234")
        return
    
    try:
        pid = int(sys.argv[1])
    except ValueError:
        print("❌ PID doit être un nombre entier")
        return
    
    print(f"⛧ Lecture du processus PID {pid} ⛧")
    print()
    
    # Informations sur le processus
    print("📊 Informations processus:")
    info = get_process_output_info(pid)
    if 'error' in info:
        print(f"❌ {info['error']}")
        return
    
    print(f"  Nom: {info['name']}")
    print(f"  Status: {info['status']}")
    print(f"  Commande: {info['cmdline']}")
    print(f"  Répertoire: {info['cwd']}")
    print(f"  Fichiers ouverts: {len(info['open_files'])}")
    print(f"  Connexions: {len(info['connections'])}")
    print()
    
    # Lecture de la sortie
    print("📖 Lecture de la sortie:")
    result = read_from_process(pid, timeout=3, max_lines=20)
    
    if result['success']:
        print(f"✅ Lecture réussie via {result['method']}")
        print(f"📄 {result['line_count']} lignes lues:")
        print("-" * 50)
        for i, line in enumerate(result['lines'], 1):
            print(f"{i:2d}: {line.rstrip()}")
        print("-" * 50)
    else:
        print(f"❌ {result['error']}")
        if 'note' in result:
            print(f"💡 {result['note']}")


if __name__ == "__main__":
    main()
