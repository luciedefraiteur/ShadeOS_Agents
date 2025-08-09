# Core/Providers/LLMProviders — Documentation basée sur le code (2025-08-09)

Providers LLM (abstraction + implémentations locales/OpenAI) avec factory.

## Interfaces & types (`llm_provider.py`)
- `ProviderType(Enum)`: openai, local, local_http, etc.
- `ErrorType(Enum)`: classification standard des erreurs (connexion, auth, quota, rate limit, invalid request, unknown).
- `ProviderStatus`: état d’un provider (latence, santé, quotas…)
- `LLMResponse`: réponse typée (contenu, tokens, temps, erreurs…)
- `ValidationResult`: résultat de validation (valid, error, capabilities…)
- `LLMProvider(ABC)`: interface
  - `async generate_response(prompt: str, **kwargs) -> LLMResponse`
  - `async generate_text(...)`, `async stream_generate_text(...)` (si supporté)
  - Méthodes utilitaires: estimation tokens, validation taille, infos provider, erreurs.

## Implémentations
- `OpenAIProvider(LLMProvider)`: via API OpenAI (chat/text). Gère timeouts, erreurs, streaming (si dispo), estimation.
- `LocalProvider(LLMProvider)`: via subprocess (ex: Ollama CLI). Adapté aux environnements sans réseau.
- `LocalProviderHTTP(LLMProvider)`: via HTTP (ex: Ollama serveur). Latence faible, local.

## Factory (`provider_factory.py`)
- `ProviderFactory.create_provider(provider_type, **config)`
- `await ProviderFactory.create_and_validate_provider(provider_type, **config)`
  - Retourne l’instance + `ValidationResult` (tests de santé rapides).

## Bonnes pratiques
- Placer les mocks sous `LLMProviders/mocks/` (noms explicites: `MockLLMProvider`, `Fake...`).
- Centraliser les secrets (API keys) via `Core/Config/secure_env_manager`.
- Définir un `timeout` et un `model` explicites à la création; prévoir un fallback local si OpenAI indisponible.

## Exemples
```python
from Core.Providers.LLMProviders.provider_factory import ProviderFactory
provider, validation = await ProviderFactory.create_and_validate_provider("local_http", model="qwen2.5:7b")
resp = await provider.generate_text("Explique le partitionnement AST")
print(resp.content)
```
