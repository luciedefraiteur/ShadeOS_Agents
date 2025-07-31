from Tools.Execution.implementation.invoke_cli_tool import invoke_cli_tool
import json

def scry_for_text(path: str, text_to_find: str, context_lines: int = 3) -> list[dict]:
    """Cherche un texte dans un fichier et retourne chaque occurrence avec un nombre défini de lignes de contexte avant et après."""
    result = invoke_cli_tool("scry_for_text", [path, text_to_find, "--context_lines", str(context_lines)])
    if result["success"]:
        return json.loads(result["stdout"])
    else:
        return [{f"Erreur lors de la divination du texte : {result["stderr"]}"}]

def locate_text_sigils(path: str, text_to_find: str, context_lines: int = 3) -> list[dict]:
    """Cherche un texte dans un fichier et retourne les numéros de ligne de début et de fin du bloc de contexte pour chaque occurrence."""
    result = invoke_cli_tool("locate_text_sigils", [path, text_to_find, "--context_lines", str(context_lines)])
    if result["success"]:
        return json.loads(result["stdout"])
    else:
        return [{f"Erreur lors de la localisation des sceaux textuels : {result["stderr"]}"}]
