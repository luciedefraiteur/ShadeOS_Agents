#!/usr/bin/env python3
"""
⛧ Regex Search File ⛧
Alma's Mystical Pattern Searcher

Recherche par regex dans un fichier unique avec contexte et coloration.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import argparse
import re
import sys

# Assure que le répertoire de l'outil est dans sys.path pour les imports internes
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Fonction de lecture sécurisée intégrée
def safe_read_file_content(file_path):
    """Lecture sécurisée d'un fichier."""
    try:
        if not os.path.exists(file_path):
            return {"success": False, "error": f"Fichier inexistant: {file_path}"}

        if not os.path.isfile(file_path):
            return {"success": False, "error": f"Le chemin n'est pas un fichier: {file_path}"}

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {"success": True, "content": content}

    except PermissionError:
        return {"success": False, "error": f"Permission refusée: {file_path}"}
    except UnicodeDecodeError:
        return {"success": False, "error": f"Erreur d'encodage: {file_path}"}
    except Exception as e:
        return {"success": False, "error": f"Erreur lecture: {e}"}


def colorize_match(text, match_obj, color_code="91"):
    """Colorise une correspondance regex dans le texte."""
    if not match_obj:
        return text
    
    start, end = match_obj.span()
    return (
        text[:start] + 
        f"\033[{color_code}m{text[start:end]}\033[0m" + 
        text[end:]
    )


def regex_search_file(file_path, pattern, context_before=2, context_after=2, 
                     case_sensitive=True, multiline=False, show_line_numbers=True,
                     highlight_matches=True, max_matches=None):
    """
    Recherche par regex dans un fichier avec contexte.
    
    Args:
        file_path: Chemin vers le fichier
        pattern: Pattern regex à rechercher
        context_before: Lignes de contexte avant
        context_after: Lignes de contexte après
        case_sensitive: Sensible à la casse
        multiline: Mode multiline
        show_line_numbers: Afficher numéros de ligne
        highlight_matches: Coloriser les correspondances
        max_matches: Nombre maximum de correspondances
    
    Returns:
        Dict avec résultats de la recherche
    """
    
    # Lecture sécurisée du fichier
    read_result = safe_read_file_content(file_path)
    if not read_result["success"]:
        return {
            "success": False,
            "error": f"Impossible de lire le fichier: {read_result['error']}",
            "matches": []
        }
    
    content = read_result["content"]
    lines = content.split('\n')
    
    # Configuration des flags regex
    flags = 0
    if not case_sensitive:
        flags |= re.IGNORECASE
    if multiline:
        flags |= re.MULTILINE
    
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        return {
            "success": False,
            "error": f"Pattern regex invalide: {e}",
            "matches": []
        }
    
    matches = []
    match_count = 0
    
    # Recherche ligne par ligne
    for line_num, line in enumerate(lines, 1):
        match = regex.search(line)
        if match:
            if max_matches and match_count >= max_matches:
                break
            
            # Calcul du contexte
            start_context = max(0, line_num - 1 - context_before)
            end_context = min(len(lines), line_num + context_after)
            
            # Extraction du contexte
            context_lines = []
            for i in range(start_context, end_context):
                line_content = lines[i]
                line_number = i + 1
                is_match_line = (line_number == line_num)
                
                # Colorisation si c'est la ligne de correspondance
                if is_match_line and highlight_matches:
                    line_match = regex.search(line_content)
                    if line_match:
                        line_content = colorize_match(line_content, line_match)
                
                context_lines.append({
                    "line_number": line_number,
                    "content": line_content,
                    "is_match": is_match_line
                })
            
            matches.append({
                "line_number": line_num,
                "match_text": match.group(0),
                "match_start": match.start(),
                "match_end": match.end(),
                "full_line": line,
                "context": context_lines,
                "groups": match.groups() if match.groups() else []
            })
            
            match_count += 1
    
    return {
        "success": True,
        "file_path": file_path,
        "pattern": pattern,
        "total_matches": len(matches),
        "matches": matches,
        "case_sensitive": case_sensitive,
        "multiline": multiline
    }


def format_search_results(results, compact=False):
    """Formate les résultats de recherche pour affichage."""
    if not results["success"]:
        return f"❌ Erreur: {results['error']}"
    
    if results["total_matches"] == 0:
        return f"🔍 Aucune correspondance trouvée pour '{results['pattern']}' dans {results['file_path']}"
    
    output = []
    output.append(f"🔍 Recherche: '{results['pattern']}' dans {results['file_path']}")
    output.append(f"📊 {results['total_matches']} correspondance(s) trouvée(s)")
    output.append("")
    
    for i, match in enumerate(results["matches"], 1):
        if not compact:
            output.append(f"⛧ Correspondance {i} (ligne {match['line_number']}):")
            output.append(f"   Match: '{match['match_text']}'")
            if match['groups']:
                output.append(f"   Groupes: {match['groups']}")
            output.append("")
            
            # Affichage du contexte
            for ctx_line in match["context"]:
                prefix = ">>> " if ctx_line["is_match"] else "    "
                line_num = f"{ctx_line['line_number']:4d}"
                output.append(f"{prefix}{line_num}: {ctx_line['content']}")
            output.append("")
        else:
            # Mode compact
            output.append(f"L{match['line_number']}: {match['match_text']}")
    
    return "\n".join(output)


def main():
    """Interface en ligne de commande."""
    parser = argparse.ArgumentParser(
        description="⛧ Recherche par regex dans un fichier - Outil d'Alma ⛧"
    )
    
    parser.add_argument("file_path", help="Chemin vers le fichier à analyser")
    parser.add_argument("pattern", help="Pattern regex à rechercher")
    parser.add_argument("-B", "--before", type=int, default=2, 
                       help="Lignes de contexte avant (défaut: 2)")
    parser.add_argument("-A", "--after", type=int, default=2,
                       help="Lignes de contexte après (défaut: 2)")
    parser.add_argument("-C", "--context", type=int,
                       help="Lignes de contexte avant et après")
    parser.add_argument("-i", "--ignore-case", action="store_true",
                       help="Ignorer la casse")
    parser.add_argument("-m", "--multiline", action="store_true",
                       help="Mode multiline")
    parser.add_argument("-n", "--no-line-numbers", action="store_true",
                       help="Ne pas afficher les numéros de ligne")
    parser.add_argument("--no-color", action="store_true",
                       help="Désactiver la coloration")
    parser.add_argument("--max-matches", type=int,
                       help="Nombre maximum de correspondances")
    parser.add_argument("--compact", action="store_true",
                       help="Affichage compact")
    parser.add_argument("--debug", action="store_true",
                       help="Mode debug avec informations détaillées")
    
    args = parser.parse_args()
    
    # Gestion du contexte unifié
    if args.context is not None:
        context_before = context_after = args.context
    else:
        context_before = args.before
        context_after = args.after
    
    if args.debug:
        print(f"⛧ Recherche regex dans fichier unique")
        print(f"  Fichier: {args.file_path}")
        print(f"  Pattern: {args.pattern}")
        print(f"  Contexte: {context_before} avant, {context_after} après")
        print(f"  Options: case_sensitive={not args.ignore_case}, multiline={args.multiline}")
        print()
    
    # Exécution de la recherche
    results = regex_search_file(
        file_path=args.file_path,
        pattern=args.pattern,
        context_before=context_before,
        context_after=context_after,
        case_sensitive=not args.ignore_case,
        multiline=args.multiline,
        show_line_numbers=not args.no_line_numbers,
        highlight_matches=not args.no_color,
        max_matches=args.max_matches
    )
    
    # Affichage des résultats
    formatted_output = format_search_results(results, compact=args.compact)
    print(formatted_output)
    
    # Code de sortie
    if results["success"] and results["total_matches"] > 0:
        sys.exit(0)
    elif results["success"] and results["total_matches"] == 0:
        sys.exit(1)  # Aucune correspondance
    else:
        sys.exit(2)  # Erreur


if __name__ == "__main__":
    main()
