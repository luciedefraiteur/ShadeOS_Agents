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

def safe_create_file(path: str, content: str = "") -> bool:
    """Crée un nouveau fichier et log les différences (diff)."""
    # Pour le diff, on considère le contenu original comme vide
    original_content = ""

    success = safe_overwrite_file(path, content, debug=True) # Utilise safe_overwrite_file pour l'écriture

    if success:
        new_content = safe_read_file_content(path, debug=True)
        if new_content.startswith("Erreur lors de la re-lecture du fichier"):
            print(f"Erreur lors de la re-lecture du fichier créé: {new_content}", file=sys.stderr)
            return False

        diff = difflib.unified_diff(
            original_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{os.path.basename(path)}",
            tofile=f"b/{os.path.basename(path)}",
            lineterm='' # Pour éviter les doubles retours à la ligne
        )
        print("\n--- Différence de création ---")
        for line in diff:
            print(line.strip('\n'))
        print("----------------------------------")
    
    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crée un nouveau fichier et log les différences.")
    parser.add_argument("path", type=str, help="Chemin du fichier à créer.")
    parser.add_argument("--content", type=str, default="", help="Contenu optionnel du fichier.")
    parser.add_argument("--debug", action="store_true", help="Active le mode débogage.")
    args = parser.parse_args()
    result = safe_create_file(args.path, args.content, debug=args.debug)
    print(result)