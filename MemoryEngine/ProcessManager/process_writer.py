#!/usr/bin/env python3
"""
⛧ Write To Process ⛧
Alma's Process Writing Tool

Écrit des données vers l'entrée d'un processus en cours d'exécution.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import sys
import psutil
import subprocess
import signal
from typing import Optional, Dict, Any


def write_to_process(pid: int, data: str, add_newline: bool = True) -> Dict[str, Any]:
    """
    Écrit des données vers l'entrée d'un processus.
    
    Args:
        pid: ID du processus cible
        data: Données à écrire
        add_newline: Ajouter un retour à la ligne
    
    Returns:
        Dict avec le résultat de l'écriture
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
                'cmdline': ' '.join(process.cmdline()) if process.cmdline() else 'N/A'
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return {
                'success': False,
                'error': f'Impossible d\'accéder au processus {pid}: {e}',
                'pid': pid
            }
        
        # Préparation des données
        if add_newline and not data.endswith('\n'):
            data += '\n'
        
        # Tentative d'écriture via /proc (Linux)
        if os.name == 'posix':
            result = _write_via_proc_fd(pid, data)
            if result['success']:
                return {
                    'success': True,
                    'pid': pid,
                    'process_info': process_info,
                    'data_sent': data,
                    'bytes_written': len(data.encode('utf-8')),
                    'method': 'proc_fd'
                }
        
        # Fallback : tentative via signal + pipe
        result = _write_via_signal(pid, data)
        if result['success']:
            return {
                'success': True,
                'pid': pid,
                'process_info': process_info,
                'data_sent': data,
                'bytes_written': len(data.encode('utf-8')),
                'method': 'signal'
            }
        
        # Si aucune méthode ne fonctionne
        return {
            'success': False,
            'error': f'Impossible d\'écrire vers le processus {pid}',
            'pid': pid,
            'process_info': process_info,
            'note': 'Le processus peut ne pas accepter d\'entrée ou être protégé'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Erreur écriture vers processus {pid}: {str(e)}',
            'pid': pid
        }


def _write_via_proc_fd(pid: int, data: str) -> Dict[str, Any]:
    """
    Écrit via les file descriptors du processus.
    
    Args:
        pid: ID du processus
        data: Données à écrire
    
    Returns:
        Dict avec résultat
    """
    try:
        # Chemin vers stdin du processus
        stdin_path = f'/proc/{pid}/fd/0'
        
        if os.path.exists(stdin_path):
            try:
                with open(stdin_path, 'w') as f:
                    f.write(data)
                    f.flush()
                
                return {'success': True}
                
            except (PermissionError, OSError, BrokenPipeError) as e:
                return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': 'stdin non accessible'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


def _write_via_signal(pid: int, data: str) -> Dict[str, Any]:
    """
    Tentative d'écriture via signaux (méthode alternative).
    
    Args:
        pid: ID du processus
        data: Données à écrire
    
    Returns:
        Dict avec résultat
    """
    try:
        # Cette méthode est limitée et ne peut pas vraiment envoyer des données
        # Elle peut seulement envoyer des signaux au processus
        
        # Vérification que le processus peut recevoir des signaux
        try:
            os.kill(pid, 0)  # Signal 0 pour tester l'existence
        except ProcessLookupError:
            return {'success': False, 'error': 'Processus non trouvé'}
        except PermissionError:
            return {'success': False, 'error': 'Permission refusée'}
        
        # Pour l'instant, cette méthode ne peut pas vraiment envoyer de données
        # Elle pourrait être étendue pour des cas spéciaux
        return {'success': False, 'error': 'Méthode signal non implémentée pour données'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


def send_signal_to_process(pid: int, signal_num: int = signal.SIGTERM) -> Dict[str, Any]:
    """
    Envoie un signal à un processus.
    
    Args:
        pid: ID du processus
        signal_num: Numéro du signal à envoyer
    
    Returns:
        Dict avec résultat
    """
    try:
        if not psutil.pid_exists(pid):
            return {
                'success': False,
                'error': f'Processus PID {pid} n\'existe pas',
                'pid': pid
            }
        
        # Informations sur le signal
        signal_name = signal.Signals(signal_num).name if hasattr(signal, 'Signals') else f'SIG{signal_num}'
        
        # Envoi du signal
        try:
            os.kill(pid, signal_num)
            
            return {
                'success': True,
                'pid': pid,
                'signal': signal_num,
                'signal_name': signal_name,
                'message': f'Signal {signal_name} envoyé au processus {pid}'
            }
            
        except ProcessLookupError:
            return {
                'success': False,
                'error': f'Processus {pid} non trouvé',
                'pid': pid
            }
        except PermissionError:
            return {
                'success': False,
                'error': f'Permission refusée pour envoyer signal au processus {pid}',
                'pid': pid
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Erreur envoi signal vers processus {pid}: {str(e)}',
            'pid': pid
        }


def interrupt_process(pid: int) -> Dict[str, Any]:
    """
    Interrompt un processus (SIGINT - Ctrl+C).
    
    Args:
        pid: ID du processus
    
    Returns:
        Dict avec résultat
    """
    return send_signal_to_process(pid, signal.SIGINT)


def terminate_process(pid: int) -> Dict[str, Any]:
    """
    Termine un processus proprement (SIGTERM).
    
    Args:
        pid: ID du processus
    
    Returns:
        Dict avec résultat
    """
    return send_signal_to_process(pid, signal.SIGTERM)


def main():
    """Test de l'outil write_to_process."""
    if len(sys.argv) < 3:
        print("⛧ Write To Process - Alma's Tool ⛧")
        print()
        print("Usage: python3 write_to_process.py <PID> <data>")
        print("       python3 write_to_process.py <PID> --signal <signal_num>")
        print("       python3 write_to_process.py <PID> --interrupt")
        print("       python3 write_to_process.py <PID> --terminate")
        print()
        print("Exemples:")
        print("  python3 write_to_process.py 1234 'hello world'")
        print("  python3 write_to_process.py 1234 --interrupt")
        print("  python3 write_to_process.py 1234 --signal 9")
        return
    
    try:
        pid = int(sys.argv[1])
    except ValueError:
        print("❌ PID doit être un nombre entier")
        return
    
    print(f"⛧ Écriture vers le processus PID {pid} ⛧")
    print()
    
    # Vérification que le processus existe
    if not psutil.pid_exists(pid):
        print(f"❌ Processus {pid} n'existe pas")
        return
    
    # Informations sur le processus
    try:
        process = psutil.Process(pid)
        print(f"📊 Processus: {process.name()}")
        print(f"📊 Status: {process.status()}")
        print(f"📊 Commande: {' '.join(process.cmdline()) if process.cmdline() else 'N/A'}")
        print()
    except Exception as e:
        print(f"⚠️ Impossible de récupérer les infos: {e}")
        print()
    
    # Traitement des arguments
    if sys.argv[2] == '--interrupt':
        print("🔄 Envoi signal SIGINT (Ctrl+C)...")
        result = interrupt_process(pid)
    elif sys.argv[2] == '--terminate':
        print("🔄 Envoi signal SIGTERM...")
        result = terminate_process(pid)
    elif sys.argv[2] == '--signal' and len(sys.argv) > 3:
        try:
            signal_num = int(sys.argv[3])
            print(f"🔄 Envoi signal {signal_num}...")
            result = send_signal_to_process(pid, signal_num)
        except ValueError:
            print("❌ Numéro de signal invalide")
            return
    else:
        # Écriture de données
        data = sys.argv[2]
        print(f"📝 Écriture de: '{data}'")
        result = write_to_process(pid, data)
    
    # Affichage du résultat
    if result['success']:
        print("✅ Opération réussie")
        if 'method' in result:
            print(f"📡 Méthode: {result['method']}")
        if 'bytes_written' in result:
            print(f"📊 Octets écrits: {result['bytes_written']}")
        if 'signal_name' in result:
            print(f"📡 Signal: {result['signal_name']}")
    else:
        print(f"❌ {result['error']}")
        if 'note' in result:
            print(f"💡 {result['note']}")


if __name__ == "__main__":
    main()
