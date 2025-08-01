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

def _overwrite_file(path: str, content: str) -> bool:
    """Écrit ou écrase un fichier avec le nouveau contenu (usage interne)."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

def safe_overwrite_file(path: str, content: str, debug: bool = False) -> bool:
    """Écrit ou écrase un fichier avec le nouveau contenu et log les différences (diff)."""
    if debug:
        print(f"[DEBUG - safe_overwrite_file] Tentative d'écriture dans: {path}", file=sys.stderr)

    original_content = safe_read_file_content(path, debug=debug)
    
    # Vérifie si la lecture a retourné une erreur (commence par "Erreur lors de la lecture du fichier")
    if original_content.startswith("Erreur lors de la lecture du fichier"):
        # Si le fichier n'existe pas, original_content sera une erreur, mais on peut quand même l'écrire
        if debug:
            print(f"[DEBUG - safe_overwrite_file] Fichier original non trouvé ou erreur de lecture: {original_content}. Procède à l'écriture.", file=sys.stderr)
        original_content = "" # Traite comme un fichier vide pour le diff

    success = _overwrite_file(path, content)

    if success:
        new_content = safe_read_file_content(path, debug=debug)
        if new_content.startswith("Erreur lors de la lecture du fichier"):
            if debug:
                print(f"[DEBUG - safe_overwrite_file] Erreur lors de la re-lecture du fichier modifié: {new_content}", file=sys.stderr)
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
        if debug:
            print(f"[DEBUG - safe_overwrite_file] Écriture réussie dans {path}.", file=sys.stderr)
        return True
    else:
        if debug:
            print(f"[DEBUG - safe_overwrite_file] Erreur lors de l'écriture du fichier: {path}", file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Écrit ou écrase un fichier avec le nouveau contenu et log les différences.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("content", type=str, help="Contenu à écrire.")
    parser.add_argument("--debug", action="store_true", help="Active le mode débogage.")
    args = parser.parse_args()
    result = safe_overwrite_file(args.path, args.content, debug=args.debug)
    print(result)
