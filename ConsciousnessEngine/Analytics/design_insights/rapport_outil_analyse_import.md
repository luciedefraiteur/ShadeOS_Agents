# 🔍 Analyseur d'Imports - Intégration TemporalFractalMemoryEngine

**Date de création :** 2025-08-06 15:45:30  
**Auteur :** Alma (via Lucie Defraiteur)  
**Contexte :** Intégration de l'analyseur d'imports dans le nouveau TemporalFractalMemoryEngine

---

## 📁 **Emplacement et Structure**

### Script Principal
- **Fichier :** `UnitTests/partitioning_import_analyzer.py`
- **Fonction :** Analyse récursive des dépendances Python avec détection de cycles
- **Génération :** Rapports Markdown et JSON détaillés

### Composants Clés
1. **`PartitioningImportAnalyzer`** - Classe principale d'analyse
2. **`SimpleImportAnalyzerLogger`** - Système de logging et génération de rapports
3. **`DependencyGraph`** - Graphe de dépendances avec détection de cycles
4. **`_generate_ascii_tree()`** - Génération d'arbre ASCII structurel

---

## 🚀 **Utilisation Actuelle**

### Commandes Principales
```bash
# Analyse complète avec logs
python UnitTests/partitioning_import_analyzer.py --local-only --log-output --log-directory logs --log-format json --no-import-resolver

# Avec ImportResolver activé
python UnitTests/partitioning_import_analyzer.py --local-only --log-output --use-import-resolver

# Avec limite de profondeur
python UnitTests/partitioning_import_analyzer.py --max-depth 3 --log-output
```

### Fonctionnalités
- ✅ **Analyse récursive pure** jusqu'à la profondeur maximale
- ✅ **Détection de cycles intelligente** avec prévention
- ✅ **Résolution d'imports** (simple + ImportResolver)
- ✅ **Génération de rapports** Markdown structurés
- ✅ **Arbre ASCII** de la hiérarchie des fichiers
- ✅ **Statistiques détaillées** par type d'import

### Sorties Générées
- **Rapport Markdown :** `logs/imports_analysis/imports_analysis_report.md`
- **Log JSON :** `logs/imports_analysis/imports_analysis.log`
- **Structure :** Liste simple → Arbre ASCII → Détails → Stats

---

## 🧠 **Intégration dans TemporalFractalMemoryEngine**

### Vision Conceptuelle

L'analyseur d'imports peut devenir un **"FractalImportMapper"** qui transforme les relations d'imports en **liens fractaux temporels**, créant une cartographie vivante des dépendances du projet.

### Architecture Proposée

#### 1. **FractalImportNode** (Nouvelle classe)
```python
@dataclass
class FractalImportNode:
    """Nœud fractal représentant un fichier et ses imports"""
    
    # Identifiants
    file_path: str
    fractal_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    temporal_timestamp: datetime = field(default_factory=datetime.now)
    
    # Relations fractales
    import_links: List[FractalImportLink] = field(default_factory=list)
    dependency_depth: int = 0
    import_complexity: float = 0.0  # Métrique de complexité
    
    # Strates temporelles
    strata: str = "cognitive"  # cognitive, temporal, fractal
    temporal_links: List[TemporalLink] = field(default_factory=list)
    
    # Métadonnées fractales
    fractal_dimensions: Dict[str, Any] = field(default_factory=dict)
    import_patterns: List[str] = field(default_factory=list)
```

#### 2. **FractalImportLink** (Nouvelle classe)
```python
@dataclass
class FractalImportLink:
    """Lien fractal entre fichiers basé sur les imports"""
    
    source_file: str
    target_file: str
    import_type: str  # relative, absolute, external
    link_strength: float = 1.0  # Force du lien (basée sur la fréquence)
    
    # Dimensions fractales
    temporal_weight: float = 0.0  # Poids temporel
    complexity_weight: float = 0.0  # Poids de complexité
    dependency_weight: float = 0.0  # Poids de dépendance
    
    # Métadonnées temporelles
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_frequency: int = 0
```

#### 3. **TemporalFractalImportMapper** (Nouvelle classe)
```python
class TemporalFractalImportMapper:
    """Mappeur d'imports fractals temporels"""
    
    def __init__(self, memory_engine: TemporalFractalMemoryEngine):
        self.memory_engine = memory_engine
        self.import_analyzer = PartitioningImportAnalyzer()
        self.fractal_nodes: Dict[str, FractalImportNode] = {}
        self.temporal_graph = TemporalDependencyGraph()
    
    async def fractalize_project_imports(self, project_root: str) -> Dict[str, FractalImportNode]:
        """Transforme les imports du projet en structure fractale temporelle"""
        
        # 1. Analyse des imports
        analysis_result = self.import_analyzer.analyze_imports(
            self._get_project_files(project_root),
            use_import_resolver=True
        )
        
        # 2. Création des nœuds fractals
        for file_path, file_data in analysis_result['files_data'].items():
            fractal_node = self._create_fractal_node(file_path, file_data)
            self.fractal_nodes[file_path] = fractal_node
        
        # 3. Création des liens temporels
        await self._create_temporal_links(analysis_result['dependencies'])
        
        # 4. Stockage dans le moteur de mémoire
        await self._store_fractal_imports()
        
        return self.fractal_nodes
    
    def _create_fractal_node(self, file_path: str, file_data: Dict) -> FractalImportNode:
        """Crée un nœud fractal à partir des données d'analyse"""
        
        # Calcul de la complexité fractale
        complexity = self._calculate_import_complexity(file_data)
        
        # Détermination de la strate
        strata = self._determine_strata(file_data['depth'], complexity)
        
        return FractalImportNode(
            file_path=file_path,
            dependency_depth=file_data['depth'],
            import_complexity=complexity,
            strata=strata,
            import_patterns=self._extract_import_patterns(file_data['imports'])
        )
    
    async def _create_temporal_links(self, dependencies: List[str]):
        """Crée les liens temporels entre les nœuds fractals"""
        
        for dep in dependencies:
            source, target = self._parse_dependency(dep)
            
            if source in self.fractal_nodes and target in self.fractal_nodes:
                temporal_link = TemporalLink(
                    source_node=self.fractal_nodes[source],
                    target_node=self.fractal_nodes[target],
                    link_type="import_dependency",
                    temporal_weight=self._calculate_temporal_weight(source, target)
                )
                
                self.temporal_graph.add_link(temporal_link)
    
    def _calculate_import_complexity(self, file_data: Dict) -> float:
        """Calcule la complexité fractale d'un fichier basée sur ses imports"""
        
        base_complexity = len(file_data['imports'])
        depth_multiplier = 1 + (file_data['depth'] * 0.2)
        import_diversity = len(set(file_data['imports']))
        
        return (base_complexity * depth_multiplier * import_diversity) / 100.0
    
    def _determine_strata(self, depth: int, complexity: float) -> str:
        """Détermine la strate temporelle basée sur la profondeur et complexité"""
        
        if depth <= 1 and complexity < 0.5:
            return "somatic"  # Fichiers simples, peu de dépendances
        elif depth <= 3 and complexity < 2.0:
            return "cognitive"  # Fichiers intermédiaires
        else:
            return "metaphysical"  # Fichiers complexes, profonds
```

### Intégration dans TemporalFractalMemoryEngine

#### 1. **Extension de l'API**
```python
class TemporalFractalMemoryEngine:
    """Moteur de mémoire fractale temporelle avec analyse d'imports"""
    
    def __init__(self, backend_type: str = "auto", **kwargs):
        super().__init__(backend_type, **kwargs)
        self.import_mapper = TemporalFractalImportMapper(self)
        self.fractal_import_graph = None
    
    async def fractalize_project_structure(self, project_root: str) -> Dict[str, Any]:
        """Fractalise la structure complète d'un projet"""
        
        # 1. Analyse des imports
        fractal_nodes = await self.import_mapper.fractalize_project_imports(project_root)
        
        # 2. Création de la mémoire fractale
        project_memory = await self._create_project_fractal_memory(fractal_nodes)
        
        # 3. Indexation temporelle
        await self._index_temporal_dependencies(fractal_nodes)
        
        return {
            'fractal_nodes': fractal_nodes,
            'temporal_graph': self.import_mapper.temporal_graph,
            'project_memory': project_memory
        }
    
    async def query_fractal_imports(self, query: str, strata: str = None) -> List[FractalImportNode]:
        """Interroge la structure fractale des imports"""
        
        # Recherche dans les nœuds fractals
        results = []
        for node in self.fractal_nodes.values():
            if self._matches_query(node, query, strata):
                results.append(node)
        
        return sorted(results, key=lambda n: n.import_complexity, reverse=True)
    
    async def get_import_dependency_path(self, source_file: str, target_file: str) -> List[str]:
        """Trouve le chemin de dépendance entre deux fichiers"""
        
        return self.import_mapper.temporal_graph.find_path(source_file, target_file)
```

#### 2. **Nouvelles Méthodes de Recherche**
```python
class TemporalFractalMemoryEngine:
    
    async def find_circular_dependencies(self) -> List[List[str]]:
        """Trouve les dépendances circulaires dans le projet"""
        return self.import_mapper.temporal_graph.detect_cycles()
    
    async def get_most_complex_files(self, limit: int = 10) -> List[FractalImportNode]:
        """Retourne les fichiers les plus complexes"""
        nodes = list(self.fractal_nodes.values())
        return sorted(nodes, key=lambda n: n.import_complexity, reverse=True)[:limit]
    
    async def get_temporal_import_evolution(self, file_path: str) -> Dict[str, Any]:
        """Analyse l'évolution temporelle des imports d'un fichier"""
        return await self._analyze_temporal_evolution(file_path)
    
    async def suggest_refactoring(self, file_path: str) -> List[str]:
        """Suggère des refactorisations basées sur l'analyse fractale"""
        return await self._generate_refactoring_suggestions(file_path)
```

### Avantages de l'Intégration

#### 1. **Cartographie Vivante**
- Visualisation en temps réel des dépendances
- Détection automatique des patterns d'imports
- Évolution temporelle de la structure

#### 2. **Intelligence Fractale**
- Métriques de complexité basées sur les imports
- Classification automatique en strates temporelles
- Détection de patterns récurrents

#### 3. **Optimisation Continue**
- Suggestions de refactoring automatiques
- Détection de dépendances circulaires
- Optimisation de la structure du projet

#### 4. **Mémoire Temporelle**
- Historique des changements d'imports
- Évolution de la complexité dans le temps
- Prédiction de l'évolution future

---

## 🔧 **Implémentation Technique**

### Étapes de Développement

#### Phase 1 : Intégration de Base
1. **Migration du code** : Déplacer `partitioning_import_analyzer.py` vers `Core/ImportAnalysis/`
2. **Création des nouvelles classes** : `FractalImportNode`, `FractalImportLink`
3. **Intégration dans TemporalFractalMemoryEngine** : Méthodes de base

#### Phase 2 : Fonctionnalités Avancées
1. **TemporalDependencyGraph** : Graphe temporel des dépendances
2. **Métriques de complexité** : Calculs fractals avancés
3. **API de requête** : Recherche et filtrage

#### Phase 3 : Intelligence Artificielle
1. **Suggestions automatiques** : Refactoring intelligent
2. **Prédiction d'évolution** : Modèles prédictifs
3. **Optimisation continue** : Auto-optimisation

### Structure de Fichiers Proposée
```
Core/
├── ImportAnalysis/
│   ├── __init__.py
│   ├── fractal_import_mapper.py
│   ├── fractal_import_node.py
│   ├── temporal_dependency_graph.py
│   └── import_complexity_analyzer.py
├── TemporalFractalMemoryEngine/
│   ├── __init__.py
│   ├── engine.py (étendu)
│   ├── fractal_import_integration.py
│   └── temporal_import_queries.py
```

---

## 📊 **Métriques et KPIs**

### Métriques de Complexité
- **Import Complexity Score** : Complexité basée sur le nombre et la diversité des imports
- **Dependency Depth** : Profondeur maximale de dépendance
- **Circular Dependency Ratio** : Ratio de dépendances circulaires
- **Temporal Evolution Rate** : Taux d'évolution des imports dans le temps

### Métriques de Performance
- **Analysis Speed** : Vitesse d'analyse des imports
- **Memory Usage** : Utilisation mémoire pour le stockage fractal
- **Query Response Time** : Temps de réponse des requêtes fractales

---

## 🎯 **Conclusion**

L'intégration de l'analyseur d'imports dans le TemporalFractalMemoryEngine représente une **évolution majeure** vers un système de mémoire fractale temporelle complet.

### Bénéfices Attendus
1. **Compréhension profonde** de la structure du projet
2. **Optimisation automatique** des dépendances
3. **Prédiction d'évolution** de la complexité
4. **Refactoring intelligent** basé sur l'analyse fractale