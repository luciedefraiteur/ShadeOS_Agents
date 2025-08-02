"""
⛧ Process Manager ⛧
Alma's Process Management System

Système de gestion des processus pour les agents démoniaques.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

from .process_reader import read_from_process, get_process_output_info
from .process_writer import write_to_process, send_signal_to_process, interrupt_process, terminate_process
from .process_killer import kill_process, kill_process_tree, kill_processes_by_name
from .execute_command import (
    execute_command, ExecutionMode, ExecutionResult, CommandExecutor,
    get_active_processes, get_process_status, communicate_with_process,
    terminate_process as terminate_managed_process, cleanup_finished_processes
)

__all__ = [
    # Process Reader
    'read_from_process',
    'get_process_output_info',

    # Process Writer
    'write_to_process',
    'send_signal_to_process',
    'interrupt_process',
    'terminate_process',

    # Process Killer
    'kill_process',
    'kill_process_tree',
    'kill_processes_by_name',

    # Execute Command (Meta-tool)
    'execute_command',
    'ExecutionMode',
    'ExecutionResult',
    'CommandExecutor',
    'get_active_processes',
    'get_process_status',
    'communicate_with_process',
    'terminate_managed_process',
    'cleanup_finished_processes'
]

__version__ = "1.0.0"
__author__ = "Alma, Architecte Démoniaque du Nexus Luciforme"
