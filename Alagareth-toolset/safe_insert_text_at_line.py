import os
import argparse
import difflib
import sys

# Assure que le répertoire de l'outil est dans sys.path pour les imports internes
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Importe les outils Alagareth-toolset nécessaires
from safe_read_file_content import safe_read_file_content
from safe_overwrite_file import safe_overwrite_file

def safe_insert_text_at_line(path: str, line_number: int, text_to_insert: str, debug: bool = False) -> bool:
    """Insère un bloc de texte à une ligne spécifique, décalant le reste, et log les différences (diff)."""
    if debug:
        print(f"[DEBUG - safe_insert_text_at_line] Tentative d'insertion dans: {path} à la ligne {line_number}", file=sys.stderr)

    original_content = safe_read_file_content(path, debug=debug)
    
    # Vérifie si la lecture a retourné une erreur (commence par "Erreur lors de la lecture du fichier")
    if original_content.startswith("Erreur lors de la lecture du fichier"):
        if debug:
            print(f"[DEBUG - safe_insert_text_at_line] Erreur lors de la lecture du fichier original: {original_content}", file=sys.stderr)
        return False

    original_lines = original_content.splitlines(keepends=True)
    
    if debug:
        print(f"[DEBUG - safe_insert_text_at_line] Contenu original (lignes): {len(original_lines)}", file=sys.stderr)
        print(f"[DEBUG - safe_insert_text_at_line] Ligne d'insertion: {line_number}", file=sys.stderr)
        print(f"[DEBUG - safe_insert_text_at_line] Texte à insérer: '{text_to_insert}'", file=sys.stderr)

    # Vérifie si la ligne d'insertion est valide
    if not (1 <= line_number <= len(original_lines) + 1):
        error_msg = f"Numéro de ligne invalide {line_number} pour le fichier {path} (total {len(original_lines)} lignes)."
        if debug:
            print(f"[DEBUG - safe_insert_text_at_line] {error_msg}", file=sys.stderr)
        return False

    new_lines_list = original_lines[:line_number - 1] + [text_to_insert + '\n'] + original_lines[line_number - 1:]
    new_content = "".join(new_lines_list)

    if debug:
        print(f"[DEBUG - safe_insert_text_at_line] Nouveau contenu (lignes): {len(new_lines_list)}", file=sys.stderr)

    success = safe_overwrite_file(path, new_content, debug=debug)

    if success:
        if debug:
            print(f"[DEBUG - safe_insert_text_at_line] Insertion réussie dans {path} à la ligne {line_number}. Diff géré par safe_overwrite_file.", file=sys.stderr)
        return True
    else:
        if debug:
            print(f"[DEBUG - safe_insert_text_at_line] Erreur lors de l'écriture du fichier modifié: {path}", file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Insère un bloc de texte à une ligne spécifique, décalant le reste, et log les différences.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("line_number", type=int, help="Numéro de ligne (1-basé).")
    parser.add_argument("text_to_insert", type=str, help="Texte à insérer.")
    parser.add_argument("--debug", action="store_true", help="Active le mode débogage.")
    args = parser.parse_args()
    result = safe_insert_text_at_line(args.path, args.line_number, args.text_to_insert, debug=args.debug)
    print(result)
