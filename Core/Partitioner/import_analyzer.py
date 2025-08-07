#!/usr/bin/env python3
"""
🔍 Import Analyzer - Outil d'analyse des dépendances Python

Version complètement redesignée avec les découvertes récentes:
- Détection automatique des modules locaux (sans préfixage en dur)
- Cache intelligent pour les performances
- Résolution d'imports hybride (simple + ImportResolver)
- AST parsing avancé avec fallback
- Rapports Markdown détaillés avec arbres ASCII
- Debug intégré et logs détaillés
- Intégration avec TemporalFractalMemoryEngine

Auteur: Assistant IA (via Lucie Defraiteur)
Date: 2025-08-07
"""

import os
import sys
import json
import asyncio
import argparse
import time
import ast
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
from collections import defaultdict

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ImportAnalysisResult:
    """Résultat d'analyse d'imports pour un fichier"""
    
    file_path: str
    imports: List[str] = field(default_factory=list)
    local_imports: List[str] = field(default_factory=list)
    external_imports: List[str] = field(default_factory=list)
    standard_imports: List[str] = field(default_factory=list)
    unresolved_imports: List[str] = field(default_factory=list)
    dependency_depth: int = 0
    import_count: int = 0
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    error_messages: List[str] = field(default_factory=list)
    resolved_paths: Dict[str, str] = field(default_factory=dict)


@dataclass
class DependencyGraph:
    """Graphe de dépendances avec détection de cycles"""
    
    nodes: Dict[str, ImportAnalysisResult] = field(default_factory=dict)
    edges: List[tuple] = field(default_factory=list)
    cycles: List[List[str]] = field(default_factory=list)
    file_depths: Dict[str, int] = field(default_factory=dict)
    
    def add_node(self, file_path: str, analysis_result: ImportAnalysisResult):
        """Ajoute un nœud au graphe"""
        self.nodes[file_path] = analysis_result
    
    def add_edge(self, source: str, target: str):
        """Ajoute une arête au graphe"""
        self.edges.append((source, target))
    
    def detect_cycles(self) -> List[List[str]]:
        """Détecte les cycles dans le graphe de dépendances"""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]):
            if node in rec_stack:
                # Cycle détecté
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            # Parcourir les dépendances
            if node in self.nodes:
                for import_path in self.nodes[node].local_imports:
                    if import_path in self.nodes:
                        dfs(import_path, path.copy())
            
            rec_stack.remove(node)
            path.pop()
        
        # DFS sur tous les nœuds
        for node in self.nodes:
            if node not in visited:
                dfs(node, [])
        
        self.cycles = cycles
        return cycles


class SimpleImportAnalyzerLogger:
    """Logger simple et direct pour l'analyseur d'imports"""
    
    def __init__(self, project_root: str, log_dir: str = "logs/imports_analysis"):
        self.project_root = project_root
        self.log_dir = log_dir
        self.md_sections = []
        self.files_data = {}  # {relative_path: {imports: [], depth: int}}
        self.cycles_detected = []
        
        # Créer le répertoire de logs
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Fichier de log principal
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"import_analysis_{timestamp}.log")
        self.md_file = os.path.join(self.log_dir, "imports_analysis_report.md")
    
    def log_info(self, message: str):
        """Log un message d'information"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] INFO: {message}"
        print(log_entry)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def log_error(self, message: str):
        """Log une erreur"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] ERROR: {message}"
        print(log_entry)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def log_debug(self, message: str):
        """Log un message de debug"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] DEBUG: {message}"
        print(log_entry)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def log_performance_metrics(self, stats: Dict[str, Any]):
        """Log les métriques de performance"""
        duration = time.time() - stats['start_time']
        self.log_info(f"Performance - Durée: {duration:.2f}s, Fichiers: {stats.get('files_analyzed', 0)}")
    
    def _add_file_to_md_report(self, file_path: str, imports: List[str], depth: int):
        """Ajoute un fichier au rapport Markdown"""
        # Convertir en chemin relatif
        try:
            relative_path = os.path.relpath(file_path, self.project_root)
        except ValueError:
            relative_path = file_path
        
        # Stocker les données du fichier
        if relative_path in self.files_data:
            # Fusionner les imports et prendre la profondeur max
            existing_data = self.files_data[relative_path]
            existing_data['imports'].extend(imports)
            existing_data['imports'] = list(set(existing_data['imports']))  # Dédupliquer
            existing_data['depth'] = max(existing_data['depth'], depth)
        else:
            self.files_data[relative_path] = {
                'imports': imports.copy(),
                'depth': depth
            }
    
    def add_cycles_to_report(self, cycles: List[List[str]]):
        """Ajoute les cycles détectés au rapport"""
        self.cycles_detected = cycles
    
    def _generate_ascii_tree(self) -> str:
        """Génère un arbre ASCII de la structure des fichiers"""
        if not self.files_data:
            return "Aucun fichier analysé"
        
        tree_lines = ["📁 Structure des fichiers analysés:"]
        
        # Créer une structure hiérarchique
        hierarchy = defaultdict(list)
        for file_path in sorted(self.files_data.keys()):
            parts = file_path.split('/')
            current_level = hierarchy
            for i, part in enumerate(parts[:-1]):
                if part not in current_level:
                    current_level[part] = defaultdict(list)
                current_level = current_level[part]
            current_level[parts[-1]] = None
        
        def print_tree(node, prefix="", is_last=True):
            if isinstance(node, dict):
                items = sorted(node.items())
                for i, (name, child) in enumerate(items):
                    is_last_item = i == len(items) - 1
                    connector = "└── " if is_last_item else "├── "
                    tree_lines.append(f"{prefix}{connector}{name}/")
                    
                    new_prefix = prefix + ("    " if is_last_item else "│   ")
                    print_tree(child, new_prefix, is_last_item)
            elif node is not None:
                tree_lines.append(f"{prefix}└── {node}")
        
        print_tree(hierarchy)
        return "\n".join(tree_lines)
    
    def finalize_report(self, stats: Dict[str, Any]) -> str:
        """Finalise et génère le rapport Markdown complet"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        duration = time.time() - stats['start_time']
        
        # Section 1: Liste simple des fichiers
        simple_list = ["## 📋 Liste Simple des Fichiers Traversés\n"]
        for file_path in sorted(self.files_data.keys()):
            simple_list.append(f"- `{file_path}`")
        
        # Section 2: Arbre ASCII
        ascii_tree = ["## 🌳 Structure Hiérarchique\n"]
        ascii_tree.append(self._generate_ascii_tree())
        
        # Section 3: Imports simples
        simple_imports = ["## 📦 Imports Locaux Détectés\n"]
        for file_path, data in sorted(self.files_data.items()):
            if data['imports']:
                simple_imports.append(f"### {file_path}")
                simple_imports.append(f"*Profondeur: {data['depth']}*")
                for imp in sorted(data['imports']):
                    simple_imports.append(f"- `{imp}`")
                simple_imports.append("")
        
        # Section 4: Analyse détaillée
        detailed_analysis = ["## 🔍 Analyse Détaillée\n"]
        for file_path, data in sorted(self.files_data.items()):
            detailed_analysis.append(f"### {file_path}")
            detailed_analysis.append(f"- **Profondeur:** {data['depth']}")
            detailed_analysis.append(f"- **Imports locaux:** {len(data['imports'])}")
            if data['imports']:
                detailed_analysis.append("- **Liste des imports:**")
                for imp in sorted(data['imports']):
                    detailed_analysis.append(f"  - `{imp}`")
            detailed_analysis.append("")
        
        # Section 5: Cycles détectés
        cycles_section = ["## 🔄 Cycles de Dépendances\n"]
        if self.cycles_detected:
            for i, cycle in enumerate(self.cycles_detected, 1):
                cycles_section.append(f"### Cycle {i}")
                cycles_section.append(" → ".join([f"`{f}`" for f in cycle]))
                cycles_section.append("")
        else:
            cycles_section.append("Aucun cycle détecté.")
        
        # Assembler le rapport complet
        report = f"""# 📊 Rapport d'Analyse d'Imports

**Date:** {timestamp}  
**Project Root:** {self.project_root}  
**Durée d'analyse:** {duration:.2f}s  
**Fichiers analysés:** {len(self.files_data)}

---

{chr(10).join(simple_list)}

---

{chr(10).join(ascii_tree)}

---

{chr(10).join(simple_imports)}

---

{chr(10).join(detailed_analysis)}

---

{chr(10).join(cycles_section)}

---

*Rapport généré automatiquement par ImportAnalyzer v2.0*
"""
        
        # Sauvegarder le rapport
        with open(self.md_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report


class ImportAnalyzer:
    """Analyseur d'imports de production - Version redesignée"""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.dependency_graph = DependencyGraph()
        self.import_resolver = None
        self.max_depth = 10
        self.analyzed_files = set()
        
        # Cache pour les modules locaux détectés automatiquement
        self._local_modules_cache = {}
        
        # Initialiser l'import resolver si disponible
        try:
            from .import_resolver import ImportResolver
            self.import_resolver = ImportResolver()
            logger.info("✅ ImportResolver initialisé")
        except ImportError:
            logger.warning("⚠️ ImportResolver non disponible, utilisation du résolveur simple")
        
        # Initialiser le partitioner si disponible
        self.partitioner = None
        try:
            from .ast_partitioners.python_ast_partitioner import PythonASTPartitioner
            self.partitioner = PythonASTPartitioner()
            logger.info("✅ PythonASTPartitioner initialisé")
        except ImportError:
            logger.warning("⚠️ PythonASTPartitioner non disponible, utilisation du parsing AST simple")
        
        # Initialiser le logger
        self.logger = SimpleImportAnalyzerLogger(self.project_root)
        
        # Statistiques d'analyse
        self.stats = {
            'start_time': time.time(),
            'files_analyzed': 0,
            'local_imports': 0,
            'external_imports': 0,
            'cycles_detected': 0,
            'max_depth': 0,
            'duration': 0
        }
    
    def _is_local_module(self, import_name: str) -> bool:
        """Détecte automatiquement si un module est local au projet."""
        # Vérifier le cache d'abord
        if import_name in self._local_modules_cache:
            return self._local_modules_cache[import_name]
        
        try:
            # Extraire le premier niveau du module (ex: "Core" de "Core.LLMProviders")
            first_level = import_name.split('.')[0]
            
            # Vérifier si ce premier niveau existe comme dossier dans le projet
            module_path = os.path.join(self.project_root, first_level)
            
            is_local = False
            
            # Si c'est un dossier, c'est probablement un module local
            if os.path.isdir(module_path):
                # Vérifier qu'il contient des fichiers Python ou un __init__.py
                if (os.path.exists(os.path.join(module_path, '__init__.py')) or
                    any(f.endswith('.py') for f in os.listdir(module_path) if os.path.isfile(os.path.join(module_path, f)))):
                    is_local = True
            
            # Vérifier aussi si c'est un fichier Python direct
            module_file = os.path.join(self.project_root, first_level + '.py')
            if os.path.exists(module_file):
                is_local = True
            
            # Mettre en cache le résultat
            self._local_modules_cache[import_name] = is_local
            return is_local
                
        except (IndexError, OSError):
            # En cas d'erreur, considérer comme non local et mettre en cache
            self._local_modules_cache[import_name] = False
            return False
    
    def _extract_imports_enhanced(self, file_path: str) -> List[str]:
        """Extrait les imports avec le partitioner ou méthode simple améliorée"""
        try:
            # Utiliser le partitioner si disponible
            if self.partitioner:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                result = self.partitioner.parse_content(content, file_path)
                if result and hasattr(result, 'imports'):
                    imports = []
                    for imp in result.imports:
                        if hasattr(imp, 'name'):
                            imports.append(imp.name)
                        elif isinstance(imp, str):
                            imports.append(imp)
                    return imports
            
            # Fallback vers la méthode simple
            return self._extract_imports_simple(file_path)
                
        except Exception as e:
            self.logger.log_error(f"Erreur extraction imports {file_path}: {e}")
            return self._extract_imports_simple(file_path)
    
    def _get_package_from_path(self, file_path: str) -> str:
        """Détermine le package Python à partir du chemin du fichier."""
        try:
            # Convertir le chemin en chemin relatif au projet
            rel_path = os.path.relpath(file_path, self.project_root)
            
            # Supprimer l'extension .py
            if rel_path.endswith('.py'):
                rel_path = rel_path[:-3]
            
            # Remplacer les séparateurs de chemin par des points
            package = rel_path.replace(os.sep, '.')
            
            # Supprimer __init__ à la fin si présent
            if package.endswith('.__init__'):
                package = package[:-9]
            
            return package
            
        except Exception:
            return ""

    def _get_package_from_path(self, file_path: str) -> str:
        """Détermine le package Python à partir du chemin du fichier."""
        try:
            # Convertir le chemin en chemin relatif au projet
            rel_path = os.path.relpath(file_path, self.project_root)
            
            # Supprimer l'extension .py
            if rel_path.endswith('.py'):
                rel_path = rel_path[:-3]
            
            # Remplacer les séparateurs de chemin par des points
            package = rel_path.replace(os.sep, '.')
            
            # Supprimer __init__ à la fin si présent
            if package.endswith('.__init__'):
                package = package[:-9]
            
            return package
            
        except Exception:
            return ""

    def _extract_imports_simple(self, file_path: str) -> List[str]:
        """Extrait les imports d'un fichier Python avec une méthode simple."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = []
            
            # Déterminer le package du fichier courant
            current_package = self._get_package_from_path(file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        if module:
                            # Gérer les imports relatifs
                            if module.startswith('.'):
                                # Import relatif - reconstruire le chemin complet
                                relative_level = len(module) - len(module.lstrip('.'))
                                if relative_level == 1:
                                    # Import du même package
                                    full_module = f"{current_package}.{module[1:]}"
                                else:
                                    # Import d'un package parent
                                    package_parts = current_package.split('.')
                                    if len(package_parts) >= relative_level:
                                        parent_package = '.'.join(package_parts[:-relative_level+1])
                                        full_module = f"{parent_package}.{module[relative_level:]}"
                                    else:
                                        full_module = module[relative_level:]
                                
                                if alias.name == '*':
                                    imports.append(full_module)
                                else:
                                    imports.append(f"{full_module}.{alias.name}")
                            else:
                                # Import absolu
                                if alias.name == '*':
                                    imports.append(module)
                                else:
                                    imports.append(f"{module}.{alias.name}")
                        else:
                            imports.append(alias.name)
            
            return imports
            
        except Exception as e:
            self.logger.log_error(f"Erreur parsing AST {file_path}: {e}")
            return []
    
    def _resolve_import_simple(self, import_name: str, current_file: str) -> Optional[str]:
        """Résout un import de manière simple."""
        try:
            if import_name.startswith('.'):
                # Import relatif
                current_dir = os.path.dirname(os.path.abspath(current_file))
                
                # Compter les .. au début
                dots_count = len(import_name) - len(import_name.lstrip('.'))
                for _ in range(dots_count // 2):
                    current_dir = os.path.dirname(current_dir)
                
                # Convertir le reste en chemin
                rest = import_name[dots_count:].replace('.', '/')
                
                # Essayer d'abord le fichier .py direct
                candidate = os.path.normpath(os.path.join(current_dir, rest + '.py'))
                if os.path.exists(candidate):
                    return candidate
                
                # Si pas trouvé, essayer avec __init__.py
                candidate = os.path.normpath(os.path.join(current_dir, rest, '__init__.py'))
                if os.path.exists(candidate):
                    return candidate
                
                return None
            else:
                # Import absolu
                # Si c'est un import de classe, essayer de trouver le module
                parts = import_name.split('.')
                if len(parts) > 1:
                    module_path = '/'.join(parts[:-1])
                    module_file = os.path.join(self.project_root, module_path + '.py')
                    if os.path.exists(module_file):
                        return module_file
                    
                    module_init = os.path.join(self.project_root, module_path, '__init__.py')
                    if os.path.exists(module_init):
                        return module_init
                
                return None
                
        except Exception as e:
            self.logger.log_error(f"Erreur résolution import {import_name}: {e}")
            return None
    
    def _resolve_import_with_resolver(self, import_name: str, current_file: str) -> Optional[str]:
        """Résout un import avec l'ImportResolver avec timeout."""
        if not self.import_resolver:
            return None
        
        try:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Timeout lors de la résolution d'import")
            
            # Définir un timeout de 10 secondes
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(10)
            
            try:
                resolved_path = self.import_resolver.resolve_import(import_name, current_file)
                signal.alarm(0)  # Annuler le timeout
                return resolved_path
            except TimeoutError:
                self.logger.log_debug(f"Timeout résolution import: {import_name}")
                return None
            finally:
                signal.alarm(0)
                
        except Exception as e:
            self.logger.log_debug(f"Erreur ImportResolver {import_name}: {e}")
            return None
    
    def find_file_for_import(self, import_name: str, current_file: str) -> Optional[str]:
        """Trouve le fichier correspondant à un import (stratégie hybride)."""
        # Essayer d'abord avec l'ImportResolver
        resolved_path = self._resolve_import_with_resolver(import_name, current_file)
        if resolved_path:
            return resolved_path
        
        # Fallback vers la résolution simple
        return self._resolve_import_simple(import_name, current_file)
    
    def analyze_files(self, file_paths: List[str], max_depth: int = None, 
                     use_import_resolver: bool = True, debug: bool = False) -> Dict[str, Any]:
        """
        Analyse les dépendances d'une liste de fichiers
        
        Args:
            file_paths: Liste des chemins de fichiers à analyser
            max_depth: Profondeur maximale d'analyse (optionnel)
            use_import_resolver: Utiliser l'ImportResolver (défaut: True)
            debug: Mode debug avec logs détaillés
        
        Returns:
            Dict contenant les résultats d'analyse
        """
        if max_depth:
            self.max_depth = max_depth
        
        self.logger.log_info(f"🔍 Début de l'analyse de {len(file_paths)} fichiers")
        self.logger.log_info(f"   Project root: {self.project_root}")
        self.logger.log_info(f"   Max depth: {self.max_depth}")
        self.logger.log_info(f"   Import resolver: {'✅' if use_import_resolver and self.import_resolver else '❌'}")
        self.logger.log_info(f"   Partitioner: {'✅' if self.partitioner else '❌'}")
        
        # Analyser chaque fichier
        for file_path in file_paths:
            if os.path.exists(file_path):
                self._analyze_file_recursive(file_path, depth=0, visited=set(), debug=debug)
            else:
                self.logger.log_error(f"⚠️ Fichier non trouvé: {file_path}")
        
        # Détecter les cycles
        cycles = self.dependency_graph.detect_cycles()
        self.dependency_graph.cycles = cycles
        
        # Mettre à jour les statistiques
        self.stats['files_analyzed'] = len(self.dependency_graph.nodes)
        self.stats['cycles_detected'] = len(cycles)
        self.stats['max_depth'] = max(self.dependency_graph.file_depths.values()) if self.dependency_graph.file_depths else 0
        self.stats['duration'] = time.time() - self.stats['start_time']
        
        # Calculer les totaux d'imports
        total_imports = sum(len(node.imports) for node in self.dependency_graph.nodes.values())
        total_local = sum(len(node.local_imports) for node in self.dependency_graph.nodes.values())
        total_external = sum(len(node.external_imports) for node in self.dependency_graph.nodes.values())
        total_standard = sum(len(node.standard_imports) for node in self.dependency_graph.nodes.values())
        
        self.stats['total_imports'] = total_imports
        self.stats['local_imports'] = total_local
        self.stats['external_imports'] = total_external
        self.stats['standard_imports'] = total_standard
        
        # Ajouter les cycles au rapport
        self.logger.add_cycles_to_report(cycles)
        
        # Générer le rapport final
        report = self._generate_analysis_report(file_paths, cycles)
        
        self.logger.log_info(f"✅ Analyse terminée: {len(self.dependency_graph.nodes)} fichiers analysés")
        self.logger.log_performance_metrics(self.stats)
        
        return report
    
    def _analyze_file_recursive(self, file_path: str, depth: int = 0, visited: Set[str] = None, debug: bool = False):
        """Analyse récursive d'un fichier et de ses dépendances"""
        if visited is None:
            visited = set()
        
        # Éviter les cycles et respecter la profondeur maximale
        if depth > self.max_depth or file_path in visited:
            return
        
        visited.add(file_path)
        
        if debug:
            self.logger.log_debug(f"🔍 Analyse récursive: {file_path} (depth: {depth})")
        
        try:
            # Analyser le fichier
            analysis_result = self._analyze_single_file(file_path, debug)
            self.dependency_graph.add_node(file_path, analysis_result)
            self.dependency_graph.file_depths[file_path] = depth
            
            # Ajouter au rapport Markdown
            self.logger._add_file_to_md_report(file_path, analysis_result.local_imports, depth)
            
            # Analyser récursivement les imports locaux
            for import_name in analysis_result.local_imports:
                if debug:
                    self.logger.log_debug(f"   📦 Import local: {import_name}")
                
                # Trouver le fichier correspondant
                resolved_path = self.find_file_for_import(import_name, file_path)
                if resolved_path and resolved_path not in visited:
                    if debug:
                        self.logger.log_debug(f"   ✅ Résolu vers: {resolved_path}")
                    self._analyze_file_recursive(resolved_path, depth + 1, visited.copy(), debug)
                    self.dependency_graph.add_edge(file_path, resolved_path)
                elif debug and not resolved_path:
                    self.logger.log_debug(f"   ❌ Non résolu: {import_name}")
        
        except Exception as e:
            self.logger.log_error(f"❌ Erreur lors de l'analyse de {file_path}: {e}")
            error_result = ImportAnalysisResult(
                file_path=file_path,
                error_messages=[str(e)]
            )
            self.dependency_graph.add_node(file_path, error_result)
    
    def _analyze_single_file(self, file_path: str, debug: bool = False) -> ImportAnalysisResult:
        """Analyse un seul fichier"""
        result = ImportAnalysisResult(file_path=file_path)
        
        try:
            # Extraire les imports
            imports = self._extract_imports_enhanced(file_path)
            result.imports = imports
            result.import_count = len(imports)
            
            if debug:
                self.logger.log_debug(f"   📋 Imports extraits: {len(imports)}")
            
            # Classifier les imports
            for import_stmt in imports:
                if debug:
                    self.logger.log_debug(f"   🔍 Classification: {import_stmt}")
                
                if import_stmt.startswith('.'):
                    # Import relatif
                    result.local_imports.append(import_stmt)
                    if debug:
                        self.logger.log_debug(f"   ✅ Relatif local: {import_stmt}")
                elif self._is_local_module(import_stmt):
                    # Import local détecté automatiquement
                    result.local_imports.append(import_stmt)
                    if debug:
                        self.logger.log_debug(f"   ✅ Local détecté: {import_stmt}")
                else:
                    # Vérifier si c'est une bibliothèque standard
                    first_part = import_stmt.split('.')[0]
                    if first_part in {
                        'os', 'sys', 'json', 'pathlib', 'typing', 'dataclasses', 
                        'asyncio', 'logging', 'datetime', 'collections', 'itertools',
                        're', 'math', 'random', 'time', 'threading', 'multiprocessing',
                        'abc', 'hashlib', 'inspect', 'platform', 'shutil', 'subprocess',
                        'argparse', 'ast', 'signal', 'time'
                    }:
                        result.standard_imports.append(import_stmt)
                        if debug:
                            self.logger.log_debug(f"   📚 Standard: {import_stmt}")
                    else:
                        result.external_imports.append(import_stmt)
                        if debug:
                            self.logger.log_debug(f"   🌐 Externe: {import_stmt}")
            
            # Mettre à jour les statistiques
            self.stats['local_imports'] += len(result.local_imports)
            self.stats['external_imports'] += len(result.external_imports)
            
        except Exception as e:
            result.error_messages.append(str(e))
            self.logger.log_error(f"Erreur analyse fichier {file_path}: {e}")
        
        return result
    
    def _generate_analysis_report(self, target_files: List[str], cycles: List[List[str]]) -> Dict[str, Any]:
        """Génère un rapport d'analyse complet"""
        
        # Statistiques générales
        total_files = len(self.dependency_graph.nodes)
        total_imports = sum(len(node.imports) for node in self.dependency_graph.nodes.values())
        total_local = sum(len(node.local_imports) for node in self.dependency_graph.nodes.values())
        total_external = sum(len(node.external_imports) for node in self.dependency_graph.nodes.values())
        total_standard = sum(len(node.standard_imports) for node in self.dependency_graph.nodes.values())
        
        # Fichiers avec le plus d'imports
        files_by_imports = sorted(
            self.dependency_graph.nodes.items(),
            key=lambda x: len(x[1].imports),
            reverse=True
        )[:10]
        
        # Fichiers avec des erreurs
        files_with_errors = [
            file_path for file_path, node in self.dependency_graph.nodes.items()
            if node.error_messages
        ]
        
        report = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'target_files': target_files,
                'total_files_analyzed': total_files,
                'max_depth': self.max_depth,
                'project_root': self.project_root
            },
            'statistics': {
                'files_analyzed': total_files,
                'total_imports': total_imports,
                'local_imports': total_local,
                'external_imports': total_external,
                'standard_imports': total_standard,
                'cycles_detected': len(cycles),
                'files_with_errors': len(files_with_errors),
                'duration': self.stats['duration']
            },
            'files_analysis': {
                file_path: {
                    'imports': node.imports,
                    'local_imports': node.local_imports,
                    'external_imports': node.external_imports,
                    'standard_imports': node.standard_imports,
                    'import_count': node.import_count,
                    'dependency_depth': node.dependency_depth,
                    'errors': node.error_messages
                }
                for file_path, node in self.dependency_graph.nodes.items()
            },
            'top_files_by_imports': [
                {'file': file_path, 'import_count': len(node.imports)}
                for file_path, node in files_by_imports
            ],
            'cycles': cycles,
            'detected_modules': self._local_modules_cache
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], output_path: str):
        """Sauvegarde le rapport au format JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
    
    def generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """Génère le rapport Markdown final"""
        return self.logger.finalize_report(self.stats)
    
    def get_detected_local_modules(self) -> Dict[str, bool]:
        """Retourne les modules locaux détectés automatiquement"""
        return self._local_modules_cache.copy()
    
    def print_detected_modules(self):
        """Affiche les modules locaux détectés automatiquement"""
        print("🔍 Modules locaux détectés automatiquement:")
        for module, is_local in sorted(self._local_modules_cache.items()):
            status = "✅" if is_local else "❌"
            print(f"  {status} {module}")
        print(f"Total: {len(self._local_modules_cache)} modules analysés")


def main():
    """Fonction principale du script d'analyse d'imports"""
    parser = argparse.ArgumentParser(
        description='🔍 Analyseur d\'imports Python - Version redesignée',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python import_analyzer.py file1.py file2.py
  python import_analyzer.py --max-depth 5 file1.py
  python import_analyzer.py --output report.json file1.py file2.py
  python import_analyzer.py --markdown report.md file1.py
  python import_analyzer.py --debug --show-modules file1.py
        """
    )
    
    parser.add_argument('files', nargs='+', help='Fichiers Python à analyser')
    parser.add_argument('--max-depth', type=int, default=None,
                       help='Limite de profondeur pour l\'analyse récursive (défaut: 10)')
    parser.add_argument('--output', type=str,
                       help='Fichier de sortie JSON pour le rapport')
    parser.add_argument('--markdown', type=str,
                       help='Fichier de sortie Markdown pour le rapport')
    parser.add_argument('--project-root', type=str, default='.',
                       help='Racine du projet (défaut: répertoire courant)')
    parser.add_argument('--no-import-resolver', action='store_true',
                       help='Désactiver l\'utilisation de l\'ImportResolver')
    parser.add_argument('--debug', action='store_true',
                       help='Mode debug avec informations détaillées')
    parser.add_argument('--show-modules', action='store_true',
                       help='Afficher les modules détectés automatiquement')
    parser.add_argument('--verbose', action='store_true',
                       help='Mode verbeux (alias pour --debug)')
    
    args = parser.parse_args()
    
    # Gérer les alias
    if args.verbose:
        args.debug = True
    
    # Créer l'analyseur
    analyzer = ImportAnalyzer(project_root=args.project_root)
    
    # Analyser les fichiers
    print("🚀 Début de l'analyse d'imports...")
    report = analyzer.analyze_files(
        args.files, 
        max_depth=args.max_depth,
        use_import_resolver=not args.no_import_resolver,
        debug=args.debug
    )
    
    # Afficher les résultats
    stats = report['statistics']
    print(f"\n📊 Résultats de l'analyse:")
    print(f"  Fichiers analysés: {stats['files_analyzed']}")
    print(f"  Imports totaux: {stats['total_imports']}")
    print(f"  Imports locaux: {stats['local_imports']}")
    print(f"  Imports externes: {stats['external_imports']}")
    print(f"  Imports standard: {stats['standard_imports']}")
    print(f"  Cycles détectés: {stats['cycles_detected']}")
    print(f"  Durée: {stats['duration']:.2f}s")
    
    # Afficher les modules détectés si demandé
    if args.show_modules:
        print()
        analyzer.print_detected_modules()
    
    # Sauvegarder le rapport JSON si demandé
    if args.output:
        analyzer.save_report(report, args.output)
        print(f"\n💾 Rapport JSON sauvegardé: {args.output}")
    
    # Sauvegarder le rapport Markdown si demandé
    if args.markdown:
        markdown_content = analyzer.generate_markdown_report(report)
        with open(args.markdown, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"📝 Rapport Markdown sauvegardé: {args.markdown}")
    else:
        # Générer le rapport Markdown par défaut
        markdown_content = analyzer.generate_markdown_report(report)
        print(f"\n📝 Rapport Markdown généré dans logs/imports_analysis/imports_analysis_report.md")
    
    print(f"\n✅ Analyse terminée!")


if __name__ == '__main__':
    main() 