"""
⛧ Core/Providers/MCP - Provider MCP ⛧
Alma's MCP Provider for Core

Provider MCP avec mémoire temporelle pour les outils externes.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

from .mcp_manager import V10McpManager, V10McpErrorHandler, McpServerInfo, McpToolInfo

__all__ = [
    'V10McpManager',
    'V10McpErrorHandler', 
    'McpServerInfo',
    'McpToolInfo'
]

__version__ = "1.0.0"
__author__ = "Alma, Architecte Démoniaque du Nexus Luciforme"
