# Core/EditingSession — Documentation basée sur le code (2025-08-09)

Système d’édition sécurisé avec registre d’outils et utilitaires d’analyse/recherche.

## Quand utiliser EditingSession
- Lire/écrire des fichiers avec garde-fous (backups, validations)
- Chercher/diagnostiquer du code (stats, diff, regex, analyse simple)
- Automatiser des transformations de projet (rename, replace project-wide)
- Orchestrer des outils via un registre commun (standard/optimisé)

## Composants

### Registres et invocation
- `ToolRegistry`: charge les fonctions d’outils, gère la résolution par id, propose une interface simple (`invoke_tool`) et des utilitaires.
- `OptimizedToolRegistry`: ajoute cache d’analyse d’imports, gestion des dépendances brisées (via `Core/Partitioner`) et triggers d’analyse.
- `ToolInvoker`: couche d’exécution avec historique, formatage des retours, et possibilité de formater les réponses pour un SDK externe.
- `ToolSearchEngine`: recherche des outils par mots-clés/métadonnées.

### Outils sécurisés (écriture)
- `safe_write_file_content`, `safe_overwrite_file`, `safe_insert_text_at_line`, `safe_delete_lines`, `safe_append_to_file`, `safe_create_file`, `safe_create_directory`, `safe_delete_directory`.
- Principes: validations d’entrée, backups optionnels, opérations ciblées (ligne ou texte), messages d’erreur explicites.

### Lecture/recherche/diagnostic
- Lecture: `safe_read_file_content`, `read_file_content`, `read_file_content_naked`, `read_file_lines`, `read_file_chars`.
- Recherche: `regex_search_file`, `find_text_in_project`, `scry_for_text`, `locate_text_sigils`.
- Analyse: `code_analyzer` (statistiques simples), `file_stats`, `file_diff` (diff contextuel et formatage), `md_hierarchy_basic` (organisation Markdown).

### Templating
- `TemplateEngine` + helpers `generate_from_template`, `create_template_from_file` — pour générer des fichiers boilerplate.

## Bonnes pratiques
- Toujours préférer les variantes `safe_*` pour éviter les corruptions de fichiers.
- Pour des opérations shell/processus, déléguer à `Core/ProcessManager` plutôt que d’appeler `subprocess` directement.
- En projets volumineux: utiliser `OptimizedToolRegistry` pour bénéficier du cache d’analyse d’imports et de la résilience.

## Exemples

### Écriture sécurisée
```python
from Core.EditingSession.Tools.safe_write_file_content import safe_write_file_content
ok = safe_write_file_content("src/new.py", "print('hello')")
```

### Recherche regex avec contexte
```python
from Core.EditingSession.Tools.regex_search_file import regex_search_file
results = regex_search_file("src/main.py", r"def\s+\w+", context_before=2, context_after=2)
```

### Invocation via registre
```python
from Core.EditingSession.Tools.tool_registry import initialize_tool_registry
from TemporalFractalMemoryEngine.core.temporal_engine import TemporalEngine

registry = initialize_tool_registry(TemporalEngine())
result = registry.invoke_tool("safe_create_file", path="docs/README.md")
```

## Intégrations
- `Core/Partitioner`: pour analyses avancées (imports, AST, tracking de localisation)
- `TemporalFractalMemoryEngine`: pour persister l’historique si nécessaire
- `Core/Agents`: les agents V9/V10 peuvent orchestrer ces outils
