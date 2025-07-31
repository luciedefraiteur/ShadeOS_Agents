import os
import argparse

def read_file_chars(path: str, start_char: int, end_char: int) -> str:
    """Lit et retourne une plage de caractères spécifique d'un fichier."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content[start_char:end_char]
    except Exception as e:
        return f"Erreur lors de la lecture des caractères du fichier : {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lit une plage de caractères spécifique d'un fichier.")
    parser.add_argument("path", type=str, help="Chemin du fichier à lire.")
    parser.add_argument("start_char", type=int, help="Caractère de début (0-basé).")
    parser.add_argument("end_char", type=int, help="Caractère de fin (0-basé).")
    args = parser.parse_args()
    result = read_file_chars(args.path, args.start_char, args.end_char)
    print(result)
