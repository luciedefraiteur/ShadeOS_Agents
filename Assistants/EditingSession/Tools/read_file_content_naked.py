import os
import argparse

def read_file_content_naked(path: str) -> str:
    """Lit et retourne tout le contenu d'un fichier texte, sans aucun décorateur."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Erreur : {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lit le contenu brut d'un fichier.")
    parser.add_argument("path", type=str, help="Chemin du fichier à lire.")
    args = parser.parse_args()
    result = read_file_content_naked(args.path)
    print(result)
