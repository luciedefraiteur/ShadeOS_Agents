"""
🔍 Partitionneur Regex - Fallback Niveau 2

Partitionnement par expressions régulières quand l'AST échoue.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import re
import time
from typing import List, Dict, Any, Optional, Pattern
from ..partition_schemas import (
    PartitionBlock, PartitionLocation, PartitionResult,
    PartitionMethod, BlockType
)
from ..location_tracker import LocationTracker
from ..error_logger import log_partitioning_warning


class RegexPartitioner:
    """Partitionneur utilisant des expressions régulières."""
    
    # Patterns regex par langage
    LANGUAGE_PATTERNS = {
        'python': {
            'class': [
                r'^class\s+(\w+).*?:',
                r'^@\w+.*?\nclass\s+(\w+).*?:'  # Avec décorateurs
            ],
            'function': [
                r'^def\s+(\w+)\s*\(',
                r'^async\s+def\s+(\w+)\s*\(',
                r'^@\w+.*?\ndef\s+(\w+)\s*\('  # Avec décorateurs
            ],
            'import': [
                r'^import\s+(\w+(?:\.\w+)*)',
                r'^from\s+(\w+(?:\.\w+)*)\s+import'
            ],
            'variable': [
                r'^(\w+)\s*=',
                r'^(\w+)\s*:\s*\w+\s*='  # Type hints
            ]
        },
        'javascript': {
            'class': [
                r'class\s+(\w+)',
                r'export\s+class\s+(\w+)'
            ],
            'function': [
                r'function\s+(\w+)\s*\(',
                r'(\w+)\s*:\s*function\s*\(',
                r'(\w+)\s*=\s*function\s*\(',
                r'(\w+)\s*=\s*\([^)]*\)\s*=>'  # Arrow functions
            ],
            'import': [
                r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]',
                r'import\s+[\'"]([^\'"]+)[\'"]',
                r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
            ],
            'variable': [
                r'(?:var|let|const)\s+(\w+)',
                r'(\w+)\s*:'  # Object properties
            ]
        },
        'typescript': {
            'class': [
                r'class\s+(\w+)',
                r'export\s+class\s+(\w+)',
                r'abstract\s+class\s+(\w+)'
            ],
            'function': [
                r'function\s+(\w+)\s*\(',
                r'(\w+)\s*\([^)]*\)\s*:\s*\w+',  # Type annotations
                r'(\w+)\s*=\s*\([^)]*\)\s*=>'
            ],
            'import': [
                r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]',
                r'import\s+type\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
            ],
            'variable': [
                r'(?:var|let|const)\s+(\w+)',
                r'(\w+)\s*:\s*\w+'  # Type annotations
            ]
        },
        'rust': {
            'class': [
                r'struct\s+(\w+)',
                r'enum\s+(\w+)',
                r'trait\s+(\w+)',
                r'impl\s+(?:\w+\s+for\s+)?(\w+)'
            ],
            'function': [
                r'fn\s+(\w+)\s*\(',
                r'pub\s+fn\s+(\w+)\s*\(',
                r'async\s+fn\s+(\w+)\s*\('
            ],
            'import': [
                r'use\s+([^;]+);',
                r'extern\s+crate\s+(\w+)'
            ],
            'variable': [
                r'let\s+(?:mut\s+)?(\w+)',
                r'const\s+(\w+)',
                r'static\s+(\w+)'
            ]
        },
        'go': {
            'class': [
                r'type\s+(\w+)\s+struct',
                r'type\s+(\w+)\s+interface'
            ],
            'function': [
                r'func\s+(\w+)\s*\(',
                r'func\s+\([^)]+\)\s+(\w+)\s*\('  # Methods
            ],
            'import': [
                r'import\s+"([^"]+)"',
                r'import\s+(\w+)\s+"[^"]+"'
            ],
            'variable': [
                r'var\s+(\w+)',
                r'(\w+)\s*:='
            ]
        }
    }
    
    def __init__(self, max_tokens: int = 3500, overlap_lines: int = 5):
        self.max_tokens = max_tokens
        self.overlap_lines = overlap_lines
        self.location_tracker = LocationTracker()
        self.compiled_patterns: Dict[str, Dict[str, List[Pattern]]] = {}
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile les patterns regex pour performance."""
        for language, categories in self.LANGUAGE_PATTERNS.items():
            self.compiled_patterns[language] = {}
            for category, patterns in categories.items():
                self.compiled_patterns[language][category] = [
                    re.compile(pattern, re.MULTILINE) for pattern in patterns
                ]
    
    def partition(self, content: str, file_path: str, language: str) -> PartitionResult:
        """Partitionne le contenu avec des regex."""
        
        start_time = time.time()
        result = PartitionResult(
            file_path=file_path,
            file_type=language,
            total_lines=len(content.split('\n')),
            total_chars=len(content),
            partitions=[],
            strategy_used=PartitionMethod.REGEX,
            success=False
        )
        
        try:
            # Initialisation du tracker
            self.location_tracker.analyze_file_structure(content)
            
            # Détection des blocs par regex
            blocks = self._detect_blocks_by_regex(content, language)
            
            # Création des partitions
            for block_info in blocks:
                try:
                    partition = self._create_partition_from_block(content, block_info)
                    result.partitions.append(partition)
                except Exception as e:
                    log_partitioning_warning(
                        "regex_partition_creation_warning",
                        f"Failed to create partition from block: {e}",
                        file_path
                    )
                    continue
            
            # Si pas assez de blocs détectés, fallback textuel
            if len(result.partitions) < 2:
                result.partitions.extend(
                    self._fallback_textual_chunks(content, file_path)
                )
            
            # Validation et finalisation
            if result.partitions:
                result.success = True
                self._add_overlap_context(result.partitions, content)
            
        except Exception as e:
            result.add_error("regex_partitioning_error", str(e))
            log_partitioning_warning(
                "regex_partitioning_failed",
                f"Regex partitioning failed: {e}",
                file_path
            )
        
        result.processing_time = time.time() - start_time
        return result
    
    def _detect_blocks_by_regex(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Détecte les blocs de code par regex."""
        
        blocks = []
        lines = content.split('\n')
        
        # Patterns pour ce langage
        patterns = self.compiled_patterns.get(language.lower(), {})
        
        for line_num, line in enumerate(lines, 1):
            for block_type, type_patterns in patterns.items():
                for pattern in type_patterns:
                    match = pattern.search(line)
                    if match:
                        # Trouve la fin du bloc
                        end_line = self._find_block_end(
                            lines, line_num - 1, block_type, language
                        )
                        
                        block_info = {
                            'type': block_type,
                            'name': match.group(1) if match.groups() else None,
                            'start_line': line_num,
                            'end_line': end_line,
                            'pattern_matched': pattern.pattern
                        }
                        blocks.append(block_info)
                        break  # Évite les matches multiples sur la même ligne
        
        # Tri par ligne de début
        blocks.sort(key=lambda x: x['start_line'])
        
        # Résolution des chevauchements
        blocks = self._resolve_overlaps(blocks)
        
        return blocks
    
    def _find_block_end(self, lines: List[str], start_idx: int, 
                       block_type: str, language: str) -> int:
        """Trouve la fin d'un bloc selon le langage et le type."""
        
        if language.lower() == 'python':
            return self._find_python_block_end(lines, start_idx, block_type)
        elif language.lower() in ['javascript', 'typescript']:
            return self._find_js_block_end(lines, start_idx)
        elif language.lower() == 'rust':
            return self._find_rust_block_end(lines, start_idx)
        elif language.lower() == 'go':
            return self._find_go_block_end(lines, start_idx)
        else:
            # Fallback générique
            return self._find_generic_block_end(lines, start_idx)
    
    def _find_python_block_end(self, lines: List[str], start_idx: int, 
                              block_type: str) -> int:
        """Trouve la fin d'un bloc Python par indentation."""
        
        if start_idx >= len(lines):
            return len(lines)
        
        start_line = lines[start_idx].rstrip()
        if not start_line.endswith(':'):
            # Pas un bloc Python standard
            return start_idx + 1
        
        # Calcul de l'indentation de base
        base_indent = len(start_line) - len(start_line.lstrip())
        
        # Cherche la fin du bloc indenté
        for i in range(start_idx + 1, len(lines)):
            line = lines[i].rstrip()
            
            # Ligne vide, continue
            if not line:
                continue
            
            # Calcul de l'indentation
            line_indent = len(line) - len(line.lstrip())
            
            # Si indentation <= base, fin du bloc
            if line_indent <= base_indent:
                return i
        
        return len(lines)
    
    def _find_js_block_end(self, lines: List[str], start_idx: int) -> int:
        """Trouve la fin d'un bloc JavaScript/TypeScript par accolades."""
        
        brace_count = 0
        found_opening = False
        
        for i in range(start_idx, len(lines)):
            line = lines[i]
            
            for char in line:
                if char == '{':
                    brace_count += 1
                    found_opening = True
                elif char == '}':
                    brace_count -= 1
                    
                    # Fin du bloc trouvée
                    if found_opening and brace_count == 0:
                        return i + 1
        
        # Si pas de fermeture trouvée, prend quelques lignes
        return min(start_idx + 10, len(lines))
    
    def _find_rust_block_end(self, lines: List[str], start_idx: int) -> int:
        """Trouve la fin d'un bloc Rust par accolades."""
        return self._find_js_block_end(lines, start_idx)  # Même logique
    
    def _find_go_block_end(self, lines: List[str], start_idx: int) -> int:
        """Trouve la fin d'un bloc Go par accolades."""
        return self._find_js_block_end(lines, start_idx)  # Même logique
    
    def _find_generic_block_end(self, lines: List[str], start_idx: int) -> int:
        """Fallback générique pour trouver la fin d'un bloc."""
        
        # Cherche la prochaine ligne vide ou début d'un autre bloc
        for i in range(start_idx + 1, len(lines)):
            line = lines[i].strip()
            
            # Ligne vide, possible fin de bloc
            if not line:
                # Vérifie si la ligne suivante commence un nouveau bloc
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith(' '):
                        return i
            
            # Ligne qui semble commencer un nouveau bloc
            elif (line.startswith(('def ', 'class ', 'function ', 'var ', 'let ', 'const ')) or
                  'function' in line or 'class' in line):
                return i
        
        # Prend au maximum 20 lignes
        return min(start_idx + 20, len(lines))
    
    def _resolve_overlaps(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Résout les chevauchements entre blocs."""
        
        if len(blocks) <= 1:
            return blocks
        
        resolved = []
        current_block = blocks[0]
        
        for next_block in blocks[1:]:
            # Si chevauchement
            if current_block['end_line'] > next_block['start_line']:
                # Ajuste la fin du bloc actuel
                current_block['end_line'] = next_block['start_line'] - 1
            
            resolved.append(current_block)
            current_block = next_block
        
        resolved.append(current_block)
        return resolved
    
    def _create_partition_from_block(self, content: str, 
                                   block_info: Dict[str, Any]) -> PartitionBlock:
        """Crée une partition à partir d'un bloc détecté."""
        
        # Création de la location
        location = self.location_tracker.create_location_from_lines(
            content, 
            block_info['start_line'], 
            block_info['end_line']
        )
        
        # Extraction du contenu
        block_content = location.extract_content(content)
        
        # Détermination du type
        block_type = self._map_block_type(block_info['type'])
        
        return PartitionBlock(
            content=block_content,
            block_type=block_type,
            location=location,
            partition_method=PartitionMethod.REGEX,
            block_name=block_info['name'],
            token_count=self._estimate_tokens(block_content),
            metadata={
                'pattern_matched': block_info['pattern_matched'],
                'detection_method': 'regex'
            }
        )
    
    def _map_block_type(self, regex_type: str) -> BlockType:
        """Mappe un type regex vers un BlockType."""
        
        mapping = {
            'class': BlockType.CLASS,
            'function': BlockType.FUNCTION,
            'import': BlockType.IMPORT,
            'variable': BlockType.VARIABLE
        }
        
        return mapping.get(regex_type, BlockType.UNKNOWN)
    
    def _fallback_textual_chunks(self, content: str, file_path: str) -> List[PartitionBlock]:
        """Fallback vers des chunks textuels si pas assez de blocs détectés."""
        
        lines = content.split('\n')
        chunks = []
        chunk_size = 50  # Lignes par chunk
        
        for i in range(0, len(lines), chunk_size):
            end_line = min(i + chunk_size, len(lines))
            
            location = self.location_tracker.create_location_from_lines(
                content, i + 1, end_line
            )
            
            chunk_content = location.extract_content(content)
            
            chunk = PartitionBlock(
                content=chunk_content,
                block_type=BlockType.CHUNK,
                location=location,
                partition_method=PartitionMethod.REGEX,
                block_name=f"chunk_{len(chunks)}",
                token_count=self._estimate_tokens(chunk_content),
                metadata={'fallback_reason': 'insufficient_regex_blocks'}
            )
            chunks.append(chunk)
        
        return chunks
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimation approximative du nombre de tokens."""
        return int(len(text.split()) * 1.3)
    
    def _add_overlap_context(self, partitions: List[PartitionBlock], content: str):
        """Ajoute du contexte d'overlap aux partitions."""
        
        lines = content.split('\n')
        
        for i, partition in enumerate(partitions):
            # Contexte précédent
            if i > 0:
                prev_end = partitions[i-1].location.end_line
                context_start = max(1, prev_end - self.overlap_lines)
                context_lines = lines[context_start-1:prev_end]
                partition.prev_context = '\n'.join(context_lines)
            
            # Contexte suivant
            if i < len(partitions) - 1:
                next_start = partitions[i+1].location.start_line
                context_end = min(len(lines), next_start + self.overlap_lines)
                context_lines = lines[next_start-1:context_end]
                partition.next_context = '\n'.join(context_lines)
