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

def _insert_text_at_line_internal(path: str, line_number: int, text_to_insert: str) -> bool:
    """Insère un bloc de texte à une ligne spécifique, décalant le reste (usage interne)."""
    try:
        with open(path, 'r', encoding='utf-2') as f:
            lines = f.readlines()
        
        lines.insert(line_number - 1, text_to_insert + '\n')

        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    except Exception:
        return False

def safe_insert_text_at_line(path: str, line_number: int, text_to_insert: str) -> bool:
    """Insère un bloc de texte à une ligne spécifique, décalant le reste, et log les différences (diff)."""
    original_content = _read_file_content_internal(path)
    if "Erreur" in original_content: # Simple vérification d'erreur
        print(f"Erreur lors de la lecture du fichier original: {original_content}")
        return False

    success = _insert_text_at_line_internal(path, line_number, text_to_insert)

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
    parser = argparse.ArgumentParser(description="Insère un bloc de texte à une ligne spécifique, décalant le reste, et log les différences.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("line_number", type=int, help="Numéro de ligne (1-basé).")
    parser.add_argument("text_to_insert", type=str, help="Texte à insérer.")
    args = parser.parse_args()
    result = safe_insert_text_at_line(args.path, args.line_number, args.text_to_insert)
    print(result)
