# Core/Providers — Documentation basée sur le code (2025-08-09)

Ensemble de providers réutilisables: LLM, logging, MCP, threads auto-feeding, prompts.

## LLMProviders
- Interface: `LLMProvider(ABC)` avec méthodes asynchrones `generate_response`, `generate_text`, `stream_generate_text`, estimation tokens, validation taille, métadonnées et erreurs structurées.
- Providers:
  - `OpenAIProvider`: connexion OpenAI (chat/text), avec timeouts, gestion d’erreurs.
  - `LocalProvider`: moteur local via subprocess (ex: Ollama CLI), utile hors réseau.
  - `LocalProviderHTTP`: moteur local via HTTP (ex: Ollama serveur).
- Factory: `ProviderFactory`
  - Création (`create_provider`), création+validation (`create_and_validate_provider`), utilitaires de test.
- Conseils:
  - Isoler les mocks sous `LLMProviders/mocks/` et nommer explicitement (`Mock...`).
  - Centraliser les clés/secret via `Core/Config/secure_env_manager`.

## LoggingProviders
- Base `BaseLoggingProvider`: interface unifiée (info/warning/error/debug, structured/performance/statistics).
- Implémentations:
  - `ConsoleLoggingProvider`: logs colorés, niveau configurable.
  - `FileLoggingProvider`: fichiers (JSON/texte), rotation, compression.
  - `ImportAnalyzerLoggingProvider`: spécialisé pour l’analyse d’imports.
- Bonnes pratiques: utiliser les logs structurés pour l’observabilité et l’agrégation (JSON).

## MCP
- `V10McpManager`: découverte serveurs/outils, cache, appels avec enregistrement temporel et gestion d’erreurs (fallback explicite).
- Utilisation: idéal pour connecter des outils externes au runtime; prévoir un feature flag.

## UniversalAutoFeedingThread
- `BaseAutoFeedingThread` + `UniversalAutoFeedingThread`: infrastructure de thread introspectif (historique, logs, protocole d’actions) utilisable au-delà de V9.
- `template_registry`: fragments et registres (local/memory engine) pour prompts dynamiques.

## PromptTemplateProvider
- Providers de prompts (assemblage de fragments); utile pour standardiser prompts LLM.

## Exemples rapides
```python
from Core.Providers.LLMProviders.provider_factory import ProviderFactory
provider, validation = await ProviderFactory.create_and_validate_provider("local", model="qwen2.5:7b")
resp = await provider.generate_text("Bonjour")
```
