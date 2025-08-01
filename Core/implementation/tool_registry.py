import os
import sys
import pprint
import inspect

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
# Imports des outils Alagareth_toolset
from Alagareth_toolset.remember import remember
from Alagareth_toolset.recall import recall
from Alagareth_toolset.list_memories import list_memories
from Alagareth_toolset.forget import forget
from Tools.Search.implementation.search_tools import *

# Chemins vers la documentation des outils
DOCS_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Tools/Library/documentation/luciforms'))
ALAGARETH_DOCS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Alagareth_toolset'))

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
    
    # Extraction du pacte (garde les symboles dans les clés)
    pacte_node = next((n for n in children if n.get('tag') == '🜄pacte'), None)
    if pacte_node:
        pacte_children = pacte_node.get('children', [])
        doc['🜄pacte'] = {
            'type': _find_node_text(pacte_children, 'type'),
            'intent': _find_node_text(pacte_children, 'intent'),
            'level': _find_node_text(pacte_children, 'level'),
        }

    # Extraction de l'invocation (garde les symboles dans les clés)
    invocation_node = next((n for n in children if n.get('tag') == '🜂invocation'), None)
    if invocation_node:
        inv_children = invocation_node.get('children', [])
        doc['🜂invocation'] = {
            'signature': _find_node_text(inv_children, 'signature'),
            'requires': _find_node_list(inv_children, 'requires'),
            'optional': _find_node_list(inv_children, 'optional'),
            'returns': _find_node_text(inv_children, 'returns'),
        }

    # Extraction de l'essence (garde les symboles dans les clés)
    essence_node = next((n for n in children if n.get('tag') == '🜁essence'), None)
    if essence_node:
        ess_children = essence_node.get('children', [])
        doc['🜁essence'] = {
            'keywords': _find_node_list(ess_children, 'keywords'),
            'symbolic_layer': _find_node_text(ess_children, 'symbolic_layer'),
            'usage_context': _find_node_text(ess_children, 'usage_context'),
        }

    return doc


def _detect_invoke_cli_proxy(tool_id, available_functions):
    """
    Détecte si un outil utilise invoke_cli_tool pour appeler Alagareth_toolset.

    Returns:
        tuple: (is_proxy, target_function, target_doc_path)
    """
    if tool_id not in available_functions:
        return False, None, None

    # Vérifier si la fonction utilise invoke_cli_tool
    func = available_functions[tool_id]
    if hasattr(func, '__code__'):
        # Lire le code source pour détecter invoke_cli_tool
        import inspect
        try:
            source = inspect.getsource(func)
            if 'invoke_cli_tool' in source and f'"{tool_id}"' in source:
                # C'est un proxy via invoke_cli_tool
                target_doc_path = os.path.join(ALAGARETH_DOCS_PATH, f"{tool_id}.luciform")
                if os.path.exists(target_doc_path):
                    return True, func, target_doc_path
        except (OSError, TypeError):
            pass

    return False, None, None


def _load_documentation_from_path(docs_path, available_functions, source_name):
    """Charge les documentations luciform depuis un répertoire donné avec détection de proxy."""
    loaded_count = 0

    if not os.path.exists(docs_path):
        sys.stderr.write(f"Avertissement : Répertoire de documentation {source_name} non trouvé : {docs_path}\n")
        return loaded_count

    for doc_file in os.listdir(docs_path):
        if doc_file.endswith(".luciform"):
            file_path = os.path.join(docs_path, doc_file)
            try:
                ast = parse_luciform(file_path)
                lucidoc = _extract_semantic_doc(ast)

                if lucidoc and lucidoc.get("id"):
                    tool_id = lucidoc["id"]

                    # Éviter les doublons - priorité à Alagareth_toolset
                    if tool_id in ALL_TOOLS:
                        sys.stderr.write(f"Info : Outil '{tool_id}' déjà chargé, ignoré depuis {source_name}.\n")
                        continue

                    # Détecter si c'est un proxy via invoke_cli_tool
                    is_proxy, proxy_function, target_doc_path = _detect_invoke_cli_proxy(tool_id, available_functions)

                    if is_proxy:
                        # C'est un proxy, charger la doc depuis Alagareth_toolset
                        try:
                            target_ast = parse_luciform(target_doc_path)
                            target_lucidoc = _extract_semantic_doc(target_ast)

                            if target_lucidoc:
                                ALL_TOOLS[tool_id] = {
                                    "function": proxy_function,
                                    "lucidoc": target_lucidoc
                                }
                                loaded_count += 1
                                sys.stderr.write(f"Info : Proxy détecté {tool_id} -> {target_doc_path}\n")
                            else:
                                sys.stderr.write(f"Erreur : Doc cible malformée pour proxy {tool_id}: {target_doc_path}\n")
                        except Exception as e:
                            sys.stderr.write(f"Erreur : Impossible de charger doc cible pour proxy {tool_id}: {e}\n")

                    elif tool_id in available_functions:
                        # Fonction normale, pas un proxy
                        ALL_TOOLS[tool_id] = {
                            "function": available_functions[tool_id],
                            "lucidoc": lucidoc
                        }
                        loaded_count += 1
                    else:
                        sys.stderr.write(f"Avertissement : Outil '{tool_id}' défini dans {doc_file} ({source_name}) mais non trouvé.\n")
                else:
                    sys.stderr.write(f"Avertissement : Luciform dans {doc_file} ({source_name}) est mal formé ou n'a pas d'ID.\n")
            except Exception as e:
                sys.stderr.write(f"Erreur lors du parsing de {doc_file} ({source_name}): {e}\n")

    return loaded_count


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
        "remember": remember,
        "recall": recall,
        "list_memories": list_memories,
        "forget": forget,
    }
    available_functions.update(memory_tool_methods)

    # Charge d'abord les documentations depuis Alagareth_toolset (priorité)
    alagareth_count = _load_documentation_from_path(ALAGARETH_DOCS_PATH, available_functions, "Alagareth_toolset")

    # Puis charge les documentations depuis Tools/Library (pour les outils non couverts)
    tools_count = _load_documentation_from_path(DOCS_BASE_PATH, available_functions, "Tools/Library")

    sys.stderr.write(f"Info : Chargé {alagareth_count} docs depuis Alagareth_toolset, {tools_count} depuis Tools/Library.\n")



if __name__ == "__main__":
    # Appelle l'initialisation si le module est exécuté directement
    from Core.Archivist.MemoryEngine.engine import MemoryEngine
    memory_engine = MemoryEngine()
    initialize_tool_registry(memory_engine)

    print("⛧ Registre d'Outils - Diagnostic Complet")
    print("⛧" + "─" * 50)
    pprint.pprint(ALL_TOOLS)
    print(f"\n⛧ Total d'outils enregistrés : {len(ALL_TOOLS)}")

    # Affichage des outils sans documentation
    tools_without_docs = [tool_id for tool_id, tool_info in ALL_TOOLS.items()
                         if not tool_info.get("lucidoc")]
    if tools_without_docs:
        print(f"\n⛧ Outils sans documentation luciform ({len(tools_without_docs)}) :")
        for tool_id in tools_without_docs:
            print(f"  - {tool_id}")
    else:
        print("\n⛧ Tous les outils ont une documentation luciform !")