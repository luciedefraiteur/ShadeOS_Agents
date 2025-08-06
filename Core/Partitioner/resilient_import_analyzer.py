#!/usr/bin/env python3
"""
🔧 Resilient Import Analyzer - Analyseur d'imports résilient

Analyseur d'imports résilient aux dépendances brisées avec stratégies
de fallback et récupération automatique.

Auteur: Alma (via Lucie Defraiteur)
Date: 2025-08-06
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from datetime import datetime

from .broken_dependency_handler import BrokenDependencyHandler, get_broken_dependency_handler
from .import_analysis_cache import ImportAnalysisOptimizer, get_import_optimizer

logger = logging.getLogger(__name__)


class ResilientImportAnalyzer:
    """Analyseur d'imports résilient aux dépendances brisées"""
    
    def __init__(self, memory_engine=None):
        self.memory_engine = memory_engine
        self.broken_handler = get_broken_dependency_handler()
        self.import_optimizer = get_import_optimizer(memory_engine)
        self.fallback_strategies = [
            self._fallback_cached_analysis,
            self._fallback_partial_analysis,
            self._fallback_basic_analysis,
            self._fallback_skip_analysis
        ]
        
        logger.info("🔧 ResilientImportAnalyzer initialisé")
    
    async def analyze_imports_resilient(self, file_path: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Analyse résiliente des imports avec gestion des dépendances brisées"""
        
        if not os.path.exists(file_path):
            logger.warning(f"⚠️ Fichier non trouvé: {file_path}")
            return self._create_error_result(file_path, "file_not_found")
        
        # Vérifier si le fichier est en mode dégradé
        if self.broken_handler.is_in_degraded_mode(file_path):
            logger.info(f"⚠️ Analyse en mode dégradé pour {file_path}")
            return await self._handle_degraded_mode_analysis(file_path)
        
        try:
            # Tentative d'analyse normale
            logger.info(f"🔄 Analyse normale pour {file_path}")
            return await self.import_optimizer.get_or_analyze_imports(file_path, force_refresh)
            
        except ImportError as e:
            # Dépendance brisée détectée
            logger.warning(f"⚠️ ImportError détecté pour {file_path}: {e}")
            return await self._handle_import_error(file_path, e)
            
        except Exception as e:
            # Autre erreur
            logger.error(f"❌ Erreur d'analyse pour {file_path}: {e}")
            return await self._handle_general_error(file_path, e)
    
    async def _handle_import_error(self, file_path: str, error: ImportError) -> Dict[str, Any]:
        """Gère une erreur d'import spécifique"""
        
        # Extraire l'import brisé du message d'erreur
        broken_import = self._extract_broken_import_from_error(error)
        
        # Gérer la dépendance brisée
        handler_result = await self.broken_handler.handle_broken_import(file_path, broken_import, error)
        
        # Essayer les stratégies de fallback
        for fallback_strategy in self.fallback_strategies:
            try:
                result = await fallback_strategy(file_path, error)
                if result and result.get('success', False):
                    logger.info(f"✅ Fallback réussi pour {file_path}: {fallback_strategy.__name__}")
                    return result
            except Exception as fallback_error:
                logger.warning(f"⚠️ Fallback échoué {fallback_strategy.__name__}: {fallback_error}")
        
        # Dernier recours
        return self._emergency_fallback(file_path, error)
    
    async def _handle_general_error(self, file_path: str, error: Exception) -> Dict[str, Any]:
        """Gère une erreur générale d'analyse"""
        
        logger.error(f"❌ Erreur générale pour {file_path}: {error}")
        
        # Essayer les stratégies de fallback
        for fallback_strategy in self.fallback_strategies:
            try:
                result = await fallback_strategy(file_path, error)
                if result and result.get('success', False):
                    logger.info(f"✅ Fallback réussi pour {file_path}: {fallback_strategy.__name__}")
                    return result
            except Exception as fallback_error:
                logger.warning(f"⚠️ Fallback échoué {fallback_strategy.__name__}: {fallback_error}")
        
        # Dernier recours
        return self._emergency_fallback(file_path, error)
    
    async def _handle_degraded_mode_analysis(self, file_path: str) -> Dict[str, Any]:
        """Gère l'analyse en mode dégradé"""
        
        # Tenter la récupération
        recovery_success = await self.broken_handler.attempt_recovery(file_path)
        
        if recovery_success:
            # Récupération réussie, analyser normalement
            logger.info(f"✅ Récupération réussie pour {file_path}, analyse normale")
            return await self.analyze_imports_resilient(file_path)
        else:
            # Toujours en mode dégradé, utiliser le fallback
            logger.info(f"⚠️ Mode dégradé persistant pour {file_path}, utilisation du fallback")
            return await self._fallback_skip_analysis(file_path, None)
    
    def _extract_broken_import_from_error(self, error: ImportError) -> str:
        """Extrait l'import brisé du message d'erreur"""
        
        error_message = str(error)
        
        # Patterns courants pour les erreurs d'import
        import re
        import_patterns = [
            "No module named '(.+)'",
            "cannot import name '(.+)'",
            "ImportError: (.+)",
            "ModuleNotFoundError: (.+)"
        ]
        
        for pattern in import_patterns:
            match = re.search(pattern, error_message)
            if match:
                return match.group(1)
        
        # Fallback : utiliser le message d'erreur complet
        return error_message
    
    async def _fallback_cached_analysis(self, file_path: str, error: Exception) -> Optional[Dict[str, Any]]:
        """Fallback : utiliser l'analyse en cache même si ancienne"""
        
        try:
            # Forcer l'utilisation du cache même s'il est expiré
            cached_result = await self.import_optimizer.get_or_analyze_imports(file_path, force_refresh=False)
            
            if cached_result:
                return {
                    'success': True,
                    'result': cached_result,
                    'fallback_strategy': 'cached_analysis',
                    'warning': 'Using cached data due to broken dependencies'
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Fallback cached_analysis échoué pour {file_path}: {e}")
            return None
    
    async def _fallback_partial_analysis(self, file_path: str, error: Exception) -> Optional[Dict[str, Any]]:
        """Fallback : analyse partielle sans les imports brisés"""
        
        try:
            # Import local pour éviter les dépendances circulaires
            from .import_analyzer import ImportAnalyzer
            
            analyzer = ImportAnalyzer()
            
            # Analyser seulement le fichier lui-même, pas ses dépendances
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraction basique des imports
            imports = self._extract_imports_basic(content)
            
            # Créer un résultat partiel
            partial_result = {
                'file_path': file_path,
                'imports': imports,
                'analysis_type': 'partial',
                'warning': 'Partial analysis due to broken dependencies',
                'broken_dependencies': True
            }
            
            return {
                'success': True,
                'result': partial_result,
                'fallback_strategy': 'partial_analysis'
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Fallback partial_analysis échoué pour {file_path}: {e}")
            return None
    
    async def _fallback_basic_analysis(self, file_path: str, error: Exception) -> Optional[Dict[str, Any]]:
        """Fallback : analyse basique sans résolution d'imports"""
        
        try:
            # Analyse syntaxique simple
            basic_info = {
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'file_extension': Path(file_path).suffix,
                'analysis_type': 'basic',
                'warning': 'Basic analysis due to broken dependencies'
            }
            
            return {
                'success': True,
                'result': basic_info,
                'fallback_strategy': 'basic_analysis'
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Fallback basic_analysis échoué pour {file_path}: {e}")
            return None
    
    async def _fallback_skip_analysis(self, file_path: str, error: Exception) -> Dict[str, Any]:
        """Fallback : ignorer l'analyse pour ce fichier"""
        
        return {
            'success': True,
            'result': {
                'file_path': file_path,
                'analysis_skipped': True,
                'reason': 'broken_dependencies',
                'error': str(error) if error else 'Unknown error'
            },
            'fallback_strategy': 'skip_analysis'
        }
    
    def _emergency_fallback(self, file_path: str, error: Exception) -> Dict[str, Any]:
        """Dernier recours en cas d'échec total"""
        
        logger.error(f"❌ Échec total pour {file_path}, utilisation du fallback d'urgence")
        
        return {
            'success': False,
            'result': {
                'file_path': file_path,
                'emergency_mode': True,
                'error': str(error) if error else 'Unknown error',
                'basic_info': {
                    'exists': os.path.exists(file_path),
                    'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                    'extension': Path(file_path).suffix
                }
            },
            'fallback_strategy': 'emergency_fallback'
        }
    
    def _create_error_result(self, file_path: str, error_type: str) -> Dict[str, Any]:
        """Crée un résultat d'erreur standardisé"""
        
        return {
            'success': False,
            'result': {
                'file_path': file_path,
                'error_type': error_type,
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _extract_imports_basic(self, content: str) -> List[str]:
        """Extraction basique des imports sans résolution"""
        
        imports = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Imports standards
            if line.startswith('import ') or line.startswith('from '):
                # Nettoyer la ligne
                import_stmt = line.split('#')[0].strip()  # Enlever les commentaires
                if import_stmt:
                    imports.append(import_stmt)
        
        return imports
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques d'analyse résiliente"""
        
        broken_stats = self.broken_handler.get_statistics()
        
        return {
            'resilient_analyzer': {
                'fallback_strategies_count': len(self.fallback_strategies),
                'memory_engine_available': self.memory_engine is not None
            },
            'broken_dependencies': broken_stats
        }


# Instance globale pour faciliter l'utilisation
_global_resilient_analyzer: Optional[ResilientImportAnalyzer] = None

def get_resilient_import_analyzer(memory_engine=None) -> ResilientImportAnalyzer:
    """Retourne l'instance globale de l'analyseur résilient"""
    global _global_resilient_analyzer
    if _global_resilient_analyzer is None:
        _global_resilient_analyzer = ResilientImportAnalyzer(memory_engine)
    return _global_resilient_analyzer

def set_resilient_import_analyzer(analyzer: ResilientImportAnalyzer):
    """Définit l'instance globale de l'analyseur résilient"""
    global _global_resilient_analyzer
    _global_resilient_analyzer = analyzer 