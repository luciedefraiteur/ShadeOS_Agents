import os
import argparse
import json

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
    parser = argparse.ArgumentParser(description="Marche récursivement dans un répertoire et retourne tous les chemins de fichiers.")
    parser.add_argument("path", type=str, help="Chemin du répertoire à parcourir.")
    args = parser.parse_args()
    result = walk_directory(args.path)
    print(json.dumps(result, indent=2, ensure_ascii=False))
