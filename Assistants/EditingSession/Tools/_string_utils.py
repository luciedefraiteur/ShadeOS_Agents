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


def _is_word_boundary_char(char: str) -> bool:
    """Vérifie si un caractère est une limite de mot (non alphanumérique, non underscore, non tiret)."""
    if not char:
        return True  # Début ou fin de chaîne
    return not (char.isalnum() or char == '_' or char == '-')


def _perform_word_boundary_replacement(source_string: str, old_word: str, new_word: str, all_occurrences: bool = False, debug: bool = False) -> str:
    """
    Effectue un remplacement de mot complet, en respectant les limites de mots.
    Équivalent à une regex avec word boundaries, mais implémenté avec des boucles pures.
    """
    if debug:
        print(f"[DEBUG - _perform_word_boundary_replacement] Source: '{source_string}'", file=sys.stderr)
        print(f"[DEBUG - _perform_word_boundary_replacement] Ancien mot: '{old_word}'", file=sys.stderr)
        print(f"[DEBUG - _perform_word_boundary_replacement] Nouveau mot: '{new_word}'", file=sys.stderr)
        print(f"[DEBUG - _perform_word_boundary_replacement] Toutes occurrences: {all_occurrences}", file=sys.stderr)

    if not old_word:
        return source_string

    result_string = []
    i = 0
    old_word_len = len(old_word)

    while i < len(source_string):
        # Vérifier si on a une correspondance potentielle
        if source_string[i:i + old_word_len] == old_word:
            # Vérifier les limites de mots
            char_before = source_string[i-1] if i > 0 else ''
            char_after = source_string[i + old_word_len] if i + old_word_len < len(source_string) else ''

            # Vérifier que c'est bien un mot complet (limites de mots avant et après)
            if _is_word_boundary_char(char_before) and _is_word_boundary_char(char_after):
                # C'est un mot complet, on peut le remplacer
                result_string.append(new_word)
                i += old_word_len

                if debug:
                    print(f"[DEBUG - _perform_word_boundary_replacement] Remplacement effectué à la position {i-old_word_len}", file=sys.stderr)

                if not all_occurrences:
                    # Ajouter le reste de la chaîne et sortir
                    result_string.append(source_string[i:])
                    break
            else:
                # Ce n'est pas un mot complet, continuer
                result_string.append(source_string[i])
                i += 1
        else:
            result_string.append(source_string[i])
            i += 1

    final_result = "".join(result_string)
    if debug:
        print(f"[DEBUG - _perform_word_boundary_replacement] Résultat: '{final_result}'", file=sys.stderr)
    return final_result


def _simple_text_search(text: str, pattern: str, case_sensitive: bool = True) -> bool:
    """
    Recherche simple de texte sans regex.
    Remplace re.search() pour des recherches basiques.
    """
    if not case_sensitive:
        text = text.lower()
        pattern = pattern.lower()

    return pattern in text


def _find_all_occurrences(text: str, pattern: str, case_sensitive: bool = True) -> list[int]:
    """
    Trouve toutes les positions d'un pattern dans un texte.
    Retourne une liste des positions de début de chaque occurrence.
    """
    if not case_sensitive:
        text = text.lower()
        pattern = pattern.lower()

    positions = []
    start = 0
    pattern_len = len(pattern)

    while start < len(text):
        pos = text.find(pattern, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + pattern_len

    return positions


def _simple_xml_tokenizer(content: str) -> list[dict]:
    """
    Tokenizer XML simple sans regex.
    Remplace la regex complexe du luciform_parser.
    """
    tokens = []
    i = 0
    content_len = len(content)

    while i < content_len:
        if content[i] == '<':
            # Début d'une balise ou commentaire
            if i + 4 < content_len and content[i:i+4] == '<!--':
                # Commentaire
                end_comment = content.find('-->', i + 4)
                if end_comment != -1:
                    comment_content = content[i+4:end_comment]
                    tokens.append({
                        'type': 'comment',
                        'content': comment_content.strip()
                    })
                    i = end_comment + 3
                else:
                    # Commentaire mal formé, traiter comme texte
                    tokens.append({
                        'type': 'text',
                        'content': content[i]
                    })
                    i += 1
            else:
                # Balise normale
                end_tag = content.find('>', i)
                if end_tag != -1:
                    tag_content = content[i+1:end_tag]

                    if tag_content.startswith('/'):
                        # Balise fermante
                        tag_name = tag_content[1:].strip()
                        tokens.append({
                            'type': 'tag_close',
                            'tag_name': tag_name
                        })
                    else:
                        # Balise ouvrante
                        # Séparer le nom de la balise des attributs
                        parts = tag_content.split()
                        tag_name = parts[0] if parts else ''

                        # Parser les attributs simplement
                        attrs = {}
                        if len(parts) > 1:
                            attr_string = ' '.join(parts[1:])
                            attrs = _parse_simple_attributes(attr_string)

                        tokens.append({
                            'type': 'tag_open',
                            'tag_name': tag_name,
                            'attrs': attrs
                        })

                    i = end_tag + 1
                else:
                    # Balise mal formée, traiter comme texte
                    tokens.append({
                        'type': 'text',
                        'content': content[i]
                    })
                    i += 1
        else:
            # Texte normal
            text_start = i
            while i < content_len and content[i] != '<':
                i += 1

            text_content = content[text_start:i]
            if text_content.strip():
                tokens.append({
                    'type': 'text',
                    'content': text_content.strip()
                })

    return tokens


def _parse_simple_attributes(attr_string: str) -> dict:
    """
    Parse simple des attributs XML sans regex.
    Format attendu: key="value" key2="value2"
    """
    attrs = {}
    i = 0
    attr_len = len(attr_string)

    while i < attr_len:
        # Ignorer les espaces
        while i < attr_len and attr_string[i].isspace():
            i += 1

        if i >= attr_len:
            break

        # Lire le nom de l'attribut
        key_start = i
        while i < attr_len and attr_string[i] not in '= \t\n':
            i += 1

        if i == key_start:
            break

        key = attr_string[key_start:i]

        # Ignorer les espaces et chercher '='
        while i < attr_len and attr_string[i].isspace():
            i += 1

        if i >= attr_len or attr_string[i] != '=':
            break

        i += 1  # Passer le '='

        # Ignorer les espaces après '='
        while i < attr_len and attr_string[i].isspace():
            i += 1

        if i >= attr_len:
            break

        # Lire la valeur (entre guillemets)
        if attr_string[i] == '"':
            i += 1  # Passer le '"' d'ouverture
            value_start = i
            while i < attr_len and attr_string[i] != '"':
                i += 1

            if i < attr_len:
                value = attr_string[value_start:i]
                attrs[key] = value
                i += 1  # Passer le '"' de fermeture
        else:
            # Valeur sans guillemets (jusqu'au prochain espace)
            value_start = i
            while i < attr_len and not attr_string[i].isspace():
                i += 1

            value = attr_string[value_start:i]
            attrs[key] = value

    return attrs
