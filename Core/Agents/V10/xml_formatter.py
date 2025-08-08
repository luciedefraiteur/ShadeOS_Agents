#!/usr/bin/env python3
"""
⛧ V10 XML Formatter ⛧
Alma's Optimized XML Formatting for V10

Formatage XML optimisé selon les insights ShadeOS.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import re
from typing import Dict, Any, List, Optional
from enum import Enum


class FormatType(Enum):
    """Types de formatage XML optimisés."""
    MINIMAL = "minimal"           # Format minimal pour outils simples
    DETAILED = "detailed"         # Format détaillé pour outils complexes
    STANDARD = "standard"         # Format standard équilibré
    COMPACT = "compact"           # Format compact pour performance


class V10XMLFormatter:
    """Formatage XML optimisé selon insights ShadeOS."""
    
    def __init__(self):
        """Initialise le formateur XML."""
        self.optimization_rules = self._load_optimization_rules()
        self.tool_patterns = self._load_tool_patterns()
    
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Charge les règles d'optimisation selon ShadeOS."""
        return {
            "minimal": {
                "remove_whitespace": True,
                "compact_attributes": True,
                "remove_comments": True,
                "optimize_tags": True
            },
            "detailed": {
                "remove_whitespace": False,
                "compact_attributes": False,
                "remove_comments": False,
                "optimize_tags": False
            },
            "standard": {
                "remove_whitespace": True,
                "compact_attributes": True,
                "remove_comments": True,
                "optimize_tags": False
            },
            "compact": {
                "remove_whitespace": True,
                "compact_attributes": True,
                "remove_comments": True,
                "optimize_tags": True,
                "minimize_attributes": True
            }
        }
    
    def _load_tool_patterns(self) -> Dict[str, str]:
        """Charge les patterns d'outils pour optimisation."""
        return {
            "read_file": "minimal",
            "write_file": "minimal",
            "list_directory": "minimal",
            "execute_command": "detailed",
            "code_analysis": "detailed",
            "import_analysis": "detailed",
            "mcp_tool": "standard",
            "mcp_resource": "standard"
        }
    
    def format_tool_call(self, tool_name: str, parameters: Dict[str, Any], format_type: Optional[str] = None) -> str:
        """
        Formate un appel d'outil en XML optimisé.
        
        Args:
            tool_name: Nom de l'outil
            parameters: Paramètres de l'outil
            format_type: Type de formatage (auto-détecté si None)
        
        Returns:
            XML formaté optimisé
        """
        # Auto-détection du format si non spécifié
        if format_type is None:
            format_type = self._determine_format_type(tool_name, parameters)
        
        # Récupération des règles d'optimisation
        rules = self.optimization_rules.get(format_type, self.optimization_rules["standard"])
        
        # Génération du XML de base
        xml_content = self._generate_base_xml(tool_name, parameters)
        
        # Application des optimisations
        optimized_xml = self._apply_optimizations(xml_content, rules)
        
        return optimized_xml
    
    def _determine_format_type(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Détermine le type de formatage optimal."""
        # Vérifier les patterns d'outils
        if tool_name in self.tool_patterns:
            return self.tool_patterns[tool_name]
        
        # Heuristiques basées sur les paramètres
        param_count = len(parameters)
        param_complexity = self._calculate_parameter_complexity(parameters)
        
        if param_count <= 2 and param_complexity <= 1:
            return "minimal"
        elif param_count >= 5 or param_complexity >= 3:
            return "detailed"
        elif "mcp" in tool_name.lower():
            return "standard"
        else:
            return "standard"
    
    def _calculate_parameter_complexity(self, parameters: Dict[str, Any]) -> int:
        """Calcule la complexité des paramètres."""
        complexity = 0
        
        for value in parameters.values():
            if isinstance(value, dict):
                complexity += 2
            elif isinstance(value, list):
                complexity += 1
            elif isinstance(value, str) and len(value) > 100:
                complexity += 1
            else:
                complexity += 0
        
        return complexity
    
    def _generate_base_xml(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Génère le XML de base."""
        xml_lines = ['<tool_call>']
        xml_lines.append(f'  <tool_name>{tool_name}</tool_name>')
        
        if parameters:
            xml_lines.append('  <parameters>')
            for key, value in parameters.items():
                xml_lines.append(f'    <{key}>{self._escape_xml_value(value)}</{key}>')
            xml_lines.append('  </parameters>')
        
        xml_lines.append('</tool_call>')
        
        return '\n'.join(xml_lines)
    
    def _escape_xml_value(self, value: Any) -> str:
        """Échappe une valeur pour XML."""
        if isinstance(value, str):
            return value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        elif isinstance(value, dict):
            return str(value)  # Simplifié pour l'exemple
        elif isinstance(value, list):
            return ', '.join(str(item) for item in value)
        else:
            return str(value)
    
    def _apply_optimizations(self, xml_content: str, rules: Dict[str, Any]) -> str:
        """Applique les optimisations selon les règles."""
        optimized = xml_content
        
        # Suppression des espaces blancs
        if rules.get("remove_whitespace", False):
            optimized = re.sub(r'\s+', ' ', optimized)
            optimized = optimized.strip()
        
        # Compactage des attributs
        if rules.get("compact_attributes", False):
            optimized = re.sub(r'>\s*<', '><', optimized)
        
        # Suppression des commentaires
        if rules.get("remove_comments", False):
            optimized = re.sub(r'<!--.*?-->', '', optimized, flags=re.DOTALL)
        
        # Optimisation des balises
        if rules.get("optimize_tags", False):
            optimized = self._optimize_tags(optimized)
        
        # Minimisation des attributs
        if rules.get("minimize_attributes", False):
            optimized = self._minimize_attributes(optimized)
        
        return optimized
    
    def _optimize_tags(self, xml_content: str) -> str:
        """Optimise les balises XML."""
        # Remplace les balises vides par des balises auto-fermantes
        xml_content = re.sub(r'<(\w+)>\s*</\1>', r'<\1/>', xml_content)
        
        return xml_content
    
    def _minimize_attributes(self, xml_content: str) -> str:
        """Minimise les attributs XML."""
        # Supprime les attributs vides
        xml_content = re.sub(r'\s+\w+=""', '', xml_content)
        
        return xml_content
    
    def format_tool_response(self, tool_name: str, result: Any, format_type: Optional[str] = None) -> str:
        """
        Formate une réponse d'outil en XML optimisé.
        
        Args:
            tool_name: Nom de l'outil
            result: Résultat de l'outil
            format_type: Type de formatage
        
        Returns:
            XML de réponse formaté
        """
        if format_type is None:
            format_type = self._determine_format_type(tool_name, {})
        
        rules = self.optimization_rules.get(format_type, self.optimization_rules["standard"])
        
        # Génération du XML de réponse
        xml_content = self._generate_response_xml(tool_name, result)
        
        # Application des optimisations
        optimized_xml = self._apply_optimizations(xml_content, rules)
        
        return optimized_xml
    
    def _generate_response_xml(self, tool_name: str, result: Any) -> str:
        """Génère le XML de réponse."""
        xml_lines = ['<tool_response>']
        xml_lines.append(f'  <tool_name>{tool_name}</tool_name>')
        xml_lines.append(f'  <success>{isinstance(result, dict) and result.get("success", True)}</success>')
        
        if isinstance(result, dict):
            xml_lines.append('  <data>')
            for key, value in result.items():
                if key != "success":
                    xml_lines.append(f'    <{key}>{self._escape_xml_value(value)}</{key}>')
            xml_lines.append('  </data>')
        else:
            xml_lines.append(f'  <result>{self._escape_xml_value(result)}</result>')
        
        xml_lines.append('</tool_response>')
        
        return '\n'.join(xml_lines)
    
    def get_format_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de formatage."""
        return {
            "optimization_rules": len(self.optimization_rules),
            "tool_patterns": len(self.tool_patterns),
            "supported_formats": [format.value for format in FormatType],
            "default_format": "standard"
        }
