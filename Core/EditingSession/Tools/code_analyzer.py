#!/usr/bin/env python3
"""
⛧ Code Analyzer ⛧
Alma's Code Analysis Tool

Outil d'analyse de code Python pour détecter les bugs et problèmes potentiels.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import ast
import re
from typing import Dict, List, Any, Optional
from pathlib import Path


class CodeAnalyzer:
    """Analyseur de code Python pour détection de bugs."""
    
    def __init__(self):
        self.issues = []
        self.suggestions = []
        
    def analyze_file(self, file_path: str, analysis_type: str = 'all') -> Dict[str, Any]:
        """Analyse un fichier Python pour détecter les bugs."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                "file_path": file_path,
                "analysis_type": analysis_type,
                "issues": [],
                "suggestions": [],
                "metrics": {},
                "ast_analysis": {}
            }
            
            # Analyse syntaxique
            if analysis_type in ['all', 'syntax']:
                syntax_issues = self._analyze_syntax(content, file_path)
                analysis["issues"].extend(syntax_issues)
            
            # Analyse sémantique
            if analysis_type in ['all', 'semantic']:
                semantic_issues = self._analyze_semantic(content, file_path)
                analysis["issues"].extend(semantic_issues)
            
            # Analyse de patterns
            if analysis_type in ['all', 'patterns']:
                pattern_issues = self._analyze_patterns(content, file_path)
                analysis["issues"].extend(pattern_issues)
            
            # Métriques
            if analysis_type in ['all', 'metrics']:
                metrics = self._calculate_metrics(content)
                analysis["metrics"] = metrics
            
            # Analyse AST
            if analysis_type in ['all', 'ast']:
                ast_analysis = self._analyze_ast(content, file_path)
                analysis["ast_analysis"] = ast_analysis
            
            return analysis
            
        except Exception as e:
            return {
                "file_path": file_path,
                "error": str(e),
                "issues": [],
                "suggestions": []
            }
    
    def _analyze_syntax(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Analyse syntaxique du code."""
        issues = []
        
        try:
            ast.parse(content)
        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "severity": "high",
                "line": e.lineno,
                "message": f"Erreur de syntaxe: {e.msg}",
                "suggestion": "Corriger la syntaxe Python"
            })
        
        return issues
    
    def _analyze_semantic(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Analyse sémantique du code."""
        issues = []
        
        # Détecter les opérations mathématiques incorrectes
        math_patterns = [
            (r'(\w+)\s*-\s*(\w+)\s*#.*[Aa]dd', "Addition incorrecte - utilise la soustraction au lieu de l'addition"),
            (r'(\w+)\s*\+\s*(\w+)\s*#.*[Ss]ubtract', "Soustraction incorrecte - utilise l'addition au lieu de la soustraction"),
            (r'(\w+)\s*/\s*(\w+)\s*#.*[Mm]ultiply', "Multiplication incorrecte - utilise la division au lieu de la multiplication"),
            (r'(\w+)\s*\*\s*(\w+)\s*#.*[Dd]ivide', "Division incorrecte - utilise la multiplication au lieu de la division"),
            (r'(\w+)\s*\*\s*(\w+)\s*#.*[Pp]ower', "Puissance incorrecte - utilise la multiplication au lieu de l'exponentiation"),
            (r'(\w+)\s*/\s*2\s*#.*[Ss]qrt', "Racine carrée incorrecte - divise par 2 au lieu d'utiliser math.sqrt"),
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern, message in math_patterns:
                if re.search(pattern, line):
                    issues.append({
                        "type": "semantic_error",
                        "severity": "high",
                        "line": line_num,
                        "message": message,
                        "code": line.strip(),
                        "suggestion": "Corriger l'opération mathématique"
                    })
        
        # Détecter les modes d'ouverture de fichiers incorrects
        file_patterns = [
            (r'open\([^)]+,\s*[\'"]w[\'"]\s*\)\s*#.*[Rr]ead', "Mode d'ouverture incorrect - utilise 'r' pour la lecture"),
            (r'open\([^)]+,\s*[\'"]r[\'"]\s*\)\s*#.*[Ww]rite', "Mode d'ouverture incorrect - utilise 'w' pour l'écriture"),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, message in file_patterns:
                if re.search(pattern, line):
                    issues.append({
                        "type": "file_operation_error",
                        "severity": "high",
                        "line": line_num,
                        "message": message,
                        "code": line.strip(),
                        "suggestion": "Corriger le mode d'ouverture du fichier"
                    })
        
        return issues
    
    def _analyze_patterns(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Analyse des patterns problématiques."""
        issues = []
        
        # Détecter les commentaires de debug
        debug_patterns = [
            (r'#.*[Bb]ug.*:', "Commentaire de bug détecté"),
            (r'#.*[Ss]hould.*be', "Commentaire indiquant un problème"),
            (r'#.*[Ii]ncorrect', "Commentaire indiquant une erreur"),
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern, message in debug_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        "type": "debug_comment",
                        "severity": "medium",
                        "line": line_num,
                        "message": message,
                        "code": line.strip(),
                        "suggestion": "Vérifier si le code correspond au commentaire"
                    })
        
        # Détecter les valeurs de retour incorrectes
        return_patterns = [
            (r'return\s+\[\]\s*#.*[Hh]istory', "Retourne une liste vide au lieu de l'historique"),
            (r'return\s+0\s*#.*[Ll]ast.*[Rr]esult', "Retourne toujours 0 au lieu du dernier résultat"),
            (r'pass\s*#.*[Cc]lear', "Ne fait rien au lieu de nettoyer"),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, message in return_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        "type": "return_value_error",
                        "severity": "high",
                        "line": line_num,
                        "message": message,
                        "code": line.strip(),
                        "suggestion": "Corriger la valeur de retour"
                    })
        
        return issues
    
    def _calculate_metrics(self, content: str) -> Dict[str, Any]:
        """Calcule les métriques du code."""
        lines = content.split('\n')
        
        metrics = {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "empty_lines": len([line for line in lines if not line.strip()]),
            "functions": len(re.findall(r'def\s+\w+', content)),
            "classes": len(re.findall(r'class\s+\w+', content)),
            "imports": len(re.findall(r'^import\s+|^from\s+', content, re.MULTILINE)),
        }
        
        return metrics
    
    def _analyze_ast(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyse l'AST du code."""
        try:
            tree = ast.parse(content)
            analysis = {
                "functions": [],
                "classes": [],
                "imports": [],
                "calls": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args]
                    })
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
                elif isinstance(node, ast.Import):
                    analysis["imports"].extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    analysis["imports"].append(f"{node.module}.{', '.join(alias.name for alias in node.names)}")
                elif isinstance(node, ast.Call):
                    if hasattr(node.func, 'id'):
                        analysis["calls"].append({
                            "function": node.func.id,
                            "line": node.lineno
                        })
            
            return analysis
            
        except SyntaxError:
            return {"error": "Impossible d'analyser l'AST - erreur de syntaxe"}
    
    def generate_fix_suggestions(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Génère des suggestions de correction pour les bugs détectés."""
        suggestions = []
        
        for issue in issues:
            if issue["type"] == "semantic_error":
                if "Addition incorrecte" in issue["message"]:
                    suggestions.append({
                        "issue_line": issue["line"],
                        "current_code": issue["code"],
                        "suggested_fix": issue["code"].replace(" - ", " + "),
                        "explanation": "Remplacer la soustraction par l'addition"
                    })
                elif "Soustraction incorrecte" in issue["message"]:
                    suggestions.append({
                        "issue_line": issue["line"],
                        "current_code": issue["code"],
                        "suggested_fix": issue["code"].replace(" + ", " - "),
                        "explanation": "Remplacer l'addition par la soustraction"
                    })
                elif "Multiplication incorrecte" in issue["message"]:
                    suggestions.append({
                        "issue_line": issue["line"],
                        "current_code": issue["code"],
                        "suggested_fix": issue["code"].replace(" / ", " * "),
                        "explanation": "Remplacer la division par la multiplication"
                    })
                elif "Division incorrecte" in issue["message"]:
                    suggestions.append({
                        "issue_line": issue["line"],
                        "current_code": issue["code"],
                        "suggested_fix": issue["code"].replace(" * ", " / "),
                        "explanation": "Remplacer la multiplication par la division"
                    })
                elif "Puissance incorrecte" in issue["message"]:
                    suggestions.append({
                        "issue_line": issue["line"],
                        "current_code": issue["code"],
                        "suggested_fix": issue["code"].replace(" * ", " ** "),
                        "explanation": "Remplacer la multiplication par l'exponentiation"
                    })
                elif "Racine carrée incorrecte" in issue["message"]:
                    suggestions.append({
                        "issue_line": issue["line"],
                        "current_code": issue["code"],
                        "suggested_fix": issue["code"].replace(" / 2", "math.sqrt(number)"),
                        "explanation": "Utiliser math.sqrt() au lieu de diviser par 2"
                    })
            
            elif issue["type"] == "file_operation_error":
                if "Mode d'ouverture incorrect" in issue["message"]:
                    if "'w'" in issue["code"] and "Read" in issue["message"]:
                        suggestions.append({
                            "issue_line": issue["line"],
                            "current_code": issue["code"],
                            "suggested_fix": issue["code"].replace("'w'", "'r'"),
                            "explanation": "Utiliser le mode lecture 'r' au lieu de 'w'"
                        })
                    elif "'r'" in issue["code"] and "Write" in issue["message"]:
                        suggestions.append({
                            "issue_line": issue["line"],
                            "current_code": issue["code"],
                            "suggested_fix": issue["code"].replace("'r'", "'w'"),
                            "explanation": "Utiliser le mode écriture 'w' au lieu de 'r'"
                        })
        
        return suggestions


def code_analyzer(file_path: str, analysis_type: str = 'all') -> Dict[str, Any]:
    """Analyse un fichier Python pour détecter les bugs."""
    analyzer = CodeAnalyzer()
    analysis = analyzer.analyze_file(file_path, analysis_type)
    
    # Générer des suggestions de correction
    if analysis.get("issues"):
        suggestions = analyzer.generate_fix_suggestions(analysis["issues"])
        analysis["fix_suggestions"] = suggestions
    
    return analysis


if __name__ == "__main__":
    # Test de l'analyseur
    test_file = "TestProject/calculator.py"
    if Path(test_file).exists():
        result = code_analyzer(test_file)
        print("Analyse du fichier calculator.py:")
        print(f"Bugs détectés: {len(result.get('issues', []))}")
        for issue in result.get('issues', []):
            print(f"  - Ligne {issue['line']}: {issue['message']}")
    else:
        print(f"Fichier {test_file} non trouvé") 