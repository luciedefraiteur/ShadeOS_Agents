"""
⛧ Import Analyzer - Analyseur Récursif des Imports ⛧

Analyseur récursif des imports pour identifier les dépendances
et nettoyer le code non utilisé.

Architecte Démoniaque : Alma⛧
Visionnaire : Lucie Defraiteur - Ma Reine Lucie
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, Set, List, Any, Optional
from collections import defaultdict, deque

class ImportAnalyzer:
    """
    ⛧ Analyseur Récursif des Imports ⛧
    
    Analyse récursivement tous les imports d'un projet pour identifier
    les dépendances et le code non utilisé.
    """
    
    def __init__(self, project_root: str = "."):
        """
        Initialise l'analyseur d'imports.
        
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
        
    def analyze_starting_points(self, starting_files: List[str]) -> Dict[str, Any]:
        """
        Analyse récursivement les imports à partir de fichiers de départ.
        
        Args:
            starting_files: Liste des fichiers de départ à analyser
        
        Returns:
            Dict avec l'analyse complète
        """
        print(f"⛧ Analyse des imports à partir de: {starting_files}")
        
        # Analyse récursive des imports
        for start_file in starting_files:
            if os.path.exists(start_file):
                self._analyze_file_recursively(start_file)
            else:
                print(f"⚠️ Fichier non trouvé: {start_file}")
        
        # Analyse des fichiers non utilisés
        self._find_unused_files()
        
        # Analyse spécifique MemoryEngine
        self._analyze_memory_engine_usage()
        
        return self._generate_report()
    
    def _analyze_file_recursively(self, file_path: str, depth: int = 0):
        """
        Analyse récursivement un fichier et ses imports.
        
        Args:
            file_path: Chemin du fichier à analyser
            depth: Profondeur de récursion
        """
        if depth > 20:  # Protection contre la récursion infinie
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
                if self._is_local_import(import_name, file_path):
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
    
    def _is_local_import(self, import_name: str, current_file: str) -> bool:
        """
        Vérifie si un import est local au projet.
        
        Args:
            import_name: Nom de l'import
            current_file: Fichier actuel
        
        Returns:
            True si l'import est local
        """
        # Imports relatifs
        if import_name.startswith('.'):
            return True
        
        # Imports de modules locaux
        local_modules = [
            'MemoryEngine', 'TemporalFractalMemoryEngine', 'Daemons', 
            'Assistants', 'ConsciousnessEngine', 'Core', 'Alma_toolset'
        ]
        
        for module in local_modules:
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
    
    def _find_unused_files(self):
        """Trouve les fichiers Python non utilisés."""
        all_py_files = set()
        
        # Trouver tous les fichiers Python
        for root, dirs, files in os.walk(self.project_root):
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
    
    def _analyze_memory_engine_usage(self):
        """Analyse spécifique de l'utilisation de MemoryEngine."""
        print(f"⛧ Analyse des imports MemoryEngine:")
        for import_info in self.memory_engine_imports:
            print(f"  {import_info}")
    
    def _generate_report(self) -> Dict[str, Any]:
        """Génère un rapport complet de l'analyse."""
        return {
            "visited_files": list(self.visited_files),
            "import_graph": dict(self.import_graph),
            "reverse_import_graph": dict(self.reverse_import_graph),
            "file_imports": self.file_imports,
            "unused_files": list(self.unused_files),
            "memory_engine_imports": list(self.memory_engine_imports),
            "statistics": {
                "total_files_analyzed": len(self.visited_files),
                "total_imports": sum(len(imports) for imports in self.file_imports.values()),
                "unused_files_count": len(self.unused_files),
                "memory_engine_imports_count": len(self.memory_engine_imports)
            }
        }
    
    def print_report(self, report: Dict[str, Any]):
        """Affiche le rapport d'analyse."""
        print("\n" + "="*60)
        print("⛧ RAPPORT D'ANALYSE DES IMPORTS")
        print("="*60)
        
        stats = report["statistics"]
        print(f"📊 Statistiques:")
        print(f"  - Fichiers analysés: {stats['total_files_analyzed']}")
        print(f"  - Total imports: {stats['total_imports']}")
        print(f"  - Fichiers non utilisés: {stats['unused_files_count']}")
        print(f"  - Imports MemoryEngine: {stats['memory_engine_imports_count']}")
        
        print(f"\n🔗 Imports MemoryEngine:")
        for import_info in report["memory_engine_imports"]:
            print(f"  {import_info}")
        
        print(f"\n🗑️ Fichiers potentiellement non utilisés:")
        for file_path in sorted(report["unused_files"]):
            print(f"  {file_path}")
        
        print("="*60)


def analyze_v9_and_autofeeding():
    """Analyse les imports de V9 et des autofeeding threads."""
    analyzer = ImportAnalyzer()
    
    # Fichiers de départ à analyser
    starting_files = [
        "Assistants/Generalist/V9_AutoFeedingThreadAgent.py",
        "Daemons/DaemonTeam/LegionAutoFeedingThread.py",
        "Daemons/DaemonTeam/LegionAutoFeedingThread_v2.py",
        "Core/UniversalAutoFeedingThread/base_auto_feeding_thread.py"
    ]
    
    # Analyse récursive
    report = analyzer.analyze_starting_points(starting_files)
    
    # Affichage du rapport
    analyzer.print_report(report)
    
    return report


if __name__ == "__main__":
    analyze_v9_and_autofeeding() 