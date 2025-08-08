#!/usr/bin/env python3
"""
⛧ File Stats ⛧
Alma's Mystical File Analyzer

Analyse détaillée des statistiques d'un fichier.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import argparse
import re
import sys
from collections import Counter
from datetime import datetime


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


def analyze_file_stats(file_path, include_words=True, include_chars=True, 
                      include_patterns=True, top_words=10):
    """
    Analyse les statistiques détaillées d'un fichier.
    
    Args:
        file_path: Chemin vers le fichier
        include_words: Inclure l'analyse des mots
        include_chars: Inclure l'analyse des caractères
        include_patterns: Inclure l'analyse des patterns
        top_words: Nombre de mots les plus fréquents
    
    Returns:
        Dict avec statistiques complètes
    """
    
    # Lecture du fichier
    read_result = safe_read_file_content(file_path)
    if not read_result["success"]:
        return {"success": False, "error": read_result["error"]}
    
    content = read_result["content"]
    lines = content.split('\n')
    
    # Informations de base du fichier
    file_stat = os.stat(file_path)
    
    # Statistiques de base
    stats = {
        "success": True,
        "file_path": file_path,
        "file_size_bytes": file_stat.st_size,
        "file_size_kb": round(file_stat.st_size / 1024, 2),
        "created_time": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
        "modified_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
        "total_lines": len(lines),
        "non_empty_lines": len([line for line in lines if line.strip()]),
        "empty_lines": len([line for line in lines if not line.strip()]),
        "total_characters": len(content),
        "total_characters_no_spaces": len(content.replace(' ', '')),
        "total_words": len(content.split()),
        "average_line_length": round(sum(len(line) for line in lines) / len(lines), 2) if lines else 0,
        "longest_line": max(len(line) for line in lines) if lines else 0,
        "shortest_line": min(len(line) for line in lines if line.strip()) if lines else 0
    }
    
    # Analyse des caractères
    if include_chars:
        char_counter = Counter(content)
        stats["character_analysis"] = {
            "unique_characters": len(char_counter),
            "most_common_chars": char_counter.most_common(10),
            "whitespace_count": content.count(' ') + content.count('\t'),
            "newline_count": content.count('\n'),
            "tab_count": content.count('\t'),
            "digit_count": sum(1 for c in content if c.isdigit()),
            "alpha_count": sum(1 for c in content if c.isalpha()),
            "upper_count": sum(1 for c in content if c.isupper()),
            "lower_count": sum(1 for c in content if c.islower())
        }
    
    # Analyse des mots
    if include_words:
        words = re.findall(r'\b\w+\b', content.lower())
        word_counter = Counter(words)
        stats["word_analysis"] = {
            "unique_words": len(word_counter),
            "total_words": len(words),
            "average_word_length": round(sum(len(word) for word in words) / len(words), 2) if words else 0,
            "longest_word": max(words, key=len) if words else "",
            "shortest_word": min(words, key=len) if words else "",
            "most_common_words": word_counter.most_common(top_words)
        }
    
    # Analyse des patterns (pour code)
    if include_patterns:
        patterns = {
            "functions": len(re.findall(r'\bdef\s+\w+', content)),
            "classes": len(re.findall(r'\bclass\s+\w+', content)),
            "imports": len(re.findall(r'\bimport\s+\w+|\bfrom\s+\w+\s+import', content)),
            "comments_python": len(re.findall(r'#.*', content)),
            "comments_js": len(re.findall(r'//.*', content)),
            "comments_multiline": len(re.findall(r'/\*.*?\*/', content, re.DOTALL)),
            "strings_double": len(re.findall(r'"[^"]*"', content)),
            "strings_single": len(re.findall(r"'[^']*'", content)),
            "numbers": len(re.findall(r'\b\d+\.?\d*\b', content)),
            "urls": len(re.findall(r'https?://[^\s]+', content)),
            "emails": len(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content))
        }
        stats["pattern_analysis"] = patterns
    
    # Analyse par type de ligne
    line_types = {
        "code_lines": 0,
        "comment_lines": 0,
        "blank_lines": 0,
        "mixed_lines": 0
    }
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            line_types["blank_lines"] += 1
        elif stripped.startswith('#') or stripped.startswith('//'):
            line_types["comment_lines"] += 1
        elif '#' in stripped or '//' in stripped:
            line_types["mixed_lines"] += 1
        else:
            line_types["code_lines"] += 1
    
    stats["line_type_analysis"] = line_types
    
    return stats


def format_stats_results(stats, detailed=True):
    """Formate les statistiques pour affichage."""
    if not stats["success"]:
        return f"❌ Erreur: {stats['error']}"
    
    output = []
    output.append(f"📊 Statistiques: {stats['file_path']}")
    output.append("⛧" + "═" * 60)
    
    # Informations de base
    output.append(f"📁 Taille: {stats['file_size_bytes']} bytes ({stats['file_size_kb']} KB)")
    output.append(f"📅 Modifié: {stats['modified_time']}")
    output.append("")
    
    # Statistiques de lignes
    output.append(f"📝 Lignes:")
    output.append(f"  Total: {stats['total_lines']}")
    output.append(f"  Non vides: {stats['non_empty_lines']}")
    output.append(f"  Vides: {stats['empty_lines']}")
    output.append(f"  Longueur moyenne: {stats['average_line_length']}")
    output.append(f"  Plus longue: {stats['longest_line']}")
    output.append("")
    
    # Statistiques de caractères et mots
    output.append(f"🔤 Caractères: {stats['total_characters']} (sans espaces: {stats['total_characters_no_spaces']})")
    output.append(f"📖 Mots: {stats['total_words']}")
    output.append("")
    
    if detailed:
        # Analyse des types de lignes
        if "line_type_analysis" in stats:
            lt = stats["line_type_analysis"]
            output.append(f"📋 Types de lignes:")
            output.append(f"  Code: {lt['code_lines']}")
            output.append(f"  Commentaires: {lt['comment_lines']}")
            output.append(f"  Mixtes: {lt['mixed_lines']}")
            output.append(f"  Vides: {lt['blank_lines']}")
            output.append("")
        
        # Analyse des mots
        if "word_analysis" in stats:
            wa = stats["word_analysis"]
            output.append(f"📚 Analyse des mots:")
            output.append(f"  Uniques: {wa['unique_words']}")
            output.append(f"  Longueur moyenne: {wa['average_word_length']}")
            output.append(f"  Plus long: '{wa['longest_word']}'")
            output.append(f"  Plus fréquents: {', '.join([f'{word}({count})' for word, count in wa['most_common_words'][:5]])}")
            output.append("")
        
        # Analyse des patterns
        if "pattern_analysis" in stats:
            pa = stats["pattern_analysis"]
            output.append(f"🔍 Patterns détectés:")
            for pattern, count in pa.items():
                if count > 0:
                    output.append(f"  {pattern}: {count}")
            output.append("")
    
    return "\n".join(output)


def main():
    """Interface en ligne de commande."""
    parser = argparse.ArgumentParser(
        description="⛧ Statistiques de fichier - Outil d'Alma ⛧"
    )
    
    parser.add_argument("file_path", help="Chemin vers le fichier à analyser")
    parser.add_argument("--no-words", action="store_true",
                       help="Désactiver l'analyse des mots")
    parser.add_argument("--no-chars", action="store_true",
                       help="Désactiver l'analyse des caractères")
    parser.add_argument("--no-patterns", action="store_true",
                       help="Désactiver l'analyse des patterns")
    parser.add_argument("--top-words", type=int, default=10,
                       help="Nombre de mots les plus fréquents (défaut: 10)")
    parser.add_argument("--compact", action="store_true",
                       help="Affichage compact")
    parser.add_argument("--debug", action="store_true",
                       help="Mode debug avec informations détaillées")
    
    args = parser.parse_args()
    
    if args.debug:
        print(f"⛧ Analyse de statistiques de fichier")
        print(f"  Fichier: {args.file_path}")
        print(f"  Options: words={not args.no_words}, chars={not args.no_chars}, patterns={not args.no_patterns}")
        print()
    
    # Exécution de l'analyse
    stats = analyze_file_stats(
        file_path=args.file_path,
        include_words=not args.no_words,
        include_chars=not args.no_chars,
        include_patterns=not args.no_patterns,
        top_words=args.top_words
    )
    
    # Affichage des résultats
    formatted_output = format_stats_results(stats, detailed=not args.compact)
    print(formatted_output)
    
    # Code de sortie
    sys.exit(0 if stats["success"] else 1)


if __name__ == "__main__":
    main()
