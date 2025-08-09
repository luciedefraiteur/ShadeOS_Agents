# Core/Providers/UniversalAutoFeedingThread — Documentation basée sur le code (2025-08-09)

Infrastructure de thread auto-feeding/introspectif générique, réutilisable (ex: V9).

## Composants
- `BaseAutoFeedingThread(ABC)` :
  - Modèle d’historique (messages), protocole d’actions, hooks de logging.
  - Logger de base: `BaseAutoFeedingThreadLogger`.
- `UniversalAutoFeedingThread` :
  - Implémentation standard d’un thread auto-feeding (ajout messages user/assistant, synthèses, métriques).
- `template_registry` :
  - `BaseTemplateRegistry` + registres concrets (`LocalTemplateRegistry`, `MemoryEngineTemplateRegistry`) pour fragments de prompts.
  - `TemplateFragment`, `FragmentMetadata`.

## Usage
- Fournir un provider LLM (via `Core/Providers/LLMProviders`) et brancher un registre de fragments (`Core/Templates`).
- Utilisé par `Core/Agents/V9/V9_AutoFeedingThreadAgent.py` pour piloter un workflow de construction/debug.
