import os
import argparse
import sys
import json

# Assure que le répertoire de l'outil est dans sys.path pour les imports internes
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Importe les outils Alagareth-toolset nécessaires
from safe_read_file_content import safe_read_file_content

def find_text_in_project(text_to_find: str, include_patterns: list = None, exclude_patterns: list = None, debug: bool = False) -> list:
    """Recherche un texte dans plusieurs fichiers et retourne les occurrences."""
    if debug:
        print(f"[DEBUG - find_text_in_project] Recherche de '{text_to_find}'", file=sys.stderr)
        print(f"[DEBUG - find_text_in_project] Inclure: {include_patterns}, Exclure: {exclude_patterns}", file=sys.stderr)

    found_occurrences = []
    
    # Parcourir tous les fichiers du répertoire courant et de ses sous-répertoires
    for root, _, files in os.walk(os.getcwd()):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            # Appliquer les filtres d'inclusion/exclusion
            if include_patterns:
                if not any(file_name.endswith(p) for p in include_patterns):
                    continue
            if exclude_patterns:
                if any(excluded_pattern in file_path for excluded_pattern in exclude_patterns):
                    continue

            if debug:
                print(f"[DEBUG - find_text_in_project] Traitement du fichier: {file_path}", file=sys.stderr)

            content = safe_read_file_content(file_path, debug=debug)
            if content.startswith("Erreur lors de la lecture du fichier"):
                if debug:
                    print(f"[DEBUG - find_text_in_project] Ignoré (erreur de lecture): {file_path}", file=sys.stderr)
                continue

            if text_to_find in content:
                for line_num, line in enumerate(content.splitlines(), 1):
                    if text_to_find in line:
                        found_occurrences.append({
                            "file_path": file_path,
                            "line_number": line_num,
                            "line_content": line.strip()
                        })
                        if debug:
                            print(f"[DEBUG - find_text_in_project] Trouvé dans: {file_path} (Ligne {line_num})", file=sys.stderr)

    return found_occurrences

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recherche un texte dans plusieurs fichiers et retourne les occurrences.")
    parser.add_argument("text_to_find", type=str, help="Texte à rechercher.")
    parser.add_argument("--include", nargs='*', help="Patterns de fichiers à inclure (ex: *.py, *.md).")
    parser.add_argument("--exclude", nargs='*', help="Patterns de chemins à exclure (ex: .git, __pycache__).")
    parser.add_argument("--debug", action="store_true", help="Active le mode débogage.")
    args = parser.parse_args()

    occurrences = find_text_in_project(args.text_to_find, args.include, args.exclude, debug=args.debug)
    if occurrences:
        print(json.dumps(occurrences, indent=2, ensure_ascii=False))
    else:
        print("Aucune occurrence trouvée.")
