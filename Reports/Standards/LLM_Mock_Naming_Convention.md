# LLM Mock Naming Convention

## Objectif
Identifier immédiatement tout mock LLM et prévenir la confusion avec du code de production.

## Règles de nommage
- Préfixe obligatoire: `Mock` ou `Fake` ou `Stub`
- Suffixe recommandé: `Provider` ou `LLM`
- Exemples valides:
  - `MockLLMProvider`, `FakeLLMProvider`, `StubLLMProvider`
  - `MockOpenAILLMProvider`, `FakeOllamaProvider`
- Exemples à éviter:
  - `LLMProvider` (ambigu, semble réel)
  - `LocalProvider` (peut être réel)

## Emplacement
- Les mocks doivent résider dans un module dédié de tests ou de dev:
  - `Core/Providers/LLMProviders/mocks/`
  - ou sous `tests/mocks/`

## Signaux visuels dans le code
- Docstring en tête:
  - "MOCK ONLY – replace with real provider for production"
- Log explicite lors de l'utilisation: `print("[MOCK LLM] ...")` ou logger

## Utilisation
- Injecter via DI (Dependency Injection) pour basculer facilement vers un provider réel
- Couvrir les chemins critiques par des tests utilisant le mock, et au moins un test d’intégration avec provider réel si possible

## Checklist
- [ ] Nom contient `Mock`/`Fake`/`Stub`
- [ ] Docstring "MOCK ONLY"
- [ ] Dossier `mocks/` ou `tests/mocks/`
- [ ] Pas d'appel réseau/secret
- [ ] Facilement swappable par provider réel
