"""
🚨 Partitionneur d'Urgence - Fallback Ultime

Partitionnement de dernier recours qui ne peut jamais échouer.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import time
import math
from typing import List, Dict, Any
from ..schemas.partition_schemas import (
    PartitionBlock, PartitionLocation, PartitionResult,
    PartitionMethod, BlockType
)
from ..trackers.location_tracker import LocationTracker


class EmergencyPartitioner:
    """Partitionneur d'urgence qui ne peut jamais échouer."""
    
    def __init__(self, max_tokens: int = 3500, overlap_lines: int = 3):
        self.max_tokens = max_tokens
        self.overlap_lines = overlap_lines
        self.location_tracker = LocationTracker()
    
    def partition(self, file_path: str, content: str) -> PartitionResult:
        """Partitionne le contenu en utilisant une stratégie d'urgence."""
        
        start_time = time.time()
        result = PartitionResult(
            file_path=file_path,
            file_type="unknown",
            total_lines=len(content.split('\n')),
            total_chars=len(content),
            partitions=[],
            strategy_used=PartitionMethod.EMERGENCY,
            success=False
        )
        
        try:
            # Initialisation du tracker
            self.location_tracker.analyze_file_structure(content)
            
            # Stratégie d'urgence selon la taille
            if len(content) == 0:
                # Fichier vide
                result.partitions = self._handle_empty_file(content)
            elif len(content) < 100:
                # Très petit fichier
                result.partitions = self._handle_tiny_file(content)
            elif len(content) < 10000:
                # Fichier normal
                result.partitions = self._create_fixed_chunks(content)
            else:
                # Gros fichier
                result.partitions = self._create_adaptive_chunks(content)
            
            # Ajout du contexte d'overlap
            if len(result.partitions) > 1:
                self._add_overlap_context(result.partitions, content)
            
            # Validation finale
            if not result.partitions:
                # Cas extrême : crée au moins un chunk
                result.partitions = [self._create_single_chunk(content)]
        
        except Exception as e:
            # Même en cas d'erreur, crée un chunk minimal
            result.partitions = [self._create_emergency_chunk(content, str(e))]
            result.add_warning(f"Emergency partitioning with error: {e}")
        
        result.processing_time = time.time() - start_time
        return result
    
    def _handle_empty_file(self, content: str) -> List[PartitionBlock]:
        """Gère les fichiers vides."""
        
        location = PartitionLocation(
            start_line=1, end_line=1, start_char=0, end_char=0,
            start_offset=0, end_offset=0, total_lines=1, total_chars=0,
            line_lengths=[0]
        )
        
        return [PartitionBlock(
            content="",
            block_type=BlockType.UNKNOWN,
            location=location,
            partition_method=PartitionMethod.EMERGENCY,
            block_name="empty_file",
            token_count=0,
            metadata={'emergency_reason': 'empty_file'}
        )]
    
    def _handle_tiny_file(self, content: str) -> List[PartitionBlock]:
        """Gère les très petits fichiers."""
        
        lines = content.split('\n')
        location = self.location_tracker.create_location_from_lines(
            content, 1, len(lines)
        )
        
        return [PartitionBlock(
            content=content,
            block_type=BlockType.UNKNOWN,
            location=location,
            partition_method=PartitionMethod.EMERGENCY,
            block_name="tiny_file",
            token_count=self._safe_token_count(content),
            metadata={'emergency_reason': 'tiny_file', 'size': len(content)}
        )]
    
    def _create_fixed_chunks(self, content: str) -> List[PartitionBlock]:
        """Crée des chunks de taille fixe pour fichiers normaux."""
        
        lines = content.split('\n')
        chunks = []
        
        # Taille de chunk adaptée
        chunk_size = self._calculate_optimal_chunk_size(len(lines))
        
        for i in range(0, len(lines), chunk_size):
            end_line = min(i + chunk_size, len(lines))
            
            try:
                location = self.location_tracker.create_location_from_lines(
                    content, i + 1, end_line
                )
                chunk_content = location.extract_content(content)
            except Exception:
                # Fallback si location tracker échoue
                chunk_lines = lines[i:end_line]
                chunk_content = '\n'.join(chunk_lines)
                location = self._create_emergency_location(content, i + 1, end_line)
            
            chunk = PartitionBlock(
                content=chunk_content,
                block_type=BlockType.CHUNK,
                location=location,
                partition_method=PartitionMethod.EMERGENCY,
                block_name=f"emergency_chunk_{len(chunks)}",
                token_count=self._safe_token_count(chunk_content),
                metadata={
                    'emergency_reason': 'fixed_chunks',
                    'chunk_index': len(chunks),
                    'chunk_size': chunk_size
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_adaptive_chunks(self, content: str) -> List[PartitionBlock]:
        """Crée des chunks adaptatifs pour gros fichiers."""
        
        lines = content.split('\n')
        chunks = []
        
        # Pour gros fichiers, chunks plus gros
        base_chunk_size = max(100, len(lines) // 20)  # Max 20 chunks
        
        i = 0
        while i < len(lines):
            # Taille adaptative selon le contenu
            chunk_size = self._adaptive_chunk_size(lines, i, base_chunk_size)
            end_line = min(i + chunk_size, len(lines))
            
            try:
                location = self.location_tracker.create_location_from_lines(
                    content, i + 1, end_line
                )
                chunk_content = location.extract_content(content)
            except Exception:
                # Fallback robuste
                chunk_lines = lines[i:end_line]
                chunk_content = '\n'.join(chunk_lines)
                location = self._create_emergency_location(content, i + 1, end_line)
            
            chunk = PartitionBlock(
                content=chunk_content,
                block_type=BlockType.CHUNK,
                location=location,
                partition_method=PartitionMethod.EMERGENCY,
                block_name=f"adaptive_chunk_{len(chunks)}",
                token_count=self._safe_token_count(chunk_content),
                metadata={
                    'emergency_reason': 'adaptive_chunks',
                    'chunk_index': len(chunks),
                    'adaptive_size': chunk_size
                }
            )
            chunks.append(chunk)
            
            i = end_line
        
        return chunks
    
    def _calculate_optimal_chunk_size(self, total_lines: int) -> int:
        """Calcule la taille optimale de chunk."""
        
        if total_lines <= 50:
            return total_lines  # Un seul chunk
        elif total_lines <= 200:
            return 50
        elif total_lines <= 1000:
            return 100
        else:
            return 150
    
    def _adaptive_chunk_size(self, lines: List[str], start_idx: int, base_size: int) -> int:
        """Calcule une taille de chunk adaptative."""
        
        # Analyse de la densité du contenu
        sample_size = min(20, len(lines) - start_idx)
        if sample_size <= 0:
            return base_size
        
        sample_lines = lines[start_idx:start_idx + sample_size]
        
        # Calcul de la densité (caractères non-blancs par ligne)
        total_chars = sum(len(line.strip()) for line in sample_lines)
        avg_density = total_chars / sample_size if sample_size > 0 else 0
        
        # Ajustement selon la densité
        if avg_density > 80:  # Lignes très denses
            return int(base_size * 0.7)
        elif avg_density < 20:  # Lignes peu denses
            return int(base_size * 1.3)
        else:
            return base_size
    
    def _create_single_chunk(self, content: str) -> PartitionBlock:
        """Crée un chunk unique pour tout le fichier."""
        
        lines = content.split('\n')
        
        try:
            location = self.location_tracker.create_location_from_lines(
                content, 1, len(lines)
            )
        except Exception:
            location = self._create_emergency_location(content, 1, len(lines))
        
        return PartitionBlock(
            content=content,
            block_type=BlockType.MIXED,
            location=location,
            partition_method=PartitionMethod.EMERGENCY,
            block_name="single_emergency_chunk",
            token_count=self._safe_token_count(content),
            metadata={'emergency_reason': 'single_chunk_fallback'}
        )
    
    def _create_emergency_chunk(self, content: str, error_msg: str) -> PartitionBlock:
        """Crée un chunk d'urgence en cas d'erreur critique."""
        
        # Location minimale d'urgence
        lines = content.split('\n') if content else ['']
        location = PartitionLocation(
            start_line=1,
            end_line=len(lines),
            start_char=0,
            end_char=len(lines[-1]) if lines else 0,
            start_offset=0,
            end_offset=len(content),
            total_lines=len(lines),
            total_chars=len(content),
            line_lengths=[len(line) for line in lines]
        )
        
        return PartitionBlock(
            content=content,
            block_type=BlockType.UNKNOWN,
            location=location,
            partition_method=PartitionMethod.EMERGENCY,
            block_name="critical_emergency_chunk",
            token_count=self._safe_token_count(content),
            metadata={
                'emergency_reason': 'critical_error',
                'error_message': error_msg
            }
        )
    
    def _create_emergency_location(self, content: str, start_line: int, 
                                  end_line: int) -> PartitionLocation:
        """Crée une location d'urgence sans dépendances."""
        
        lines = content.split('\n')
        
        # Calculs sécurisés
        safe_start = max(1, min(start_line, len(lines)))
        safe_end = max(safe_start, min(end_line, len(lines)))
        
        # Calcul approximatif des offsets
        start_offset = 0
        for i in range(safe_start - 1):
            if i < len(lines):
                start_offset += len(lines[i]) + 1  # +1 pour \n
        
        end_offset = start_offset
        for i in range(safe_start - 1, safe_end):
            if i < len(lines):
                end_offset += len(lines[i]) + 1
        
        # Ajustements finaux
        end_offset = min(end_offset, len(content))
        
        return PartitionLocation(
            start_line=safe_start,
            end_line=safe_end,
            start_char=0,
            end_char=len(lines[safe_end - 1]) if safe_end <= len(lines) else 0,
            start_offset=start_offset,
            end_offset=end_offset,
            total_lines=len(lines),
            total_chars=len(content),
            line_lengths=[len(line) for line in lines]
        )
    
    def _safe_token_count(self, text: str) -> int:
        """Compte les tokens de manière sécurisée."""
        
        try:
            if not text:
                return 0
            
            # Estimation simple et robuste
            words = text.split()
            return max(1, int(len(words) * 1.2))
        
        except Exception:
            # Fallback ultime
            return max(1, len(text) // 4)
    
    def _add_overlap_context(self, partitions: List[PartitionBlock], content: str):
        """Ajoute du contexte d'overlap de manière sécurisée."""
        
        try:
            lines = content.split('\n')
            
            for i, partition in enumerate(partitions):
                # Contexte précédent
                if i > 0:
                    try:
                        prev_end = partitions[i-1].location.end_line
                        context_start = max(1, prev_end - self.overlap_lines)
                        context_lines = lines[context_start-1:prev_end]
                        partition.prev_context = '\n'.join(context_lines)
                    except Exception:
                        partition.prev_context = ""
                
                # Contexte suivant
                if i < len(partitions) - 1:
                    try:
                        next_start = partitions[i+1].location.start_line
                        context_end = min(len(lines), next_start + self.overlap_lines)
                        context_lines = lines[next_start-1:context_end]
                        partition.next_context = '\n'.join(context_lines)
                    except Exception:
                        partition.next_context = ""
        
        except Exception:
            # Si même l'overlap échoue, continue sans
            pass
