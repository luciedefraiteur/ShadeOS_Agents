from openai import tool

@tool
def replace_text_in_file(path: str, old_text: str, new_text: str, all_occurrences: bool = False) -> bool:
    """Remplace la première ou toutes les occurrences d'un texte dans un fichier."""
    __lucidoc__ = {
        "id": "replace_text_in_file",
        "type": "modification",
        "intent": "Transmuter une séquence de symboles en une autre.",
        "requires": ["path", "old_text", "new_text"],
        "optional": ["all_occurrences"],
        "returns": "bool: True si une modification a eu lieu.",
        "ritual_keywords": ["replace", "text", "modify", "substitute"],
        "symbolic_layer": "Réécriture alchimique d'un fragment de réalité.",
        "usage_context": "Pour corriger des erreurs, renommer des variables, ou altérer des configurations.",
        "level": "intermédiaire"
    }
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if all_occurrences:
            new_content = content.replace(old_text, new_text)
        else:
            new_content = content.replace(old_text, new_text, 1)
            
        if new_content == content:
            return False # Aucune modification

        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception:
        return False

@tool
def replace_lines_in_file(path: str, start_line: int, end_line: int, new_lines: list[str]) -> bool:
    """Remplace une plage de lignes par de nouvelles lignes."""
    __lucidoc__ = {
        "id": "replace_lines_in_file",
        "type": "modification",
        "intent": "Remplacer un bloc de lignes par un nouveau contenu.",
        "requires": ["path", "start_line", "end_line", "new_lines"],
        "returns": "bool: True si la modification a réussi.",
        "ritual_keywords": ["replace", "lines", "block", "section"],
        "symbolic_layer": "Excision et greffe d'une partie de l'âme d'un fichier.",
        "usage_context": "Pour remplacer des fonctions, des configurations multi-lignes, ou des sections entières de texte.",
        "level": "avancé"
    }
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Remplacement des lignes
        # Les numéros de ligne sont 1-based
        new_content_lines = lines[:start_line-1] + [l + '\n' for l in new_lines] + lines[end_line:]

        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_content_lines)
        return True
    except Exception:
        return False

@tool
def insert_text_at_line(path: str, line_number: int, text_to_insert: str) -> bool:
    """Insère un bloc de texte à un numéro de ligne donné."""
    __lucidoc__ = {
        "id": "insert_text_at_line",
        "type": "modification",
        "intent": "Insérer du texte à une ligne spécifique, décalant le reste.",
        "requires": ["path", "line_number", "text_to_insert"],
        "returns": "bool: True si l'insertion a réussi.",
        "ritual_keywords": ["insert", "add", "line", "inject"],
        "symbolic_layer": "Injecte une nouvelle pensée dans un flux de conscience existant.",
        "usage_context": "Pour ajouter des imports, des déclarations, ou de nouvelles étapes dans un script.",
        "level": "intermédiaire"
    }
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Insertion du texte
        # Le numéro de ligne est 1-based
        lines.insert(line_number - 1, text_to_insert + '\n')

        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    except Exception:
        return False
False
