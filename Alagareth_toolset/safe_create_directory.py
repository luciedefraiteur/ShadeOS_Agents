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

def _read_directory_structure(path: str, debug: bool = False) -> str:
    """Lit et retourne une représentation simple de la structure d'un répertoire (usage interne)."""
    if debug:
        print(f"[DEBUG - _read_directory_structure] Lecture de la structure de: {path}", file=sys.stderr)
    structure = []
    if os.path.exists(path):
        for root, dirs, files in os.walk(path):
            level = root.replace(path, '').count(os.sep)
            indent = ' ' * 4 * (level)
            structure.append(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                structure.append(f'{subindent}{f}')
    if debug:
        print(f"[DEBUG - _read_directory_structure] Structure lue:\n{os.linesep.join(structure)}", file=sys.stderr)
    return "\n".join(structure)

def safe_create_directory(path: str, debug: bool = False) -> bool:
    """Crée un nouveau répertoire et log les différences (diff)."""
    if debug:
        print(f"[DEBUG - safe_create_directory] Tentative de création de répertoire: {path}", file=sys.stderr)

    # Capture l'état avant
    parent_dir = os.path.dirname(path) if os.path.dirname(path) else '.'
    original_structure = _read_directory_structure(parent_dir, debug=debug)

    success = False
    try:
        os.makedirs(path, exist_ok=True)
        success = True
    except Exception as e:
        error_msg = f"Erreur lors de la création du répertoire '{path}': {e}"
        if debug:
            print(f"[DEBUG - safe_create_directory] {error_msg}", file=sys.stderr)
        print(error_msg, file=sys.stderr)
        return False

    if success:
        if debug:
            print(f"[DEBUG - safe_create_directory] Répertoire '{path}' créé avec succès.", file=sys.stderr)
        # Capture l'état après
        new_structure = _read_directory_structure(parent_dir, debug=debug)

        diff = difflib.unified_diff(
            original_structure.splitlines(keepends=True),
            new_structure.splitlines(keepends=True),
            fromfile=f"a/{os.path.basename(parent_dir)}/",
            tofile=f"b/{os.path.basename(parent_dir)}/",
            lineterm=''
        )
        print("\n--- Différence de création de répertoire ---")
        for line in diff:
            print(line.strip('\n'))
        print("----------------------------------")
    
    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crée un nouveau répertoire et log les différences.")
    parser.add_argument("path", type=str, help="Chemin du répertoire à créer.")
    parser.add_argument("--debug", action="store_true", help="Active le mode débogage.")
    args = parser.parse_args()
    result = safe_create_directory(args.path, debug=args.debug)
    print(result)
