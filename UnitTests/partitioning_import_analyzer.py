#!/usr/bin/env python3
"""
Analyseur d'imports utilisant le partitioner pour une analyse précise
des dépendances des auto-feeding threads.
"""

import os
import sys
import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Set, List, Dict, Optional, Tuple
from collections import defaultdict, deque

# Ajouter le chemin pour importer le partitioner
sys.path.append('Assistants/EditingSession')

# Ajouter le répertoire racine pour les imports Core
sys.path.append('.')

try:
    from partitioning.ast_partitioners import PythonASTPartitioner
    from partitioning.partition_schemas import PartitioningError
    print("✅ Partitioner importé avec succès!")
except ImportError as e:
    print(f"❌ Erreur import partitioner: {e}")
    sys.exit(1)

# Importer les providers de logging
from Core.LoggingProviders import (
    BaseLoggingProvider,
    FileLoggingProvider,
    ConsoleLoggingProvider,
    ImportAnalyzerLoggingProvider
)
print("✅ Providers de logging importés avec succès!")

class DependencyGraph:
    """Graphe de dépendances avec détection de cycles intelligente."""
    
    def __init__(self):
        self.graph = defaultdict(set)  # file -> set of dependencies
        self.reverse_graph = defaultdict(set)  # dependency -> set of files that depend on it
        self.visited = set()
        self.recursion_stack = set()
        self.cycle_detected = False
        self.cycles = []
        
    def add_dependency(self, file_path: str, dependency: str):
        """Ajoute une dépendance au graphe."""
        if dependency and dependency != file_path:  # Éviter les auto-dépendances
            self.graph[file_path].add(dependency)
            self.reverse_graph[dependency].add(file_path)
    
    def detect_cycles(self) -> List[List[str]]:
        """Détecte tous les cycles dans le graphe de dépendances."""
        self.cycles = []
        self.visited.clear()
        self.recursion_stack.clear()
        
        for node in self.graph:
            if node not in self.visited:
                self._dfs_cycle_detection(node, [])
        
        return self.cycles
    
    def _dfs_cycle_detection(self, node: str, path: List[str]):
        """DFS pour détecter les cycles."""
        if node in self.recursion_stack:
            # Cycle détecté !
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            self.cycles.append(cycle)
            return
        
        if node in self.visited:
            return
        
        self.visited.add(node)
        self.recursion_stack.add(node)
        path.append(node)
        
        for dependency in self.graph[node]:
            self._dfs_cycle_detection(dependency, path)
        
        path.pop()
        self.recursion_stack.remove(node)
    
    def get_cycle_free_dependencies(self, file_path: str) -> Set[str]:
        """Retourne les dépendances d'un fichier en excluant celles qui créeraient des cycles."""
        if file_path not in self.graph:
            return set()
        
        safe_dependencies = set()
        for dependency in self.graph[file_path]:
            # Vérifier si cette dépendance créerait un cycle
            if not self._would_create_cycle(file_path, dependency):
                safe_dependencies.add(dependency)
            else:
                # Log du cycle évité
                print(f"🔄 Cycle évité: {file_path} -> {dependency}")
        
        return safe_dependencies
    
    def _would_create_cycle(self, from_file: str, to_file: str) -> bool:
        """Vérifie si ajouter une dépendance créerait un cycle."""
        # Vérifier s'il existe un chemin de to_file vers from_file
        visited = set()
        queue = deque([to_file])
        
        while queue:
            current = queue.popleft()
            if current == from_file:
                return True  # Cycle détecté
            
            if current in visited:
                continue
                
            visited.add(current)
            
            for dependency in self.graph[current]:
                if dependency not in visited:
                    queue.append(dependency)
        
        return False
    
    def get_dependency_stats(self) -> Dict[str, any]:
        """Retourne des statistiques sur le graphe de dépendances."""
        total_nodes = len(self.graph)
        total_edges = sum(len(deps) for deps in self.graph.values())
        
        # Trouver les fichiers avec le plus de dépendances
        dependency_counts = [(file, len(deps)) for file, deps in self.graph.items()]
        dependency_counts.sort(key=lambda x: x[1], reverse=True)
        
        # Trouver les fichiers les plus dépendus
        reverse_counts = [(file, len(self.reverse_graph[file])) for file in self.reverse_graph]
        reverse_counts.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'total_files': total_nodes,
            'total_dependencies': total_edges,
            'cycles_detected': len(self.cycles),
            'top_dependents': dependency_counts[:10],
            'top_dependencies': reverse_counts[:10],
            'cycles': self.cycles
        }

class PartitioningImportAnalyzer:
    def __init__(self, project_root: str = '.', logging_provider: BaseLoggingProvider = None):
        self.project_root = Path(project_root)
        self.visited = set()
        self.all_dependencies = set()
        self.partitioner = PythonASTPartitioner()
        self.logging_provider = logging_provider or ConsoleLoggingProvider()
        
        # Cache pour l'ImportResolver pour éviter les reconstructions
        self._import_resolver = None
        self._resolver_cache_built = False
        
        # Graphe de dépendances intelligent
        self.dependency_graph = DependencyGraph()
        
    def _get_import_resolver(self):
        """Retourne l'ImportResolver avec cache optimisé."""
        if self._import_resolver is None:
            try:
                from partitioning.import_resolver import ImportResolver
                self._import_resolver = ImportResolver(str(self.project_root))
            except Exception as e:
                self.logging_provider.log_error(f'Erreur création ImportResolver: {e}')
                return None
        return self._import_resolver
        
    def _safe_log(self, method_name: str, *args, **kwargs):
        """Appelle une méthode de logging de manière sécurisée."""
        if hasattr(self.logging_provider, method_name):
            try:
                method = getattr(self.logging_provider, method_name)
                method(*args, **kwargs)
            except Exception as e:
                # Fallback vers les méthodes de base
                self.logging_provider.log_error(f"Erreur dans {method_name}: {e}")
        else:
            # Fallback vers les méthodes de base
            if method_name == 'log_file_analysis_start':
                self.logging_provider.log_info(f"📁 Analyse: {args[0] if args else 'Unknown'}")
            elif method_name == 'log_import_resolution':
                import_name, file_path, resolved_path = args[:3]
                if resolved_path:
                    self.logging_provider.log_info(f"  ✅ {import_name} -> {resolved_path}")
                else:
                    self.logging_provider.log_warning(f"  ❌ {import_name} -> Non résolu")
            elif method_name == 'log_imports_summary':
                file_path = args[0]
                local_imports, standard_imports, third_party_imports = args[1:4]
                self.logging_provider.log_info(f"📊 Résumé {file_path}: {len(local_imports)} locaux, {len(standard_imports)} standard, {len(third_party_imports)} tiers")
            elif method_name == 'log_file_analysis_complete':
                file_path, resolved_count, total_imports = args[:3]
                self.logging_provider.log_info(f"  📦 {file_path}: {resolved_count}/{total_imports} résolus")
            elif method_name == 'log_analysis_start':
                start_files = args[0] if args else []
                self.logging_provider.log_info(f"🚀 Début analyse avec {len(start_files)} fichiers")
            elif method_name == 'log_recursive_analysis_complete':
                all_dependencies, unused_files = args[:2]
                self.logging_provider.log_info(f"🎯 Analyse terminée: {len(all_dependencies)} dépendances, {len(unused_files)} non utilisés")
        
    def extract_imports_with_partitioner(self, file_path: str) -> List[str]:
        """Extrait tous les imports d'un fichier Python avec le partitioner."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parser avec le partitioner
            tree = self.partitioner.parse_content(content, file_path)
            
            # Analyser les imports
            import_analysis = self.partitioner.extract_import_analysis(tree)
            
            # Utiliser la nouvelle liste unifiée
            if 'all_imports' in import_analysis:
                return import_analysis['all_imports']
            
            # Fallback sur l'ancienne méthode si pas de all_imports
            all_imports = []
            
            # Imports de la bibliothèque standard
            for import_info in import_analysis.get('standard_library', []):
                if isinstance(import_info, str):
                    all_imports.append(import_info)
                elif isinstance(import_info, dict):
                    module = import_info['module']
                    for name in import_info['names']:
                        all_imports.append(f"{module}.{name}")
            
            # Imports tiers
            for import_info in import_analysis.get('third_party', []):
                if isinstance(import_info, str):
                    all_imports.append(import_info)
                elif isinstance(import_info, dict):
                    module = import_info['module']
                    for name in import_info['names']:
                        all_imports.append(f"{module}.{name}")
            
            # Imports relatifs
            for import_info in import_analysis.get('relative_imports', []):
                module = import_info['module']
                level = import_info['level']
                for name in import_info['names']:
                    # Construire l'import relatif
                    dots = '.' * level
                    if module:
                        all_imports.append(f"{dots}{module}.{name}")
                    else:
                        all_imports.append(f"{dots}{name}")
            
            return all_imports
            
        except Exception as e:
            self.logging_provider.log_error(f'Erreur partitioner {file_path}: {e}')
            return []
    
    def find_file_for_import(self, import_name: str, current_file: str) -> Optional[str]:
        """Trouve le fichier correspondant à un import en utilisant l'ImportResolver."""
        try:
            resolver = self._get_import_resolver()
            if resolver is None:
                return None
                
            # Vérifier si c'est un import de bibliothèque standard
            if self._is_standard_library_import(import_name):
                return None  # Ne pas résoudre les imports standard
                
            return resolver.resolve_import(import_name, current_file)
        except Exception as e:
            self.logging_provider.log_error(f'Erreur ImportResolver pour {import_name}: {e}')
            return None
    
    def _is_standard_library_import(self, import_name: str) -> bool:
        """Vérifie si un import fait partie de la bibliothèque standard."""
        standard_modules = {
            'time', 'json', 'os', 'sys', 'pathlib', 'typing', 'dataclasses', 
            'collections', 'abc', 're', 'asyncio', 'enum', 'datetime', 'logging',
            'argparse', 'functools', 'itertools', 'contextlib', 'threading',
            'multiprocessing', 'subprocess', 'tempfile', 'shutil', 'glob',
            'fnmatch', 'pickle', 'copy', 'weakref', 'types', 'inspect',
            'traceback', 'warnings', 'unittest', 'doctest', 'pdb', 'profile',
            'cProfile', 'timeit', 'dis', 'pickletools', 'tabnanny', 'py_compile',
            'compileall', 'keyword', 'token', 'tokenize', 'ast', 'symtable',
            'code', 'codeop', 'zipimport', 'pkgutil', 'modulefinder', 'runpy',
            'importlib', 'importlib.util', 'importlib.machinery', 'importlib.abc'
        }
        
        # Extraire le module principal
        module_name = import_name.split('.')[0]
        return module_name in standard_modules
    
    def analyze_file_recursively(self, file_path: str, depth: int = 0, 
                               local_only: bool = False, verbose: bool = False, debug: bool = False):
        """Analyse récursivement un fichier et ses dépendances avec détection de cycles intelligente."""
        if file_path in self.visited:
            if verbose:
                self.logging_provider.log_info(f'📁 Déjà visité: {file_path} (profondeur {depth})')
            return
        
        self.visited.add(file_path)
        self.all_dependencies.add(file_path)
        
        # Log du début d'analyse du fichier
        self._safe_log('log_file_analysis_start', file_path, depth)
        
        imports = self.extract_imports_with_partitioner(file_path)
        indent = '  ' * depth
        
        if not local_only or verbose:
            print(f'{indent}📁 {file_path}')
            print(f'{indent}   Imports (partitioner): {imports}')
        
        resolved_count = 0
        local_imports = []
        standard_imports = []
        third_party_imports = []
        
        for import_name in imports:
            # Éviter les imports de bibliothèque standard en mode local_only
            if local_only and self._is_standard_library_import(import_name):
                continue
                
            start_time = time.time()
            local_file = self.find_file_for_import(import_name, file_path)
            resolution_time = time.time() - start_time
            
            # Log de la résolution d'import
            self._safe_log('log_import_resolution', import_name, file_path, local_file, resolution_time)
            
            if local_file and os.path.exists(local_file):
                # Ajouter au graphe de dépendances
                self.dependency_graph.add_dependency(file_path, local_file)
                
                # Vérifier si cette dépendance créerait un cycle
                if not self.dependency_graph._would_create_cycle(file_path, local_file):
                    resolved_count += 1
                    local_imports.append((import_name, local_file))
                    if not local_only or verbose:
                        print(f'{indent}   ✅ {import_name} -> {local_file}')
                    # Récursion seulement si pas de cycle
                    if local_file not in self.visited:
                        self.analyze_file_recursively(local_file, depth + 1, local_only, verbose, debug)
                else:
                    if verbose:
                        print(f'{indent}   🔄 Cycle évité: {import_name} -> {local_file}')
            else:
                if not local_only or verbose:
                    print(f'{indent}   ❌ {import_name} -> Non résolu')
        
        # Log du résumé des imports
        self._safe_log('log_imports_summary', file_path, 
                      [imp[0] for imp in local_imports], standard_imports, third_party_imports)
        
        if local_only and local_imports:
            print(f'{indent}📁 {file_path}')
            print(f'{indent}   Imports locaux:')
            for import_name, local_file in local_imports:
                print(f'{indent}   ✅ {import_name} -> {local_file}')
        
        # Log de la fin d'analyse du fichier
        self._safe_log('log_file_analysis_complete', file_path, resolved_count, len(imports))
        
        if resolved_count > 0 and (not local_only or verbose):
            print(f'{indent}   📦 Résolus: {resolved_count}')
    
    def analyze_autofeeding_dependencies(self, local_only: bool = False, verbose: bool = False, debug: bool = False):
        """Analyse les dépendances des auto-feeding threads."""
        autofeeding_files = [
            'Assistants/Generalist/V9_AutoFeedingThreadAgent.py',
            'Daemons/DaemonTeam/LegionAutoFeedingThread.py',
            'Daemons/DaemonTeam/LegionAutoFeedingThread_v2.py',
            'Core/UniversalAutoFeedingThread/base_auto_feeding_thread.py',
            'Core/UniversalAutoFeedingThread/universal_auto_feeding_thread.py'
        ]
        
        # Log du début d'analyse
        self._safe_log('log_analysis_start', autofeeding_files)
        
        if local_only:
            print('🎯 Analyse RÉCURSIVE - IMPORTS LOCAUX SEULEMENT...')
        else:
            print('🔍 Analyse RÉCURSIVE avec PARTITIONER...')
        print('🔄 Détection de cycles intelligente activée')
        print('=' * 80)
        
        for file_path in autofeeding_files:
            if os.path.exists(file_path):
                if not local_only:
                    print(f'\n📁 DÉPART: {file_path}')
                    print('-' * 60)
                self.analyze_file_recursively(file_path, local_only=local_only, verbose=verbose, debug=debug)
            else:
                self.logging_provider.log_warning(f'Fichier non trouvé: {file_path}')
                print(f'⚠️ Fichier non trouvé: {file_path}')
        
        # Analyser les cycles détectés
        cycles = self.dependency_graph.detect_cycles()
        if cycles:
            print(f'\n🔄 CYCLES DÉTECTÉS: {len(cycles)}')
            for i, cycle in enumerate(cycles, 1):
                print(f'  Cycle {i}: {" -> ".join(cycle)}')
        else:
            print(f'\n✅ AUCUN CYCLE DÉTECTÉ')
        
        # Statistiques du graphe
        stats = self.dependency_graph.get_dependency_stats()
        print(f'\n📊 STATISTIQUES DU GRAPHE:')
        print(f'  Fichiers analysés: {stats["total_files"]}')
        print(f'  Dépendances totales: {stats["total_dependencies"]}')
        print(f'  Cycles détectés: {stats["cycles_detected"]}')
        
        if stats['top_dependents']:
            print(f'\n📈 TOP 5 FICHIERS AVEC LE PLUS DE DÉPENDANCES:')
            for file, count in stats['top_dependents'][:5]:
                print(f'  {file}: {count} dépendances')
        
        if not local_only:
            print(f'\n📊 TOTAL DÉPENDANCES: {len(self.all_dependencies)}')
            print('\n📋 Liste complète des dépendances:')
            for dep in sorted(self.all_dependencies):
                print(f'  {dep}')
            
            # Trouver tous les fichiers Python du projet
            all_py_files = set()
            for root, dirs, files in os.walk(self.project_root):
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache']]
                for file in files:
                    if file.endswith('.py'):
                        all_py_files.add(str(Path(root) / file))
            
            unused_files = all_py_files - self.all_dependencies
            print(f'\n🗑️ FICHIERS NON UTILISÉS: {len(unused_files)}')
            print('\n📋 Premiers fichiers non utilisés:')
            for file_path in sorted(unused_files)[:20]:
                print(f'  {file_path}')
        else:
            print(f'\n📊 TOTAL FICHIERS AVEC IMPORTS LOCAUX: {len(self.all_dependencies)}')
        
        # Log de la fin d'analyse
        unused_files = set() if local_only else unused_files
        self._safe_log('log_recursive_analysis_complete', self.all_dependencies, unused_files)
        
        return self.all_dependencies, unused_files if not local_only else set()

def main():
    parser = argparse.ArgumentParser(description='Analyse récursive des imports - Alma Diabolique')
    parser.add_argument('--local-only', action='store_true', 
                       help='Afficher seulement les imports locaux (fichiers du projet)')
    parser.add_argument('--verbose', action='store_true',
                       help='Afficher les détails de résolution des imports')
    parser.add_argument('--debug', action='store_true',
                       help='Mode debug avec tous les logs')
    parser.add_argument('--log-output', action='store_true',
                       help='Sauvegarder les logs dans des fichiers')
    parser.add_argument('--log-directory', type=str, default='logs',
                       help='Répertoire pour les logs (défaut: logs)')
    parser.add_argument('--log-format', choices=['json', 'text'], default='json',
                       help='Format des logs (défaut: json)')
    parser.add_argument('--use-import-analyzer-provider', action='store_true',
                       help='Utiliser le provider spécialisé ImportAnalyzerLoggingProvider')
    parser.add_argument('--show-cycles', action='store_true',
                       help='Afficher les cycles de dépendances détectés')
    
    args = parser.parse_args()
    
    print("🕷️ ANALYSE RÉCURSIVE DES IMPORTS - ALMA DIABOLIQUE ⛧")
    print("=" * 60)
    
    if args.local_only:
        print("🎯 MODE: Imports locaux seulement")
    if args.verbose:
        print("🔍 MODE: Verbose activé")
    if args.debug:
        print("🐛 MODE: Debug activé")
    if args.log_output:
        print(f"📝 MODE: Logs dans {args.log_directory}")
    if args.use_import_analyzer_provider:
        print("🔧 MODE: Provider ImportAnalyzerLoggingProvider")
    if args.show_cycles:
        print("🔄 MODE: Affichage des cycles activé")
    print("🧠 Détection de cycles intelligente (sans limite de profondeur)")
    print()
    
    # Configurer le provider de logging
    if args.use_import_analyzer_provider:
        # Si log_output est activé, créer un FileLoggingProvider comme base
        if args.log_output:
            base_provider = FileLoggingProvider(
                log_directory=args.log_directory,
                log_format=args.log_format
            )
            # Créer l'ImportAnalyzerLoggingProvider en héritant du FileLoggingProvider
            logging_provider = ImportAnalyzerLoggingProvider(
                log_resolution_details=args.verbose,
                log_performance_metrics=args.debug,
                log_directory=args.log_directory,
                log_format=args.log_format
            )
        else:
            logging_provider = ImportAnalyzerLoggingProvider(
                log_resolution_details=args.verbose,
                log_performance_metrics=args.debug
            )
    elif args.log_output:
        logging_provider = FileLoggingProvider(
            log_directory=args.log_directory,
            log_format=args.log_format
        )
    else:
        logging_provider = ConsoleLoggingProvider(
            use_colors=True,
            compact_format=not args.verbose
        )
    
    analyzer = PartitioningImportAnalyzer(logging_provider=logging_provider)
    dependencies, unused = analyzer.analyze_autofeeding_dependencies(
        local_only=args.local_only, 
        verbose=args.verbose, 
        debug=args.debug
    )
    
    print(f'\n🎯 ANALYSE TERMINÉE !')
    if args.local_only:
        print(f'📊 Fichiers avec imports locaux: {len(dependencies)}')
    else:
        print(f'📊 Dépendances: {len(dependencies)}')
        print(f'🗑️ Non utilisés: {len(unused)}')
    
    # Afficher les cycles si demandé
    if args.show_cycles:
        cycles = analyzer.dependency_graph.detect_cycles()
        if cycles:
            print(f'\n🔄 CYCLES DÉTECTÉS: {len(cycles)}')
            for i, cycle in enumerate(cycles, 1):
                print(f'  Cycle {i}: {" -> ".join(cycle)}')
        else:
            print(f'\n✅ AUCUN CYCLE DÉTECTÉ')
    
    # Afficher les fichiers de logs si mode log
    if args.log_output and isinstance(logging_provider, FileLoggingProvider):
        print(f'\n📁 FICHIERS DE LOGS:')
        for name, path in logging_provider.get_log_files().items():
            if path.exists():
                print(f'  {name}: {path}')
    
    # Afficher le rapport d'analyse si provider spécialisé
    if args.use_import_analyzer_provider and isinstance(logging_provider, ImportAnalyzerLoggingProvider):
        report = logging_provider.get_analysis_report()
        print(f'\n📊 RAPPORT D\'ANALYSE:')
        print(f'  Session ID: {report["session_id"]}')
        print(f'  Temps total: {report["total_time"]:.2f}s')
        print(f'  Fichiers analysés: {report["stats"]["files_analyzed"]}')
        print(f'  Imports résolus: {report["stats"]["imports_resolved"]}')

if __name__ == '__main__':
    main() 