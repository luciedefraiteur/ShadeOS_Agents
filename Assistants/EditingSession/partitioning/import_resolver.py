"""
🔍 Résolveur d'Imports Locaux pour le Partitioner

Module spécialisé pour résoudre correctement tous les imports locaux
et analyser les dépendances récursives avec une approche générique.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import ast
import logging
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass
from collections import defaultdict
from enum import Enum

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ImportErrorType(Enum):
    """Types d'erreurs d'imports."""
    STANDARD_LIBRARY = "standard_library"
    THIRD_PARTY_MISSING = "third_party_missing"
    LOCAL_FILE_MISSING = "local_file_missing"
    LOCAL_PACKAGE_MISSING = "local_package_missing"
    RELATIVE_IMPORT_ERROR = "relative_import_error"
    CIRCULAR_IMPORT = "circular_import"
    SYNTAX_ERROR = "syntax_error"
    UNKNOWN = "unknown"

@dataclass
class ImportErrorInfo:
    """Informations détaillées sur une erreur d'import."""
    import_name: str
    error_type: ImportErrorType
    file_path: str
    line_number: Optional[int]
    error_message: str
    suggested_fix: Optional[str] = None
    severity: str = "warning"  # info, warning, error, critical

@dataclass
class ImportInfo:
    """Informations sur un import."""
    module_name: str
    class_name: Optional[str]
    is_relative: bool
    level: int
    file_path: Optional[str] = None
    resolved: bool = False
    error_message: Optional[str] = None
    error_type: Optional[ImportErrorType] = None
    line_number: Optional[int] = None

@dataclass
class DependencyNode:
    """Nœud de dépendance."""
    file_path: str
    imports: List[ImportInfo]
    dependencies: Set[str]
    complexity: int
    architectural_patterns: List[str]
    unresolved_imports: List[str]
    import_errors: List[ImportErrorInfo]

class ImportErrorClassifier:
    """Classificateur d'erreurs d'imports générique."""
    
    def __init__(self):
        self.standard_libs = self._get_standard_libraries()
        self.third_party_cache = {}
    
    def _get_standard_libraries(self) -> Set[str]:
        """Détecte automatiquement les bibliothèques standard Python."""
        standard_libs = set()
        
        # Modules standard connus
        known_standard = {
            'os', 'sys', 'time', 'json', 're', 'asyncio', 'subprocess', 
            'pathlib', 'typing', 'dataclasses', 'enum', 'logging', 
            'threading', 'psutil', 'abc', 'collections', 'uuid', 'hashlib',
            'datetime', 'random', 'math', 'itertools', 'functools'
        }
        
        # Vérifier avec importlib
        for module_name in known_standard:
            try:
                spec = importlib.util.find_spec(module_name)
                if spec and spec.origin and 'site-packages' not in spec.origin:
                    standard_libs.add(module_name)
            except:
                pass
        
        return standard_libs
    
    def classify_import_error(self, import_name: str, current_file: str, error_message: str = "") -> ImportErrorInfo:
        """Classifie une erreur d'import."""
        # Vérifier si c'est une bibliothèque standard
        if import_name in self.standard_libs:
            return ImportErrorInfo(
                import_name=import_name,
                error_type=ImportErrorType.STANDARD_LIBRARY,
                file_path=current_file,
                line_number=None,
                error_message=f"Bibliothèque standard: {import_name}",
                suggested_fix=None,
                severity="info"
            )
        
        # Vérifier si c'est une bibliothèque tierce
        if self._is_third_party_library(import_name):
            return ImportErrorInfo(
                import_name=import_name,
                error_type=ImportErrorType.THIRD_PARTY_MISSING,
                file_path=current_file,
                line_number=None,
                error_message=f"Bibliothèque tierce manquante: {import_name}",
                suggested_fix=f"pip install {import_name.split('.')[0]}",
                severity="error"
            )
        
        # Vérifier si c'est un fichier local manquant
        if self._is_local_file_import(import_name):
            return ImportErrorInfo(
                import_name=import_name,
                error_type=ImportErrorType.LOCAL_FILE_MISSING,
                file_path=current_file,
                line_number=None,
                error_message=f"Fichier local manquant: {import_name}",
                suggested_fix=f"Vérifier l'existence du fichier pour {import_name}",
                severity="error"
            )
        
        # Vérifier si c'est un package local manquant
        if self._is_local_package_import(import_name):
            return ImportErrorInfo(
                import_name=import_name,
                error_type=ImportErrorType.LOCAL_PACKAGE_MISSING,
                file_path=current_file,
                line_number=None,
                error_message=f"Package local manquant: {import_name}",
                suggested_fix=f"Vérifier la structure du package pour {import_name}",
                severity="error"
            )
        
        # Erreur inconnue
        return ImportErrorInfo(
            import_name=import_name,
            error_type=ImportErrorType.UNKNOWN,
            file_path=current_file,
            line_number=None,
            error_message=f"Erreur d'import inconnue: {import_name}",
            suggested_fix="Analyser manuellement l'import",
            severity="warning"
        )
    
    def _is_third_party_library(self, import_name: str) -> bool:
        """Détermine si c'est une bibliothèque tierce."""
        if import_name in self.third_party_cache:
            return self.third_party_cache[import_name]
        
        try:
            spec = importlib.util.find_spec(import_name.split('.')[0])
            if spec and spec.origin and 'site-packages' in spec.origin:
                self.third_party_cache[import_name] = True
                return True
        except:
            pass
        
        self.third_party_cache[import_name] = False
        return False
    
    def _is_local_file_import(self, import_name: str) -> bool:
        """Détermine si c'est un import de fichier local."""
        return '.' in import_name and not import_name.startswith('.')
    
    def _is_local_package_import(self, import_name: str) -> bool:
        """Détermine si c'est un import de package local."""
        return not '.' in import_name and not import_name.startswith('.')

class PackageAnalyzer:
    """Analyseur de packages pour comprendre les exports."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.package_cache = {}
    
    def analyze_package_exports(self, package_path: Path) -> Dict[str, str]:
        """Analyse les exports d'un package via son __init__.py."""
        if package_path in self.package_cache:
            return self.package_cache[package_path]
        
        exports = {}
        init_file = package_path / "__init__.py"
        
        if init_file.exists():
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                # Analyser les imports et exports
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module:
                            # from .module import Class
                            for alias in node.names:
                                if node.level == 1:  # Import relatif
                                    exports[alias.name] = f"{package_path.name}.{node.module}.{alias.name}"
                    
                    elif isinstance(node, ast.Assign):
                        # __all__ = ['Class1', 'Class2']
                        if (isinstance(node.targets[0], ast.Name) and 
                            node.targets[0].id == '__all__' and 
                            isinstance(node.value, ast.List)):
                            for item in node.value.elts:
                                if isinstance(item, ast.Constant):
                                    exports[item.value] = f"{package_path.name}.{item.value}"
                
            except Exception as e:
                logger.error(f"Erreur analyse package {package_path}: {e}")
        
        self.package_cache[package_path] = exports
        return exports
    
    def find_package_for_import(self, import_name: str, current_file: Path) -> Optional[Path]:
        """Trouve le package correspondant à un import."""
        # Chercher dans les packages parents
        current_dir = current_file.parent
        
        while current_dir != self.project_root.parent:
            if (current_dir / "__init__.py").exists():
                # Vérifier si ce package peut exporter l'import
                exports = self.analyze_package_exports(current_dir)
                if import_name in exports:
                    return current_dir
            
            current_dir = current_dir.parent
        
        return None

class ImportResolver:
    """Résolveur d'imports locaux amélioré avec approche générique."""
    
    def __init__(self, project_root: str = '.'):
        self.project_root = Path(project_root)
        self.import_cache: Dict[str, Optional[str]] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.file_structure_cache: Dict[str, List[str]] = {}
        self.unresolved_imports: List[str] = []
        self.error_classifier = ImportErrorClassifier()
        self.package_analyzer = PackageAnalyzer(self.project_root)
        
    def _build_file_structure_cache(self):
        """Construit un cache de la structure des fichiers."""
        if self.file_structure_cache:
            return
            
        logger.info("🔧 Construction du cache de structure des fichiers...")
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    path_str = str(file_path)
                    
                    # Indexer par nom de fichier
                    if file not in self.file_structure_cache:
                        self.file_structure_cache[file] = []
                    self.file_structure_cache[file].append(path_str)
                    
                    # Indexer par chemin complet
                    path_parts = list(file_path.parts)
                    path_key = '/'.join(path_parts)
                    self.file_structure_cache[path_key] = [path_str]
        
        logger.info(f"✅ Cache construit: {len(self.file_structure_cache)} entrées")
    
    def resolve_import(self, import_name: str, current_file: str) -> Optional[str]:
        """Résout un import vers un fichier Python."""
        cache_key = f"{import_name}:{current_file}"
        if cache_key in self.import_cache:
            return self.import_cache[cache_key]
        
        logger.debug(f"🔍 Résolution: {import_name} depuis {current_file}")
        
        self._build_file_structure_cache()
        current_path = Path(current_file)
        
        # Simuler les modifications de sys.path pour ce fichier
        search_paths = self._get_search_paths_for_file(current_file)
        
        # Import relatif
        if import_name.startswith('.'):
            result = self._resolve_relative_import(import_name, current_path)
        else:
            result = self._resolve_absolute_import_with_paths(import_name, search_paths)
        
        if result:
            logger.debug(f"✅ Résolu: {import_name} -> {result}")
        else:
            logger.warning(f"❌ Non résolu: {import_name} depuis {current_file}")
            self.unresolved_imports.append(f"{import_name} (depuis {current_file})")
        
        self.import_cache[cache_key] = result
        return result
    
    def _resolve_relative_import(self, import_name: str, current_path: Path) -> Optional[str]:
        """Résout un import relatif."""
        logger.debug(f"  📁 Import relatif: {import_name}")
        
        dots = len(import_name) - len(import_name.lstrip('.'))
        module_name = import_name[dots:]
        
        # Remonter dans l'arborescence
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
                logger.debug(f"    ✅ Trouvé: {file_path}")
                return str(file_path)
        
        logger.debug(f"    ❌ Aucun fichier trouvé pour {module_name}")
        return None
    
    def _resolve_absolute_import_with_paths(self, import_name: str, search_paths: List[Path]) -> Optional[str]:
        """Résout un import absolu en utilisant les chemins de recherche."""
        logger.debug(f"  📁 Import absolu avec chemins: {import_name}")
        
        import_parts = import_name.split('.')
        
        # Cas 1: Import avec classe (ex: MemoryEngine.core.engine.MemoryEngine)
        if len(import_parts) > 1:
            module_parts = import_parts[:-1]  # ['MemoryEngine', 'core', 'engine']
            class_name = import_parts[-1]     # 'MemoryEngine'
            
            logger.debug(f"    Module parts: {module_parts}")
            logger.debug(f"    Class name: {class_name}")
            
            # Chercher dans tous les chemins de recherche
            for search_path in search_paths:
                # Construire le chemin attendu
                expected_path = search_path / '/'.join(module_parts[:-1]) / f'{module_parts[-1]}.py'
                
                logger.debug(f"    Chemin attendu: {expected_path}")
                
                # Vérifier si le fichier existe
                if expected_path.exists():
                    logger.debug(f"    ✅ Fichier trouvé: {expected_path}")
                    return str(expected_path)
                else:
                    logger.debug(f"    ❌ Fichier non trouvé: {expected_path}")
                
                # Cas 2: Chercher par nom de fichier dans ce chemin
                last_module = module_parts[-1]
                if f'{last_module}.py' in self.file_structure_cache:
                    candidates = self.file_structure_cache[f'{last_module}.py']
                    
                    for candidate in candidates:
                        candidate_path = Path(candidate)
                        if candidate_path.is_relative_to(search_path):
                            path_parts = list(candidate_path.parts)
                            path_dirs = path_parts[:-1]
                            
                            # Vérifier si le chemin correspond au module
                            if len(path_dirs) >= len(module_parts):
                                path_suffix = path_dirs[-(len(module_parts)):]
                                if path_suffix == module_parts:
                                    logger.debug(f"    ✅ Match trouvé: {candidate}")
                                    return candidate
                                else:
                                    logger.debug(f"    ❌ Pas de match: {path_suffix} != {module_parts}")
            
            # Cas 3: Chercher récursivement dans tout le projet
            logger.debug(f"    🔍 Recherche récursive...")
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
                                logger.debug(f"    ✅ Match récursif: {file_path}")
                                return str(file_path)
        
        # Cas 4: Import simple (ex: os, sys)
        if len(import_parts) == 1:
            module_name = import_parts[0]
            logger.debug(f"    Import simple: {module_name}")
            
            # Vérifier si c'est une bibliothèque standard
            if module_name in self.error_classifier.standard_libs:
                logger.debug(f"    ✅ Bibliothèque standard: {module_name}")
                return None  # Ne pas résoudre les bibliothèques standard
            
            if f'{module_name}.py' in self.file_structure_cache:
                candidates = self.file_structure_cache[f'{module_name}.py']
                if candidates:
                    logger.debug(f"    ✅ Import simple trouvé: {candidates[0]}")
                    return candidates[0]
                else:
                    logger.debug(f"    ❌ Import simple non trouvé: {module_name}")
        
        logger.debug(f"    ❌ Aucune correspondance trouvée")
        return None
    
    def _get_search_paths_for_file(self, file_path: str) -> List[Path]:
        """Détermine les chemins de recherche pour un fichier donné."""
        search_paths = [self.project_root]  # Chemin par défaut
        
        # Analyser les modifications de sys.path dans le fichier
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Chercher les modifications de sys.path
            import re
            
            # sys.path.insert(0, str(project_root))
            project_root_pattern = r'sys\.path\.insert\(0,\s*str\(project_root\)\)'
            if re.search(project_root_pattern, content):
                # Extraire la définition de project_root
                project_root_match = re.search(r'project_root\s*=\s*Path\(__file__\)\.parent\.parent\.parent', content)
                if project_root_match:
                    file_dir = Path(file_path).parent
                    project_root = file_dir.parent.parent.parent
                    search_paths.insert(0, project_root)
                    logger.debug(f"  📁 Ajouté project_root: {project_root}")
            
            # sys.path.insert(0, os.path.abspath('.'))
            abspath_pattern = r'sys\.path\.insert\(0,\s*os\.path\.abspath\([\'"]\.[\'"]\)\)'
            if re.search(abspath_pattern, content):
                search_paths.insert(0, self.project_root)
                logger.debug(f"  📁 Ajouté abspath('.')")
            
            # sys.path.insert(0, _current_dir)
            current_dir_pattern = r'sys\.path\.insert\(0,\s*_current_dir\)'
            if re.search(current_dir_pattern, content):
                file_dir = Path(file_path).parent
                search_paths.insert(0, file_dir)
                logger.debug(f"  📁 Ajouté _current_dir: {file_dir}")
                
        except Exception as e:
            logger.error(f"Erreur analyse sys.path pour {file_path}: {e}")
        
        return search_paths
    
    def extract_imports_from_file(self, file_path: str) -> List[ImportInfo]:
        """Extrait tous les imports d'un fichier Python."""
        logger.info(f"📁 Extraction imports: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_info = ImportInfo(
                            module_name=alias.name,
                            class_name=None,
                            is_relative=False,
                            level=0
                        )
                        imports.append(import_info)
                        logger.debug(f"  📦 Import: {alias.name}")
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        if module:
                            full_import = f'{module}.{alias.name}'
                            import_info = ImportInfo(
                                module_name=full_import,
                                class_name=alias.name,
                                is_relative=node.level > 0,
                                level=node.level
                            )
                        else:
                            import_info = ImportInfo(
                                module_name=alias.name,
                                class_name=alias.name,
                                is_relative=node.level > 0,
                                level=node.level
                            )
                        imports.append(import_info)
                        logger.debug(f"  📦 ImportFrom: {import_info.module_name}")
            
            logger.info(f"  ✅ {len(imports)} imports extraits")
            return imports
            
        except Exception as e:
            logger.error(f"  ❌ Erreur extraction imports {file_path}: {e}")
            return []
    
    def analyze_file_dependencies(self, file_path: str) -> DependencyNode:
        """Analyse les dépendances d'un fichier."""
        logger.info(f"🔍 Analyse dépendances: {file_path}")
        
        imports = self.extract_imports_from_file(file_path)
        dependencies = set()
        unresolved_imports = []
        import_errors = []
        
        for import_info in imports:
            resolved_file = self.resolve_import(import_info.module_name, file_path)
            if resolved_file:
                import_info.file_path = resolved_file
                import_info.resolved = True
                dependencies.add(resolved_file)
                self.dependency_graph[file_path].add(resolved_file)
                logger.debug(f"  ✅ Dépendance résolue: {import_info.module_name} -> {resolved_file}")
            else:
                import_info.error_message = "Non résolu"
                unresolved_imports.append(import_info.module_name)
                
                # Classifier l'erreur
                error_info = self.error_classifier.classify_import_error(
                    import_info.module_name, file_path
                )
                import_info.error_type = error_info.error_type
                import_errors.append(error_info)
                
                logger.debug(f"  ❌ Dépendance non résolue: {import_info.module_name}")
        
        # Calculer la complexité (nombre d'imports + lignes de code)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            complexity = len(content.split('\n')) + len(imports)
        except:
            complexity = len(imports)
        
        # Détecter les patterns architecturaux (simplifié)
        architectural_patterns = self._detect_architectural_patterns(file_path)
        
        logger.info(f"  📊 Résultats: {len(dependencies)} dépendances, {len(unresolved_imports)} non résolues")
        
        return DependencyNode(
            file_path=file_path,
            imports=imports,
            dependencies=dependencies,
            complexity=complexity,
            architectural_patterns=architectural_patterns,
            unresolved_imports=unresolved_imports,
            import_errors=import_errors
        )
    
    def _detect_architectural_patterns(self, file_path: str) -> List[str]:
        """Détecte les patterns architecturaux dans un fichier."""
        patterns = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Détecter les classes
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            if len(classes) == 1:
                patterns.append('Singleton')
            
            # Détecter les factories
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and 'factory' in node.name.lower():
                    patterns.append('Factory')
                    break
            
            # Détecter les décorateurs
            decorators = [node for node in ast.walk(tree) if hasattr(node, 'decorator_list') and node.decorator_list]
            if decorators:
                patterns.append('Decorator')
            
        except Exception as e:
            logger.error(f"Erreur détection patterns {file_path}: {e}")
        
        return patterns
    
    def analyze_recursive_dependencies(self, start_files: List[str], max_depth: int = 50) -> Dict[str, DependencyNode]:
        """Analyse récursive des dépendances."""
        logger.info(f"🔄 Analyse récursive: {len(start_files)} fichiers de départ")
        
        visited = set()
        all_dependencies: Dict[str, DependencyNode] = {}
        
        def analyze_recursively(file_path: str, depth: int = 0):
            if depth > max_depth or file_path in visited:
                return
            
            visited.add(file_path)
            logger.debug(f"  {'  ' * depth}📁 {file_path}")
            
            # Analyser le fichier
            dependency_node = self.analyze_file_dependencies(file_path)
            all_dependencies[file_path] = dependency_node
            
            # Analyser récursivement les dépendances
            for dep_file in dependency_node.dependencies:
                if dep_file not in visited:
                    analyze_recursively(dep_file, depth + 1)
        
        # Analyser tous les fichiers de départ
        for file_path in start_files:
            if os.path.exists(file_path):
                analyze_recursively(file_path)
            else:
                logger.warning(f"⚠️ Fichier non trouvé: {file_path}")
        
        logger.info(f"✅ Analyse terminée: {len(all_dependencies)} fichiers analysés")
        return all_dependencies
    
    def get_dependency_stats(self, dependencies: Dict[str, DependencyNode]) -> Dict[str, any]:
        """Calcule les statistiques des dépendances."""
        total_files = len(dependencies)
        total_imports = sum(len(node.imports) for node in dependencies.values())
        resolved_imports = sum(len([imp for imp in node.imports if imp.resolved]) for node in dependencies.values())
        total_complexity = sum(node.complexity for node in dependencies.values())
        
        # Patterns architecturaux
        all_patterns = []
        for node in dependencies.values():
            all_patterns.extend(node.architectural_patterns)
        
        pattern_counts = defaultdict(int)
        for pattern in all_patterns:
            pattern_counts[pattern] += 1
        
        # Imports non résolus
        all_unresolved = []
        for node in dependencies.values():
            all_unresolved.extend(node.unresolved_imports)
        
        # Erreurs d'imports classifiées
        all_errors = []
        for node in dependencies.values():
            all_errors.extend(node.import_errors)
        
        error_counts = defaultdict(int)
        for error in all_errors:
            error_counts[error.error_type.value] += 1
        
        logger.info(f"📊 Statistiques finales:")
        logger.info(f"  Total fichiers: {total_files}")
        logger.info(f"  Total imports: {total_imports}")
        logger.info(f"  Imports résolus: {resolved_imports}")
        logger.info(f"  Taux de résolution: {resolved_imports/total_imports*100:.2f}%")
        logger.info(f"  Imports non résolus: {len(all_unresolved)}")
        logger.info(f"  Erreurs classifiées: {len(all_errors)}")
        
        return {
            'total_files': total_files,
            'total_imports': total_imports,
            'resolved_imports': resolved_imports,
            'resolution_rate': resolved_imports / total_imports if total_imports > 0 else 0,
            'total_complexity': total_complexity,
            'average_complexity': total_complexity / total_files if total_files > 0 else 0,
            'architectural_patterns': dict(pattern_counts),
            'unresolved_imports': all_unresolved,
            'import_errors': all_errors,
            'error_counts': dict(error_counts)
        }

# Instance globale
global_import_resolver = ImportResolver() 