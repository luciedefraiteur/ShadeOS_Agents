import re

def parse_luciform(file_path: str) -> dict:
    """
    Parse un fichier .luciform en un arbre de syntaxe abstrait (AST).
    Le parseur est agnostique au contenu et préserve la structure, y compris les commentaires.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Tokenizer pour séparer les commentaires, les balises, et le texte.
    tokenizer = re.compile(r'(<!--.*?-->)|(<([^>\s/]+)[^>]*>)|(</[^>]+>)|([^<]+)', re.DOTALL)
    
    stack = [{"tag": "root", "attrs": {}, "children": []}] # Pile pour gérer la hiérarchie
    
    for match in tokenizer.finditer(content):
        comment, tag_open, tag_name, tag_close, text = match.groups()

        if comment:
            # Ajoute un nœud de commentaire
            stack[-1]["children"].append({"tag": "comment", "content": comment.strip('<!- ->').strip()})
        
        elif tag_open:
            # Balise ouvrante : crée un nouveau nœud et le pousse sur la pile
            attrs = dict(re.findall(r'([a-zA-Z0-9_\-:]+)="([^"]+)"', tag_open))
            new_node = {"tag": tag_name, "attrs": attrs, "children": []}
            stack.append(new_node)

        elif tag_close:
            # Balise fermante : finalise le nœud et le lie à son parent
            if len(stack) > 1:
                closed_node = stack.pop()
                stack[-1]["children"].append(closed_node)

        elif text and text.strip():
            # Ajoute un nœud de texte
            stack[-1]["children"].append({"tag": "text", "content": text.strip()})
            
    # Le résultat final est le premier (et unique) enfant du nœud racine
    if len(stack) == 1 and len(stack[0]["children"]) == 1:
        return stack[0]["children"][0]
    else:
        # Retourne la racine si plusieurs enfants ou pour débogage
        return stack[0]
