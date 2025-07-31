from Tools.Execution.implementation.invoke_cli_tool import invoke_cli_tool

def create_file(path: str, content: str = "") -> bool:
    """Crée un nouveau fichier avec un contenu optionnel. Échoue si le fichier existe déjà."""
    args = [path]
    if content:
        args.extend(["--content", content])
    result = invoke_cli_tool("create_file", args)
    return result["success"]

def append_to_file(path: str, content: str) -> bool:
    """Ajoute du contenu à la fin d'un fichier."""
    result = invoke_cli_tool("append_to_file", [path, content])
    return result["success"]

def overwrite_file(path: str, content: str) -> bool:
    """Écrit ou écrase un fichier avec le nouveau contenu."""
    result = invoke_cli_tool("overwrite_file", [path, content])
    return result["success"]
