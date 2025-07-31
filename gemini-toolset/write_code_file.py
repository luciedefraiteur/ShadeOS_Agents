import os
import argparse

def write_code_file(path: str, content: str) -> bool:
    """Écrit du contenu dans un fichier, écrasant le contenu existant."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Écrit du contenu dans un fichier.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("content", type=str, help="Contenu à écrire.")
    args = parser.parse_args()
    result = write_code_file(args.path, args.content)
    print(result)
