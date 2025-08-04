"""
📍 Système de Tracking de Localisation Précise

Calcul et gestion des coordonnées exactes dans les fichiers.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import ast
from typing import List, Tuple, Optional, Dict, Any
from .partition_schemas import PartitionLocation, LocationTrackingError


class LocationTracker:
    """Tracker de localisation précise pour fichiers."""
    
    def __init__(self):
        self.line_offsets: List[int] = []
        self.line_lengths: List[int] = []
        self.total_chars: int = 0
        self.total_lines: int = 0
    
    def analyze_file_structure(self, content: str) -> None:
        """Analyse la structure du fichier pour le tracking."""
        self.line_offsets = []
        self.line_lengths = []
        
        lines = content.split('\n')
        self.total_lines = len(lines)
        self.total_chars = len(content)
        
        current_offset = 0
        for line in lines:
            self.line_offsets.append(current_offset)
            self.line_lengths.append(len(line))
            current_offset += len(line) + 1  # +1 pour le \n
    
    def create_location_from_lines(self, content: str, start_line: int, 
                                  end_line: int, start_char: int = 0, 
                                  end_char: Optional[int] = None) -> PartitionLocation:
        """Crée une PartitionLocation à partir de coordonnées de lignes."""
        
        if not self.line_offsets:
            self.analyze_file_structure(content)
        
        # Validation des coordonnées
        if start_line < 1 or start_line > self.total_lines:
            raise LocationTrackingError(f"start_line {start_line} invalide (1-{self.total_lines})")
        
        if end_line < start_line or end_line > self.total_lines:
            raise LocationTrackingError(f"end_line {end_line} invalide ({start_line}-{self.total_lines})")
        
        # Calcul des offsets absolus
        start_offset = self.line_offsets[start_line - 1] + start_char
        
        if end_char is None:
            end_char = self.line_lengths[end_line - 1]
        
        end_offset = self.line_offsets[end_line - 1] + end_char
        
        # Validation des offsets
        if start_offset < 0 or start_offset > self.total_chars:
            raise LocationTrackingError(f"start_offset {start_offset} invalide")
        
        if end_offset < start_offset or end_offset > self.total_chars:
            raise LocationTrackingError(f"end_offset {end_offset} invalide")
        
        return PartitionLocation(
            start_line=start_line,
            end_line=end_line,
            start_char=start_char,
            end_char=end_char,
            start_offset=start_offset,
            end_offset=end_offset,
            total_lines=self.total_lines,
            total_chars=self.total_chars,
            line_lengths=self.line_lengths.copy()
        )
    
    def create_location_from_offsets(self, content: str, start_offset: int, 
                                   end_offset: int) -> PartitionLocation:
        """Crée une PartitionLocation à partir d'offsets absolus."""
        
        if not self.line_offsets:
            self.analyze_file_structure(content)
        
        # Validation des offsets
        if start_offset < 0 or start_offset > self.total_chars:
            raise LocationTrackingError(f"start_offset {start_offset} invalide")
        
        if end_offset < start_offset or end_offset > self.total_chars:
            raise LocationTrackingError(f"end_offset {end_offset} invalide")
        
        # Calcul des coordonnées de lignes
        start_line, start_char = self._offset_to_line_char(start_offset)
        end_line, end_char = self._offset_to_line_char(end_offset)
        
        return PartitionLocation(
            start_line=start_line,
            end_line=end_line,
            start_char=start_char,
            end_char=end_char,
            start_offset=start_offset,
            end_offset=end_offset,
            total_lines=self.total_lines,
            total_chars=self.total_chars,
            line_lengths=self.line_lengths.copy()
        )
    
    def create_location_from_ast_node(self, content: str, node: ast.AST) -> PartitionLocation:
        """Crée une PartitionLocation à partir d'un nœud AST."""
        
        if not self.line_offsets:
            self.analyze_file_structure(content)
        
        # Extraction des coordonnées AST
        start_line = getattr(node, 'lineno', 1)
        end_line = getattr(node, 'end_lineno', start_line)
        start_char = getattr(node, 'col_offset', 0)
        end_char = getattr(node, 'end_col_offset', None)
        
        # Si end_col_offset n'est pas disponible, utilise la fin de la ligne
        if end_char is None:
            if end_line <= len(self.line_lengths):
                end_char = self.line_lengths[end_line - 1]
            else:
                end_char = 0
        
        return self.create_location_from_lines(
            content, start_line, end_line, start_char, end_char
        )
    
    def _offset_to_line_char(self, offset: int) -> Tuple[int, int]:
        """Convertit un offset absolu en coordonnées ligne/caractère."""
        
        # Recherche binaire de la ligne
        left, right = 0, len(self.line_offsets) - 1
        line_index = 0
        
        while left <= right:
            mid = (left + right) // 2
            if self.line_offsets[mid] <= offset:
                line_index = mid
                left = mid + 1
            else:
                right = mid - 1
        
        # Calcul du caractère dans la ligne
        line_start_offset = self.line_offsets[line_index]
        char_in_line = offset - line_start_offset
        
        # Validation
        if char_in_line > self.line_lengths[line_index]:
            char_in_line = self.line_lengths[line_index]
        
        return line_index + 1, char_in_line  # +1 car les lignes sont 1-based
    
    def validate_location(self, location: PartitionLocation, content: str) -> bool:
        """Valide qu'une location est cohérente avec le contenu."""
        
        try:
            # Vérification que l'extraction fonctionne
            extracted = location.extract_content(content)
            
            # Vérification des coordonnées
            if location.start_line < 1 or location.end_line > location.total_lines:
                return False
            
            if location.start_offset < 0 or location.end_offset > location.total_chars:
                return False
            
            if location.start_offset >= location.end_offset:
                return False
            
            # Vérification de la cohérence lignes/offsets
            calculated_location = self.create_location_from_lines(
                content, location.start_line, location.end_line,
                location.start_char, location.end_char
            )
            
            return (calculated_location.start_offset == location.start_offset and
                   calculated_location.end_offset == location.end_offset)
        
        except Exception:
            return False
    
    def merge_locations(self, locations: List[PartitionLocation]) -> Optional[PartitionLocation]:
        """Fusionne plusieurs locations en une seule englobante."""
        
        if not locations:
            return None
        
        if len(locations) == 1:
            return locations[0]
        
        # Trouve les bornes min/max
        min_start_line = min(loc.start_line for loc in locations)
        max_end_line = max(loc.end_line for loc in locations)
        min_start_offset = min(loc.start_offset for loc in locations)
        max_end_offset = max(loc.end_offset for loc in locations)
        
        # Utilise les métadonnées de la première location
        first_loc = locations[0]
        
        # Calcul des caractères de début/fin
        start_char = 0
        end_char = 0
        
        for loc in locations:
            if loc.start_line == min_start_line:
                start_char = loc.start_char
            if loc.end_line == max_end_line:
                end_char = loc.end_char
        
        return PartitionLocation(
            start_line=min_start_line,
            end_line=max_end_line,
            start_char=start_char,
            end_char=end_char,
            start_offset=min_start_offset,
            end_offset=max_end_offset,
            total_lines=first_loc.total_lines,
            total_chars=first_loc.total_chars,
            line_lengths=first_loc.line_lengths
        )
    
    def calculate_overlap(self, loc1: PartitionLocation, 
                         loc2: PartitionLocation) -> Optional[PartitionLocation]:
        """Calcule la zone de chevauchement entre deux locations."""
        
        if not loc1.overlaps_with(loc2):
            return None
        
        # Calcul des bornes de l'overlap
        start_line = max(loc1.start_line, loc2.start_line)
        end_line = min(loc1.end_line, loc2.end_line)
        start_offset = max(loc1.start_offset, loc2.start_offset)
        end_offset = min(loc1.end_offset, loc2.end_offset)
        
        # Calcul des caractères (approximatif)
        start_char = 0
        end_char = 0
        
        if start_line == loc1.start_line:
            start_char = loc1.start_char
        elif start_line == loc2.start_line:
            start_char = loc2.start_char
        
        if end_line == loc1.end_line:
            end_char = loc1.end_char
        elif end_line == loc2.end_line:
            end_char = loc2.end_char
        
        return PartitionLocation(
            start_line=start_line,
            end_line=end_line,
            start_char=start_char,
            end_char=end_char,
            start_offset=start_offset,
            end_offset=end_offset,
            total_lines=loc1.total_lines,
            total_chars=loc1.total_chars,
            line_lengths=loc1.line_lengths
        )
    
    def get_context_location(self, location: PartitionLocation, 
                           context_lines: int = 5) -> PartitionLocation:
        """Crée une location étendue avec du contexte."""
        
        start_line = max(1, location.start_line - context_lines)
        end_line = min(location.total_lines, location.end_line + context_lines)
        
        # Calcul des nouveaux offsets
        start_offset = self.line_offsets[start_line - 1] if start_line <= len(self.line_offsets) else 0
        
        if end_line <= len(self.line_offsets):
            end_offset = self.line_offsets[end_line - 1] + self.line_lengths[end_line - 1]
        else:
            end_offset = location.total_chars
        
        return PartitionLocation(
            start_line=start_line,
            end_line=end_line,
            start_char=0,
            end_char=self.line_lengths[end_line - 1] if end_line <= len(self.line_lengths) else 0,
            start_offset=start_offset,
            end_offset=end_offset,
            total_lines=location.total_lines,
            total_chars=location.total_chars,
            line_lengths=location.line_lengths
        )
