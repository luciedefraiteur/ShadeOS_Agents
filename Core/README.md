# Core — Index technique (2025-08-09)

Ce document sert d’index pour la base `Core/`. Chaque sous-dossier dispose de son README généré à partir du code effectif.

## Carte des modules
- `Core/Agents/` — Agents IA (V10 multi-agents, V9 auto-feeding, V8 legacy)
  - Lire: `Core/Agents/README.md`
- `Core/EditingSession/` — Outils d’édition sécurisés, registre d’outils
  - Lire: `Core/EditingSession/README.md`
- `Core/Providers/` — Providers LLM, logging, MCP, threads, prompts
  - Lire: `Core/Providers/README.md`
  - Sous-modules:
    - `Core/Providers/LLMProviders/README.md`
    - `Core/Providers/LoggingProviders/README.md`
    - `Core/Providers/MCP/README.md`
    - `Core/Providers/UniversalAutoFeedingThread/README.md`
    - `Core/Providers/PromptTemplateProvider/README.md`
- `Core/Partitioner/` — Partitionnement AST/Textuel, analyse d’imports
  - Lire: `Core/Partitioner/README.md`
- `Core/Parsers/` — Parsers Luciform et extraction de métadonnées
  - Lire: `Core/Parsers/README.md`
- `Core/ProcessManager/` — Exécution/gestion de processus
  - Lire: `Core/ProcessManager/README.md`
- `Core/Daemons/` — Daemons Legion AutoFeedingThread (V1/V2)
  - Lire: `Core/Daemons/README.md`
- `Core/Config/` — Environnement/config sécurisé
  - Lire: `Core/Config/README.md`
- `Core/IntrospectiveParser/` — Introspection (parser/thread/cache)
  - Lire: `Core/IntrospectiveParser/README.md`
- `Core/Templates/` — Fragments de prompts
  - Lire: `Core/Templates/README.md`
- `Core/Utils/` — Utilitaires divers
  - Lire: `Core/Utils/README.md`

## Points d’entrée fréquents (APIs)
- Partitionnement & analyse: `from Core.Partitioner import partition_file, detect_language`
- Processus: `from Core.ProcessManager import execute_command, ExecutionMode`
- Outils d’édition: `from Core.EditingSession.Tools.tool_registry import initialize_tool_registry`
- Providers LLM: `from Core.Providers.LLMProviders.provider_factory import ProviderFactory`
- Agents V10: `from Core.Agents.V10.assistant_v10 import V10Assistant`

## Bonnes pratiques transverses
- Exécution shell: utiliser `Core/ProcessManager` (pas `subprocess` direct).
- Mocks LLM: nom explicite (`Mock...`), isolés sous `mocks/`.
- Imports optionnels: protéger via `try/except` + messages clairs; fournir un fallback simulé si possible.
