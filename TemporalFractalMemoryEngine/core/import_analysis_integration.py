#!/usr/bin/env python3
"""
🔍 Intégration Import Analyzer - TemporalFractalMemoryEngine

Intégration de l'analyseur d'imports avec le TemporalFractalMemoryEngine
pour créer des nœuds fractaux basés sur les dépendances d'imports.

Auteur: Alma (via Lucie Defraiteur)
Date: 2025-08-06
"""

import os
import sys
import asyncio
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
import uuid

# Import de l'analyseur d'imports
try:
    from Core.Partitioner.analyzers.import_analyzer import ImportAnalyzer, ImportAnalysisResult
except ImportError:
    logger.warning("ImportAnalyzer non disponible")
    ImportAnalyzer = None
    ImportAnalysisResult = None

# Import du TemporalFractalMemoryEngine
try:
    from .temporal_engine import TemporalFractalMemoryEngine
    from .memory_node import MemoryNode
    from .temporal_index import TemporalIndex
except ImportError:
    logger.warning("TemporalFractalMemoryEngine non disponible")
    TemporalFractalMemoryEngine = None
    MemoryNode = None
    TemporalIndex = None

logger = logging.getLogger(__name__)


@dataclass
class FractalImportNode:
    """Nœud fractal représentant un fichier et ses imports"""
    
    # Identifiants
    file_path: str
    fractal_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    temporal_timestamp: datetime = field(default_factory=datetime.now)
    
    # Relations fractales
    import_links: List['FractalImportLink'] = field(default_factory=list)
    dependency_depth: int = 0
    import_complexity: float = 0.0  # Métrique de complexité
    
    # Strates temporelles
    strata: str = "cognitive"  # cognitive, temporal, fractal
    temporal_links: List['TemporalLink'] = field(default_factory=list)
    
    # Métadonnées fractales
    fractal_dimensions: Dict[str, Any] = field(default_factory=dict)
    import_patterns: List[str] = field(default_factory=list)
    
    # Données d'analyse
    analysis_result: Optional[ImportAnalysisResult] = None


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


@dataclass
class TemporalLink:
    """Lien temporel entre nœuds fractals"""
    
    source_node: FractalImportNode
    target_node: FractalImportNode
    link_type: str  # import_dependency, temporal_sequence, fractal_relation
    temporal_weight: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)


class TemporalFractalImportMapper:
    """Mappeur d'imports fractals temporels"""
    
    def __init__(self, memory_engine: TemporalFractalMemoryEngine):
        self.memory_engine = memory_engine
        self.import_analyzer = ImportAnalyzer() if ImportAnalyzer else None
        self.fractal_nodes: Dict[str, FractalImportNode] = {}
        self.temporal_graph = TemporalDependencyGraph()
        
        if not self.import_analyzer:
            logger.warning("ImportAnalyzer non disponible, fonctionnalités limitées")
    
    async def fractalize_project_imports(self, project_root: str) -> Dict[str, FractalImportNode]:
        """Transforme les imports du projet en structure fractale temporelle"""
        
        if not self.import_analyzer:
            logger.error("ImportAnalyzer non disponible")
            return {}
        
        logger.info(f"🔍 Fractalisation des imports du projet: {project_root}")
        
        # 1. Obtenir tous les fichiers Python du projet
        python_files = self._get_project_python_files(project_root)
        
        # 2. Analyser les imports
        analysis_result = self.import_analyzer.analyze_files(python_files)
        
        # 3. Créer les nœuds fractals
        for file_path, file_data in analysis_result['detailed_results'].items():
            fractal_node = self._create_fractal_node(file_path, file_data)
            self.fractal_nodes[file_path] = fractal_node
        
        # 4. Créer les liens temporels
        await self._create_temporal_links(analysis_result['cycles'])
        
        # 5. Stocker dans le moteur de mémoire
        await self._store_fractal_imports()
        
        logger.info(f"✅ Fractalisation terminée: {len(self.fractal_nodes)} nœuds créés")
        
        return self.fractal_nodes
    
    async def fractalize_file_imports(self, file_paths: List[str]) -> Dict[str, FractalImportNode]:
        """Fractalise les imports d'une liste de fichiers spécifiques"""
        
        if not self.import_analyzer:
            logger.error("ImportAnalyzer non disponible")
            return {}
        
        logger.info(f"🔍 Fractalisation des imports de {len(file_paths)} fichiers")
        
        # 1. Analyser les imports
        analysis_result = self.import_analyzer.analyze_files(file_paths)
        
        # 2. Créer les nœuds fractals
        for file_path, file_data in analysis_result['detailed_results'].items():
            fractal_node = self._create_fractal_node(file_path, file_data)
            self.fractal_nodes[file_path] = fractal_node
        
        # 3. Créer les liens temporels
        await self._create_temporal_links(analysis_result['cycles'])
        
        # 4. Stocker dans le moteur de mémoire
        await self._store_fractal_imports()
        
        logger.info(f"✅ Fractalisation terminée: {len(self.fractal_nodes)} nœuds créés")
        
        return self.fractal_nodes
    
    def _get_project_python_files(self, project_root: str) -> List[str]:
        """Récupère tous les fichiers Python d'un projet"""
        python_files = []
        
        for root, dirs, files in os.walk(project_root):
            # Ignorer les dossiers spéciaux
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)
        
        return python_files
    
    def _create_fractal_node(self, file_path: str, file_data: Dict) -> FractalImportNode:
        """Crée un nœud fractal à partir des données d'analyse"""
        
        # Calcul de la complexité fractale
        complexity = self._calculate_import_complexity(file_data)
        
        # Détermination de la strate
        strata = self._determine_strata(file_data.get('import_count', 0), complexity)
        
        # Extraction des patterns d'imports
        import_patterns = self._extract_import_patterns(file_data.get('imports', []))
        
        # Création du nœud fractal
        fractal_node = FractalImportNode(
            file_path=file_path,
            dependency_depth=file_data.get('dependency_depth', 0),
            import_complexity=complexity,
            strata=strata,
            import_patterns=import_patterns,
            fractal_dimensions={
                'local_imports': len(file_data.get('local_imports', [])),
                'external_imports': len(file_data.get('external_imports', [])),
                'standard_imports': len(file_data.get('standard_imports', [])),
                'unresolved_imports': len(file_data.get('unresolved_imports', []))
            }
        )
        
        return fractal_node
    
    def _calculate_import_complexity(self, file_data: Dict) -> float:
        """Calcule la complexité fractale d'un fichier basée sur ses imports"""
        
        base_complexity = file_data.get('import_count', 0)
        depth_multiplier = 1 + (file_data.get('dependency_depth', 0) * 0.2)
        
        # Diversité des imports
        local_imports = len(file_data.get('local_imports', []))
        external_imports = len(file_data.get('external_imports', []))
        standard_imports = len(file_data.get('standard_imports', []))
        
        import_diversity = local_imports + external_imports + standard_imports
        
        # Complexité basée sur les imports non résolus
        unresolved_penalty = len(file_data.get('unresolved_imports', [])) * 0.5
        
        complexity = (base_complexity * depth_multiplier * import_diversity) / 100.0
        complexity += unresolved_penalty
        
        return max(0.1, complexity)  # Minimum de complexité
    
    def _determine_strata(self, import_count: int, complexity: float) -> str:
        """Détermine la strate temporelle basée sur la profondeur et complexité"""
        
        if import_count <= 3 and complexity < 0.5:
            return "somatic"  # Fichiers simples, peu de dépendances
        elif import_count <= 10 and complexity < 2.0:
            return "cognitive"  # Fichiers intermédiaires
        else:
            return "metaphysical"  # Fichiers complexes, profonds
    
    def _extract_import_patterns(self, imports: List[str]) -> List[str]:
        """Extrait les patterns d'imports récurrents"""
        patterns = []
        
        # Pattern: imports relatifs
        relative_imports = [imp for imp in imports if imp.startswith('from .') or imp.startswith('from ..')]
        if relative_imports:
            patterns.append("relative_imports")
        
        # Pattern: imports absolus
        absolute_imports = [imp for imp in imports if imp.startswith('from ') and not imp.startswith('from .')]
        if absolute_imports:
            patterns.append("absolute_imports")
        
        # Pattern: imports standards
        standard_modules = {'os', 'sys', 'json', 'pathlib', 'typing', 'dataclasses', 'asyncio'}
        standard_imports = [imp for imp in imports if any(module in imp for module in standard_modules)]
        if standard_imports:
            patterns.append("standard_library")
        
        return patterns
    
    async def _create_temporal_links(self, cycles: List[List[str]]):
        """Crée les liens temporels entre les nœuds fractals"""
        
        # Créer des liens basés sur les cycles
        for cycle in cycles:
            for i in range(len(cycle) - 1):
                source = cycle[i]
                target = cycle[i + 1]
                
                if source in self.fractal_nodes and target in self.fractal_nodes:
                    temporal_link = TemporalLink(
                        source_node=self.fractal_nodes[source],
                        target_node=self.fractal_nodes[target],
                        link_type="cycle_dependency",
                        temporal_weight=2.0  # Poids élevé pour les cycles
                    )
                    
                    self.temporal_graph.add_link(temporal_link)
        
        # Créer des liens basés sur les dépendances directes
        for file_path, fractal_node in self.fractal_nodes.items():
            if fractal_node.analysis_result:
                for import_path in fractal_node.analysis_result.local_imports:
                    if import_path in self.fractal_nodes:
                        temporal_link = TemporalLink(
                            source_node=fractal_node,
                            target_node=self.fractal_nodes[import_path],
                            link_type="import_dependency",
                            temporal_weight=1.0
                        )
                        
                        self.temporal_graph.add_link(temporal_link)
    
    async def _store_fractal_imports(self):
        """Stocke les nœuds fractals dans le moteur de mémoire"""
        
        if not self.memory_engine:
            logger.warning("TemporalFractalMemoryEngine non disponible, stockage ignoré")
            return
        
        logger.info("💾 Stockage des nœuds fractals dans le moteur de mémoire...")
        
        for file_path, fractal_node in self.fractal_nodes.items():
            try:
                # Créer un nœud de mémoire pour le fichier
                memory_node = MemoryNode(
                    content=f"Fichier Python: {file_path}",
                    metadata={
                        'file_path': file_path,
                        'fractal_uuid': fractal_node.fractal_uuid,
                        'import_complexity': fractal_node.import_complexity,
                        'strata': fractal_node.strata,
                        'import_patterns': fractal_node.import_patterns,
                        'fractal_dimensions': fractal_node.fractal_dimensions
                    },
                    temporal_timestamp=fractal_node.temporal_timestamp
                )
                
                # Stocker dans le moteur de mémoire
                await self.memory_engine.store_memory(memory_node)
                
            except Exception as e:
                logger.error(f"❌ Erreur lors du stockage de {file_path}: {e}")
        
        logger.info(f"✅ {len(self.fractal_nodes)} nœuds fractals stockés")
    
    async def query_fractal_imports(self, query: str, strata: str = None) -> List[FractalImportNode]:
        """Interroge la structure fractale des imports"""
        
        results = []
        
        for node in self.fractal_nodes.values():
            if self._matches_query(node, query, strata):
                results.append(node)
        
        # Trier par complexité décroissante
        return sorted(results, key=lambda n: n.import_complexity, reverse=True)
    
    def _matches_query(self, node: FractalImportNode, query: str, strata: str = None) -> bool:
        """Vérifie si un nœud correspond à la requête"""
        
        # Filtre par strate si spécifié
        if strata and node.strata != strata:
            return False
        
        # Recherche dans le chemin du fichier
        if query.lower() in node.file_path.lower():
            return True
        
        # Recherche dans les patterns d'imports
        for pattern in node.import_patterns:
            if query.lower() in pattern.lower():
                return True
        
        return False
    
    async def get_import_dependency_path(self, source_file: str, target_file: str) -> List[str]:
        """Trouve le chemin de dépendance entre deux fichiers"""
        
        if not self.temporal_graph:
            return []
        
        return self.temporal_graph.find_path(source_file, target_file)
    
    async def find_circular_dependencies(self) -> List[List[str]]:
        """Trouve les dépendances circulaires dans le projet"""
        
        if not self.temporal_graph:
            return []
        
        return self.temporal_graph.detect_cycles()
    
    async def get_most_complex_files(self, limit: int = 10) -> List[FractalImportNode]:
        """Retourne les fichiers les plus complexes"""
        
        nodes = list(self.fractal_nodes.values())
        return sorted(nodes, key=lambda n: n.import_complexity, reverse=True)[:limit]


class TemporalDependencyGraph:
    """Graphe temporel des dépendances"""
    
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.cycles = []
    
    def add_link(self, temporal_link: TemporalLink):
        """Ajoute un lien temporel au graphe"""
        self.edges.append(temporal_link)
    
    def find_path(self, source: str, target: str) -> List[str]:
        """Trouve un chemin entre deux fichiers"""
        # Implémentation simplifiée - à étendre
        return []
    
    def detect_cycles(self) -> List[List[str]]:
        """Détecte les cycles dans le graphe"""
        # Implémentation simplifiée - à étendre
        return []


# Fonctions utilitaires pour l'intégration
async def create_fractal_import_mapper(memory_engine: TemporalFractalMemoryEngine) -> TemporalFractalImportMapper:
    """Crée un mappeur d'imports fractals temporels"""
    return TemporalFractalImportMapper(memory_engine)


async def analyze_and_fractalize_files(file_paths: List[str], memory_engine: TemporalFractalMemoryEngine = None) -> Dict[str, FractalImportNode]:
    """Analyse et fractalise les imports d'une liste de fichiers"""
    
    if not ImportAnalyzer:
        logger.error("ImportAnalyzer non disponible")
        return {}
    
    # Créer le mappeur
    mapper = TemporalFractalImportMapper(memory_engine) if memory_engine else TemporalFractalImportMapper(None)
    
    # Fractaliser les fichiers
    fractal_nodes = await mapper.fractalize_file_imports(file_paths)
    
    return fractal_nodes


async def analyze_and_fractalize_project(project_root: str, memory_engine: TemporalFractalMemoryEngine = None) -> Dict[str, FractalImportNode]:
    """Analyse et fractalise les imports d'un projet entier"""
    
    if not ImportAnalyzer:
        logger.error("ImportAnalyzer non disponible")
        return {}
    
    # Créer le mappeur
    mapper = TemporalFractalImportMapper(memory_engine) if memory_engine else TemporalFractalImportMapper(None)
    
    # Fractaliser le projet
    fractal_nodes = await mapper.fractalize_project_imports(project_root)
    
    return fractal_nodes 