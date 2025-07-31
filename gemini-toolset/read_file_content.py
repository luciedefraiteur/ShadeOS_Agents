import os
import argparse

def read_file_content(path: str) -> str:
    """Lit et retourne tout le contenu d'un fichier texte."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Erreur lors de la lecture du fichier : {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lit le contenu complet d'un fichier.")
    parser.add_argument("path", type=str, help="Chemin du fichier à lire.")
    args = parser.parse_args()
    result = read_file_content(args.path)
    print(result)
