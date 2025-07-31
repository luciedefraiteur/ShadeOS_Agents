from openai import tool

@tool
def read_file_content(path: str) -> str:
    """Lit et retourne tout le contenu d'un fichier texte."""
    __lucidoc__ = {
        "id": "read_file_content",
        "type": "reading",
        "intent": "Invoquer l'intégralité du contenu d'un fichier.",
        "requires": ["path"],
        "returns": "str: Le contenu complet du fichier.",
        "ritual_keywords": ["read", "content", "full", "file"],
        "symbolic_layer": "Absorbe l'âme d'un fichier en une seule inspiration.",
        "usage_context": "Quand une vue d'ensemble complète est nécessaire, sans se soucier des détails.",
        "level": "fondamental"
    }
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Erreur lors de la lecture du fichier : {e}"

@tool
def read_file_lines(path: str, start_line: int, end_line: int) -> list[str]:
    """Lit et retourne une plage de lignes spécifiques d'un fichier."""
    __lucidoc__ = {
        "id": "read_file_lines",
        "type": "reading",
        "intent": "Extraire une séquence précise de lignes d'un fichier.",
        "requires": ["path", "start_line", "end_line"],
        "returns": "list[str]: Les lignes demandées.",
        "ritual_keywords": ["read", "lines", "range", "extract"],
        "symbolic_layer": "Découpe un fragment du temps d'un fichier, ligne par ligne.",
        "usage_context": "Pour se concentrer sur une section spécifique d'un script ou d'un log.",
        "level": "fondamental"
    }
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Les numéros de ligne sont 1-based pour l'utilisateur
            return [line.strip('\n') for line in lines[start_line-1:end_line]]
    except Exception as e:
        return [f"Erreur lors de la lecture des lignes du fichier : {e}"]

@tool
def read_file_chars(path: str, start_char: int, end_char: int) -> str:
    """Lit et retourne une plage de caractères spécifique d'un fichier."""
    __lucidoc__ = {
        "id": "read_file_chars",
        "type": "reading",
        "intent": "Matérialiser une tranche de caractères depuis un fichier.",
        "requires": ["path", "start_char", "end_char"],
        "returns": "str: La tranche de caractères demandée.",
        "ritual_keywords": ["read", "chars", "slice", "specific"],
        "symbolic_layer": "Extrait l'essence brute, symbole par symbole.",
        "usage_context": "Utile pour analyser des formats binaires ou des sections de données très précises.",
        "level": "intermédiaire"
    }
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content[start_char:end_char]
    except Exception as e:
        return f"Erreur lors de la lecture des caractères du fichier : {e}"}
