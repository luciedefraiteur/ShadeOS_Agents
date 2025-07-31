import os
import argparse

def overwrite_file(path: str, content: str) -> bool:
    """Écrit ou écrase un fichier avec le nouveau contenu."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Écrit ou écrase un fichier avec le nouveau contenu.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("content", type=str, help="Contenu à écrire.")
    args = parser.parse_args()
    result = overwrite_file(args.path, args.content)
    print(result)
