import os
import argparse
import difflib
import sys
import fnmatch

# Assure que le répertoire de l'outil est dans sys.path pour les imports internes
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Importe les outils Alma_toolset nécessaires
from safe_read_file_content import safe_read_file_content
from safe_overwrite_file import safe_overwrite_file
from _string_utils import _perform_string_replacement, _perform_word_boundary_replacement

def replace_text_in_project(old_text: str, new_text: str, include_patterns: list = None, exclude_patterns: list = None, word_boundaries: bool = False, debug: bool = False) -> list:
    """Recherche et remplace du texte dans plusieurs fichiers, en logant les différences."""
    if debug:
        print(f"[DEBUG - replace_text_in_project] Recherche de '{old_text}' pour remplacer par '{new_text}'", file=sys.stderr)
        print(f"[DEBUG - replace_text_in_project] Inclure: {include_patterns}, Exclure: {exclude_patterns}", file=sys.stderr)
        print(f"[DEBUG - replace_text_in_project] Limites de mots: {word_boundaries}", file=sys.stderr)

    modified_files = []
    
    # Parcourir tous les fichiers du répertoire courant et de ses sous-répertoires
    for root, _, files in os.walk(os.getcwd()):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            # Appliquer les filtres d'inclusion/exclusion avec fnmatch pour les patterns
            if include_patterns:
                if not any(fnmatch.fnmatch(file_name, pattern) for pattern in include_patterns):
                    continue
            if exclude_patterns:
                if any(excluded_pattern in file_path for excluded_pattern in exclude_patterns):
                    continue

            if debug:
                print(f"[DEBUG - replace_text_in_project] Traitement du fichier: {file_path}", file=sys.stderr)

            original_content = safe_read_file_content(file_path, debug=debug)
            if original_content.startswith("Erreur lors de la lecture du fichier"):
                if debug:
                    print(f"[DEBUG - replace_text_in_project] Ignoré (erreur de lecture): {file_path}", file=sys.stderr)
                continue

            if old_text in original_content:
                # Choisir la méthode de remplacement selon le paramètre word_boundaries
                if word_boundaries:
                    new_content = _perform_word_boundary_replacement(original_content, old_text, new_text, all_occurrences=True, debug=debug)
                else:
                    new_content = _perform_string_replacement(original_content, old_text, new_text, all_occurrences=True, debug=debug)

                if new_content != original_content:
                    if safe_overwrite_file(file_path, new_content, debug=debug):
                        modified_files.append(file_path)
                        if debug:
                            print(f"[DEBUG - replace_text_in_project] Fichier modifié: {file_path}", file=sys.stderr)
                    else:
                        if debug:
                            print(f"[DEBUG - replace_text_in_project] Échec de l'écriture pour: {file_path}", file=sys.stderr)
            else:
                if debug:
                    print(f"[DEBUG - replace_text_in_project] '{old_text}' non trouvé dans: {file_path}", file=sys.stderr)

    return modified_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recherche et remplace du texte dans plusieurs fichiers.")
    parser.add_argument("old_text", type=str, help="Texte à rechercher.")
    parser.add_argument("new_text", type=str, help="Texte de remplacement.")
    parser.add_argument("--include", nargs='*', help="Patterns de fichiers à inclure (ex: *.py, *.md).")
    parser.add_argument("--exclude", nargs='*', help="Patterns de chemins à exclure (ex: .git, __pycache__).")
    parser.add_argument("--word-boundaries", action="store_true", help="Utilise les limites de mots pour le remplacement (évite les remplacements partiels).")
    parser.add_argument("--debug", action="store_true", help="Active le mode débogage.")
    args = parser.parse_args()

    modified_files = replace_text_in_project(args.old_text, args.new_text, args.include, args.exclude, word_boundaries=args.word_boundaries, debug=args.debug)
    if modified_files:
        print("\nFichiers modifiés:")
        for f in modified_files:
            print(f)
    else:
        print("Aucun fichier modifié.")