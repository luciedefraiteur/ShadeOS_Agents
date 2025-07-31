import os
import sys
from .luciform_parser import parse_luciform

# Importe les fonctions d'outils
from ShadeOS_Agents.Tools.FileSystem.implementation.reading_tools import *
from ShadeOS_Agents.Tools.FileSystem.implementation.writing_tools import *
from ShadeOS_Agents.Tools.FileSystem.implementation.listing_tools import *
from ShadeOS_Agents.Tools.FileSystem.implementation.modification_tools import *
from ShadeOS_Agents.Tools.FileSystem.implementation.scry.scrying_tools import *
from ShadeOS_Agents.Tools.Library.implementation.library_tools import *

# Chemin vers la documentation des outils
DOCS_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../documentation/luciforms'))

ALL_TOOLS = {}

def _reconstruct_doc_from_tree(parsed_tree):
    """Reconstruit un dictionnaire plat depuis l'arbre parsé."""
    print(f"[DEBUG] Reconstruire depuis l'arbre: {parsed_tree}", file=sys.stderr)
    if not parsed_tree or not parsed_tree.get("attrs"):
        print("[DEBUG] Arbre parsé invalide ou sans attributs.", file=sys.stderr)
        return None
        
    doc = {"id": parsed_tree["attrs"].get("id")}
    if not doc["id"]:
        print("[DEBUG] ID non trouvé dans l'arbre parsé.", file=sys.stderr)
        return None

    for section in parsed_tree.get("children", []):
        print(f"[DEBUG] Traitement de la section: {section.get("tag")}", file=sys.stderr)
        if section.get("type") == "comment": continue
        
        section_name = section.get("tag")
        if not section_name:
            print("[DEBUG] Nom de section non trouvé.", file=sys.stderr)
            continue

        section_data = {}
        comments = []
        for item in section.get("children", []):
            item_type = item.get("type")
            item_tag = item.get("tag")
            print(f"[DEBUG]   - Traitement de l'élément: {item_tag} (Type: {item_type})", file=sys.stderr)

            if item_type == "comment":
                comments.append(item.get("content"))
            elif item_type == "text":
                continue
            else: # C'est une balise
                children = item.get("children", [])
                if any(child.get("tag") == "param" for child in children):
                    section_data[item_tag] = [child["children"][0]["content"] for child in children if child.get("tag") == "param" and child.get("children")]
                elif children and children[0].get("type") == "text":
                    section_data[item_tag] = children[0].get("content")
                elif children and children[0].get("type") == "comment": # Gère les commentaires au niveau de l'élément
                    if "comments" not in section_data: section_data["comments"] = []
                    section_data["comments"].append(children[0].get("content"))
                elif item_tag: # Gère les balises sans enfants texte direct (comme <keywords>)
                    # Récupère les enfants de la balise (ex: <keyword>)
                    nested_children_data = []
                    for nested_child in children:
                        if nested_child.get("type") == "text":
                            nested_children_data.append(nested_child.get("content"))
                        elif nested_child.get("tag") == "keyword" and nested_child.get("children") and nested_child["children"][0].get("type") == "text":
                            nested_children_data.append(nested_child["children"][0].get("content"))
                        # Ajout pour gérer les balises simples comme <type> et <intent>
                        elif nested_child.get("tag") and nested_child.get("children") and nested_child["children"][0].get("type") == "text":
                            section_data[nested_child.get("tag")] = nested_child["children"][0].get("content")
                    if nested_children_data:
                        section_data[item_tag] = nested_children_data
                # Ajout pour gérer les balises simples comme <type> et <intent> qui sont directement dans la section
                elif item_tag and children and children[0].get("type") == "text":
                    section_data[item_tag] = children[0].get("content")
                # Ajout pour gérer les balises simples comme <type> et <intent> qui sont directement dans la section
                elif item_tag and children and children[0].get("type") == "text":
                    section_data[item_tag] = children[0].get("content")
                # Ajout pour gérer les balises simples comme <type> et <intent> qui sont directement dans la section
                elif item_tag and children and children[0].get("type") == "text":
                    section_data[item_tag] = children[0].get("content")
                # Ajout pour gérer les balises simples comme <type> et <intent> qui sont directement dans la section
                elif item_tag and children and children[0].get("type") == "text":
                    section_data[item_tag] = children[0].get("content")
        
        if comments:
            section_data["comments"] = comments
        
        doc[section_name] = section_data
    print(f"[DEBUG] Document reconstruit: {doc}", file=sys.stderr)
    return doc

def _build_dynamic_registry():
    """Construit le registre dynamiquement en lisant les fichiers .luciform."""
    available_functions = {**globals()}

    for doc_file in os.listdir(DOCS_BASE_PATH):
        if doc_file.endswith(".luciform"):
            try:
                parsed_tree = parse_luciform(os.path.join(DOCS_BASE_PATH, doc_file))
                lucidoc = _reconstruct_doc_from_tree(parsed_tree)
                if not lucidoc:
                    continue
                tool_id = lucidoc.get("id")
                
                if tool_id and tool_id in available_functions:
                    ALL_TOOLS[tool_id] = {
                        "function": available_functions[tool_id],
                        "lucidoc": lucidoc
                    }
            except (ValueError, KeyError, IndexError) as e:
                print(f"[DEBUG] Erreur de reconstruction du luciform {doc_file}: {e}", file=sys.stderr)
                continue

_build_dynamic_registry()