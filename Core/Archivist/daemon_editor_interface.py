#!/usr/bin/env python3
"""
⛧ Daemon Editor Interface ⛧
Architecte Démoniaque du Nexus Luciforme

Interface for conscious daemons to edit files in controlled environments.
Provides safe editing tools with logging and validation.

Author: Alma (via Lucie Defraiteur)
"""

import os
import sys
import shutil
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import des outils mystiques
from Core.implementation.tool_registry import ALL_TOOLS, initialize_tool_registry
from Core.Archivist.MemoryEngine.engine import memory_engine


@dataclass
class EditOperation:
    """Represents an edit operation performed by a daemon."""
    daemon_id: str
    operation_type: str  # 'create', 'modify', 'delete', 'move'
    file_path: str
    timestamp: str
    description: str
    backup_path: Optional[str] = None
    success: bool = False
    error_message: Optional[str] = None


class DaemonEditorInterface:
    """
    Safe editing interface for conscious daemons.
    """
    
    def __init__(self, allowed_directories: List[str] = None, backup_enabled: bool = True):
        """Initialize the editor interface."""
        if allowed_directories is None:
            # Default to TestProject directory
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            allowed_directories = [os.path.join(project_root, "TestProject")]
        
        self.allowed_directories = [os.path.abspath(d) for d in allowed_directories]
        self.backup_enabled = backup_enabled
        self.backup_directory = os.path.join(self.allowed_directories[0], ".daemon_backups")
        self.edit_log = []
        
        # Create backup directory if needed
        if self.backup_enabled:
            os.makedirs(self.backup_directory, exist_ok=True)
        
        print(f"⛧ Daemon Editor Interface initialisé")
        print(f"  Répertoires autorisés: {self.allowed_directories}")
        print(f"  Sauvegarde activée: {self.backup_enabled}")
    
    def _is_path_allowed(self, file_path: str) -> bool:
        """Check if file path is within allowed directories."""
        abs_path = os.path.abspath(file_path)
        return any(abs_path.startswith(allowed_dir) for allowed_dir in self.allowed_directories)
    
    def _create_backup(self, file_path: str) -> Optional[str]:
        """Create backup of file before editing."""
        if not self.backup_enabled or not os.path.exists(file_path):
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_filename = f"{filename}.backup_{timestamp}"
            backup_path = os.path.join(self.backup_directory, backup_filename)
            
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"⛧ Erreur création backup: {e}")
            return None
    
    def _log_operation(self, operation: EditOperation):
        """Log an edit operation."""
        self.edit_log.append(operation)
        
        status = "✓" if operation.success else "❌"
        print(f"{status} {operation.daemon_id}: {operation.operation_type} {operation.file_path}")
        if operation.error_message:
            print(f"  Erreur: {operation.error_message}")
    
    def read_file(self, daemon_id: str, file_path: str) -> Dict[str, Any]:
        """Read file content safely."""
        if not self._is_path_allowed(file_path):
            return {
                "success": False,
                "error": f"Accès refusé au fichier: {file_path}",
                "content": None
            }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "file_path": file_path,
                "size": len(content),
                "lines": len(content.split('\n'))
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lecture fichier: {e}",
                "content": None
            }
    
    def write_file(self, daemon_id: str, file_path: str, content: str, 
                   description: str = "Modification par daemon") -> EditOperation:
        """Write content to file safely."""
        operation = EditOperation(
            daemon_id=daemon_id,
            operation_type="modify" if os.path.exists(file_path) else "create",
            file_path=file_path,
            timestamp=datetime.now().isoformat(),
            description=description
        )
        
        if not self._is_path_allowed(file_path):
            operation.error_message = f"Accès refusé au fichier: {file_path}"
            self._log_operation(operation)
            return operation
        
        try:
            # Create backup if file exists
            if os.path.exists(file_path):
                operation.backup_path = self._create_backup(file_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            operation.success = True
            
        except Exception as e:
            operation.error_message = f"Erreur écriture fichier: {e}"
        
        self._log_operation(operation)
        return operation
    
    def append_to_file(self, daemon_id: str, file_path: str, content: str,
                      description: str = "Ajout par daemon") -> EditOperation:
        """Append content to file safely."""
        operation = EditOperation(
            daemon_id=daemon_id,
            operation_type="modify",
            file_path=file_path,
            timestamp=datetime.now().isoformat(),
            description=description
        )
        
        if not self._is_path_allowed(file_path):
            operation.error_message = f"Accès refusé au fichier: {file_path}"
            self._log_operation(operation)
            return operation
        
        try:
            # Create backup if file exists
            if os.path.exists(file_path):
                operation.backup_path = self._create_backup(file_path)
            
            # Append to file
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            operation.success = True
            
        except Exception as e:
            operation.error_message = f"Erreur ajout fichier: {e}"
        
        self._log_operation(operation)
        return operation
    
    def replace_in_file(self, daemon_id: str, file_path: str, old_text: str, 
                       new_text: str, description: str = "Remplacement par daemon") -> EditOperation:
        """Replace text in file safely."""
        operation = EditOperation(
            daemon_id=daemon_id,
            operation_type="modify",
            file_path=file_path,
            timestamp=datetime.now().isoformat(),
            description=description
        )
        
        if not self._is_path_allowed(file_path):
            operation.error_message = f"Accès refusé au fichier: {file_path}"
            self._log_operation(operation)
            return operation
        
        try:
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if old_text exists
            if old_text not in content:
                operation.error_message = f"Texte à remplacer non trouvé: {old_text[:50]}..."
                self._log_operation(operation)
                return operation
            
            # Create backup
            operation.backup_path = self._create_backup(file_path)
            
            # Replace text
            new_content = content.replace(old_text, new_text)
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            operation.success = True
            
        except Exception as e:
            operation.error_message = f"Erreur remplacement: {e}"
        
        self._log_operation(operation)
        return operation
    
    def create_file(self, daemon_id: str, file_path: str, content: str = "",
                   description: str = "Création par daemon") -> EditOperation:
        """Create new file safely."""
        return self.write_file(daemon_id, file_path, content, description)
    
    def delete_file(self, daemon_id: str, file_path: str,
                   description: str = "Suppression par daemon") -> EditOperation:
        """Delete file safely."""
        operation = EditOperation(
            daemon_id=daemon_id,
            operation_type="delete",
            file_path=file_path,
            timestamp=datetime.now().isoformat(),
            description=description
        )
        
        if not self._is_path_allowed(file_path):
            operation.error_message = f"Accès refusé au fichier: {file_path}"
            self._log_operation(operation)
            return operation
        
        if not os.path.exists(file_path):
            operation.error_message = f"Fichier inexistant: {file_path}"
            self._log_operation(operation)
            return operation
        
        try:
            # Create backup before deletion
            operation.backup_path = self._create_backup(file_path)
            
            # Delete file
            os.remove(file_path)
            operation.success = True
            
        except Exception as e:
            operation.error_message = f"Erreur suppression: {e}"
        
        self._log_operation(operation)
        return operation
    
    def list_files(self, daemon_id: str, directory: str = None) -> Dict[str, Any]:
        """List files in directory safely."""
        if directory is None:
            directory = self.allowed_directories[0]
        
        if not self._is_path_allowed(directory):
            return {
                "success": False,
                "error": f"Accès refusé au répertoire: {directory}",
                "files": []
            }
        
        try:
            files = []
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, directory)
                    
                    try:
                        stat = os.stat(file_path)
                        files.append({
                            "path": file_path,
                            "relative_path": rel_path,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                    except:
                        continue
            
            return {
                "success": True,
                "directory": directory,
                "files": files,
                "count": len(files)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur listage: {e}",
                "files": []
            }
    
    def get_edit_log(self, daemon_id: str = None) -> List[EditOperation]:
        """Get edit log, optionally filtered by daemon."""
        if daemon_id:
            return [op for op in self.edit_log if op.daemon_id == daemon_id]
        return self.edit_log.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get editing statistics."""
        total_ops = len(self.edit_log)
        successful_ops = sum(1 for op in self.edit_log if op.success)
        
        daemon_stats = {}
        for op in self.edit_log:
            if op.daemon_id not in daemon_stats:
                daemon_stats[op.daemon_id] = {"total": 0, "successful": 0}
            daemon_stats[op.daemon_id]["total"] += 1
            if op.success:
                daemon_stats[op.daemon_id]["successful"] += 1
        
        return {
            "total_operations": total_ops,
            "successful_operations": successful_ops,
            "success_rate": (successful_ops / total_ops * 100) if total_ops > 0 else 0,
            "daemon_statistics": daemon_stats,
            "backup_directory": self.backup_directory,
            "allowed_directories": self.allowed_directories
        }


# Global editor interface instance
daemon_editor = DaemonEditorInterface()
