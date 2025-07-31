from openai import tool
import os

@tool
def create_file(path: str, content: str = "") -> bool:
    """Crée un nouveau fichier avec un contenu optionnel. Échoue si le fichier existe déjà."""
    __lucidoc__ = {
        "id": "create_file",
        "type": "writing",
        "intent": "Matérialiser un nouveau fichier dans le néant.",
        "requires": ["path"],
        "optional": ["content"],
        "returns": "bool: True si le fichier a été créé, False sinon.",
        "ritual_keywords": ["create", "new", "file", "empty"],
        "symbolic_layer": "Donne naissance à un nouveau réceptacle de pensées.",
        "usage_context": "Pour initialiser un nouveau script, un log, ou tout autre fichier vierge.",
        "level": "fondamental"
    }
    if os.path.exists(path):
        return False
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

@tool
def append_to_file(path: str, content: str) -> bool:
    """Ajoute du contenu à la fin d'un fichier."""
    __lucidoc__ = {
        "id": "append_to_file",
        "type": "writing",
        "intent": "Ajouter des pensées à la fin d'un grimoire existant.",
        "requires": ["path", "content"],
        "returns": "bool: True si l'ajout a réussi.",
        "ritual_keywords": ["append", "add", "end", "file"],
        "symbolic_layer": "Continue une histoire déjà commencée.",
        "usage_context": "Idéal pour logger des événements ou ajouter des notes à un fichier existant.",
        "level": "fondamental"
    }
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

@tool
def overwrite_file(path: str, content: str) -> bool:
    """Écrit ou écrase un fichier avec le nouveau contenu."""
    __lucidoc__ = {
        "id": "overwrite_file",
        "type": "writing",
        "intent": "Réécrire entièrement le pacte d'un fichier.",
        "requires": ["path", "content"],
        "returns": "bool: True si l'écriture a réussi.",
        "ritual_keywords": ["overwrite", "replace", "write", "full"],
        "symbolic_layer": "Efface le passé et le remplace par une nouvelle vérité.",
        "usage_context": "Quand un fichier de configuration doit être entièrement remplacé ou qu'un fichier temporaire est réutilisé.",
        "level": "intermédiaire"
    }
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False
