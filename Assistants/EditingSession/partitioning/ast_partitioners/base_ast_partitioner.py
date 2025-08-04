"""
🌳 Interface de Base pour Partitionneurs AST

Interface commune pour tous les partitionneurs utilisant l'analyse syntaxique.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import ast
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Set, Tuple
from ..partition_schemas import (
    PartitionBlock, PartitionLocation, PartitionResult,
    PartitionMethod, BlockType, PartitioningError
)
from ..location_tracker import LocationTracker
from ..error_logger import log_partitioning_error, log_partitioning_warning


class BaseASTPartitioner(ABC):
    """Interface de base pour partitionneurs AST."""
    
    def __init__(self, max_tokens: int = 3500, overlap_lines: int = 5):
        self.max_tokens = max_tokens
        self.overlap_lines = overlap_lines
        self.location_tracker = LocationTracker()
        self.token_counter = self._init_token_counter()
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """Extensions de fichiers supportées."""
        pass
    
    @abstractmethod
    def parse_content(self, content: str, file_path: str) -> ast.AST:
        """Parse le contenu en AST."""
        pass
    
    @abstractmethod
    def extract_top_level_nodes(self, tree: ast.AST) -> List[ast.AST]:
        """Extrait les nœuds de niveau supérieur."""
        pass
    
    @abstractmethod
    def get_node_type(self, node: ast.AST) -> BlockType:
        """Détermine le type d'un nœud."""
        pass
    
    @abstractmethod
    def get_node_name(self, node: ast.AST) -> Optional[str]:
        """Extrait le nom d'un nœud."""
        pass
    
    @abstractmethod
    def extract_dependencies(self, node: ast.AST) -> List[str]:
        """Extrait les dépendances d'un nœud."""
        pass
    
    def partition(self, file_path: str, content: str) -> PartitionResult:
        """Partitionne le contenu en utilisant l'AST."""
        
        start_time = time.time()
        result = PartitionResult(
            file_path=file_path,
            file_type=self._detect_file_type(file_path),
            total_lines=len(content.split('\n')),
            total_chars=len(content),
            partitions=[],
            strategy_used=PartitionMethod.AST,
            success=False
        )
        
        try:
            # Initialisation du tracker
            self.location_tracker.analyze_file_structure(content)
            
            # Parsing AST
            tree = self.parse_content(content, file_path)
            
            # Extraction des imports globaux
            imports_block = self._extract_imports_block(content, tree)
            if imports_block:
                result.partitions.append(imports_block)
            
            # Extraction des nœuds top-level
            top_level_nodes = self.extract_top_level_nodes(tree)
            
            # Partitionnement de chaque nœud
            for node in top_level_nodes:
                try:
                    blocks = self._partition_node(content, node, file_path)
                    result.partitions.extend(blocks)
                except Exception as e:
                    log_partitioning_error(
                        "node_partition_error",
                        f"Failed to partition node: {e}",
                        file_path,
                        line_number=getattr(node, 'lineno', None),
                        details=f"Node type: {type(node).__name__}"
                    )
                    # Continue avec les autres nœuds
                    continue
            
            # Validation et finalisation
            if self._validate_partitions(result.partitions, content):
                result.success = True
                self._add_overlap_context(result.partitions, content)
            else:
                result.add_warning("Partition validation failed")
            
        except SyntaxError as e:
            result.add_error("syntax_error", str(e), {
                "line": e.lineno,
                "column": e.offset,
                "text": e.text
            })
            # Tentative de récupération partielle
            result.partitions = self._recover_from_syntax_error(content, e)
            
        except Exception as e:
            result.add_error("ast_parsing_error", str(e))
            log_partitioning_error(
                "ast_parsing_error", str(e), file_path, 
                PartitionMethod.AST, exception=e
            )
        
        result.processing_time = time.time() - start_time
        return result
    
    def _partition_node(self, content: str, node: ast.AST, 
                       file_path: str) -> List[PartitionBlock]:
        """Partitionne un nœud AST."""
        
        # Création de la location
        location = self.location_tracker.create_location_from_ast_node(content, node)
        
        # Extraction du contenu
        node_content = location.extract_content(content)
        
        # Vérification de la taille
        token_count = self._count_tokens(node_content)
        
        if token_count <= self.max_tokens:
            # Nœud de taille acceptable
            return [self._create_partition_block(
                content, node, location, node_content, token_count
            )]
        else:
            # Nœud trop gros, subdivision nécessaire
            return self._subdivide_large_node(content, node, file_path)
    
    def _create_partition_block(self, content: str, node: ast.AST,
                               location: PartitionLocation, node_content: str,
                               token_count: int) -> PartitionBlock:
        """Crée un bloc de partition à partir d'un nœud."""
        
        return PartitionBlock(
            content=node_content,
            block_type=self.get_node_type(node),
            location=location,
            partition_method=PartitionMethod.AST,
            block_name=self.get_node_name(node),
            dependencies=self.extract_dependencies(node),
            token_count=token_count,
            complexity_score=self._calculate_complexity(node)
        )
    
    def _subdivide_large_node(self, content: str, node: ast.AST, 
                             file_path: str) -> List[PartitionBlock]:
        """Subdivise un nœud trop volumineux."""
        
        # Stratégie de subdivision selon le type de nœud
        if hasattr(node, 'body') and node.body:
            return self._subdivide_by_body(content, node, file_path)
        else:
            # Fallback : subdivision textuelle
            return self._subdivide_textually(content, node, file_path)
    
    def _subdivide_by_body(self, content: str, node: ast.AST, 
                          file_path: str) -> List[PartitionBlock]:
        """Subdivise un nœud par son body."""
        
        blocks = []
        
        # Traite chaque élément du body
        for child_node in node.body:
            try:
                child_blocks = self._partition_node(content, child_node, file_path)
                blocks.extend(child_blocks)
            except Exception as e:
                log_partitioning_warning(
                    "child_node_partition_warning",
                    f"Failed to partition child node: {e}",
                    file_path,
                    PartitionMethod.AST
                )
                continue
        
        return blocks
    
    def _subdivide_textually(self, content: str, node: ast.AST, 
                            file_path: str) -> List[PartitionBlock]:
        """Subdivision textuelle d'un nœud."""
        
        location = self.location_tracker.create_location_from_ast_node(content, node)
        node_content = location.extract_content(content)
        
        # Division en chunks de lignes
        lines = node_content.split('\n')
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for line in lines:
            line_tokens = self._count_tokens(line)
            
            if current_tokens + line_tokens > self.max_tokens and current_chunk:
                # Finalise le chunk actuel
                chunk_content = '\n'.join(current_chunk)
                chunk_location = self._create_chunk_location(
                    content, location, current_chunk, lines
                )
                
                chunk_block = PartitionBlock(
                    content=chunk_content,
                    block_type=BlockType.CHUNK,
                    location=chunk_location,
                    partition_method=PartitionMethod.AST,
                    block_name=f"{self.get_node_name(node)}_chunk_{len(chunks)}",
                    token_count=current_tokens
                )
                chunks.append(chunk_block)
                
                current_chunk = []
                current_tokens = 0
            
            current_chunk.append(line)
            current_tokens += line_tokens
        
        # Dernier chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunk_location = self._create_chunk_location(
                content, location, current_chunk, lines
            )
            
            chunk_block = PartitionBlock(
                content=chunk_content,
                block_type=BlockType.CHUNK,
                location=chunk_location,
                partition_method=PartitionMethod.AST,
                block_name=f"{self.get_node_name(node)}_chunk_{len(chunks)}",
                token_count=current_tokens
            )
            chunks.append(chunk_block)
        
        return chunks
    
    def _extract_imports_block(self, content: str, tree: ast.AST) -> Optional[PartitionBlock]:
        """Extrait un bloc d'imports globaux."""
        
        import_nodes = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_nodes.append(node)
            else:
                break  # Arrête dès qu'on trouve autre chose qu'un import
        
        if not import_nodes:
            return None
        
        # Création de la location englobante
        first_node = import_nodes[0]
        last_node = import_nodes[-1]
        
        start_location = self.location_tracker.create_location_from_ast_node(content, first_node)
        end_location = self.location_tracker.create_location_from_ast_node(content, last_node)
        
        merged_location = self.location_tracker.merge_locations([start_location, end_location])
        imports_content = merged_location.extract_content(content)
        
        return PartitionBlock(
            content=imports_content,
            block_type=BlockType.IMPORT,
            location=merged_location,
            partition_method=PartitionMethod.AST,
            block_name="imports",
            dependencies=[],
            token_count=self._count_tokens(imports_content)
        )
    
    def _recover_from_syntax_error(self, content: str, 
                                  syntax_error: SyntaxError) -> List[PartitionBlock]:
        """Récupération partielle en cas d'erreur de syntaxe."""
        
        lines = content.split('\n')
        error_line = syntax_error.lineno - 1 if syntax_error.lineno else 0
        
        blocks = []
        
        # Partie avant l'erreur
        if error_line > 0:
            valid_content = '\n'.join(lines[:error_line])
            if valid_content.strip():
                try:
                    # Tentative de parsing de la partie valide
                    valid_tree = self.parse_content(valid_content, "partial")
                    valid_location = self.location_tracker.create_location_from_lines(
                        content, 1, error_line
                    )
                    
                    valid_block = PartitionBlock(
                        content=valid_content,
                        block_type=BlockType.MIXED,
                        location=valid_location,
                        partition_method=PartitionMethod.AST,
                        block_name="valid_part",
                        token_count=self._count_tokens(valid_content)
                    )
                    blocks.append(valid_block)
                    
                except:
                    # Si même la partie valide échoue, crée un bloc textuel
                    pass
        
        # Partie avec erreur
        if error_line < len(lines):
            invalid_content = '\n'.join(lines[error_line:])
            if invalid_content.strip():
                invalid_location = self.location_tracker.create_location_from_lines(
                    content, error_line + 1, len(lines)
                )
                
                invalid_block = PartitionBlock(
                    content=invalid_content,
                    block_type=BlockType.UNKNOWN,
                    location=invalid_location,
                    partition_method=PartitionMethod.AST,
                    block_name="syntax_error_part",
                    token_count=self._count_tokens(invalid_content)
                )
                invalid_block.add_error("syntax_error", str(syntax_error))
                blocks.append(invalid_block)
        
        return blocks
    
    def _init_token_counter(self):
        """Initialise le compteur de tokens."""
        try:
            import tiktoken
            return tiktoken.get_encoding("cl100k_base")
        except ImportError:
            # Fallback simple
            return None
    
    def _count_tokens(self, text: str) -> int:
        """Compte les tokens dans un texte."""
        if self.token_counter:
            return len(self.token_counter.encode(text))
        else:
            # Estimation approximative
            return len(text.split()) * 1.3
    
    def _calculate_complexity(self, node: ast.AST) -> float:
        """Calcule un score de complexité pour un nœud."""
        # Complexité cyclomatique simplifiée
        complexity = 1.0
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 0.5
        
        return complexity
    
    def _detect_file_type(self, file_path: str) -> str:
        """Détecte le type de fichier."""
        if file_path.endswith('.py'):
            return 'python'
        elif file_path.endswith('.js'):
            return 'javascript'
        elif file_path.endswith('.ts'):
            return 'typescript'
        else:
            return 'unknown'
    
    def _validate_partitions(self, partitions: List[PartitionBlock], 
                           content: str) -> bool:
        """Valide la cohérence des partitions."""
        if not partitions:
            return False
        
        # Vérification basique de non-chevauchement
        for i, partition in enumerate(partitions):
            for j, other in enumerate(partitions[i+1:], i+1):
                if partition.location.overlaps_with(other.location):
                    log_partitioning_warning(
                        "partition_overlap",
                        f"Partitions {i} and {j} overlap",
                        "validation"
                    )
                    return False
        
        return True
    
    def _add_overlap_context(self, partitions: List[PartitionBlock], content: str):
        """Ajoute du contexte d'overlap aux partitions."""
        lines = content.split('\n')
        
        for i, partition in enumerate(partitions):
            # Contexte précédent
            if i > 0:
                prev_partition = partitions[i-1]
                context_start = max(0, prev_partition.location.end_line - self.overlap_lines)
                context_lines = lines[context_start:prev_partition.location.end_line]
                partition.prev_context = '\n'.join(context_lines)
            
            # Contexte suivant
            if i < len(partitions) - 1:
                next_partition = partitions[i+1]
                context_end = min(len(lines), next_partition.location.start_line + self.overlap_lines)
                context_lines = lines[next_partition.location.start_line-1:context_end]
                partition.next_context = '\n'.join(context_lines)
    
    def _create_chunk_location(self, content: str, parent_location: PartitionLocation,
                              chunk_lines: List[str], all_lines: List[str]) -> PartitionLocation:
        """Crée une location pour un chunk de lignes."""
        # Calcul approximatif - à améliorer si nécessaire
        chunk_start_line = parent_location.start_line
        chunk_end_line = chunk_start_line + len(chunk_lines) - 1
        
        return self.location_tracker.create_location_from_lines(
            content, chunk_start_line, chunk_end_line
        )
