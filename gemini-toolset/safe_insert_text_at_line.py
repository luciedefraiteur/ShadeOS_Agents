import os
import argparse
import difflib

# Importe les outils gemini-toolset nécessaires
from safe_read_file_content import safe_read_file_content
from safe_overwrite_file import safe_overwrite_file

def safe_insert_text_at_line(path: str, line_number: int, text_to_insert: str) -> bool:
    """Insère un bloc de texte à une ligne spécifique, décalant le reste, et log les différences (diff)."""
    original_content = safe_read_file_content(path)
    if "Erreur" in original_content: # Simple vérification d'erreur
        print(f"Erreur lors de la lecture du fichier original: {original_content}")
        return False

    original_lines = original_content.splitlines(keepends=True)
    new_lines_list = original_lines[:line_number - 1] + [text_to_insert + '\n'] + original_lines[line_number - 1:]
    new_content = "".join(new_lines_list)

    success = safe_overwrite_file(path, new_content)

    if success:
        # safe_overwrite_file gère déjà le diff, mais nous pouvons le refaire ici pour la cohérence
        # ou simplement afficher un message de succès.
        print(f"Insertion réussie dans {path} à la ligne {line_number}.")
        return True
    else:
        print(f"Erreur lors de l'écriture du fichier modifié: {path}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Insère un bloc de texte à une ligne spécifique, décalant le reste, et log les différences.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("line_number", type=int, help="Numéro de ligne (1-basé).")
    parser.add_argument("text_to_insert", type=str, help="Texte à insérer.")
    args = parser.parse_args()
    result = safe_insert_text_at_line(args.path, args.line_number, args.text_to_insert)
    print(result)