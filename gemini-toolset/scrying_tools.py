import os
import argparse
import json

def scry_for_text(path: str, text_to_find: str, context_lines: int = 3) -> list[dict]:
    """Cherche un texte dans un fichier et retourne chaque occurrence avec un nombre défini de lignes de contexte avant et après."""
    results = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [line.strip('\n') for line in f.readlines()]
        
        for i, line in enumerate(lines):
            if text_to_find in line:
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                context = lines[start:end]
                results.append({
                    "line_number": i + 1,
                    "match": line,
                    "context": context
                })
        return results
    except Exception as e:
        return [{f"Erreur lors de la divination du texte : {e}"}]

def locate_text_sigils(path: str, text_to_find: str, context_lines: int = 3) -> list[dict]:
    """Cherche un texte dans un fichier et retourne les numéros de ligne de début et de fin du bloc de contexte pour chaque occurrence."""
    results = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            if text_to_find in line:
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                results.append({
                    "match_line": i + 1,
                    "context_start": start + 1,
                    "context_end": end
                })
        return results
    except Exception as e:
        return [{f"Erreur lors de la localisation des sceaux textuels : {e}"}]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Outils de divination de texte.")
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")

    # Subparser pour scry_for_text
    parser_scry = subparsers.add_parser("scry", help="Cherche un texte et retourne le contexte.")
    parser_scry.add_argument("path", type=str, help="Chemin du fichier.")
    parser_scry.add_argument("text_to_find", type=str, help="Texte à chercher.")
    parser_scry.add_argument("--context_lines", type=int, default=3, help="Nombre de lignes de contexte.")

    # Subparser pour locate_text_sigils
    parser_locate = subparsers.add_parser("locate", help="Cherche un texte et retourne les coordonnées.")
    parser_locate.add_argument("path", type=str, help="Chemin du fichier.")
    parser_locate.add_argument("text_to_find", type=str, help="Texte à chercher.")
    parser_locate.add_argument("--context_lines", type=int, default=3, help="Nombre de lignes de contexte.")

    args = parser.parse_args()

    if args.command == "scry":
        result = scry_for_text(args.path, args.text_to_find, args.context_lines)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "locate":
        result = locate_text_sigils(args.path, args.text_to_find, args.context_lines)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        parser.print_help()
