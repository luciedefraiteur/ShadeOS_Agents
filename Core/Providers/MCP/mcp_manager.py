#!/usr/bin/env python3
"""
⛧ V10 MCP Manager ⛧
Alma's MCP Management with Temporal Memory for V10

Gestionnaire MCP avec mémoire temporelle pour l'Assistant V10.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime

try:
    from mcp import McpHub, McpServer, McpTool, McpResource, McpToolCallResponse
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️ MCP non disponible - Mode simulation activé")


@dataclass
class McpServerInfo:
    """Informations sur un serveur MCP."""
    name: str
    description: Optional[str]
    tools_count: int
    resources_count: int
    last_seen: datetime
    status: str = "active"


@dataclass
class McpToolInfo:
    """Informations sur un outil MCP."""
    name: str
    description: Optional[str]
    parameters: Dict[str, Any]
    server_name: str
    last_used: Optional[datetime] = None


class V10McpErrorHandler:
    """Gestionnaire d'erreurs MCP pour V10."""
    
    def __init__(self, temporal_integration):
        """Initialise le gestionnaire d'erreurs."""
        self.temporal_integration = temporal_integration
        self.error_count = 0
        self.recovery_attempts = {}
    
    async def handle_mcp_error(self, error: Exception, server_name: str, tool_name: str, session_id: str) -> Dict[str, Any]:
        """Gère une erreur MCP avec fallback."""
        error_key = f"{server_name}:{tool_name}"
        
        # Enregistrement temporel de l'erreur
        await self.temporal_integration.create_temporal_node(
            content=f"MCP Error: {error}",
            metadata={
                "error_type": type(error).__name__,
                "server_name": server_name,
                "tool_name": tool_name,
                "error_message": str(error),
                "timestamp": datetime.now().isoformat()
            },
            session_id=session_id
        )
        
        # Comptage des erreurs
        self.error_count += 1
        if error_key not in self.recovery_attempts:
            self.recovery_attempts[error_key] = 0
        self.recovery_attempts[error_key] += 1
        
        # Stratégie de fallback
        fallback_result = await self._create_fallback_response(server_name, tool_name, error)
        
        return fallback_result
    
    async def _create_fallback_response(self, server_name: str, tool_name: str, error: Exception) -> Dict[str, Any]:
        """Crée une réponse de fallback."""
        return {
            "success": False,
            "error": str(error),
            "fallback": True,
            "server_name": server_name,
            "tool_name": tool_name,
            "suggestion": "Utilisez un outil local équivalent"
        }


class V10McpManager:
    """Gestionnaire MCP avec mémoire temporelle pour V10."""
    
    def __init__(self, temporal_integration):
        """Initialise le gestionnaire MCP."""
        self.temporal_integration = temporal_integration
        self.mcp_hub = None
        self.tool_cache = {}
        self.server_cache = {}
        self.error_handler = V10McpErrorHandler(temporal_integration)
        
        if MCP_AVAILABLE:
            try:
                self.mcp_hub = McpHub()
                print("✅ MCP Hub initialisé")
            except Exception as e:
                print(f"⚠️ Erreur initialisation MCP Hub: {e}")
        else:
            print("⚠️ Mode simulation MCP activé")
    
    async def discover_servers(self, session_id: str) -> List[McpServerInfo]:
        """Découvre les serveurs MCP avec enregistrement temporel."""
        if not self.mcp_hub:
            # Mode simulation
            simulated_servers = [
                McpServerInfo("sim_server_1", "Serveur simulé 1", 5, 2, datetime.now()),
                McpServerInfo("sim_server_2", "Serveur simulé 2", 3, 1, datetime.now())
            ]
            
            for server in simulated_servers:
                await self.temporal_integration.create_temporal_node(
                    content=f"MCP Server Discovered: {server.name}",
                    metadata={
                        "server_name": server.name,
                        "description": server.description,
                        "tools_count": server.tools_count,
                        "resources_count": server.resources_count,
                        "simulated": True
                    },
                    session_id=session_id
                )
            
            return simulated_servers
        
        try:
            servers = await self.mcp_hub.get_servers()
            server_infos = []
            
            for server in servers:
                # Création des informations serveur
                server_info = McpServerInfo(
                    name=server.name,
                    description=getattr(server, 'description', None),
                    tools_count=len(server.tools or []),
                    resources_count=len(server.resources or []),
                    last_seen=datetime.now()
                )
                
                server_infos.append(server_info)
                self.server_cache[server.name] = server_info
                
                # Enregistrement temporel
                await self.temporal_integration.create_temporal_node(
                    content=f"MCP Server Discovered: {server.name}",
                    metadata={
                        "server_name": server.name,
                        "description": server_info.description,
                        "tools_count": server_info.tools_count,
                        "resources_count": server_info.resources_count,
                        "simulated": False
                    },
                    session_id=session_id
                )
            
            return server_infos
            
        except Exception as e:
            print(f"❌ Erreur découverte serveurs MCP: {e}")
            return []
    
    async def get_server_tools(self, server_name: str, session_id: str) -> List[McpToolInfo]:
        """Récupère les outils d'un serveur MCP."""
        if not self.mcp_hub:
            # Mode simulation
            simulated_tools = [
                McpToolInfo("read_file", "Lecture de fichier", {"path": "string"}, server_name),
                McpToolInfo("write_file", "Écriture de fichier", {"path": "string", "content": "string"}, server_name)
            ]
            
            for tool in simulated_tools:
                await self.temporal_integration.create_temporal_node(
                    content=f"MCP Tool: {tool.name}",
                    metadata={
                        "server_name": server_name,
                        "tool_name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                        "simulated": True
                    },
                    session_id=session_id
                )
            
            return simulated_tools
        
        try:
            server = await self.mcp_hub.get_server(server_name)
            if not server or not server.tools:
                return []
            
            tools = []
            for tool in server.tools:
                tool_info = McpToolInfo(
                    name=tool.name,
                    description=getattr(tool, 'description', None),
                    parameters=getattr(tool, 'parameters', {}),
                    server_name=server_name
                )
                
                tools.append(tool_info)
                self.tool_cache[f"{server_name}:{tool.name}"] = tool_info
                
                # Enregistrement temporel
                await self.temporal_integration.create_temporal_node(
                    content=f"MCP Tool: {tool.name}",
                    metadata={
                        "server_name": server_name,
                        "tool_name": tool.name,
                        "description": tool_info.description,
                        "parameters": tool_info.parameters,
                        "simulated": False
                    },
                    session_id=session_id
                )
            
            return tools
            
        except Exception as e:
            print(f"❌ Erreur récupération outils serveur {server_name}: {e}")
            return []
    
    async def call_tool_with_memory(self, server_name: str, tool_name: str, arguments: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Appelle un outil MCP avec mémoire temporelle."""
        
        # Enregistrement de l'appel
        call_node_id = await self.temporal_integration.create_temporal_node(
            content=f"MCP Call: {server_name}.{tool_name}",
            metadata={
                "server_name": server_name,
                "tool_name": tool_name,
                "arguments": arguments,
                "timestamp": datetime.now().isoformat()
            },
            session_id=session_id
        )
        
        try:
            if not self.mcp_hub:
                # Mode simulation
                await asyncio.sleep(0.1)  # Simulation de latence
                
                simulated_response = {
                    "success": True,
                    "data": f"Simulated response for {tool_name}",
                    "server_name": server_name,
                    "tool_name": tool_name,
                    "simulated": True
                }
                
                # Enregistrement de la réponse simulée
                response_node_id = await self.temporal_integration.create_temporal_node(
                    content=f"MCP Response: {simulated_response['data']}",
                    metadata={
                        "server_name": server_name,
                        "tool_name": tool_name,
                        "response": simulated_response,
                        "success": True,
                        "simulated": True
                    },
                    session_id=session_id
                )
                
                # Création du lien temporel
                if call_node_id and response_node_id:
                    await self.temporal_integration.create_temporal_link(
                        call_node_id, response_node_id, "mcp_call_response", session_id
                    )
                
                return simulated_response
            
            # Appel réel MCP
            response = await self.mcp_hub.callTool(server_name, tool_name, arguments)
            
            # Enregistrement de la réponse
            response_node_id = await self.temporal_integration.create_temporal_node(
                content=f"MCP Response: {response}",
                metadata={
                    "server_name": server_name,
                    "tool_name": tool_name,
                    "response": response.dict() if hasattr(response, 'dict') else str(response),
                    "success": not getattr(response, 'isError', False),
                    "simulated": False
                },
                session_id=session_id
            )
            
            # Création du lien temporel
            if call_node_id and response_node_id:
                await self.temporal_integration.create_temporal_link(
                    call_node_id, response_node_id, "mcp_call_response", session_id
                )
            
            # Mise à jour du cache
            tool_key = f"{server_name}:{tool_name}"
            if tool_key in self.tool_cache:
                self.tool_cache[tool_key].last_used = datetime.now()
            
            return {
                "success": not getattr(response, 'isError', False),
                "data": response.dict() if hasattr(response, 'dict') else str(response),
                "server_name": server_name,
                "tool_name": tool_name,
                "simulated": False
            }
            
        except Exception as e:
            # Gestion d'erreur avec fallback
            return await self.error_handler.handle_mcp_error(e, server_name, tool_name, session_id)
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache."""
        return {
            "tool_cache_size": len(self.tool_cache),
            "server_cache_size": len(self.server_cache),
            "mcp_available": MCP_AVAILABLE,
            "error_count": self.error_handler.error_count
        }
    
    async def cleanup_cache(self) -> int:
        """Nettoie le cache expiré."""
        current_time = datetime.now()
        expired_tools = 0
        
        # Nettoyage des outils non utilisés depuis plus d'1 heure
        for tool_key, tool_info in list(self.tool_cache.items()):
            if tool_info.last_used and (current_time - tool_info.last_used).seconds > 3600:
                del self.tool_cache[tool_key]
                expired_tools += 1
        
        return expired_tools
