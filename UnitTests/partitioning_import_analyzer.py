#!/usr/bin/env python3
"""
Analyseur d'imports utilisant le partitioner pour une analyse précise
des dépendances des auto-feeding threads.
"""

import os
import sys
from pathlib import Path
from typing import Set, List, Dict, Optional

# Ajouter le chemin pour importer le partitioner
sys.path.append('Assistants/EditingSession')

try:
    from partitioning.ast_partitioners import PythonASTPartitioner
    from partitioning.partition_schemas import PartitioningError
    print("✅ Partitioner importé avec succès!")
except ImportError as e:
    print(f"❌ Erreur import partitioner: {e}")
    sys.exit(1)

class PartitioningImportAnalyzer:
    def __init__(self, project_root: str = '.'):
        self.project_root = Path(project_root)
        self.visited = set()
        self.all_dependencies = set()
        self.partitioner = PythonASTPartitioner()
        
    def extract_imports_with_partitioner(self, file_path: str) -> List[str]:
        """Extrait tous les imports d'un fichier Python avec le partitioner."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parser avec le partitioner
            tree = self.partitioner.parse_content(content, file_path)
            
            # Analyser les imports
            import_analysis = self.partitioner.extract_import_analysis(tree)
            
            # Collecter tous les imports
            all_imports = []
            
            # Imports de la bibliothèque standard
            for import_info in import_analysis['standard_library']:
                if isinstance(import_info, str):
                    all_imports.append(import_info)
                elif isinstance(import_info, dict):
                    module = import_info['module']
                    for name in import_info['names']:
                        all_imports.append(f"{module}.{name}")
            
            # Imports tiers
            for import_info in import_analysis['third_party']:
                if isinstance(import_info, str):
                    all_imports.append(import_info)
                elif isinstance(import_info, dict):
                    module = import_info['module']
                    for name in import_info['names']:
                        all_imports.append(f"{module}.{name}")
            
            # Imports relatifs
            for import_info in import_analysis['relative_imports']:
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
            print(f'⚠️ Erreur partitioner {file_path}: {e}')
            return []
    
    def find_file_for_import(self, import_name: str, current_file: str) -> Optional[str]:
        """Trouve le fichier correspondant à un import."""
        current_path = Path(current_file)
        
        # Import relatif (commence par .)
        if import_name.startswith('.'):
            dots = len(import_name) - len(import_name.lstrip('.'))
            module_name = import_name[dots:]
            target_dir = current_path.parent
            for _ in range(dots - 1):
                target_dir = target_dir.parent
            
            possible_files = [
                target_dir / f'{module_name}.py',
                target_dir / module_name / '__init__.py',
                target_dir / module_name / f'{module_name.split(".")[-1]}.py'
            ]
            
            for file_path in possible_files:
                if file_path.exists():
                    return str(file_path)
        
        # Import absolu - chercher dans tout le projet
        else:
            import_parts = import_name.split('.')
            
            # Séparer le module de la classe/fonction
            if len(import_parts) > 1:
                module_parts = import_parts[:-1]  # Tout sauf la dernière partie
                class_name = import_parts[-1]     # Dernière partie
                
                # Chercher le fichier du module
                for root, dirs, files in os.walk(self.project_root):
                    dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache']]
                    
                    for file in files:
                        if file.endswith('.py'):
                            file_path = Path(root) / file
                            path_parts = list(file_path.parts)
                            path_dirs = path_parts[:-1]  # Enlever le nom du fichier
                            
                            # Vérifier si les dossiers correspondent au module
                            if len(path_dirs) >= len(module_parts):
                                path_suffix = path_dirs[-(len(module_parts)):]
                                
                                if path_suffix == module_parts:
                                    return str(file_path)
            
            # Si pas trouvé, essayer avec le nom complet comme module
            for root, dirs, files in os.walk(self.project_root):
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache']]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = Path(root) / file
                        path_str = str(file_path)
                        
                        # Cas 1: fichier direct
                        if file == f'{import_parts[-1]}.py':
                            path_parts = list(file_path.parts)
                            path_dirs = path_parts[:-1]
                            
                            if len(path_dirs) >= len(import_parts) - 1:
                                path_suffix = path_dirs[-(len(import_parts) - 1):]
                                import_dirs = import_parts[:-1]
                                
                                if path_suffix == import_dirs:
                                    return str(file_path)
                        
                        # Cas 2: __init__.py
                        elif file == '__init__.py':
                            import_path = '/'.join(import_parts)
                            if import_path in path_str:
                                return str(file_path)
        
        return None
    
    def analyze_file_recursively(self, file_path: str, depth: int = 0, max_depth: int = 50):
        """Analyse récursivement un fichier et ses dépendances."""
        if depth > max_depth or file_path in self.visited:
            return
        
        self.visited.add(file_path)
        self.all_dependencies.add(file_path)
        
        imports = self.extract_imports_with_partitioner(file_path)
        indent = '  ' * depth
        
        print(f'{indent}📁 {file_path}')
        print(f'{indent}   Imports (partitioner): {imports}')
        
        resolved_count = 0
        for import_name in imports:
            local_file = self.find_file_for_import(import_name, file_path)
            if local_file and os.path.exists(local_file):
                resolved_count += 1
                print(f'{indent}   ✅ {import_name} -> {local_file}')
                self.analyze_file_recursively(local_file, depth + 1, max_depth)
            else:
                print(f'{indent}   ❌ {import_name} -> Non résolu')
        
        if resolved_count > 0:
            print(f'{indent}   📦 Résolus: {resolved_count}')
    
    def analyze_autofeeding_dependencies(self):
        """Analyse les dépendances des auto-feeding threads."""
        autofeeding_files = [
            'Assistants/Generalist/V9_AutoFeedingThreadAgent.py',
            'Daemons/DaemonTeam/LegionAutoFeedingThread.py',
            'Daemons/DaemonTeam/LegionAutoFeedingThread_v2.py',
            'Core/UniversalAutoFeedingThread/base_auto_feeding_thread.py',
            'Core/UniversalAutoFeedingThread/universal_auto_feeding_thread.py'
        ]
        
        print('🔍 Analyse RÉCURSIVE avec PARTITIONER...')
        print('=' * 80)
        
        for file_path in autofeeding_files:
            if os.path.exists(file_path):
                print(f'\n📁 DÉPART: {file_path}')
                print('-' * 60)
                self.analyze_file_recursively(file_path)
            else:
                print(f'⚠️ Fichier non trouvé: {file_path}')
        
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
        
        return self.all_dependencies, unused_files

def main():
    analyzer = PartitioningImportAnalyzer()
    dependencies, unused = analyzer.analyze_autofeeding_dependencies()
    
    print(f'\n🎯 ANALYSE TERMINÉE !')
    print(f'📊 Dépendances: {len(dependencies)}')
    print(f'🗑️ Non utilisés: {len(unused)}')

if __name__ == '__main__':
    main() 