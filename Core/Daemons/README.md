# ⛧ Core/Daemons - Système de Daemons

**Date :** 2025-08-07  
**Auteur :** Alma (via Lucie Defraiteur)  
**Contexte :** Système de daemons pour ShadeOS_Agents

---

## 🎯 Vue d'Ensemble

Le dossier `Core/Daemons` contient tous les daemons du système ShadeOS_Agents, organisés par type et version pour une meilleure maintenabilité.

---

## 📁 Structure

### **⛧ Daemons Disponibles :**

#### **LegionAutoFeedingThread/ - Daemon Legion**
- **V1/** : Version initiale du Legion Auto-Feeding Thread
- **V2/** : Version améliorée avec optimisations
- **Architecture** : Auto-feeding thread avec mémoire temporelle
- **Status** : Stable, en production

---

## 🔧 Architecture

### **✅ Principe de Versioning :**
- **Isolation** : Chaque version est indépendante
- **Rétrocompatibilité** : Migration progressive possible
- **Évolutivité** : Ajout facile de nouvelles versions
- **Tests** : Tests isolés par version

### **✅ Imports Standardisés :**
```python
# Import d'un daemon spécifique
from Core.Daemons.LegionAutoFeedingThread.V1 import LegionAutoFeedingThreadV1
from Core.Daemons.LegionAutoFeedingThread.V2 import LegionAutoFeedingThreadV2

# Import du registre de daemons
from Core.Daemons import DaemonRegistry
```

---

## 🚀 Utilisation

### **1. Création d'un Daemon :**
```python
from Core.Daemons.LegionAutoFeedingThread.V2 import LegionAutoFeedingThreadV2

# Initialisation avec mémoire temporelle
temporal_engine = TemporalFractalMemoryEngine()
daemon = LegionAutoFeedingThreadV2(temporal_engine=temporal_engine)

# Démarrage du daemon
await daemon.start()
```

### **2. Migration entre Versions :**
```python
# Migration V1 -> V2
from Core.Daemons.LegionAutoFeedingThread.V1 import LegionAutoFeedingThreadV1
from Core.Daemons.LegionAutoFeedingThread.V2 import LegionAutoFeedingThreadV2

v1_daemon = LegionAutoFeedingThreadV1()
v2_daemon = LegionAutoFeedingThreadV2.from_v1_migration(v1_daemon)
```

### **3. Tests de Daemons :**
```python
# Tests isolés par version
from Core.Daemons.LegionAutoFeedingThread.V2.tests import test_legion_v2
from Core.Daemons.LegionAutoFeedingThread.V1.tests import test_legion_v1
```

---

## 📊 Métriques

### **✅ Performance par Version :**
- **V2** : Optimisations mémoire, < 1s latence
- **V1** : Baseline, < 2s latence

### **✅ Stabilité par Version :**
- **V2** : Stable, production ready
- **V1** : Legacy, maintenance minimale

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
from Core.Daemons.migration import DaemonMigrator

migrator = DaemonMigrator()
migrator.migrate_v1_to_v2(source_daemon, target_daemon)
```

---

## 📝 Développement

### **✅ Ajout d'un Nouveau Daemon :**
1. **Créer le dossier** : `Core/Daemons/NouveauDaemon/V1/`
2. **Implémenter le daemon** : `NouveauDaemonV1`
3. **Ajouter les tests** : `tests/test_nouveau_daemon_v1.py`
4. **Documenter** : `README.md` spécifique
5. **Intégrer** : Dans le registre de daemons

### **✅ Standards de Code :**
- **Type hints** : Obligatoires
- **Docstrings** : Documentation complète
- **Tests** : Couverture > 80%
- **Logging** : Structured logging
- **Error handling** : Gestion robuste d'erreurs

---

## 🔗 Liens

### **📋 Documentation :**
- [Migration Guide](./migration/README.md)
- [Testing Guide](./tests/README.md)

### **📋 Code :**
- [LegionAutoFeedingThread V2](./LegionAutoFeedingThread/V2/)
- [LegionAutoFeedingThread V1](./LegionAutoFeedingThread/V1/)

---

**Rapport généré automatiquement par Alma**  
**Date :** 2025-08-07  
**Statut :** Documentation complète du système de daemons
