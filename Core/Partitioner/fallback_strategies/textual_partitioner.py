"""
📝 Partitionneur Textuel - Fallback Niveau 3

Partitionnement par analyse textuelle quand regex et AST échouent.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from ..schemas.partition_schemas import (
    PartitionBlock, PartitionLocation, PartitionResult,
    PartitionMethod, BlockType
)
from ..trackers.location_tracker import LocationTracker
from ..handlers.error_logger import log_partitioning_warning


class TextualPartitioner:
    """Partitionneur utilisant l'analyse textuelle."""
    
    def __init__(self, max_tokens: int = 3500, overlap_lines: int = 5):
        self.max_tokens = max_tokens
        self.overlap_lines = overlap_lines
        self.location_tracker = LocationTracker()
    
    def partition(self, file_path: str, content: str) -> PartitionResult:
        """Partitionne le contenu en utilisant une approche textuelle simple."""
        
        start_time = time.time()
        result = PartitionResult(
            file_path=file_path,
            file_type="text",
            total_lines=len(content.split('\n')),
            total_chars=len(content),
            partitions=[],
            strategy_used=PartitionMethod.TEXTUAL,
            success=False
        )
        
        try:
            # Initialisation du tracker
            self.location_tracker.analyze_file_structure(content)
            
            # Analyse textuelle pour détecter des sections
            sections = self._detect_textual_sections(content)
            
            # Si des sections sont détectées, les utilise
            if sections:
                for section in sections:
                    partition = self._create_section_partition(content, section)
                    result.partitions.append(partition)
            else:
                # Fallback vers chunking intelligent
                chunks = self._create_intelligent_chunks(content)
                result.partitions.extend(chunks)
            
            # Validation et finalisation
            if result.partitions:
                result.success = True
                self._add_overlap_context(result.partitions, content)
            
        except Exception as e:
            result.add_error("textual_partitioning_error", str(e))
            log_partitioning_warning(
                "textual_partitioning_failed",
                f"Textual partitioning failed: {e}",
                file_path
            )
        
        result.processing_time = time.time() - start_time
        return result
    
    def _detect_textual_sections(self, content: str) -> List[Dict[str, Any]]:
        """Détecte des sections par analyse textuelle."""
        
        lines = content.split('\n')
        sections = []
        
        # Stratégies de détection
        strategies = [
            self._detect_by_empty_lines,
            self._detect_by_indentation_changes,
            self._detect_by_comment_blocks,
            self._detect_by_line_patterns
        ]
        
        for strategy in strategies:
            detected_sections = strategy(lines)
            if detected_sections and len(detected_sections) > 1:
                # Utilise la première stratégie qui trouve des sections
                return detected_sections
        
        return []
    
    def _detect_by_empty_lines(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Détecte des sections séparées par des lignes vides."""
        
        sections = []
        current_start = 1
        
        for i, line in enumerate(lines):
            # Ligne vide trouvée
            if not line.strip():
                # Vérifie s'il y a plusieurs lignes vides consécutives
                empty_count = 1
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    empty_count += 1
                    j += 1
                
                # Si 2+ lignes vides, considère comme séparateur de section
                if empty_count >= 2 and i + 1 > current_start:
                    sections.append({
                        'type': 'section',
                        'start_line': current_start,
                        'end_line': i,
                        'detection_method': 'empty_lines'
                    })
                    current_start = j + 1
        
        # Dernière section
        if current_start <= len(lines):
            sections.append({
                'type': 'section',
                'start_line': current_start,
                'end_line': len(lines),
                'detection_method': 'empty_lines'
            })
        
        return sections if len(sections) > 1 else []
    
    def _detect_by_indentation_changes(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Détecte des sections par changements d'indentation."""
        
        sections = []
        current_start = 1
        base_indent = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            
            # Calcul de l'indentation
            indent = len(line) - len(line.lstrip())
            
            # Première ligne non-vide
            if base_indent is None:
                base_indent = indent
                continue
            
            # Changement significatif d'indentation (retour au niveau de base)
            if indent == base_indent and i > current_start + 5:  # Au moins 5 lignes
                sections.append({
                    'type': 'indented_section',
                    'start_line': current_start,
                    'end_line': i,
                    'detection_method': 'indentation'
                })
                current_start = i + 1
        
        # Dernière section
        if current_start <= len(lines):
            sections.append({
                'type': 'indented_section',
                'start_line': current_start,
                'end_line': len(lines),
                'detection_method': 'indentation'
            })
        
        return sections if len(sections) > 1 else []
    
    def _detect_by_comment_blocks(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Détecte des sections séparées par des blocs de commentaires."""
        
        sections = []
        current_start = 1
        
        # Patterns de commentaires par langage
        comment_patterns = [
            r'^\s*#',      # Python, Shell
            r'^\s*//',     # JavaScript, C++, Java
            r'^\s*/\*',    # CSS, C, Java (début)
            r'^\s*\*',     # Continuation de commentaire
            r'^\s*<!--',   # HTML, XML
        ]
        
        for i, line in enumerate(lines):
            # Vérifie si c'est un commentaire
            is_comment = any(
                __import__('re').match(pattern, line) 
                for pattern in comment_patterns
            )
            
            # Ligne de commentaire qui semble être un séparateur
            if is_comment and len(line.strip()) > 20:  # Commentaire long
                # Vérifie si c'est un séparateur (caractères répétés)
                stripped = line.strip().lstrip('#/').lstrip('*').strip()
                if len(set(stripped)) <= 3 and len(stripped) > 10:  # Caractères répétés
                    if i > current_start + 3:  # Au moins quelques lignes
                        sections.append({
                            'type': 'comment_section',
                            'start_line': current_start,
                            'end_line': i,
                            'detection_method': 'comment_blocks'
                        })
                        current_start = i + 1
        
        # Dernière section
        if current_start <= len(lines):
            sections.append({
                'type': 'comment_section',
                'start_line': current_start,
                'end_line': len(lines),
                'detection_method': 'comment_blocks'
            })
        
        return sections if len(sections) > 1 else []
    
    def _detect_by_line_patterns(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Détecte des sections par patterns de lignes."""
        
        sections = []
        current_start = 1
        
        # Patterns qui suggèrent le début d'une nouvelle section
        section_start_patterns = [
            r'^\s*[A-Z][A-Z\s]+:',  # Titres en majuscules
            r'^\s*\d+\.',           # Listes numérotées
            r'^\s*[a-zA-Z]+\s*\(',  # Appels de fonction
            r'^\s*\w+\s*=',         # Assignations
        ]
        
        for i, line in enumerate(lines):
            # Vérifie si la ligne correspond à un début de section
            is_section_start = any(
                __import__('re').match(pattern, line)
                for pattern in section_start_patterns
            )
            
            if is_section_start and i > current_start + 10:  # Au moins 10 lignes
                sections.append({
                    'type': 'pattern_section',
                    'start_line': current_start,
                    'end_line': i,
                    'detection_method': 'line_patterns'
                })
                current_start = i + 1
        
        # Dernière section
        if current_start <= len(lines):
            sections.append({
                'type': 'pattern_section',
                'start_line': current_start,
                'end_line': len(lines),
                'detection_method': 'line_patterns'
            })
        
        return sections if len(sections) > 1 else []
    
    def _create_intelligent_chunks(self, content: str) -> List[PartitionBlock]:
        """Crée des chunks intelligents basés sur l'analyse textuelle."""
        
        lines = content.split('\n')
        chunks = []
        
        # Paramètres adaptatifs
        base_chunk_size = min(50, max(10, len(lines) // 10))  # Adapté à la taille
        
        i = 0
        while i < len(lines):
            # Détermine la taille du chunk
            chunk_end = min(i + base_chunk_size, len(lines))
            
            # Ajustement intelligent de la fin du chunk
            chunk_end = self._find_intelligent_break(lines, i, chunk_end)
            
            # Création du chunk
            location = self.location_tracker.create_location_from_lines(
                content, i + 1, chunk_end
            )
            
            chunk_content = location.extract_content(content)
            
            chunk = PartitionBlock(
                content=chunk_content,
                block_type=BlockType.CHUNK,
                location=location,
                partition_method=PartitionMethod.TEXTUAL,
                block_name=f"textual_chunk_{len(chunks)}",
                token_count=self._estimate_tokens(chunk_content),
                complexity_score=self._calculate_text_complexity(chunk_content),
                metadata={
                    'chunk_strategy': 'intelligent',
                    'lines_count': chunk_end - i
                }
            )
            chunks.append(chunk)
            
            i = chunk_end
        
        return chunks
    
    def _find_intelligent_break(self, lines: List[str], start: int, proposed_end: int) -> int:
        """Trouve un point de coupure intelligent pour un chunk."""
        
        if proposed_end >= len(lines):
            return len(lines)
        
        # Cherche un bon point de coupure dans les dernières lignes
        search_range = min(10, proposed_end - start)
        
        for offset in range(search_range):
            check_line = proposed_end - offset - 1
            if check_line <= start:
                break
            
            line = lines[check_line].strip()
            
            # Ligne vide - bon point de coupure
            if not line:
                return check_line + 1
            
            # Ligne qui semble terminer quelque chose
            if (line.endswith((':','}', ';', '.')) or
                line.startswith(('return', 'break', 'continue', 'pass'))):
                return check_line + 1
        
        return proposed_end
    
    def _create_section_partition(self, content: str, section: Dict[str, Any]) -> PartitionBlock:
        """Crée une partition à partir d'une section détectée."""
        
        location = self.location_tracker.create_location_from_lines(
            content, section['start_line'], section['end_line']
        )
        
        section_content = location.extract_content(content)
        
        return PartitionBlock(
            content=section_content,
            block_type=BlockType.SECTION,
            location=location,
            partition_method=PartitionMethod.TEXTUAL,
            block_name=f"{section['type']}_{section['start_line']}",
            token_count=self._estimate_tokens(section_content),
            complexity_score=self._calculate_text_complexity(section_content),
            metadata={
                'detection_method': section['detection_method'],
                'section_type': section['type']
            }
        )
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimation du nombre de tokens."""
        # Estimation plus précise pour texte
        words = text.split()
        # Compte les mots + ponctuation + caractères spéciaux
        tokens = len(words)
        tokens += text.count('.') + text.count(',') + text.count(';')
        tokens += text.count('(') + text.count(')') + text.count('{') + text.count('}')
        return int(tokens * 1.2)
    
    def _calculate_text_complexity(self, text: str) -> float:
        """Calcule un score de complexité textuelle."""
        
        if not text.strip():
            return 0.0
        
        lines = text.split('\n')
        complexity = 1.0
        
        # Facteurs de complexité
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Longueur moyenne des lignes
        if non_empty_lines:
            avg_line_length = sum(len(line) for line in non_empty_lines) / len(non_empty_lines)
            complexity += avg_line_length / 100  # Normalisation
        
        # Variété de caractères
        unique_chars = len(set(text.lower()))
        complexity += unique_chars / 50  # Normalisation
        
        # Niveaux d'indentation
        indents = set()
        for line in non_empty_lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indents.add(indent)
        complexity += len(indents) * 0.5
        
        # Caractères spéciaux (suggèrent du code)
        special_chars = sum(1 for char in text if char in '{}()[]<>=+-*/%&|!@#$^~`')
        complexity += special_chars / len(text) * 10 if text else 0
        
        return min(complexity, 10.0)  # Cap à 10
    
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
