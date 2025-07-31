import os
import argparse
import difflib
import json

def _read_file_content_internal(path: str) -> str:
    """Lit et retourne tout le contenu d'un fichier texte (usage interne)."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Erreur lors de la lecture du fichier : {e}"

def _replace_lines_in_file_internal(path: str, start_line: int, end_line: int, new_lines: list[str]) -> bool:
    """Remplace une plage de lignes par de nouvelles lignes (usage interne)."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_content_lines = lines[:start_line-1] + [l + '\n' for l in new_lines] + lines[end_line:]

        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_content_lines)
        return True
    except Exception:
        return False

def safe_replace_lines_in_file(path: str, start_line: int, end_line: int, new_lines: list[str]) -> bool:
    """Remplace une plage de lignes par de nouvelles lignes et log les différences (diff)."""
    original_content = _read_file_content_internal(path)
    if "Erreur" in original_content: # Simple vérification d'erreur
        print(f"Erreur lors de la lecture du fichier original: {original_content}")
        return False

    success = _replace_lines_in_file_internal(path, start_line, end_line, new_lines)

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
    parser = argparse.ArgumentParser(description="Remplace une plage de lignes par de nouvelles lignes et log les différences.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("start_line", type=int, help="Ligne de début (1-basé).")
    parser.add_argument("end_line", type=int, help="Ligne de fin (1-basé).")
    parser.add_argument("new_lines", type=str, nargs='+', help="Nouvelles lignes (chaînes de caractères, séparées par des espaces).")
    args = parser.parse_args()
    result = safe_replace_lines_in_file(args.path, args.start_line, args.end_line, args.new_lines)
    print(result)
