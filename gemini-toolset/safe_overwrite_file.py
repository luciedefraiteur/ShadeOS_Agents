import os
import argparse
import difflib

def _read_file_content_internal(path: str) -> str:
    """Lit et retourne tout le contenu d'un fichier texte (usage interne)."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Erreur lors de la lecture du fichier : {e}"

def _overwrite_file_internal(path: str, content: str) -> bool:
    """Écrit ou écrase un fichier avec le nouveau contenu (usage interne)."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

def safe_overwrite_file(path: str, content: str) -> bool:
    """Écrit ou écrase un fichier avec le nouveau contenu et log les différences (diff)."""
    original_content = _read_file_content_internal(path)
    if "Erreur" in original_content: # Simple vérification d'erreur
        print(f"Erreur lors de la lecture du fichier original: {original_content}")
        return False

    success = _overwrite_file_internal(path, content)

    if success:
        new_content = _read_file_content_internal(path)
        if "Erreur" in new_content: # Simple vérification d'erreur
            print(f"Erreur lors de la lecture du fichier modifié: {new_content}")
            return False

        diff = difflib.unified_diff(
            original_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{os.path.basename(path)}",
            tofile=f"b/{os.path.basename(path)}",
            lineterm='' # Pour éviter les doubles retours à la ligne
        )
        print("\n--- Différence de remplacement ---")
        for line in diff:
            print(line.strip('\n'))
        print("----------------------------------")
    
    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Écrit ou écrase un fichier avec le nouveau contenu et log les différences.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("content", type=str, help="Contenu à écrire.")
    args = parser.parse_args()
    result = safe_overwrite_file(args.path, args.content)
    print(result)
