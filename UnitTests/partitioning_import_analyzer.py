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

try:
    from Core.LoggingProviders.base_logging_provider import BaseLoggingProvider
    from Core.LoggingProviders.console_logging_provider import ConsoleLoggingProvider
    from Core.LoggingProviders.file_logging_provider import FileLoggingProvider
    print("✅ Providers de logging importés avec succès!")
except ImportError as e:
    print(f"❌ Erreur import providers: {e}")
    sys.exit(1)


class SimpleImportAnalyzerLogger:
    """Logger simple et direct pour l'analyse d'imports, sans dépendances complexes."""
    
    def __init__(self, log_directory: Optional[str] = None, log_format: str = "json"):
        self.log_directory = log_directory
        self.log_format = log_format
        self.session_id = f"analysis_{int(time.time())}"
        self.start_time = time.time()
        
        # Créer le répertoire de logs si nécessaire
        if log_directory:
            Path(log_directory).mkdir(parents=True, exist_ok=True)
            self.log_file = Path(log_directory) / "imports_analysis.log"
        else:
            self.log_file = None
    
    def _write_log(self, level: str, message: str, data: Dict = None):
        """Écrit un log dans le fichier."""
        if not self.log_file:
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "session_id": self.session_id,
            "message": message
        }
        
        if data:
            log_entry.update(data)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                if self.log_format == "json":
                    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                else:
                    f.write(f"[{timestamp}] {level}: {message}\n")
        except Exception as e:
            print(f"❌ Erreur écriture log: {e}")
    
    def log_analysis_start(self, start_files: List[str]):
        """Log le début d'une analyse."""
        self._write_log("INFO", "🚀 Début analyse", {
            "type": "analysis_start",
            "start_files": start_files,
            "total_start_files": len(start_files)
        })
        print(f"🚀 Début analyse session {self.session_id}")
        print(f"📁 Fichiers de départ: {len(start_files)}")
    
    def log_file_analysis_start(self, file_path: str, depth: int = 0):
        """Log le début de l'analyse d'un fichier."""
        self._write_log("INFO", f"📁 Analyse: {file_path}", {
            "type": "file_analysis_start",
            "file_path": file_path,
            "depth": depth
        })
        indent = '  ' * depth
        print(f"{indent}📁 Analyse: {file_path}")
    
    def log_import_resolution(self, import_name: str, current_file: str, resolved_path: Optional[str], resolution_time: float):
        """Log la résolution d'un import."""
        self._write_log("INFO", f"Import résolu: {import_name}", {
            "type": "import_resolution",
            "import_name": import_name,
            "current_file": current_file,
            "resolved_path": resolved_path,
            "resolution_time": resolution_time,
            "success": resolved_path is not None
        })
        
        if resolved_path:
            print(f"  ✅ {import_name} -> {resolved_path}")
        else:
            print(f"  ❌ {import_name} -> Non résolu")
    
    def log_imports_summary(self, file_path: str, local_imports: List[str], standard_imports: List[str], third_party_imports: List[str]):
        """Log un résumé des imports d'un fichier."""
        self._write_log("INFO", f"Résumé imports: {file_path}", {
            "type": "imports_summary",
            "file_path": file_path,
            "local_imports": local_imports,
            "standard_imports": standard_imports,
            "third_party_imports": third_party_imports,
            "total_imports": len(local_imports) + len(standard_imports) + len(third_party_imports)
        })
        print(f"📊 Résumé {file_path}: {len(local_imports)} locaux, {len(standard_imports)} standard, {len(third_party_imports)} tiers")
    
    def log_file_analysis_complete(self, file_path: str, resolved_count: int, total_imports: int):
        """Log la fin de l'analyse d'un fichier."""
        self._write_log("INFO", f"Analyse terminée: {file_path}", {
            "type": "file_analysis_complete",
            "file_path": file_path,
            "resolved_count": resolved_count,
            "total_imports": total_imports,
            "resolution_rate": resolved_count / total_imports if total_imports > 0 else 0.0
        })
        print(f"  📦 {file_path}: {resolved_count}/{total_imports} résolus")
    
    def log_recursive_analysis_complete(self, all_dependencies: Set[str], unused_files: Set[str]):
        """Log la fin de l'analyse récursive."""
        total_time = time.time() - self.start_time
        self._write_log("INFO", "🎯 Analyse récursive terminée", {
            "type": "recursive_analysis_complete",
            "all_dependencies": list(all_dependencies),
            "unused_files": list(unused_files),
            "total_dependencies": len(all_dependencies),
            "total_unused": len(unused_files),
            "total_time": total_time
        })
        print(f"🎯 Analyse terminée: {len(all_dependencies)} dépendances, {len(unused_files)} non utilisés")
        print(f"⏱️ Temps total: {total_time:.2f}s")
    
    def log_error(self, message: str, error: Exception = None):
        """Log une erreur."""
        error_data = {"type": "error", "message": message}
        if error:
            error_data["error_type"] = type(error).__name__
            error_data["error_details"] = str(error)
        
        self._write_log("ERROR", message, error_data)
        print(f"❌ ERREUR: {message}")
        if error:
            print(f"   Détails: {error}")
    
    def log_warning(self, message: str):
        """Log un avertissement."""
        self._write_log("WARNING", message, {"type": "warning"})
        print(f"⚠️ {message}")
    
    def log_info(self, message: str):
        """Log une information."""
        self._write_log("INFO", message, {"type": "info"})
        print(f"ℹ️ {message}")


class DependencyGraph:
    """Graphe de dépendances avec détection de cycles intelligente."""
    
    def __init__(self):
        self.dependencies = defaultdict(set)
        self.visited = set()
        self.recursion_stack = set()
    
    def add_dependency(self, file_path: str, dependency: str):
        """Ajoute une dépendance si elle ne crée pas de cycle."""
        if not self._would_create_cycle(file_path, dependency):
            self.dependencies[file_path].add(dependency)
    
    def detect_cycles(self) -> List[List[str]]:
        """Détecte tous les cycles dans le graphe."""
        self.visited.clear()
        self.recursion_stack.clear()
        cycles = []
        
        for node in self.dependencies:
            if node not in self.visited:
                self._dfs_cycle_detection(node, [], cycles)
        
        return cycles
    
    def _dfs_cycle_detection(self, node: str, path: List[str], cycles: List[List[str]]):
        """DFS pour détecter les cycles."""
        if node in self.recursion_stack:
            # Cycle détecté
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            cycles.append(cycle)
            return
        
        if node in self.visited:
            return
        
        self.visited.add(node)
        self.recursion_stack.add(node)
        path.append(node)
        
        for neighbor in self.dependencies[node]:
            self._dfs_cycle_detection(neighbor, path, cycles)
        
        path.pop()
        self.recursion_stack.remove(node)
    
    def get_cycle_free_dependencies(self, file_path: str) -> Set[str]:
        """Retourne les dépendances qui ne créent pas de cycles."""
        safe_deps = set()
        for dep in self.dependencies[file_path]:
            if not self._would_create_cycle(file_path, dep):
                safe_deps.add(dep)
        return safe_deps
    
    def _would_create_cycle(self, from_file: str, to_file: str) -> bool:
        """Vérifie si ajouter une dépendance créerait un cycle."""
        if from_file == to_file:
            return True
        
        # BFS pour vérifier s'il existe un chemin de to_file vers from_file
        queue = deque([to_file])
        visited = {to_file}
        
        while queue:
            current = queue.popleft()
            
            for neighbor in self.dependencies[current]:
                if neighbor == from_file:
                    return True  # Cycle détecté
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return False
    
    def get_dependency_stats(self) -> Dict[str, any]:
        """Retourne des statistiques sur le graphe de dépendances."""
        total_files = len(self.dependencies)
        total_deps = sum(len(deps) for deps in self.dependencies.values())
        
        # Top 5 fichiers avec le plus de dépendances
        file_dep_counts = [(file, len(deps)) for file, deps in self.dependencies.items()]
        file_dep_counts.sort(key=lambda x: x[1], reverse=True)
        top_files = file_dep_counts[:5]
        
        return {
            'total_files': total_files,
            'total_dependencies': total_deps,
            'top_files': top_files
        }

class PartitioningImportAnalyzer:
    """Analyseur d'imports utilisant le partitioner pour une analyse précise des dépendances."""
    
    def __init__(self, project_root: str = '.', logging_provider: BaseLoggingProvider = None):
        self.project_root = project_root
        self.partitioner = PythonASTPartitioner()
        self.import_resolver = None
        self.visited = set()
        self.all_dependencies = set()  # Ajout de l'attribut manquant
        self.dependency_graph = DependencyGraph()
        
        # Utiliser le logger simple par défaut
        if logging_provider is None:
            self.logger = SimpleImportAnalyzerLogger()
        else:
            # Si un provider est fourni, créer un logger simple qui l'utilise
            self.logger = SimpleImportAnalyzerLogger()
            # TODO: Adapter pour utiliser le provider si nécessaire
    
    def _get_import_resolver(self):
        """Retourne l'ImportResolver, en le créant si nécessaire."""
        if self.import_resolver is None:
            try:
                from partitioning.import_resolver import ImportResolver
                self.import_resolver = ImportResolver(project_root=self.project_root)
            except ImportError as e:
                self.logger.log_error(f"Impossible d'importer ImportResolver: {e}")
                return None
        return self.import_resolver
    
    def _safe_log(self, method_name: str, *args, **kwargs):
        """Appelle une méthode de logging de manière sécurisée."""
        if hasattr(self.logger, method_name):
            try:
                method = getattr(self.logger, method_name)
                method(*args, **kwargs)
            except Exception as e:
                # Fallback vers les méthodes de base
                self.logger.log_error(f"Erreur dans {method_name}: {e}")
        else:
            # Fallback vers les méthodes de base seulement si la méthode spécialisée n'existe pas
            if method_name == 'log_file_analysis_start':
                self.logger.log_info(f"📁 Analyse: {args[0] if args else 'Unknown'}")
            elif method_name == 'log_import_resolution':
                import_name, file_path, resolved_path = args[:3]
                if resolved_path:
                    self.logger.log_info(f"  ✅ {import_name} -> {resolved_path}")
                else:
                    self.logger.log_warning(f"  ❌ {import_name} -> Non résolu")
            elif method_name == 'log_imports_summary':
                file_path = args[0]
                local_imports, standard_imports, third_party_imports = args[1:4]
                self.logger.log_info(f"📊 Résumé {file_path}: {len(local_imports)} locaux, {len(standard_imports)} standard, {len(third_party_imports)} tiers")
            elif method_name == 'log_file_analysis_complete':
                file_path, resolved_count, total_imports = args[:3]
                self.logger.log_info(f"  📦 {file_path}: {resolved_count}/{total_imports} résolus")
            elif method_name == 'log_analysis_start':
                start_files = args[0] if args else []
                self.logger.log_info(f"🚀 Début analyse avec {len(start_files)} fichiers")
            elif method_name == 'log_recursive_analysis_complete':
                all_dependencies, unused_files = args[:2]
                self.logger.log_info(f"🎯 Analyse terminée: {len(all_dependencies)} dépendances, {len(unused_files)} non utilisés")
    
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
            self.logger.log_error(f'Erreur partitioner {file_path}: {e}')
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
            self.logger.log_error(f'Erreur ImportResolver pour {import_name}: {e}')
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
                self.logger.log_info(f'📁 Déjà visité: {file_path} (profondeur {depth})')
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
                self.logger.log_warning(f'Fichier non trouvé: {file_path}')
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
        print(f'  Cycles détectés: {len(cycles)}') # Use len(cycles) from dependency_graph
        
        if stats['top_files']:
            print(f'\n📈 TOP 5 FICHIERS AVEC LE PLUS DE DÉPENDANCES:')
            for file, count in stats['top_files'][:5]:
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
    """Fonction principale du script d'analyse d'imports."""
    parser = argparse.ArgumentParser(description='Analyseur d\'imports avec partitioner')
    parser.add_argument('--local-only', action='store_true', help='Analyser seulement les imports locaux')
    parser.add_argument('--verbose', action='store_true', help='Mode verbeux')
    parser.add_argument('--debug', action='store_true', help='Mode debug')
    parser.add_argument('--show-cycles', action='store_true', help='Afficher les cycles détectés')
    parser.add_argument('--log-output', action='store_true', help='Activer la sortie de logs')
    parser.add_argument('--log-directory', default='logs', help='Répertoire pour les logs')
    parser.add_argument('--log-format', choices=['json', 'text'], default='json', help='Format des logs')
    parser.add_argument('--use-import-analyzer-provider', action='store_true', help='Utiliser le provider spécialisé')
    
    args = parser.parse_args()
    
    # Configurer le logger simple
    if args.log_output:
        logger = SimpleImportAnalyzerLogger(
            log_directory=args.log_directory,
            log_format=args.log_format
        )
    else:
        logger = SimpleImportAnalyzerLogger()
    
    # Créer l'analyseur avec le logger simple
    analyzer = PartitioningImportAnalyzer(logging_provider=None)  # On utilise le logger simple intégré
    # Remplacer le logger intégré par celui configuré
    analyzer.logger = logger
    
    print("🧠 Détection de cycles intelligente (sans limite de profondeur)")
    print("=" * 60)
    
    # Analyser les dépendances
    analyzer.analyze_autofeeding_dependencies(
        local_only=args.local_only,
        verbose=args.verbose,
        debug=args.debug
    )
    
    # Afficher les résultats
    cycles = analyzer.dependency_graph.detect_cycles()
    stats = analyzer.dependency_graph.get_dependency_stats()
    
    if cycles:
        print(f'\n🔄 CYCLES DÉTECTÉS: {len(cycles)}')
        for i, cycle in enumerate(cycles, 1):
            print(f'  Cycle {i}: {" -> ".join(cycle)}')
    else:
        print('\n✅ Aucun cycle détecté')
    
    print(f'\n📊 STATISTIQUES DU GRAPHE:')
    print(f'  Fichiers analysés: {stats["total_files"]}')
    print(f'  Dépendances totales: {stats["total_dependencies"]}')
    print(f'  Cycles détectés: {len(cycles)}')
    
    if stats['top_files']:
        print(f'\n📈 TOP 5 FICHIERS AVEC LE PLUS DE DÉPENDANCES:')
        for file, count in stats['top_files'][:5]:
            print(f'  {file}: {count} dépendances')
    
    print(f'\n📊 TOTAL FICHIERS AVEC IMPORTS LOCAUX: {len(analyzer.visited)}')
    
    print('\n🎯 ANALYSE TERMINÉE !')
    print(f'📊 Fichiers avec imports locaux: {len(analyzer.visited)}')
    
    # Afficher le rapport final
    print('\n📊 RAPPORT D\'ANALYSE:')
    print(f'  Session ID: {logger.session_id}')
    total_time = time.time() - logger.start_time
    print(f'  Temps total: {total_time:.2f}s')
    print(f'  Fichiers analysés: {len(analyzer.visited)}')
    print(f'  Imports résolus: {stats["total_dependencies"]}')

if __name__ == '__main__':
    main() 