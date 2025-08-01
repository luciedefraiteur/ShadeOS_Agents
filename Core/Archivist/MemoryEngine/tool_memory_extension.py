#!/usr/bin/env python3
"""
⛧ Tool Memory Extension ⛧
Alma's Mystical Tool Indexer for MemoryEngine

Extension du MemoryEngine pour indexer et rechercher les outils mystiques.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import sys
import json
from typing import Dict, List, Optional, Any

# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from Core.implementation.luciform_parser import parse_luciform


class ToolMemoryExtension:
    """Extension du MemoryEngine pour la gestion des outils mystiques."""
    
    def __init__(self, memory_engine):
        """
        Initialise l'extension avec un MemoryEngine existant.
        
        Args:
            memory_engine: Instance du MemoryEngine
        """
        self.memory_engine = memory_engine
        self.tools_namespace = "/tools"
        self.indexed = False
    
    def extract_tool_metadata(self, luciform_path: str) -> Optional[Dict[str, Any]]:
        """
        Extrait les métadonnées d'un fichier luciform.
        
        Args:
            luciform_path: Chemin vers le fichier luciform
        
        Returns:
            Dict avec métadonnées ou None si erreur
        """
        try:
            # Parse du luciform
            parsed = parse_luciform(luciform_path)
            if not parsed or not parsed.get('success'):
                return None
            
            metadata = {
                'file_path': luciform_path,
                'tool_id': None,
                'type': None,
                'intent': None,
                'level': None,
                'keywords': [],
                'signature': None,
                'symbolic_layer': None,
                'usage_context': None
            }
            
            # Extraction depuis la structure parsée
            content = parsed.get('content', {})
            
            # ID de l'outil
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
            
            return metadata
            
        except Exception as e:
            print(f"Erreur extraction métadonnées {luciform_path}: {e}")
            return None
    
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
            os.path.join(base_dir, 'Alma_toolset'),
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
    
    def index_all_tools(self, force_reindex: bool = False):
        """
        Indexe tous les outils dans le MemoryEngine.
        
        Args:
            force_reindex: Force la réindexation même si déjà fait
        """
        if self.indexed and not force_reindex:
            return
        
        print("⛧ Indexation des outils mystiques dans le MemoryEngine...")
        
        # Extraction des métadonnées
        all_metadata = self.scan_luciform_directories()
        
        # Indexation dans le MemoryEngine
        for metadata in all_metadata:
            tool_id = metadata['tool_id']
            tool_type = metadata.get('type', 'unknown')
            
            # Chemin dans le namespace des outils
            tool_path = f"{self.tools_namespace}/{tool_type}/{tool_id}"
            
            # Contenu pour le MemoryEngine
            content = json.dumps(metadata, indent=2, ensure_ascii=False)
            summary = f"{tool_type.title()} tool: {metadata.get('intent', tool_id)}"
            keywords = [tool_type, tool_id] + metadata.get('keywords', [])
            
            # Création du nœud mémoire
            try:
                self.memory_engine.create_memory(
                    path=tool_path,
                    content=content,
                    summary=summary,
                    keywords=keywords,
                    strata="cognitive"  # Strate cognitive pour les outils
                )
            except Exception as e:
                print(f"Erreur indexation {tool_id}: {e}")
        
        self.indexed = True
        print(f"⛧ {len(all_metadata)} outils indexés avec succès !")
    
    def find_tools_by_type(self, tool_type: str) -> List[Dict[str, Any]]:
        """
        Trouve tous les outils d'un type mystique donné.
        
        Args:
            tool_type: Type mystique (divination, protection, etc.)
        
        Returns:
            Liste des outils correspondants
        """
        if not self.indexed:
            self.index_all_tools()
        
        # Recherche par mot-clé dans le namespace des outils
        tool_paths = self.memory_engine.find_memories_by_keyword(tool_type)
        
        # Filtrage pour ne garder que les outils du bon type
        tools = []
        for path in tool_paths:
            if path.startswith(f"{self.tools_namespace}/{tool_type}/"):
                node = self.memory_engine.get_memory_node(path)
                if node and node.content:
                    try:
                        metadata = json.loads(node.content)
                        tools.append(metadata)
                    except:
                        pass
        
        return tools
    
    def find_tools_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Trouve les outils contenant un mot-clé spécifique.
        
        Args:
            keyword: Mot-clé à rechercher
        
        Returns:
            Liste des outils correspondants
        """
        if not self.indexed:
            self.index_all_tools()
        
        # Recherche par mot-clé
        tool_paths = self.memory_engine.find_memories_by_keyword(keyword)
        
        # Filtrage pour ne garder que les outils
        tools = []
        for path in tool_paths:
            if path.startswith(self.tools_namespace):
                node = self.memory_engine.get_memory_node(path)
                if node and node.content:
                    try:
                        metadata = json.loads(node.content)
                        tools.append(metadata)
                    except:
                        pass
        
        return tools
    
    def find_tools_by_level(self, level: str) -> List[Dict[str, Any]]:
        """
        Trouve les outils par niveau de complexité.
        
        Args:
            level: Niveau (fondamental, intermédiaire, avancé)
        
        Returns:
            Liste des outils du niveau spécifié
        """
        if not self.indexed:
            self.index_all_tools()
        
        # Recherche par mot-clé niveau
        tool_paths = self.memory_engine.find_memories_by_keyword(level)
        
        # Filtrage et vérification du niveau
        tools = []
        for path in tool_paths:
            if path.startswith(self.tools_namespace):
                node = self.memory_engine.get_memory_node(path)
                if node and node.content:
                    try:
                        metadata = json.loads(node.content)
                        if metadata.get('level') == level:
                            tools.append(metadata)
                    except:
                        pass
        
        return tools
    
    def search_tools(self, tool_type: str = None, keyword: str = None, 
                    level: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Recherche combinée d'outils avec multiple critères.
        
        Args:
            tool_type: Type mystique optionnel
            keyword: Mot-clé optionnel
            level: Niveau optionnel
            limit: Nombre maximum de résultats
        
        Returns:
            Liste triée des outils correspondants
        """
        if not self.indexed:
            self.index_all_tools()
        
        # Collecte des résultats selon les critères
        results = set()
        
        if tool_type:
            type_tools = self.find_tools_by_type(tool_type)
            results.update(tool['tool_id'] for tool in type_tools if tool.get('tool_id'))
        
        if keyword:
            keyword_tools = self.find_tools_by_keyword(keyword)
            keyword_ids = set(tool['tool_id'] for tool in keyword_tools if tool.get('tool_id'))
            if results:
                results = results.intersection(keyword_ids)
            else:
                results = keyword_ids
        
        if level:
            level_tools = self.find_tools_by_level(level)
            level_ids = set(tool['tool_id'] for tool in level_tools if tool.get('tool_id'))
            if results:
                results = results.intersection(level_ids)
            else:
                results = level_ids
        
        # Si aucun critère, retourner tous les outils
        if not (tool_type or keyword or level):
            all_paths = []
            # Parcourir le namespace des outils
            try:
                # Cette méthode dépend de l'implémentation du backend
                # Pour l'instant, on utilise une approche simple
                results = set()
            except:
                pass
        
        # Récupération des métadonnées complètes
        final_tools = []
        for tool_id in list(results)[:limit]:
            # Recherche du chemin complet
            tool_paths = self.memory_engine.find_memories_by_keyword(tool_id)
            for path in tool_paths:
                if path.startswith(self.tools_namespace) and path.endswith(f"/{tool_id}"):
                    node = self.memory_engine.get_memory_node(path)
                    if node and node.content:
                        try:
                            metadata = json.loads(node.content)
                            final_tools.append(metadata)
                            break
                        except:
                            pass
        
        return final_tools
    
    def get_tool_info(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations complètes d'un outil.
        
        Args:
            tool_id: Identifiant de l'outil
        
        Returns:
            Métadonnées de l'outil ou None
        """
        if not self.indexed:
            self.index_all_tools()
        
        # Recherche par ID
        tool_paths = self.memory_engine.find_memories_by_keyword(tool_id)
        
        for path in tool_paths:
            if path.startswith(self.tools_namespace) and path.endswith(f"/{tool_id}"):
                node = self.memory_engine.get_memory_node(path)
                if node and node.content:
                    try:
                        return json.loads(node.content)
                    except:
                        pass
        
        return None
    
    def list_all_tool_types(self) -> List[str]:
        """
        Liste tous les types mystiques d'outils disponibles.
        
        Returns:
            Liste des types uniques
        """
        if not self.indexed:
            self.index_all_tools()
        
        # Cette méthode nécessiterait une amélioration du backend
        # Pour l'instant, on retourne les types connus
        return [
            'divination', 'protection', 'transmutation', 'scrying',
            'augury', 'memory', 'inscription', 'revelation', 'metamorphosis'
        ]


def main():
    """Test de l'extension Tool Memory."""
    from Core.Archivist.MemoryEngine.engine import MemoryEngine
    
    print("⛧ Test de l'Extension Tool Memory ⛧")
    print()
    
    # Initialisation du MemoryEngine
    memory_engine = MemoryEngine(backend_type="filesystem", base_path="./test_tool_memory")
    
    # Création de l'extension
    tool_extension = ToolMemoryExtension(memory_engine)
    
    # Test d'indexation
    tool_extension.index_all_tools()
    
    # Test de recherche par type
    print("=== Recherche par type 'divination' ===")
    divination_tools = tool_extension.find_tools_by_type("divination")
    for tool in divination_tools:
        print(f"- {tool.get('tool_id')}: {tool.get('intent')}")
    
    print("\n=== Recherche par mot-clé 'regex' ===")
    regex_tools = tool_extension.find_tools_by_keyword("regex")
    for tool in regex_tools:
        print(f"- {tool.get('tool_id')}: {tool.get('intent')}")
    
    print("\n=== Recherche combinée ===")
    combined = tool_extension.search_tools(tool_type="divination", keyword="pattern")
    for tool in combined:
        print(f"- {tool.get('tool_id')}: {tool.get('intent')}")


if __name__ == "__main__":
    main()
