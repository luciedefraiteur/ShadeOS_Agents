# Core/Providers/PromptTemplateProvider — Documentation basée sur le code (2025-08-09)

Providers de prompts composables à partir de fragments.

## Composants (`prompt_template_provider.py`)
- `PromptTemplate` : unité de prompt (contenu, métadonnées).
- `ReconstructedPrompt` : résultat assemblé avec contexte.
- `BasePromptTemplateProvider(ABC)` : interface commune.
- `LegionPromptTemplateProvider`, `V9PromptTemplateProvider` : implémentations concrètes par domaine.
- `PromptTemplateVisualizer` : visualisation/export des prompts assemblés.

## Usage
- Charger des fragments depuis `Core/Templates/` et composer un prompt adapté au contexte (utilisateur, état du projet, historique…).
- Optionnel: persister/visualiser les prompts pour audit et itérations.
