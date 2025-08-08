"""
V10FileIntelligenceEngine - Moteur d'intelligence pour traitement de fichiers.

Gestion intelligente des gros fichiers avec détection de taille, type et stratégies adaptatives.
"""

import os
import asyncio
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum
import time
import re

# Import des composants V10
from Core.Agents.V10.temporal_integration import V10TemporalIntegration


class FileProcessingStrategy(Enum):
    """Stratégies de traitement de fichier."""
    
    # Petits fichiers (< 1MB)
    FULL_READ = "full_read"
    
    # Fichiers moyens (1-10MB)
    CHUNKED_READ = "chunked_read"
    
    # Gros fichiers (10-100MB)
    STREAMING_READ = "streaming_read"
    
    # Fichiers énormes (> 100MB)
    SUMMARIZED_READ = "summarized_read"


@dataclass
class FileMetadata:
    """Métadonnées enrichies de fichier."""
    
    file_path: str
    file_size: int
    file_type: str
    processing_strategy: FileProcessingStrategy
    structure_analysis: Dict[str, Any]
    content_summary: str
    key_points: List[str]
    processing_time: float
    chunks_processed: int
    memory_usage: float


class V10FileSizeAnalyzer:
    """Analyseur intelligent de taille de fichiers."""
    
    def analyze_file_strategy(self, file_path: str) -> FileProcessingStrategy:
        """Détermine la stratégie optimale selon la taille."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        size = os.path.getsize(file_path)
        
        if size < 1_000_000:  # < 1MB
            return FileProcessingStrategy.FULL_READ
        elif size < 10_000_000:  # < 10MB
            return FileProcessingStrategy.CHUNKED_READ
        elif size < 100_000_000:  # < 100MB
            return FileProcessingStrategy.STREAMING_READ
        else:  # > 100MB
            return FileProcessingStrategy.SUMMARIZED_READ
    
    def get_optimal_chunk_size(self, file_size: int) -> int:
        """Détermine la taille optimale de chunk selon la taille du fichier."""
        if file_size < 1_000_000:
            return file_size  # Lecture complète
        elif file_size < 10_000_000:
            return 100_000  # 100KB chunks
        elif file_size < 100_000_000:
            return 1000  # 1000 lignes
        else:
            return 100  # 100 lignes pour résumé


class V10FileTypeDetector:
    """Détecteur intelligent de type de fichier."""
    
    def __init__(self):
        self.code_extensions = {'.py', '.js', '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala'}
        self.text_extensions = {'.md', '.txt', '.rst', '.tex', '.adoc', '.org'}
        self.data_extensions = {'.csv', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'}
        self.binary_extensions = {'.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.db', '.sqlite'}
    
    def detect_file_type(self, file_path: str) -> str:
        """Détecte le type de fichier intelligemment."""
        extension = os.path.splitext(file_path)[1].lower()
        
        # Détection par extension
        if extension in self.code_extensions:
            return "code"
        elif extension in self.text_extensions:
            return "text"
        elif extension in self.data_extensions:
            return "data"
        elif extension in self.binary_extensions:
            return "binary"
        
        # Détection par contenu (premières lignes)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_lines = [f.readline() for _ in range(10)]
                first_content = ''.join(first_lines)
                
                if self._contains_code_patterns(first_content):
                    return "code"
                elif self._contains_data_patterns(first_content):
                    return "data"
                else:
                    return "text"
        except UnicodeDecodeError:
            return "binary"
    
    def _contains_code_patterns(self, content: str) -> bool:
        """Détecte les patterns de code."""
        code_patterns = [
            r'def\s+\w+\s*\(',
            r'function\s+\w+\s*\(',
            r'class\s+\w+',
            r'import\s+',
            r'from\s+',
            r'#include',
            r'public\s+class',
            r'private\s+\w+',
            r'var\s+\w+',
            r'let\s+\w+',
            r'const\s+\w+',
            r'if\s*\(',
            r'for\s*\(',
            r'while\s*\(',
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def _contains_data_patterns(self, content: str) -> bool:
        """Détecte les patterns de données."""
        data_patterns = [
            r'^\s*\{.*\}',
            r'^\s*\[.*\]',
            r'^\s*[^,]+,[^,]+,[^,]+',
            r'^\s*[^=]+=.*',
            r'^\s*[^:]+:.*',
        ]
        
        for pattern in data_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return True
        return False


class V10ContentSummarizer:
    """Résumeur intelligent de contenu."""
    
    def __init__(self):
        self.max_summary_length = 500
        self.key_patterns = [
            r'class\s+(\w+)',
            r'def\s+(\w+)',
            r'function\s+(\w+)',
            r'#\s*(.+)',
            r'//\s*(.+)',
            r'/\*\s*(.+?)\s*\*/',
        ]
    
    async def summarize_large_content(self, content: str, max_length: int = None) -> str:
        """Résume intelligemment le contenu."""
        if max_length is None:
            max_length = self.max_summary_length
        
        # 1. Analyse structurelle
        structure = self._analyze_structure(content)
        
        # 2. Extraction des points clés
        key_points = self._extract_key_points(content, structure)
        
        # 3. Génération de résumé
        summary = self._generate_summary(key_points, structure, max_length)
        
        return summary
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyse la structure du contenu."""
        lines = content.split('\n')
        
        structure = {
            'total_lines': len(lines),
            'non_empty_lines': len([l for l in lines if l.strip()]),
            'code_blocks': 0,
            'comment_blocks': 0,
            'function_definitions': 0,
            'class_definitions': 0,
            'import_statements': 0,
        }
        
        in_code_block = False
        in_comment_block = False
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                continue
            
            # Détection de blocs de code
            if stripped.startswith('```') or stripped.startswith('~~~'):
                in_code_block = not in_code_block
                if in_code_block:
                    structure['code_blocks'] += 1
            
            # Détection de commentaires
            elif stripped.startswith('<!--') or stripped.startswith('/*'):
                in_comment_block = True
                structure['comment_blocks'] += 1
            elif stripped.endswith('-->') or stripped.endswith('*/'):
                in_comment_block = False
            
            # Détection de définitions
            elif re.search(r'^def\s+\w+', stripped):
                structure['function_definitions'] += 1
            elif re.search(r'^class\s+\w+', stripped):
                structure['class_definitions'] += 1
            elif re.search(r'^import\s+', stripped) or re.search(r'^from\s+', stripped):
                structure['import_statements'] += 1
        
        return structure
    
    def _extract_key_points(self, content: str, structure: Dict[str, Any]) -> List[str]:
        """Extrait les points clés du contenu."""
        key_points = []
        
        # Extraction basée sur les patterns
        for pattern in self.key_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            key_points.extend(matches)
        
        # Ajout d'informations structurelles
        if structure['function_definitions'] > 0:
            key_points.append(f"{structure['function_definitions']} fonctions définies")
        if structure['class_definitions'] > 0:
            key_points.append(f"{structure['class_definitions']} classes définies")
        if structure['import_statements'] > 0:
            key_points.append(f"{structure['import_statements']} imports")
        if structure['code_blocks'] > 0:
            key_points.append(f"{structure['code_blocks']} blocs de code")
        
        return key_points[:10]  # Limiter à 10 points clés
    
    def _generate_summary(self, key_points: List[str], structure: Dict[str, Any], max_length: int) -> str:
        """Génère un résumé à partir des points clés."""
        if not key_points:
            return f"Fichier de {structure['total_lines']} lignes ({structure['non_empty_lines']} non vides)"
        
        summary_parts = []
        
        # Informations générales
        summary_parts.append(f"Fichier de {structure['total_lines']} lignes")
        
        # Points clés
        if key_points:
            summary_parts.append("Points clés:")
            for point in key_points[:5]:  # Limiter à 5 points
                summary_parts.append(f"- {point}")
        
        summary = '\n'.join(summary_parts)
        
        # Tronquer si nécessaire
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary


class V10AdaptiveToolRegistry:
    """Registre d'outils adaptatifs selon la taille."""
    
    def __init__(self):
        self.small_file_tools = {}
        self.medium_file_tools = {}
        self.large_file_tools = {}
        self.huge_file_tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialise les outils par catégorie."""
        # Outils pour petits fichiers
        self.small_file_tools = {
            "read_file": self._create_read_file_tool(),
            "write_file": self._create_write_file_tool(),
            "replace_text": self._create_replace_text_tool(),
        }
        
        # Outils pour fichiers moyens
        self.medium_file_tools = {
            "read_chunk": self._create_read_chunk_tool(),
            "write_chunk": self._create_write_chunk_tool(),
            "replace_chunk": self._create_replace_chunk_tool(),
        }
        
        # Outils pour gros fichiers
        self.large_file_tools = {
            "read_lines": self._create_read_lines_tool(),
            "write_lines": self._create_write_lines_tool(),
            "replace_lines": self._create_replace_lines_tool(),
            "summarize_chunk": self._create_summarize_chunk_tool(),
        }
        
        # Outils pour fichiers énormes
        self.huge_file_tools = {
            "analyze_structure": self._create_analyze_structure_tool(),
            "create_index": self._create_create_index_tool(),
            "summarize_section": self._create_summarize_section_tool(),
        }
    
    def get_optimal_tools(self, file_size: int, file_type: str) -> Dict[str, Any]:
        """Retourne les outils optimaux selon la taille et le type."""
        
        if file_size < 1_000_000:
            return self.small_file_tools
        elif file_size < 10_000_000:
            return self.medium_file_tools
        elif file_size < 100_000_000:
            return self.large_file_tools
        else:
            return self.huge_file_tools
    
    def _create_read_file_tool(self):
        """Crée l'outil de lecture de fichier."""
        return {"name": "read_file", "type": "small_file"}
    
    def _create_write_file_tool(self):
        """Crée l'outil d'écriture de fichier."""
        return {"name": "write_file", "type": "small_file"}
    
    def _create_replace_text_tool(self):
        """Crée l'outil de remplacement de texte."""
        return {"name": "replace_text", "type": "small_file"}
    
    def _create_read_chunk_tool(self):
        """Crée l'outil de lecture par chunk."""
        return {"name": "read_chunk", "type": "medium_file"}
    
    def _create_write_chunk_tool(self):
        """Crée l'outil d'écriture par chunk."""
        return {"name": "write_chunk", "type": "medium_file"}
    
    def _create_replace_chunk_tool(self):
        """Crée l'outil de remplacement par chunk."""
        return {"name": "replace_chunk", "type": "medium_file"}
    
    def _create_read_lines_tool(self):
        """Crée l'outil de lecture ligne par ligne."""
        return {"name": "read_lines", "type": "large_file"}
    
    def _create_write_lines_tool(self):
        """Crée l'outil d'écriture ligne par ligne."""
        return {"name": "write_lines", "type": "large_file"}
    
    def _create_replace_lines_tool(self):
        """Crée l'outil de remplacement ligne par ligne."""
        return {"name": "replace_lines", "type": "large_file"}
    
    def _create_summarize_chunk_tool(self):
        """Crée l'outil de résumé de chunk."""
        return {"name": "summarize_chunk", "type": "large_file"}
    
    def _create_analyze_structure_tool(self):
        """Crée l'outil d'analyse de structure."""
        return {"name": "analyze_structure", "type": "huge_file"}
    
    def _create_create_index_tool(self):
        """Crée l'outil de création d'index."""
        return {"name": "create_index", "type": "huge_file"}
    
    def _create_summarize_section_tool(self):
        """Crée l'outil de résumé de section."""
        return {"name": "summarize_section", "type": "huge_file"}


class V10FileIntelligenceEngine:
    """Moteur d'intelligence pour traitement de fichiers."""
    
    def __init__(self, temporal_integration: Optional[V10TemporalIntegration] = None):
        self.size_analyzer = V10FileSizeAnalyzer()
        self.type_detector = V10FileTypeDetector()
        self.tool_registry = V10AdaptiveToolRegistry()
        self.summarizer = V10ContentSummarizer()
        self.temporal_integration = temporal_integration
    
    async def process_large_file(self, file_path: str, operation: str, session_id: str = None) -> Dict[str, Any]:
        """Traite un gros fichier avec intelligence."""
        
        start_time = time.time()
        
        try:
            # 1. Analyse de taille et type
            strategy = self.size_analyzer.analyze_file_strategy(file_path)
            file_type = self.type_detector.detect_file_type(file_path)
            file_size = os.path.getsize(file_path)
            
            # 2. Sélection d'outils
            tools = self.tool_registry.get_optimal_tools(file_size, file_type)
            
            # 3. Traitement adaptatif
            if strategy == FileProcessingStrategy.FULL_READ:
                result = await self._full_read_process(file_path, operation, tools)
            elif strategy == FileProcessingStrategy.CHUNKED_READ:
                result = await self._chunked_process(file_path, operation, tools)
            elif strategy == FileProcessingStrategy.STREAMING_READ:
                result = await self._streaming_process(file_path, operation, tools)
            else:  # SUMMARIZED_READ
                result = await self._summarized_process(file_path, operation, tools)
            
            # 4. Métadonnées
            processing_time = time.time() - start_time
            metadata = FileMetadata(
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                processing_strategy=strategy,
                structure_analysis=result.get('structure', {}),
                content_summary=result.get('summary', ''),
                key_points=result.get('key_points', []),
                processing_time=processing_time,
                chunks_processed=result.get('chunks_processed', 0),
                memory_usage=result.get('memory_usage', 0.0)
            )
            
            # 5. Enregistrement temporel si disponible
            if self.temporal_integration and session_id:
                await self._record_temporal_metadata(metadata, session_id)
            
            return {
                'success': True,
                'result': result,
                'metadata': metadata,
                'strategy': strategy.value,
                'file_type': file_type,
                'processing_time': processing_time
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    async def _full_read_process(self, file_path: str, operation: str, tools: Dict[str, Any]) -> Dict[str, Any]:
        """Traitement pour petits fichiers (lecture complète)."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'content': content,
            'size': len(content),
            'operation': operation,
            'chunks_processed': 1
        }
    
    async def _chunked_process(self, file_path: str, operation: str, tools: Dict[str, Any]) -> Dict[str, Any]:
        """Traitement pour fichiers moyens (par chunks)."""
        chunk_size = self.size_analyzer.get_optimal_chunk_size(os.path.getsize(file_path))
        chunks = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                chunks.append(chunk)
        
        return {
            'chunks': chunks,
            'chunks_processed': len(chunks),
            'operation': operation,
            'total_size': sum(len(chunk) for chunk in chunks)
        }
    
    async def _streaming_process(self, file_path: str, operation: str, tools: Dict[str, Any]) -> Dict[str, Any]:
        """Traitement pour gros fichiers (streaming)."""
        lines = []
        key_points = []
        chunks_processed = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                lines.append(line)
                
                # Traitement par chunks de 1000 lignes
                if len(lines) >= 1000:
                    chunk_content = ''.join(lines)
                    chunk_summary = await self.summarizer.summarize_large_content(chunk_content)
                    key_points.append(f"Chunk {chunks_processed + 1}: {chunk_summary}")
                    chunks_processed += 1
                    lines = []
        
        # Traitement du dernier chunk
        if lines:
            chunk_content = ''.join(lines)
            chunk_summary = await self.summarizer.summarize_large_content(chunk_content)
            key_points.append(f"Chunk {chunks_processed + 1}: {chunk_summary}")
            chunks_processed += 1
        
        return {
            'chunks_processed': chunks_processed,
            'key_points': key_points,
            'operation': operation,
            'total_lines': sum(len(chunk.split('\n')) for chunk in key_points)
        }
    
    async def _summarized_process(self, file_path: str, operation: str, tools: Dict[str, Any]) -> Dict[str, Any]:
        """Traitement pour fichiers énormes (résumé)."""
        structure_analysis = {}
        key_points = []
        chunks_processed = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            structure_analysis = self.summarizer._analyze_structure(content)
            summary = await self.summarizer.summarize_large_content(content)
            key_points = self.summarizer._extract_key_points(content, structure_analysis)
            chunks_processed = 1
        
        return {
            'summary': summary,
            'structure': structure_analysis,
            'key_points': key_points,
            'chunks_processed': chunks_processed,
            'operation': operation
        }
    
    async def _record_temporal_metadata(self, metadata: FileMetadata, session_id: str):
        """Enregistre les métadonnées dans la mémoire temporelle."""
        if self.temporal_integration:
            await self.temporal_integration.create_temporal_node(
                content=f"File processing: {metadata.file_path}",
                metadata={
                    'file_size': metadata.file_size,
                    'file_type': metadata.file_type,
                    'strategy': metadata.processing_strategy.value,
                    'processing_time': metadata.processing_time,
                    'chunks_processed': metadata.chunks_processed
                },
                session_id=session_id
            )


# Interface principale
async def process_file_intelligently(file_path: str, operation: str, session_id: str = None) -> Dict[str, Any]:
    """Interface principale pour traitement intelligent de fichiers."""
    engine = V10FileIntelligenceEngine()
    return await engine.process_large_file(file_path, operation, session_id)
