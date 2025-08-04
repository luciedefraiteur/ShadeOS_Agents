# ⛧ UnitTests - Tests Unitaires et d'Intégration ⛧

## 📁 Structure des Tests

### 🧠 MemoryEngine/
Tests du système de mémoire fractale et des composants core
- `test_memory_engine_core.py` : Tests du moteur principal
- `test_extensions.py` : Tests des extensions
- `test_process_manager.py` : Tests du gestionnaire de processus
- `test_editing_session.py` : Tests de la session d'édition

### 🤖 Assistants/
Tests des assistants IA et des daemons
- `test_v3_local_model.py` : Tests du modèle local V3
- `test_debug_agent_with_bugs.py` : Tests de débogage
- `test_openai_assistant_original.py` : Tests OpenAI

### 📚 Archiviste/
Tests du daemon Archiviste et de la gestion mémoire
- `test_archiviste_logging_architecture.py` : Tests d'architecture
- `test_archiviste_alma_integration.py` : Tests d'intégration Alma
- `test_archiviste_naive_logging.py` : Tests de logging

### 🎭 Orchestrator/
Tests de l'orchestrateur de daemons
- `test_meta_daemon_orchestrator.py` : Tests de l'orchestrateur
- `test_orchestrator_alma_communication.py` : Tests de communication

### 🔗 Integration/
Tests d'intégration entre composants
- `test_reflection_engine.py` : Tests du moteur de réflexion
- `test_introspective_dynamic.py` : Tests introspectifs
- `test_alma_timeline_integration.py` : Tests d'intégration timeline

### 🛠️ Scripts/
Scripts de test et utilitaires
- `test_lucie_model.py` : Tests du modèle Lucie
- `test_lucie_simple.sh` : Scripts shell de test
- `test_output.txt` : Fichiers de sortie de test

## 🚀 Utilisation

```bash
# Lancer tous les tests
python -m UnitTests

# Lancer les tests d'un module spécifique
python -m UnitTests.MemoryEngine
python -m UnitTests.Assistants
python -m UnitTests.Archiviste
```

**⛧ Créé par : Alma, Architecte Démoniaque du Nexus Luciforme ⛧**
