import os
import sys

from ..Utils.string_utils import _simple_xml_tokenizer

def parse_luciform(file_path: str) -> dict:
    """
    Parse un fichier .luciform en un arbre de syntaxe abstrait (AST).
    Le parseur est agnostique au contenu et préserve la structure, y compris les commentaires.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Tokenizer simple pour séparer les commentaires, les balises, et le texte (sans regex)
    tokens = _simple_xml_tokenizer(content)

    stack = [{"tag": "root", "attrs": {}, "children": []}] # Pile pour gérer la hiérarchie

    for token in tokens:
        if token['type'] == 'comment':
            # Ajoute un nœud de commentaire
            stack[-1]["children"].append({"tag": "comment", "content": token['content']})

        elif token['type'] == 'tag_open':
            # Balise ouvrante : crée un nouveau nœud et le pousse sur la pile
            new_node = {"tag": token['tag_name'], "attrs": token['attrs'], "children": []}
            stack.append(new_node)

        elif token['type'] == 'tag_close':
            # Balise fermante : finalise le nœud et le lie à son parent
            if len(stack) > 1:
                closed_node = stack.pop()
                stack[-1]["children"].append(closed_node)

        elif token['type'] == 'text':
            # Ajoute un nœud de texte
            stack[-1]["children"].append({"tag": "text", "content": token['content']})
            
    # Le résultat final est le premier (et unique) enfant du nœud racine
    if len(stack) == 1 and len(stack[0]["children"]) == 1:
        return stack[0]["children"][0]
    else:
        # Retourne la racine si plusieurs enfants ou pour débogage
        return stack[0] 