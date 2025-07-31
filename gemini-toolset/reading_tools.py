import os
import argparse
import sys

def read_file_content(path: str) -> str:
    """Lit et retourne tout le contenu d'un fichier texte."""
    try:
        print(f"DEBUG: Attempting to open: {path}", file=sys.stderr)
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Erreur lors de la lecture du fichier : {e}"

def read_file_lines(path: str, start_line: int, end_line: int) -> list[str]:
    """Lit et retourne une plage de lignes spécifiques d'un fichier."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return [line.strip('\n') for line in lines[start_line-1:end_line]]
    except Exception as e:
        return [f"Erreur lors de la lecture des lignes du fichier : {e}"]

def read_file_chars(path: str, start_char: int, end_char: int) -> str:
    """Lit et retourne une plage de caractères spécifique d'un fichier."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content[start_char:end_char]
    except Exception as e:
        return f"Erreur lors de la lecture des caractères du fichier : {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Outils de lecture de fichiers.")
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")

    # Subparser pour read_file_content
    parser_content = subparsers.add_parser("content", help="Lit le contenu complet d'un fichier.")
    parser_content.add_argument("path", type=str, help="Chemin du fichier à lire.")

    # Subparser pour read_file_lines
    parser_lines = subparsers.add_parser("lines", help="Lit une plage de lignes d'un fichier.")
    parser_lines.add_argument("path", type=str, help="Chemin du fichier à lire.")
    parser_lines.add_argument("start_line", type=int, help="Ligne de début (1-basé).")
    parser_lines.add_argument("end_line", type=int, help="Ligne de fin (1-basé).")

    # Subparser pour read_file_chars
    parser_chars = subparsers.add_parser("chars", help="Lit une plage de caractères d'un fichier.")
    parser_chars.add_argument("path", type=str, help="Chemin du fichier à lire.")
    parser_chars.add_argument("start_char", type=int, help="Caractère de début (0-basé).")
    parser_chars.add_argument("end_char", type=int, help="Caractère de fin (0-basé).")

    args = parser.parse_args()

    if args.command == "content":
        result = read_file_content(args.path)
        print(result)
    elif args.command == "lines":
        result = read_file_lines(args.path, args.start_line, args.end_line)
        for line in result:
            print(line)
    elif args.command == "chars":
        result = read_file_chars(args.path, args.start_char, args.end_char)
        print(result)
    else:
        parser.print_help()
