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

# Ajouter le répertoire racine pour les imports Core
sys.path.append('.')

try:
    from Core.Partitioner.ast_partitioners.python_ast_partitioner import PythonASTPartitioner
    from Core.Partitioner.partition_schemas import PartitioningError
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

# Importer l'ImportResolver existant
try:
    from Core.Partitioner.import_resolver import ImportResolver
    print("✅ ImportResolver importé avec succès!")
except ImportError as e:
    print(f"⚠️ Erreur import ImportResolver: {e}")
    ImportResolver = None


class SimpleImportAnalyzerLogger:
    """Logger simple et direct pour l'analyse d'imports, sans dépendances complexes."""
    
    def __init__(self, log_directory: Optional[str] = None, log_format: str = "json", project_root: str = "."):
        self.log_directory = log_directory
        self.log_format = log_format
        self.project_root = project_root
        self.session_id = f"analysis_{int(time.time())}"
        self.start_time = time.time()
        self.analysis_data = {
            'files_analyzed': [],
            'imports_found': {},
            'cycles_detected': [],
            'stats': {}
        }
        
        # Pré-construction du rapport markdown en mémoire
        self.md_sections = []
        self.files_data = {}  # Dictionnaire pour éviter les doublons: {file_path: {depth, imports}}
        self.cycles_detected = []
        
        # Créer le répertoire de logs si nécessaire
        if log_directory:
            Path(log_directory).mkdir(parents=True, exist_ok=True)
            # Créer le sous-répertoire imports_analysis
            imports_analysis_dir = Path(log_directory) / "imports_analysis"
            imports_analysis_dir.mkdir(parents=True, exist_ok=True)
            
            # Fichier de log JSON
            self.log_file = imports_analysis_dir / "imports_analysis.log"
            
            # Fichier de rapport Markdown
            self.md_file = imports_analysis_dir / "imports_analysis_report.md"
        else:
            self.log_file = None
            self.md_file = None
    
    def _init_md_report(self):
        """Initialise le rapport Markdown avec l'en-tête."""
        if self.md_file:
            header = f"""# 📊 Rapport d'Analyse d'Imports

**Session ID:** `{self.session_id}`  
**Date:** {datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')}  
**Format:** Analyse des dépendances Python avec détection de cycles intelligente

---

## 🎯 Résumé Exécutif

*Ce rapport détaille l'analyse des imports Python dans le projet, incluant les dépendances locales, les cycles détectés et les statistiques d'analyse.*

---

## 📁 Liste Simple des Fichiers Parcourus

*Liste complète de tous les fichiers analysés (style "ls récursif") :*

"""
            self.md_sections.append(header)
    
    def _write_md_section(self, content: str):
        """Ajoute une section au rapport markdown en mémoire."""
        self.md_sections.append(content)
    
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
    
    def log_warning(self, message: str, **kwargs):
        """Log un avertissement."""
        self._write_log("WARNING", message, {"type": "warning"})
        print(f"⚠️ {message}")
        if 'cycle' in kwargs:
            self.cycles_detected.append(kwargs['cycle'])
    
    def log_info(self, message: str, **kwargs):
        """Log un message d'information."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = {
            'timestamp': timestamp,
            'level': 'INFO',
            'message': message,
            'session_id': self.session_id,
            **kwargs
        }
        
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        # Ajouter au rapport Markdown si c'est un message d'analyse
        if 'file' in kwargs:
            self._add_file_to_md_report(kwargs['file'], kwargs.get('imports', []), kwargs.get('depth', 0))
        elif 'cycle' in kwargs:
            self.cycles_detected.append(kwargs['cycle'])
    
    def _add_file_to_md_report(self, file_path: str, imports: List[str], depth: int):
        """Ajoute un fichier analysé au rapport Markdown (en mémoire)."""
        # Convertir le chemin absolu en chemin relatif
        try:
            relative_path = os.path.relpath(file_path, self.project_root)
        except ValueError:
            # Si le fichier n'est pas dans le projet, garder le chemin absolu
            relative_path = file_path
        
        # Stocker dans le dictionnaire pour éviter les doublons
        if relative_path not in self.files_data:
            self.files_data[relative_path] = {
                'depth': depth,
                'imports': imports
            }
        else:
            # Si le fichier est déjà présent, mettre à jour la profondeur et les imports
            # Garder la profondeur la plus élevée (plus de détails)
            if depth > self.files_data[relative_path]['depth']:
                self.files_data[relative_path]['depth'] = depth
            # Fusionner les imports (éviter les doublons)
            existing_imports = set(self.files_data[relative_path]['imports'])
            new_imports = set(imports)
            self.files_data[relative_path]['imports'] = list(existing_imports | new_imports)
    
    def _add_cycle_to_md_report(self, cycle: List[str]):
        """Ajoute un cycle détecté au rapport Markdown (en mémoire)."""
        self.cycles_detected.append(cycle)
    
    def log_debug(self, message: str, **kwargs):
        """Log un message de debug."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = {
            'timestamp': timestamp,
            'level': 'DEBUG',
            'message': message,
            'session_id': self.session_id,
            **kwargs
        }
        
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def log_structured(self, level: str, message: str, **kwargs):
        """Log un message structuré."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = {
            'timestamp': timestamp,
            'level': level.upper(),
            'message': message,
            'session_id': self.session_id,
            **kwargs
        }
        
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def finalize_report(self, stats: Dict):
        """Finalise le rapport Markdown en écrivant tout le contenu pré-construit."""
        if not self.md_file:
            return
        
        # Initialiser l'en-tête
        self._init_md_report()
        
        # Générer la liste simple des fichiers parcourus
        files_list = []
        for file_path in sorted(self.files_data.keys()):
            files_list.append(f"`{file_path}`")
        
        # Ajouter la liste simple des fichiers
        files_section = "\n".join(files_list)
        self._write_md_section(files_section)
        
        # Section de l'arbre ASCII structurel
        tree_section = """

---

## 🌳 Arbre Structurel des Fichiers

*Représentation visuelle de la hiérarchie des fichiers analysés :*

"""
        self._write_md_section(tree_section)
        
        # Générer l'arbre ASCII structurel relatif
        ascii_tree = self._generate_ascii_tree()
        self._write_md_section(ascii_tree)
        
        # Section des imports
        imports_section = """

---

## 📋 Liste Simple des Imports (Style "ls récursif")

*Liste simplifiée de tous les imports locaux trouvés, organisés par fichier :*

"""
        self._write_md_section(imports_section)
        
        # Générer la liste simple des imports à partir du dictionnaire
        simple_entries = []
        for file_path, file_data in sorted(self.files_data.items()):
            simple_entry = f"**{file_path}** (profondeur {file_data['depth']}):"
            if file_data['imports']:
                for imp in sorted(file_data['imports']):
                    simple_entry += f"\n  - `{imp}`"
            else:
                simple_entry += "\n  - *Aucun import local*"
            simple_entries.append(simple_entry)
        
        # Ajouter la liste simple des imports
        simple_section = "\n\n".join(simple_entries)
        self._write_md_section(simple_section)
        
        # Section détaillée
        detailed_section = """

---

## 📁 Analyse Détaillée par Fichier

"""
        self._write_md_section(detailed_section)
        
        # Ajouter chaque fichier avec ses détails
        for file_path, file_data in sorted(self.files_data.items()):
            indent = "  " * file_data['depth']
            section = f"""
### {indent}📄 {Path(file_path).name}

**Chemin:** `{file_path}`  
**Profondeur:** {file_data['depth']}

**Imports trouvés ({len(file_data['imports'])}):**
"""
            
            if file_data['imports']:
                for imp in sorted(file_data['imports']):
                    section += f"- `{imp}`\n"
            else:
                section += "- *Aucun import local trouvé*\n"
            
            self._write_md_section(section)
        
        # Section des cycles
        if self.cycles_detected:
            cycles_section = """

---

## ⚠️ Cycles Détectés

"""
            for i, cycle in enumerate(self.cycles_detected, 1):
                cycles_section += f"""
### Cycle {i}

**Fichiers impliqués:**
"""
                for j, file_path in enumerate(cycle, 1):
                    file_name = Path(file_path).name
                    cycles_section += f"{j}. `{file_path}` ({file_name})\n"
            
            self._write_md_section(cycles_section)
        
        # Statistiques finales
        end_time = time.time()
        duration = end_time - self.start_time
        
        summary = f"""
---

## 📈 Statistiques d'Analyse

**Durée totale:** {duration:.2f} secondes  
**Fichiers analysés:** {stats.get('files_analyzed', 0)}  
**Imports locaux trouvés:** {stats.get('local_imports', 0)}  
**Cycles détectés:** {stats.get('cycles_detected', 0)}  
**Profondeur maximale:** {stats.get('max_depth', 0)}

### 🔍 Détails par Type d'Import

"""
        
        import_types = stats.get('import_types', {})
        for import_type, count in import_types.items():
            summary += f"- **{import_type}:** {count}\n"
        
        summary += f"""
---

## 🎯 Recommandations

"""
        
        if stats.get('cycles_detected', 0) > 0:
            summary += """
### ⚠️ Cycles Détectés
Des cycles de dépendances ont été détectés. Considérez:
- Refactoriser les imports circulaires
- Utiliser des imports conditionnels
- Séparer les responsabilités des modules
"""
        else:
            summary += """
### ✅ Aucun Cycle Détecté
La structure des imports est saine, aucune action requise.
"""
        
        summary += f"""
---

*Rapport généré automatiquement le {datetime.now().strftime('%Y-%m-%d à %H:%M:%S')}*
"""
        
        self._write_md_section(summary)
        
        # Écrire tout le rapport d'un coup
        with open(self.md_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.md_sections))

    def _generate_ascii_tree(self) -> str:
        """Génère un arbre ASCII structurel relatif des fichiers analysés."""
        from collections import defaultdict
        
        # Créer une structure d'arbre hiérarchique
        tree = defaultdict(lambda: defaultdict(set))
        
        for file_path in self.files_data.keys():
            # Le file_path est déjà un chemin relatif maintenant
            rel_path = file_path
            
            # Séparer le chemin en parties
            parts = rel_path.split(os.sep)
            
            if len(parts) == 1:
                # Fichier à la racine
                tree['.']['files'].add(parts[0])
            elif len(parts) == 2:
                # Fichier dans un sous-dossier direct
                tree[parts[0]]['files'].add(parts[1])
            else:
                # Fichier dans un sous-dossier profond
                current_level = tree[parts[0]]
                for i in range(1, len(parts) - 1):
                    if parts[i] not in current_level:
                        current_level[parts[i]] = defaultdict(set)
                    current_level = current_level[parts[i]]
                current_level['files'].add(parts[-1])
        
        # Générer l'arbre ASCII
        tree_lines = []
        tree_lines.append("```")
        
        def add_directory(dir_name, content, prefix="", is_last=True):
            if dir_name == '.':
                tree_lines.append(".")
            else:
                tree_lines.append(f"{prefix}📁 {dir_name}/")
            
            # Ajouter les sous-dossiers
            subdirs = [(k, v) for k, v in content.items() if k != 'files']
            for i, (subdir_name, subdir_content) in enumerate(sorted(subdirs)):
                is_subdir_last = (i == len(subdirs) - 1) and not content.get('files')
                sub_prefix = "└── " if is_subdir_last else "├── "
                new_prefix = prefix + ("    " if is_subdir_last else "│   ")
                add_directory(subdir_name, subdir_content, new_prefix, is_subdir_last)
            
            # Ajouter les fichiers
            files = sorted(content.get('files', []))
            for i, file_name in enumerate(files):
                is_file_last = (i == len(files) - 1)
                file_prefix = "└── " if is_file_last else "├── "
                tree_lines.append(f"{prefix}{file_prefix}📄 {file_name}")
        
        # Traiter les dossiers principaux
        main_dirs = sorted(tree.keys())
        for i, dir_name in enumerate(main_dirs):
            is_last = (i == len(main_dirs) - 1)
            add_directory(dir_name, tree[dir_name], "", is_last)
        
        tree_lines.append("```")
        return "\n".join(tree_lines)


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
        self.project_root = os.path.abspath(project_root)
        self.logging_provider = logging_provider
        self.logger = SimpleImportAnalyzerLogger(project_root=self.project_root)
        
        # Cache pour les modules locaux détectés
        self._local_modules_cache = {}
        
        # Initialiser les structures de données
        self.visited = set()
        self.file_depths = {}
        self.all_dependencies = set()
        self.dependency_graph = DependencyGraph()
        
        # Initialiser le partitioner
        try:
            from Core.Partitioner.ast_partitioners.python_ast_partitioner import PythonASTPartitioner
            self.partitioner = PythonASTPartitioner()
            print("✅ Partitioner importé avec succès!")
        except ImportError as e:
            print(f"⚠️ Erreur import partitioner: {e}")
            self.partitioner = None
        
        # ImportResolver (optionnel)
        self.import_resolver = None
    
    def _get_import_resolver(self, current_file: str = None):
        """Retourne l'ImportResolver, en le créant si nécessaire."""
        if self.import_resolver is None:
            try:
                from Core.Partitioner.import_resolver import ImportResolver
                # Ne pas passer current_file au constructeur car il ne l'accepte pas
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
    
    def extract_imports_with_partitioner(self, file_path: str, use_import_resolver: bool = True) -> List[str]:
        """Extrait les imports d'un fichier en utilisant le partitioner ou la méthode simple."""
        try:
            # Si le partitioner n'est pas disponible, utiliser la méthode simple
            if self.partitioner is None:
                return self._extract_imports_simple(file_path)
            
            # Si use_import_resolver est False, utiliser la méthode simple
            if not use_import_resolver:
                return self._extract_imports_simple(file_path)
            
            # Utiliser le partitioner si disponible
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Utiliser le partitioner pour extraire les imports
            result = self.partitioner.parse_content(content)
            if result and hasattr(result, 'imports'):
                imports = []
                for imp in result.imports:
                    if hasattr(imp, 'name'):
                        imports.append(imp.name)
                    elif isinstance(imp, str):
                        imports.append(imp)
                return imports
            else:
                # Fallback vers la méthode simple si le partitioner échoue
                return self._extract_imports_simple(file_path)
                
        except Exception as e:
            self.logger.log_error(f'Erreur partitioner {file_path}: {e}')
            # Fallback vers la méthode simple en cas d'erreur
            return self._extract_imports_simple(file_path)
    
    def _extract_imports_simple(self, file_path: str) -> List[str]:
        """Extrait les imports d'un fichier Python avec une méthode simple (sans ImportResolver)."""
        try:
            import ast
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    level = node.level
                    
                    for alias in node.names:
                        if level > 0:
                            # Import relatif
                            dots = '.' * level
                            if module:
                                imports.append(f"{dots}{module}.{alias.name}")
                            else:
                                imports.append(f"{dots}{alias.name}")
                        else:
                            # Import absolu
                            if module:
                                imports.append(f"{module}.{alias.name}")
                            else:
                                imports.append(alias.name)
            
            return imports
            
        except Exception as e:
            self.logger.log_error(f'Erreur extraction simple {file_path}: {e}')
            return []
    
    def find_file_for_import(self, import_name: str, current_file: str, use_import_resolver: bool = True) -> Optional[str]:
        """Trouve le fichier correspondant à un import en utilisant l'ImportResolver existant."""
        try:
            # Vérifier si c'est un import de bibliothèque standard
            if self._is_standard_library_import(import_name):
                return None  # Ne pas résoudre les imports standard
            
            # Vérifier si c'est un import local (simple et rapide)
            if not self._is_local_import(import_name):
                return None  # Ne pas résoudre les imports non locaux
            
            # Utiliser l'ImportResolver existant si disponible et activé
            if use_import_resolver and ImportResolver is not None:
                # Créer une instance d'ImportResolver si pas encore fait
                if not hasattr(self, '_import_resolver_instance'):
                    self._import_resolver_instance = ImportResolver(project_root=self.project_root)
                
                # Utiliser la méthode resolve_import de l'ImportResolver
                resolved_path = self._import_resolver_instance.resolve_import(import_name, current_file)
                if resolved_path and os.path.exists(resolved_path):
                    return resolved_path
            
            # Fallback vers la logique simple si ImportResolver non disponible ou désactivé
            return self._resolve_import_simple(import_name, current_file)
            
        except Exception as e:
            self.logger.log_error(f'Erreur résolution import {import_name}: {e}')
            return None
    
    def _is_local_import(self, import_name: str) -> bool:
        """Vérifie si un import est local au projet en détectant automatiquement les modules."""
        # Imports relatifs (commencent par .)
        if import_name.startswith('.'):
            return True
        
        # Détection automatique des modules locaux
        return self._is_local_module(import_name)
    
    def _is_local_module(self, import_name: str) -> bool:
        """Détecte automatiquement si un module est local au projet."""
        # Vérifier le cache d'abord
        if import_name in self._local_modules_cache:
            return self._local_modules_cache[import_name]
        
        try:
            # Extraire le premier niveau du module (ex: "Core" de "Core.LLMProviders")
            first_level = import_name.split('.')[0]
            
            # Vérifier si ce premier niveau existe comme dossier dans le projet
            module_path = os.path.join(self.project_root, first_level)
            
            is_local = False
            
            # Si c'est un dossier, c'est probablement un module local
            if os.path.isdir(module_path):
                # Vérifier qu'il contient des fichiers Python ou un __init__.py
                if (os.path.exists(os.path.join(module_path, '__init__.py')) or
                    any(f.endswith('.py') for f in os.listdir(module_path) if os.path.isfile(os.path.join(module_path, f)))):
                    is_local = True
            
            # Vérifier aussi si c'est un fichier Python direct
            module_file = os.path.join(self.project_root, first_level + '.py')
            if os.path.exists(module_file):
                is_local = True
            
            # Mettre en cache le résultat
            self._local_modules_cache[import_name] = is_local
            return is_local
                
        except (IndexError, OSError):
            # En cas d'erreur, considérer comme non local et mettre en cache
            self._local_modules_cache[import_name] = False
            return False
    
    def _resolve_import_simple(self, import_name: str, current_file: str) -> Optional[str]:
        """Résout un import de manière simple sans ImportResolver."""
        try:
            if import_name.startswith('.'):
                # Import relatif
                current_dir = os.path.dirname(os.path.abspath(current_file))
                
                # Compter les .. au début (chaque .. = remonter d'un niveau)
                dots_count = len(import_name) - len(import_name.lstrip('.'))
                # Remonter du bon nombre de niveaux (diviser par 2 car .. = 2 caractères)
                for _ in range(dots_count // 2):
                    current_dir = os.path.dirname(current_dir)
                
                # Convertir le reste en chemin
                rest = import_name[dots_count:].replace('.', '/')
                
                # Essayer d'abord le fichier .py direct
                if rest.endswith('.py'):
                    candidate = os.path.normpath(os.path.join(current_dir, rest))
                else:
                    candidate = os.path.normpath(os.path.join(current_dir, rest + '.py'))
                
                if os.path.exists(candidate):
                    return candidate
                
                # Si pas trouvé, essayer avec __init__.py
                candidate = os.path.normpath(os.path.join(current_dir, rest, '__init__.py'))
                if os.path.exists(candidate):
                    return candidate
                
                # Si c'est un import de classe (ex: ..backends.storage_backends.FileSystemBackend)
                # Essayer de trouver le module contenant la classe
                parts = rest.split('/')
                if len(parts) > 1:
                    # Prendre tout sauf la dernière partie comme module
                    module_path = '/'.join(parts[:-1])
                    module_file = os.path.normpath(os.path.join(current_dir, module_path + '.py'))
                    if os.path.exists(module_file):
                        return module_file
                    
                    # Essayer avec __init__.py
                    module_init = os.path.normpath(os.path.join(current_dir, module_path, '__init__.py'))
                    if os.path.exists(module_init):
                        return module_init
                
                return None
            else:
                # Import absolu - essayer de trouver dans le projet
                project_root = self.project_root
                
                # Essayer avec .py
                candidate = os.path.join(project_root, import_name.replace('.', '/') + '.py')
                if os.path.exists(candidate):
                    return candidate
                
                # Essayer avec __init__.py
                candidate = os.path.join(project_root, import_name.replace('.', '/'), '__init__.py')
                if os.path.exists(candidate):
                    return candidate
                
                # Si c'est un import de classe (ex: MemoryEngine.core.engine.MemoryEngine)
                # Essayer de trouver le module contenant la classe
                parts = import_name.split('.')
                if len(parts) > 1:
                    # Prendre tout sauf la dernière partie comme module
                    module_path = '/'.join(parts[:-1])
                    module_file = os.path.join(project_root, module_path + '.py')
                    if os.path.exists(module_file):
                        return module_file
                    
                    # Essayer avec __init__.py
                    module_init = os.path.join(project_root, module_path, '__init__.py')
                    if os.path.exists(module_init):
                        return module_init
                
                return None
                
        except Exception as e:
            print(f"❌ Erreur résolution import {import_name}: {e}")
            return None
    
    def _resolve_import_with_resolver(self, import_name: str, current_file: str) -> Optional[str]:
        """Résolution avec l'ImportResolver en mode sécurisé."""
        try:
            import importlib.util
            import sys
            
            # Sauvegarder l'état actuel de sys.path
            old_sys_path = list(sys.path)
            
            try:
                # Ajouter le project_root temporairement
                project_root_str = str(self.project_root)
                if project_root_str not in sys.path:
                    sys.path.insert(0, project_root_str)
                
                # Ajouter le dossier parent du fichier courant
                current_dir = os.path.dirname(os.path.abspath(current_file))
                if current_dir not in sys.path:
                    sys.path.insert(0, current_dir)
                
                # Pour les imports relatifs, construire le nom de module
                if import_name.startswith('.'):
                    # Compter les .. au début
                    dots_count = len(import_name) - len(import_name.lstrip('.'))
                    # Remonter du bon nombre de niveaux
                    current_dir_path = os.path.dirname(os.path.abspath(current_file))
                    for _ in range(dots_count // 2):
                        current_dir_path = os.path.dirname(current_dir_path)
                    
                    # Convertir le reste en nom de module
                    rest = import_name[dots_count:].replace('.', '/')
                    module_name = rest.replace('/', '.')
                    
                    # Ajouter le dossier calculé à sys.path
                    if current_dir_path not in sys.path:
                        sys.path.insert(0, current_dir_path)
                else:
                    # Import absolu
                    module_name = import_name
                
                # Utiliser importlib pour résoudre
                spec = importlib.util.find_spec(module_name)
                if spec and spec.origin:
                    # Vérifier si c'est un fichier local
                    if spec.origin.startswith(str(self.project_root)):
                        return spec.origin
                
            finally:
                # Restaurer sys.path
                sys.path = old_sys_path
                
        except Exception as e:
            self.logger.log_error(f'Erreur résolution avec resolver {import_name}: {e}')
        
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
                               local_only: bool = False, verbose: bool = False, debug: bool = False,
                               use_import_resolver: bool = True):
        """Analyse récursivement un fichier et ses dépendances avec détection de cycles intelligente."""
        if file_path in self.visited:
            if verbose:
                self.logger.log_info(f'📁 Déjà visité: {file_path} (profondeur {depth})')
            return
        
        self.visited.add(file_path)
        self.all_dependencies.add(file_path)
        self.file_depths[file_path] = depth # Stocker la profondeur
        
        # Log du début d'analyse du fichier
        self._safe_log('log_file_analysis_start', file_path, depth)
        
        imports = self.extract_imports_with_partitioner(file_path, use_import_resolver)
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
            local_file = self.find_file_for_import(import_name, file_path, use_import_resolver)
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
                        self.analyze_file_recursively(local_file, depth + 1, local_only, verbose, debug, use_import_resolver)
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
        
        # Filtrer seulement les fichiers qui existent
        existing_files = [f for f in autofeeding_files if os.path.exists(f)]
        if not existing_files:
            self.logger.log_warning("Aucun fichier d'auto-feeding thread trouvé")
            print("⚠️ Aucun fichier d'auto-feeding thread trouvé")
            return set(), set()
        
        # Log du début d'analyse
        self._safe_log('log_analysis_start', existing_files)
        
        if local_only:
            print('🎯 Analyse RÉCURSIVE - IMPORTS LOCAUX SEULEMENT...')
        else:
            print('🔍 Analyse RÉCURSIVE avec PARTITIONER...')
        print('🔄 Détection de cycles intelligente activée')
        print('=' * 80)
        
        for file_path in existing_files:
            if not local_only:
                print(f'\n📁 DÉPART: {file_path}')
                print('-' * 60)
            
            # Log du début d'analyse du fichier
            self.logger.log_info(f"📁 Analyse de {file_path}", file=file_path, depth=0)
            
            # Analyser les imports du fichier
            imports = self.extract_imports_with_partitioner(file_path)
            
            # Log des imports trouvés
            if imports:
                self.logger.log_info(f"✅ Imports trouvés dans {file_path}", 
                                   file=file_path, 
                                   imports=imports,
                                   depth=0)
            else:
                self.logger.log_info(f"📄 Aucun import local trouvé dans {file_path}", 
                                   file=file_path, 
                                   imports=[],
                                   depth=0)
            
            # Analyser récursivement
            self.analyze_file_recursively(file_path, local_only=local_only, verbose=verbose, debug=debug)
        
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
        
        # Finaliser le rapport Markdown
        final_stats = {
            'files_analyzed': stats['total_files'],
            'local_imports': len(self.all_dependencies),
            'cycles_detected': len(cycles),
            'max_depth': max(self.file_depths.values()), # Utiliser la profondeur maximale
            'duration': 0,  # Pas de durée calculée dans cette méthode
            'import_types': {}  # Pas de types d'imports calculés dans cette méthode
        }
        self.logger.finalize_report(final_stats)
        
        return self.all_dependencies, unused_files if not local_only else set()

    def analyze_imports(self, files_to_analyze: List[str], use_import_resolver: bool = True, max_depth: Optional[int] = None) -> Dict:
        """Analyse les imports des fichiers donnés avec détection de cycles intelligente et analyse récursive pure."""
        self.logger.log_info("🚀 Début de l'analyse d'imports récursive pure", 
                           files_count=len(files_to_analyze),
                           files=files_to_analyze,
                           use_import_resolver=use_import_resolver,
                           max_depth=max_depth)
        
        start_time = time.time()
        local_dependencies = set()  # Seulement les imports locaux
        all_dependencies = set()    # Tous les imports pour les stats
        import_types = defaultdict(int)
        
        # Réinitialiser l'état pour une nouvelle analyse
        self.visited.clear()
        self.dependency_graph = DependencyGraph()
        self.file_depths.clear() # Réinitialiser les profondeurs
        
        # Analyser chaque fichier de manière récursive pure
        for file_path in files_to_analyze:
            if file_path in self.visited:
                continue
                
            self.logger.log_info(f"📁 Analyse de {file_path}", file=file_path, depth=0)
            
            # Analyser récursivement avec logique pure (une seule passe)
            self._analyze_file_recursively_pure(file_path, 0, use_import_resolver, max_depth, 
                                              local_dependencies, all_dependencies, import_types)
        
        # Détecter les cycles
        cycles = self.dependency_graph.detect_cycles()
        for cycle in cycles:
            self.logger.log_warning(f"⚠️ Cycle détecté: {' -> '.join(cycle)}", cycle=cycle)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Statistiques finales
        stats = {
            'files_analyzed': len(self.visited),
            'local_imports': len(local_dependencies),  # Seulement les imports locaux
            'total_imports': len(all_dependencies),    # Tous les imports
            'cycles_detected': len(cycles),
            'max_depth': max(self.file_depths.values()) if self.file_depths else 0,
            'duration': duration,
            'import_types': dict(import_types)
        }
        
        self.logger.log_info("🎯 Analyse terminée", 
                           stats=stats,
                           duration=duration)
        
        # Finaliser le rapport Markdown
        self.logger.finalize_report(stats)
        
        return {
            'dependencies': list(all_dependencies),
            'cycles': cycles,
            'stats': stats
        }
    
    def _analyze_file_recursively_pure(self, file_path: str, depth: int, use_import_resolver: bool, 
                                     max_depth: Optional[int], local_dependencies: set, 
                                     all_dependencies: set, import_types: defaultdict):
        """Analyse récursive pure d'un fichier - tout se fait en une seule passe."""
        # Vérifier la limite de profondeur AVANT de marquer comme visité
        if max_depth is not None and depth > max_depth:
            self.logger.log_info(f"🛑 Limite de profondeur atteinte pour {file_path}", 
                               file=file_path, depth=depth, max_depth=max_depth)
            return
        
        # Vérifier si déjà visité (éviter les cycles)
        if file_path in self.visited:
            self.logger.log_info(f"🔄 Déjà visité: {file_path} (profondeur {depth})", 
                               file=file_path, depth=depth)
            return
        
        # Marquer comme visité et stocker la profondeur
        self.visited.add(file_path)
        self.file_depths[file_path] = depth
        
        # Extraire les imports du fichier
        imports = self.extract_imports_with_partitioner(file_path, use_import_resolver)
        
        # Filtrer et traiter les imports
        local_imports = []
        for imp in imports:
            # Ajouter à tous les imports pour les stats
            all_dependencies.add(imp)
            
            if self._is_local_import(imp):
                local_imports.append(imp)
                local_dependencies.add(imp)
            else:
                # Compter les types d'imports pour les stats
                if imp.startswith('.'):
                    import_types['relative'] += 1
                elif self._is_standard_library_import(imp):
                    import_types['external'] += 1
                else:
                    import_types['external'] += 1
        
        # Ajouter au rapport Markdown (seulement les imports locaux)
        self.logger._add_file_to_md_report(file_path, local_imports, depth)
        
        # Log de l'analyse
        self.logger.log_info(f"📄 Fichier analysé: {file_path}", 
                           file=file_path, depth=depth, 
                           local_imports=len(local_imports), 
                           total_imports=len(imports))
        
        # Récursion pour les imports locaux (seulement si pas à la limite)
        if max_depth is None or depth < max_depth:
            for import_name in local_imports:
                local_file = self.find_file_for_import(import_name, file_path, use_import_resolver)
                

                
                if local_file and os.path.exists(local_file):
                    # Ajouter au graphe de dépendances
                    self.dependency_graph.add_dependency(file_path, local_file)
                    
                    # Vérifier si cette dépendance créerait un cycle
                    if not self.dependency_graph._would_create_cycle(file_path, local_file):
                        # Récursion pure
                        print(f"🔄 Récursion vers: {local_file} (profondeur {depth + 1})")
                        self._analyze_file_recursively_pure(local_file, depth + 1, use_import_resolver, 
                                                          max_depth, local_dependencies, all_dependencies, import_types)
                    else:
                        self.logger.log_warning(f"🔄 Cycle évité: {import_name} -> {local_file}", 
                                              cycle=[file_path, local_file])
                else:
                    # Debug: afficher plus d'informations sur les imports non résolus
                    if 'TemporalFractalMemoryEngine' in import_name:
                        print(f"🔍 DEBUG: Import non résolu: {import_name} dans {file_path}")
                        print(f"   Tentative de résolution...")
                        # Test manuel de résolution
                        test_resolution = self._resolve_import_simple(import_name, file_path)
                        print(f"   Résolution test: {test_resolution}")
                        if test_resolution:
                            print(f"   Fichier existe: {os.path.exists(test_resolution)}")
                    else:
                        self.logger.log_info(f"❌ Import non résolu: {import_name} dans {file_path}")
        else:
            self.logger.log_info(f"🛑 Récursion arrêtée à la profondeur {depth} pour {file_path}")

    def get_detected_local_modules(self) -> Dict[str, bool]:
        """Retourne tous les modules locaux détectés automatiquement (pour debug)."""
        return self._local_modules_cache.copy()
    
    def print_detected_modules(self):
        """Affiche les modules locaux détectés (pour debug)."""
        print("🔍 Modules locaux détectés automatiquement:")
        for module, is_local in sorted(self._local_modules_cache.items()):
            status = "✅" if is_local else "❌"
            print(f"  {status} {module}")
        print(f"Total: {len(self._local_modules_cache)} modules analysés")

def main():
    """Fonction principale du script d'analyse d'imports."""
    parser = argparse.ArgumentParser(description='Analyseur d\'imports Python avec détection de cycles')
    parser.add_argument('--local-only', action='store_true', 
                       help='Analyser seulement les imports locaux')
    parser.add_argument('--verbose', action='store_true', 
                       help='Mode verbeux avec plus de détails')
    parser.add_argument('--debug', action='store_true', 
                       help='Mode debug avec informations détaillées')
    parser.add_argument('--log-output', action='store_true', 
                       help='Activer la sortie de logs')
    parser.add_argument('--log-directory', type=str, default='logs', 
                       help='Répertoire pour les fichiers de log')
    parser.add_argument('--log-format', type=str, choices=['json', 'text'], default='json', 
                       help='Format des logs (json ou text)')
    parser.add_argument('--use-import-resolver', action='store_true', default=True,
                       help='Utiliser l\'ImportResolver pour une résolution plus intelligente (défaut: True)')
    parser.add_argument('--no-import-resolver', action='store_true',
                       help='Désactiver l\'ImportResolver et utiliser seulement la logique simple')
    parser.add_argument('--max-depth', type=int, default=None,
                       help='Limite de profondeur pour l\'analyse récursive (optionnel)')
    parser.add_argument('--show-detected-modules', action='store_true',
                       help='Afficher les modules locaux détectés automatiquement')
    
    args = parser.parse_args()
    
    # Gérer les options mutuellement exclusives
    if args.no_import_resolver:
        args.use_import_resolver = False
    
    # Définir les variables
    log_directory = args.log_directory
    files_to_analyze = [
        'Assistants/Generalist/V9_AutoFeedingThreadAgent.py',
        'Daemons/DaemonTeam/LegionAutoFeedingThread.py',
        'Daemons/DaemonTeam/LegionAutoFeedingThread_v2.py',
        'Core/UniversalAutoFeedingThread/base_auto_feeding_thread.py',
        'Core/UniversalAutoFeedingThread/universal_auto_feeding_thread.py'
    ]
    
    # Configurer le logger simple
    if args.log_output:
        logger = SimpleImportAnalyzerLogger(
            log_directory=log_directory,
            log_format=args.log_format,
            project_root=os.getcwd()
        )
    else:
        logger = SimpleImportAnalyzerLogger(project_root=os.getcwd())
    
    # Créer l'analyseur avec le logger simple
    analyzer = PartitioningImportAnalyzer(logging_provider=logger)
    analyzer.logger = logger
    
    print(f"🔧 Configuration:")
    print(f"   - ImportResolver: {'✅ Activé' if args.use_import_resolver else '❌ Désactivé'}")
    print(f"   - Mode local seulement: {'✅ Oui' if args.local_only else '❌ Non'}")
    print(f"   - Logs: {'✅ Activés' if args.log_output else '❌ Désactivés'}")
    print(f"   - Profondeur max: {'∞' if args.max_depth is None else args.max_depth}")
    print(f"   - Fichiers à analyser: {len(files_to_analyze)}")
    print()
    
    # Analyser les imports avec logique récursive pure
    result = analyzer.analyze_imports(files_to_analyze, 
                                    use_import_resolver=args.use_import_resolver,
                                    max_depth=args.max_depth)
    
    # Afficher les résultats
    print(f"📊 Résultats de l'analyse des auto-feeding threads:")
    print(f"   Fichiers analysés: {result['stats']['files_analyzed']}")
    print(f"   Imports locaux trouvés: {result['stats']['local_imports']}")
    print(f"   Cycles détectés: {result['stats']['cycles_detected']}")
    print(f"   Profondeur max atteinte: {result['stats']['max_depth']}")
    print(f"   Durée: {result['stats']['duration']:.2f}s")
    print()
    
    if result['dependencies']:
        print(f"📦 Dépendances trouvées:")
        for dep in sorted(result['dependencies']):
            print(f"   - {dep}")
        print()
    
    if result['cycles']:
        print(f"⚠️ Cycles détectés:")
        for cycle in result['cycles']:
            print(f"   - {' -> '.join(cycle)}")
        print()
    else:
        print(f"✅ Aucun cycle détecté - structure saine!")
        print()
    
    if args.log_output:
        print(f"📝 Rapport détaillé généré dans: {log_directory}/imports_analysis/")
        print(f"   - Log JSON: imports_analysis.log")
        print(f"   - Rapport Markdown: imports_analysis_report.md")
        print()
    
    # Afficher les modules détectés si demandé
    if args.show_detected_modules:
        analyzer.print_detected_modules()
        print()

if __name__ == '__main__':
    main() 