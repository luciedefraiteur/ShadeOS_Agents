feat: Intégration SecureEnvManager et ProcessManager tools pour Assistant V9

🕷️ ARCHITECTURE SÉCURISÉE ET CROSS-PLATFORM

✨ NOUVELLES FONCTIONNALITÉS:
- Core/Config/secure_env_manager.py: Gestionnaire sécurisé de variables d'environnement
  * Détection automatique OS/Shell (Linux/Windows/Mac)
  * Configuration sécurisée dans ~/.shadeos_env
  * Variables d'environnement personnalisées pour ShadeOS_Agents
  * Intégration avec ProcessManager pour adaptation commandes

- Core/ProcessManager/process_manager_tools.py: Outils ProcessManager pour Assistant V9
  * execute_command: Exécution de commandes shell adaptées
  * get_active_processes: Monitoring des processus
  * communicate_with_process: Communication interactive
  * terminate_process: Gestion des processus

🔧 AMÉLIORATIONS:
- Core/ProcessManager/execute_command.py: Intégration SecureEnvManager
- Daemons/DaemonTeam/LegionAutoFeedingThread.py: Debug et parsing LLM optimisé
- ConsciousnessEngine/ShadeOS_Extraction/alma_thesis_proposal.md: Proposition de thèse

🔒 SÉCURITÉ:
- Variables d'environnement dans ~/.shadeos_env (pas dans git)
- Permissions restrictives (600) sur les fichiers de config
- Mot de passe Neo4j personnalisé: ShadeOS_Agents_2025
- Détection automatique OS/Shell pour adaptation commandes

🎯 INTÉGRATION ASSISTANT V9:
- Prompt système enrichi avec informations OS/Shell
- Outils ProcessManager disponibles via ToolRegistry
- Adaptation automatique des commandes shell
- Chargement sécurisé des variables d'environnement

⛧ ARCHITECTE DÉMONIAQUE: Alma
🔮 VISION: Assistant V9 avec capacités shell cross-platform 