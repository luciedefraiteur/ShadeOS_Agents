#!/usr/bin/env python3
"""
⛧ File Diff ⛧
Alma's Mystical File Comparator

Compare deux fichiers avec diff coloré et statistiques.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import argparse
import difflib
import sys


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


def colorize_diff_line(line):
    """Colorise une ligne de diff."""
    if line.startswith('+++') or line.startswith('---'):
        return f"\033[1m{line}\033[0m"  # Bold
    elif line.startswith('@@'):
        return f"\033[36m{line}\033[0m"  # Cyan
    elif line.startswith('+'):
        return f"\033[32m{line}\033[0m"  # Green
    elif line.startswith('-'):
        return f"\033[31m{line}\033[0m"  # Red
    else:
        return line


def file_diff(file1_path, file2_path, context_lines=3, ignore_whitespace=False, 
              unified=True, colorize=True):
    """
    Compare deux fichiers et retourne les différences.
    
    Args:
        file1_path: Chemin vers le premier fichier
        file2_path: Chemin vers le second fichier
        context_lines: Nombre de lignes de contexte
        ignore_whitespace: Ignorer les différences d'espaces
        unified: Format unifié (True) ou côte à côte (False)
        colorize: Coloriser la sortie
    
    Returns:
        Dict avec résultats de la comparaison
    """
    
    # Lecture des fichiers
    read1 = safe_read_file_content(file1_path)
    if not read1["success"]:
        return {"success": False, "error": f"Fichier 1: {read1['error']}"}
    
    read2 = safe_read_file_content(file2_path)
    if not read2["success"]:
        return {"success": False, "error": f"Fichier 2: {read2['error']}"}
    
    content1 = read1["content"]
    content2 = read2["content"]
    
    # Traitement des espaces si demandé
    if ignore_whitespace:
        lines1 = [line.strip() for line in content1.splitlines()]
        lines2 = [line.strip() for line in content2.splitlines()]
    else:
        lines1 = content1.splitlines()
        lines2 = content2.splitlines()
    
    # Calcul des différences
    if unified:
        diff_lines = list(difflib.unified_diff(
            lines1, lines2,
            fromfile=file1_path,
            tofile=file2_path,
            n=context_lines,
            lineterm=''
        ))
    else:
        diff_lines = list(difflib.context_diff(
            lines1, lines2,
            fromfile=file1_path,
            tofile=file2_path,
            n=context_lines,
            lineterm=''
        ))
    
    # Colorisation si demandée
    if colorize:
        diff_lines = [colorize_diff_line(line) for line in diff_lines]
    
    # Statistiques
    added_lines = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
    removed_lines = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
    
    # Vérification si les fichiers sont identiques
    identical = (content1 == content2)
    
    return {
        "success": True,
        "file1_path": file1_path,
        "file2_path": file2_path,
        "identical": identical,
        "diff_lines": diff_lines,
        "added_lines": added_lines,
        "removed_lines": removed_lines,
        "total_changes": added_lines + removed_lines,
        "context_lines": context_lines,
        "ignore_whitespace": ignore_whitespace,
        "unified_format": unified
    }


def format_diff_results(results):
    """Formate les résultats de diff pour affichage."""
    if not results["success"]:
        return f"❌ Erreur: {results['error']}"
    
    output = []
    output.append(f"🔍 Comparaison: {results['file1_path']} ↔ {results['file2_path']}")
    
    if results["identical"]:
        output.append("✅ Les fichiers sont identiques")
        return "\n".join(output)
    
    output.append(f"📊 Statistiques:")
    output.append(f"  + {results['added_lines']} lignes ajoutées")
    output.append(f"  - {results['removed_lines']} lignes supprimées")
    output.append(f"  📈 {results['total_changes']} changements au total")
    output.append("")
    
    if results["diff_lines"]:
        output.append("🔄 Différences:")
        output.extend(results["diff_lines"])
    
    return "\n".join(output)


def main():
    """Interface en ligne de commande."""
    parser = argparse.ArgumentParser(
        description="⛧ Comparaison de fichiers - Outil d'Alma ⛧"
    )
    
    parser.add_argument("file1", help="Premier fichier à comparer")
    parser.add_argument("file2", help="Second fichier à comparer")
    parser.add_argument("-c", "--context", type=int, default=3,
                       help="Lignes de contexte (défaut: 3)")
    parser.add_argument("-w", "--ignore-whitespace", action="store_true",
                       help="Ignorer les différences d'espaces")
    parser.add_argument("--side-by-side", action="store_true",
                       help="Format côte à côte au lieu d'unifié")
    parser.add_argument("--no-color", action="store_true",
                       help="Désactiver la coloration")
    parser.add_argument("--debug", action="store_true",
                       help="Mode debug avec informations détaillées")
    
    args = parser.parse_args()
    
    if args.debug:
        print(f"⛧ Comparaison de fichiers")
        print(f"  Fichier 1: {args.file1}")
        print(f"  Fichier 2: {args.file2}")
        print(f"  Contexte: {args.context} lignes")
        print(f"  Options: ignore_whitespace={args.ignore_whitespace}, unified={not args.side_by_side}")
        print()
    
    # Exécution de la comparaison
    results = file_diff(
        file1_path=args.file1,
        file2_path=args.file2,
        context_lines=args.context,
        ignore_whitespace=args.ignore_whitespace,
        unified=not args.side_by_side,
        colorize=not args.no_color
    )
    
    # Affichage des résultats
    formatted_output = format_diff_results(results)
    print(formatted_output)
    
    # Code de sortie
    if results["success"]:
        if results["identical"]:
            sys.exit(0)  # Fichiers identiques
        else:
            sys.exit(1)  # Fichiers différents
    else:
        sys.exit(2)  # Erreur


if __name__ == "__main__":
    main()
