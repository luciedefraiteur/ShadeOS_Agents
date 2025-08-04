# 🧹 Plan de Cleanup Complet - Codebase Archiviste

## 📊 État Actuel
- **Fichiers .md restants :** 56 (était 2679 avant suppression de ShadeOS)
- **Branche :** cleanup_for_archivist
- **Objectif :** Codebase propre et fonctionnelle pour l'Archiviste

## 🗑️ Suppressions Prioritaires

### 1. **Dossiers Obsolètes**
- `OldVersions/` - Archive complète
- `IAIntrospectionDaemons/PromptEngineeringDaemons/` - Architecture obsolète
- `MemoryEngine/EditingSession/` - Module non utilisé pour l'Archiviste

### 2. **Fichiers .md Obsolètes**
- `commit_message_temp.md` - Temporaire
- `ROADMAP.md` - Obsolète
- `DAEMON_CAPABILITIES.md` - Remplacé par l'implémentation
- `README.md` racine - À remplacer par un README Archiviste
- `TestProject/README.md` - Test obsolète

### 3. **Code Legacy**
- `MemoryEngine/core/archiviste_daemon_naive.py` - Remplacé par le système modulaire
- `MemoryEngine/core/archiviste_daemon_conceptual.py` - Concept obsolète
- `MemoryEngine/core/archiviste_daemon_prompt.luciform` - Remplacé par les prompts modulaires

## 🧭 Conservation Stratégique

### **À Garder (Fonctionnel)**
- `MemoryEngine/core/archiviste/` - Système modulaire actuel
- `MemoryEngine/core/engine.py` - Core fonctionnel
- `MemoryEngine/core/memory_node.py` - Structure de données
- `MemoryEngine/core/temporal_index.py` - Index temporel
- `Alma_toolset/` - Outils fonctionnels
- `Alma/ALMA_PERSONALITY.md` - Personnalité d'Alma

### **À Évaluer**
- `IAIntrospectionDaemons/debugging_local_llm_assistant/` - Utile pour debug
- `MemoryEngine/UnitTests/` - Tests à conserver
- `MemoryEngine/backends/` - Backends fonctionnels

## 🎯 Plan d'Exécution

### Phase 1 : Suppressions Massives
1. Supprimer `OldVersions/`
2. Supprimer `IAIntrospectionDaemons/PromptEngineeringDaemons/`
3. Supprimer `MemoryEngine/EditingSession/`
4. Supprimer les fichiers .md obsolètes

### Phase 2 : Nettoyage Code
1. Supprimer les daemons obsolètes
2. Nettoyer les imports inutilisés
3. Vérifier la cohérence des modules

### Phase 3 : Documentation
1. Créer un README Archiviste moderne
2. Documenter l'architecture actuelle
3. Créer un guide d'utilisation

## 📈 Objectifs
- **Réduction :** 56 → ~10 fichiers .md
- **Codebase :** Focus sur l'Archiviste et MemoryEngine
- **Lisibilité :** Structure claire et fonctionnelle 