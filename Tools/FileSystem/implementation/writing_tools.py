import os

def create_file(path: str, content: str = "") -> bool:
    """Crée un nouveau fichier avec un contenu optionnel. Échoue si le fichier existe déjà."""
    if os.path.exists(path):
        return False
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

def append_to_file(path: str, content: str) -> bool:
    """Ajoute du contenu à la fin d'un fichier."""
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

def overwrite_file(path: str, content: str) -> bool:
    """Écrit ou écrase un fichier avec le nouveau contenu."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False