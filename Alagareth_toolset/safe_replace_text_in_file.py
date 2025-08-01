import os
import argparse
import difflib
import sys

# Assure que le répertoire de l'outil est dans sys.path pour les imports internes
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Importe les outils Alagareth_toolset nécessaires
from safe_read_file_content import safe_read_file_content
from safe_overwrite_file import safe_overwrite_file

def safe_replace_text_in_file(path: str, old_text: str, new_text: str, all_occurrences: bool = False, debug: bool = False) -> bool:
    """Remplace du texte dans un fichier et log les différences (diff)."""
    if debug:
        print(f"[DEBUG - safe_replace_text_in_file] Tentative de remplacement dans: {path}", file=sys.stderr)

    original_content = safe_read_file_content(path, debug=debug)
    if original_content.startswith("Erreur lors de la lecture du fichier"):
        if debug:
            print(f"[DEBUG - safe_replace_text_in_file] Erreur lors de la lecture du fichier original: {original_content}", file=sys.stderr)
        return False

    if old_text not in original_content:
        if debug:
            print(f"[DEBUG - safe_replace_text_in_file] '{old_text}' non trouvé dans: {path}", file=sys.stderr)
        return False

    if all_occurrences:
        new_content = original_content.replace(old_text, new_text)
    else:
        new_content = original_content.replace(old_text, new_text, 1)

    if new_content == original_content:
        if debug:
            print(f"[DEBUG - safe_replace_text_in_file] Aucun changement détecté pour '{old_text}' dans {path}.", file=sys.stderr)
        return False

    success = safe_overwrite_file(path, new_content, debug=debug)

    if success:
        if debug:
            print(f"[DEBUG - safe_replace_text_in_file] Remplacement réussi dans {path}. Diff géré par safe_overwrite_file.", file=sys.stderr)
        return True
    else:
        if debug:
            print(f"[DEBUG - safe_replace_text_in_file] Erreur lors de l'écriture du fichier modifié: {path}", file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remplace du texte dans un fichier et log les différences.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("old_text", type=str, help="Texte à remplacer.")
    parser.add_argument("new_text", type=str, help="Nouveau texte.")
    parser.add_argument("--all_occurrences", action="store_true", help="Remplacer toutes les occurrences.")
    parser.add_argument("--debug", action="store_true", help="Active le mode débogage.")
    args = parser.parse_args()
    result = safe_replace_text_in_file(args.path, args.old_text, args.new_text, args.all_occurrences, debug=args.debug)
    print(result)