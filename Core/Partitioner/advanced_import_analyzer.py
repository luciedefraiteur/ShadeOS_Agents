#!/usr/bin/env python3
"""
⛧ Advanced Import Analyzer - Utilise les nouveaux outils du partitioner ⛧

Analyseur d'imports utilisant les nouveaux outils de Core.Partitioner
pour générer un beau rapport Markdown.
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

# Ajouter le répertoire racine pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Imports des nouveaux outils du partitioner
try:
    from Core.Partitioner import (
        ImportAnalyzer, ImportAnalysisResult, DependencyGraph,
        PartitionResult, PartitionBlock, PartitionLocation,
        PartitioningError, LocationTrackingError, PartitionValidationError,
        global_error_logger, log_partitioning_error, log_partitioning_warning
    )
    print("✅ Nouveaux outils du partitioner importés avec succès!")
except ImportError as e:
    print(f"❌ Erreur import nouveaux outils: {e}")
    sys.exit(1)

class AdvancedImportAnalyzerLogger:
    """Logger avancé pour l'analyse d'imports avec les nouveaux outils."""
    
    def __init__(self, log_directory: Optional[str] = None, project_root: str = "."):
        self.log_directory = log_directory
        self.project_root = project_root
        self.session_id = f"advanced_analysis_{int(time.time())}"
        self.start_time = time.time()
        
        # Données d'analyse
        self.files_data = {}  # {file_path: {depth, imports, analysis_result}}
        self.cycles_detected = []
        self.stats = {}
        
        # Créer le répertoire de logs si nécessaire
        if log_directory:
            Path(log_directory).mkdir(parents=True, exist_ok=True)
            imports_analysis_dir = Path(log_directory) / "advanced_imports_analysis"
            imports_analysis_dir.mkdir(parents=True, exist_ok=True)
            
            # Fichier de log JSON
            self.log_file = imports_analysis_dir / "advanced_imports_analysis.log"
            
            # Fichier de rapport Markdown
            self.md_file = imports_analysis_dir / "advanced_imports_analysis_report.md"
        else:
            self.log_file = None
            self.md_file = None
    
    def log_analysis_start(self, start_files: List[str]):
        """Log le début d'une analyse."""
        print(f"🚀 Début analyse avancée session {self.session_id}")
        print(f"📁 Fichiers de départ: {len(start_files)}")
        self._write_log("INFO", "🚀 Début analyse avancée", {
            "type": "analysis_start",
            "start_files": start_files,
            "total_start_files": len(start_files)
        })
    
    def log_file_analysis_start(self, file_path: str, depth: int = 0):
        """Log le début de l'analyse d'un fichier."""
        indent = '  ' * depth
        print(f"{indent}📁 Analyse: {file_path}")
        self._write_log("INFO", f"📁 Analyse: {file_path}", {
            "type": "file_analysis_start",
            "file_path": file_path,
            "depth": depth
        })
    
    def log_import_analysis_result(self, file_path: str, analysis_result: ImportAnalysisResult):
        """Log le résultat d'analyse d'imports."""
        print(f"  📊 Résultat analyse: {len(analysis_result.imports)} imports trouvés")
        self._write_log("INFO", f"Résultat analyse: {file_path}", {
            "type": "import_analysis_result",
            "file_path": file_path,
            "imports_count": len(analysis_result.imports),
            "cycles_detected": len(analysis_result.cycles) if hasattr(analysis_result, 'cycles') else 0
        })
    
    def log_cycle_detection(self, cycle: List[str]):
        """Log la détection d'un cycle."""
        print(f"  ⚠️ Cycle détecté: {' -> '.join(cycle)}")
        self.cycles_detected.append(cycle)
        self._write_log("WARNING", f"Cycle détecté: {' -> '.join(cycle)}", {
            "type": "cycle_detection",
            "cycle": cycle
        })
    
    def log_error(self, message: str, error: Exception = None):
        """Log une erreur."""
        print(f"❌ ERREUR: {message}")
        if error:
            print(f"   Détails: {error}")
        
        error_data = {"type": "error", "message": message}
        if error:
            error_data["error_type"] = type(error).__name__
            error_data["error_details"] = str(error)
        
        self._write_log("ERROR", message, error_data)
    
    def log_warning(self, message: str, **kwargs):
        """Log un avertissement."""
        print(f"⚠️ {message}")
        self._write_log("WARNING", message, {"type": "warning"})
    
    def log_info(self, message: str, **kwargs):
        """Log un message d'information."""
        print(f"ℹ️ {message}")
        self._write_log("INFO", message, kwargs)
    
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
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"❌ Erreur écriture log: {e}")
    
    def add_file_data(self, file_path: str, depth: int, imports: List[str], analysis_result: ImportAnalysisResult = None):
        """Ajoute les données d'un fichier analysé."""
        if file_path not in self.files_data:
            self.files_data[file_path] = {
                'depth': depth,
                'imports': imports,
                'analysis_result': analysis_result
            }
        else:
            # Mettre à jour si la profondeur est plus élevée
            if depth > self.files_data[file_path]['depth']:
                self.files_data[file_path]['depth'] = depth
            # Fusionner les imports
            existing_imports = set(self.files_data[file_path]['imports'])
            new_imports = set(imports)
            self.files_data[file_path]['imports'] = list(existing_imports | new_imports)
    
    def finalize_report(self, stats: Dict):
        """Finalise le rapport Markdown."""
        if not self.md_file:
            return
        
        print(f"📝 Génération du rapport Markdown: {self.md_file}")
        
        # En-tête du rapport
        header = f"""# 📊 Rapport d'Analyse d'Imports Avancée

**Session ID:** `{self.session_id}`  
**Date:** {datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')}  
**Format:** Analyse des dépendances Python avec les nouveaux outils du partitioner

---

## 🎯 Résumé Exécutif

*Ce rapport détaille l'analyse des imports Python dans le projet, utilisant les nouveaux outils de Core.Partitioner.*

---

## 📁 Liste des Fichiers Analysés

*Liste complète de tous les fichiers analysés :*

"""
        
        # Liste des fichiers
        files_list = []
        for file_path in sorted(self.files_data.keys()):
            files_list.append(f"`{file_path}`")
        
        files_section = "\n".join(files_list)
        
        # Arbre structurel
        tree_section = """

---

## 🌳 Arbre Structurel des Fichiers

*Représentation visuelle de la hiérarchie des fichiers analysés :*

"""
        
        # Générer l'arbre ASCII
        ascii_tree = self._generate_ascii_tree()
        
        # Section des imports
        imports_section = """

---

## 📋 Analyse des Imports par Fichier

*Détail des imports trouvés dans chaque fichier :*

"""
        
        # Générer la liste des imports
        imports_entries = []
        for file_path, file_data in sorted(self.files_data.items()):
            entry = f"**{file_path}** (profondeur {file_data['depth']}):"
            if file_data['imports']:
                for imp in sorted(file_data['imports']):
                    entry += f"\n  - `{imp}`"
            else:
                entry += "\n  - *Aucun import local*"
            imports_entries.append(entry)
        
        imports_list = "\n\n".join(imports_entries)
        
        # Section des cycles
        cycles_section = ""
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
        
        # Écrire le rapport complet
        full_report = header + files_section + tree_section + ascii_tree + imports_section + imports_list + cycles_section + summary
        
        with open(self.md_file, 'w', encoding='utf-8') as f:
            f.write(full_report)
        
        print(f"✅ Rapport généré avec succès: {self.md_file}")

    def _generate_ascii_tree(self) -> str:
        """Génère un arbre ASCII structurel des fichiers analysés."""
        from collections import defaultdict
        
        # Créer une structure d'arbre hiérarchique
        tree = defaultdict(lambda: defaultdict(set))
        
        for file_path in self.files_data.keys():
            # Convertir en chemin relatif depuis la racine du projet
            try:
                rel_path = os.path.relpath(file_path, self.project_root)
            except ValueError:
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


class AdvancedImportAnalyzer:
    """Analyseur d'imports utilisant les nouveaux outils du partitioner."""
    
    def __init__(self, project_root: str = '.'):
        """Initialise l'analyseur avancé."""
        self.project_root = os.path.abspath(project_root)
        self.import_analyzer = ImportAnalyzer(project_root)
        self.logger = AdvancedImportAnalyzerLogger(project_root=project_root)
        self.visited = set()
        self.file_depths = {}
        self.stats = {
            'files_analyzed': 0,
            'local_imports': 0,
            'cycles_detected': 0,
            'max_depth': 0,
            'import_types': defaultdict(int)
        }
    
    def analyze_files(self, file_paths: List[str], max_depth: Optional[int] = None) -> Dict:
        """Analyse les fichiers donnés avec les nouveaux outils."""
        self.logger.log_analysis_start(file_paths)
        
        start_time = time.time()
        
        # Réinitialiser l'état
        self.visited.clear()
        self.file_depths.clear()
        self.stats['import_types'].clear()
        
        # Analyser chaque fichier
        for file_path in file_paths:
            if file_path in self.visited:
                continue
            
            self.analyze_file_recursively(file_path, 0, max_depth)
        
        # Calculer les statistiques finales
        end_time = time.time()
        self.stats['duration'] = end_time - start_time
        self.stats['files_analyzed'] = len(self.visited)
        self.stats['max_depth'] = max(self.file_depths.values()) if self.file_depths else 0
        self.stats['cycles_detected'] = len(self.logger.cycles_detected)
        
        # Finaliser le rapport
        self.logger.finalize_report(self.stats)
        
        return {
            'files_analyzed': self.stats['files_analyzed'],
            'local_imports': self.stats['local_imports'],
            'cycles_detected': self.stats['cycles_detected'],
            'max_depth': self.stats['max_depth'],
            'duration': self.stats['duration'],
            'import_types': dict(self.stats['import_types'])
        }
    
    def analyze_file_recursively(self, file_path: str, depth: int, max_depth: Optional[int] = None):
        """Analyse récursivement un fichier et ses dépendances."""
        # Vérifier la limite de profondeur
        if max_depth is not None and depth > max_depth:
            self.logger.log_info(f"🛑 Limite de profondeur atteinte pour {file_path}")
            return
        
        # Vérifier si déjà visité
        if file_path in self.visited:
            self.logger.log_info(f"🔄 Déjà visité: {file_path}")
            return
        
        # Marquer comme visité
        self.visited.add(file_path)
        self.file_depths[file_path] = depth
        
        self.logger.log_file_analysis_start(file_path, depth)
        
        try:
            # Utiliser l'ImportAnalyzer pour analyser le fichier
            analysis_result = self.import_analyzer.analyze_files([file_path])
            
            if analysis_result and 'files' in analysis_result:
                file_analysis = analysis_result['files'].get(file_path, {})
                imports = file_analysis.get('imports', [])
                
                # Classifier les imports
                local_imports = []
                for imp in imports:
                    if self._is_local_import(imp):
                        local_imports.append(imp)
                        self.stats['local_imports'] += 1
                    else:
                        self.stats['import_types']['external'] += 1
                
                # Ajouter les données au logger
                self.logger.add_file_data(file_path, depth, local_imports, analysis_result)
                
                # Log du résultat
                self.logger.log_import_analysis_result(file_path, analysis_result)
                
                # Vérifier les cycles
                if 'cycles' in file_analysis:
                    for cycle in file_analysis['cycles']:
                        self.logger.log_cycle_detection(cycle)
                
                # Récursion pour les imports locaux
                if max_depth is None or depth < max_depth:
                    for import_name in local_imports:
                        local_file = self._find_file_for_import(import_name, file_path)
                        if local_file and os.path.exists(local_file):
                            self.analyze_file_recursively(local_file, depth + 1, max_depth)
            
        except Exception as e:
            self.logger.log_error(f"Erreur analyse {file_path}: {e}")
    
    def _is_local_import(self, import_name: str) -> bool:
        """Vérifie si un import est local au projet."""
        # Imports relatifs
        if import_name.startswith('.'):
            return True
        
        # Imports absolus locaux
        local_prefixes = [
            'Core.', 'Assistants.', 'MemoryEngine.', 'UnitTests.',
            'partitioning.', 'LLMProviders.', 'Utils.', 'Parsers.',
            'Config.', 'ProcessManager.', 'LoggingProviders.',
            'TemporalFractalMemoryEngine.'
        ]
        
        for prefix in local_prefixes:
            if import_name.startswith(prefix):
                return True
        
        return False
    
    def _find_file_for_import(self, import_name: str, current_file: str) -> Optional[str]:
        """Trouve le fichier correspondant à un import."""
        try:
            if import_name.startswith('.'):
                # Import relatif
                current_dir = os.path.dirname(os.path.abspath(current_file))
                
                # Compter les .. au début
                dots_count = len(import_name) - len(import_name.lstrip('.'))
                for _ in range(dots_count // 2):
                    current_dir = os.path.dirname(current_dir)
                
                # Convertir le reste en chemin
                rest = import_name[dots_count:].replace('.', '/')
                
                # Essayer d'abord le fichier .py direct
                candidate = os.path.normpath(os.path.join(current_dir, rest + '.py'))
                if os.path.exists(candidate):
                    return candidate
                
                # Essayer avec __init__.py
                candidate = os.path.normpath(os.path.join(current_dir, rest, '__init__.py'))
                if os.path.exists(candidate):
                    return candidate
                
                return None
            else:
                # Import absolu
                project_root = self.project_root
                
                # Essayer avec .py
                candidate = os.path.join(project_root, import_name.replace('.', '/') + '.py')
                if os.path.exists(candidate):
                    return candidate
                
                # Essayer avec __init__.py
                candidate = os.path.join(project_root, import_name.replace('.', '/'), '__init__.py')
                if os.path.exists(candidate):
                    return candidate
                
                return None
                
        except Exception as e:
            self.logger.log_error(f"Erreur résolution import {import_name}: {e}")
            return None


def main():
    """Fonction principale du script d'analyse avancée."""
    parser = argparse.ArgumentParser(description='Analyseur d\'imports avancé utilisant les nouveaux outils du partitioner')
    parser.add_argument('--files', nargs='+', required=True,
                       help='Liste des fichiers à analyser')
    parser.add_argument('--config-file', type=str,
                       help='Fichier de configuration JSON avec la liste des fichiers')
    parser.add_argument('--max-depth', type=int, default=None,
                       help='Limite de profondeur pour l\'analyse récursive')
    parser.add_argument('--log-directory', type=str, default='logs',
                       help='Répertoire pour les fichiers de log')
    parser.add_argument('--project-root', type=str, default='.',
                       help='Racine du projet')
    
    args = parser.parse_args()
    
    # Déterminer les fichiers à analyser
    files_to_analyze = []
    
    if args.config_file:
        # Lire depuis le fichier de configuration
        try:
            with open(args.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                files_to_analyze = config.get('files', [])
        except Exception as e:
            print(f"❌ Erreur lecture fichier config {args.config_file}: {e}")
            sys.exit(1)
    else:
        # Utiliser les fichiers fournis en argument
        files_to_analyze = args.files
    
    # Vérifier que les fichiers existent
    existing_files = []
    for file_path in files_to_analyze:
        if os.path.exists(file_path):
            existing_files.append(file_path)
        else:
            print(f"⚠️ Fichier non trouvé: {file_path}")
    
    if not existing_files:
        print("❌ Aucun fichier valide à analyser")
        sys.exit(1)
    
    print(f"🔧 Configuration:")
    print(f"   - Fichiers à analyser: {len(existing_files)}")
    print(f"   - Profondeur max: {'∞' if args.max_depth is None else args.max_depth}")
    print(f"   - Racine projet: {args.project_root}")
    print(f"   - Répertoire logs: {args.log_directory}")
    print()
    
    # Créer l'analyseur et analyser
    analyzer = AdvancedImportAnalyzer(project_root=args.project_root)
    analyzer.logger = AdvancedImportAnalyzerLogger(
        log_directory=args.log_directory,
        project_root=args.project_root
    )
    
    result = analyzer.analyze_files(existing_files, max_depth=args.max_depth)
    
    # Afficher les résultats
    print(f"📊 Résultats de l'analyse:")
    print(f"   Fichiers analysés: {result['files_analyzed']}")
    print(f"   Imports locaux trouvés: {result['local_imports']}")
    print(f"   Cycles détectés: {result['cycles_detected']}")
    print(f"   Profondeur max atteinte: {result['max_depth']}")
    print(f"   Durée: {result['duration']:.2f}s")
    print()
    
    if result['cycles_detected'] > 0:
        print(f"⚠️ {result['cycles_detected']} cycles détectés - voir le rapport pour plus de détails")
    else:
        print(f"✅ Aucun cycle détecté - structure saine!")
    
    print(f"📝 Rapport généré dans: {args.log_directory}/advanced_imports_analysis/")

if __name__ == '__main__':
    main() 