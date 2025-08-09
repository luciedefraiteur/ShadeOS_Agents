# Core/Providers/MCP — Documentation basée sur le code (2025-08-09)

Gestionnaire MCP (Model Context Protocol) avec mémoire temporelle et fallback simulation.

## Composants (`mcp_manager.py`)
- `McpServerInfo`, `McpToolInfo` : métadonnées serveur/outil (nom, description, paramètres, derniers usages).
- `V10McpErrorHandler` : gestion d’erreurs MCP (journalisation via mémoire temporelle, compteur d’erreurs, suggestions de fallback).
- `V10McpManager` :
  - Découverte de serveurs (`discover_servers`) avec traces temporelles.
  - Récupération d’outils (`get_server_tools`) + cache.
  - Appel d’outil (`call_tool_with_memory`) : enregistre appel et réponse en mémoire temporelle; crée des liens temporels; fallback simulé si MCP indisponible.
  - Nettoyage de cache, statistiques.

## Bonnes pratiques
- Activer/désactiver MCP via flag de configuration pour les environnements sans hub MCP.
- Vérifier la cohérence des noms d’outils côté MCP vs agent local.
- Surveiller `error_count` et implémenter des bascules vers des outils locaux en cas d’instabilité.
