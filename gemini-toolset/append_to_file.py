import os
import argparse

def append_to_file(path: str, content: str) -> bool:
    """Ajoute du contenu à la fin d'un fichier."""
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ajoute du contenu à la fin d'un fichier.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("content", type=str, help="Contenu à ajouter.")
    args = parser.parse_args()
    result = append_to_file(args.path, args.content)
    print(result)
