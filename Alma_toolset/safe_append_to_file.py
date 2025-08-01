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

def safe_append_to_file(path: str, content: str, debug: bool = False) -> bool:
    """Ajoute du contenu à la fin d'un fichier et log les différences (diff)."""
    if debug:
        print(f"[DEBUG - safe_append_to_file] Tentative d'ajout dans: {path}", file=sys.stderr)

    original_content = safe_read_file_content(path, debug=debug)
    if original_content.startswith("Erreur lors de la lecture du fichier"):
        if debug:
            print(f"[DEBUG - safe_append_to_file] Fichier original non trouvé ou erreur de lecture: {original_content}. Procède à l'ajout.", file=sys.stderr)
        original_content = "" # Traite comme un fichier vide pour le diff

    new_content = original_content + content

    success = safe_overwrite_file(path, new_content, debug=debug)

    if success:
        if debug:
            print(f"[DEBUG - safe_append_to_file] Ajout réussi dans {path}. Diff géré par safe_overwrite_file.", file=sys.stderr)
        return True
    else:
        if debug:
            print(f"[DEBUG - safe_append_to_file] Erreur lors de l'ajout au fichier: {path}", file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ajoute du contenu à la fin d'un fichier et log les différences.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("content", type=str, help="Contenu à ajouter.")
    parser.add_argument("--debug", action="store_true", help="Active le mode débogage.")
    args = parser.parse_args()
    result = safe_append_to_file(args.path, args.content, debug=args.debug)
    print(result)