def read_file_content_naked(path: str) -> str:
    """Lit et retourne tout le contenu d'un fichier texte, sans aucun décorateur."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Erreur : {e}"