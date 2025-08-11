"""
V10SpecializedTools - Outils spécialisés pour gros fichiers.

Outils optimisés pour le traitement de fichiers volumineux avec gestion ligne par ligne.
"""

import os
import asyncio
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import time
import re
import ast
import tokenize
import io

# Import des composants V10
from Core.Agents.V10.file_intelligence_engine import V10ContentSummarizer
# Imports optionnels avec fallback pour éviter durs
try:
    from TemporalFractalMemoryEngine.core.temporal_engine import TemporalEngine
    _HAS_TFME = True
except Exception:
    _HAS_TFME = False
    class TemporalEngine:  # type: ignore
        async def create_temporal_node(self, *args, **kwargs):
            class _N: node_id = "sim_scope_node"
            return _N()

try:
    from Core.Providers.LLMProviders.llm_provider import LLMProvider, ProviderType
except Exception:
    class LLMProvider:  # type: ignore
        async def generate_text(self, prompt: str, **kwargs):
            class _R: content = f"MOCK_ONLY: {prompt[:60]}..."
            return _R()
    class ProviderType:  # type: ignore
        LOCAL = "local"

# Imports optionnels ProviderFactory et flags/env
try:
    from Core.Providers.LLMProviders.provider_factory import ProviderFactory
except Exception:
    ProviderFactory = None  # type: ignore

try:
    from Core.Config.feature_flags import get_llm_mode, allow_mock_fallback
except Exception:
    def get_llm_mode() -> str:  # type: ignore
        return "mock"
    def allow_mock_fallback() -> bool:  # type: ignore
        return True

try:
    from Core.Config.secure_env_manager import load_project_environment
except Exception:
    async def load_project_environment():  # type: ignore
        return {}


@dataclass
class ToolResult:
    """Résultat d'exécution d'outil."""
    
    success: bool
    tool_name: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


class V10ReadLinesTool:
    """Outil de lecture ligne par ligne pour gros fichiers."""
    
    def __init__(self):
        self.default_chunk_size = 1000
        self.max_line_length = 10000  # 10KB par ligne max
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Exécute la lecture ligne par ligne."""
        start_time = time.time()
        
        try:
            file_path = params.get("file_path")
            start_line = params.get("start_line", 1)
            end_line = params.get("end_line", None)
            chunk_size = params.get("chunk_size", self.default_chunk_size)
            
            if not file_path or not os.path.exists(file_path):
                return ToolResult(
                    success=False,
                    tool_name="read_lines",
                    error=f"Fichier non trouvé: {file_path}",
                    execution_time=time.time() - start_time
                )
            
            lines = []
            line_count = 0
            current_line = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    current_line += 1
                    
                    # Vérifier les limites
                    if current_line < start_line:
                        continue
                    
                    if end_line and current_line > end_line:
                        break
                    
                    # Vérifier la longueur de ligne
                    if len(line) > self.max_line_length:
                        line = line[:self.max_line_length] + "... [TRONQUÉ]"
                    
                    lines.append(line)
                    line_count += 1
                    
                    # Limiter par chunk
                    if line_count >= chunk_size:
                        break
            
            return ToolResult(
                success=True,
                tool_name="read_lines",
                data={
                    "lines": lines,
                    "start_line": start_line,
                    "end_line": current_line,
                    "total_lines_read": line_count,
                    "file_path": file_path
                },
                execution_time=time.time() - start_time,
                metadata={
                    "chunk_size": chunk_size,
                    "max_line_length": self.max_line_length
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                tool_name="read_lines",
                error=str(e),
                execution_time=time.time() - start_time
            )


class V10WriteLinesTool:
    """Outil d'écriture ligne par ligne pour gros fichiers."""
    
    def __init__(self):
        self.backup_extension = ".backup"
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Exécute l'écriture ligne par ligne."""
        start_time = time.time()
        
        try:
            file_path = params.get("file_path")
            lines = params.get("lines", [])
            mode = params.get("mode", "overwrite")  # overwrite, append, insert
            insert_line = params.get("insert_line", None)
            create_backup = params.get("create_backup", True)
            
            if not file_path:
                return ToolResult(
                    success=False,
                    tool_name="write_lines",
                    error="Chemin de fichier manquant",
                    execution_time=time.time() - start_time
                )
            
            # Créer backup si demandé
            if create_backup and os.path.exists(file_path):
                backup_path = file_path + self.backup_extension
                os.rename(file_path, backup_path)
            
            # Écriture selon le mode
            if mode == "overwrite":
                with open(file_path, 'w', encoding='utf-8') as f:
                    for line in lines:
                        f.write(line)
            
            elif mode == "append":
                with open(file_path, 'a', encoding='utf-8') as f:
                    for line in lines:
                        f.write(line)
            
            elif mode == "insert" and insert_line is not None:
                # Lecture du fichier existant
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_lines = f.readlines()
                
                # Insertion des nouvelles lignes
                existing_lines[insert_line:insert_line] = lines
                
                # Réécriture complète
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(existing_lines)
            
            return ToolResult(
                success=True,
                tool_name="write_lines",
                data={
                    "file_path": file_path,
                    "lines_written": len(lines),
                    "mode": mode,
                    "backup_created": create_backup and os.path.exists(file_path + self.backup_extension)
                },
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                tool_name="write_lines",
                error=str(e),
                execution_time=time.time() - start_time
            )


class V10ReplaceLinesTool:
    """Outil de remplacement ligne par ligne pour gros fichiers."""
    
    def __init__(self):
        self.max_replacements = 10000  # Limite de sécurité
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Exécute le remplacement ligne par ligne."""
        start_time = time.time()
        
        try:
            file_path = params.get("file_path")
            search_pattern = params.get("search_pattern")
            replace_pattern = params.get("replace_pattern", "")
            start_line = params.get("start_line", 1)
            end_line = params.get("end_line", None)
            case_sensitive = params.get("case_sensitive", False)
            regex_mode = params.get("regex_mode", False)
            
            if not file_path or not os.path.exists(file_path):
                return ToolResult(
                    success=False,
                    tool_name="replace_lines",
                    error=f"Fichier non trouvé: {file_path}",
                    execution_time=time.time() - start_time
                )
            
            if not search_pattern:
                return ToolResult(
                    success=False,
                    tool_name="replace_lines",
                    error="Pattern de recherche manquant",
                    execution_time=time.time() - start_time
                )
            
            # Compiler le pattern si regex
            if regex_mode:
                try:
                    pattern = re.compile(search_pattern, flags=0 if case_sensitive else re.IGNORECASE)
                except re.error as e:
                    return ToolResult(
                        success=False,
                        tool_name="replace_lines",
                        error=f"Pattern regex invalide: {e}",
                        execution_time=time.time() - start_time
                    )
            else:
                pattern = None
            
            # Lecture et remplacement
            lines = []
            replacements = 0
            current_line = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    current_line += 1
                    
                    # Vérifier les limites
                    if current_line < start_line:
                        lines.append(line)
                        continue
                    
                    if end_line and current_line > end_line:
                        lines.append(line)
                        continue
                    
                    # Effectuer le remplacement
                    original_line = line
                    if regex_mode:
                        if pattern.search(line):
                            line = pattern.sub(replace_pattern, line)
                            replacements += 1
                    else:
                        if case_sensitive:
                            if search_pattern in line:
                                line = line.replace(search_pattern, replace_pattern)
                                replacements += 1
                        else:
                            if search_pattern.lower() in line.lower():
                                # Remplacement insensible à la casse
                                import re
                                pattern_ci = re.compile(re.escape(search_pattern), re.IGNORECASE)
                                line = pattern_ci.sub(replace_pattern, line)
                                replacements += 1
                    
                    lines.append(line)
                    
                    # Limite de sécurité
                    if replacements >= self.max_replacements:
                        break
            
            # Écriture du fichier modifié
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return ToolResult(
                success=True,
                tool_name="replace_lines",
                data={
                    "file_path": file_path,
                    "replacements_made": replacements,
                    "total_lines_processed": current_line,
                    "search_pattern": search_pattern,
                    "replace_pattern": replace_pattern
                },
                execution_time=time.time() - start_time,
                metadata={
                    "case_sensitive": case_sensitive,
                    "regex_mode": regex_mode,
                    "max_replacements": self.max_replacements
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                tool_name="replace_lines",
                error=str(e),
                execution_time=time.time() - start_time
            )


class V10SummarizeChunkTool:
    """Outil de résumé de chunk pour gros fichiers."""
    
    def __init__(self):
        self.summarizer = V10ContentSummarizer()
        self.max_chunk_size = 10000  # 10KB par chunk
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Exécute le résumé de chunk."""
        start_time = time.time()
        
        try:
            content = params.get("content", "")
            chunk_id = params.get("chunk_id", "unknown")
            max_length = params.get("max_length", 500)
            include_metadata = params.get("include_metadata", True)
            
            if not content:
                return ToolResult(
                    success=False,
                    tool_name="summarize_chunk",
                    error="Contenu manquant",
                    execution_time=time.time() - start_time
                )
            
            # Limiter la taille du chunk
            if len(content) > self.max_chunk_size:
                content = content[:self.max_chunk_size] + "... [TRONQUÉ]"
            
            # Générer le résumé
            summary = await self.summarizer.summarize_large_content(content, max_length)
            
            # Analyser la structure
            structure = self.summarizer._analyze_structure(content)
            key_points = self.summarizer._extract_key_points(content, structure)
            
            result_data = {
                "chunk_id": chunk_id,
                "summary": summary,
                "original_length": len(content),
                "summary_length": len(summary)
            }
            
            if include_metadata:
                result_data.update({
                    "structure": structure,
                    "key_points": key_points,
                    "compression_ratio": len(summary) / len(content) if len(content) > 0 else 0
                })
            
            return ToolResult(
                success=True,
                tool_name="summarize_chunk",
                data=result_data,
                execution_time=time.time() - start_time,
                metadata={
                    "max_chunk_size": self.max_chunk_size,
                    "include_metadata": include_metadata
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                tool_name="summarize_chunk",
                error=str(e),
                execution_time=time.time() - start_time
            )


class V10AnalyzeStructureTool:
    """Outil d'analyse de structure pour fichiers énormes."""
    
    def __init__(self):
        self.structure_patterns = {
            'headers': [r'^#{1,6}\s+', r'^[A-Z][A-Z\s]+\n=+\n'],
            'code_blocks': [r'```[\w]*\n', r'~~~[\w]*\n'],
            'functions': [r'^def\s+\w+', r'^function\s+\w+', r'^public\s+\w+'],
            'classes': [r'^class\s+\w+', r'^interface\s+\w+'],
            'imports': [r'^import\s+', r'^from\s+', r'^#include'],
            'comments': [r'^#\s+', r'^//\s+', r'^/\*'],
        }
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Exécute l'analyse de structure."""
        start_time = time.time()
        
        try:
            file_path = params.get("file_path")
            max_lines = params.get("max_lines", 10000)
            include_patterns = params.get("include_patterns", True)
            
            if not file_path or not os.path.exists(file_path):
                return ToolResult(
                    success=False,
                    tool_name="analyze_structure",
                    error=f"Fichier non trouvé: {file_path}",
                    execution_time=time.time() - start_time
                )
            
            structure_analysis = {
                'file_path': file_path,
                'total_lines': 0,
                'non_empty_lines': 0,
                'sections': [],
                'patterns_found': {},
                'structure_summary': {}
            }
            
            line_count = 0
            current_section = None
            section_start = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line_count += 1
                    stripped_line = line.strip()
                    
                    if line_count > max_lines:
                        break
                    
                    if stripped_line:
                        structure_analysis['non_empty_lines'] += 1
                    
                    # Détection de sections
                    if self._is_section_header(line):
                        if current_section:
                            # Fermer la section précédente
                            structure_analysis['sections'].append({
                                'name': current_section,
                                'start_line': section_start,
                                'end_line': line_count - 1,
                                'line_count': line_count - section_start
                            })
                        
                        current_section = stripped_line
                        section_start = line_count
                    
                    # Détection de patterns
                    if include_patterns:
                        for pattern_type, patterns in self.structure_patterns.items():
                            for pattern in patterns:
                                if re.search(pattern, line, re.IGNORECASE):
                                    if pattern_type not in structure_analysis['patterns_found']:
                                        structure_analysis['patterns_found'][pattern_type] = 0
                                    structure_analysis['patterns_found'][pattern_type] += 1
                                    break
                
                # Fermer la dernière section
                if current_section:
                    structure_analysis['sections'].append({
                        'name': current_section,
                        'start_line': section_start,
                        'end_line': line_count,
                        'line_count': line_count - section_start + 1
                    })
            
            structure_analysis['total_lines'] = line_count
            
            # Générer le résumé de structure
            structure_analysis['structure_summary'] = self._generate_structure_summary(structure_analysis)
            
            return ToolResult(
                success=True,
                tool_name="analyze_structure",
                data=structure_analysis,
                execution_time=time.time() - start_time,
                metadata={
                    'max_lines_analyzed': max_lines,
                    'include_patterns': include_patterns
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                tool_name="analyze_structure",
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def _is_section_header(self, line: str) -> bool:
        """Détecte si une ligne est un en-tête de section."""
        stripped = line.strip()
        
        # Headers Markdown
        if re.match(r'^#{1,6}\s+', stripped):
            return True
        
        # Headers avec soulignement
        if re.match(r'^[A-Z][A-Z\s]+\n=+\n', line):
            return True
        
        # Headers avec tirets
        if re.match(r'^[A-Z][A-Z\s]+\n-+\n', line):
            return True
        
        return False
    
    def _generate_structure_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Génère un résumé de la structure."""
        summary = {
            'total_sections': len(analysis['sections']),
            'largest_section': None,
            'average_section_size': 0,
            'pattern_summary': {}
        }
        
        if analysis['sections']:
            section_sizes = [s['line_count'] for s in analysis['sections']]
            summary['largest_section'] = max(section_sizes)
            summary['average_section_size'] = sum(section_sizes) / len(section_sizes)
        
        for pattern_type, count in analysis['patterns_found'].items():
            summary['pattern_summary'][pattern_type] = count
        
        return summary


class V10CreateIndexTool:
    """Outil de création d'index pour fichiers énormes."""
    
    def __init__(self):
        self.index_patterns = {
            'keywords': [r'\b\w{4,}\b'],  # Mots de 4+ caractères
            'functions': [r'def\s+(\w+)', r'function\s+(\w+)'],
            'classes': [r'class\s+(\w+)', r'interface\s+(\w+)'],
            'imports': [r'import\s+(\w+)', r'from\s+(\w+)'],
            'headers': [r'^#{1,6}\s+(\w+)'],
        }
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Exécute la création d'index."""
        start_time = time.time()
        
        try:
            file_path = params.get("file_path")
            index_types = params.get("index_types", ["keywords", "functions", "classes"])
            max_entries = params.get("max_entries", 1000)
            
            if not file_path or not os.path.exists(file_path):
                return ToolResult(
                    success=False,
                    tool_name="create_index",
                    error=f"Fichier non trouvé: {file_path}",
                    execution_time=time.time() - start_time
                )
            
            index_data = {
                'file_path': file_path,
                'index_types': index_types,
                'entries': {},
                'statistics': {}
            }
            
            # Créer les index demandés
            for index_type in index_types:
                if index_type in self.index_patterns:
                    index_data['entries'][index_type] = await self._create_index_for_type(
                        file_path, index_type, max_entries
                    )
            
            # Calculer les statistiques
            for index_type, entries in index_data['entries'].items():
                index_data['statistics'][index_type] = {
                    'total_entries': len(entries),
                    'unique_entries': len(set(entries)),
                    'most_common': self._get_most_common(entries, 10)
                }
            
            return ToolResult(
                success=True,
                tool_name="create_index",
                data=index_data,
                execution_time=time.time() - start_time,
                metadata={
                    'index_types': index_types,
                    'max_entries': max_entries
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                tool_name="create_index",
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def _create_index_for_type(self, file_path: str, index_type: str, max_entries: int) -> List[str]:
        """Crée un index pour un type spécifique."""
        entries = []
        patterns = self.index_patterns.get(index_type, [])
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                for pattern in patterns:
                    matches = re.findall(pattern, line, re.IGNORECASE)
                    entries.extend(matches)
                    
                    if len(entries) >= max_entries:
                        return entries[:max_entries]
        
        return entries[:max_entries]
    
    def _get_most_common(self, entries: List[str], top_n: int) -> List[Tuple[str, int]]:
        """Trouve les entrées les plus communes."""
        from collections import Counter
        counter = Counter(entries)
        return counter.most_common(top_n)


class V10SummarizeSectionTool:
    """Outil de résumé de section pour fichiers énormes."""
    
    def __init__(self):
        self.summarizer = V10ContentSummarizer()
        self.max_section_size = 50000  # 50KB par section
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Exécute le résumé de section."""
        start_time = time.time()
        
        try:
            file_path = params.get("file_path")
            section_name = params.get("section_name")
            start_line = params.get("start_line", 1)
            end_line = params.get("end_line", None)
            max_length = params.get("max_length", 300)
            
            if not file_path or not os.path.exists(file_path):
                return ToolResult(
                    success=False,
                    tool_name="summarize_section",
                    error=f"Fichier non trouvé: {file_path}",
                    execution_time=time.time() - start_time
                )
            
            # Extraire la section
            section_content = await self._extract_section(file_path, start_line, end_line)
            
            if not section_content:
                return ToolResult(
                    success=False,
                    tool_name="summarize_section",
                    error="Section vide ou non trouvée",
                    execution_time=time.time() - start_time
                )
            
            # Limiter la taille
            if len(section_content) > self.max_section_size:
                section_content = section_content[:self.max_section_size] + "... [TRONQUÉ]"
            
            # Générer le résumé
            summary = await self.summarizer.summarize_large_content(section_content, max_length)
            
            # Analyser la structure
            structure = self.summarizer._analyze_structure(section_content)
            key_points = self.summarizer._extract_key_points(section_content, structure)
            
            return ToolResult(
                success=True,
                tool_name="summarize_section",
                data={
                    'section_name': section_name,
                    'start_line': start_line,
                    'end_line': end_line,
                    'summary': summary,
                    'original_length': len(section_content),
                    'summary_length': len(summary),
                    'structure': structure,
                    'key_points': key_points,
                    'compression_ratio': len(summary) / len(section_content) if len(section_content) > 0 else 0
                },
                execution_time=time.time() - start_time,
                metadata={
                    'max_section_size': self.max_section_size
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                tool_name="summarize_section",
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def _extract_section(self, file_path: str, start_line: int, end_line: Optional[int]) -> str:
        """Extrait le contenu d'une section."""
        lines = []
        current_line = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                current_line += 1
                
                if current_line < start_line:
                    continue
                
                if end_line and current_line > end_line:
                    break
                
                lines.append(line)
        
        return ''.join(lines)


class V10ReadChunksUntilScopeTool:
    """Outil spécialisé pour lire des chunks jusqu'au prochain scope complet."""
    
    def __init__(self, temporal_engine: TemporalEngine, llm_provider: Optional[LLMProvider] = None):
        self.temporal_engine = temporal_engine
        self.scope_detector = V10ScopeDetector()
        # LLM provider optionnel (utilise un mock local si absent)
        self.llm_provider = llm_provider or _MockLLMProvider()

    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Lit des chunks jusqu'à un scope complet, optionnellement analyse le scope via LLM, et crée un nœud temporel."""
        start_time = time.time()
        try:
            file_path = params.get('file_path')
            start_line = params.get('start_line', 1)
            max_chunks = params.get('max_chunks', 10)
            scope_type = params.get('scope_type', 'auto')  # auto, function, class, block
            include_analysis = params.get('include_analysis', True)
            debug_mode = params.get('debug', False)
            prefer_balanced_end = params.get('prefer_balanced_end')
            min_scanned_lines = params.get('min_scanned_lines')

            if not file_path:
                return ToolResult(success=False, tool_name='read_chunks_until_scope', error='file_path est requis')

            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            file_ext = os.path.splitext(file_path)[1].lower()
            is_python = file_ext == '.py'
            if prefer_balanced_end is None:
                prefer_balanced_end = is_python
            if min_scanned_lines is None:
                min_scanned_lines = 3 if is_python else 1

            scope_result = await self._detect_scope_boundaries(
                lines, start_line, scope_type, max_chunks,
                debug_mode=debug_mode, prefer_balanced_end=prefer_balanced_end, is_python=is_python,
                min_scanned_lines=min_scanned_lines
            )
            scope_content = self._extract_scope_content(lines, scope_result)

            # AST validation (non-invasive): validate snippet and optionally file
            ast_valid, ast_issues, ast_notes = self._validate_python_ast("\n".join(lines), scope_content)
            if ast_issues:
                scope_result.setdefault('issues', []).extend([iss for iss in ast_issues if iss not in scope_result.get('issues', [])])
            scope_result['ast_valid'] = ast_valid

            analysis = None
            if include_analysis:
                analysis = await self._analyze_scope_with_llm(scope_content, scope_type)

            # LLM fallback if scope seems invalid and analysis is allowed
            fallback_used = None
            if include_analysis and not scope_result.get('valid', True):
                guess = await self._llm_guess_boundaries(lines, start_line, scope_type, is_python)
                if guess and guess.get('end_line') and guess['end_line'] > scope_result['end_line']:
                    scope_result['end_line'] = guess['end_line']
                    scope_content = self._extract_scope_content(lines, scope_result)
                    fallback_used = 'llm_guess_boundaries'

            fractal_result = await self._create_fractal_scope_result(file_path, scope_content, scope_result, analysis)

            return ToolResult(
                success=True,
                tool_name='read_chunks_until_scope',
                data={
                    'file_path': file_path,
                    'scope_content': scope_content,
                    'scope_boundaries': scope_result,
                    'analysis': analysis,
                    'fractal_result': fractal_result,
                    'scope_type': scope_type,
                    'lines_read': scope_result['end_line'] - scope_result['start_line'] + 1
                },
                execution_time=time.time() - start_time,
                metadata={
                    'debug': scope_result.get('debug_trace') if debug_mode else None,
                    'prefer_balanced_end': prefer_balanced_end,
                    'min_scanned_lines': min_scanned_lines,
                    'fallback_used': fallback_used,
                    'ast_notes': ast_notes,
                }
            )
        except Exception as e:
            return ToolResult(success=False, tool_name='read_chunks_until_scope', error=str(e), execution_time=time.time() - start_time)

    async def _detect_scope_boundaries(self, lines: List[str], start_line: int,
                                     scope_type: str, max_chunks: int,
                                     debug_mode: bool = False,
                                     prefer_balanced_end: bool = False,
                                     is_python: bool = False,
                                     min_scanned_lines: int = 1) -> Dict[str, Any]:
        """Détecte les limites du scope."""
        current_line = start_line
        scope_start = start_line
        scope_end = start_line
        indent_level = 0
        bracket_count = 0
        brace_count = 0
        paren_count = 0

        scope_patterns = self.scope_detector.get_scope_patterns(scope_type)
        debug_trace = [] if debug_mode else None
        end_reason = None
        end_pattern = None
        issues: List[str] = []

        started_on_start_pattern = False
        try:
            line0 = lines[start_line - 1] if 0 <= start_line - 1 < len(lines) else ''
            for p in scope_patterns.get('start_patterns', []):
                if re.search(p, line0):
                    started_on_start_pattern = True
                    break
        except Exception:
            pass
        base_indent = self._calculate_indent_level(lines[start_line - 1]) if 0 <= start_line - 1 < len(lines) else 0
        start_indent = base_indent

        max_index = min(len(lines), start_line + max_chunks * 50)
        last_non_blank_line = scope_start

        # Backward header search for Python: always find nearest preceding def/class (with decorators)
        scan_start_index = start_line - 1
        if is_python:
            header_idx = None
            j = start_line - 1
            header_re = re.compile(r"^\s*(def|async\s+def|class)\s+",
                                   re.IGNORECASE)
            while j - 1 >= 0:
                prev = lines[j - 1]
                if header_re.search(prev):
                    header_idx = j - 1
                    # include contiguous decorators above
                    k = header_idx - 1
                    while k >= 0 and re.match(r"^\s*@\w", lines[k]):
                        header_idx = k
                        k -= 1
                    break
                # stop if we reach a less-indented non-empty line that looks like a sibling header
                # For robustness, do not stop early; only break at file start or after finding header
                j -= 1
            if header_idx is not None:
                scope_start = header_idx + 1
                started_on_start_pattern = True
                start_indent = self._calculate_indent_level(lines[header_idx])
                base_indent = start_indent
                last_non_blank_line = scope_start
                scan_start_index = header_idx
            else:
                # If no header found above, keep original start but treat as mid-scope (invalid if too short)
                started_on_start_pattern = False

        seen_body = False
        for i in range(scan_start_index, max_index):
            line = lines[i]
            line_num = i + 1

            indent_level = self._calculate_indent_level(line)
            bracket_count += line.count('[') - line.count(']')
            brace_count += line.count('{') - line.count('}')
            paren_count += line.count('(') - line.count(')')

            # Only consider lines inside the current scope as candidates for last_non_blank_line
            # For Python, a line is inside the scope if it is non-blank and its indentation is
            # strictly greater than the start indent (body), or it's the start line itself.
            if line.strip():
                if is_python:
                    if line_num == scope_start or indent_level > start_indent:
                        last_non_blank_line = line_num
                        if indent_level > start_indent:
                            seen_body = True
                else:
                    last_non_blank_line = line_num

            # With Python header recentered above, follow normal end checks; for non-Python, keep pattern end logic
            if is_python:
                matched = False  # rely on indentation-based end below
            else:
                matched = self._is_scope_end(line, scope_patterns, indent_level, bracket_count, brace_count, paren_count)

            # Python indentation-based end: when we see a non-comment, non-blank line whose
            # indentation is less than or equal to the start indent (and not the start line),
            # we consider the current scope closed just before this line.
            if is_python and started_on_start_pattern:
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and line_num != scope_start:
                    # Only allow termination after body has been seen; prevents decorator/def header from closing immediately
                    if seen_body and indent_level <= start_indent:
                        matched = True
            # Do not terminate immediately on the starting line for Python 'def'/'class'
            if line_num == start_line and started_on_start_pattern and is_python:
                matched = False
            if is_python and prefer_balanced_end and not started_on_start_pattern:
                if isinstance(matched, str) and re.search(r"^\s*(return|break|continue)\b", line):
                    matched = False
                if (bracket_count == 0 and brace_count == 0 and paren_count == 0 and indent_level <= base_indent and line.strip()):
                    matched = True
            if debug_mode:
                debug_trace.append({'line_num': line_num, 'indent': indent_level, 'brackets': bracket_count, 'braces': brace_count, 'parens': paren_count, 'matched_end': bool(matched)})
            # Enforce minimum scan window when starting mid-scope
            if matched and not started_on_start_pattern and (line_num - start_line + 1) < max(1, min_scanned_lines):
                matched = False

            if matched:
                # Prefer indentation-based end for Python scopes: the scope ends when indentation returns
                # to the start indent (or less) on a non-blank line, meaning the next top-level construct begins.
                # Therefore, we do not include the current line (belongs to the next construct).
                # Close at the last non-blank line inside the scope.
                if is_python:
                    # Use exclusive end bound (one past last non-blank in-body line)
                    scope_end_candidate = max(scope_start, last_non_blank_line)
                    if scope_end_candidate == line_num and last_non_blank_line == line_num:
                        scope_end_candidate = max(scope_start, line_num - 1)
                    scope_end = scope_end_candidate + 1
                    end_reason = 'indent_out'
                    end_pattern = None
                else:
                    if isinstance(matched, str):
                        scope_end = line_num
                        end_reason = 'pattern'
                        end_pattern = matched
                    else:
                        scope_end = max(scope_start, last_non_blank_line)
                        if scope_end == line_num and last_non_blank_line == line_num:
                            scope_end = max(scope_start, line_num - 1)
                        end_reason = 'balanced_root_nonempty'
                        end_pattern = None
                end_pattern = matched if isinstance(matched, str) else None
                break

            scope_end = line_num

        # If we reached EOF or scan limit without a dedent and we saw body, mark as unterminated for Python
        if end_reason is None and is_python and started_on_start_pattern and seen_body:
            # do not move scope_end further; it's already at last scanned
            if debug_trace is not None:
                debug_trace.append({'note': 'eof_without_dedent'})
            # mark as invalid; caller can still use the partial
            # we do not append below_min_scanned_lines here; it's a different issue
            # issues list declared above
            issues.append('unterminated_scope_eof')

        valid = True
        if end_reason == 'pattern' and is_python and prefer_balanced_end and not started_on_start_pattern:
            valid = False
            issues.append('ended_by_pattern_mid_scope')
        if (brace_count != 0 or bracket_count != 0 or paren_count != 0):
            valid = False
            issues.append('unbalanced_delimiters')
        result_len = (scope_end - scope_start + 1)
        # En mode Python en démarrant au milieu d'un scope, on exige une fenêtre minimale inclusive
        if not started_on_start_pattern and is_python and prefer_balanced_end and result_len <= max(1, min_scanned_lines):
            valid = False
            issues.append('below_min_scanned_lines')

        result = {
            'start_line': scope_start,
            'end_line': scope_end,
            'indent_level': indent_level,
            'bracket_count': bracket_count,
            'brace_count': brace_count,
            'paren_count': paren_count,
            'scope_type': scope_type,
            'scanned_lines': (scope_end - scope_start + 1),
            'end_reason': end_reason,
            'end_pattern': end_pattern,
            'started_on_start_pattern': started_on_start_pattern,
            'valid': valid,
            'issues': issues
        }
        if debug_mode:
            result['debug_trace'] = debug_trace
        return result

    async def _llm_guess_boundaries(self, lines: List[str], start_line: int, scope_type: str, is_python: bool) -> Optional[Dict[str, int]]:
        """Demande au LLM de proposer une fin de scope, budget très court.
        Retourne {'end_line': int} ou None.
        """
        if not hasattr(self.llm_provider, 'generate_text') and not hasattr(self.llm_provider, 'generate_response'):
            return None
        snippet = ''.join(lines[start_line-1:start_line-1+80])
        prompt = (
            "Tu es un assistant pour détecter les bornes de scope.\n"
            f"Langage: {'python' if is_python else 'unknown'}; Type: {scope_type}.\n"
            f"Texte (80 lignes max) à partir de la ligne {start_line}:\n{snippet}\n\n"
            "Propose un numéro de ligne de fin plausible (absolu), format strict: END_LINE: <nombre>."
        )
        try:
            if hasattr(self.llm_provider, 'generate_text'):
                resp = await self.llm_provider.generate_text(prompt, max_tokens=30)
                text = getattr(resp, 'content', '')
            else:
                resp = await self.llm_provider.generate_response(prompt, max_tokens=30)
                text = getattr(resp, 'content', resp)
            import re as _re
            m = _re.search(r"END_LINE:\s*(\d+)", text or '')
            if m:
                return {'end_line': int(m.group(1))}
        except Exception:
            return None
        return None

    def _calculate_indent_level(self, line: str) -> int:
        """Calcule le niveau d'indentation."""
        stripped = line.lstrip()
        if not stripped:
            return 0
        return len(line) - len(stripped)

    def _is_scope_end(self, line: str, scope_patterns: Dict, indent_level: int,
                      bracket_count: int, brace_count: int, paren_count: int):
        """Détermine si c'est la fin d'un scope."""
        if bracket_count == 0 and brace_count == 0 and paren_count == 0:
            if indent_level == 0 and line.strip():
                return True
        for pattern in scope_patterns.get('end_patterns', []):
            if re.search(pattern, line):
                return pattern
        return False

    def _extract_scope_content(self, lines: List[str], scope_result: Dict) -> str:
        """Extrait le contenu du scope."""
        start = scope_result['start_line'] - 1
        end = scope_result['end_line']
        scope_lines = lines[start:end]
        return ''.join(scope_lines)

    def _validate_python_ast(self, file_text: str, snippet: str) -> (bool, List[str], List[str]):
        """Validate Python AST for snippet (and optionally file). Returns (ast_valid, issues, notes)."""
        issues: List[str] = []
        notes: List[str] = []

        # Quick tokenizer check for snippet
        try:
            _ = list(tokenize.generate_tokens(io.StringIO(snippet).readline))
        except Exception as e:
            issues.append('unterminated_string')
            notes.append(f'tokenize_error: {e}')

        # Try raw parse of snippet (notes only; do not wrap, do not add issues here)
        ast_valid = True
        try:
            ast.parse(snippet)
        except Exception as e:
            ast_valid = False
            notes.append(f'ast_invalid_snippet: {getattr(e, "msg", str(e))} @ line {getattr(e, "lineno", "?")}')

        # Optional: file-level parse to surface file-wide issues (do not change ast_valid flag of snippet)
        try:
            ast.parse(file_text)
        except SyntaxError as e:
            notes.append(f'file_ast_invalid: {e.msg} @ line {e.lineno}')

        return ast_valid, issues, notes

    async def _analyze_scope_with_llm(self, scope_content: str, scope_type: str) -> Dict[str, Any]:
        """Analyse le scope avec LLM."""
        prompt = f"""
        Analyse ce bloc de code et fournis :
        1. Type de scope détecté
        2. Fonctionnalité principale
        3. Variables et fonctions définies
        4. Complexité estimée
        5. Suggestions d'amélioration
        
        Scope type: {scope_type}
        Contenu:
        {scope_content}
        """

        try:
            # Supporte generate_response OU generate_text
            call_resp = None
            if hasattr(self.llm_provider, 'generate_response'):
                call_resp = await getattr(self.llm_provider, 'generate_response')(prompt)
            elif hasattr(self.llm_provider, 'generate_text'):
                call_resp = await getattr(self.llm_provider, 'generate_text')(prompt, max_tokens=200)
            else:
                call_resp = ""
            text = getattr(call_resp, 'content', call_resp)
            return self._parse_llm_analysis(str(text))
        except Exception as e:
            return {
                'error': f"Erreur d'analyse LLM: {str(e)}",
                'scope_type': scope_type,
                'content_length': len(scope_content)
            }

    def _parse_llm_analysis(self, llm_response: str) -> Dict[str, Any]:
        """Parse la réponse LLM."""
        analysis = {
            'scope_type': 'unknown',
            'functionality': 'unknown',
            'variables': [],
            'functions': [],
            'complexity': 'unknown',
            'suggestions': []
        }
        patterns = {
            'scope_type': r'Type de scope[:\s]+([^\n]+)',
            'functionality': r'Fonctionnalité[:\s]+([^\n]+)',
            'complexity': r'Complexité[:\s]+([^\n]+)'
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, llm_response, re.IGNORECASE)
            if match:
                analysis[key] = match.group(1).strip()
        return analysis

    async def _create_fractal_scope_result(self, file_path: str, scope_content: str,
                                         scope_result: Dict, analysis: Dict) -> Dict[str, Any]:
        """Crée un résultat fractal pour le scope."""
        scope_node = await self.temporal_engine.create_temporal_node(
            node_type="scope",
            content=scope_content,
            metadata={
                'file_path': file_path,
                'start_line': scope_result['start_line'],
                'end_line': scope_result['end_line'],
                'scope_type': scope_result['scope_type'],
                'analysis': analysis,
                'indent_level': scope_result['indent_level'],
                'lines_count': scope_result['end_line'] - scope_result['start_line'] + 1
            }
        )
        return {
            'node_id': scope_node.node_id,
            'scope_type': scope_result['scope_type'],
            'boundaries': {
                'start': scope_result['start_line'],
                'end': scope_result['end_line']
            },
            'analysis': analysis,
            'content_preview': scope_content[:200] + "..." if len(scope_content) > 200 else scope_content
        }


class _MockLLMProvider:
    """MOCK ONLY – remplaçable par un provider réel via DI."""
    def __init__(self):
        self.provider_type = getattr(ProviderType, 'LOCAL', 'local')
    async def generate_response(self, prompt: str, **kwargs) -> str:
        return f"MOCK: {prompt[:120]}..."
    async def generate_text(self, prompt: str, **kwargs):
        class _R: content = f"MOCK: {prompt[:120]}..."
        return _R()
    async def test_connection(self):
        return {"valid": True, "provider_type": "mock"}
    

class V10ScopeDetector:
    """Détecteur de scopes pour différents langages."""
    
    def __init__(self):
        self.scope_patterns = {
            'auto': {
                'start_patterns': [
                    r'^\s*(def|class|if|for|while|try|with|async def)\s+',
                    r'^\s*\{',
                    r'^\s*\[',
                    r'^\s*\('
                ],
                'end_patterns': [
                    r'^\s*$',  # Ligne vide
                    r'^\s*#',   # Commentaire
                    r'^\s*return\s+',
                    r'^\s*break\s*$',
                    r'^\s*continue\s*$'
                ]
            },
            'function': {
                'start_patterns': [
                    r'^\s*def\s+\w+\s*\(',
                    r'^\s*async\s+def\s+\w+\s*\(',
                    r'^\s*function\s+\w+\s*\(',
                    r'^\s*public\s+\w+\s+\w+\s*\(',
                    r'^\s*private\s+\w+\s+\w+\s*\('
                ],
                'end_patterns': [
                    # For Python, avoid premature termination on 'return' inside branches.
                    # Prefer indentation-based end at next top-level non-empty.
                ]
            },
            'class': {
                'start_patterns': [
                    r'^\s*class\s+\w+',
                    r'^\s*public\s+class\s+\w+',
                    r'^\s*private\s+class\s+\w+'
                ],
                'end_patterns': [
                    # Similarly, end via indentation-based heuristic
                ]
            },
            'block': {
                'start_patterns': [
                    r'^\s*if\s+',
                    r'^\s*for\s+',
                    r'^\s*while\s+',
                    r'^\s*try\s*:',
                    r'^\s*with\s+',
                    r'^\s*\{',
                    r'^\s*\['
                ],
                'end_patterns': [
                    r'^\s*else\s*:',
                    r'^\s*elif\s+',
                    r'^\s*except\s+',
                    r'^\s*finally\s*:',
                    r'^\s*\}',
                    r'^\s*\]'
                ]
            }
        }
    
    def get_scope_patterns(self, scope_type: str) -> Dict[str, List[str]]:
        """Retourne les patterns pour un type de scope."""
        return self.scope_patterns.get(scope_type, self.scope_patterns['auto'])


# Interface principale pour les outils spécialisés
class V10SpecializedToolsRegistry:
    """Registre des outils spécialisés V10."""
    
    def __init__(self):
        # Charger l'environnement (pour les clés Gemini/OpenAI)
        try:
            # load_project_environment peut être sync dans notre implémentation
            env_vars = load_project_environment()
        except Exception:
            env_vars = {}

        # Préparer un provider LLM si disponible
        llm_provider_instance = None
        try:
            mode = get_llm_mode()
            if ProviderFactory is not None and mode != "mock":
                provider_type = {
                    "gemini": "gemini",
                    "openai": "openai",
                    "local_http": "local",
                    "local_subprocess": "local_subprocess",
                }.get(mode, "gemini")
                default_cfg = ProviderFactory.create_default_config(provider_type)
                import asyncio as _aio
                loop = _aio.get_event_loop()
                if loop.is_running():
                    # Ne pas bloquer une boucle déjà active (ex: tests async). Le provider sera None.
                    llm_provider_instance = None
                else:
                    llm_provider_instance, validation = loop.run_until_complete(
                        ProviderFactory.create_and_validate_provider(provider_type, **default_cfg)
                    )
                    if not validation.valid:
                        # Si non valide: seulement fallback mock si autorisé explicitement
                        llm_provider_instance = None
                        if not allow_mock_fallback():
                            raise RuntimeError(f"Provider LLM invalide: {validation.error}")
        except Exception as e:
            # En mode strict (pas de fallback), propager l'erreur lors du premier usage de l'outil
            if not allow_mock_fallback():
                # Enregistre un placeholder qui soulèvera une erreur à l'exécution
                class _FailingProvider:
                    async def generate_text(self, *a, **k):
                        raise RuntimeError(f"LLM provider indisponible: {e}")
                    async def generate_response(self, *a, **k):
                        raise RuntimeError(f"LLM provider indisponible: {e}")
                llm_provider_instance = _FailingProvider()
            else:
                llm_provider_instance = None

        # Initialiser un TemporalEngine sécurisé
        try:
            temporal_engine_instance = TemporalEngine(
                backend_type="filesystem",
                base_path='.',
                enable_auto_improvement=False,
                enable_query_enrichment=False,
            )
        except Exception:
            class _DummyTemporalEngine:
                async def create_temporal_node(self, *args, **kwargs):
                    class _N:
                        node_id = "sim_scope_node"
                    return _N()
            temporal_engine_instance = _DummyTemporalEngine()

        self.tools = {
            'read_lines': V10ReadLinesTool(),
            'write_lines': V10WriteLinesTool(),
            'replace_lines': V10ReplaceLinesTool(),
            'summarize_chunk': V10SummarizeChunkTool(),
            'analyze_structure': V10AnalyzeStructureTool(),
            'create_index': V10CreateIndexTool(),
            'summarize_section': V10SummarizeSectionTool(),
            'read_chunks_until_scope': V10ReadChunksUntilScopeTool(temporal_engine_instance, llm_provider=llm_provider_instance),
        }
    
    def get_tool(self, tool_name: str):
        """Récupère un outil par nom."""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """Liste tous les outils disponibles."""
        return list(self.tools.keys())
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> ToolResult:
        """Exécute un outil par nom."""
        tool = self.get_tool(tool_name)
        if tool:
            return await tool.execute(params)
        else:
            return ToolResult(
                success=False,
                tool_name=tool_name,
                error=f"Outil non trouvé: {tool_name}"
            )


# Interface principale
async def execute_specialized_tool(tool_name: str, params: Dict[str, Any]) -> ToolResult:
    """Interface principale pour exécution d'outils spécialisés."""
    registry = V10SpecializedToolsRegistry()
    return await registry.execute_tool(tool_name, params)
