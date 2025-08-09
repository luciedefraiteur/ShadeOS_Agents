# Core/Templates — Documentation basée sur les fichiers (2025-08-09)

Fragments et registres de prompts utilisés par les threads/agents.

## Organisation
- `fragments/`
  - `general/BaseAutoFeedingThread`: squelette générique (headers, base prompts, logging)
  - `v9/V9AutoFeedingThreadAgent`: prompts spécifiques V9 (system/execution)
  - `legion/LegionAutoFeedingThread`: prompts pour daemons Legion (orchestration, analyses, mémoires)
- Registres
  - `local_registry.json`: index local des fragments
  - `fragments_config.json`: configuration des fragments

## Usage
- Consommés par `Core/Providers/PromptTemplateProvider` et `UniversalAutoFeedingThread` pour assembler des prompts dynamiquement selon le contexte.
- Ajouter un nouveau fragment: créer le `.prompt` et mettre à jour le registre.
