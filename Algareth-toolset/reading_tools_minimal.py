import os
import argparse
import sys

# Assure que le répertoire de l'outil est dans sys.path pour les imports internes
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

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
