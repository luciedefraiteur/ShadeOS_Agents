import os

def list_directory_contents(path: str) -> dict:
    """Liste les fichiers et sous-répertoires d'un répertoire donné."""
    try:
        items = os.listdir(path)
        files = [item for item in items if os.path.isfile(os.path.join(path, item))]
        directories = [item for item in items if os.path.isdir(os.path.join(path, item))]
        return {"files": files, "directories": directories}
    except Exception as e:
        return {f"Erreur lors du listage du répertoire : {e}"}

def walk_directory(path: str) -> list[str]:
    """Marche récursivement dans un répertoire et retourne tous les chemins de fichiers."""
    try:
        file_paths = []
        for root, _, files in os.walk(path):
            for file in files:
                file_paths.append(os.path.join(root, file))
        return file_paths
    except Exception as e:
        return [f"Erreur lors du parcours du répertoire : {e}"]