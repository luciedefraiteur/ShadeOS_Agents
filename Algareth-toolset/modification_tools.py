import os
import argparse
import sys

# Assure que le répertoire de l'outil est dans sys.path pour les imports internes
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

def replace_text_in_file(path: str, old_text: str, new_text: str, all_occurrences: bool = False) -> bool:
    """Remplace la première ou toutes les occurrences d'un texte dans un fichier."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if all_occurrences:
            new_content = content.replace(old_text, new_text)
        else:
            new_content = content.replace(old_text, new_text, 1)
            
        if new_content == content:
            return False

        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception:
        return False

def replace_lines_in_file(path: str, start_line: int, end_line: int, new_lines: list[str]) -> bool:
    """Remplace une plage de lignes par de nouvelles lignes."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_content_lines = lines[:start_line-1] + [l + '\n' for l in new_lines] + lines[end_line:]

        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_content_lines)
        return True
    except Exception:
        return False

def insert_text_at_line(path: str, line_number: int, text_to_insert: str) -> bool:
    """Insère un bloc de texte à une ligne spécifique, décalant le reste."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        lines.insert(line_number - 1, text_to_insert + '\n')

        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Outils de modification de fichiers.")
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")

    # Subparser pour replace_text_in_file
    parser_replace_text = subparsers.add_parser("replace_text", help="Remplace du texte dans un fichier.")
    parser_replace_text.add_argument("path", type=str, help="Chemin du fichier.")
    parser_replace_text.add_argument("old_text", type=str, help="Texte à remplacer.")
    parser_replace_text.add_argument("new_text", type=str, help="Nouveau texte.")
    parser_replace_text.add_argument("--all_occurrences", action="store_true", help="Remplacer toutes les occurrences.")

    # Subparser pour replace_lines_in_file
    parser_replace_lines = subparsers.add_parser("replace_lines", help="Remplace une plage de lignes.")
    parser_replace_lines.add_argument("path", type=str, help="Chemin du fichier.")
    parser_replace_lines.add_argument("start_line", type=int, help="Ligne de début (1-basé).")
    parser_replace_lines.add_argument("end_line", type=int, help="Ligne de fin (1-basé).")
    parser_replace_lines.add_argument("new_lines", type=str, nargs='+', help="Nouvelles lignes.")

    # Subparser pour insert_text_at_line
    parser_insert_text = subparsers.add_parser("insert_text", help="Insère du texte à une ligne.")
    parser_insert_text.add_argument("path", type=str, help="Chemin du fichier.")
    parser_insert_text.add_argument("line_number", type=int, help="Numéro de ligne (1-basé).")
    parser_insert_text.add_argument("text_to_insert", type=str, help="Texte à insérer.")

    args = parser.parse_args()

    if args.command == "replace_text":
        result = replace_text_in_file(args.path, args.old_text, args.new_text, args.all_occurrences)
        print(result)
    elif args.command == "replace_lines":
        result = replace_lines_in_file(args.path, args.start_line, args.end_line, args.new_lines)
        print(result)
    elif args.command == "insert_text":
        result = insert_text_at_line(args.path, args.line_number, args.text_to_insert)
        print(result)
    else:
        parser.print_help()