import os
import sys
import pprint

# Ajoute le répertoire racine du projet au PYTHONPATH pour les imports absolus
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Core.implementation.luciform_parser import parse_luciform

# Importe les fonctions d'outils pour qu'elles soient dans le scope global
from Tools.FileSystem.implementation.reading_tools import *
from Tools.FileSystem.implementation.writing_tools import *
from Core.Archivist.MemoryEngine.engine import memory_engine
from Tools.FileSystem.implementation.listing_tools import *
from Tools.FileSystem.implementation.modification_tools import *
from Tools.FileSystem.implementation.scry.scrying_tools import *
from Tools.Library.implementation.library_tools import *
from Tools.Execution.implementation.execution_tools import *
from Tools.Execution.implementation.invoke_cli_tool import invoke_cli_tool
from Tools.Search.implementation.search_tools import *

# Chemin vers la documentation des outils
DOCS_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Tools/Library/documentation/luciforms'))

ALL_TOOLS = {}

def _find_node_text(nodes, tag):
    """Utilitaire pour trouver le contenu textuel d'un nœud spécifique."""
    for node in nodes:
        if node.get('tag') == tag:
            for child in node.get('children', []):
                if child.get('tag') == 'text':
                    return child.get('content')
    return None

def _find_node_list(nodes, tag):
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

def _extract_semantic_doc(ast: dict) -> dict:
    """Extrait un dictionnaire sémantique depuis l'arbre de syntaxe abstrait (AST)."""
    if not ast or ast.get('tag') != '🜲luciform_doc':
        return None

    doc = {'id': ast.get('attrs', {}).get('id')}
    
    children = ast.get('children', [])
    
    # Extraction du pacte
    pacte_node = next((n for n in children if n.get('tag') == '🜄pacte'), None)
    if pacte_node:
        pacte_children = pacte_node.get('children', [])
        doc['pacte'] = {
            'type': _find_node_text(pacte_children, 'type'),
            'intent': _find_node_text(pacte_children, 'intent'),
            'level': _find_node_text(pacte_children, 'level'),
        }

    # Extraction de l'invocation
    invocation_node = next((n for n in children if n.get('tag') == '🜂invocation'), None)
    if invocation_node:
        inv_children = invocation_node.get('children', [])
        doc['invocation'] = {
            'signature': _find_node_text(inv_children, 'signature'),
            'requires': _find_node_list(inv_children, 'requires'),
            'optional': _find_node_list(inv_children, 'optional'),
            'returns': _find_node_text(inv_children, 'returns'),
        }

    # Extraction de l'essence
    essence_node = next((n for n in children if n.get('tag') == '🜁essence'), None)
    if essence_node:
        ess_children = essence_node.get('children', [])
        doc['essence'] = {
            'keywords': _find_node_list(ess_children, 'keywords'),
            'symbolic_layer': _find_node_text(ess_children, 'symbolic_layer'),
            'usage_context': _find_node_text(ess_children, 'usage_context'),
        }

    return doc

def initialize_tool_registry(memory_engine_instance):
    """Construit le registre dynamiquement en lisant et parsant les fichiers .luciform."""
    # Rassemble d'abord les fonctions globales
    available_functions = {**globals()}
    # Ajoute ensuite les méthodes du moteur de mémoire
    memory_tool_methods = {
        "create_memory": memory_engine_instance.create_memory,
        "get_memory_node": memory_engine_instance.get_memory_node,
        "find_memories_by_keyword": memory_engine_instance.find_memories_by_keyword,
        "list_children": memory_engine_instance.list_children,
        "list_links": memory_engine_instance.list_links,
    }
    available_functions.update(memory_tool_methods)

    for doc_file in os.listdir(DOCS_BASE_PATH):
        if doc_file.endswith(".luciform"):
            file_path = os.path.join(DOCS_BASE_PATH, doc_file)
            try:
                ast = parse_luciform(file_path)
                lucidoc = _extract_semantic_doc(ast)
                
                if lucidoc and lucidoc.get("id"):
                    tool_id = lucidoc["id"]
                    if tool_id in available_functions:
                        ALL_TOOLS[tool_id] = {
                            "function": available_functions[tool_id],
                            "lucidoc": lucidoc
                        }
                    else:
                        sys.stderr.write(f"Avertissement : Outil '{tool_id}' défini dans {doc_file} mais non trouvé.\n")
                else:
                    sys.stderr.write(f"Avertissement : Luciform dans {doc_file} est mal formé ou n'a pas d'ID.\n")
            except Exception as e:
                sys.stderr.write(f"Erreur lors du traitement du luciform {doc_file}: {e}\n")
                continue



if __name__ == "__main__":    initialize_tool_registry() # Appelle l'initialisation si le module est exécuté directement    pprint.pprint(ALL_TOOLS)    print(f"\nTotal d'outils enregistrés : {len(ALL_TOOLS)}")