from openai import tool
import os

@tool
def list_directory_contents(path: str) -> dict:
    """Liste les fichiers et sous-répertoires d'un répertoire donné."""
    __lucidoc__ = {
        "id": "list_directory_contents",
        "type": "listing",
        "intent": "Révéler les entités directes d'un répertoire.",
        "requires": ["path"],
        "returns": "dict: {'files': list[str], 'directories': list[str]}",
        "ritual_keywords": ["list", "ls", "directory", "contents"],
        "symbolic_layer": "Ouvre un oeil sur un plan de l'existence, sans regarder en profondeur.",
        "usage_context": "Pour obtenir une vue rapide du contenu d'un dossier.",
        "level": "fondamental"
    }
    try:
        items = os.listdir(path)
        files = [item for item in items if os.path.isfile(os.path.join(path, item))]
        directories = [item for item in items if os.path.isdir(os.path.join(path, item))]
        return {"files": files, "directories": directories}
    except Exception as e:
        return {f"Erreur lors du listage du répertoire : {e}"}

@tool
def walk_directory(path: str) -> list[str]:
    """Marche récursivement dans un répertoire et retourne tous les chemins de fichiers."""
    __lucidoc__ = {
        "id": "walk_directory",
        "type": "listing",
        "intent": "Parcourir récursivement une arborescence pour en cartographier tous les fichiers.",
        "requires": ["path"],
        "returns": "list[str]: La liste de tous les chemins de fichiers trouvés.",
        "ritual_keywords": ["walk", "recursive", "find", "files"],
        "symbolic_layer": "Envoie des échos astraux dans un labyrinthe pour en révéler toutes les issues.",
        "usage_context": "Essentiel pour des opérations sur un projet entier, comme des recherches ou des modifications de masse.",
        "level": "intermédiaire"
    }
    try:
        file_paths = []
        for root, _, files in os.walk(path):
            for file in files:
                file_paths.append(os.path.join(root, file))
        return file_paths
    except Exception as e:
        return [f"Erreur lors du parcours du répertoire : {e}"]
