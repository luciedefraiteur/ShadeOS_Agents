#!/usr/bin/env python3
"""
⛧ Daemon Tools Interface ⛧
Architecte Démoniaque du Nexus Luciforme

Interface for conscious daemons to access the complete arsenal of mystical tools.
Provides safe access to all 29 tools with logging and validation.

Author: Alma (via Lucie Defraiteur)
"""

import os
import sys
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import des outils mystiques
from Core.implementation.tool_registry import ALL_TOOLS, initialize_tool_registry
from Core.Archivist.MemoryEngine.engine import MemoryEngine


@dataclass
class ToolInvocation:
    """Represents a tool invocation by a daemon."""
    daemon_id: str
    tool_id: str
    args: Dict[str, Any]
    timestamp: str
    result: Optional[Any] = None
    success: bool = False
    error_message: Optional[str] = None
    execution_time: float = 0.0


class DaemonToolsInterface:
    """
    Interface for conscious daemons to access all mystical tools.
    """
    
    def __init__(self, allowed_directories: List[str] = None):
        """Initialize the tools interface."""
        if allowed_directories is None:
            # Default to TestProject and current directory
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            allowed_directories = [
                os.path.join(project_root, "TestProject"),
                project_root
            ]
        
        self.allowed_directories = [os.path.abspath(d) for d in allowed_directories]
        self.invocation_log = []
        
        # Initialize tool registry
        self.memory_engine = MemoryEngine()
        initialize_tool_registry(self.memory_engine)
        
        print(f"⛧ Daemon Tools Interface initialisé")
        print(f"  Outils disponibles: {len(ALL_TOOLS)}")
        print(f"  Répertoires autorisés: {self.allowed_directories}")
    
    def _is_path_allowed(self, file_path: str) -> bool:
        """Check if file path is within allowed directories."""
        abs_path = os.path.abspath(file_path)
        return any(abs_path.startswith(allowed_dir) for allowed_dir in self.allowed_directories)
    
    def _validate_tool_args(self, tool_id: str, args: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate tool arguments and paths."""
        if tool_id not in ALL_TOOLS:
            return False, f"Outil inconnu: {tool_id}"
        
        # Check for path arguments and validate them
        path_args = ['path', 'file_path', 'directory', 'filepath']
        for arg_name, arg_value in args.items():
            if arg_name in path_args and isinstance(arg_value, str):
                if not self._is_path_allowed(arg_value):
                    return False, f"Accès refusé au chemin: {arg_value}"
        
        return True, ""
    
    def _log_invocation(self, invocation: ToolInvocation):
        """Log a tool invocation."""
        self.invocation_log.append(invocation)
        
        status = "✓" if invocation.success else "❌"
        print(f"{status} {invocation.daemon_id}: {invocation.tool_id}({', '.join(f'{k}={v}' for k, v in invocation.args.items())})")
        if invocation.error_message:
            print(f"  Erreur: {invocation.error_message}")
        if invocation.success and invocation.execution_time > 0:
            print(f"  Temps: {invocation.execution_time:.3f}s")
    
    def invoke_tool(self, daemon_id: str, tool_id: str, **kwargs) -> ToolInvocation:
        """Invoke a mystical tool safely."""
        start_time = datetime.now()
        
        invocation = ToolInvocation(
            daemon_id=daemon_id,
            tool_id=tool_id,
            args=kwargs,
            timestamp=start_time.isoformat()
        )
        
        try:
            # Validate tool and arguments
            valid, error_msg = self._validate_tool_args(tool_id, kwargs)
            if not valid:
                invocation.error_message = error_msg
                self._log_invocation(invocation)
                return invocation
            
            # Get tool function
            tool_info = ALL_TOOLS[tool_id]
            tool_function = tool_info['function']
            
            # Invoke tool
            result = tool_function(**kwargs)
            
            invocation.result = result
            invocation.success = True
            
            # Calculate execution time
            end_time = datetime.now()
            invocation.execution_time = (end_time - start_time).total_seconds()
            
        except Exception as e:
            invocation.error_message = f"Erreur exécution outil: {e}"
        
        self._log_invocation(invocation)
        return invocation
    
    def list_available_tools(self, daemon_id: str, category_filter: str = None) -> Dict[str, Any]:
        """List available tools, optionally filtered by category."""
        try:
            # Group tools by category
            categories = {}
            for tool_id, tool_info in ALL_TOOLS.items():
                lucidoc = tool_info.get('lucidoc', {})
                pacte = lucidoc.get('🜄pacte', {})
                tool_type = pacte.get('type', 'unknown')
                
                if category_filter and tool_type != category_filter:
                    continue
                
                if tool_type not in categories:
                    categories[tool_type] = []
                
                categories[tool_type].append({
                    'id': tool_id,
                    'intent': pacte.get('intent', 'Intention non documentée'),
                    'level': pacte.get('level', 'unknown'),
                    'signature': lucidoc.get('🜂invocation', {}).get('signature', 'Signature non documentée')
                })
            
            return {
                "success": True,
                "daemon_id": daemon_id,
                "categories": categories,
                "total_tools": sum(len(tools) for tools in categories.values()),
                "filter_applied": category_filter
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur listage outils: {e}",
                "daemon_id": daemon_id
            }
    
    def get_tool_documentation(self, daemon_id: str, tool_id: str) -> Dict[str, Any]:
        """Get complete documentation for a specific tool."""
        try:
            if tool_id not in ALL_TOOLS:
                return {
                    "success": False,
                    "error": f"Outil inconnu: {tool_id}",
                    "daemon_id": daemon_id
                }
            
            tool_info = ALL_TOOLS[tool_id]
            lucidoc = tool_info.get('lucidoc', {})
            
            return {
                "success": True,
                "daemon_id": daemon_id,
                "tool_id": tool_id,
                "documentation": lucidoc,
                "function_available": tool_info.get('function') is not None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur documentation outil: {e}",
                "daemon_id": daemon_id,
                "tool_id": tool_id
            }
    
    def get_tools_by_category(self, daemon_id: str, category: str) -> List[str]:
        """Get list of tool IDs for a specific category."""
        try:
            tools = []
            for tool_id, tool_info in ALL_TOOLS.items():
                lucidoc = tool_info.get('lucidoc', {})
                pacte = lucidoc.get('🜄pacte', {})
                tool_type = pacte.get('type', 'unknown')
                
                if tool_type == category:
                    tools.append(tool_id)
            
            return tools
            
        except Exception as e:
            print(f"⛧ Erreur récupération outils par catégorie: {e}")
            return []
    
    def get_invocation_log(self, daemon_id: str = None, tool_id: str = None) -> List[ToolInvocation]:
        """Get invocation log, optionally filtered."""
        filtered_log = self.invocation_log.copy()
        
        if daemon_id:
            filtered_log = [inv for inv in filtered_log if inv.daemon_id == daemon_id]
        
        if tool_id:
            filtered_log = [inv for inv in filtered_log if inv.tool_id == tool_id]
        
        return filtered_log
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tools usage statistics."""
        total_invocations = len(self.invocation_log)
        successful_invocations = sum(1 for inv in self.invocation_log if inv.success)
        
        # Statistics by daemon
        daemon_stats = {}
        for inv in self.invocation_log:
            if inv.daemon_id not in daemon_stats:
                daemon_stats[inv.daemon_id] = {"total": 0, "successful": 0, "tools_used": set()}
            daemon_stats[inv.daemon_id]["total"] += 1
            daemon_stats[inv.daemon_id]["tools_used"].add(inv.tool_id)
            if inv.success:
                daemon_stats[inv.daemon_id]["successful"] += 1
        
        # Convert sets to lists for JSON serialization
        for stats in daemon_stats.values():
            stats["tools_used"] = list(stats["tools_used"])
            stats["unique_tools"] = len(stats["tools_used"])
        
        # Statistics by tool
        tool_stats = {}
        for inv in self.invocation_log:
            if inv.tool_id not in tool_stats:
                tool_stats[inv.tool_id] = {"total": 0, "successful": 0, "daemons_used": set()}
            tool_stats[inv.tool_id]["total"] += 1
            tool_stats[inv.tool_id]["daemons_used"].add(inv.daemon_id)
            if inv.success:
                tool_stats[inv.tool_id]["successful"] += 1
        
        # Convert sets to lists
        for stats in tool_stats.values():
            stats["daemons_used"] = list(stats["daemons_used"])
            stats["unique_daemons"] = len(stats["daemons_used"])
        
        return {
            "total_invocations": total_invocations,
            "successful_invocations": successful_invocations,
            "success_rate": (successful_invocations / total_invocations * 100) if total_invocations > 0 else 0,
            "daemon_statistics": daemon_stats,
            "tool_statistics": tool_stats,
            "available_tools": len(ALL_TOOLS),
            "allowed_directories": self.allowed_directories
        }
    
    def suggest_tools_for_task(self, daemon_id: str, task_description: str) -> List[str]:
        """Suggest tools based on task description."""
        suggestions = []
        task_lower = task_description.lower()
        
        # Simple keyword-based suggestions
        keyword_mappings = {
            'read': ['read_file_content', 'read_file_lines', 'read_file_chars'],
            'write': ['create_file', 'overwrite_file', 'append_to_file'],
            'search': ['find_files', 'search_in_files', 'scry_for_text'],
            'modify': ['replace_text_in_file', 'replace_lines_in_file', 'insert_text_at_line'],
            'list': ['list_directory_contents', 'walk_directory'],
            'memory': ['create_memory', 'recall', 'find_memories_by_keyword'],
            'execute': ['run_shell_command', 'invoke_cli_tool'],
            'documentation': ['get_tool_documentation', 'get_luciform_grimoire']
        }
        
        for keyword, tools in keyword_mappings.items():
            if keyword in task_lower:
                suggestions.extend(tools)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for tool in suggestions:
            if tool not in seen and tool in ALL_TOOLS:
                seen.add(tool)
                unique_suggestions.append(tool)
        
        return unique_suggestions[:10]  # Limit to 10 suggestions


# Global tools interface instance
daemon_tools = DaemonToolsInterface()
