import os
import argparse
import json

def replace_lines_in_file(path: str, start_line: int, end_line: int, new_lines: list[str]) -> bool:
    """Remplace une plage de lignes par de nouvelles lignes."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_content_lines = lines[:start_line-1] + [l + '\n' for l in new_lines] + lines[end_line:]

        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_content_lines)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remplace une plage de lignes par de nouvelles lignes.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("start_line", type=int, help="Ligne de début (1-basé).")
    parser.add_argument("end_line", type=int, help="Ligne de fin (1-basé).")
    parser.add_argument("new_lines", type=str, nargs='+', help="Nouvelles lignes (chaînes de caractères, séparées par des espaces).")
    args = parser.parse_args()
    result = replace_lines_in_file(args.path, args.start_line, args.end_line, args.new_lines)
    print(result)
