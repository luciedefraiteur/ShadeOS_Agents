from Tools.Execution.implementation.invoke_cli_tool import invoke_cli_tool
import json

def read_file_content(path: str) -> str:
    """Lit et retourne tout le contenu d'un fichier texte."""
    result = invoke_cli_tool("read_file_content", [path])
    if result["success"]:
        return result["stdout"]
    else:
        return f"Erreur lors de la lecture du fichier : {result["stderr"]}"

def read_file_lines(path: str, start_line: int, end_line: int) -> list[str]:
    """Lit et retourne une plage de lignes spécifiques d'un fichier."""
    result = invoke_cli_tool("read_file_lines", [path, str(start_line), str(end_line)])
    if result["success"]:
        return result["stdout"].splitlines()
    else:
        return [f"Erreur lors de la lecture des lignes du fichier : {result["stderr"]}"]

def read_file_chars(path: str, start_char: int, end_char: int) -> str:
    """Lit et retourne une plage de caractères spécifique d'un fichier."""
    result = invoke_cli_tool("read_file_chars", [path, str(start_char), str(end_char)])
    if result["success"]:
        return result["stdout"]
    else:
        return f"Erreur lors de la lecture des caractères du fichier : {result["stderr"]}"
