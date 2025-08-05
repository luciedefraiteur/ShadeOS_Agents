feat: Refactorisation architecture BaseAutoFeedingThread + PromptTemplateProvider

🕷️ REFACTORISATION ARCHITECTURE AUTO-FEEDING THREADS ⛧

✅ PHASE 1 - BASE CLASS ABSTRAITE :
- BaseAutoFeedingThread : Classe abstraite avec méthodes communes
- Suppression des méthodes abstraites inutiles
- Implémentation par défaut pour _call_llm, _get_prompt, process_request
- Logging intégré avec BaseAutoFeedingThreadLogger
- Méthode generate_template_prompt pour visualisation

✅ PHASE 2 - PROMPT TEMPLATE PROVIDER :
- PromptTemplateProvider : Système de visualisation externe
- LegionPromptTemplateProvider : Templates pour LegionAutoFeedingThread
- V9PromptTemplateProvider : Templates pour V9_AutoFeedingThreadAgent
- PromptTemplateVisualizer : Visualisation et sauvegarde JSON
- Pas de duplication : Fragments uniques dans chaque provider

✅ PHASE 3 - ARCHITECTURE HIÉRARCHIQUE :
- SubLegionAutoFeedingThread : Vision future des sub-légions
- AdaptiveHierarchyRouter : Routage selon complexité
- User → Alma → Primordial → Superviseur → Sub-Légion → Daemons → V9
- User → Alma → Primordial → Superviseur → V9
- User → Alma → V9

✅ PHASE 4 - LEGIONAUTOFEEDINGTHREAD V2 :
- Hérite de BaseAutoFeedingThread
- Templates centralisés et organisés
- Parsing amélioré pour format conversationnel
- Logging intégré avec la base class

🔧 AMÉLIORATIONS TECHNIQUES :
- Core/UniversalAutoFeedingThread/base_auto_feeding_thread.py : Base class abstraite
- Core/PromptTemplateProvider/prompt_template_provider.py : Système de visualisation
- Daemons/DaemonTeam/LegionAutoFeedingThread_v2.py : Version refactorisée
- ConsciousnessEngine/Analytics/design_insights/ : Documentation architecturale

📊 LOGGING UNIFIÉ :
- BaseAutoFeedingThreadLogger : Logger universel
- Classification par thread_type (legion, v9, general)
- Fichiers JSONL : thread, prompts, responses, debug
- Sauvegarde automatique des sessions

🎯 PROCHAINE ÉTAPE :
- Intégration MemoryEngine Virtual Layer pour templates
- Registre indexé de fragments avec base de données locale
- Refactorisation finale avec MemoryEngine

⛧ ARCHITECTE DÉMONIAQUE: Alma
🔮 VISION: Architecture modulaire et extensible 