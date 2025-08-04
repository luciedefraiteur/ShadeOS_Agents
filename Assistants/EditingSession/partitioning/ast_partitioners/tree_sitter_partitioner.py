"""
🌳 Partitionneur Universel Tree-sitter

Partitionneur universel utilisant Tree-sitter pour tous les langages.
Étape 1 de la stratégie hybride : Découverte universelle.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

from typing import List, Dict, Any, Optional, Set
from .base_ast_partitioner import BaseASTPartitioner
from ..partition_schemas import BlockType, PartitioningError
from ..error_logger import log_partitioning_error, log_partitioning_warning

try:
    import tree_sitter
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    tree_sitter = None


class TreeSitterPartitioner(BaseASTPartitioner):
    """Partitionneur universel utilisant Tree-sitter."""
    
    # Mapping des types de nœuds par langage
    LANGUAGE_NODE_MAPPINGS = {
        'python': {
            'class': ['class_definition'],
            'function': ['function_definition', 'async_function_definition'],
            'import': ['import_statement', 'import_from_statement'],
            'variable': ['assignment', 'augmented_assignment'],
            'comment': ['comment']
        },
        'javascript': {
            'class': ['class_declaration'],
            'function': ['function_declaration', 'arrow_function', 'function_expression'],
            'import': ['import_statement', 'export_statement'],
            'variable': ['variable_declaration', 'lexical_declaration'],
            'comment': ['comment']
        },
        'typescript': {
            'class': ['class_declaration'],
            'function': ['function_declaration', 'arrow_function', 'method_definition'],
            'import': ['import_statement', 'export_statement'],
            'variable': ['variable_declaration', 'lexical_declaration'],
            'comment': ['comment']
        },
        'rust': {
            'class': ['struct_item', 'enum_item', 'trait_item'],
            'function': ['function_item'],
            'import': ['use_declaration'],
            'variable': ['let_declaration'],
            'comment': ['line_comment', 'block_comment']
        },
        'go': {
            'class': ['type_declaration'],
            'function': ['function_declaration', 'method_declaration'],
            'import': ['import_declaration'],
            'variable': ['var_declaration'],
            'comment': ['comment']
        },
        'cpp': {
            'class': ['class_specifier', 'struct_specifier'],
            'function': ['function_definition', 'function_declarator'],
            'import': ['preproc_include'],
            'variable': ['declaration'],
            'comment': ['comment']
        },
        'java': {
            'class': ['class_declaration', 'interface_declaration'],
            'function': ['method_declaration', 'constructor_declaration'],
            'import': ['import_declaration'],
            'variable': ['variable_declaration'],
            'comment': ['comment']
        }
    }
    
    def __init__(self, language: str, max_tokens: int = 3500, overlap_lines: int = 5):
        if not TREE_SITTER_AVAILABLE:
            raise PartitioningError("Tree-sitter not available. Install with: pip install tree-sitter")
        
        super().__init__(max_tokens, overlap_lines)
        self.language = language.lower()
        self.parser = None
        self.tree_sitter_language = None
        self._init_parser()
    
    def _init_parser(self):
        """Initialise le parser Tree-sitter pour le langage."""
        try:
            # Tentative de chargement du langage
            language_names = [
                f'tree-sitter-{self.language}',
                f'tree_sitter_{self.language}',
                self.language
            ]
            
            for lang_name in language_names:
                try:
                    self.tree_sitter_language = tree_sitter.Language(lang_name)
                    break
                except:
                    continue
            
            if not self.tree_sitter_language:
                raise PartitioningError(f"Tree-sitter language '{self.language}' not found")
            
            self.parser = tree_sitter.Parser()
            self.parser.set_language(self.tree_sitter_language)
            
        except Exception as e:
            log_partitioning_error(
                "tree_sitter_init_error",
                f"Failed to initialize Tree-sitter for {self.language}: {e}",
                f"tree_sitter_{self.language}",
                exception=e
            )
            raise PartitioningError(f"Failed to initialize Tree-sitter for {self.language}")
    
    def get_supported_extensions(self) -> List[str]:
        """Extensions supportées selon le langage."""
        extension_mappings = {
            'python': ['.py', '.pyw', '.pyi'],
            'javascript': ['.js', '.jsx', '.mjs'],
            'typescript': ['.ts', '.tsx'],
            'rust': ['.rs'],
            'go': ['.go'],
            'cpp': ['.cpp', '.cxx', '.cc', '.c', '.h', '.hpp'],
            'java': ['.java'],
            'c': ['.c', '.h'],
            'ruby': ['.rb'],
            'php': ['.php'],
            'swift': ['.swift'],
            'kotlin': ['.kt', '.kts']
        }
        return extension_mappings.get(self.language, [f'.{self.language}'])
    
    def parse_content(self, content: str, file_path: str):
        """Parse le contenu avec Tree-sitter."""
        try:
            content_bytes = content.encode('utf-8')
            tree = self.parser.parse(content_bytes)
            return tree.root_node
        except Exception as e:
            log_partitioning_error(
                "tree_sitter_parse_error",
                f"Failed to parse content: {e}",
                file_path,
                exception=e
            )
            raise PartitioningError(f"Tree-sitter parsing failed: {e}")
    
    def extract_top_level_nodes(self, root_node) -> List:
        """Extrait les nœuds de niveau supérieur."""
        if not root_node or not hasattr(root_node, 'children'):
            return []
        
        top_level_nodes = []
        node_mappings = self.LANGUAGE_NODE_MAPPINGS.get(self.language, {})
        
        # Collecte tous les types de nœuds intéressants
        interesting_types = set()
        for category_types in node_mappings.values():
            interesting_types.update(category_types)
        
        # Si pas de mapping spécifique, prend tous les enfants directs
        if not interesting_types:
            return list(root_node.children)
        
        # Filtre selon les types intéressants
        for child in root_node.children:
            if child.type in interesting_types:
                top_level_nodes.append(child)
            # Inclut aussi les nœuds non mappés pour éviter de perdre du contenu
            elif child.type not in ['comment', 'newline', 'whitespace']:
                top_level_nodes.append(child)
        
        return top_level_nodes
    
    def get_node_type(self, node) -> BlockType:
        """Détermine le type d'un nœud Tree-sitter."""
        if not node or not hasattr(node, 'type'):
            return BlockType.UNKNOWN
        
        node_mappings = self.LANGUAGE_NODE_MAPPINGS.get(self.language, {})
        
        for block_type, node_types in node_mappings.items():
            if node.type in node_types:
                if block_type == 'class':
                    return BlockType.CLASS
                elif block_type == 'function':
                    return BlockType.FUNCTION
                elif block_type == 'import':
                    return BlockType.IMPORT
                elif block_type == 'variable':
                    return BlockType.VARIABLE
                elif block_type == 'comment':
                    return BlockType.COMMENT
        
        return BlockType.UNKNOWN
    
    def get_node_name(self, node) -> Optional[str]:
        """Extrait le nom d'un nœud Tree-sitter."""
        if not node or not hasattr(node, 'children'):
            return None
        
        # Stratégies de recherche de nom selon le type
        name_strategies = [
            self._extract_name_by_field,
            self._extract_name_by_pattern,
            self._extract_name_by_position
        ]
        
        for strategy in name_strategies:
            name = strategy(node)
            if name:
                return name
        
        return None
    
    def _extract_name_by_field(self, node) -> Optional[str]:
        """Extrait le nom via les champs nommés Tree-sitter."""
        try:
            # Tentative d'accès aux champs nommés
            if hasattr(node, 'child_by_field_name'):
                name_node = node.child_by_field_name('name')
                if name_node:
                    return self._node_text(name_node)
            
            # Autres champs possibles
            for field_name in ['identifier', 'id', 'function_name', 'class_name']:
                if hasattr(node, 'child_by_field_name'):
                    field_node = node.child_by_field_name(field_name)
                    if field_node:
                        return self._node_text(field_node)
        except:
            pass
        
        return None
    
    def _extract_name_by_pattern(self, node) -> Optional[str]:
        """Extrait le nom par patterns selon le type de nœud."""
        node_type = node.type
        
        # Patterns par type de nœud
        if 'function' in node_type or 'method' in node_type:
            return self._find_identifier_after_keyword(node, ['function', 'def', 'fn'])
        elif 'class' in node_type or 'struct' in node_type:
            return self._find_identifier_after_keyword(node, ['class', 'struct', 'trait'])
        elif 'variable' in node_type or 'declaration' in node_type:
            return self._find_first_identifier(node)
        
        return None
    
    def _extract_name_by_position(self, node) -> Optional[str]:
        """Extrait le nom par position (fallback)."""
        try:
            # Cherche le premier identifier dans les enfants
            for child in node.children:
                if child.type == 'identifier':
                    return self._node_text(child)
                # Recherche récursive limitée
                elif hasattr(child, 'children') and len(child.children) < 5:
                    for grandchild in child.children:
                        if grandchild.type == 'identifier':
                            return self._node_text(grandchild)
        except:
            pass
        
        return None
    
    def _find_identifier_after_keyword(self, node, keywords: List[str]) -> Optional[str]:
        """Trouve un identifier après un mot-clé."""
        try:
            for i, child in enumerate(node.children):
                child_text = self._node_text(child)
                if child_text and child_text.lower() in keywords:
                    # Cherche l'identifier suivant
                    for j in range(i + 1, len(node.children)):
                        next_child = node.children[j]
                        if next_child.type == 'identifier':
                            return self._node_text(next_child)
        except:
            pass
        
        return None
    
    def _find_first_identifier(self, node) -> Optional[str]:
        """Trouve le premier identifier dans le nœud."""
        try:
            for child in node.children:
                if child.type == 'identifier':
                    return self._node_text(child)
        except:
            pass
        
        return None
    
    def _node_text(self, node) -> Optional[str]:
        """Extrait le texte d'un nœud Tree-sitter."""
        try:
            if hasattr(node, 'text'):
                return node.text.decode('utf-8')
            elif hasattr(node, 'start_byte') and hasattr(node, 'end_byte'):
                # Fallback si text n'est pas disponible
                return None  # Nécessiterait le contenu original
        except:
            pass
        
        return None
    
    def extract_dependencies(self, node) -> List[str]:
        """Extrait les dépendances d'un nœud Tree-sitter."""
        dependencies = set()
        
        try:
            # Parcourt tous les sous-nœuds
            self._collect_identifiers(node, dependencies)
        except Exception as e:
            log_partitioning_warning(
                "dependency_extraction_warning",
                f"Failed to extract dependencies: {e}",
                "tree_sitter"
            )
        
        # Filtre les mots-clés du langage
        filtered_deps = self._filter_language_keywords(dependencies)
        return sorted(filtered_deps)
    
    def _collect_identifiers(self, node, dependencies: Set[str]):
        """Collecte récursivement les identifiers."""
        if not hasattr(node, 'children'):
            return
        
        for child in node.children:
            if child.type == 'identifier':
                text = self._node_text(child)
                if text and len(text) > 1:  # Évite les identifiers trop courts
                    dependencies.add(text)
            elif hasattr(child, 'children'):
                self._collect_identifiers(child, dependencies)
    
    def _filter_language_keywords(self, identifiers: Set[str]) -> List[str]:
        """Filtre les mots-clés du langage."""
        
        # Mots-clés communs par langage
        keywords_by_language = {
            'python': {'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'import', 'from', 'return', 'yield', 'lambda', 'and', 'or', 'not', 'in', 'is', 'True', 'False', 'None'},
            'javascript': {'function', 'class', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default', 'try', 'catch', 'finally', 'return', 'var', 'let', 'const', 'true', 'false', 'null', 'undefined'},
            'typescript': {'function', 'class', 'interface', 'type', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default', 'try', 'catch', 'finally', 'return', 'var', 'let', 'const', 'true', 'false', 'null', 'undefined'},
            'rust': {'fn', 'struct', 'enum', 'trait', 'impl', 'if', 'else', 'for', 'while', 'loop', 'match', 'return', 'let', 'mut', 'true', 'false'},
            'go': {'func', 'type', 'struct', 'interface', 'if', 'else', 'for', 'switch', 'case', 'default', 'return', 'var', 'const', 'true', 'false', 'nil'},
            'java': {'class', 'interface', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default', 'try', 'catch', 'finally', 'return', 'true', 'false', 'null'}
        }
        
        language_keywords = keywords_by_language.get(self.language, set())
        
        return [identifier for identifier in identifiers 
                if identifier not in language_keywords and len(identifier) > 1]
