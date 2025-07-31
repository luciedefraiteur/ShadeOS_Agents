import os
import argparse

def create_file(path: str, content: str = "") -> bool:
    """Crée un nouveau fichier avec un contenu optionnel. Échoue si le fichier existe déjà."""
    if os.path.exists(path):
        return False
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crée un nouveau fichier.")
    parser.add_argument("path", type=str, help="Chemin du fichier à créer.")
    parser.add_argument("--content", type=str, default="", help="Contenu optionnel du fichier.")
    args = parser.parse_args()
    result = create_file(args.path, args.content)
    print(result)
