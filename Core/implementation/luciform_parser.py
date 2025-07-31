import re

def parse_luciform(file_path: str) -> dict:
    """Parse un fichier .luciform de manière abstraite, en respectant sa structure hiérarchique."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex pour trouver toutes les balises, commentaires et textes
    tokenizer = re.compile(r'(<!--.*?-->)|(<([^>\s]+)[^>]*>)|([^<]+)', re.DOTALL)
    
    stack = [{ "tag": "root", "children": [] }] # La pile pour gérer la hiérarchie
    
    for match in tokenizer.finditer(content):
        comment, tag_full, tag_name, text = match.groups()

        if comment:
            stack[-1]["children"].append({"type": "comment", "content": comment.strip('<!- ->')})
        elif tag_full:
            if tag_full.startswith('</'): # Balise fermante
                if len(stack) > 1:
                    closed_node = stack.pop()
                    stack[-1]["children"].append(closed_node)
            else: # Balise ouvrante
                # Extrait les attributs (ex: id="valeur")
                attrs = dict(re.findall(r'([a-zA-Z0-9_]+)="([^"]+)"', tag_full))
                new_node = {"tag": tag_name, "attrs": attrs, "children": []}
                stack.append(new_node)
        elif text and text.strip():
            stack[-1]["children"].append({"type": "text", "content": text.strip()})
            
    # Le résultat final est l'enfant de la racine (notre luciform_doc)
    if len(stack) == 1 and stack[0]["children"]:
        return stack[0]["children"][0]
    else:
        raise ValueError("Structure de luciform mal formée ou pile non résolue.")