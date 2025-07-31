from Tools.Execution.implementation.invoke_cli_tool import invoke_cli_tool
import json

def replace_text_in_file(path: str, old_text: str, new_text: str, all_occurrences: bool = False) -> bool:
    """Remplace la première ou toutes les occurrences d'un texte dans un fichier."""
    args = [path, old_text, new_text]
    if all_occurrences:
        args.append("--all_occurrences")
    result = invoke_cli_tool("safe_replace_text_in_file", args)
    return result["success"]

def replace_lines_in_file(path: str, start_line: int, end_line: int, new_lines: list[str]) -> bool:
    """Remplace une plage de lignes par de nouvelles lignes."""
    args = [path, str(start_line), str(end_line)] + new_lines
    result = invoke_cli_tool("safe_replace_lines_in_file", args)
    return result["success"]

def insert_text_at_line(path: str, line_number: int, text_to_insert: str) -> bool:
    """Insère un bloc de texte à une ligne spécifique, décalant le reste."""
    args = [path, str(line_number), text_to_insert]
    result = invoke_cli_tool("safe_insert_text_at_line", args)
    return result["success"]
