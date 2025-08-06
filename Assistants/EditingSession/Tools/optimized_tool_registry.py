#!/usr/bin/env python3
"""
⛧ Optimized Tool Registry ⛧
ToolRegistry optimisé avec cache d'analyse d'imports

Registre dynamique d'outils avec intégration TemporalFractalMemoryEngine et 
cache intelligent pour éviter les analyses redondantes d'imports.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import sys
import inspect
import asyncio
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

from Core.Parsers.luciform_parser import parse_luciform
from TemporalFractalMemoryEngine.core.temporal_engine import TemporalEngine
from Core.Partitioner.import_analysis_cache import get_import_optimizer


class OptimizedToolRegistry:
    """Registre dynamique d'outils optimisé avec cache d'analyse d'imports."""
    
    def __init__(self, memory_engine: TemporalEngine):
        self.memory_engine = memory_engine
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.tools_path = Path(__file__).parent  # Répertoire local Tools
        self.tools_docs_path = Path("Tools/Library/documentation/luciforms")
        
        # Optimiseur d'analyse d'imports
        self.import_optimizer = get_import_optimizer(memory_engine)
        
        # Configuration des triggers d'analyse
        self.analysis_triggers = {
            'code_analyzer': True,
            'file_diff': True,
            'file_stats': True,
            'template_generator': True,
            'safe_read_file_content': False,  # Pas d'analyse pour lecture simple
            'safe_write_file_content': True,  # Analyse après écriture
            'safe_replace_text_in_file': True,
            'safe_insert_text_at_line': True,
            'safe_delete_lines': True,
            'safe_overwrite_file': True,
            'safe_append_to_file': True,
            'safe_create_file': True,
            'safe_delete_file': True,
            'safe_create_directory': False,
            'safe_delete_directory': False,
            'walk_directory': False,
            'list_directory_contents': False,
            'find_text_in_project': False,
            'replace_text_in_project': True,
            'regex_search_file': False,
            'scry_for_text': False,
            'locate_text_sigils': False,
            'file_stats': True,
            'backup_creator': False,
            'template_generator': True,
            'md_hierarchy_basic': False,
            'read_file_content_naked': False,
            'reading_tools': False,
            'rename_project_entity': True,
        }
        
    def _find_node_text(self, nodes: List[Dict], tag: str) -> Optional[str]:
        """Utilitaire pour trouver le contenu textuel d'un nœud spécifique."""
        for node in nodes:
            if node.get('tag') == tag:
                for child in node.get('children', []):
                    if child.get('tag') == 'text':
                        return child.get('content')
        return None
    
    def _find_node_list(self, nodes: List[Dict], tag: str) -> List[str]:
        """Utilitaire pour trouver une liste de contenus textuels dans des sous-nœuds."""
        for node in nodes:
            if node.get('tag') == tag:
                items = []
                for child in node.get('children', []):
                    if child.get('tag') != 'comment':
                        for sub_child in child.get('children', []):
                            if sub_child.get('tag') == 'text':
                                items.append(sub_child.get('content'))
                return items
        return []
    
    def _extract_semantic_doc(self, ast: Dict) -> Optional[Dict]:
        """Extrait un dictionnaire sémantique depuis l'arbre de syntaxe abstrait (AST)."""
        if not ast or ast.get('tag') != '🜲luciform_doc':
            return None

        doc = {'id': ast.get('attrs', {}).get('id')}
        
        children = ast.get('children', [])
        
        # Extraction du pacte (garde les symboles dans les clés)
        pacte_node = next((n for n in children if n.get('tag') == '🜄pacte'), None)
        if pacte_node:
            pacte_children = pacte_node.get('children', [])
            doc['🜄pacte'] = {
                'type': self._find_node_text(pacte_children, 'type'),
                'intent': self._find_node_text(pacte_children, 'intent'),
                'level': self._find_node_text(pacte_children, 'level'),
            }

        # Extraction de l'invocation (garde les symboles dans les clés)
        invocation_node = next((n for n in children if n.get('tag') == '🜂invocation'), None)
        if invocation_node:
            inv_children = invocation_node.get('children', [])
            doc['🜂invocation'] = {
                'signature': self._find_node_text(inv_children, 'signature'),
                'requires': self._find_node_list(inv_children, 'requires'),
                'optional': self._find_node_list(inv_children, 'optional'),
                'returns': self._find_node_text(inv_children, 'returns'),
            }

        # Extraction de l'essence (garde les symboles dans les clés)
        essence_node = next((n for n in children if n.get('tag') == '🜁essence'), None)
        if essence_node:
            ess_children = essence_node.get('children', [])
            doc['🜁essence'] = {
                'keywords': self._find_node_list(ess_children, 'keywords'),
                'symbolic_layer': self._find_node_text(ess_children, 'symbolic_layer'),
                'usage_context': self._find_node_text(ess_children, 'usage_context'),
            }

        return doc
    
    def _load_tools_from_directory(self, docs_path: Path, available_functions: Dict[str, Callable], 
                                  source_name: str) -> int:
        """Charge les outils depuis un répertoire de documentation."""
        loaded_count = 0
        
        if not docs_path.exists():
            print(f"⚠️  Répertoire de documentation {source_name} non trouvé : {docs_path}")
            return loaded_count
        
        for luciform_file in docs_path.glob("*.luciform"):
            try:
                with open(luciform_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                ast = parse_luciform(content)
                doc = self._extract_semantic_doc(ast)
                
                if doc and doc.get('id'):
                    tool_id = doc['id']
                    
                    # Vérifier si la fonction existe
                    if tool_id in available_functions:
                        self.tools[tool_id] = {
                            'doc': doc,
                            'function': available_functions[tool_id],
                            'source': source_name,
                            'luciform_file': str(luciform_file)
                        }
                        loaded_count += 1
                    else:
                        print(f"⚠️  Fonction {tool_id} non trouvée dans {source_name}")
                        
            except Exception as e:
                print(f"❌ Erreur lors du chargement de {luciform_file}: {e}")
        
        return loaded_count
    
    def _get_available_functions(self) -> Dict[str, Callable]:
        """Récupère toutes les fonctions disponibles dans le répertoire Tools."""
        available_functions = {}
        
        # Fonctions de base
        base_functions = {
            'execute_command': self._execute_command_wrapper,
            'execute_command_async': self._execute_command_async_wrapper,
        }
        available_functions.update(base_functions)
        
        # Charger les fonctions depuis les fichiers Python
        for py_file in self.tools_path.glob("*.py"):
            if py_file.name.startswith('_') or py_file.name == '__init__.py':
                continue
                
            try:
                module_name = py_file.stem
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Chercher les fonctions principales
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr) and not attr_name.startswith('_'):
                        available_functions[attr_name] = attr
                        
            except Exception as e:
                print(f"⚠️  Erreur lors du chargement de {py_file}: {e}")
        
        return available_functions
    
    def _execute_command_wrapper(self, command: str, **kwargs):
        """Wrapper pour l'exécution de commandes."""
        import subprocess
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_command_async_wrapper(self, command: str, **kwargs):
        """Wrapper asynchrone pour l'exécution de commandes."""
        import subprocess
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            return {
                'success': process.returncode == 0,
                'stdout': stdout.decode(),
                'stderr': stderr.decode(),
                'returncode': process.returncode
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def initialize(self) -> None:
        """Initialise le registre d'outils."""
        print("🔧 Initialisation du registre d'outils optimisé...")
        
        available_functions = self._get_available_functions()
        
        # Charger les outils depuis différents répertoires
        loaded_count = 0
        loaded_count += self._load_tools_from_directory(
            self.tools_path, available_functions, "Tools"
        )
        
        if self.tools_docs_path.exists():
            loaded_count += self._load_tools_from_directory(
                self.tools_docs_path, available_functions, "Tools/Library"
            )
        
        print(f"✅ {loaded_count} outils chargés dans le registre optimisé")
    
    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un outil par son ID."""
        return self.tools.get(tool_id)
    
    def list_tools(self, filter_type: Optional[str] = None, 
                   filter_level: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Liste les outils disponibles avec filtres optionnels."""
        tools_list = []
        
        for tool_id, tool_info in self.tools.items():
            doc = tool_info['doc']
            
            # Appliquer les filtres
            if filter_type and doc.get('🜄pacte', {}).get('type') != filter_type:
                continue
            if filter_level and doc.get('🜄pacte', {}).get('level') != filter_level:
                continue
            
            tools_list.append({
                'id': tool_id,
                'doc': doc,
                'source': tool_info['source']
            })
        
        # Limiter le nombre de résultats
        if limit:
            tools_list = tools_list[:limit]
        
        return tools_list
    
    def search_tools(self, query: str) -> List[Dict[str, Any]]:
        """Recherche des outils par mots-clés."""
        results = []
        query_lower = query.lower()
        
        for tool_id, tool_info in self.tools.items():
            doc = tool_info['doc']
            
            # Rechercher dans différents champs
            searchable_text = [
                tool_id,
                doc.get('🜄pacte', {}).get('intent', ''),
                doc.get('🜁essence', {}).get('keywords', []),
                doc.get('🜁essence', {}).get('usage_context', '')
            ]
            
            # Aplatir les listes
            searchable_text = [str(item) for item in searchable_text if item]
            if isinstance(searchable_text[2], list):
                searchable_text[2] = ' '.join(searchable_text[2])
            
            combined_text = ' '.join(searchable_text).lower()
            
            if query_lower in combined_text:
                results.append({
                    'id': tool_id,
                    'doc': doc,
                    'source': tool_info['source'],
                    'relevance_score': combined_text.count(query_lower)
                })
        
        # Trier par score de pertinence
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return results
    
    def get_tool_for_openai(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un outil au format OpenAI."""
        tool_info = self.get_tool(tool_id)
        if not tool_info:
            return None
        
        doc = tool_info['doc']
        
        return {
            'type': 'function',
            'function': {
                'name': tool_id,
                'description': doc.get('🜄pacte', {}).get('intent', ''),
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': doc.get('🜂invocation', {}).get('requires', [])
                }
            }
        }
    
    def get_all_tools_for_openai(self) -> List[Dict[str, Any]]:
        """Récupère tous les outils au format OpenAI."""
        return [self.get_tool_for_openai(tool_id) for tool_id in self.tools.keys()]
    
    async def invoke_tool(self, tool_id: str, **kwargs) -> Dict[str, Any]:
        """Invocation d'outil avec optimisation d'analyse d'imports."""
        
        # Vérifier si on doit analyser les imports
        if self._should_analyze_imports(tool_id, kwargs):
            file_path = kwargs.get('file_path')
            if file_path:
                # Analyse optimisée
                fractal_nodes = await self.import_optimizer.get_or_analyze_imports(file_path)
                
                # Mise à jour de la mémoire temporelle
                await self._update_temporal_memory_with_imports(fractal_nodes, file_path)
        
        # Exécution normale de l'outil
        result = self._execute_tool(tool_id, **kwargs)
        
        return result
    
    def _should_analyze_imports(self, tool_id: str, kwargs: dict) -> bool:
        """Détermine si on doit analyser les imports"""
        return (self.analysis_triggers.get(tool_id, False) and 
                'file_path' in kwargs)
    
    def _execute_tool(self, tool_id: str, **kwargs) -> Dict[str, Any]:
        """Exécute un outil."""
        tool_info = self.get_tool(tool_id)
        if not tool_info:
            return {'success': False, 'error': f'Outil {tool_id} non trouvé'}
        
        try:
            function = tool_info['function']
            result = function(**kwargs)
            
            return {
                'success': True,
                'result': result,
                'tool_id': tool_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tool_id': tool_id
            }
    
    async def _update_temporal_memory_with_imports(self, fractal_nodes: Dict[str, Any], file_path: str):
        """Met à jour la mémoire temporelle avec les imports analysés"""
        try:
            if self.memory_engine and fractal_nodes:
                # Créer un nœud de mémoire pour les imports
                import_memory = {
                    'type': 'import_analysis',
                    'file_path': file_path,
                    'fractal_nodes': fractal_nodes,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Stocker dans la mémoire temporelle
                await self.memory_engine.store_memory(import_memory)
                
                print(f"💾 Imports analysés stockés pour {file_path}")
        except Exception as e:
            print(f"⚠️ Erreur lors de la mise à jour de la mémoire: {e}")


# Instance globale
_global_optimized_registry: Optional[OptimizedToolRegistry] = None

def initialize_optimized_tool_registry(memory_engine: TemporalEngine) -> OptimizedToolRegistry:
    """Initialise le registre d'outils optimisé global."""
    global _global_optimized_registry
    _global_optimized_registry = OptimizedToolRegistry(memory_engine)
    _global_optimized_registry.initialize()
    return _global_optimized_registry

def get_optimized_tool_registry() -> OptimizedToolRegistry:
    """Récupère le registre d'outils optimisé global."""
    if _global_optimized_registry is None:
        raise RuntimeError("OptimizedToolRegistry non initialisé. Appelez initialize_optimized_tool_registry() d'abord.")
    return _global_optimized_registry 