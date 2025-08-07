#!/usr/bin/env python3
"""
Analyseur récursif d'imports pour identifier la vraie codebase utilisée
par les auto-feeding threads.
"""

import ast
import os
import sys
from pathlib import Path
from typing import Set, List, Dict, Optional

class RecursiveImportAnalyzer:
    def __init__(self, project_root: str = '.'):
        self.project_root = Path(project_root)
        self.visited = set()
        self.all_dependencies = set()
        self.import_resolution_cache = {}
        
    def extract_imports(self, file_path: str) -> List[str]:
        """Extrait tous les imports d'un fichier Python."""
        try:
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
                    for alias in node.names:
                        if module:
                            full_import = f'{module}.{alias.name}'
                        else:
                            full_import = alias.name
                        imports.append(full_import)
            
            return imports
        except Exception as e:
            print(f'⚠️ Erreur lecture {file_path}: {e}')
            return []
    
    def resolve_local_import(self, import_name: str, current_file: str) -> Optional[str]:
        """Résout un import local vers un fichier Python."""
        cache_key = f"{import_name}:{current_file}"
        if cache_key in self.import_resolution_cache:
            return self.import_resolution_cache[cache_key]
        
        current_path = Path(current_file)
        
        # Import relatif (commence par .)
        if import_name.startswith('.'):
            dots = len(import_name) - len(import_name.lstrip('.'))
            module_name = import_name[dots:]
            
            # Remonter dans l'arborescence selon le nombre de points
            target_dir = current_path.parent
            for _ in range(dots - 1):
                target_dir = target_dir.parent
            
            # Possibilités pour l'import relatif
            possible_files = [
                target_dir / f'{module_name}.py',
                target_dir / module_name / '__init__.py',
                target_dir / module_name / f'{module_name.split(".")[-1]}.py'
            ]
            
            for file_path in possible_files:
                if file_path.exists():
                    self.import_resolution_cache[cache_key] = str(file_path)
                    return str(file_path)
        
        # Import absolu - chercher dans tout le projet
        else:
            # Chercher dans tout le projet
            for root, dirs, files in os.walk(self.project_root):
                # Ignorer les dossiers système
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules']]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = Path(root) / file
                        
                        # Cas 1: fichier direct (ex: MemoryEngine.core.engine -> engine.py)
                        if file == f'{import_name.split(".")[-1]}.py':
                            # Vérifier que le chemin correspond à l'import
                            path_parts = file_path.parts
                            import_parts = import_name.split('.')
                            
                            # Vérifier si les parties de l'import correspondent au chemin
                            if len(path_parts) >= len(import_parts):
                                path_suffix = path_parts[-(len(import_parts)):]
                                if all(part in str(path_suffix) for part in import_parts):
                                    self.import_resolution_cache[cache_key] = str(file_path)
                                    return str(file_path)
                        
                        # Cas 2: __init__.py dans un package
                        elif file == '__init__.py':
                            # Vérifier si le chemin correspond à l'import
                            path_str = str(file_path)
                            import_str = import_name.replace('.', '/')
                            if import_str in path_str:
                                self.import_resolution_cache[cache_key] = str(file_path)
                                return str(file_path)
        
        # Aucune correspondance trouvée
        self.import_resolution_cache[cache_key] = None
        return None
    
    def analyze_file_recursively(self, file_path: str, depth: int = 0, max_depth: int = 50):
        """Analyse récursivement un fichier et ses dépendances."""
        if depth > max_depth or file_path in self.visited:
            return
        
        self.visited.add(file_path)
        self.all_dependencies.add(file_path)
        
        imports = self.extract_imports(file_path)
        indent = '  ' * depth
        
        print(f'{indent}📁 {file_path}')
        print(f'{indent}   Imports: {imports}')
        
        resolved_imports = []
        for import_name in imports:
            local_file = self.resolve_local_import(import_name, file_path)
            if local_file and os.path.exists(local_file):
                resolved_imports.append(local_file)
                print(f'{indent}   ✅ {import_name} -> {local_file}')
                self.analyze_file_recursively(local_file, depth + 1, max_depth)
            else:
                print(f'{indent}   ❌ {import_name} -> Non résolu')
        
        if resolved_imports:
            print(f'{indent}   📦 Dépendances résolues: {len(resolved_imports)}')
    
    def analyze_autofeeding_dependencies(self):
        """Analyse les dépendances des auto-feeding threads."""
        autofeeding_files = [
            'Assistants/Generalist/V9_AutoFeedingThreadAgent.py',
            'Daemons/DaemonTeam/LegionAutoFeedingThread.py',
            'Daemons/DaemonTeam/LegionAutoFeedingThread_v2.py',
            'Core/UniversalAutoFeedingThread/base_auto_feeding_thread.py',
            'Core/UniversalAutoFeedingThread/universal_auto_feeding_thread.py'
        ]
        
        print('🔍 Analyse RÉCURSIVE COMPLÈTE des dépendances autofeeding...')
        print('=' * 80)
        
        for file_path in autofeeding_files:
            if os.path.exists(file_path):
                print(f'\n📁 DÉPART: {file_path}')
                print('-' * 60)
                self.analyze_file_recursively(file_path)
            else:
                print(f'⚠️ Fichier non trouvé: {file_path}')
        
        print(f'\n📊 TOTAL DÉPENDANCES RÉCURSIVES: {len(self.all_dependencies)}')
        print('\n📋 Liste complète des dépendances récursives:')
        for dep in sorted(self.all_dependencies):
            print(f'  {dep}')
        
        # Trouver tous les fichiers Python du projet
        all_py_files = set()
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules']]
            for file in files:
                if file.endswith('.py'):
                    all_py_files.add(str(Path(root) / file))
        
        unused_files = all_py_files - self.all_dependencies
        print(f'\n🗑️ FICHIERS NON UTILISÉS PAR AUTOFEEDING: {len(unused_files)}')
        print('\n📋 Premiers fichiers non utilisés:')
        for file_path in sorted(unused_files)[:20]:
            print(f'  {file_path}')
        
        return self.all_dependencies, unused_files

def main():
    analyzer = RecursiveImportAnalyzer()
    dependencies, unused = analyzer.analyze_autofeeding_dependencies()
    
    print(f'\n🎯 ANALYSE TERMINÉE !')
    print(f'📊 Dépendances: {len(dependencies)}')
    print(f'🗑️ Non utilisés: {len(unused)}')

if __name__ == '__main__':
    main() 