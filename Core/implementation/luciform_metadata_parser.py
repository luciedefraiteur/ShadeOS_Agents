#!/usr/bin/env python3
"""
⛧ Luciform Metadata Parser ⛧
Alma's Mystical Metadata Extractor

Extracteur de métadonnées mystiques depuis les luciformes.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import sys
import re
from typing import Dict, List, Optional, Any

# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Core.implementation.luciform_parser import parse_luciform


def extract_tool_metadata(luciform_path: str) -> Optional[Dict[str, Any]]:
    """
    Extrait les métadonnées mystiques d'un fichier luciform.
    
    Args:
        luciform_path: Chemin vers le fichier luciform
    
    Returns:
        Dict avec métadonnées ou None si erreur
    """
    try:
        # Parse du luciform
        parsed = parse_luciform(luciform_path)
        if not parsed or 'success' not in parsed or not parsed['success']:
            return None
        
        # Extraction des métadonnées
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
        
        # Lecture du contenu brut pour recherches textuelles
        try:
            with open(luciform_path, 'r', encoding='utf-8') as f:
                metadata['raw_content'] = f.read()
        except:
            pass
        
        # Extraction depuis la structure parsée
        if 'content' in parsed:
            content = parsed['content']
            
            # ID de l'outil depuis l'attribut luciform_doc
            if isinstance(content, dict) and 'attributes' in content:
                metadata['tool_id'] = content['attributes'].get('id')
            
            # Parcours des nœuds pour extraire les informations
            if 'children' in content:
                for child in content['children']:
                    if child.get('tag') == '🜄pacte':
                        metadata.update(_extract_pacte_info(child))
                    elif child.get('tag') == '🜂invocation':
                        metadata.update(_extract_invocation_info(child))
                    elif child.get('tag') == '🜁essence':
                        metadata.update(_extract_essence_info(child))
        
        return metadata
        
    except Exception as e:
        print(f"Erreur extraction métadonnées {luciform_path}: {e}")
        return None


def _extract_pacte_info(pacte_node: Dict) -> Dict[str, Any]:
    """Extrait les informations du pacte."""
    info = {}
    
    if 'children' in pacte_node:
        for child in pacte_node['children']:
            tag = child.get('tag')
            if tag in ['type', 'intent', 'level']:
                text_content = _extract_text_content(child)
                if text_content:
                    info[tag] = text_content.strip()
    
    return info


def _extract_invocation_info(invocation_node: Dict) -> Dict[str, Any]:
    """Extrait les informations d'invocation."""
    info = {}
    
    if 'children' in invocation_node:
        for child in invocation_node['children']:
            tag = child.get('tag')
            
            if tag == 'signature':
                text_content = _extract_text_content(child)
                if text_content:
                    info['signature'] = text_content.strip()
            
            elif tag == 'requires':
                params = _extract_param_list(child)
                info['required_params'] = params
            
            elif tag == 'optional':
                params = _extract_param_list(child)
                info['optional_params'] = params
            
            elif tag == 'returns':
                text_content = _extract_text_content(child)
                if text_content:
                    info['returns'] = text_content.strip()
    
    return info


def _extract_essence_info(essence_node: Dict) -> Dict[str, Any]:
    """Extrait les informations d'essence."""
    info = {}
    
    if 'children' in essence_node:
        for child in essence_node['children']:
            tag = child.get('tag')
            
            if tag == 'keywords':
                keywords = _extract_keywords_list(child)
                info['keywords'] = keywords
            
            elif tag == 'symbolic_layer':
                text_content = _extract_text_content(child)
                if text_content:
                    info['symbolic_layer'] = text_content.strip()
            
            elif tag == 'usage_context':
                text_content = _extract_text_content(child)
                if text_content:
                    info['usage_context'] = text_content.strip()
    
    return info


def _extract_text_content(node: Dict) -> Optional[str]:
    """Extrait le contenu textuel d'un nœud."""
    if 'children' in node:
        for child in node['children']:
            if child.get('tag') == 'text':
                return child.get('content', '')
    return None


def _extract_param_list(node: Dict) -> List[str]:
    """Extrait une liste de paramètres."""
    params = []
    
    if 'children' in node:
        for child in node['children']:
            if child.get('tag') == 'param':
                text_content = _extract_text_content(child)
                if text_content:
                    params.append(text_content.strip())
    
    return params


def _extract_keywords_list(node: Dict) -> List[str]:
    """Extrait une liste de mots-clés."""
    keywords = []
    
    if 'children' in node:
        for child in node['children']:
            if child.get('tag') == 'keyword':
                text_content = _extract_text_content(child)
                if text_content:
                    keywords.append(text_content.strip())
    
    return keywords


def scan_luciform_directory(directory: str) -> List[Dict[str, Any]]:
    """
    Scanne un répertoire pour extraire toutes les métadonnées luciformes.
    
    Args:
        directory: Répertoire à scanner
    
    Returns:
        Liste des métadonnées extraites
    """
    metadata_list = []
    
    if not os.path.exists(directory):
        return metadata_list
    
    # Parcours récursif du répertoire
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.luciform'):
                file_path = os.path.join(root, file)
                metadata = extract_tool_metadata(file_path)
                if metadata:
                    metadata_list.append(metadata)
    
    return metadata_list


def extract_all_tool_metadata() -> List[Dict[str, Any]]:
    """
    Extrait toutes les métadonnées des outils du projet.
    
    Returns:
        Liste complète des métadonnées
    """
    all_metadata = []
    
    # Répertoires à scanner
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    directories = [
        os.path.join(base_dir, 'Tools/Library/documentation/luciforms'),
        os.path.join(base_dir, 'Alma_toolset'),
        os.path.join(base_dir, 'Tools/Search/documentation/luciforms'),
        os.path.join(base_dir, 'Tools/FileSystem/documentation/luciforms'),
        os.path.join(base_dir, 'Tools/Execution/documentation/luciforms'),
    ]
    
    # Scan de chaque répertoire
    for directory in directories:
        if os.path.exists(directory):
            metadata_list = scan_luciform_directory(directory)
            all_metadata.extend(metadata_list)
    
    return all_metadata


def create_metadata_index(metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Crée un index des métadonnées pour recherche rapide.
    
    Args:
        metadata_list: Liste des métadonnées
    
    Returns:
        Index structuré pour recherche
    """
    index = {
        'by_type': {},
        'by_level': {},
        'by_keyword': {},
        'by_tool_id': {},
        'all_tools': metadata_list
    }
    
    for metadata in metadata_list:
        tool_id = metadata.get('tool_id')
        tool_type = metadata.get('type')
        level = metadata.get('level')
        keywords = metadata.get('keywords', [])
        
        # Index par ID
        if tool_id:
            index['by_tool_id'][tool_id] = metadata
        
        # Index par type
        if tool_type:
            if tool_type not in index['by_type']:
                index['by_type'][tool_type] = []
            index['by_type'][tool_type].append(metadata)
        
        # Index par niveau
        if level:
            if level not in index['by_level']:
                index['by_level'][level] = []
            index['by_level'][level].append(metadata)
        
        # Index par mots-clés
        for keyword in keywords:
            if keyword not in index['by_keyword']:
                index['by_keyword'][keyword] = []
            index['by_keyword'][keyword].append(metadata)
    
    return index


def main():
    """Test du parser de métadonnées."""
    print("⛧ Test du Parser de Métadonnées Mystiques ⛧")
    print()
    
    # Test sur un fichier spécifique
    test_file = os.path.join(os.path.dirname(__file__), '../../Alma_toolset/regex_search_file.luciform')
    if os.path.exists(test_file):
        print(f"Test sur: {test_file}")
        metadata = extract_tool_metadata(test_file)
        if metadata:
            print(f"Tool ID: {metadata.get('tool_id')}")
            print(f"Type: {metadata.get('type')}")
            print(f"Intent: {metadata.get('intent')}")
            print(f"Level: {metadata.get('level')}")
            print(f"Keywords: {metadata.get('keywords')}")
            print()
    
    # Test sur tous les outils
    print("Extraction de toutes les métadonnées...")
    all_metadata = extract_all_tool_metadata()
    print(f"Trouvé {len(all_metadata)} outils avec métadonnées")
    
    # Création de l'index
    index = create_metadata_index(all_metadata)
    print(f"Types disponibles: {list(index['by_type'].keys())}")
    print(f"Niveaux disponibles: {list(index['by_level'].keys())}")
    print(f"Mots-clés disponibles: {len(index['by_keyword'])} uniques")


if __name__ == "__main__":
    main()
