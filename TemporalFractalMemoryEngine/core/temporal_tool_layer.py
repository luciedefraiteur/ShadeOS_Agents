#!/usr/bin/env python3
"""
⛧ MemoryEngine V2 - ToolTemporalLayer ⛧

Migration de ToolMemoryExtension vers l'architecture temporelle universelle.
Compatibilité totale avec l'existant + dimension temporelle.
"""

import os
import sys
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

from Core.Parsers.luciform_parser import parse_luciform
from .temporal_components import ToolTemporalLayer as BaseToolTemporalLayer
from .temporal_memory_node import TemporalMemoryNode


class ToolTemporalLayer(BaseToolTemporalLayer):
    """Migration de ToolMemoryExtension vers l'architecture temporelle universelle"""
    
    def __init__(self, memory_engine):
        # Initialisation de la base temporelle
        super().__init__(memory_engine)
        
        # Propriétés héritées de ToolMemoryExtension
        self.engine = memory_engine  # Alias pour compatibilité
        self.tools_namespace = "/tools"
        self.indexed = False
        
        # Cache des outils indexés
        self.tool_cache = {}
        self.tool_metadata_cache = {}
        
        # Évolution temporelle de l'initialisation
        self.temporal_dimension.evolve("tool_temporal_layer_initialized", {
            "tools_namespace": self.tools_namespace,
            "memory_engine_available": memory_engine is not None
        })
    
    def index_tool(self, tool_data: Dict[str, Any]) -> str:
        """Indexe un outil avec tracking temporel"""
        try:
            tool_id = tool_data.get('tool_id', tool_data.get('id', 'unknown'))
            tool_type = tool_data.get('type', 'unknown')
            
            # Chemin dans le namespace des outils
            tool_path = f"{self.tools_namespace}/{tool_type}/{tool_id}"
            
            # Contenu pour le MemoryEngine
            content = json.dumps(tool_data, indent=2, ensure_ascii=False)
            summary = f"{tool_type.title()} tool: {tool_data.get('intent', tool_id)}"
            keywords = [tool_type, tool_id] + tool_data.get('keywords', [])
            
            # Création du nœud mémoire temporel
            temporal_node = TemporalMemoryNode(
                content=content,
                metadata={
                    "tool_id": tool_id,
                    "tool_type": tool_type,
                    "summary": summary,
                    "original_data": tool_data
                },
                strata="cognitive",  # Strate cognitive pour les outils
                keywords=keywords
            )
            
            # Enregistrement dans le registre temporel
            self.tool_registry.add_entity(tool_id, temporal_node)
            
            # Mise en cache
            self.tool_cache[tool_id] = temporal_node
            self.tool_metadata_cache[tool_id] = tool_data
            
            # Évolution temporelle de l'indexation
            self.temporal_dimension.evolve("tool_indexed", {
                "tool_id": tool_id,
                "tool_type": tool_type,
                "tool_path": tool_path,
                "keywords_count": len(keywords)
            })
            
            # Apprentissage temporel
            self.learn_from_interaction({
                "type": "tool_indexation",
                "tool_id": tool_id,
                "tool_type": tool_type,
                "keywords_count": len(keywords)
            })
            
            return tool_id
            
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("tool_indexation_error", {
                "tool_id": tool_data.get('tool_id', 'unknown'),
                "error": str(e)
            })
            return None
    
    def extract_tool_metadata(self, luciform_path: str) -> Optional[Dict[str, Any]]:
        """Extrait les métadonnées d'un fichier luciform avec tracking temporel"""
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
                attributes = content['attributes']
                metadata['tool_id'] = attributes.get('id', attributes.get('name', 'unknown'))
                metadata['type'] = attributes.get('type', 'unknown')
                metadata['level'] = attributes.get('level', 'basic')
            
            # Intent et signature
            if 'pacte' in content:
                self._extract_pacte_info(content['pacte'], metadata)
            
            if 'invocation' in content:
                self._extract_invocation_info(content['invocation'], metadata)
            
            if 'essence' in content:
                self._extract_essence_info(content['essence'], metadata)
            
            # Évolution temporelle de l'extraction
            self.temporal_dimension.evolve("tool_metadata_extracted", {
                "file_path": luciform_path,
                "tool_id": metadata.get('tool_id'),
                "tool_type": metadata.get('type'),
                "level": metadata.get('level')
            })
            
            return metadata
            
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("tool_metadata_extraction_error", {
                "file_path": luciform_path,
                "error": str(e)
            })
            return None
    
    def _extract_pacte_info(self, pacte_node: Dict, metadata: Dict):
        """Extraction des informations du pacte avec tracking temporel"""
        if 'intent' in pacte_node:
            metadata['intent'] = self._extract_text_content(pacte_node['intent'])
        if 'keywords' in pacte_node:
            metadata['keywords'] = self._extract_keywords_list(pacte_node['keywords'])
    
    def _extract_invocation_info(self, invocation_node: Dict, metadata: Dict):
        """Extraction des informations d'invocation avec tracking temporel"""
        if 'signature' in invocation_node:
            metadata['signature'] = self._extract_text_content(invocation_node['signature'])
    
    def _extract_essence_info(self, essence_node: Dict, metadata: Dict):
        """Extraction des informations d'essence avec tracking temporel"""
        if 'symbolic_layer' in essence_node:
            metadata['symbolic_layer'] = self._extract_text_content(essence_node['symbolic_layer'])
        if 'usage_context' in essence_node:
            metadata['usage_context'] = self._extract_text_content(essence_node['usage_context'])
    
    def _extract_text_content(self, node: Dict) -> Optional[str]:
        """Extraction du contenu textuel"""
        if isinstance(node, dict) and 'text' in node:
            return node['text']
        elif isinstance(node, str):
            return node
        return None
    
    def _extract_keywords_list(self, node: Dict) -> List[str]:
        """Extraction de la liste de mots-clés"""
        keywords = []
        if isinstance(node, dict) and 'keywords' in node:
            keywords_node = node['keywords']
            if isinstance(keywords_node, list):
                keywords = keywords_node
            elif isinstance(keywords_node, dict) and 'text' in keywords_node:
                keywords = [keywords_node['text']]
        return keywords
    
    def scan_luciform_directories(self) -> List[Dict[str, Any]]:
        """Scan des répertoires luciform avec tracking temporel"""
        try:
            tools_found = []
            
            # Répertoires à scanner
            scan_dirs = [
                "Alma_toolset",
                "Core/Templates",
                "MemoryEngine/core",
                "Daemons"
            ]
            
            for scan_dir in scan_dirs:
                if os.path.exists(scan_dir):
                    for root, dirs, files in os.walk(scan_dir):
                        for file in files:
                            if file.endswith('.luciform'):
                                file_path = os.path.join(root, file)
                                metadata = self.extract_tool_metadata(file_path)
                                if metadata:
                                    tools_found.append(metadata)
            
            # Évolution temporelle du scan
            self.temporal_dimension.evolve("luciform_directories_scanned", {
                "scan_dirs": scan_dirs,
                "tools_found_count": len(tools_found)
            })
            
            return tools_found
            
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("luciform_scan_error", {
                "error": str(e)
            })
            return []
    
    def index_all_tools(self, force_reindex: bool = False):
        """Indexe tous les outils avec tracking temporel"""
        try:
            if self.indexed and not force_reindex:
                return
            
            # Scan des outils
            tools_metadata = self.scan_luciform_directories()
            
            # Indexation de chaque outil
            indexed_count = 0
            for metadata in tools_metadata:
                if self.index_tool(metadata):
                    indexed_count += 1
            
            self.indexed = True
            
            # Évolution temporelle de l'indexation complète
            self.temporal_dimension.evolve("all_tools_indexed", {
                "tools_metadata_count": len(tools_metadata),
                "indexed_count": indexed_count,
                "force_reindex": force_reindex
            })
            
            # Apprentissage temporel
            self.learn_from_interaction({
                "type": "bulk_tool_indexation",
                "tools_metadata_count": len(tools_metadata),
                "indexed_count": indexed_count
            })
            
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("bulk_tool_indexation_error", {
                "error": str(e)
            })
    
    def find_tools_by_type(self, tool_type: str) -> List[Dict[str, Any]]:
        """Recherche d'outils par type avec tracking temporel"""
        try:
            tools = []
            
            for tool_id, temporal_node in self.tool_registry.entities.items():
                if temporal_node.metadata.get('tool_type') == tool_type:
                    tools.append({
                        'tool_id': tool_id,
                        'metadata': temporal_node.metadata,
                        'content': temporal_node.content,
                        'consciousness_level': temporal_node.get_consciousness_level()
                    })
            
            # Évolution temporelle de la recherche
            self.temporal_dimension.evolve("tools_found_by_type", {
                "tool_type": tool_type,
                "tools_found_count": len(tools)
            })
            
            return tools
            
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("tool_type_search_error", {
                "tool_type": tool_type,
                "error": str(e)
            })
            return []
    
    def find_tools_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Recherche d'outils par mot-clé avec tracking temporel"""
        try:
            tools = []
            
            for tool_id, temporal_node in self.tool_registry.entities.items():
                if keyword.lower() in [kw.lower() for kw in temporal_node.keywords]:
                    tools.append({
                        'tool_id': tool_id,
                        'metadata': temporal_node.metadata,
                        'content': temporal_node.content,
                        'consciousness_level': temporal_node.get_consciousness_level()
                    })
            
            # Évolution temporelle de la recherche
            self.temporal_dimension.evolve("tools_found_by_keyword", {
                "keyword": keyword,
                "tools_found_count": len(tools)
            })
            
            return tools
            
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("tool_keyword_search_error", {
                "keyword": keyword,
                "error": str(e)
            })
            return []
    
    def find_tools_by_level(self, level: str) -> List[Dict[str, Any]]:
        """Recherche d'outils par niveau avec tracking temporel"""
        try:
            tools = []
            
            for tool_id, temporal_node in self.tool_registry.entities.items():
                if temporal_node.metadata.get('level') == level:
                    tools.append({
                        'tool_id': tool_id,
                        'metadata': temporal_node.metadata,
                        'content': temporal_node.content,
                        'consciousness_level': temporal_node.get_consciousness_level()
                    })
            
            # Évolution temporelle de la recherche
            self.temporal_dimension.evolve("tools_found_by_level", {
                "level": level,
                "tools_found_count": len(tools)
            })
            
            return tools
            
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("tool_level_search_error", {
                "level": level,
                "error": str(e)
            })
            return []
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques des outils avec métadonnées temporelles"""
        try:
            stats = {
                "total_tools": len(self.tool_registry.entities),
                "tool_types": {},
                "tool_levels": {},
                "consciousness_levels": {
                    "high": 0,
                    "medium": 0,
                    "low": 0
                },
                "temporal_metadata": {
                    "consciousness_level": self.get_consciousness_level(),
                    "evolution_count": len(self.temporal_dimension.evolution_history)
                }
            }
            
            # Calcul des statistiques
            for tool_id, temporal_node in self.tool_registry.entities.items():
                tool_type = temporal_node.metadata.get('tool_type', 'unknown')
                tool_level = temporal_node.metadata.get('level', 'unknown')
                consciousness_level = temporal_node.get_consciousness_level()
                
                # Types d'outils
                stats["tool_types"][tool_type] = stats["tool_types"].get(tool_type, 0) + 1
                
                # Niveaux d'outils
                stats["tool_levels"][tool_level] = stats["tool_levels"].get(tool_level, 0) + 1
                
                # Niveaux de conscience
                if consciousness_level >= 0.8:
                    stats["consciousness_levels"]["high"] += 1
                elif consciousness_level >= 0.5:
                    stats["consciousness_levels"]["medium"] += 1
                else:
                    stats["consciousness_levels"]["low"] += 1
            
            return stats
            
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("tool_statistics_error", {
                "error": str(e)
            })
            return {}
    
    def search_tools(self, name_filter: str = None, type_filter: str = None, 
                    level_filter: str = None, keyword_filter: str = None) -> List[Dict[str, Any]]:
        """Recherche avancée d'outils avec tracking temporel"""
        try:
            results = []
            
            for tool_id, temporal_node in self.tool_registry.entities.items():
                metadata = temporal_node.metadata
                
                # Application des filtres
                if name_filter and name_filter.lower() not in tool_id.lower():
                    continue
                if type_filter and metadata.get('tool_type') != type_filter:
                    continue
                if level_filter and metadata.get('level') != level_filter:
                    continue
                if keyword_filter and keyword_filter.lower() not in [kw.lower() for kw in temporal_node.keywords]:
                    continue
                
                results.append({
                    'tool_id': tool_id,
                    'metadata': metadata,
                    'content': temporal_node.content,
                    'consciousness_level': temporal_node.get_consciousness_level(),
                    'keywords': temporal_node.keywords
                })
            
            # Évolution temporelle de la recherche
            self.temporal_dimension.evolve("tools_advanced_search", {
                "name_filter": name_filter,
                "type_filter": type_filter,
                "level_filter": level_filter,
                "keyword_filter": keyword_filter,
                "results_count": len(results)
            })
            
            return results
            
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("tools_advanced_search_error", {
                "error": str(e)
            })
            return []
    
    def get_tool_info(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'un outil avec tracking temporel"""
        try:
            if tool_id in self.tool_registry.entities:
                temporal_node = self.tool_registry.entities[tool_id]
                
                # Accès au nœud pour tracking
                temporal_node.access_node()
                
                tool_info = {
                    'tool_id': tool_id,
                    'metadata': temporal_node.metadata,
                    'content': temporal_node.content,
                    'consciousness_level': temporal_node.get_consciousness_level(),
                    'keywords': temporal_node.keywords,
                    'evolution_history': temporal_node.get_evolution_history()
                }
                
                # Évolution temporelle de l'accès
                self.temporal_dimension.evolve("tool_info_accessed", {
                    "tool_id": tool_id,
                    "consciousness_level": temporal_node.get_consciousness_level()
                })
                
                return tool_info
            
            return None
            
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("tool_info_access_error", {
                "tool_id": tool_id,
                "error": str(e)
            })
            return None
    
    def list_all_tool_types(self) -> List[str]:
        """Liste tous les types d'outils avec tracking temporel"""
        try:
            tool_types = set()
            
            for temporal_node in self.tool_registry.entities.values():
                tool_type = temporal_node.metadata.get('tool_type')
                if tool_type:
                    tool_types.add(tool_type)
            
            tool_types_list = list(tool_types)
            
            # Évolution temporelle de la liste
            self.temporal_dimension.evolve("tool_types_listed", {
                "tool_types_count": len(tool_types_list)
            })
            
            return tool_types_list
            
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("tool_types_list_error", {
                "error": str(e)
            })
            return []
    
    def get_entity_specific_data(self) -> Dict[str, Any]:
        """Données spécifiques à la couche outil temporelle"""
        return {
            "tools_namespace": self.tools_namespace,
            "indexed": self.indexed,
            "tool_cache_size": len(self.tool_cache),
            "tool_metadata_cache_size": len(self.tool_metadata_cache),
            "tool_registry_size": len(self.tool_registry.entities)
        } 