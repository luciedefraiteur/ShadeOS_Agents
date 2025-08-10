# 📊 Rapport d'Analyse Complète - Import Analyzer

## 🎯 Résumé Exécutif

**Date d'analyse:** 2025-08-07T18:27:26.021198  
**Racine du projet:** /home/luciedefraiteur/ShadeOS_Agents  
**Version Python:** 3.13.5 | packaged by Anaconda, Inc. | (main, Jun 12 2025, 16:09:02) [GCC 11.2.0]

### 📈 Métriques Clés

- **Fichiers analysés:** 14
- **Imports totaux:** 195
- **Imports locaux:** 16
- **Imports externes:** 50
- **Cycles détectés:** 0
- **Durée d'analyse:** 0.46s

---

## 🔍 Analyse de Complexité

### Métriques de Complexité

- **Fichiers Python totaux:** 14
- **Imports moyens par fichier:** 13.93
- **Imports locaux moyens par fichier:** 1.14

### 📋 Fichiers les Plus Complexes


#### Assistants/Generalist/V9_AutoFeedingThreadAgent.py
- **Imports totaux:** 24
- **Imports locaux:** 10

#### /home/luciedefraiteur/ShadeOS_Agents/TemporalFractalMemoryEngine/core/temporal_engine.py
- **Imports totaux:** 24
- **Imports locaux:** 0

#### Core/Partitioner/import_analyzer.py
- **Imports totaux:** 22
- **Imports locaux:** 0

#### /home/luciedefraiteur/ShadeOS_Agents/Assistants/EditingSession/Tools/optimized_tool_registry.py
- **Imports totaux:** 17
- **Imports locaux:** 5

#### /home/luciedefraiteur/ShadeOS_Agents/TemporalFractalMemoryEngine/core/temporal_workspace_layer.py
- **Imports totaux:** 16
- **Imports locaux:** 1


---

## ⚠️ Modules Critiques

### Modules les Plus Dépendus


🔴 **Core**
- **Dépendances:** 10
- **Niveau de criticité:** HIGH

🟡 **TemporalFractalMemoryEngine**
- **Dépendances:** 4
- **Niveau de criticité:** MEDIUM

🟢 **Assistants**
- **Dépendances:** 2
- **Niveau de criticité:** LOW


---

## 📊 Détails Techniques

### Statistiques Détaillées

- **Imports standard:** 129
- **Fichiers avec erreurs:** 0
- **Profondeur maximale:** 0

### 🔄 Cycles de Dépendances

Aucun cycle de dépendances détecté.



---

## 🎯 Recommandations

### Optimisations Suggérées

1. **Modules critiques:** Surveiller les modules avec un niveau de criticité HIGH
2. **Complexité:** Considérer la refactorisation des fichiers avec plus de 10 imports
3. **Cycles:** Éviter les cycles de dépendances pour maintenir la maintenabilité

---

*Rapport généré automatiquement par HighLevelImportAnalyzer*
