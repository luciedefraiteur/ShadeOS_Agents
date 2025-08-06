"""
🐍 Partitionneur AST Python

Partitionneur spécialisé pour les fichiers Python utilisant l'AST natif.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import ast
from typing import List, Dict, Any, Optional, Set
from .base_ast_partitioner import BaseASTPartitioner
from ..partition_schemas import BlockType, PartitioningError
from ..error_logger import log_partitioning_warning


class PythonASTPartitioner(BaseASTPartitioner):
    """Partitionneur spécialisé pour Python."""
    
    def __init__(self, max_tokens: int = 3500, overlap_lines: int = 5):
        super().__init__(max_tokens, overlap_lines)
        self.python_version = (3, 8)  # Version Python cible
    
    def get_supported_extensions(self) -> List[str]:
        """Extensions supportées."""
        return ['.py', '.pyw', '.pyi']
    
    def parse_content(self, content: str, file_path: str) -> ast.AST:
        """Parse le contenu Python en AST."""
        try:
            return ast.parse(content, filename=file_path)
        except SyntaxError as e:
            # Tentative avec mode exec explicite
            try:
                return ast.parse(content, filename=file_path, mode='exec')
            except SyntaxError:
                # Re-raise l'erreur originale
                raise e
    
    def extract_top_level_nodes(self, tree: ast.AST) -> List[ast.AST]:
        """Extrait les nœuds de niveau supérieur."""
        if not isinstance(tree, ast.Module):
            raise PartitioningError(f"Expected Module, got {type(tree)}")
        
        # Filtre les imports (déjà traités séparément)
        top_level = []
        for node in tree.body:
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                top_level.append(node)
        
        return top_level
    
    def get_node_type(self, node: ast.AST) -> BlockType:
        """Détermine le type d'un nœud Python."""
        
        if isinstance(node, ast.ClassDef):
            return BlockType.CLASS
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return BlockType.FUNCTION
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            return BlockType.IMPORT
        elif isinstance(node, ast.Assign):
            return BlockType.VARIABLE
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, str):
                return BlockType.COMMENT  # Docstring
        
        return BlockType.UNKNOWN
    
    def get_node_name(self, node: ast.AST) -> Optional[str]:
        """Extrait le nom d'un nœud Python."""
        
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            return node.name
        elif isinstance(node, ast.Assign):
            # Essaie d'extraire le nom de la variable
            if len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name):
                    return target.id
                elif isinstance(target, ast.Attribute):
                    return ast.unparse(target) if hasattr(ast, 'unparse') else str(target)
        elif isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
            return f"import_{','.join(names)}"
        elif isinstance(node, ast.ImportFrom):
            module = node.module or "relative"
            names = [alias.name for alias in node.names]
            return f"from_{module}_import_{','.join(names)}"
        
        return None
    
    def extract_dependencies(self, node: ast.AST) -> List[str]:
        """Extrait les dépendances d'un nœud Python."""
        
        dependencies = set()
        
        # Parcourt tous les sous-nœuds
        for child in ast.walk(node):
            # Appels de fonction
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    dependencies.add(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    # Extrait le nom de base
                    if isinstance(child.func.value, ast.Name):
                        dependencies.add(child.func.value.id)
            
            # Accès aux attributs
            elif isinstance(child, ast.Attribute):
                if isinstance(child.value, ast.Name):
                    dependencies.add(child.value.id)
            
            # Noms de variables
            elif isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                dependencies.add(child.id)
        
        # Filtre les built-ins et mots-clés Python
        python_builtins = {
            'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
            'range', 'enumerate', 'zip', 'map', 'filter', 'sum', 'max', 'min',
            'abs', 'round', 'sorted', 'reversed', 'any', 'all', 'isinstance',
            'hasattr', 'getattr', 'setattr', 'delattr', 'type', 'super',
            'True', 'False', 'None', 'self', 'cls'
        }
        
        filtered_deps = [dep for dep in dependencies if dep not in python_builtins]
        return sorted(filtered_deps)
    
    def extract_class_methods(self, class_node: ast.ClassDef) -> List[ast.AST]:
        """Extrait les méthodes d'une classe."""
        
        methods = []
        for node in class_node.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(node)
        
        return methods
    
    def extract_class_attributes(self, class_node: ast.ClassDef) -> List[str]:
        """Extrait les attributs d'une classe."""
        
        attributes = set()
        
        for node in ast.walk(class_node):
            # Assignations dans __init__ ou autres méthodes
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == 'self':
                            attributes.add(target.attr)
            
            # Annotations de type
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Attribute):
                    if isinstance(node.target.value, ast.Name) and node.target.value.id == 'self':
                        attributes.add(node.target.attr)
        
        return sorted(attributes)
    
    def extract_function_parameters(self, func_node: ast.FunctionDef) -> List[str]:
        """Extrait les paramètres d'une fonction."""
        
        params = []
        
        # Arguments positionnels
        for arg in func_node.args.args:
            params.append(arg.arg)
        
        # Arguments avec valeurs par défaut
        for arg in func_node.args.posonlyargs:
            params.append(arg.arg)
        
        # Arguments keyword-only
        for arg in func_node.args.kwonlyargs:
            params.append(arg.arg)
        
        # *args
        if func_node.args.vararg:
            params.append(f"*{func_node.args.vararg.arg}")
        
        # **kwargs
        if func_node.args.kwarg:
            params.append(f"**{func_node.args.kwarg.arg}")
        
        return params
    
    def extract_decorators(self, node: ast.AST) -> List[str]:
        """Extrait les décorateurs d'un nœud."""
        
        if not hasattr(node, 'decorator_list'):
            return []
        
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                if hasattr(ast, 'unparse'):
                    decorators.append(ast.unparse(decorator))
                else:
                    decorators.append(str(decorator))
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    decorators.append(f"{decorator.func.id}(...)")
                elif hasattr(ast, 'unparse'):
                    decorators.append(ast.unparse(decorator))
        
        return decorators
    
    def analyze_node_complexity(self, node: ast.AST) -> Dict[str, Any]:
        """Analyse détaillée de la complexité d'un nœud."""
        
        complexity_info = {
            'cyclomatic_complexity': 1,
            'nesting_depth': 0,
            'num_statements': 0,
            'num_functions': 0,
            'num_classes': 0,
            'num_loops': 0,
            'num_conditions': 0
        }
        
        current_depth = 0
        max_depth = 0
        
        for child in ast.walk(node):
            # Complexité cyclomatique
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity_info['cyclomatic_complexity'] += 1
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            
            # Compteurs spécifiques
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity_info['num_functions'] += 1
            elif isinstance(child, ast.ClassDef):
                complexity_info['num_classes'] += 1
            elif isinstance(child, (ast.For, ast.While)):
                complexity_info['num_loops'] += 1
            elif isinstance(child, ast.If):
                complexity_info['num_conditions'] += 1
            
            # Statements
            if isinstance(child, ast.stmt):
                complexity_info['num_statements'] += 1
        
        complexity_info['nesting_depth'] = max_depth
        return complexity_info
    
    def extract_docstring(self, node: ast.AST) -> Optional[str]:
        """Extrait la docstring d'un nœud."""
        
        if not hasattr(node, 'body') or not node.body:
            return None
        
        first_stmt = node.body[0]
        if (isinstance(first_stmt, ast.Expr) and 
            isinstance(first_stmt.value, ast.Constant) and
            isinstance(first_stmt.value.value, str)):
            return first_stmt.value.value
        
        return None
    
    def _create_partition_block(self, content: str, node: ast.AST,
                               location, node_content: str, token_count: int):
        """Crée un bloc de partition Python enrichi."""
        
        # Bloc de base
        block = super()._create_partition_block(
            content, node, location, node_content, token_count
        )
        
        # Enrichissement spécifique Python
        block.metadata = {
            'decorators': self.extract_decorators(node),
            'docstring': self.extract_docstring(node),
            'complexity_analysis': self.analyze_node_complexity(node)
        }
        
        # Informations spécifiques selon le type
        if isinstance(node, ast.ClassDef):
            block.metadata.update({
                'base_classes': [ast.unparse(base) if hasattr(ast, 'unparse') else str(base) 
                               for base in node.bases],
                'methods': [method.name for method in self.extract_class_methods(node)],
                'attributes': self.extract_class_attributes(node)
            })
            block.child_scopes = [method.name for method in self.extract_class_methods(node)]
        
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            block.metadata.update({
                'parameters': self.extract_function_parameters(node),
                'is_async': isinstance(node, ast.AsyncFunctionDef),
                'return_annotation': (ast.unparse(node.returns) if hasattr(ast, 'unparse') and node.returns 
                                    else str(node.returns) if node.returns else None)
            })
        
        return block
    
    def validate_python_syntax(self, content: str) -> Dict[str, Any]:
        """Valide la syntaxe Python et retourne des informations."""
        
        validation_result = {
            'is_valid': False,
            'syntax_errors': [],
            'warnings': [],
            'python_version_required': None
        }
        
        try:
            tree = ast.parse(content)
            validation_result['is_valid'] = True
            
            # Détection de features spécifiques à certaines versions
            for node in ast.walk(tree):
                # f-strings (Python 3.6+)
                if isinstance(node, ast.JoinedStr):
                    validation_result['python_version_required'] = (3, 6)
                
                # Assignment expressions := (Python 3.8+)
                elif isinstance(node, ast.NamedExpr):
                    validation_result['python_version_required'] = (3, 8)
                
                # Positional-only parameters (Python 3.8+)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.args.posonlyargs:
                        validation_result['python_version_required'] = (3, 8)
        
        except SyntaxError as e:
            validation_result['syntax_errors'].append({
                'line': e.lineno,
                'column': e.offset,
                'message': e.msg,
                'text': e.text
            })
        
        return validation_result

    def extract_class_hierarchy(self, class_node: ast.ClassDef) -> Dict[str, Any]:
        """Analyse la hiérarchie d'une classe."""

        hierarchy = {
            'name': class_node.name,
            'bases': [],
            'metaclass': None,
            'mro_complexity': 0
        }

        # Analyse des classes de base
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                hierarchy['bases'].append(base.id)
            elif isinstance(base, ast.Attribute):
                if hasattr(ast, 'unparse'):
                    hierarchy['bases'].append(ast.unparse(base))
                else:
                    hierarchy['bases'].append(f"{base.value.id}.{base.attr}")

        # Analyse des keywords (metaclass, etc.)
        for keyword in class_node.keywords:
            if keyword.arg == 'metaclass':
                if isinstance(keyword.value, ast.Name):
                    hierarchy['metaclass'] = keyword.value.id

        # Calcul de la complexité MRO
        hierarchy['mro_complexity'] = len(hierarchy['bases']) * 1.5

        return hierarchy

    def extract_import_analysis(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyse détaillée des imports avec résolution via ImportResolver."""

        import_analysis = {
            'standard_library': [],
            'third_party': [],
            'local_imports': [],
            'relative_imports': [],
            'star_imports': [],
            'conditional_imports': [],
            'all_imports': []  # NOUVEAU : liste unifiée de tous les imports
        }

        # Importer l'ImportResolver
        try:
            from ..import_resolver import ImportResolver
            resolver = ImportResolver()
        except ImportError:
            # Fallback si ImportResolver n'est pas disponible
            resolver = None

        # Bibliothèques standard Python connues
        stdlib_modules = {
            'os', 'sys', 'json', 'datetime', 'collections', 'itertools',
            'functools', 'typing', 're', 'math', 'random', 'pathlib',
            'asyncio', 'threading', 'multiprocessing', 'logging'
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    
                    # Ajouter à la liste unifiée
                    import_analysis['all_imports'].append(alias.name)
                    
                    # Utiliser l'ImportResolver si disponible
                    if resolver:
                        try:
                            resolved_path = resolver.resolve_import(alias.name, 'current_file.py')
                            if resolved_path:
                                import_analysis['local_imports'].append(alias.name)
                                continue
                        except:
                            pass
                    
                    # Fallback sur la classification manuelle
                    if module_name in stdlib_modules:
                        import_analysis['standard_library'].append(alias.name)
                    else:
                        import_analysis['third_party'].append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    if node.level > 0:  # Relative import
                        # Construire l'import relatif complet
                        dots = '.' * node.level
                        for alias in node.names:
                            if node.module:
                                relative_import = f"{dots}{node.module}.{alias.name}"
                            else:
                                relative_import = f"{dots}{alias.name}"
                            import_analysis['all_imports'].append(relative_import)
                        
                        import_analysis['relative_imports'].append({
                            'module': node.module,
                            'level': node.level,
                            'names': [alias.name for alias in node.names]
                        })
                    else:
                        module_name = node.module.split('.')[0]
                        
                        # Ajouter tous les imports from
                        for alias in node.names:
                            from_import = f"{node.module}.{alias.name}"
                            import_analysis['all_imports'].append(from_import)
                        
                        import_info = {
                            'module': node.module,
                            'names': [alias.name for alias in node.names]
                        }

                        # Utiliser l'ImportResolver si disponible
                        if resolver:
                            try:
                                resolved_path = resolver.resolve_import(node.module, 'current_file.py')
                                if resolved_path:
                                    import_analysis['local_imports'].append(import_info)
                                    continue
                            except:
                                pass

                        # Fallback sur la classification manuelle
                        if module_name in stdlib_modules:
                            import_analysis['standard_library'].append(import_info)
                        else:
                            import_analysis['third_party'].append(import_info)

                        # Détection des star imports
                        if any(alias.name == '*' for alias in node.names):
                            import_analysis['star_imports'].append(node.module)

        return import_analysis
