import os
import argparse
import difflib

def _read_directory_structure_internal(path: str) -> str:
    """Lit et retourne une représentation simple de la structure d'un répertoire (usage interne)."""
    structure = []
    if os.path.exists(path):
        for root, dirs, files in os.walk(path):
            level = root.replace(path, '').count(os.sep)
            indent = ' ' * 4 * (level)
            structure.append(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                structure.append(f'{subindent}{f}')
    return "\n".join(structure)

def safe_create_directory(path: str) -> bool:
    """Crée un nouveau répertoire et log les différences (diff)."""
    # Capture l'état avant
    parent_dir = os.path.dirname(path) if os.path.dirname(path) else '.'
    original_structure = _read_directory_structure_internal(parent_dir)

    success = False
    try:
        os.makedirs(path, exist_ok=True)
        success = True
    except Exception as e:
        print(f"Erreur lors de la création du répertoire : {e}")
        return False

    if success:
        # Capture l'état après
        new_structure = _read_directory_structure_internal(parent_dir)

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
    args = parser.parse_args()
    result = safe_create_directory(args.path)
    print(result)
