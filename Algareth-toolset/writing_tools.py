import os
import argparse
import sys

# Assure que le répertoire de l'outil est dans sys.path pour les imports internes
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

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

def append_to_file(path: str, content: str) -> bool:
    """Ajoute du contenu à la fin d'un fichier."""
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

def overwrite_file(path: str, content: str) -> bool:
    """Écrit ou écrase un fichier avec le nouveau contenu."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Outils d'écriture de fichiers.")
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")

    # Subparser pour create_file
    parser_create = subparsers.add_parser("create", help="Crée un nouveau fichier.")
    parser_create.add_argument("path", type=str, help="Chemin du fichier à créer.")
    parser_create.add_argument("--content", type=str, default="", help="Contenu optionnel du fichier.")

    # Subparser pour append_to_file
    parser_append = subparsers.add_parser("append", help="Ajoute du contenu à la fin d'un fichier.")
    parser_append.add_argument("path", type=str, help="Chemin du fichier.")
    parser_append.add_argument("content", type=str, help="Contenu à ajouter.")

    # Subparser pour overwrite_file
    parser_overwrite = subparsers.add_parser("overwrite", help="Écrit ou écrase un fichier.")
    parser_overwrite.add_argument("path", type=str, help="Chemin du fichier.")
    parser_overwrite.add_argument("content", type=str, help="Contenu à écrire.")

    args = parser.parse_args()

    if args.command == "create":
        result = create_file(args.path, args.content)
        print(result)
    elif args.command == "append":
        result = append_to_file(args.path, args.content)
        print(result)
    elif args.command == "overwrite":
        result = overwrite_file(args.path, args.content)
        print(result)
    else:
        parser.print_help()