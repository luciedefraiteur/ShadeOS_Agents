def read_file_content(path: str) -> str:
    """Lit et retourne tout le contenu d'un fichier texte."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Erreur lors de la lecture du fichier : {e}"

def read_file_lines(path: str, start_line: int, end_line: int) -> list[str]:
    """Lit et retourne une plage de lignes spécifiques d'un fichier."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return [line.strip('\n') for line in lines[start_line-1:end_line]]
    except Exception as e:
        return [f"Erreur lors de la lecture des lignes du fichier : {e}"]

def read_file_chars(path: str, start_char: int, end_char: int) -> str:
    """Lit et retourne une plage de caractères spécifique d'un fichier."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content[start_char:end_char]
    except Exception as e:
        return f"Erreur lors de la lecture des caractères du fichier : {e}"