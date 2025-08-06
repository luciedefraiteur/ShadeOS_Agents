#!/usr/bin/env python3
"""
🔍 Import Analyzer - Outil d'analyse des dépendances Python

Outil de production pour analyser les dépendances récursives d'un ou plusieurs fichiers.
Intégré avec le système de partitioning et le TemporalFractalMemoryEngine.

Auteur: Alma (via Lucie Defraiteur)
Date: 2025-08-06
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ImportAnalysisResult:
    """Résultat d'analyse d'imports pour un fichier"""
    
    file_path: str
    imports: List[str] = field(default_factory=list)
    local_imports: List[str] = field(default_factory=list)
    external_imports: List[str] = field(default_factory=list)
    standard_imports: List[str] = field(default_factory=list)
    unresolved_imports: List[str] = field(default_factory=list)
    dependency_depth: int = 0
    import_count: int = 0
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    error_messages: List[str] = field(default_factory=list)


@dataclass
class DependencyGraph:
    """Graphe de dépendances avec détection de cycles"""
    
    nodes: Dict[str, ImportAnalysisResult] = field(default_factory=dict)
    edges: List[tuple] = field(default_factory=list)
    cycles: List[List[str]] = field(default_factory=list)
    
    def add_node(self, file_path: str, analysis_result: ImportAnalysisResult):
        """Ajoute un nœud au graphe"""
        self.nodes[file_path] = analysis_result
    
    def add_edge(self, source: str, target: str):
        """Ajoute une arête au graphe"""
        self.edges.append((source, target))
    
    def detect_cycles(self) -> List[List[str]]:
        """Détecte les cycles dans le graphe de dépendances"""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]):
            if node in rec_stack:
                # Cycle détecté
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            # Parcourir les dépendances
            if node in self.nodes:
                for import_path in self.nodes[node].local_imports:
                    if import_path in self.nodes:
                        dfs(import_path, path.copy())
            
            rec_stack.remove(node)
            path.pop()
        
        # DFS sur tous les nœuds
        for node in self.nodes:
            if node not in visited:
                dfs(node, [])
        
        self.cycles = cycles
        return cycles


class ImportAnalyzer:
    """Analyseur d'imports de production"""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.dependency_graph = DependencyGraph()
        self.import_resolver = None
        self.max_depth = 10
        self.analyzed_files = set()
        
        # Initialiser l'import resolver si disponible
        try:
            from .import_resolver import ImportResolver
            self.import_resolver = ImportResolver()
        except ImportError:
            logger.warning("ImportResolver non disponible, utilisation du résolveur simple")
    
    def analyze_files(self, file_paths: List[str], max_depth: int = None) -> Dict[str, Any]:
        """
        Analyse les dépendances d'une liste de fichiers
        
        Args:
            file_paths: Liste des chemins de fichiers à analyser
            max_depth: Profondeur maximale d'analyse (optionnel)
        
        Returns:
            Dict contenant les résultats d'analyse
        """
        if max_depth:
            self.max_depth = max_depth
        
        logger.info(f"🔍 Début de l'analyse de {len(file_paths)} fichiers")
        
        # Analyser chaque fichier
        for file_path in file_paths:
            if os.path.exists(file_path):
                self._analyze_file_recursive(file_path, depth=0)
            else:
                logger.warning(f"⚠️ Fichier non trouvé: {file_path}")
        
        # Détecter les cycles
        cycles = self.dependency_graph.detect_cycles()
        
        # Générer le rapport
        report = self._generate_analysis_report(file_paths, cycles)
        
        logger.info(f"✅ Analyse terminée: {len(self.dependency_graph.nodes)} fichiers analysés")
        
        return report
    
    def _analyze_file_recursive(self, file_path: str, depth: int = 0, visited: Set[str] = None):
        """Analyse récursive d'un fichier et de ses dépendances"""
        if visited is None:
            visited = set()
        
        # Éviter les cycles et respecter la profondeur maximale
        if depth > self.max_depth or file_path in visited:
            return
        
        visited.add(file_path)
        
        try:
            # Analyser le fichier
            analysis_result = self._analyze_single_file(file_path)
            self.dependency_graph.add_node(file_path, analysis_result)
            
            # Analyser récursivement les imports locaux
            for import_path in analysis_result.local_imports:
                if import_path not in visited:
                    self._analyze_file_recursive(import_path, depth + 1, visited.copy())
                    self.dependency_graph.add_edge(file_path, import_path)
        
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse de {file_path}: {e}")
            error_result = ImportAnalysisResult(
                file_path=file_path,
                error_messages=[str(e)]
            )
            self.dependency_graph.add_node(file_path, error_result)
    
    def _analyze_single_file(self, file_path: str) -> ImportAnalysisResult:
        """Analyse un seul fichier"""
        result = ImportAnalysisResult(file_path=file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraire les imports
            imports = self._extract_imports(content)
            result.imports = imports
            result.import_count = len(imports)
            
            # Classifier les imports
            for import_stmt in imports:
                import_type = self._classify_import(import_stmt, file_path)
                if import_type == 'local':
                    result.local_imports.append(import_stmt)
                elif import_type == 'standard':
                    result.standard_imports.append(import_stmt)
                else:
                    result.external_imports.append(import_stmt)
            
            # Résoudre les imports si possible
            if self.import_resolver:
                resolved_imports = self._resolve_imports(imports, file_path)
                result.unresolved_imports = [imp for imp in imports if imp not in resolved_imports]
            
        except Exception as e:
            result.error_messages.append(str(e))
            logger.error(f"❌ Erreur lors de l'analyse de {file_path}: {e}")
        
        return result
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extrait les imports d'un contenu de fichier"""
        imports = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Imports standards
            if line.startswith('import ') or line.startswith('from '):
                # Nettoyer la ligne
                import_stmt = line.split('#')[0].strip()  # Enlever les commentaires
                if import_stmt:
                    imports.append(import_stmt)
        
        return imports
    
    def _classify_import(self, import_stmt: str, current_file: str) -> str:
        """Classifie un import (local, standard, external)"""
        # Imports standards Python
        standard_modules = {
            'os', 'sys', 'json', 'pathlib', 'typing', 'dataclasses', 
            'asyncio', 'logging', 'datetime', 'collections', 'itertools',
            're', 'math', 'random', 'time', 'threading', 'multiprocessing'
        }
        
        # Extraire le nom du module
        if import_stmt.startswith('from '):
            parts = import_stmt.split(' ')
            if len(parts) >= 2:
                module_name = parts[1].split('.')[0]
            else:
                module_name = ""
        elif import_stmt.startswith('import '):
            parts = import_stmt.split(' ')
            if len(parts) >= 2:
                module_name = parts[1].split('.')[0]
            else:
                module_name = ""
        else:
            module_name = ""
        
        # Classification
        if module_name in standard_modules:
            return 'standard'
        elif module_name.startswith('.') or module_name.startswith('..'):
            return 'local'
        else:
            return 'external'
    
    def _resolve_imports(self, imports: List[str], current_file: str) -> List[str]:
        """Résout les imports en utilisant l'ImportResolver"""
        resolved = []
        
        if not self.import_resolver:
            return resolved
        
        for import_stmt in imports:
            try:
                # Utiliser l'ImportResolver pour résoudre l'import
                resolved_path = self.import_resolver.resolve_import(import_stmt, current_file)
                if resolved_path:
                    resolved.append(import_stmt)
            except Exception as e:
                logger.debug(f"❌ Import non résolu: {import_stmt} -> {e}")
        
        return resolved
    
    def _generate_analysis_report(self, target_files: List[str], cycles: List[List[str]]) -> Dict[str, Any]:
        """Génère un rapport d'analyse complet"""
        
        # Statistiques générales
        total_files = len(self.dependency_graph.nodes)
        total_imports = sum(len(node.imports) for node in self.dependency_graph.nodes.values())
        total_unresolved = sum(len(node.unresolved_imports) for node in self.dependency_graph.nodes.values())
        
        # Fichiers avec le plus d'imports
        files_by_imports = sorted(
            self.dependency_graph.nodes.items(),
            key=lambda x: len(x[1].imports),
            reverse=True
        )[:10]
        
        # Fichiers avec des erreurs
        files_with_errors = [
            file_path for file_path, node in self.dependency_graph.nodes.items()
            if node.error_messages
        ]
        
        report = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'target_files': target_files,
                'total_files_analyzed': total_files,
                'max_depth': self.max_depth
            },
            'statistics': {
                'total_imports': total_imports,
                'unresolved_imports': total_unresolved,
                'cycles_detected': len(cycles),
                'files_with_errors': len(files_with_errors)
            },
            'cycles': cycles,
            'files_with_errors': files_with_errors,
            'top_files_by_imports': [
                {
                    'file_path': file_path,
                    'import_count': len(node.imports),
                    'local_imports': len(node.local_imports),
                    'external_imports': len(node.external_imports),
                    'standard_imports': len(node.standard_imports)
                }
                for file_path, node in files_by_imports
            ],
            'detailed_results': {
                file_path: {
                    'imports': node.imports,
                    'local_imports': node.local_imports,
                    'external_imports': node.external_imports,
                    'standard_imports': node.standard_imports,
                    'unresolved_imports': node.unresolved_imports,
                    'import_count': node.import_count,
                    'error_messages': node.error_messages
                }
                for file_path, node in self.dependency_graph.nodes.items()
            }
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], output_path: str):
        """Sauvegarde le rapport dans un fichier"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"📄 Rapport sauvegardé: {output_path}")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde: {e}")
    
    def generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """Génère un rapport Markdown"""
        
        md_content = f"""# 🔍 Rapport d'Analyse d'Imports

**Date d'analyse :** {report['analysis_metadata']['timestamp']}  
**Fichiers cibles :** {len(report['analysis_metadata']['target_files'])}  
**Fichiers analysés :** {report['statistics']['total_files_analyzed']}

## 📊 Statistiques Générales

- **Total d'imports :** {report['statistics']['total_imports']}
- **Imports non résolus :** {report['statistics']['unresolved_imports']}
- **Cycles détectés :** {report['statistics']['cycles_detected']}
- **Fichiers avec erreurs :** {report['statistics']['files_with_errors']}

## 🔄 Cycles de Dépendances

"""
        
        if report['cycles']:
            for i, cycle in enumerate(report['cycles'], 1):
                md_content += f"**Cycle {i}:** {' -> '.join(cycle)}\n\n"
        else:
            md_content += "✅ Aucun cycle détecté\n\n"
        
        md_content += """## 📈 Top 10 Fichiers par Nombre d'Imports

| Fichier | Imports | Locaux | Externes | Standards |
|---------|---------|--------|----------|-----------|
"""
        
        for file_info in report['top_files_by_imports']:
            md_content += f"| {file_info['file_path']} | {file_info['import_count']} | {file_info['local_imports']} | {file_info['external_imports']} | {file_info['standard_imports']} |\n"
        
        md_content += "\n## ⚠️ Fichiers avec Erreurs\n\n"
        
        if report['files_with_errors']:
            for file_path in report['files_with_errors']:
                md_content += f"- `{file_path}`\n"
        else:
            md_content += "✅ Aucun fichier avec erreurs\n"
        
        return md_content


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="🔍 Analyseur d'imports Python - Outil de production",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python import_analyzer.py file1.py file2.py
  python import_analyzer.py --max-depth 5 file1.py
  python import_analyzer.py --output report.json file1.py file2.py
  python import_analyzer.py --markdown report.md file1.py
        """
    )
    
    parser.add_argument(
        'files',
        nargs='+',
        help='Fichiers Python à analyser'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        default=10,
        help='Profondeur maximale d\'analyse (défaut: 10)'
    )
    
    parser.add_argument(
        '--output',
        help='Fichier de sortie JSON pour le rapport'
    )
    
    parser.add_argument(
        '--markdown',
        help='Fichier de sortie Markdown pour le rapport'
    )
    
    parser.add_argument(
        '--project-root',
        help='Racine du projet (défaut: répertoire courant)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mode verbeux'
    )
    
    args = parser.parse_args()
    
    # Configuration du logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Création de l'analyseur
    analyzer = ImportAnalyzer(project_root=args.project_root)
    
    # Analyse
    print("🔍 Début de l'analyse d'imports...")
    report = analyzer.analyze_files(args.files, max_depth=args.max_depth)
    
    # Affichage des résultats
    print(f"\n📊 Résultats de l'analyse:")
    print(f"  Fichiers analysés: {report['statistics']['total_files_analyzed']}")
    print(f"  Total d'imports: {report['statistics']['total_imports']}")
    print(f"  Imports non résolus: {report['statistics']['unresolved_imports']}")
    print(f"  Cycles détectés: {report['statistics']['cycles_detected']}")
    print(f"  Fichiers avec erreurs: {report['statistics']['files_with_errors']}")
    
    # Sauvegarde des rapports
    if args.output:
        analyzer.save_report(report, args.output)
    
    if args.markdown:
        md_content = analyzer.generate_markdown_report(report)
        with open(args.markdown, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"📄 Rapport Markdown sauvegardé: {args.markdown}")
    
    # Affichage des cycles si présents
    if report['cycles']:
        print(f"\n🔄 Cycles détectés:")
        for i, cycle in enumerate(report['cycles'], 1):
            print(f"  Cycle {i}: {' -> '.join(cycle)}")
    
    print("\n✅ Analyse terminée !")


if __name__ == "__main__":
    main() 