# Core/Agents — Documentation basée sur le code (2025-08-09)

Ce module regroupe les assistants (agents) par version. Les descriptions ci-dessous sont construites à partir du code Python actuel.

## V10 — Assistant multi-agents avec mémoire temporelle (en cours)

- Orchestration: `V10Assistant` (fichier `V10/assistant_v10.py`)
  - Coordonne un cycle complet: enregistrement de la requête → analyse → plan → exécution d’outils → synthèse → réponse + traces temporelles.
  - Expose `initialize(user_id)`, `handle_request(user_request)`, métriques et cleanup.
- Raisonnement/planification: `V10DevAgent` (fichier `V10/dev_agent.py`)
  - Décore ses méthodes avec un mock LLM (voir plus bas) pour fournir des sorties déterministes en attendant un provider réel.
  - Construit `TaskAnalysis` et `TaskPlan`, exécute le plan via l’agent d’outils et synthétise les résultats.
- Exécution d’outils: `V10ToolAgent` (fichier `V10/tool_agent.py`)
  - Exécute des outils locaux d’un registre (`V10ToolRegistry`) ou via MCP s’il est disponible.
  - Formate les appels et réponses (XML) via `V10XMLFormatter`.
  - Outils locaux fournis: lecture/écriture de fichiers, listage de répertoire, exécution de commande (voir Sécurité), analyse simple de code/imports.
- Mémoire temporelle (session + traces): `V10TemporalIntegration` (fichier `V10/temporal_integration.py`)
  - Fournit des sessions (`TemporalSession`), la création de nœuds/lien temporels et un mode simulation quand `TemporalFractalMemoryEngine` n’est pas importable.
- Gestion des gros fichiers: `V10FileIntelligenceEngine` (fichier `V10/file_intelligence_engine.py`)
  - Stratégies adaptatives selon taille/type (full/chunked/streaming/summarized) + résumeur et métadonnées enrichies.
- Outils spécialisés: `V10/specialized_tools.py`
  - Outils ligne-par-ligne, résumé de chunks/sections, analyse de structure, indexation, détection de scopes.
  - Note: l’outil "read_chunks_until_scope" embarque un `MockLLMProvider` pour le développement. Conserver un nom explicite (« Mock ») et un emplacement dédié aux mocks lors d’une refactorisation.
- Formatage XML: `V10XMLFormatter` (fichier `V10/xml_formatter.py`)
  - Règles d’optimisation de la verbosité (minimal/standard/detailed/compact) pour les échanges outillés.
- Décorateur LLM (mock): `V10/llm_provider_decorator.py`
  - `@mock_llm_provider` encapsule les méthodes pour retourner des textes simulés (tests/démo). Prévu pour être remplacé par un vrai provider (OpenAI/Ollama via `Core/Providers/LLMProviders`).

### Exemple d’usage (V10)

```python
import asyncio
from Core.Agents.V10.assistant_v10 import create_v10_assistant, handle_v10_request

async def run():
    assistant = await create_v10_assistant("user_123")
    resp = await handle_v10_request(assistant, "Analyse le fichier main.py et liste les imports")
    print(resp.success, resp.message, resp.execution_time)
    await assistant.cleanup_session()

asyncio.run(run())
```

### Sécurité et bonnes pratiques (V10)
- L’outil `execute_command` de `V10ToolAgent` utilise `subprocess` avec `shell=True`. Préférer, quand possible, les outils `Core/ProcessManager` pour limiter les risques, valider les commandes et centraliser la politique de temps d’exécution.
- Conserver les mocks LLM avec un nom explicite (ex. `MockLLMProvider`) et les isoler dans un sous-dossier `mocks/` pour éviter toute ambiguïté en production.
- Certaines classes attendues par les tests historiques ne correspondent pas exactement aux noms actuels (ex. `V10ToolResult` vs `ToolResult`). Harmoniser tests ou exposer alias selon la stratégie retenue.

### Extension (V10)
- Ajouter un outil local:
  1) Créer une sous-classe de `V10BaseTool` avec `async def execute(self, parameters)`.
  2) L’enregistrer dans `V10ToolRegistry._register_default_tools()`.
- Brancher un provider LLM réel:
  - Remplacer `@mock_llm_provider` par un décorateur qui appelle `Core/Providers/LLMProviders`.
- Activer MCP:
  - Vérifier `Core/Providers/MCP/mcp_manager.py` et la disponibilité des serveurs MCP; `V10ToolAgent` basculera en MCP s’il détecte l’outil.

## V9 — Auto-Feeding Thread (stable)

- Fichier: `V9/V9_AutoFeedingThreadAgent.py`
- Agent `AutoFeedingThreadAgent`: boucle itérative guidée par un LLM (via `ProviderFactory`) avec un protocole d’actions textuel (LAYER/TOOL/INTROSPECT/CONTINUE/DONE).
- Intégration `TemporalFractalMemoryEngine` (workspace/git layers), registre d’outils d’édition, logs JSONL détaillés.

### Exemple rapide (V9)

```python
# Voir la fonction test_auto_feeding_thread_agent() dans V9_AutoFeedingThreadAgent.py
```

## V8 — Legacy

- Fichier: `V8/V7_safe.py` — Assistant local V7 (logger + assistant) conservé pour compat.

---

## Intégration transversale
- Mémoire temporelle: V10 via intégration simulée; V9 direct.
- Outils d’édition: préférer `Core/EditingSession/Tools`.
- Exécution shell/processus: `Core/ProcessManager`.
- Providers LLM: via `Core/Providers/LLMProviders` (OpenAI/local). Conserver des mocks explicites.
