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

def recall(path: str, debug: bool = False) -> dict:
    """Récupère le contenu complet d'un nœud mémoire sous forme de dictionnaire."""
    if debug:
        print(f"[DEBUG - recall] Tentative de récupération de mémoire: {path}", file=sys.stderr)

    try:
        node_data = memory_engine.get_memory_node(path)
        if debug:
            print(f"[DEBUG - recall] Récupération réussie pour: {path}", file=sys.stderr)
        return node_data
    except Exception as e:
        error_msg = f"Erreur lors de la récupération de la mémoire '{path}': {e}"
        if debug:
            print(f"[DEBUG - recall] {error_msg}", file=sys.stderr)
        print(error_msg, file=sys.stderr)
        return {"error": error_msg}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Récupère le contenu complet d'un nœud mémoire.")
    parser.add_argument("path", type=str, help="Chemin du souvenir à récupérer.")
    parser.add_argument("--debug", action="store_true", help="Active le mode débogage.")
    args = parser.parse_args()

    result = recall(args.path, debug=args.debug)
    print(json.dumps(result, indent=2, ensure_ascii=False))
