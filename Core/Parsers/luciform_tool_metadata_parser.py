#!/usr/bin/env python3
"""
⛧ Luciform Tool Metadata Parser ⛧
Alma's Mystical Metadata Extractor

Extracteur de métadonnées mystiques depuis les luciformes d'outils.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import sys
import re
from typing import Dict, List, Optional, Any

try:
    from .luciform_parser import parse_luciform
except ImportError:
    print("⚠️ luciform_parser non trouvé, utilisation du parser de base")
    parse_luciform = None


class LuciformToolMetadataParser:
    """Parser spécialisé pour extraire les métadonnées des outils mystiques."""
    
    def __init__(self):
        """Initialise le parser."""
        self.supported_types = {
            'divination', 'protection', 'transmutation', 'scrying',
            'augury', 'memory', 'inscription', 'revelation', 'metamorphosis'
        }
    
    def extract_tool_metadata(self, luciform_path: str) -> Optional[Dict[str, Any]]:
        """
        Extrait les métadonnées mystiques d'un fichier luciform.
        
        Args:
            luciform_path: Chemin vers le fichier luciform
        
        Returns:
            Dict avec métadonnées ou None si erreur
        """
        try:
            # Initialisation des métadonnées
            metadata = {
                'file_path': luciform_path,
                'tool_id': None,
                'type': None,
                'intent': None,
                'level': None,
                'keywords': [],
                'signature': None,
                'required_params': [],
                'optional_params': [],
                'returns': None,
                'symbolic_layer': None,
                'usage_context': None,
                'raw_content': None
            }
            
            # Lecture du contenu brut
            try:
                with open(luciform_path, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                metadata['raw_content'] = raw_content
            except Exception as e:
                print(f"Erreur lecture {luciform_path}: {e}")
                return None
            
            # Tentative avec le parser officiel
            if parse_luciform:
                parsed = parse_luciform(luciform_path)
                if parsed and parsed.get('success'):
                    self._extract_from_parsed_structure(parsed, metadata)
                    if metadata.get('tool_id'):
                        return metadata
            
            # Fallback : parsing manuel par regex
            self._extract_with_regex_fallback(raw_content, metadata)
            
            # Validation finale
            if metadata.get('tool_id') and metadata.get('type'):
                return metadata
            
            return None
            
        except Exception as e:
            print(f"Erreur extraction métadonnées {luciform_path}: {e}")
            return None
    
    def _extract_from_parsed_structure(self, parsed: Dict, metadata: Dict):
        """Extrait depuis la structure parsée officielle."""
        content = parsed.get('content', {})
        
        # ID de l'outil depuis l'attribut luciform_doc
        if 'attributes' in content:
            metadata['tool_id'] = content['attributes'].get('id')
        
        # Parcours des nœuds pour extraire les informations
        if 'children' in content:
            for child in content['children']:
                if child.get('tag') == '🜄pacte':
                    self._extract_pacte_info(child, metadata)
                elif child.get('tag') == '🜂invocation':
                    self._extract_invocation_info(child, metadata)
                elif child.get('tag') == '🜁essence':
                    self._extract_essence_info(child, metadata)
    
    def _extract_pacte_info(self, pacte_node: Dict, metadata: Dict):
        """Extrait les informations du pacte."""
        if 'children' in pacte_node:
            for child in pacte_node['children']:
                tag = child.get('tag')
                if tag in ['type', 'intent', 'level']:
                    text_content = self._extract_text_content(child)
                    if text_content:
                        metadata[tag] = text_content.strip()
    
    def _extract_invocation_info(self, invocation_node: Dict, metadata: Dict):
        """Extrait les informations d'invocation."""
        if 'children' in invocation_node:
            for child in invocation_node['children']:
                if child.get('tag') == 'signature':
                    text_content = self._extract_text_content(child)
                    if text_content:
                        metadata['signature'] = text_content.strip()
                elif child.get('tag') == 'required_params':
                    params = self._extract_param_list(child)
                    metadata['required_params'] = params
                elif child.get('tag') == 'optional_params':
                    params = self._extract_param_list(child)
                    metadata['optional_params'] = params
                elif child.get('tag') == 'returns':
                    text_content = self._extract_text_content(child)
                    if text_content:
                        metadata['returns'] = text_content.strip()
    
    def _extract_essence_info(self, essence_node: Dict, metadata: Dict):
        """Extrait les informations d'essence."""
        if 'children' in essence_node:
            for child in essence_node['children']:
                tag = child.get('tag')
                
                if tag == 'keywords':
                    keywords = self._extract_keywords_list(child)
                    metadata['keywords'] = keywords
                elif tag == 'symbolic_layer':
                    text_content = self._extract_text_content(child)
                    if text_content:
                        metadata['symbolic_layer'] = text_content.strip()
                elif tag == 'usage_context':
                    text_content = self._extract_text_content(child)
                    if text_content:
                        metadata['usage_context'] = text_content.strip()
    
    def _extract_text_content(self, node: Dict) -> Optional[str]:
        """Extrait le contenu textuel d'un nœud."""
        if 'children' in node:
            for child in node['children']:
                if child.get('tag') == 'text':
                    return child.get('content', '')
        return None
    
    def _extract_param_list(self, node: Dict) -> List[str]:
        """Extrait une liste de paramètres."""
        params = []
        if 'children' in node:
            for child in node['children']:
                if child.get('tag') == 'param':
                    text_content = self._extract_text_content(child)
                    if text_content:
                        params.append(text_content.strip())
        return params
    
    def _extract_keywords_list(self, node: Dict) -> List[str]:
        """Extrait une liste de mots-clés."""
        keywords = []
        if 'children' in node:
            for child in node['children']:
                if child.get('tag') == 'keyword':
                    text_content = self._extract_text_content(child)
                    if text_content:
                        keywords.append(text_content.strip())
        return keywords
    
    def _extract_with_regex_fallback(self, content: str, metadata: Dict):
        """Extraction par regex en cas d'échec du parser officiel."""
        try:
            # Extraction de l'ID depuis l'attribut luciform_doc
            id_match = re.search(r'luciform_doc\s*=\s*"([^"]+)"', content)
            if id_match:
                metadata['tool_id'] = id_match.group(1)
            
            # Extraction du type depuis 🜄pacte
            type_match = re.search(r'<🜄pacte[^>]*>.*?<type>([^<]+)</type>', content, re.DOTALL)
            if type_match:
                metadata['type'] = type_match.group(1).strip()
            
            # Extraction de l'intent depuis 🜄pacte
            intent_match = re.search(r'<🜄pacte[^>]*>.*?<intent>([^<]+)</intent>', content, re.DOTALL)
            if intent_match:
                metadata['intent'] = intent_match.group(1).strip()
            
            # Extraction du level depuis 🜄pacte
            level_match = re.search(r'<🜄pacte[^>]*>.*?<level>([^<]+)</level>', content, re.DOTALL)
            if level_match:
                metadata['level'] = level_match.group(1).strip()
            
            # Extraction de la signature depuis 🜂invocation
            signature_match = re.search(r'<🜂invocation[^>]*>.*?<signature>([^<]+)</signature>', content, re.DOTALL)
            if signature_match:
                metadata['signature'] = signature_match.group(1).strip()
            
            # Extraction des mots-clés depuis 🜁essence
            keywords_matches = re.findall(r'<🜁essence[^>]*>.*?<keyword>([^<]+)</keyword>', content, re.DOTALL)
            if keywords_matches:
                metadata['keywords'] = [kw.strip() for kw in keywords_matches]
            
            # Extraction de la couche symbolique
            symbolic_match = re.search(r'<🜁essence[^>]*>.*?<symbolic_layer>([^<]+)</symbolic_layer>', content, re.DOTALL)
            if symbolic_match:
                metadata['symbolic_layer'] = symbolic_match.group(1).strip()
            
            # Extraction du contexte d'usage
            context_match = re.search(r'<🜁essence[^>]*>.*?<usage_context>([^<]+)</usage_context>', content, re.DOTALL)
            if context_match:
                metadata['usage_context'] = context_match.group(1).strip()
                
        except Exception as e:
            print(f"Erreur extraction regex: {e}")
    
    def scan_luciform_directories(self) -> List[Dict[str, Any]]:
        """
        Scanne tous les répertoires de luciformes pour extraire les métadonnées.
        
        Returns:
            Liste des métadonnées extraites
        """
        all_metadata = []
        
        # Répertoires à scanner
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        directories = [
            os.path.join(base_dir, 'Tools/Library/documentation/luciforms'),
            os.path.join(base_dir, 'Assistants', 'EditingSession', 'Tools'),
            os.path.join(base_dir, 'Tools/Search/documentation/luciforms'),
            os.path.join(base_dir, 'Tools/FileSystem/documentation/luciforms'),
            os.path.join(base_dir, 'Tools/Execution/documentation/luciforms'),
        ]
        
        # Scan de chaque répertoire
        for directory in directories:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.luciform'):
                            file_path = os.path.join(root, file)
                            metadata = self.extract_tool_metadata(file_path)
                            if metadata and metadata.get('tool_id'):
                                all_metadata.append(metadata)
        
        return all_metadata
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Valide les métadonnées extraites.
        
        Args:
            metadata: Métadonnées à valider
        
        Returns:
            True si valide, False sinon
        """
        required_fields = ['tool_id', 'type', 'intent']
        
        for field in required_fields:
            if not metadata.get(field):
                print(f"⚠️ Champ requis manquant: {field}")
                return False
        
        # Validation du type
        if metadata.get('type') not in self.supported_types:
            print(f"⚠️ Type non supporté: {metadata.get('type')}")
            return False
        
        return True
    
    def get_statistics(self, metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère des statistiques sur une liste de métadonnées.
        
        Args:
            metadata_list: Liste des métadonnées
        
        Returns:
            Dict avec statistiques
        """
        stats = {
            'total_tools': len(metadata_list),
            'types': {},
            'levels': {},
            'validation_errors': 0,
            'missing_fields': {}
        }
        
        for metadata in metadata_list:
            # Statistiques par type
            tool_type = metadata.get('type', 'unknown')
            stats['types'][tool_type] = stats['types'].get(tool_type, 0) + 1
            
            # Statistiques par niveau
            level = metadata.get('level', 'unknown')
            stats['levels'][level] = stats['levels'].get(level, 0) + 1
            
            # Validation
            if not self.validate_metadata(metadata):
                stats['validation_errors'] += 1
            
            # Champs manquants
            for field in ['signature', 'keywords', 'symbolic_layer', 'usage_context']:
                if not metadata.get(field):
                    stats['missing_fields'][field] = stats['missing_fields'].get(field, 0) + 1
        
        return stats 