import sys

def _perform_string_replacement(source_string: str, old_substring: str, new_substring: str, all_occurrences: bool = False, debug: bool = False) -> str:
    """Effectue un remplacement de sous-chaîne manuel, caractère par caractère."""
    if debug:
        print(f"[DEBUG - _perform_string_replacement] Source: '{source_string}'", file=sys.stderr)
        print(f"[DEBUG - _perform_string_replacement] Ancien: '{old_substring}'", file=sys.stderr)
        print(f"[DEBUG - _perform_string_replacement] Nouveau: '{new_substring}'", file=sys.stderr)
        print(f"[DEBUG - _perform_string_replacement] Toutes occurrences: {all_occurrences}", file=sys.stderr)

    result_string = []
    i = 0
    while i < len(source_string):
        if source_string[i:i + len(old_substring)] == old_substring:
            result_string.append(new_substring)
            i += len(old_substring)
            if not all_occurrences:
                # Ajouter le reste de la chaîne et sortir
                result_string.append(source_string[i:])
                break
        else:
            result_string.append(source_string[i])
            i += 1
    
    final_result = "".join(result_string)
    if debug:
        print(f"[DEBUG - _perform_string_replacement] Résultat: '{final_result}'", file=sys.stderr)
    return final_result
