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