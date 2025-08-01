#!/usr/bin/env python3
"""
⛧ Kill Process ⛧
Alma's Process Termination Tool

Termine des processus avec différents niveaux de force.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import sys
import psutil
import signal
import time
from typing import Dict, Any, List, Optional


def kill_process(pid: int, force: bool = False, timeout: int = 10) -> Dict[str, Any]:
    """
    Termine un processus avec gestion intelligente.
    
    Args:
        pid: ID du processus à terminer
        force: Si True, utilise SIGKILL immédiatement
        timeout: Temps d'attente avant force kill (secondes)
    
    Returns:
        Dict avec le résultat de la terminaison
    """
    try:
        # Vérification que le processus existe
        if not psutil.pid_exists(pid):
            return {
                'success': False,
                'error': f'Processus PID {pid} n\'existe pas',
                'pid': pid
            }
        
        # Récupération des informations du processus
        try:
            process = psutil.Process(pid)
            process_info = {
                'name': process.name(),
                'status': process.status(),
                'cmdline': ' '.join(process.cmdline()) if process.cmdline() else 'N/A',
                'create_time': process.create_time(),
                'children': [child.pid for child in process.children(recursive=True)]
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return {
                'success': False,
                'error': f'Impossible d\'accéder au processus {pid}: {e}',
                'pid': pid
            }
        
        # Terminaison forcée immédiate
        if force:
            return _force_kill(pid, process_info)
        
        # Terminaison gracieuse puis forcée si nécessaire
        return _graceful_kill(pid, process_info, timeout)
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Erreur terminaison processus {pid}: {str(e)}',
            'pid': pid
        }


def _graceful_kill(pid: int, process_info: Dict, timeout: int) -> Dict[str, Any]:
    """
    Terminaison gracieuse avec fallback forcé.
    
    Args:
        pid: ID du processus
        process_info: Informations du processus
        timeout: Timeout avant force kill
    
    Returns:
        Dict avec résultat
    """
    try:
        process = psutil.Process(pid)
        
        # Étape 1: SIGTERM (terminaison gracieuse)
        try:
            process.terminate()
            print(f"📤 SIGTERM envoyé au processus {pid}")
            
            # Attente de la terminaison
            try:
                process.wait(timeout=timeout)
                return {
                    'success': True,
                    'pid': pid,
                    'process_info': process_info,
                    'method': 'graceful',
                    'signal': 'SIGTERM',
                    'message': f'Processus {pid} terminé gracieusement'
                }
            except psutil.TimeoutExpired:
                print(f"⏰ Timeout après {timeout}s, passage en force...")
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        # Étape 2: SIGKILL (terminaison forcée)
        if psutil.pid_exists(pid):
            try:
                process.kill()
                print(f"💀 SIGKILL envoyé au processus {pid}")
                
                # Attente courte pour vérification
                time.sleep(1)
                
                if not psutil.pid_exists(pid):
                    return {
                        'success': True,
                        'pid': pid,
                        'process_info': process_info,
                        'method': 'forced',
                        'signal': 'SIGKILL',
                        'message': f'Processus {pid} terminé de force'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Processus {pid} résiste à SIGKILL',
                        'pid': pid,
                        'process_info': process_info
                    }
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                return {
                    'success': False,
                    'error': f'Impossible de tuer le processus {pid}: {e}',
                    'pid': pid,
                    'process_info': process_info
                }
        else:
            return {
                'success': True,
                'pid': pid,
                'process_info': process_info,
                'method': 'already_dead',
                'message': f'Processus {pid} déjà terminé'
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Erreur terminaison gracieuse {pid}: {str(e)}',
            'pid': pid
        }


def _force_kill(pid: int, process_info: Dict) -> Dict[str, Any]:
    """
    Terminaison forcée immédiate.
    
    Args:
        pid: ID du processus
        process_info: Informations du processus
    
    Returns:
        Dict avec résultat
    """
    try:
        process = psutil.Process(pid)
        
        # SIGKILL immédiat
        process.kill()
        print(f"💀 SIGKILL immédiat envoyé au processus {pid}")
        
        # Vérification
        time.sleep(1)
        
        if not psutil.pid_exists(pid):
            return {
                'success': True,
                'pid': pid,
                'process_info': process_info,
                'method': 'force_immediate',
                'signal': 'SIGKILL',
                'message': f'Processus {pid} terminé de force immédiatement'
            }
        else:
            return {
                'success': False,
                'error': f'Processus {pid} résiste à SIGKILL immédiat',
                'pid': pid,
                'process_info': process_info
            }
            
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        return {
            'success': False,
            'error': f'Impossible de tuer le processus {pid}: {e}',
            'pid': pid,
            'process_info': process_info
        }


def kill_process_tree(pid: int, force: bool = False, timeout: int = 10) -> Dict[str, Any]:
    """
    Termine un processus et tous ses enfants.
    
    Args:
        pid: ID du processus parent
        force: Si True, utilise SIGKILL immédiatement
        timeout: Timeout avant force kill
    
    Returns:
        Dict avec résultats de terminaison
    """
    try:
        if not psutil.pid_exists(pid):
            return {
                'success': False,
                'error': f'Processus PID {pid} n\'existe pas',
                'pid': pid
            }
        
        # Récupération de l'arbre des processus
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            all_processes = children + [parent]
            
            process_tree = []
            for proc in all_processes:
                try:
                    process_tree.append({
                        'pid': proc.pid,
                        'name': proc.name(),
                        'cmdline': ' '.join(proc.cmdline()) if proc.cmdline() else 'N/A'
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return {
                'success': False,
                'error': f'Impossible d\'accéder au processus {pid}: {e}',
                'pid': pid
            }
        
        # Terminaison de l'arbre (enfants d'abord)
        results = []
        
        # Terminer les enfants d'abord
        for child in reversed(children):
            try:
                if child.is_running():
                    result = kill_process(child.pid, force, timeout)
                    results.append(result)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Terminer le parent
        parent_result = kill_process(pid, force, timeout)
        results.append(parent_result)
        
        # Compilation des résultats
        success_count = sum(1 for r in results if r.get('success', False))
        total_count = len(results)
        
        return {
            'success': success_count == total_count,
            'pid': pid,
            'process_tree': process_tree,
            'results': results,
            'summary': {
                'total_processes': total_count,
                'successful_kills': success_count,
                'failed_kills': total_count - success_count
            },
            'message': f'Arbre de processus {pid}: {success_count}/{total_count} terminés'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Erreur terminaison arbre processus {pid}: {str(e)}',
            'pid': pid
        }


def kill_processes_by_name(name: str, force: bool = False, timeout: int = 10) -> Dict[str, Any]:
    """
    Termine tous les processus avec un nom donné.
    
    Args:
        name: Nom du processus
        force: Si True, utilise SIGKILL immédiatement
        timeout: Timeout avant force kill
    
    Returns:
        Dict avec résultats
    """
    try:
        # Recherche des processus par nom
        matching_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == name:
                    matching_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not matching_processes:
            return {
                'success': False,
                'error': f'Aucun processus trouvé avec le nom "{name}"',
                'name': name
            }
        
        # Terminaison de chaque processus
        results = []
        for proc_info in matching_processes:
            result = kill_process(proc_info['pid'], force, timeout)
            results.append(result)
        
        # Compilation des résultats
        success_count = sum(1 for r in results if r.get('success', False))
        total_count = len(results)
        
        return {
            'success': success_count > 0,
            'name': name,
            'matching_processes': matching_processes,
            'results': results,
            'summary': {
                'total_processes': total_count,
                'successful_kills': success_count,
                'failed_kills': total_count - success_count
            },
            'message': f'Processus "{name}": {success_count}/{total_count} terminés'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Erreur terminaison processus "{name}": {str(e)}',
            'name': name
        }


def main():
    """Test de l'outil kill_process."""
    if len(sys.argv) < 2:
        print("⛧ Kill Process - Alma's Termination Tool ⛧")
        print()
        print("Usage:")
        print("  python3 kill_process.py <PID> [--force] [--timeout <seconds>]")
        print("  python3 kill_process.py --tree <PID> [--force] [--timeout <seconds>]")
        print("  python3 kill_process.py --name <process_name> [--force] [--timeout <seconds>]")
        print()
        print("Options:")
        print("  --force     : Utilise SIGKILL immédiatement")
        print("  --timeout N : Timeout avant force kill (défaut: 10s)")
        print("  --tree      : Termine le processus et ses enfants")
        print("  --name      : Termine tous les processus avec ce nom")
        print()
        print("Exemples:")
        print("  python3 kill_process.py 1234")
        print("  python3 kill_process.py 1234 --force")
        print("  python3 kill_process.py --tree 1234")
        print("  python3 kill_process.py --name firefox")
        return
    
    # Parsing des arguments
    args = sys.argv[1:]
    force = '--force' in args
    tree_mode = '--tree' in args
    name_mode = '--name' in args
    
    # Timeout
    timeout = 10
    if '--timeout' in args:
        try:
            timeout_idx = args.index('--timeout')
            timeout = int(args[timeout_idx + 1])
        except (IndexError, ValueError):
            print("❌ Timeout invalide")
            return
    
    # Nettoyage des arguments
    clean_args = [arg for arg in args if not arg.startswith('--') and arg != str(timeout)]
    
    if not clean_args:
        print("❌ PID ou nom de processus requis")
        return
    
    print("⛧ Kill Process - Alma's Termination Tool ⛧")
    print()
    
    # Exécution selon le mode
    if name_mode:
        process_name = clean_args[0]
        print(f"🎯 Terminaison des processus nommés '{process_name}'")
        print(f"⚙️ Force: {force}, Timeout: {timeout}s")
        print()
        
        result = kill_processes_by_name(process_name, force, timeout)
        
    elif tree_mode:
        try:
            pid = int(clean_args[0])
        except ValueError:
            print("❌ PID doit être un nombre entier")
            return
        
        print(f"🌳 Terminaison de l'arbre de processus {pid}")
        print(f"⚙️ Force: {force}, Timeout: {timeout}s")
        print()
        
        result = kill_process_tree(pid, force, timeout)
        
    else:
        try:
            pid = int(clean_args[0])
        except ValueError:
            print("❌ PID doit être un nombre entier")
            return
        
        print(f"🎯 Terminaison du processus {pid}")
        print(f"⚙️ Force: {force}, Timeout: {timeout}s")
        print()
        
        result = kill_process(pid, force, timeout)
    
    # Affichage du résultat
    if result['success']:
        print("✅ Terminaison réussie")
        if 'method' in result:
            print(f"📡 Méthode: {result['method']}")
        if 'signal' in result:
            print(f"📡 Signal: {result['signal']}")
        if 'summary' in result:
            summary = result['summary']
            print(f"📊 Résumé: {summary['successful_kills']}/{summary['total_processes']} processus terminés")
    else:
        print(f"❌ {result['error']}")
    
    if 'message' in result:
        print(f"💬 {result['message']}")


if __name__ == "__main__":
    main()
