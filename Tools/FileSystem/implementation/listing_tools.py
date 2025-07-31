from Tools.Execution.implementation.invoke_cli_tool import invoke_cli_tool
import json

def list_directory_contents(path: str) -> dict:
    """Liste les fichiers et sous-répertoires d'un répertoire donné."""
    result = invoke_cli_tool("list_directory_contents", [path])
    if result["success"]:
        return json.loads(result["stdout"])
    else:
        return {f"Erreur lors du listage du répertoire : {result["stderr"]}"}

def walk_directory(path: str) -> list[str]:
    """Marche récursivement dans un répertoire et retourne tous les chemins de fichiers."""
    result = invoke_cli_tool("walk_directory", [path])
    if result["success"]:
        return json.loads(result["stdout"])
    else:
        return [f"Erreur lors du parcours du répertoire : {result["stderr"]}"]
