# Core/Config — Documentation basée sur le code (2025-08-09)

Gestion d’environnement sécurisé et configuration projet.

## `secure_env_manager.SecureEnvManager`
- Rôle: centraliser variables d’environnement, détecter l’OS/shell, adapter les commandes.
- Méthodes:
  - `get_secure_env_manager() -> SecureEnvManager`
  - `load_project_environment() -> Dict[str, str]` (charge .env/config projet si présent)
- Usage recommandé: fournir `env`/adapter commandes dans `Core/ProcessManager` et outils/agents.
