import os
import argparse

def insert_text_at_line(path: str, line_number: int, text_to_insert: str) -> bool:
    """Insère un bloc de texte à une ligne spécifique, décalant le reste."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        lines.insert(line_number - 1, text_to_insert + '\n')

        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Insère un bloc de texte à une ligne spécifique.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("line_number", type=int, help="Numéro de ligne (1-basé).")
    parser.add_argument("text_to_insert", type=str, help="Texte à insérer.")
    args = parser.parse_args()
    result = insert_text_at_line(args.path, args.line_number, args.text_to_insert)
    print(result)


