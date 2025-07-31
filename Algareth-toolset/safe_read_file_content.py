import os
import argparse
import sys

# Assure que le répertoire de l'outil est dans sys.path pour les imports internes
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

def safe_read_file_content(path: str, debug: bool = False) -> str:
    """Lit et retourne tout le contenu d'un fichier texte, avec gestion d'erreur et mode débogage."""
    if debug:
        print(f"[DEBUG - safe_read_file_content] Tentative de lecture de: {path}", file=sys.stderr)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            if debug:
                print(f"[DEBUG - safe_read_file_content] Lecture réussie. Taille: {len(content)} octets.", file=sys.stderr)
            return content
    except Exception as e:
        error_msg = f"Erreur lors de la lecture du fichier '{path}': {e}"
        if debug:
            print(f"[DEBUG - safe_read_file_content] {error_msg}", file=sys.stderr)
        return error_msg

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lit le contenu complet d'un fichier en toute sécurité.")
    parser.add_argument("path", type=str, help="Chemin du fichier à lire.")
    parser.add_argument("--debug", action="store_true", help="Active le mode débogage.")
    args = parser.parse_args()
    result = safe_read_file_content(args.path, debug=args.debug)
    print(result)
