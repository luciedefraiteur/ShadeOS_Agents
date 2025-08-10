# Core/IntrospectiveParser — Documentation basée sur le code (2025-08-09)

Parsers et threads d’introspection (raisonnement et contexte).

## Composants
- `IntelligentIntrospectiveParser`
  - Représentations: `IntrospectiveElement`, `IntrospectiveMessage`
  - Objectif: analyser des échanges/états pour en extraire un contexte exploitable.
- `IntelligentCache`
  - Éléments: `CacheEntry`, `ContextSignature`
  - Objectif: mémoriser des contextes/signatures pour accélérer des analyses récurrentes.
- `UniversalIntrospectiveThread`
  - Métriques: `ThreadMetrics`
  - Objectif: fil d’introspection générique (traces, synthèse, KPIs).

## Intégrations
- Peut être utilisé par des agents (V9/V10) pour enrichir le raisonnement hors-LMM.
