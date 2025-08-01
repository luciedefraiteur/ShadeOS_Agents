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

# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from Core.implementation.luciform_parser import parse_luciform
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
        
        # Parcours des nœuds
        if 'children' in content:
            for child in content['children']:
                tag = child.get('tag')
                
                if tag == '🜄pacte':
                    self._extract_pacte_info(child, metadata)
                elif tag == '🜂invocation':
                    self._extract_invocation_info(child, metadata)
                elif tag == '🜁essence':
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
                tag = child.get('tag')
                
                if tag == 'signature':
                    text_content = self._extract_text_content(child)
                    if text_content:
                        metadata['signature'] = text_content.strip()
                elif tag == 'requires':
                    params = self._extract_param_list(child)
                    metadata['required_params'] = params
                elif tag == 'optional':
                    params = self._extract_param_list(child)
                    metadata['optional_params'] = params
                elif tag == 'returns':
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
        
        # Extraction de l'ID depuis luciform_doc
        id_match = re.search(r'<🜲luciform_doc\s+id="([^"]+)"', content)
        if id_match:
            metadata['tool_id'] = id_match.group(1)
        
        # Extraction du type
        type_match = re.search(r'<type>([^<]+)</type>', content)
        if type_match:
            metadata['type'] = type_match.group(1).strip()
        
        # Extraction de l'intent
        intent_match = re.search(r'<intent>([^<]+)</intent>', content)
        if intent_match:
            metadata['intent'] = intent_match.group(1).strip()
        
        # Extraction du level
        level_match = re.search(r'<level>([^<]+)</level>', content)
        if level_match:
            metadata['level'] = level_match.group(1).strip()
        
        # Extraction de la signature
        sig_match = re.search(r'<signature>([^<]+)</signature>', content)
        if sig_match:
            metadata['signature'] = sig_match.group(1).strip()
        
        # Extraction des returns
        returns_match = re.search(r'<returns>([^<]+)</returns>', content)
        if returns_match:
            metadata['returns'] = returns_match.group(1).strip()
        
        # Extraction des keywords
        keywords = []
        keyword_matches = re.findall(r'<keyword>([^<]+)</keyword>', content)
        for match in keyword_matches:
            keywords.append(match.strip())
        metadata['keywords'] = keywords
        
        # Extraction des paramètres requis
        required_params = []
        # Recherche dans la section requires
        requires_section = re.search(r'<requires>(.*?)</requires>', content, re.DOTALL)
        if requires_section:
            param_matches = re.findall(r'<param>([^<]+)</param>', requires_section.group(1))
            required_params = [p.strip() for p in param_matches]
        metadata['required_params'] = required_params
        
        # Extraction des paramètres optionnels
        optional_params = []
        optional_section = re.search(r'<optional>(.*?)</optional>', content, re.DOTALL)
        if optional_section:
            param_matches = re.findall(r'<param>([^<]+)</param>', optional_section.group(1))
            optional_params = [p.strip() for p in param_matches]
        metadata['optional_params'] = optional_params
        
        # Extraction du symbolic_layer
        symbolic_match = re.search(r'<symbolic_layer>([^<]+)</symbolic_layer>', content)
        if symbolic_match:
            metadata['symbolic_layer'] = symbolic_match.group(1).strip()
        
        # Extraction du usage_context
        usage_match = re.search(r'<usage_context>([^<]+)</usage_context>', content)
        if usage_match:
            metadata['usage_context'] = usage_match.group(1).strip()
    
    def scan_luciform_directories(self) -> List[Dict[str, Any]]:
        """
        Scanne tous les répertoires de luciformes pour extraire les métadonnées.
        
        Returns:
            Liste des métadonnées extraites
        """
        all_metadata = []
        
        # Répertoires à scanner - SEULS les outils Alma_toolset (non redondants et avancés)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        directories = [
            os.path.join(base_dir, 'Alma_toolset'),
            # Tools/Library IGNORÉ: redondant avec Alma_toolset (versions obsolètes)
            # Tools/Execution IGNORÉ: pas de documentation luciforme
        ]
        
        print(f"⛧ Scan des répertoires de luciformes...")
        
        # Scan de chaque répertoire
        for directory in directories:
            if os.path.exists(directory):
                print(f"  📁 Scanning {directory}")
                count = 0
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.luciform'):
                            file_path = os.path.join(root, file)
                            metadata = self.extract_tool_metadata(file_path)
                            if metadata and metadata.get('tool_id'):
                                all_metadata.append(metadata)
                                count += 1
                print(f"     ✅ {count} outils trouvés")
            else:
                print(f"  ⚠️ Répertoire non trouvé: {directory}")
        
        print(f"⛧ Total: {len(all_metadata)} outils avec métadonnées")
        return all_metadata
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Valide les métadonnées extraites.
        
        Args:
            metadata: Métadonnées à valider
        
        Returns:
            True si valides, False sinon
        """
        # Champs obligatoires
        required_fields = ['tool_id', 'type']
        for field in required_fields:
            if not metadata.get(field):
                return False
        
        # Type mystique valide
        if metadata['type'] not in self.supported_types:
            print(f"⚠️ Type non supporté: {metadata['type']} pour {metadata['tool_id']}")
            return False
        
        return True
    
    def get_statistics(self, metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère des statistiques sur les métadonnées extraites.
        
        Args:
            metadata_list: Liste des métadonnées
        
        Returns:
            Dict avec statistiques
        """
        stats = {
            'total_tools': len(metadata_list),
            'by_type': {},
            'by_level': {},
            'total_keywords': 0,
            'unique_keywords': set(),
            'tools_with_signature': 0,
            'tools_with_symbolic_layer': 0
        }
        
        for metadata in metadata_list:
            # Par type
            tool_type = metadata.get('type', 'unknown')
            stats['by_type'][tool_type] = stats['by_type'].get(tool_type, 0) + 1
            
            # Par niveau
            level = metadata.get('level', 'unknown')
            stats['by_level'][level] = stats['by_level'].get(level, 0) + 1
            
            # Keywords
            keywords = metadata.get('keywords', [])
            stats['total_keywords'] += len(keywords)
            stats['unique_keywords'].update(keywords)
            
            # Signature
            if metadata.get('signature'):
                stats['tools_with_signature'] += 1
            
            # Symbolic layer
            if metadata.get('symbolic_layer'):
                stats['tools_with_symbolic_layer'] += 1
        
        stats['unique_keywords'] = len(stats['unique_keywords'])
        return stats


def main():
    """Test du parser de métadonnées."""
    print("⛧ Test du Parser de Métadonnées d'Outils Mystiques ⛧")
    print()
    
    parser = LuciformToolMetadataParser()
    
    # Test sur un fichier spécifique
    test_file = os.path.join(os.path.dirname(__file__), '../../Alma_toolset/regex_search_file.luciform')
    if os.path.exists(test_file):
        print(f"📄 Test sur: {os.path.basename(test_file)}")
        metadata = parser.extract_tool_metadata(test_file)
        if metadata:
            print(f"  ✅ Tool ID: {metadata.get('tool_id')}")
            print(f"  🎭 Type: {metadata.get('type')}")
            print(f"  📝 Intent: {metadata.get('intent')[:50]}..." if metadata.get('intent') else "  📝 Intent: None")
            print(f"  📊 Level: {metadata.get('level')}")
            print(f"  🏷️ Keywords: {metadata.get('keywords')}")
            print(f"  ✅ Validation: {parser.validate_metadata(metadata)}")
        else:
            print("  ❌ Échec extraction")
        print()
    
    # Test sur tous les outils
    print("🔍 Extraction de toutes les métadonnées...")
    all_metadata = parser.scan_luciform_directories()
    
    # Statistiques
    stats = parser.get_statistics(all_metadata)
    print(f"\n📊 Statistiques:")
    print(f"  📦 Total outils: {stats['total_tools']}")
    print(f"  🎭 Par type: {dict(stats['by_type'])}")
    print(f"  📊 Par niveau: {dict(stats['by_level'])}")
    print(f"  🏷️ Keywords uniques: {stats['unique_keywords']}")
    print(f"  📝 Avec signature: {stats['tools_with_signature']}")
    print(f"  ⛧ Avec symbolic_layer: {stats['tools_with_symbolic_layer']}")


if __name__ == "__main__":
    main()
