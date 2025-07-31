import re
import sys

def parse_luciform(file_path: str) -> dict:
    """Parse un fichier .luciform de manière abstraite, en respectant sa structure hiérarchique."""
    print(f"[PARSER DEBUG] Début du parsage de: {file_path}", file=sys.stderr)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"[PARSER DEBUG] Contenu lu (partiel): {content[:200]}...", file=sys.stderr)

    tokenizer = re.compile(r'(<!--.*?-->)|(<([^>\s]+)[^>]*>)|([^<]+)', re.DOTALL)
    
    stack = [{ "tag": "root", "children": [] }] # La pile pour gérer la hiérarchie
    
    for match in tokenizer.finditer(content):
        comment, tag_full, tag_name, text = match.groups()
        text_preview = text[:50] if text is not None else None
        print(f"[PARSER DEBUG] Match: comment={comment}, tag_full={tag_full}, tag_name={tag_name}, text={text_preview}...", file=sys.stderr)

        if comment:
            print(f"[PARSER DEBUG]   - Commentaire détecté: {comment.strip()[:50]}...", file=sys.stderr)
            stack[-1]["children"].append({"type": "comment", "content": comment.strip('<!- ->')})
        elif tag_full:
            if tag_full.startswith('</'): # Balise fermante
                print(f"[PARSER DEBUG]   - Balise fermante: {tag_full}", file=sys.stderr)
                if len(stack) > 1:
                    closed_node = stack.pop()
                    stack[-1]["children"].append(closed_node)
                    print(f"[PARSER DEBUG]     - Pile après pop: {[s["tag"] for s in stack]}", file=sys.stderr)
            else: # Balise ouvrante
                print(f"[PARSER DEBUG]   - Balise ouvrante: {tag_full}", file=sys.stderr)
                attrs = dict(re.findall(r'([a-zA-Z0-9_]+)="([^"]+)"', tag_full))
                new_node = {"tag": tag_name, "attrs": attrs, "children": []}
                stack.append(new_node)
                print(f"[PARSER DEBUG]     - Pile après push: {[s["tag"] for s in stack]}", file=sys.stderr)
        elif text and text.strip():
            print(f"[PARSER DEBUG]   - Texte détecté: {text.strip()[:50]}...", file=sys.stderr)
            stack[-1]["children"].append({"type": "text", "content": text.strip()})
            
    # Le résultat final est l'enfant de la racine (notre luciform_doc)
    if len(stack) == 1 and stack[0]["children"]:
        print(f"[PARSER DEBUG] Parsage terminé. Arbre racine: {stack[0]["children"][0]["tag"]}", file=sys.stderr)
        return stack[0]["children"][0]
    else:
        print(f"[PARSER DEBUG] Erreur: Structure de luciform mal formée ou pile non résolue. Pile finale: {[s["tag"] for s in stack]}", file=sys.stderr)
        raise ValueError("Structure de luciform mal formée ou pile non résolue.")
