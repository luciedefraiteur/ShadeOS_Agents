from openai import tool

@tool
def scry_for_text(path: str, text_to_find: str, context_lines: int = 3) -> list[dict]:
    """Cherche un texte dans un fichier et retourne chaque occurrence avec un nombre défini de lignes de contexte avant et après."""
    __lucidoc__ = {
        "id": "scry_for_text",
        "type": "divination",
        "intent": "Révéler le contexte d’un symbole textuel dans un fichier.",
        "requires": ["path", "text_to_find"],
        "optional": ["context_lines"],
        "returns": "list of dicts: {line_number, match, context}",
        "ritual_keywords": ["scry", "divine", "seek", "context"],
        "symbolic_layer": "Lecture oraculaire. Les lignes deviennent des visions.",
        "usage_context": "À appeler quand un agent cherche à comprendre le sens profond d’un mot caché dans un grimoire brut.",
        "level": "intermédiaire"
    }
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

@tool
def locate_text_sigils(path: str, text_to_find: str, context_lines: int = 3) -> list[dict]:
    """Cherche un texte dans un fichier et retourne les numéros de ligne de début et de fin du bloc de contexte pour chaque occurrence."""
    __lucidoc__ = {
        "id": "locate_text_sigils",
        "type": "divination",
        "intent": "Révéler les coordonnées astrales (numéros de ligne) d’un texte et de son contexte.",
        "requires": ["path", "text_to_find"],
        "optional": ["context_lines"],
        "returns": "list of dicts: {match_line, context_start, context_end}",
        "ritual_keywords": ["locate", "sigil", "position", "coordinates"],
        "symbolic_layer": "Cartographie les échos d'une pensée sans la matérialiser.",
        "usage_context": "Pour planifier des modifications ou des lectures ciblées sans avoir à lire le contenu au préalable.",
        "level": "avancé"
    }
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
