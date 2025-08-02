#!/usr/bin/env python3
"""
⛧ Tool Search Extension ⛧
Alma's Mystical Tool Search for MemoryEngine

Extension du MemoryEngine pour indexer et rechercher les outils mystiques épurés.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import sys
import json
from typing import Dict, List, Optional, Any

from ..parsers.luciform_tool_metadata_parser import LuciformToolMetadataParser


class ToolSearchExtension:
    """Extension du MemoryEngine pour la recherche d'outils mystiques épurés."""
    
    def __init__(self, memory_engine):
        """
        Initialise l'extension avec un MemoryEngine existant.
        
        Args:
            memory_engine: Instance du MemoryEngine
        """
        self.memory_engine = memory_engine
        self.parser = LuciformToolMetadataParser()
        self.tools_namespace = "/tools"
        self.indexed = False
        self._tool_cache = {}
    
    def register_tool(self, tool_metadata: Dict[str, Any]) -> bool:
        """
        Enregistre un outil dans le MemoryEngine.
        
        Args:
            tool_metadata: Métadonnées complètes de l'outil
        
        Returns:
            True si succès, False sinon
        """
        try:
            tool_id = tool_metadata.get('tool_id')
            tool_type = tool_metadata.get('type', 'unknown')
            
            if not tool_id:
                print(f"⚠️ Outil sans ID ignoré")
                return False
            
            # Chemin dans le namespace des outils
            tool_path = f"{self.tools_namespace}/{tool_type}/{tool_id}"
            
            # Contenu pour le MemoryEngine
            content = json.dumps(tool_metadata, indent=2, ensure_ascii=False)
            
            # Résumé mystique
            intent = tool_metadata.get('intent', tool_id)
            summary = f"{tool_type.title()}: {intent[:100]}..."
            
            # Keywords pour la recherche
            keywords = [tool_type, tool_id]
            keywords.extend(tool_metadata.get('keywords', []))
            keywords.append(tool_metadata.get('level', 'unknown'))
            
            # Création du nœud mémoire
            self.memory_engine.create_memory(
                path=tool_path,
                content=content,
                summary=summary,
                keywords=keywords,
                strata="cognitive"  # Strate cognitive pour les outils
            )
            
            # Cache local
            self._tool_cache[tool_id] = tool_metadata
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur enregistrement {tool_metadata.get('tool_id', 'unknown')}: {e}")
            return False
    
    def inject_tool_from_luciform(self, luciform_path: str) -> bool:
        """
        Injecte un outil depuis son fichier luciform.
        
        Args:
            luciform_path: Chemin vers le fichier .luciform
        
        Returns:
            True si succès, False sinon
        """
        try:
            # Parse des métadonnées
            metadata = self.parser.extract_tool_metadata(luciform_path)
            
            if not metadata or not metadata.get('tool_id'):
                print(f"⚠️ Métadonnées invalides pour {luciform_path}")
                return False
            
            # Enregistrement dans le MemoryEngine
            success = self.register_tool(metadata)
            
            if success:
                print(f"✅ Outil {metadata['tool_id']} injecté depuis {luciform_path}")
            else:
                print(f"❌ Échec injection {luciform_path}")
            
            return success
            
        except Exception as e:
            print(f"❌ Erreur injection {luciform_path}: {e}")
            return False
    
    def index_all_tools(self, force_reindex: bool = False) -> int:
        """
        Indexe tous les outils luciformes disponibles.
        
        Args:
            force_reindex: Force la réindexation même si déjà fait
        
        Returns:
            Nombre d'outils indexés
        """
        if self.indexed and not force_reindex:
            print("⛧ Index déjà à jour")
            return len(self._tool_cache)
        
        print("⛧ Indexation des outils mystiques...")
        
        # Répertoires à scanner
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        directories = [
            os.path.join(base_dir, 'Alma_toolset'),
            os.path.join(base_dir, 'Tools/Library/documentation/luciforms'),
            os.path.join(base_dir, 'Tools/Search/documentation/luciforms'),
            os.path.join(base_dir, 'Tools/FileSystem/documentation/luciforms'),
            os.path.join(base_dir, 'Tools/Execution/documentation/luciforms'),
        ]
        
        indexed_count = 0
        
        # Scan de chaque répertoire
        for directory in directories:
            if os.path.exists(directory):
                print(f"🔍 Scan de {directory}...")
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.luciform'):
                            file_path = os.path.join(root, file)
                            if self.inject_tool_from_luciform(file_path):
                                indexed_count += 1
        
        self.indexed = True
        print(f"⛧ {indexed_count} outils indexés avec succès !")
        return indexed_count
    
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
                tool = self._get_tool_from_path(path)
                if tool:
                    tools.append(tool)
        
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
                tool = self._get_tool_from_path(path)
                if tool and self._tool_contains_keyword(tool, keyword):
                    tools.append(tool)
        
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
                tool = self._get_tool_from_path(path)
                if tool and tool.get('level') == level:
                    tools.append(tool)
        
        return tools
    
    def find_tools_by_intent(self, intent_query: str) -> List[Dict[str, Any]]:
        """
        Trouve les outils par intention (recherche textuelle dans l'intent).
        
        Args:
            intent_query: Requête textuelle pour l'intention
        
        Returns:
            Liste des outils correspondants
        """
        if not self.indexed:
            self.index_all_tools()
        
        # Recherche dans tous les outils
        all_tools = self._get_all_tools()
        
        # Filtrage par intention
        matching_tools = []
        intent_query_lower = intent_query.lower()
        
        for tool in all_tools:
            intent = tool.get('intent', '')
            if intent_query_lower in intent.lower():
                matching_tools.append(tool)
        
        return matching_tools
    
    def search_tools(self, tool_type: str = None, keyword: str = None, 
                    level: str = None, intent: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Recherche combinée d'outils avec multiple critères.
        
        Args:
            tool_type: Type mystique optionnel
            keyword: Mot-clé optionnel
            level: Niveau optionnel
            intent: Intention optionnelle
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
        
        if intent:
            intent_tools = self.find_tools_by_intent(intent)
            intent_ids = set(tool['tool_id'] for tool in intent_tools if tool.get('tool_id'))
            if results:
                results = results.intersection(intent_ids)
            else:
                results = intent_ids
        
        # Si aucun critère, retourner tous les outils
        if not (tool_type or keyword or level or intent):
            all_tools = self._get_all_tools()
            return all_tools[:limit]
        
        # Récupération des métadonnées complètes
        final_tools = []
        for tool_id in list(results)[:limit]:
            tool = self._tool_cache.get(tool_id)
            if tool:
                final_tools.append(tool)
        
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
        
        # Recherche dans le cache local
        if tool_id in self._tool_cache:
            return self._tool_cache[tool_id]
        
        # Recherche par ID dans le MemoryEngine
        tool_paths = self.memory_engine.find_memories_by_keyword(tool_id)
        
        for path in tool_paths:
            if path.startswith(self.tools_namespace) and path.endswith(f"/{tool_id}"):
                tool = self._get_tool_from_path(path)
                if tool:
                    return tool
        
        return None
    
    def list_all_tool_types(self) -> List[str]:
        """
        Liste tous les types mystiques d'outils disponibles.
        
        Returns:
            Liste des types uniques
        """
        if not self.indexed:
            self.index_all_tools()
        
        types = set()
        for tool in self._tool_cache.values():
            tool_type = tool.get('type')
            if tool_type:
                types.add(tool_type)
        
        return sorted(list(types))
    
    def list_tool_types_with_descriptions(self) -> Dict[str, Dict[str, Any]]:
        """
        Liste tous les types avec leurs descriptions et statistiques.
        
        Returns:
            Dict avec types et leurs métadonnées
        """
        if not self.indexed:
            self.index_all_tools()
        
        type_stats = {}
        
        for tool in self._tool_cache.values():
            tool_type = tool.get('type', 'unknown')
            
            if tool_type not in type_stats:
                type_stats[tool_type] = {
                    'count': 0,
                    'levels': set(),
                    'examples': [],
                    'description': tool.get('symbolic_layer', '')
                }
            
            type_stats[tool_type]['count'] += 1
            type_stats[tool_type]['levels'].add(tool.get('level', 'unknown'))
            
            # Garder quelques exemples
            if len(type_stats[tool_type]['examples']) < 3:
                type_stats[tool_type]['examples'].append({
                    'tool_id': tool.get('tool_id'),
                    'intent': tool.get('intent', '')
                })
        
        # Convertir les sets en listes pour la sérialisation
        for tool_type in type_stats:
            type_stats[tool_type]['levels'] = list(type_stats[tool_type]['levels'])
        
        return type_stats
    
    def unregister_tool(self, tool_id: str) -> bool:
        """
        Supprime un outil du MemoryEngine.
        
        Args:
            tool_id: Identifiant de l'outil à supprimer
        
        Returns:
            True si succès, False sinon
        """
        try:
            # Recherche du chemin de l'outil
            tool_paths = self.memory_engine.find_memories_by_keyword(tool_id)
            
            for path in tool_paths:
                if path.startswith(self.tools_namespace) and path.endswith(f"/{tool_id}"):
                    # Suppression du nœud mémoire
                    success = self.memory_engine.forget_memory(path)
                    
                    if success:
                        # Suppression du cache local
                        self._tool_cache.pop(tool_id, None)
                        print(f"✅ Outil {tool_id} supprimé")
                        return True
            
            print(f"⚠️ Outil {tool_id} non trouvé")
            return False
            
        except Exception as e:
            print(f"❌ Erreur suppression {tool_id}: {e}")
            return False
    
    def format_tool_types_help(self) -> str:
        """
        Formate l'aide pour les types d'outils.
        
        Returns:
            Texte d'aide formaté
        """
        type_stats = self.list_tool_types_with_descriptions()
        
        help_text = "⛧ Types d'outils mystiques disponibles :\n\n"
        
        for tool_type, stats in type_stats.items():
            help_text += f"🜄 {tool_type.title()}\n"
            help_text += f"   Nombre d'outils : {stats['count']}\n"
            help_text += f"   Niveaux : {', '.join(stats['levels'])}\n"
            
            if stats['description']:
                help_text += f"   Description : {stats['description']}\n"
            
            if stats['examples']:
                help_text += "   Exemples :\n"
                for example in stats['examples']:
                    help_text += f"     - {example['tool_id']}: {example['intent']}\n"
            
            help_text += "\n"
        
        return help_text
    
    def get_tools_statistics(self) -> Dict[str, Any]:
        """
        Obtient des statistiques sur les outils indexés.
        
        Returns:
            Dict avec statistiques
        """
        if not self.indexed:
            self.index_all_tools()
        
        stats = {
            'total_tools': len(self._tool_cache),
            'tool_types': {},
            'levels': {},
            'recent_additions': []
        }
        
        # Statistiques par type
        for tool in self._tool_cache.values():
            tool_type = tool.get('type', 'unknown')
            level = tool.get('level', 'unknown')
            
            stats['tool_types'][tool_type] = stats['tool_types'].get(tool_type, 0) + 1
            stats['levels'][level] = stats['levels'].get(level, 0) + 1
        
        return stats
    
    def _get_tool_from_path(self, path: str) -> Optional[Dict[str, Any]]:
        """Récupère un outil depuis son chemin dans le MemoryEngine."""
        try:
            node = self.memory_engine.get_memory_node(path)
            if node and node.content:
                return json.loads(node.content)
        except:
            pass
        return None
    
    def _get_all_tools(self) -> List[Dict[str, Any]]:
        """Récupère tous les outils du cache local."""
        return list(self._tool_cache.values())
    
    def _tool_contains_keyword(self, tool: Dict[str, Any], keyword: str) -> bool:
        """Vérifie si un outil contient un mot-clé."""
        keyword_lower = keyword.lower()
        
        # Recherche dans différents champs
        fields_to_search = ['tool_id', 'intent', 'symbolic_layer', 'usage_context']
        
        for field in fields_to_search:
            value = tool.get(field, '')
            if keyword_lower in value.lower():
                return True
        
        # Recherche dans les mots-clés
        keywords = tool.get('keywords', [])
        for kw in keywords:
            if keyword_lower in kw.lower():
                return True
        
        return False 