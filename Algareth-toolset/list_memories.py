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

def list_memories(path: str = '.', list_type: str = "children", debug: bool = False) -> list:
    """Liste les enfants directs ou les liens interdimensionnels d'un nœud mémoire."""
    if debug:
        print(f"[DEBUG - list_memories] Tentative de lister '{list_type}' pour: {path}", file=sys.stderr)

    try:
        if list_type == "children":
            results = memory_engine.list_children(path)
        elif list_type == "links":
            results = memory_engine.list_links(path)
        else:
            error_msg = f"Type de liste invalide: {list_type}. Utilisez 'children' ou 'links'."
            if debug:
                print(f"[DEBUG - list_memories] {error_msg}", file=sys.stderr)
            print(error_msg, file=sys.stderr)
            return []
        
        if debug:
            print(f"[DEBUG - list_memories] Listing réussi pour: {path}, type: {list_type}", file=sys.stderr)
        return results
    except Exception as e:
        error_msg = f"Erreur lors du listage des mémoires pour '{path}' ({list_type}): {e}"
        if debug:
            print(f"[DEBUG - list_memories] {error_msg}", file=sys.stderr)
        print(error_msg, file=sys.stderr)
        return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Liste les enfants directs ou les liens interdimensionnels d'un nœud mémoire.")
    parser.add_argument("path", type=str, nargs='?', default='.', help="Chemin du souvenir (par défaut: .).")
    parser.add_argument("--type", type=str, default="children", choices=["children", "links"], help="Type de liste: 'children' ou 'links' (par défaut: children).")
    parser.add_argument("--debug", action="store_true", help="Active le mode débogage.")
    args = parser.parse_args()

    result = list_memories(args.path, args.type, debug=args.debug)
    print(json.dumps(result, indent=2, ensure_ascii=False))
