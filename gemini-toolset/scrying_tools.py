def scry_for_text(path: str, text_to_find: str, context_lines: int = 3) -> list[dict]:
    """Cherche un texte dans un fichier et retourne chaque occurrence avec un nombre défini de lignes de contexte avant et après."""
    results = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [line.strip('\n') for line in f.readlines()]
        
        for i, line in enumerate(lines):
            if text_to_find in line:
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                context = lines[start:end]
                results.append({
                    "line_number": i + 1,
                    "match": line,
                    "context": context
                })
        return results
    except Exception as e:
        return [{f"Erreur lors de la divination du texte : {e}"}]

def locate_text_sigils(path: str, text_to_find: str, context_lines: int = 3) -> list[dict]:
    """Cherche un texte dans un fichier et retourne les numéros de ligne de début et de fin du bloc de contexte pour chaque occurrence."""
    results = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            if text_to_find in line:
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                results.append({
                    "match_line": i + 1,
                    "context_start": start + 1,
                    "context_end": end
                })
        return results
    except Exception as e:
        return [{f"Erreur lors de la localisation des sceaux textuels : {e}"}]