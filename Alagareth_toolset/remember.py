import os
import argparse
import json
import sys

# Assure que le répertoire de l'outil est dans sys.path pour les imports internes
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Importe l'instance du moteur de mémoire
from Core.Archivist.MemoryEngine.engine import memory_engine

def remember(path: str, content: str, summary: str, keywords: list, links: list = None, debug: bool = False) -> bool:
    """Graver un nouveau souvenir dans la mémoire fractale."""
    if debug:
        print(f"[DEBUG - remember] Tentative de création de mémoire: {path}", file=sys.stderr)
        print(f"[DEBUG - remember] Contenu: {content[:50]}...", file=sys.stderr)
        print(f"[DEBUG - remember] Résumé: {summary}", file=sys.stderr)
        print(f"[DEBUG - remember] Mots-clés: {keywords}", file=sys.stderr)
        print(f"[DEBUG - remember] Liens: {links}", file=sys.stderr)

    try:
        success = memory_engine.create_memory(path, content, summary, keywords, links)
        if debug:
            print(f"[DEBUG - remember] Création de mémoire réussie: {success}", file=sys.stderr)
        return success
    except Exception as e:
        error_msg = f"Erreur lors de la création de la mémoire '{path}': {e}"
        if debug:
            print(f"[DEBUG - remember] {error_msg}", file=sys.stderr)
        print(error_msg, file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Graver un nouveau souvenir dans la mémoire fractale.")
    parser.add_argument("path", type=str, help="Chemin du souvenir (ex: mon_projet/analyse_bug_X).")
    parser.add_argument("content", type=str, help="Contenu détaillé du souvenir.")
    parser.add_argument("summary", type=str, help="Résumé succinct du souvenir.")
    parser.add_argument("keywords", type=str, nargs='+', help="Mots-clés associés au souvenir.")
    parser.add_argument("--links", type=str, nargs='*', help="Chemins vers d'autres souvenirs liés.")
    parser.add_argument("--debug", action="store_true", help="Active le mode débogage.")
    args = parser.parse_args()

    result = remember(args.path, args.content, args.summary, args.keywords, args.links, debug=args.debug)
    print(result)
