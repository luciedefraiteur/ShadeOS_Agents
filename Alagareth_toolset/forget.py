import os
import argparse
import sys

# Assure que le répertoire de l'outil est dans sys.path pour les imports internes
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Importe l'instance du moteur de mémoire
from Core.Archivist.MemoryEngine.engine import memory_engine

def forget(path: str, debug: bool = False) -> bool:
    """Supprime un souvenir de la mémoire fractale."""
    if debug:
        print(f"[DEBUG - forget] Tentative de suppression de mémoire: {path}", file=sys.stderr)

    try:
        # Nous devrons ajouter une méthode delete_memory au MemoryEngine
        # Pour l'instant, nous allons simuler la suppression ou gérer l'erreur si la méthode n'existe pas
        if hasattr(memory_engine, 'delete_memory'):
            success = memory_engine.delete_memory(path)
            if debug:
                print(f"[DEBUG - forget] Suppression de mémoire réussie: {success}", file=sys.stderr)
            return success
        else:
            error_msg = "La méthode 'delete_memory' n'est pas implémentée dans MemoryEngine."
            if debug:
                print(f"[DEBUG - forget] {error_msg}", file=sys.stderr)
            print(error_msg, file=sys.stderr)
            return False
    except Exception as e:
        error_msg = f"Erreur lors de la suppression de la mémoire '{path}': {e}"
        if debug:
            print(f"[DEBUG - forget] {error_msg}", file=sys.stderr)
        print(error_msg, file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Supprime un souvenir de la mémoire fractale.")
    parser.add_argument("path", type=str, help="Chemin du souvenir à supprimer.")
    parser.add_argument("--debug", action="store_true", help="Active le mode débogage.")
    args = parser.parse_args()

    result = forget(args.path, debug=args.debug)
    print(result)
