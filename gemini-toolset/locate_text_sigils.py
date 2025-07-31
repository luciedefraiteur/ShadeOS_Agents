import os
import argparse
import json

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
    parser = argparse.ArgumentParser(description="Cherche un texte dans un fichier et retourne les numéros de ligne de début et de fin du bloc de contexte pour chaque occurrence.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("text_to_find", type=str, help="Texte à chercher.")
    parser.add_argument("--context_lines", type=int, default=3, help="Nombre de lignes de contexte.")
    args = parser.parse_args()
    result = locate_text_sigils(args.path, args.text_to_find, args.context_lines)
    print(json.dumps(result, indent=2, ensure_ascii=False))
