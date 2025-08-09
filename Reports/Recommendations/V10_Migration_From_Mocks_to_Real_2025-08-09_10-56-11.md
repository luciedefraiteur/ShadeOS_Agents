# V10 — Plan de migration des mocks vers usages réels (2025-08-09_10-56-11)

Objectif: passer d’un environnement mock (LLM, mémoire temporelle simulée, outils locaux only) à un environnement réel (providers LLM, TemporalFractalMemoryEngine, MCP optionnel) avec jalons et tests intermédiaires.

## Contexte initial
- LLM: décorateurs `@mock_llm_provider` renvoient des réponses déterministes pour les méthodes V10 (`analyze_task`, `create_execution_plan`, `synthesize_results`).
- Mémoire: `V10TemporalIntegration` fonctionne en simulation si `TemporalEngine` indisponible.
- Outils: exécution locale OK; MCP en mode simulation si non installé.

## Lignes directrices
- Feature flags & DI (Dependency Injection) pour tous les services (LLM, temporal engine, MCP): bascule facile mock ↔ réel par config.
- Tests par étapes: conserver un “chemin heureux” rapide; ajouter des suites d’intégration cibles au fur et à mesure (smoke → contract → stress).
- Observabilité: logs structurés + métriques (latences, taux succès) pour objectiver la bascule.

## Roadmap par domaine

### 1) LLM — Mocks → Providers réels
- P0: Abstraction prête (via `Core/Providers/LLMProviders`).
- Jalons:
  1. Injection provider (OpenAI ou Local HTTP) via config dans V10 (remplacer décorateurs mock au niveau des appels clés; conserver option mock pour tests rapides).
  2. Tests contractuels (unitaires) pour `LLMProvider`: réponses non vides, délais < X s, erreurs typées (`ErrorType`).
  3. Tests d’intégration V10: exécuter `handle_request` avec provider réel (petites requêtes), vérifier métriques/temps < SLA.
  4. Tests de résilience: timeouts réseau, rate limit → fallback local provider / retry backoff.
- Actions code:
  - Introduire un paramètre de config `LLM_MODE` (mock|openai|local_http|local_subprocess) + création via `ProviderFactory`.
  - Remplacer `@mock_llm_provider` par des wrappers qui délèguent au provider injecté (ou mock si flag "mock").
  - Ajouter un test d’intégration “LLM smoke” par mode (mock, local_http, openai) avec des prompts courts.

### 2) TemporalFractalMemoryEngine — Simulation → Engine réel
- P0: V10 utilise déjà un mode simulation (no-op mais traçant).
- Jalons:
  1. Intégration pilotée par flag `TEMPORAL_ENGINE=on/off` + configuration backend (`filesystem` par défaut).
  2. Tests smoke: `TemporalEngine(backend=filesystem)` → `create_temporal_memory` / `intelligent_search` basiques.
  3. Wire V10: remplacer appels simulés (`create_temporal_node`, `create_temporal_link`, `get_relevant_context`) par appels réels si flag actif; fallback sinon.
  4. Non-fonctionnels: mesurer l’overhead temporel et l’impact IO; tuner batch/flush si besoin.
- Actions code:
  - Dans `V10TemporalIntegration`, tenter l’instanciation du moteur si flag actif; exposer un état `temporal_engine_available`.
  - Ajouter tests d’intégration “V10 + TFME filesystem” (sans Neo4j) pour éviter coûts/dépendances.

### 3) MCP — Simulation → Hub réel (optionnel)
- Jalons:
  1. Découverte serveurs/validation basique (latence, liste d’outils) et enregistrement en mémoire temporelle.
  2. Exécution d’un outil trivial via MCP (args simples) + vérification résultat → smoke test.
  3. Mapping d’un outil V10 local à son équivalent MCP (si existant) + A/B (local vs MCP).
- Actions code:
  - Feature flag `MCP_ENABLED` + configuration hub.
  - Tests d’intégration tolérants (skippés si hub indisponible); garde en simulation sinon.

### 4) Outils locaux — ProcessManager
- Jalons:
  1. Migrer `V10ExecuteCommandTool` pour utiliser `Core/ProcessManager` (wrapper minimal) avec `timeout`/`cwd`/`env`.
  2. Tests unitaires (commande simple) + tests d’erreurs (timeout/command not found) + logs sécurisés.

### 5) Observabilité & Santé
- Ajouter un endpoint/fonction `get_health_snapshot()` (Assistant):
  - Providers actifs, temporal engine dispo, MCP dispo, nombre d’outils locaux/MCP, métriques dernières requêtes.
- Exporter métriques clés:
  - LLM: latences, erreurs par type, tokens (si dispo)
  - Temporal: nœuds/secondes, liens, échecs
  - Outils: taux succès, temps moyen

## Plan de tests intermédiaires

| Stade | Cible | Test | Critères de succès |
|---|---|---|---|
| S1 | Mocks only | `handle_request` (V10) sur 3 requêtes types | < 2s; 100% succès; traces simulées |
| S2 | LLM local_http | Même jeu + prompts courts réels | < 3s; pas d’erreurs réseau; contenu non vide |
| S3 | Temporal FS | `create_temporal_memory`/`intelligent_search` + V10 flag ON | Opérations retournent IDs; V10 enregistre nœuds |
| S4 | MCP smoke | Découverte serveurs + appel d’un outil trivial | Liste outils non vide; appel success=True |
| S5 | Mix | V10 avec LLM local + Temporal FS + (MCP off) | `handle_request` < 4s; traces réelles |
| S6 | OpenAI | V10 avec OpenAI minimal | Latence acceptable; coûts monitorés |

## Checklist de migration
- [ ] Flags de configuration (LLM_MODE, TEMPORAL_ENGINE, MCP_ENABLED)
- [ ] Injection de dépendances dans V10 (`assistant_v10`/`dev_agent`/`tool_agent`)
- [ ] Wrappers de compat pour remplacer les décorateurs mock
- [ ] Migration ProcessManager pour exec commandes
- [ ] Suites de tests S1→S6 (skip auto si deps non présentes)
- [ ] Health snapshot + métriques exportées

## Risques & mitigations
- Latence LLM: prévoir provider local HTTP par défaut; fallbacks robustes.
- Variabilité réponses: tests “contract” sur structure, pas le texte exact.
- IO Temporal: filesystem backend par défaut; batcher si besoin.
- Stabilité MCP: rester optionnel; dégrader proprement vers local.

## Deliverables
- Code: flags + DI + wrappers + migrations
- Tests: suites S1→S6
- Docs: mise à jour READMEs (V10/Providers/Temporal), guide d’activation par flags
