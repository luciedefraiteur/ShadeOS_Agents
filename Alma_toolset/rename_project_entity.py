import os
import argparse
import sys

# Assure que le répertoire de l'outil est dans sys.path pour les imports internes
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Importe les outils Alma_toolset nécessaires
from safe_read_file_content import safe_read_file_content
from safe_overwrite_file import safe_overwrite_file
from replace_text_in_project import replace_text_in_project

def rename_project_entity(old_name: str, new_name: str, debug: bool = False) -> bool:
    """Renomme une entité (fichier ou dossier) dans le projet et met à jour ses références."""
    if debug:
        print(f"[DEBUG - rename_project_entity] Tentative de renommage de '{old_name}' en '{new_name}'", file=sys.stderr)

    # Phase 1: Renommage physique
    old_path = os.path.abspath(old_name)
    new_path = os.path.abspath(new_name)

    if not os.path.exists(old_path):
        error_msg = f"L'entité '{old_name}' n'existe pas."
        if debug:
            print(f"[DEBUG - rename_project_entity] {error_msg}", file=sys.stderr)
        print(error_msg, file=sys.stderr)
        return False

    try:
        os.rename(old_path, new_path)
        if debug:
            print(f"[DEBUG - rename_project_entity] Renommage physique réussi: {old_path} -> {new_path}", file=sys.stderr)
    except Exception as e:
        error_msg = f"Erreur lors du renommage physique de '{old_name}' en '{new_name}': {e}"
        if debug:
            print(f"[DEBUG - rename_project_entity] {error_msg}", file=sys.stderr)
        print(error_msg, file=sys.stderr)
        return False

    # Phase 2: Mise à jour des références dans le contenu des fichiers
    # Utilise une regex pour s'assurer de ne remplacer que le nom complet
    # Utilise des limites de mots () pour éviter les remplacements partiels
    modified_files = replace_text_in_project(old_name, new_name, include_patterns=[".py", ".luciform", ".md"], exclude_patterns=[".git", "__pycache__"], word_boundaries=True, debug=debug)

    if debug:
        if modified_files:
            print(f"[DEBUG - rename_project_entity] Références mises à jour dans: {modified_files}", file=sys.stderr)
        else:
            print(f"[DEBUG - rename_project_entity] Aucune référence trouvée pour '{old_name}' dans le contenu des fichiers.", file=sys.stderr)

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Renomme une entité (fichier ou dossier) dans le projet et met à jour ses références.")
    parser.add_argument("old_name", type=str, help="Ancien nom du fichier ou dossier.")
    parser.add_argument("new_name", type=str, help="Nouveau nom du fichier ou dossier.")
    parser.add_argument("--debug", action="store_true", help="Active le mode débogage.")
    args = parser.parse_args()

    result = rename_project_entity(args.old_name, args.new_name, debug=args.debug)
    print(result)
