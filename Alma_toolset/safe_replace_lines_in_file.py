import os
import argparse
import difflib
import sys

# Assure que le répertoire de l'outil est dans sys.path pour les imports internes
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Importe les outils Alma_toolset nécessaires
from safe_read_file_content import safe_read_file_content
from safe_overwrite_file import safe_overwrite_file

def safe_replace_lines_in_file(path: str, start_line: int, end_line: int, new_lines: list[str], debug: bool = False) -> bool:
    """Remplace une plage de lignes par de nouvelles lignes et log les différences (diff)."""
    if debug:
        print(f"[DEBUG - safe_replace_lines_in_file] Tentative de remplacement de lignes dans: {path} de la ligne {start_line} à {end_line}", file=sys.stderr)

    original_content = safe_read_file_content(path, debug=debug)
    if original_content.startswith("Erreur lors de la lecture du fichier"):
        if debug:
            print(f"[DEBUG - safe_replace_lines_in_file] Erreur lors de la lecture du fichier original: {original_content}", file=sys.stderr)
        return False

    original_lines = original_content.splitlines(keepends=True)
    
    if debug:
        print(f"[DEBUG - safe_replace_lines_in_file] Contenu original (lignes): {len(original_lines)}", file=sys.stderr)
        print(f"[DEBUG - safe_replace_lines_in_file] Lignes à remplacer: {start_line}-{end_line}", file=sys.stderr)
        print(f"[DEBUG - safe_replace_lines_in_file] Nouvelles lignes: {new_lines}", file=sys.stderr)

    # Vérifie si les lignes à remplacer sont valides
    if not (1 <= start_line <= end_line <= len(original_lines) + 1):
        error_msg = f"Plage de lignes invalide {start_line}-{end_line} pour le fichier {path} (total {len(original_lines)} lignes)."
        if debug:
            print(f"[DEBUG - safe_replace_lines_in_file] {error_msg}", file=sys.stderr)
        return False

    new_lines_list = original_lines[:start_line - 1] + [l + '\n' for l in new_lines] + original_lines[end_line:]
    new_content = "".join(new_lines_list)

    if debug:
        print(f"[DEBUG - safe_replace_lines_in_file] Nouveau contenu (lignes): {len(new_lines_list)}", file=sys.stderr)

    success = safe_overwrite_file(path, new_content, debug=debug)

    if success:
        if debug:
            print(f"[DEBUG - safe_replace_lines_in_file] Remplacement réussi dans {path}. Diff géré par safe_overwrite_file.", file=sys.stderr)
        return True
    else:
        if debug:
            print(f"[DEBUG - safe_replace_lines_in_file] Erreur lors de l'écriture du fichier modifié: {path}", file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remplace une plage de lignes par de nouvelles lignes et log les différences.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("start_line", type=int, help="Ligne de début (1-basé).")
    parser.add_argument("end_line", type=int, help="Ligne de fin (1-basé).")
    parser.add_argument("new_lines", type=str, nargs='+', help="Nouvelles lignes (chaînes de caractères, séparées par des espaces).")
    parser.add_argument("--debug", action="store_true", help="Active le mode débogage.")
    args = parser.parse_args()
    result = safe_replace_lines_in_file(args.path, args.start_line, args.end_line, args.new_lines, debug=args.debug)
    print(result)