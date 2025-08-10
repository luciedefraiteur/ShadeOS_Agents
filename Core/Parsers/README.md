# Core/Parsers — Documentation basée sur le code (2025-08-09)

Parsers dédiés aux fichiers Luciform et extraction de métadonnées d’outils.

## Modules
- `luciform_parser.parse_luciform(path) -> dict`
  - Parse un fichier `.luciform` en AST léger (préserve structure/texte/commentaires).
  - Usage: alimenter un registre d’outils à partir de templates Luciform.
- `luciform_tool_metadata_parser.LuciformToolMetadataParser`
  - Extrait les champs clés d’un outil (id, pacte/type-intent-level, invocation/params requis-optionnels-returns, essence/keywords-context-layer).
  - Fournit validation et statistiques sur des répertoires de luciforms.

## Exemple
```python
from Core.Parsers.luciform_parser import parse_luciform
ast = parse_luciform("Core/EditingSession/Tools/safe_write_file_content.luciform")
```

## Notes
- En cas d’échec parsing, prévoir un fallback regex externe au besoin.
- Les métadonnées extraites sont utilisées par les registres d’outils (EditingSession) pour générer des schémas/paramètres.
