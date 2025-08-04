#!/usr/bin/env python3
"""
⛧ Tool Registry ⛧
Alma's Dynamic Tool Registry for MemoryEngine

Registre dynamique d'outils avec intégration MemoryEngine et support OpenAI Agents SDK.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import sys
import inspect
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

from Core.Parsers.luciform_parser import parse_luciform
from MemoryEngine.core.engine import MemoryEngine


class ToolRegistry:
    """Registre dynamique d'outils avec intégration MemoryEngine."""
    
    def __init__(self, memory_engine: MemoryEngine):
        self.memory_engine = memory_engine
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.tools_path = Path(__file__).parent  # Répertoire local Tools
        self.tools_docs_path = Path("Tools/Library/documentation/luciforms")
        
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
        
        for doc_file in docs_path.glob("*.luciform"):
            try:
                # Parse le fichier luciform
                ast = parse_luciform(str(doc_file))
                lucidoc = self._extract_semantic_doc(ast)
                
                if lucidoc and lucidoc.get("id"):
                    tool_id = lucidoc["id"]
                    
                    # Éviter les doublons - priorité à Alma_toolset
                    if tool_id in self.tools:
                        print(f"ℹ️  Outil '{tool_id}' déjà chargé, ignoré depuis {source_name}.")
                        continue
                    
                    # Vérifier si la fonction existe
                    if tool_id in available_functions:
                        self.tools[tool_id] = {
                            "function": available_functions[tool_id],
                            "lucidoc": lucidoc,
                            "source": source_name,
                            "file_path": str(doc_file)
                        }
                        loaded_count += 1
                    else:
                        print(f"⚠️  Outil '{tool_id}' défini dans {doc_file.name} mais fonction non trouvée.")
                else:
                    print(f"⚠️  Luciform dans {doc_file.name} mal formé ou sans ID.")
            except Exception as e:
                print(f"❌ Erreur parsing {doc_file.name}: {e}")
        
        return loaded_count
    
    def _get_available_functions(self) -> Dict[str, Callable]:
        """Collecte toutes les fonctions et méthodes d'outils disponibles."""
        functions = {}
        
        # Charger dynamiquement les fonctions depuis Alma_toolset
        try:
            import sys
            import os
            from pathlib import Path
            
            # Ajouter le répertoire racine au PYTHONPATH
            root_dir = Path(__file__).parent.parent.parent.parent
            sys.path.insert(0, str(root_dir))
            
            # Importer les modules Tools locaux
            tools_dir = Path(__file__).parent
            
            if tools_dir.exists():
                # Charger tous les modules Python dans Tools
                for py_file in tools_dir.glob("*.py"):
                    if py_file.name.startswith("__") or py_file.name.startswith("tool_"):
                        continue
                    
                    module_name = py_file.stem
                    try:
                        # Importer le module
                        module = __import__(f"Assistants.EditingSession.Tools.{module_name}", fromlist=[module_name])
                        
                        # Chercher la fonction principale (même nom que le module)
                        if hasattr(module, module_name):
                            functions[module_name] = getattr(module, module_name)
                            print(f"✅ Chargé: {module_name}")
                        
                        # Chercher d'autres fonctions dans le module
                        for attr_name in dir(module):
                            if not attr_name.startswith("_") and callable(getattr(module, attr_name)):
                                # Éviter les doublons
                                if attr_name not in functions:
                                    functions[attr_name] = getattr(module, attr_name)
                                    print(f"✅ Chargé: {attr_name}")
                    
                    except ImportError as e:
                        print(f"⚠️  Impossible d'importer {module_name}: {e}")
                    except Exception as e:
                        print(f"⚠️  Erreur lors du chargement de {module_name}: {e}")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement des fonctions Tools: {e}")
        
        # Ajouter des fonctions de fallback pour les tests
        fallback_functions = {
            "safe_create_file": lambda *args, **kwargs: {"success": True, "tool": "safe_create_file", "args": kwargs},
            "safe_replace_text_in_file": lambda *args, **kwargs: {"success": True, "tool": "safe_replace_text_in_file", "args": kwargs},
            "analyze_file_structure": lambda *args, **kwargs: {"success": True, "tool": "analyze_file_structure", "args": kwargs},
            "read_file_content": lambda *args, **kwargs: {"success": True, "tool": "read_file_content", "args": kwargs},
        }
        
        # Ajouter les fonctions de fallback seulement si elles ne sont pas déjà chargées
        for name, func in fallback_functions.items():
            if name not in functions:
                functions[name] = func
        
        print(f"📊 Total: {len(functions)} fonctions chargées")
        return functions
    
    def initialize(self) -> None:
        """Initialise le registre d'outils."""
        print("🔧 Initialisation du registre d'outils...")
        
        available_functions = self._get_available_functions()
        
        # Charge les outils locaux
        tools_count = self._load_tools_from_directory(
            self.tools_path, available_functions, "Tools"
        )
        
        # Puis charge les autres outils si disponibles
        library_count = self._load_tools_from_directory(
            self.tools_docs_path, available_functions, "Tools/Library"
        )
        
        print(f"✅ Chargé {tools_count} outils depuis Tools, {library_count} depuis Tools/Library")
        print(f"📊 Total: {len(self.tools)} outils enregistrés")
    
    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un outil par son ID."""
        return self.tools.get(tool_id)
    
    def list_tools(self, filter_type: Optional[str] = None, 
                   filter_level: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Liste les outils avec filtres optionnels."""
        filtered_tools = []
        
        for tool_id, tool_info in self.tools.items():
            lucidoc = tool_info.get("lucidoc", {})
            pacte = lucidoc.get("🜄pacte", {})
            
            # Appliquer les filtres
            if filter_type and pacte.get("type") != filter_type:
                continue
            if filter_level and pacte.get("level") != filter_level:
                continue
            
            filtered_tools.append({
                "id": tool_id,
                "type": pacte.get("type"),
                "level": pacte.get("level"),
                "intent": pacte.get("intent"),
                "source": tool_info.get("source")
            })
        
        # Appliquer la limite si spécifiée
        if limit is not None:
            filtered_tools = filtered_tools[:limit]
        
        return filtered_tools
    
    def search_tools(self, query: str) -> List[Dict[str, Any]]:
        """Recherche d'outils par mot-clé."""
        results = []
        query_lower = query.lower()
        
        for tool_id, tool_info in self.tools.items():
            lucidoc = tool_info.get("lucidoc", {})
            pacte = lucidoc.get("🜄pacte", {})
            essence = lucidoc.get("🜁essence", {})
            
            # Recherche dans l'intention
            intent = pacte.get("intent", "").lower()
            if query_lower in intent:
                results.append({
                    "id": tool_id,
                    "match_type": "intent",
                    "intent": pacte.get("intent"),
                    "type": pacte.get("type"),
                    "level": pacte.get("level")
                })
                continue
            
            # Recherche dans les mots-clés
            keywords = essence.get("keywords", [])
            if any(query_lower in kw.lower() for kw in keywords):
                results.append({
                    "id": tool_id,
                    "match_type": "keywords",
                    "keywords": keywords,
                    "intent": pacte.get("intent"),
                    "type": pacte.get("type"),
                    "level": pacte.get("level")
                })
        
        return results
    
    def get_tool_for_openai(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Formate un outil pour OpenAI Agents SDK."""
        tool_info = self.get_tool(tool_id)
        if not tool_info:
            return None
        
        lucidoc = tool_info.get("lucidoc", {})
        invocation = lucidoc.get("🜂invocation", {})
        pacte = lucidoc.get("🜄pacte", {})
        
        # Construction des paramètres OpenAI
        properties = {}
        required = []
        
        # Ajouter les paramètres requis
        for param in invocation.get("requires", []):
            properties[param] = {
                "type": "string",
                "description": f"Paramètre requis: {param}"
            }
            required.append(param)
        
        # Ajouter les paramètres optionnels
        for param in invocation.get("optional", []):
            properties[param] = {
                "type": "string",
                "description": f"Paramètre optionnel: {param}"
            }
        
        return {
            "type": "function",
            "function": {
                "name": tool_id,
                "description": pacte.get("intent", f"Outil {tool_id}"),
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    def get_all_tools_for_openai(self) -> List[Dict[str, Any]]:
        """Récupère tous les outils formatés pour OpenAI Agents SDK."""
        openai_tools = []
        
        for tool_id in self.tools.keys():
            tool_format = self.get_tool_for_openai(tool_id)
            if tool_format:
                openai_tools.append(tool_format)
        
        return openai_tools
    
    def invoke_tool(self, tool_id: str, **kwargs) -> Dict[str, Any]:
        """Proxy pour invoquer un outil via le ToolInvoker."""
        from Assistants.EditingSession.Tools.tool_invoker import ToolInvoker
        
        # Créer un invoker temporaire si nécessaire
        if not hasattr(self, '_invoker'):
            self._invoker = ToolInvoker(self)
        
        return self._invoker.invoke_tool(tool_id, **kwargs)


# Instance globale
_global_registry: Optional[ToolRegistry] = None

def initialize_tool_registry(memory_engine: MemoryEngine) -> ToolRegistry:
    """Initialise le registre global d'outils."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry(memory_engine)
        _global_registry.initialize()
    return _global_registry

def get_tool_registry() -> ToolRegistry:
    """Récupère le registre global d'outils."""
    if _global_registry is None:
        raise RuntimeError("ToolRegistry non initialisé. Appelez initialize_tool_registry() d'abord.")
    return _global_registry 