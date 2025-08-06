# 🔧 Core Partitioner

**Système de partitioning et d'analyse d'imports centralisé**

Composant central pour le partitioning de code et l'analyse des dépendances Python.
Réutilisable par tous les composants du système (EditingSession, TemporalEngine, LegionAutoFeedingThread, etc.)

## 📁 Structure

```
Core/Partitioner/
├── __init__.py                    # Module principal
├── import_analyzer.py            # Analyseur d'imports Python
├── import_resolver.py            # Résolveur d'imports
├── language_registry.py          # Registre des langages supportés
├── location_tracker.py           # Traqueur de localisation
├── partition_schemas.py          # Schémas de partition
├── error_logger.py               # Logger d'erreurs
├── ast_partitioners/             # Partitioners basés sur AST
│   ├── base_ast_partitioner.py
│   ├── python_ast_partitioner.py
│   └── tree_sitter_partitioner.py
├── fallback_strategies/          # Stratégies de fallback
│   ├── emergency_partitioner.py
│   ├── regex_partitioner.py
│   └── textual_partitioner.py
└── docs/                         # Documentation
    ├── HYBRID_STRATEGY_PLAN.md
    └── README.md
```

## 🚀 Utilisation

### Import Analyzer

```python
from Core.Partitioner import ImportAnalyzer

# Analyser les imports d'un fichier
analyzer = ImportAnalyzer()
report = analyzer.analyze_files(['file1.py', 'file2.py'])

# Générer un rapport Markdown
md_content = analyzer.generate_markdown_report(report)
```

### En ligne de commande

```bash
# Analyser un fichier
python Core/Partitioner/import_analyzer.py file1.py

# Analyser plusieurs fichiers avec profondeur limitée
python Core/Partitioner/import_analyzer.py --max-depth 5 file1.py file2.py

# Générer un rapport JSON
python Core/Partitioner/import_analyzer.py --output report.json file1.py

# Générer un rapport Markdown
python Core/Partitioner/import_analyzer.py --markdown report.md file1.py
```

### Intégration avec TemporalFractalMemoryEngine

```python
from Core.Partitioner import ImportAnalyzer
from TemporalFractalMemoryEngine.core.import_analysis_integration import analyze_and_fractalize_files

# Fractaliser les imports d'une liste de fichiers
fractal_nodes = await analyze_and_fractalize_files(['file1.py', 'file2.py'])
```

## 🔧 Fonctionnalités

### Import Analyzer
- ✅ Analyse récursive des dépendances Python
- ✅ Détection de cycles de dépendances
- ✅ Classification des imports (local, standard, external)
- ✅ Résolution d'imports avec ImportResolver
- ✅ Génération de rapports JSON et Markdown
- ✅ Interface en ligne de commande complète

### Partitioning System
- ✅ Partitioning basé sur AST
- ✅ Stratégies de fallback robustes
- ✅ Support multi-langages
- ✅ Traçage de localisation précis
- ✅ Gestion d'erreurs avancée

### Intégration Fractale
- ✅ Création de nœuds fractaux basés sur les imports
- ✅ Calcul de complexité fractale
- ✅ Classification en strates temporelles
- ✅ Stockage dans le moteur de mémoire

## 📊 Métriques

### Complexité Fractale
- **Base** : Nombre d'imports
- **Multiplicateur de profondeur** : 1 + (profondeur × 0.2)
- **Diversité** : Somme des types d'imports
- **Pénalité** : Imports non résolus × 0.5

### Strates Temporelles
- **Somatic** : ≤ 3 imports, complexité < 0.5
- **Cognitive** : ≤ 10 imports, complexité < 2.0
- **Metaphysical** : > 10 imports ou complexité ≥ 2.0

## 🔗 Intégrations

### Composants Utilisateurs
- ✅ **EditingSession** : Partitioning de fichiers pour édition
- ✅ **TemporalFractalMemoryEngine** : Analyse fractale des dépendances
- ✅ **LegionAutoFeedingThread** : Analyse des imports pour auto-feeding
- ✅ **Daemons** : Analyse de structure pour introspection

### Outils Externes
- ✅ **ImportResolver** : Résolution d'imports complexes
- ✅ **TreeSitter** : Parsing avancé (optionnel)
- ✅ **AST** : Parsing Python natif

## 🎯 Avantages

### Centralisation
- ✅ **Réutilisabilité** : Un seul composant pour tous
- ✅ **Maintenance** : Mise à jour centralisée
- ✅ **Cohérence** : Même logique partout

### Performance
- ✅ **Cache** : Résultats mis en cache
- ✅ **Optimisation** : Algorithmes optimisés
- ✅ **Parallélisation** : Support multi-threading

### Robustesse
- ✅ **Fallback** : Stratégies de récupération
- ✅ **Erreurs** : Gestion d'erreurs complète
- ✅ **Validation** : Vérification des résultats

## ⛧ Évolution

### Versions Futures
- 🔮 **Support multi-langages** : JavaScript, TypeScript, etc.
- 🔮 **Analyse sémantique** : Compréhension du contexte
- 🔮 **Prédiction** : Anticipation des changements
- 🔮 **Optimisation automatique** : Suggestions de refactoring

### Intégrations Planifiées
- 🔮 **IDE** : Plugins pour éditeurs
- 🔮 **CI/CD** : Intégration continue
- 🔮 **Monitoring** : Surveillance en temps réel
- 🔮 **API** : Interface REST/GraphQL

---

**Auteur :** Alma (via Lucie Defraiteur)  
**Version :** 1.0.0  
**Date :** 2025-08-06 