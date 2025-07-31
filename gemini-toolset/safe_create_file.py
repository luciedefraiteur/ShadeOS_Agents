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

def _create_file_internal(path: str, content: str = "") -> bool:
    """Crée un nouveau fichier avec un contenu optionnel. Échoue si le fichier existe déjà (usage interne)."""
    if os.path.exists(path):
        return False
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

def safe_create_file(path: str, content: str = "") -> bool:
    """Crée un nouveau fichier et log les différences (diff)."""
    success = _create_file_internal(path, content)

    if success:
        new_content = _read_file_content_internal(path)
        if "Erreur" in new_content: # Simple vérification d'erreur
            print(f"Erreur lors de la lecture du fichier créé: {new_content}")
            return False

        # Génère un diff contre un contenu vide pour montrer les ajouts
        diff = difflib.unified_diff(
            "".splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{os.path.basename(path)}",
            tofile=f"b/{os.path.basename(path)}",
            lineterm='' # Pour éviter les doubles retours à la ligne
        )
        print("\n--- Différence de création ---")
        for line in diff:
            print(line.strip('\n'))
        print("----------------------------------")
    
    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crée un nouveau fichier et log les différences.")
    parser.add_argument("path", type=str, help="Chemin du fichier à créer.")
    parser.add_argument("--content", type=str, default="", help="Contenu optionnel du fichier.")
    args = parser.parse_args()
    result = safe_create_file(args.path, args.content)
    print(result)
