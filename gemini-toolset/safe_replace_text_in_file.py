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

def _replace_text_in_file_internal(path: str, old_text: str, new_text: str, all_occurrences: bool = False) -> bool:
    """Remplace la première ou toutes les occurrences d'un texte dans un fichier (usage interne)."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if all_occurrences:
            new_content = content.replace(old_text, new_text)
        else:
            new_content = content.replace(old_text, new_text, 1)
            
        if new_content == content:
            return False

        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception:
        return False

def safe_replace_text_in_file(path: str, old_text: str, new_text: str, all_occurrences: bool = False) -> bool:
    """Remplace du texte dans un fichier et log les différences (diff)."""
    original_content = _read_file_content_internal(path)
    if "Erreur" in original_content: # Simple vérification d'erreur
        print(f"Erreur lors de la lecture du fichier original: {original_content}")
        return False

    success = _replace_text_in_file_internal(path, old_text, new_text, all_occurrences)

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
        print("\n--- Différence de modification ---")
        for line in diff:
            print(line.strip('\n'))
        print("----------------------------------")
    
    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remplace du texte dans un fichier et log les différences.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("old_text", type=str, help="Texte à remplacer.")
    parser.add_argument("new_text", type=str, help="Nouveau texte.")
    parser.add_argument("--all_occurrences", action="store_true", help="Remplacer toutes les occurrences.")
    args = parser.parse_args()
    result = safe_replace_text_in_file(args.path, args.old_text, args.new_text, args.all_occurrences)
    print(result)
