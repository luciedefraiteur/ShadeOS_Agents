"""
🌍 Registre des Langages et Partitionneurs

Gestionnaire central pour tous les partitionneurs selon la stratégie hybride.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
from typing import Dict, List, Optional, Type, Any
from .partition_schemas import PartitionResult, PartitioningError
from ..ast_partitioners.base_ast_partitioner import BaseASTPartitioner
from ..ast_partitioners.python_ast_partitioner import PythonASTPartitioner
from ..ast_partitioners.tree_sitter_partitioner import TreeSitterPartitioner, TREE_SITTER_AVAILABLE
from ..fallback_strategies import (
    RegexPartitioner,
    TextualPartitioner,
    EmergencyPartitioner
)
from ..handlers.error_logger import log_partitioning_error, log_partitioning_warning


class LanguageRegistry:
    """Registre central des partitionneurs par langage."""
    
    def __init__(self):
        self.partitioners: Dict[str, BaseASTPartitioner] = {}
        self.language_mappings: Dict[str, str] = {}
        self.extension_mappings: Dict[str, str] = {}
        self.languages: Dict[str, Dict[str, Any]] = {}  # Attribut pour les tests
        self._init_default_mappings()
        self._init_default_partitioners()
    
    def _init_default_mappings(self):
        """Initialise les mappings par défaut."""
        
        # Mapping extensions -> langages
        self.extension_mappings = {
            # Python
            '.py': 'python',
            '.pyw': 'python', 
            '.pyi': 'python',
            
            # JavaScript
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.mjs': 'javascript',
            
            # TypeScript
            '.ts': 'typescript',
            '.tsx': 'typescript',
            
            # Rust
            '.rs': 'rust',
            
            # Go
            '.go': 'go',
            
            # C/C++
            '.c': 'c',
            '.h': 'c',
            '.cpp': 'cpp',
            '.cxx': 'cpp',
            '.cc': 'cpp',
            '.hpp': 'cpp',
            
            # Java
            '.java': 'java',
            
            # Autres langages
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.cs': 'csharp',
            '.fs': 'fsharp',
            '.hs': 'haskell',
            '.ml': 'ocaml',
            '.elm': 'elm'
        }
        
        # Mapping noms -> langages canoniques
        self.language_mappings = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'rs': 'rust',
            'rb': 'ruby',
            'kt': 'kotlin',
            'cs': 'csharp',
            'fs': 'fsharp',
            'hs': 'haskell',
            'ml': 'ocaml'
        }
    
    def _init_default_partitioners(self):
        """Initialise les partitionneurs par défaut selon la stratégie hybride."""
        
        # Python : Version Alma complète (Étape 3)
        try:
            self.partitioners['python'] = PythonASTPartitioner()
            log_partitioning_warning(
                "partitioner_init",
                "Python partitioner initialized (Alma native)",
                "language_registry"
            )
        except Exception as e:
            log_partitioning_error(
                "python_partitioner_init_error",
                f"Failed to initialize Python partitioner: {e}",
                "language_registry",
                exception=e
            )
        
        # Autres langages : Tree-sitter universel (Étape 1)
        if TREE_SITTER_AVAILABLE:
            tree_sitter_languages = [
                'javascript', 'typescript', 'rust', 'go', 'cpp', 'c', 
                'java', 'ruby', 'php', 'swift', 'kotlin'
            ]
            
            for language in tree_sitter_languages:
                try:
                    self.partitioners[language] = TreeSitterPartitioner(language)
                    log_partitioning_warning(
                        "partitioner_init",
                        f"{language} partitioner initialized (Tree-sitter)",
                        "language_registry"
                    )
                except Exception as e:
                    log_partitioning_warning(
                        "tree_sitter_partitioner_warning",
                        f"Failed to initialize Tree-sitter for {language}: {e}",
                        "language_registry"
                    )
        else:
            log_partitioning_warning(
                "tree_sitter_unavailable",
                "Tree-sitter not available, only Python partitioner will work",
                "language_registry"
            )
    
    def detect_language(self, file_path: str, content: Optional[str] = None) -> str:
        """Détecte le langage d'un fichier."""
        
        # Détection par extension
        _, ext = os.path.splitext(file_path.lower())
        if ext in self.extension_mappings:
            return self.extension_mappings[ext]
        
        # Détection par contenu si fourni
        if content:
            detected = self._detect_language_by_content(content)
            if detected:
                return detected
        
        # Détection par nom de fichier
        filename = os.path.basename(file_path).lower()
        if filename in ['makefile', 'dockerfile', 'rakefile']:
            return filename
        
        return 'unknown'
    
    def _detect_language_by_content(self, content: str) -> Optional[str]:
        """Détecte le langage par analyse du contenu."""
        if not content:
            return None
        
        # Détection Python
        python_indicators = [
            'def ', 'class ', 'import ', 'from ', 'if __name__', 
            'print(', 'return ', 'self.', 'async def', 'await ',
            'try:', 'except:', 'finally:', 'with ', 'for ', 'while ',
            'lambda ', 'yield ', 'raise ', 'assert '
        ]
        
        content_lower = content.lower()
        python_score = sum(1 for indicator in python_indicators if indicator in content_lower)
        
        if python_score >= 2:  # Au moins 2 indicateurs Python
            return 'python'
        
        # Détection JavaScript/TypeScript
        js_indicators = [
            'function ', 'const ', 'let ', 'var ', 'console.log',
            'export ', 'import ', '=>', 'async function', 'await ',
            'class ', 'extends ', 'new ', 'this.', 'prototype'
        ]
        
        js_score = sum(1 for indicator in js_indicators if indicator in content_lower)
        
        if js_score >= 2:
            return 'javascript'
        
        # Détection Rust
        rust_indicators = [
            'fn ', 'let ', 'mut ', 'pub ', 'struct ', 'enum ',
            'impl ', 'trait ', 'use ', 'mod ', 'extern crate',
            'unsafe ', 'match ', 'if let', 'while let'
        ]
        
        rust_score = sum(1 for indicator in rust_indicators if indicator in content_lower)
        
        if rust_score >= 2:
            return 'rust'
        
        # Détection Go
        go_indicators = [
            'func ', 'package ', 'import ', 'var ', 'const ',
            'type ', 'struct ', 'interface ', 'go ', 'defer ',
            'select ', 'case ', 'default:', 'chan ', 'map['
        ]
        
        go_score = sum(1 for indicator in go_indicators if indicator in content_lower)
        
        if go_score >= 2:
            return 'go'
        
        return None
    
    def get_partitioner(self, language: str) -> Optional[BaseASTPartitioner]:
        """Récupère le partitionneur pour un langage."""
        
        # Normalisation du nom du langage
        normalized_language = self.language_mappings.get(language.lower(), language.lower())
        
        return self.partitioners.get(normalized_language)
    
    def partition_file(self, file_path: str, content: str, 
                      language: Optional[str] = None) -> PartitionResult:
        """Partitionne un fichier selon son langage."""
        
        # Détection du langage si non fourni
        if not language:
            language = self.detect_language(file_path, content)
        
        # Récupération du partitionneur
        partitioner = self.get_partitioner(language)
        
        if not partitioner:
            # Cascade de fallbacks intelligente
            partitioner = self._get_fallback_partitioner(language, file_path)
        
        # Partitionnement
        try:
            # Adaptation selon le type de partitionneur
            if isinstance(partitioner, (RegexPartitioner, TextualPartitioner, EmergencyPartitioner)):
                # Les fallbacks ont besoin du langage
                result = partitioner.partition(content, file_path, language)
            else:
                # Les partitionneurs AST classiques
                result = partitioner.partition(content, file_path)

            result.metadata['detected_language'] = language
            result.metadata['partitioner_type'] = type(partitioner).__name__
            return result
        except Exception as e:
            log_partitioning_error(
                "partitioning_failed",
                f"Partitioning failed for {language}: {e}",
                file_path,
                details=str(e)
            )
            raise

    def _get_fallback_partitioner(self, language: str, file_path: str) -> BaseASTPartitioner:
        """Obtient un partitionneur de fallback selon la cascade intelligente."""

        # Niveau 1 : Tree-sitter (si disponible et langage supporté)
        if TREE_SITTER_AVAILABLE and language != 'unknown':
            try:
                partitioner = TreeSitterPartitioner(language)
                log_partitioning_warning(
                    "fallback_tree_sitter",
                    f"Using Tree-sitter fallback for {language}",
                    file_path
                )
                return partitioner
            except Exception as e:
                log_partitioning_warning(
                    "tree_sitter_fallback_failed",
                    f"Tree-sitter fallback failed for {language}: {e}",
                    file_path
                )

        # Niveau 2 : Regex Partitioner
        try:
            partitioner = RegexPartitioner()
            log_partitioning_warning(
                "fallback_regex",
                f"Using Regex fallback for {language}",
                file_path
            )
            return partitioner
        except Exception as e:
            log_partitioning_warning(
                "regex_fallback_failed",
                f"Regex fallback failed: {e}",
                file_path
            )

        # Niveau 3 : Textual Partitioner
        try:
            partitioner = TextualPartitioner()
            log_partitioning_warning(
                "fallback_textual",
                f"Using Textual fallback for {language}",
                file_path
            )
            return partitioner
        except Exception as e:
            log_partitioning_warning(
                "textual_fallback_failed",
                f"Textual fallback failed: {e}",
                file_path
            )

        # Niveau 4 : Emergency Partitioner (ne peut jamais échouer)
        partitioner = EmergencyPartitioner()
        log_partitioning_warning(
            "fallback_emergency",
            f"Using Emergency fallback for {language} (guaranteed success)",
            file_path
        )
        return partitioner

    def register_partitioner(self, language: str, partitioner: BaseASTPartitioner):
        """Enregistre un partitionneur personnalisé."""
        self.partitioners[language.lower()] = partitioner
        log_partitioning_warning(
            "custom_partitioner_registered",
            f"Custom partitioner registered for {language}",
            "language_registry"
        )
    
    def register_language(self, language: str, partitioner: BaseASTPartitioner, 
                          extensions: List[str] = None, aliases: List[str] = None,
                          fallback: str = None):
        """Enregistre un nouveau langage avec son partitionneur."""
        self.partitioners[language] = partitioner
        self.languages[language] = {
            'partitioner': partitioner,
            'extensions': extensions or [],
            'aliases': aliases or [],
            'fallback': fallback or 'textual'
        }
        
        # Enregistrer les extensions
        if extensions:
            for ext in extensions:
                self.extension_mappings[ext] = language
        
        # Enregistrer les alias
        if aliases:
            for alias in aliases:
                self.language_mappings[alias] = language
    
    def get_supported_languages(self) -> List[str]:
        """Retourne la liste des langages supportés."""
        return list(self.partitioners.keys())
    
    def get_supported_extensions(self) -> List[str]:
        """Retourne la liste des extensions supportées."""
        return list(self.extension_mappings.keys())
    
    def get_language_info(self, language: str) -> Dict[str, Any]:
        """Retourne les informations sur un langage."""
        
        partitioner = self.get_partitioner(language)
        if not partitioner:
            return {'supported': False}
        
        # Extensions supportées pour ce langage
        extensions = [ext for ext, lang in self.extension_mappings.items() 
                     if lang == language.lower()]
        
        return {
            'supported': True,
            'partitioner_type': type(partitioner).__name__,
            'extensions': extensions,
            'stage': self._get_language_stage(language),
            'capabilities': self._get_partitioner_capabilities(partitioner)
        }
    
    def _get_language_stage(self, language: str) -> str:
        """Détermine l'étape de développement du langage."""
        
        if language.lower() == 'python':
            return 'Stage 3 - Demonic Mastery (Alma Native)'
        elif language.lower() in ['javascript', 'typescript']:
            return 'Stage 1 - Universal Discovery (Tree-sitter)'
        else:
            return 'Stage 1 - Universal Discovery (Tree-sitter)'
    
    def _get_partitioner_capabilities(self, partitioner: BaseASTPartitioner) -> List[str]:
        """Analyse les capacités d'un partitionneur."""
        
        capabilities = ['basic_partitioning']
        
        if isinstance(partitioner, PythonASTPartitioner):
            capabilities.extend([
                'ast_analysis',
                'syntax_validation', 
                'class_hierarchy',
                'import_analysis',
                'complexity_analysis',
                'metadata_extraction'
            ])
        elif isinstance(partitioner, TreeSitterPartitioner):
            capabilities.extend([
                'universal_parsing',
                'error_recovery',
                'incremental_parsing'
            ])
        
        return capabilities
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Statistiques du registre."""
        
        total_languages = len(self.partitioners)
        python_partitioners = sum(1 for p in self.partitioners.values() 
                                 if isinstance(p, PythonASTPartitioner))
        tree_sitter_partitioners = sum(1 for p in self.partitioners.values() 
                                      if isinstance(p, TreeSitterPartitioner))
        
        return {
            'total_languages': total_languages,
            'python_partitioners': python_partitioners,
            'tree_sitter_partitioners': tree_sitter_partitioners,
            'supported_extensions': len(self.extension_mappings),
            'tree_sitter_available': TREE_SITTER_AVAILABLE
        }


# Instance globale du registre
global_language_registry = LanguageRegistry()


def partition_file(file_path: str, content: str = None, language: Optional[str] = None) -> PartitionResult:
    """Partitionne un fichier en utilisant le registre global."""
    if content is None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise PartitioningError(f"Impossible de lire le fichier {file_path}: {e}")
    
    return global_language_registry.partition_file(file_path, content, language)


def detect_language(file_path: str, content: Optional[str] = None) -> str:
    """Fonction utilitaire pour détecter un langage."""
    return global_language_registry.detect_language(file_path, content)


def get_supported_languages() -> List[str]:
    """Fonction utilitaire pour lister les langages supportés."""
    return global_language_registry.get_supported_languages()
