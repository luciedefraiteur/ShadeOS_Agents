import os

def list_available_tools(all_tools: dict, type_filter: str = None, keyword_filter: str = None) -> list[dict]:
    """Liste tous les outils disponibles, avec une option de filtrage."""
    all_docs = [info["lucidoc"] for info in all_tools.values()]

    filtered_docs = all_docs

    if type_filter:
        filtered_docs = [doc for doc in filtered_docs if doc.get("pacte", {}).get("type") == type_filter]
    
    if keyword_filter:
        filtered_docs = [doc for doc in filtered_docs if keyword_filter in doc.get("essence", {}).get("keywords", [])]

    public_docs = [
        {"id": doc.get("id"), "type": doc.get("pacte", {}).get("type"), "intent": doc.get("pacte", {}).get("intent")}
        for doc in filtered_docs
    ]
    
    return public_docs

def get_tool_documentation(all_tools: dict, tool_id: str) -> dict:
    """Retourne la documentation complète (`lucidoc`) pour un outil donné."""
    if tool_id in all_tools:
        return all_tools[tool_id]["lucidoc"]
    else:
        return {"error": f"Outil avec l'id '{tool_id}' non trouvé."}

def get_luciform_grimoire(tool_id: str) -> str:
    """Retrouve et présente le contenu brut et intégral d'un fichier .luciform de documentation."""
    # Chemin vers la documentation des outils
    DOCS_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../documentation/luciforms'))
    file_path = os.path.join(DOCS_BASE_PATH, f"{tool_id}.luciform")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Erreur : Le grimoire pour l'outil '{tool_id}' est introuvable."
