import os
import importlib.util
from openai import tool

# Le chemin vers la racine des outils, à adapter si nécessaire
TOOLS_BASE_PATH = "/home/luciedefraiteur/ShadeOS_Agents/Tools/"

def _find_tool_files():
    """Helper pour trouver tous les fichiers d'implémentation d'outils."""
    tool_files = []
    for root, _, files in os.walk(TOOLS_BASE_PATH):
        for file in files:
            if file.endswith("_tools.py"):
                tool_files.append(os.path.join(root, file))
    return tool_files

def _extract_lucidoc_from_file(path):
    """Helper pour extraire tous les __lucidoc__ d'un fichier."""
    docs = []
    try:
        spec = importlib.util.spec_from_file_location("module.name", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if hasattr(attr, "__lucidoc__"):
                docs.append(getattr(attr, "__lucidoc__"))
    except Exception:
        # Ignorer les fichiers qui ne peuvent être importés
        pass
    return docs

@tool
def list_available_tools(type_filter: str = None, keyword_filter: str = None) -> list[dict]:
    """
    Liste tous les outils disponibles, avec une option de filtrage.
    Retourne une liste de dictionnaires contenant l'id, le type et l'intention de chaque outil.
    """
    all_docs = []
    tool_files = _find_tool_files()
    for file_path in tool_files:
        all_docs.extend(_extract_lucidoc_from_file(file_path))

    filtered_docs = all_docs

    if type_filter:
        filtered_docs = [doc for doc in filtered_docs if doc.get("type") == type_filter]
    
    if keyword_filter:
        filtered_docs = [doc for doc in filtered_docs if keyword_filter in doc.get("ritual_keywords", [])]

    # Ne retourne que les champs publics pour la liste
    public_docs = [
        {"id": doc.get("id"), "type": doc.get("type"), "intent": doc.get("intent")}
        for doc in filtered_docs
    ]
    
    return public_docs

@tool
def get_tool_documentation(tool_id: str) -> dict:
    """
    Retourne la documentation complète (`__lucidoc__`) pour un outil donné.
    """
    tool_files = _find_tool_files()
    for file_path in tool_files:
        docs = _extract_lucidoc_from_file(file_path)
        for doc in docs:
            if doc.get("id") == tool_id:
                return doc
    return {"error": f"Outil avec l'id '{tool_id}' non trouvé."}
