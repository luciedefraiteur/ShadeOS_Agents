#!/usr/bin/env python3
"""
⛧ V10 Tool Agent ⛧
Alma's Tool Execution Agent for V10

Agent spécialisé dans l'exécution d'outils et la gestion des formats.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from .temporal_integration import V10TemporalIntegration
from .xml_formatter import V10XMLFormatter


@dataclass
class ToolResult:
    """Résultat d'exécution d'un outil."""
    success: bool
    tool_name: str
    data: Any
    execution_time: float
    error: Optional[str] = None
    node_id: Optional[str] = None


class V10ToolAgent:
    """Agent spécialisé dans l'exécution d'outils et la gestion des formats."""
    
    def __init__(self, temporal_integration: V10TemporalIntegration):
        """Initialise l'agent outils."""
        self.temporal_integration = temporal_integration
        self.xml_formatter = V10XMLFormatter()
        self.tool_registry = V10ToolRegistry()
        self.mcp_manager = None  # Sera initialisé si MCP disponible
        
        # Initialisation du gestionnaire MCP selon feature flag
        try:
            from Core.Config.feature_flags import is_mcp_enabled
        except Exception:
            def is_mcp_enabled() -> bool:
                return False

        if is_mcp_enabled():
            try:
                from Core.Providers.MCP import V10McpManager
                self.mcp_manager = V10McpManager(temporal_integration)
                print("✅ MCP Manager intégré dans Tool Agent")
            except ImportError:
                print("⚠️ MCP Manager non disponible - Mode local uniquement")
        else:
            print("ℹ️ MCP désactivé par feature flag - Mode local uniquement")
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], session_id: str) -> ToolResult:
        """Exécute un outil avec formatage optimisé."""
        
        start_time = datetime.now()
        
        # Enregistrement du début d'exécution
        execution_node_id = await self.temporal_integration.create_temporal_node(
            content=f"Tool Execution Started: {tool_name}",
            metadata={
                "tool_name": tool_name,
                "parameters": parameters,
                "start_time": start_time.isoformat(),
                "agent": "tool_agent"
            },
            session_id=session_id
        )
        
        try:
            # 1. Détermination du format optimal
            format_type = self._determine_format_type(tool_name, parameters)
            
            # 2. Formatage XML optimisé
            xml_call = self.xml_formatter.format_tool_call(tool_name, parameters, format_type)
            
            # 3. Exécution selon le type d'outil
            if self._is_mcp_tool(tool_name):
                result = await self._execute_mcp_tool(tool_name, parameters, session_id)
            else:
                result = await self._execute_local_tool(tool_name, parameters, session_id)
            
            # 4. Calcul du temps d'exécution
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # 5. Création du résultat
            tool_result = ToolResult(
                success=result.get('success', False),
                tool_name=tool_name,
                data=result.get('data', {}),
                execution_time=execution_time,
                error=result.get('error'),
                node_id=execution_node_id
            )
            
            # 6. Enregistrement du résultat
            result_node_id = await self.temporal_integration.create_temporal_node(
                content=f"Tool Execution Result: {tool_name}",
                metadata={
                    "tool_name": tool_name,
                    "success": tool_result.success,
                    "execution_time": execution_time,
                    "error": tool_result.error,
                    "agent": "tool_agent"
                },
                session_id=session_id
            )
            
            # 7. Création du lien temporel
            if execution_node_id and result_node_id:
                await self.temporal_integration.create_temporal_link(
                    execution_node_id, result_node_id, "tool_execution_result", session_id
                )
            
            return tool_result
            
        except Exception as e:
            # Gestion d'erreur
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            error_result = ToolResult(
                success=False,
                tool_name=tool_name,
                data={},
                execution_time=execution_time,
                error=str(e),
                node_id=execution_node_id
            )
            
            # Enregistrement de l'erreur
            await self.temporal_integration.create_temporal_node(
                content=f"Tool Execution Error: {tool_name}",
                metadata={
                    "tool_name": tool_name,
                    "error": str(e),
                    "execution_time": execution_time,
                    "agent": "tool_agent"
                },
                session_id=session_id
            )
            
            return error_result
    
    def _determine_format_type(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Détermine le type de formatage optimal."""
        # Heuristiques basées sur le nom de l'outil et les paramètres
        param_count = len(parameters)
        param_complexity = self._calculate_parameter_complexity(parameters)
        
        if param_count <= 2 and param_complexity <= 1:
            return "minimal"
        elif param_count >= 5 or param_complexity >= 3:
            return "detailed"
        elif "mcp" in tool_name.lower():
            return "standard"
        else:
            return "standard"
    
    def _calculate_parameter_complexity(self, parameters: Dict[str, Any]) -> int:
        """Calcule la complexité des paramètres."""
        complexity = 0
        
        for value in parameters.values():
            if isinstance(value, dict):
                complexity += 2
            elif isinstance(value, list):
                complexity += 1
            elif isinstance(value, str) and len(value) > 100:
                complexity += 1
            else:
                complexity += 0
        
        return complexity
    
    def _is_mcp_tool(self, tool_name: str) -> bool:
        """Détermine si un outil est un outil MCP."""
        if not self.mcp_manager:
            return False
        
        # Vérification dans le cache MCP
        mcp_tools = self.mcp_manager.tool_cache.keys()
        return any(tool_name in mcp_tool for mcp_tool in mcp_tools)
    
    async def _execute_mcp_tool(self, tool_name: str, parameters: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Exécute un outil MCP."""
        if not self.mcp_manager:
            return {
                "success": False,
                "error": "MCP Manager non disponible",
                "data": {}
            }
        
        try:
            # Recherche du serveur MCP pour cet outil
            server_name = self._find_mcp_server_for_tool(tool_name)
            if not server_name:
                return {
                    "success": False,
                    "error": f"Pas de serveur MCP trouvé pour {tool_name}",
                    "data": {}
                }
            
            # Exécution via MCP
            result = await self.mcp_manager.call_tool_with_memory(
                server_name, tool_name, parameters, session_id
            )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur MCP: {str(e)}",
                "data": {}
            }
    
    def _find_mcp_server_for_tool(self, tool_name: str) -> Optional[str]:
        """Trouve le serveur MCP pour un outil donné."""
        if not self.mcp_manager:
            return None
        
        # Recherche dans le cache d'outils
        for tool_key, tool_info in self.mcp_manager.tool_cache.items():
            if tool_info.name == tool_name:
                return tool_info.server_name
        
        return None
    
    async def _execute_local_tool(self, tool_name: str, parameters: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Exécute un outil local."""
        
        try:
            # Recherche de l'outil dans le registre local
            tool = self.tool_registry.get_tool(tool_name)
            if not tool:
                return {
                    "success": False,
                    "error": f"Outil non trouvé: {tool_name}",
                    "data": {}
                }
            
            # Exécution de l'outil
            result = await tool.execute(parameters)
            
            return {
                "success": True,
                "data": result,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur exécution locale: {str(e)}",
                "data": {}
            }
    
    async def execute_plan(self, plan: List[Dict[str, Any]], session_id: str) -> List[ToolResult]:
        """Exécute un plan d'outils."""
        results = []
        
        for step in plan:
            tool_name = step.get('tool_name')
            parameters = step.get('parameters', {})
            
            if tool_name:
                result = await self.execute_tool(tool_name, parameters, session_id)
                results.append(result)
            else:
                # Étape sans outil - création d'un résultat d'erreur
                error_result = ToolResult(
                    success=False,
                    tool_name="unknown",
                    data={},
                    execution_time=0.0,
                    error="Pas d'outil spécifié dans l'étape"
                )
                results.append(error_result)
        
        return results
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques des outils."""
        return {
            "local_tools_count": len(self.tool_registry.tools),
            "mcp_available": self.mcp_manager is not None,
            "mcp_tools_count": len(self.mcp_manager.tool_cache) if self.mcp_manager else 0,
            "xml_formatter_stats": self.xml_formatter.get_format_statistics()
        }


class V10ToolRegistry:
    """Registre d'outils locaux pour V10."""
    
    def __init__(self):
        """Initialise le registre d'outils."""
        self.tools = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Enregistre les outils par défaut."""
        self.tools = {
            "read_file": V10ReadFileTool(),
            "write_file": V10WriteFileTool(),
            "list_directory": V10ListDirectoryTool(),
            "execute_command": V10ExecuteCommandTool(),
            "code_analyzer": V10CodeAnalyzerTool(),
            "import_analyzer": V10ImportAnalyzerTool()
        }
    
    def get_tool(self, tool_name: str):
        """Récupère un outil par son nom."""
        return self.tools.get(tool_name)
    
    def register_tool(self, tool_name: str, tool):
        """Enregistre un nouvel outil."""
        self.tools[tool_name] = tool


class V10BaseTool:
    """Classe de base pour les outils V10."""
    
    def __init__(self, name: str):
        """Initialise l'outil de base."""
        self.name = name
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute l'outil."""
        raise NotImplementedError("Les sous-classes doivent implémenter execute")


class V10ReadFileTool(V10BaseTool):
    """Outil de lecture de fichier."""
    
    def __init__(self):
        super().__init__("read_file")
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Lit un fichier."""
        file_path = parameters.get('path', '')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "content": content,
                "file_path": file_path,
                "size": len(content)
            }
        except Exception as e:
            return {
                "error": str(e),
                "file_path": file_path
            }


class V10WriteFileTool(V10BaseTool):
    """Outil d'écriture de fichier."""
    
    def __init__(self):
        super().__init__("write_file")
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Écrit un fichier."""
        file_path = parameters.get('path', '')
        content = parameters.get('content', '')
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": file_path,
                "size": len(content)
            }
        except Exception as e:
            return {
                "error": str(e),
                "file_path": file_path
            }


class V10ListDirectoryTool(V10BaseTool):
    """Outil de liste de répertoire."""
    
    def __init__(self):
        super().__init__("list_directory")
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Liste le contenu d'un répertoire."""
        import os
        
        dir_path = parameters.get('path', '.')
        
        try:
            items = os.listdir(dir_path)
            return {
                "items": items,
                "directory": dir_path,
                "count": len(items)
            }
        except Exception as e:
            return {
                "error": str(e),
                "directory": dir_path
            }


class V10ExecuteCommandTool(V10BaseTool):
    """Outil d'exécution de commande."""
    
    def __init__(self):
        super().__init__("execute_command")
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une commande avec ProcessManager pour plus de sécurité/portabilité."""
        try:
            # Import tardif pour éviter dépendances globales
            from Core.ProcessManager.execute_command import (
                execute_command, ExecutionMode
            )
        except Exception as e:
            return {"success": False, "error": f"ProcessManager indisponible: {e}"}

        command = parameters.get('command', '')
        timeout = parameters.get('timeout', 30)
        cwd = parameters.get('cwd')
        env = parameters.get('env')

        try:
            result = execute_command(
                command=command,
                mode=ExecutionMode.BLOCKING,
                timeout=timeout,
                cwd=cwd,
                env=env,
            )

            return {
                "success": result.success,
                "stdout": getattr(result, 'stdout', ''),
                "stderr": getattr(result, 'stderr', ''),
                "return_code": getattr(result, 'return_code', None),
                "command": command,
                "execution_time": getattr(result, 'execution_time', None),
            }
        except Exception as e:
            return {"success": False, "error": str(e), "command": command}


class V10CodeAnalyzerTool(V10BaseTool):
    """Outil d'analyse de code."""
    
    def __init__(self):
        super().__init__("code_analyzer")
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse du code."""
        file_path = parameters.get('path', '')
        
        try:
            # Analyse simplifiée
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            return {
                "total_lines": len(lines),
                "non_empty_lines": len(non_empty_lines),
                "file_path": file_path,
                "size": len(content)
            }
        except Exception as e:
            return {
                "error": str(e),
                "file_path": file_path
            }


class V10ImportAnalyzerTool(V10BaseTool):
    """Outil d'analyse d'imports."""
    
    def __init__(self):
        super().__init__("import_analyzer")
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse des imports."""
        file_path = parameters.get('path', '')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Analyse simple des imports
            import_lines = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    import_lines.append(line)
            
            return {
                "imports": import_lines,
                "import_count": len(import_lines),
                "file_path": file_path
            }
        except Exception as e:
            return {
                "error": str(e),
                "file_path": file_path
            }
