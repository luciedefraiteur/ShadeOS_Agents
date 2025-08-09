# Core/Partitioner — Documentation basée sur le code (2025-08-09)

Partitionnement de fichiers, analyse d’imports et utilitaires de localisation.

## APIs publiques
- `partition_file(file_path, **kwargs) -> PartitionResult`
- `detect_language(file_path) -> str`
- `get_supported_languages() -> List[str]`

## Partitionneurs
- `PythonASTPartitioner`: parsing AST Python natif, enrichi (décorateurs, docstrings, complexité, hiérarchie de classe, signatures).
- `TreeSitterPartitioner`: support multi-langages via Tree-sitter (si installé).
- `BaseASTPartitioner`: protocole commun (parse/extract/mapping vers `PartitionBlock`).

## Fallback strategies
- `RegexPartitioner`, `TextualPartitioner`, `EmergencyPartitioner`: maintiennent la couverture quand AST échoue (fichiers corrompus/syntaxe non standard).

## Schémas / Tracking / Erreurs
- `PartitionLocation` (coordonnées précises), `PartitionBlock` (blocs), `PartitionResult` (résultat global), exceptions dédiées.
- `LocationTracker`: offsets, conversions ligne↔offset, fusion/overlap, contexte autour d’une location.
- `error_logger`: warnings/errors structurés; utile pour télémétrie.

## Analyse d’imports (nouvelle génération)
- `ImportAnalyzer` (production) et `analyzers.ImportAnalyzer` (lib):
  - Extraction AST avec fallback, classification sophistiquée (builtin/stdlib/external), détection modules locaux auto, graphes de dépendances, cycles, rapport Markdown.
  - Résolution hybride (résolveur + simple), cache d’analyses, gestion des dépendances brisées.

## Exemples
```python
from Core.Partitioner import partition_file, detect_language
lang = detect_language("src/main.py")
result = partition_file("src/main.py", language=lang)
for block in result.blocks:
    print(block.type, block.location.start_line)
```

## Bonnes pratiques
- Tenter AST d’abord; basculer vers fallback en cas d’échec.
- Conserver/propager `PartitionLocation` pour toute opération d’édition ciblée.
- Journaliser via `handlers.error_logger` pour faciliter le debug et l’observabilité.
