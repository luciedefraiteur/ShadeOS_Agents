import os
import argparse
import json
import sys

# Assure que le répertoire de l'outil est dans sys.path pour les imports internes
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Outils de listage de fichiers et répertoires.")
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")

    # Subparser pour list_directory_contents
    parser_list = subparsers.add_parser("list", help="Liste les fichiers et sous-répertoires d'un répertoire.")
    parser_list.add_argument("path", type=str, help="Chemin du répertoire à lister.")

    # Subparser pour walk_directory
    parser_walk = subparsers.add_parser("walk", help="Marche récursivement dans un répertoire.")
    parser_walk.add_argument("path", type=str, help="Chemin du répertoire à parcourir.")

    args = parser.parse_args()

    if args.command == "list":
        result = list_directory_contents(args.path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "walk":
        result = walk_directory(args.path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        parser.print_help()