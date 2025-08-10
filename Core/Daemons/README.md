# Core/Daemons — Documentation basée sur le code (2025-08-09)

Daemons d’automatisation (LegionAutoFeedingThread).

## V1
- `LegionAutoFeedingThread`
  - Composants: `DaemonRole`, `DaemonHierarchy`, `DaemonMessage`, `DaemonConversation`, `DaemonMetaVirtualLayer`.
  - Rôle: boucle daemon avec hiérarchie et messages typés; intégration possible avec mémoire temporelle et couches virtuelles.

## V2
- `LegionAutoFeedingThread(BaseAutoFeedingThread)`
  - Hérite de l’infrastructure universelle (historique, logs, protocole d’actions).
  - Améliorations de performance/stabilité par rapport à V1.

## Notes d’usage
- Préférer V2 pour nouveaux développements.
- Injecter un provider LLM et un moteur de mémoire si nécessaire (via `Core/Providers`).
