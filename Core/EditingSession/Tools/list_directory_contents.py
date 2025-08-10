import os
import argparse
import json

def list_directory_contents(path: str) -> dict:
    """Liste les fichiers et sous-répertoires d'un répertoire donné."""
    try:
        items = os.listdir(path)
        files = [item for item in items if os.path.isfile(os.path.join(path, item))]
        directories = [item for item in items if os.path.isdir(os.path.join(path, item))]
        return {"files": files, "directories": directories}
    except Exception as e:
        return {f"Erreur lors du listage du répertoire : {e}"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Liste les fichiers et sous-répertoires d'un répertoire donné.")
    parser.add_argument("path", type=str, help="Chemin du répertoire à lister.")
    args = parser.parse_args()
    result = list_directory_contents(args.path)
    print(json.dumps(result, indent=2, ensure_ascii=False))
