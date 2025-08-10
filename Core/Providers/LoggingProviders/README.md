# Core/Providers/LoggingProviders — Documentation basée sur le code (2025-08-09)

Providers de logging unifiés (console/fichier/spécialisé) pour une observabilité cohérente.

## Base (`base_logging_provider.py`)
- `BaseLoggingProvider(ABC)` : interface commune
  - `log_info/warning/error/debug(message, **metadata)`
  - `log_structured(data: dict, **metadata)`
  - `log_statistics(stats: dict, **metadata)`
  - `log_performance(operation: str, duration: float, **metadata)`

## Implémentations
- `ConsoleLoggingProvider` : logs colorés, format configurable (timestamp, level, nom du provider), niveaux.
- `FileLoggingProvider` : fichiers (JSON/texte), rotation, compression, dossiers dédiés.
- `ImportAnalyzerLoggingProvider` : méthodes spécialisées pour tracer des analyses d’import (début, résolutions, résumés, perf).

## Recommandations
- Utiliser des logs structurés (JSON) pour l’agrégation et les métriques.
- Paramétrer le niveau global par environnement (DEBUG en dev, INFO/ERROR en prod).
- Conserver un dossier `logs/` organisé par domaine (ex: `logs/imports_analysis/`).
