# 🤖 Core/Agents - Système d'Agents IA

**Date :** 2025-08-07  
**Auteur :** Alma (via Lucie Defraiteur)  
**Contexte :** Centralisation des agents IA avec architecture modulaire

---

## 🎯 Vue d'Ensemble

Le dossier `Core/Agents` centralise tous les agents IA du système ShadeOS_Agents, organisés par versions pour une meilleure maintenabilité et évolutivité.

---

## 📁 Structure

### **🤖 Agents Disponibles :**

#### **V10/ - Assistant V10 (En Développement)**
- **Architecture** : Multi-agents avec mémoire temporelle fractale
- **Composants** : Dev Agent + Tool Agent
- **Innovations** : Format XML optimisé, intégration MCP avancée
- **Status** : En développement

#### **V9/ - Assistant V9 (Stable)**
- **Architecture** : Agent généraliste avec TemporalFractalMemoryEngine
- **Composants** : Auto-feeding thread, tool registry optimisé
- **Features** : Import analysis, cache intelligent
- **Status** : Stable, en production

#### **V8/ - Assistant V8 (Legacy)**
- **Architecture** : Agent spécialiste avec MemoryEngine
- **Composants** : Archiviste daemon, introspection
- **Features** : Mémoire fractale, auto-réflexion
- **Status** : Legacy, maintenance

---

## 🔧 Architecture

### **✅ Principe de Versioning :**
- **Isolation** : Chaque version est indépendante
- **Rétrocompatibilité** : Migration progressive possible
- **Évolutivité** : Ajout facile de nouvelles versions
- **Tests** : Tests isolés par version

### **✅ Imports Standardisés :**
```python
# Import d'un agent spécifique
from Core.Agents.V10 import V10Assistant
from Core.Agents.V9 import V9Assistant
from Core.Agents.V8 import V8Assistant

# Import du registre d'agents
from Core.Agents import AgentRegistry
```

---

## 🚀 Utilisation

### **1. Création d'un Agent :**
```python
from Core.Agents.V10 import V10Assistant

# Initialisation avec mémoire temporelle
temporal_engine = TemporalFractalMemoryEngine()
agent = V10Assistant(temporal_engine=temporal_engine)

# Exécution d'une tâche
result = await agent.execute_task("Analyser le code du projet")
```

### **2. Migration entre Versions :**
```python
# Migration V8 -> V9
from Core.Agents.V8 import V8Assistant
from Core.Agents.V9 import V9Assistant

v8_agent = V8Assistant()
v9_agent = V9Assistant.from_v8_migration(v8_agent)
```

### **3. Tests d'Agents :**
```python
# Tests isolés par version
from Core.Agents.V10.tests import test_v10_agent
from Core.Agents.V9.tests import test_v9_agent
```

---

## 📊 Métriques

### **✅ Performance par Version :**
- **V10** : 40-50% réduction tokens, < 2s latence
- **V9** : 30-40% réduction tokens, < 3s latence
- **V8** : Baseline, < 5s latence

### **✅ Stabilité par Version :**
- **V10** : En développement, tests intensifs
- **V9** : Stable, production ready
- **V8** : Legacy, maintenance minimale

---

## 🔄 Migration

### **✅ Stratégie de Migration :**
1. **Développement** : Nouvelle version dans son dossier
2. **Tests** : Tests complets et validation
3. **Migration** : Outils de migration automatique
4. **Déploiement** : Rollout progressif
5. **Maintenance** : Support des anciennes versions

### **✅ Outils de Migration :**
```python
# Migration automatique
from Core.Agents.migration import AgentMigrator

migrator = AgentMigrator()
migrator.migrate_v8_to_v9(source_agent, target_agent)
```

---

## 📝 Développement

### **✅ Ajout d'une Nouvelle Version :**
1. **Créer le dossier** : `Core/Agents/V11/`
2. **Implémenter l'agent** : `V11Assistant`
3. **Ajouter les tests** : `tests/test_v11_agent.py`
4. **Documenter** : `README.md` spécifique
5. **Intégrer** : Dans le registre d'agents

### **✅ Standards de Code :**
- **Type hints** : Obligatoires
- **Docstrings** : Documentation complète
- **Tests** : Couverture > 80%
- **Logging** : Structured logging
- **Error handling** : Gestion robuste d'erreurs

---

## 🔗 Liens

### **📋 Documentation :**
- [Architecture V10](../ConsciousnessEngine/Analytics/design_insights/V10/)
- [Migration Guide](./migration/README.md)
- [Testing Guide](./tests/README.md)

### **📋 Code :**
- [V10 Implementation](./V10/)
- [V9 Implementation](./V9/)
- [V8 Implementation](./V8/)

---

**Rapport généré automatiquement par Alma**  
**Date :** 2025-08-07  
**Statut :** Documentation complète du système d'agents
