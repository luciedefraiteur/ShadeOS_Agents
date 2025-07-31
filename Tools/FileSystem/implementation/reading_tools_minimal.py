from Tools.Execution.implementation.invoke_cli_tool import invoke_cli_tool

def read_file_content_naked(path: str) -> str:
    """Lit et retourne tout le contenu d'un fichier texte, sans aucun décorateur."""
    result = invoke_cli_tool("read_file_content_naked", [path])
    if result["success"]:
        return result["stdout"]
    else:
        return f"Erreur : {result["stderr"]}"