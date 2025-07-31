import os
import argparse

def replace_text_in_file(path: str, old_text: str, new_text: str, all_occurrences: bool = False) -> bool:
    """Remplace la première ou toutes les occurrences d'un texte dans un fichier."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if all_occurrences:
            new_content = content.replace(old_text, new_text)
        else:
            new_content = content.replace(old_text, new_text, 1)
            
        if new_content == content:
            return False

        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remplace du texte dans un fichier.")
    parser.add_argument("path", type=str, help="Chemin du fichier.")
    parser.add_argument("old_text", type=str, help="Texte à remplacer.")
    parser.add_argument("new_text", type=str, help="Nouveau texte.")
    parser.add_argument("--all_occurrences", action="store_true", help="Remplacer toutes les occurrences.")
    args = parser.parse_args()
    result = replace_text_in_file(args.path, args.old_text, args.new_text, args.all_occurrences)
    print(result)
