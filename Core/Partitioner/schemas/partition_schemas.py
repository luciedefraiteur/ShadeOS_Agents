"""
🧠 Schémas de Données pour le Partitionnement de Fichiers

Structures de données fondamentales pour le système de partitionnement robuste.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class PartitionMethod(Enum):
    """Méthodes de partitionnement disponibles."""
    AST = "ast"
    REGEX = "regex"
    TEXTUAL = "textual"
    EMERGENCY = "emergency"
    CUSTOM = "custom"


class BlockType(Enum):
    """Types de blocs de partition."""
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    IMPORT = "import"
    VARIABLE = "variable"
    COMMENT = "comment"
    SECTION = "section"
    CHUNK = "chunk"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class PartitionLocation:
    """Localisation précise d'un bloc dans un fichier."""
    
    # Coordonnées de ligne (1-based)
    start_line: int
    end_line: int
    
    # Coordonnées de caractère (0-based dans la ligne)
    start_char: int
    end_char: int
    
    # Coordonnées absolues dans le fichier (0-based)
    start_offset: int
    end_offset: int
    
    # Métadonnées du fichier
    total_lines: int
    total_chars: int
    line_lengths: List[int] = field(default_factory=list)
    
    def __init__(self, start_line: int = None, start_char: int = None, end_line: int = None, 
                 end_char: int = None, start_offset: int = None, end_offset: int = None, 
                 total_lines: int = None, total_chars: int = None, line_lengths: List[int] = None,
                 start_column: int = None, end_column: int = None):
        """Constructeur avec paramètres nommés pour compatibilité avec les tests."""
        # Support des anciens paramètres positionnels
        if start_line is not None and start_char is not None and end_line is not None and end_char is not None:
            self.start_line = start_line
            self.start_char = start_char
            self.end_line = end_line
            self.end_char = end_char
            self.start_offset = start_offset or 0
            self.end_offset = end_offset or 0
            self.total_lines = total_lines or 1
            self.total_chars = total_chars or 0
            self.line_lengths = line_lengths or []
        else:
            # Support des nouveaux paramètres nommés
            self.start_line = start_line or 1
            self.start_char = start_char or 0
            self.end_line = end_line or 1
            self.end_char = end_char or 0
            self.start_offset = start_offset or 0
            self.end_offset = end_offset or 0
            self.total_lines = total_lines or 1
            self.total_chars = total_chars or 0
            self.line_lengths = line_lengths or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Sérialisation pour stockage."""
        return asdict(self)
    
    def extract_content(self, full_content: str) -> str:
        """Extrait le contenu exact basé sur les coordonnées."""
        if self.start_offset >= len(full_content) or self.end_offset > len(full_content):
            raise ValueError(f"Offsets invalides: {self.start_offset}-{self.end_offset} pour contenu de {len(full_content)} caractères")
        
        return full_content[self.start_offset:self.end_offset]
    
    def get_line_range(self) -> range:
        """Range des lignes concernées."""
        return range(self.start_line, self.end_line + 1)
    
    def contains_line(self, line_number: int) -> bool:
        """Vérifie si une ligne est dans ce bloc."""
        return self.start_line <= line_number <= self.end_line
    
    def contains_position(self, line: int, char: int) -> bool:
        """Vérifie si une position est dans ce bloc."""
        if line < self.start_line or line > self.end_line:
            return False
        
        if line == self.start_line and char < self.start_char:
            return False
        
        if line == self.end_line and char > self.end_char:
            return False
        
        return True
    
    def overlaps_with(self, other: 'PartitionLocation') -> bool:
        """Vérifie si ce bloc chevauche avec un autre."""
        return not (self.end_line < other.start_line or self.start_line > other.end_line)
    
    def get_size_info(self) -> Dict[str, int]:
        """Informations sur la taille du bloc."""
        return {
            'lines': self.end_line - self.start_line + 1,
            'chars': self.end_offset - self.start_offset,
            'start_line': self.start_line,
            'end_line': self.end_line
        }


@dataclass
class PartitionBlock:
    """Représente un bloc partitionné."""
    block_type: BlockType
    content: str
    location: PartitionLocation
    metadata: Dict[str, Any] = field(default_factory=dict)
    method: PartitionMethod = PartitionMethod.AST
    confidence: float = 1.0
    dependencies: List[str] = field(default_factory=list)
    parent_block: Optional[str] = None


@dataclass
class PartitionResult:
    """Résultat complet d'un partitionnement."""
    
    # Métadonnées du fichier
    file_path: str
    file_type: str
    total_lines: int
    total_chars: int
    
    # Résultats de partition
    partitions: List[PartitionBlock]
    strategy_used: Optional[PartitionMethod] = None
    success: bool = False
    
    # Erreurs et warnings
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Métadonnées de traitement
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Sérialisation pour stockage."""
        data = asdict(self)
        data['strategy_used'] = self.strategy_used.value if self.strategy_used else None
        data['timestamp'] = self.timestamp.isoformat()
        data['partitions'] = [p.to_dict() for p in self.partitions]
        return data
    
    def get_partition_by_location(self, line: int, char: int = 0) -> Optional[PartitionBlock]:
        """Trouve la partition contenant une position donnée."""
        for partition in self.partitions:
            if partition.location.contains_position(line, char):
                return partition
        return None
    
    def get_overlapping_partitions(self, start_line: int, end_line: int) -> List[PartitionBlock]:
        """Trouve toutes les partitions qui chevauchent une plage."""
        overlapping = []
        for partition in self.partitions:
            loc = partition.location
            if not (end_line < loc.start_line or start_line > loc.end_line):
                overlapping.append(partition)
        return overlapping
    
    def get_partitions_by_type(self, block_type: BlockType) -> List[PartitionBlock]:
        """Récupère toutes les partitions d'un type donné."""
        return [p for p in self.partitions if p.block_type == block_type]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques du partitionnement."""
        type_counts = {}
        for partition in self.partitions:
            type_name = partition.block_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        total_errors = sum(len(p.parsing_errors) for p in self.partitions)
        total_warnings = sum(len(p.warnings) for p in self.partitions)
        
        return {
            'total_partitions': len(self.partitions),
            'partition_types': type_counts,
            'strategy_used': self.strategy_used.value if self.strategy_used else None,
            'success': self.success,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'processing_time': self.processing_time,
            'coverage': self._calculate_coverage()
        }
    
    def _calculate_coverage(self) -> float:
        """Calcule le pourcentage de couverture du fichier."""
        if not self.partitions:
            return 0.0
        
        covered_chars = sum(len(p.content) for p in self.partitions)
        return (covered_chars / self.total_chars) * 100 if self.total_chars > 0 else 0.0
    
    def add_error(self, error_type: str, message: str, details: Dict[str, Any] = None):
        """Ajoute une erreur globale au résultat."""
        error = {
            'type': error_type,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.errors.append(error)
    
    def add_warning(self, message: str):
        """Ajoute un avertissement global au résultat."""
        self.warnings.append(f"{datetime.now().isoformat()}: {message}")


# Exceptions personnalisées
class PartitioningError(Exception):
    """Erreur de partitionnement."""
    pass


class LocationTrackingError(Exception):
    """Erreur de tracking de localisation."""
    pass


class PartitionValidationError(Exception):
    """Erreur de validation de partition."""
    pass
