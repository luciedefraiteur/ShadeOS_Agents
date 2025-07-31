import os
import argparse

def read_file_lines(path: str, start_line: int, end_line: int) -> list[str]:
    """Lit et retourne une plage de lignes spécifiques d'un fichier."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return [line.strip('\n') for line in lines[start_line-1:end_line]]
    except Exception as e:
        return [f"Erreur lors de la lecture des lignes du fichier : {e}"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lit une plage de lignes d'un fichier.")
    parser.add_argument("path", type=str, help="Chemin du fichier à lire.")
    parser.add_argument("start_line", type=int, help="Ligne de début (1-basé).")
    parser.add_argument("end_line", type=int, help="Ligne de fin (1-basé).")
    args = parser.parse_args()
    result = read_file_lines(args.path, args.start_line, args.end_line)
    for line in result:
        print(line)
