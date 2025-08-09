# Core/ProcessManager — Documentation basée sur le code (2025-08-09)

Gestion centralisée de l’exécution de commandes et du cycle de vie des processus.

## Principes
- Éviter `subprocess` direct ailleurs dans le code; utiliser ces APIs pour uniformiser sécurité, timeouts, logs et portabilité.
- Modes adaptés: bloquant, background, interactif, monitoré.

## API
- `execute_command(command, mode=ExecutionMode.BLOCKING, **kwargs) -> ExecutionResult`
  - Paramètres utiles: `cwd`, `env`, `timeout`, callbacks (`on_output`, `on_error`, `on_complete`), `input_data`.
- Inspection et contrôle:
  - `get_active_processes()`, `get_process_status(pid)`
  - `communicate_with_process(pid, data)`
  - `terminate_process(pid, force=False)`, `cleanup_finished_processes()`
- Sous-modules spécialisés:
  - `process_reader`: lecture sortie/processus, statistiques
  - `process_writer`: écriture/signaux (interrupt/terminate), communication
  - `process_killer`: arrêt propre/forcé, arbre de processus, par nom
  - `process_manager_tools`: wrappers orientés « outils »

## Exemples
```python
from Core.ProcessManager import execute_command, ExecutionMode
res = execute_command("ls -la", mode=ExecutionMode.BLOCKING, timeout=10)
print(res.success, res.return_code)
```

## Bonnes pratiques
- Toujours définir un `timeout` raisonnable; fournir `cwd`/`env` si contexte spécifique.
- Logger via Providers/Logging si besoin de traçabilité.
