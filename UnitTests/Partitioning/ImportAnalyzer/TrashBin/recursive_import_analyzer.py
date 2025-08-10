#!/usr/bin/env python3
"""
⛧ Recursive Import Analyzer - Analyseur Récursif Complet ⛧

Script complet pour analyser récursivement tous les imports du projet
et identifier le code obsolète.

Architecte Démoniaque : Alma⛧
Visionnaire : Lucie Defraiteur - Ma Reine Lucie
"""

import ast
import os
import sys
import json
from pathlib import Path
from typing import Dict, Set, List, Any, Optional
from collections import defaultdict, deque
from datetime import datetime

class RecursiveImportAnalyzer:
    """
    ⛧ Analyseur Récursif Complet des Imports ⛧
    
    Analyse récursivement tous les imports du projet pour identifier
    les dépendances et le code obsolète.
    """
    
    def __init__(self, project_root: str = "."):
        """
        Initialise l'analyseur récursif.
        
        Args:
            project_root: Racine du projet à analyser
        """
        self.project_root = Path(project_root).resolve()
        self.visited_files = set()
        self.import_graph = defaultdict(set)
        self.reverse_import_graph = defaultdict(set)
        self.file_imports = {}
        self.unused_files = set()
        self.memory_engine_imports = set()
        self.obsolete_files = set()
        self.critical_files = set()
        
        # Fichiers de départ critiques
        self.critical_starting_points = [
            "Assistants/Generalist/V9_AutoFeedingThreadAgent.py",
            "Daemons/DaemonTeam/LegionAutoFeedingThread.py",
            "Daemons/DaemonTeam/LegionAutoFeedingThread_v2.py",
            "Core/UniversalAutoFeedingThread/base_auto_feeding_thread.py",
            "Core/UniversalAutoFeedingThread/universal_auto_feeding_thread.py"
        ]
        
        # Modules locaux du projet
        self.local_modules = {
            'MemoryEngine', 'TemporalFractalMemoryEngine', 'Daemons', 
            'Assistants', 'ConsciousnessEngine', 'Core', 'Alma_toolset',
            'LLMProviders', 'IAIntrospectionDaemons'
        }
    
    def analyze_project(self) -> Dict[str, Any]:
        """
        Analyse complète du projet.
        
        Returns:
            Rapport complet d'analyse
        """
        print("⛧ Début de l'analyse récursive du projet...")
        
        # 1. Analyse des fichiers critiques
        print("📊 Étape 1: Analyse des fichiers critiques...")
        for start_file in self.critical_starting_points:
            if os.path.exists(start_file):
                self._analyze_file_recursively(start_file)
                self.critical_files.add(start_file)
            else:
                print(f"⚠️ Fichier critique non trouvé: {start_file}")
        
        # 2. Analyse des fichiers de test
        print("📊 Étape 2: Analyse des fichiers de test...")
        test_files = self._find_test_files()
        for test_file in test_files:
            self._analyze_file_recursively(test_file)
        
        # 3. Analyse des fichiers de configuration
        print("📊 Étape 3: Analyse des fichiers de configuration...")
        config_files = self._find_config_files()
        for config_file in config_files:
            self._analyze_file_recursively(config_file)
        
        # 4. Identification des fichiers non utilisés
        print("📊 Étape 4: Identification des fichiers non utilisés...")
        self._find_unused_files()
        
        # 5. Identification des fichiers obsolètes
        print("📊 Étape 5: Identification des fichiers obsolètes...")
        self._identify_obsolete_files()
        
        # 6. Analyse spécifique MemoryEngine
        print("📊 Étape 6: Analyse spécifique MemoryEngine...")
        self._analyze_memory_engine_usage()
        
        return self._generate_complete_report()
    
    def _analyze_file_recursively(self, file_path: str, depth: int = 0):
        """
        Analyse récursivement un fichier et ses imports.
        
        Args:
            file_path: Chemin du fichier à analyser
            depth: Profondeur de récursion
        """
        if depth > 30:  # Protection contre la récursion infinie
            print(f"⚠️ Profondeur maximale atteinte pour: {file_path}")
            return
        
        if file_path in self.visited_files:
            return
        
        self.visited_files.add(file_path)
        
        try:
            # Analyse du fichier
            imports = self._extract_imports_from_file(file_path)
            self.file_imports[file_path] = imports
            
            # Analyse récursive des imports locaux
            for import_name in imports:
                if self._is_local_import(import_name):
                    local_file = self._resolve_local_import(import_name, file_path)
                    if local_file and os.path.exists(local_file):
                        self.import_graph[file_path].add(local_file)
                        self.reverse_import_graph[local_file].add(file_path)
                        self._analyze_file_recursively(local_file, depth + 1)
        
        except Exception as e:
            print(f"❌ Erreur analyse {file_path}: {e}")
    
    def _extract_imports_from_file(self, file_path: str) -> Set[str]:
        """
        Extrait tous les imports d'un fichier Python.
        
        Args:
            file_path: Chemin du fichier
        
        Returns:
            Set des noms d'imports
        """
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                        if alias.name.startswith('MemoryEngine'):
                            self.memory_engine_imports.add(f"{file_path} -> {alias.name}")
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        full_import = f"{module}.{alias.name}" if module else alias.name
                        imports.add(full_import)
                        if module.startswith('MemoryEngine') or full_import.startswith('MemoryEngine'):
                            self.memory_engine_imports.add(f"{file_path} -> {full_import}")
        
        except Exception as e:
            print(f"❌ Erreur extraction imports {file_path}: {e}")
        
        return imports
    
    def _is_local_import(self, import_name: str) -> bool:
        """
        Vérifie si un import est local au projet.
        
        Args:
            import_name: Nom de l'import
        
        Returns:
            True si l'import est local
        """
        # Imports relatifs
        if import_name.startswith('.'):
            return True
        
        # Imports de modules locaux
        for module in self.local_modules:
            if import_name.startswith(module):
                return True
        
        return False
    
    def _resolve_local_import(self, import_name: str, current_file: str) -> Optional[str]:
        """
        Résout un import local vers un fichier.
        
        Args:
            import_name: Nom de l'import
            current_file: Fichier actuel
        
        Returns:
            Chemin du fichier résolu ou None
        """
        current_dir = Path(current_file).parent
        
        # Import relatif
        if import_name.startswith('.'):
            dots = len(import_name) - len(import_name.lstrip('.'))
            module_name = import_name[dots:]
            
            # Remonter dans l'arborescence
            target_dir = current_dir
            for _ in range(dots - 1):
                target_dir = target_dir.parent
            
            # Chercher le fichier
            possible_files = [
                target_dir / f"{module_name}.py",
                target_dir / module_name / "__init__.py",
                target_dir / module_name / f"{module_name.split('.')[-1]}.py"
            ]
            
            for file_path in possible_files:
                if file_path.exists():
                    return str(file_path)
        
        # Import absolu
        else:
            # Chercher dans le projet
            for root, dirs, files in os.walk(self.project_root):
                for file in files:
                    if file.endswith('.py'):
                        file_path = Path(root) / file
                        if file_path.name == f"{import_name.split('.')[-1]}.py":
                            return str(file_path)
                        elif file_path.name == "__init__.py" and import_name in str(file_path):
                            return str(file_path)
        
        return None
    
    def _find_test_files(self) -> List[str]:
        """Trouve tous les fichiers de test."""
        test_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py') and ('test' in file.lower() or 'Test' in file):
                    test_files.append(str(Path(root) / file))
        
        return test_files
    
    def _find_config_files(self) -> List[str]:
        """Trouve tous les fichiers de configuration."""
        config_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py') and any(keyword in file.lower() for keyword in ['config', 'setup', 'init']):
                    config_files.append(str(Path(root) / file))
        
        return config_files
    
    def _find_unused_files(self):
        """Trouve les fichiers Python non utilisés."""
        all_py_files = set()
        
        # Trouver tous les fichiers Python
        for root, dirs, files in os.walk(self.project_root):
            # Ignorer certains dossiers
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = str(Path(root) / file)
                    all_py_files.add(file_path)
        
        # Fichiers utilisés = ceux visités + ceux référencés
        used_files = self.visited_files.copy()
        for file_path in self.visited_files:
            used_files.update(self.import_graph[file_path])
        
        # Fichiers non utilisés
        self.unused_files = all_py_files - used_files
    
    def _identify_obsolete_files(self):
        """Identifie les fichiers potentiellement obsolètes."""
        obsolete_patterns = [
            'old_', 'legacy_', 'deprecated_', 'v1_', 'v2_', 'v3_', 'v4_', 'v5_', 'v6_', 'v7_', 'v8_',
            'backup_', 'temp_', 'tmp_', 'test_', 'debug_', 'experimental_'
        ]
        
        for file_path in self.unused_files:
            file_name = Path(file_path).name.lower()
            if any(pattern in file_name for pattern in obsolete_patterns):
                self.obsolete_files.add(file_path)
    
    def _analyze_memory_engine_usage(self):
        """Analyse spécifique de l'utilisation de MemoryEngine."""
        print(f"⛧ Analyse des imports MemoryEngine:")
        for import_info in sorted(self.memory_engine_imports):
            print(f"  {import_info}")
    
    def _generate_complete_report(self) -> Dict[str, Any]:
        """Génère un rapport complet de l'analyse."""
        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "critical_files": list(self.critical_files),
            "visited_files": list(self.visited_files),
            "import_graph": dict(self.import_graph),
            "reverse_import_graph": dict(self.reverse_import_graph),
            "file_imports": self.file_imports,
            "unused_files": list(self.unused_files),
            "obsolete_files": list(self.obsolete_files),
            "memory_engine_imports": list(self.memory_engine_imports),
            "statistics": {
                "total_files_analyzed": len(self.visited_files),
                "total_imports": sum(len(imports) for imports in self.file_imports.values()),
                "unused_files_count": len(self.unused_files),
                "obsolete_files_count": len(self.obsolete_files),
                "memory_engine_imports_count": len(self.memory_engine_imports),
                "critical_files_count": len(self.critical_files)
            }
        }
    
    def print_complete_report(self, report: Dict[str, Any]):
        """Affiche le rapport complet d'analyse."""
        print("\n" + "="*80)
        print("⛧ RAPPORT COMPLET D'ANALYSE RÉCURSIVE DES IMPORTS")
        print("="*80)
        
        stats = report["statistics"]
        print(f"📊 Statistiques Générales:")
        print(f"  - Fichiers analysés: {stats['total_files_analyzed']}")
        print(f"  - Total imports: {stats['total_imports']}")
        print(f"  - Fichiers critiques: {stats['critical_files_count']}")
        print(f"  - Fichiers non utilisés: {stats['unused_files_count']}")
        print(f"  - Fichiers obsolètes: {stats['obsolete_files_count']}")
        print(f"  - Imports MemoryEngine: {stats['memory_engine_imports_count']}")
        
        print(f"\n🔗 Imports MemoryEngine:")
        for import_info in sorted(report["memory_engine_imports"]):
            print(f"  {import_info}")
        
        print(f"\n🗑️ Fichiers potentiellement obsolètes:")
        for file_path in sorted(report["obsolete_files"]):
            print(f"  {file_path}")
        
        print(f"\n❓ Fichiers non utilisés (autres):")
        unused_others = set(report["unused_files"]) - set(report["obsolete_files"])
        for file_path in sorted(unused_others):
            print(f"  {file_path}")
        
        print("="*80)
    
    def save_report(self, report: Dict[str, Any], filename: str = "import_analysis_report.json"):
        """Sauvegarde le rapport dans un fichier JSON."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"💾 Rapport sauvegardé: {filename}")


def main():
    """Fonction principale."""
    print("⛧ Démarrage de l'analyseur récursif des imports...")
    
    analyzer = RecursiveImportAnalyzer()
    report = analyzer.analyze_project()
    
    # Affichage du rapport
    analyzer.print_complete_report(report)
    
    # Sauvegarde du rapport
    analyzer.save_report(report)
    
    print("⛧ Analyse terminée !")


if __name__ == "__main__":
    main() 