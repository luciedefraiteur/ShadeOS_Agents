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

# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from Core.implementation.luciform_tool_metadata_parser import LuciformToolMetadataParser


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
            
            if metadata and metadata.get('tool_id'):
                # Validation
                if self.parser.validate_metadata(metadata):
                    return self.register_tool(metadata)
                else:
                    print(f"⚠️ Métadonnées invalides pour {luciform_path}")
            else:
                print(f"⚠️ Impossible d'extraire métadonnées de {luciform_path}")
            
            return False
            
        except Exception as e:
            print(f"❌ Erreur injection {luciform_path}: {e}")
            return False
    
    def index_all_tools(self, force_reindex: bool = False) -> int:
        """
        Indexe automatiquement tous les outils trouvés.
        
        Args:
            force_reindex: Force la réindexation même si déjà fait
        
        Returns:
            Nombre d'outils indexés
        """
        if self.indexed and not force_reindex:
            print("⛧ Outils déjà indexés (utilisez force_reindex=True pour forcer)")
            return len(self._tool_cache)
        
        print("⛧ Indexation des outils mystiques épurés dans le MemoryEngine...")
        
        # Extraction des métadonnées
        all_metadata = self.parser.scan_luciform_directories()
        
        # Compteurs
        success_count = 0
        error_count = 0
        
        # Injection de chaque outil
        for metadata in all_metadata:
            if metadata.get('tool_id'):
                if self.register_tool(metadata):
                    success_count += 1
                else:
                    error_count += 1
        
        self.indexed = True
        
        print(f"⛧ Indexation terminée: {success_count} succès, {error_count} erreurs")
        return success_count
    
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
        
        try:
            # Recherche par mot-clé dans le MemoryEngine
            tool_paths = self.memory_engine.find_memories_by_keyword(tool_type)
            
            # Filtrage pour ne garder que les outils du bon type
            tools = []
            for path in tool_paths:
                if path.startswith(f"{self.tools_namespace}/{tool_type}/"):
                    tool = self._get_tool_from_path(path)
                    if tool:
                        tools.append(tool)
            
            return tools
            
        except Exception as e:
            print(f"❌ Erreur recherche par type {tool_type}: {e}")
            return []
    
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
        
        try:
            # Recherche par mot-clé
            tool_paths = self.memory_engine.find_memories_by_keyword(keyword)
            
            # Filtrage pour ne garder que les outils
            tools = []
            for path in tool_paths:
                if path.startswith(self.tools_namespace):
                    tool = self._get_tool_from_path(path)
                    if tool:
                        # Vérification que le keyword est vraiment présent
                        if self._tool_contains_keyword(tool, keyword):
                            tools.append(tool)
            
            return tools
            
        except Exception as e:
            print(f"❌ Erreur recherche par keyword {keyword}: {e}")
            return []
    
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
        
        try:
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
            
        except Exception as e:
            print(f"❌ Erreur recherche par niveau {level}: {e}")
            return []
    
    def find_tools_by_intent(self, intent_query: str) -> List[Dict[str, Any]]:
        """
        Trouve les outils par intention/description.
        
        Args:
            intent_query: Requête d'intention (ex: "sauvegarder fichier")
        
        Returns:
            Liste des outils correspondants avec score de pertinence
        """
        if not self.indexed:
            self.index_all_tools()
        
        try:
            # Recherche floue dans les intentions
            all_tools = self._get_all_tools()
            matching_tools = []
            
            query_words = intent_query.lower().split()
            
            for tool in all_tools:
                intent = tool.get('intent', '').lower()
                usage_context = tool.get('usage_context', '').lower()
                
                # Score basé sur les mots trouvés
                score = 0
                for word in query_words:
                    if word in intent:
                        score += 2
                    if word in usage_context:
                        score += 1
                    if word in [kw.lower() for kw in tool.get('keywords', [])]:
                        score += 1
                
                if score > 0:
                    tool_copy = tool.copy()
                    tool_copy['_relevance_score'] = score
                    matching_tools.append(tool_copy)
            
            # Tri par score de pertinence
            matching_tools.sort(key=lambda x: x['_relevance_score'], reverse=True)
            
            return matching_tools
            
        except Exception as e:
            print(f"❌ Erreur recherche par intention '{intent_query}': {e}")
            return []
    
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
        
        try:
            # Collecte des résultats selon les critères
            result_sets = []
            
            if tool_type:
                type_tools = self.find_tools_by_type(tool_type)
                result_sets.append(set(tool['tool_id'] for tool in type_tools))
            
            if keyword:
                keyword_tools = self.find_tools_by_keyword(keyword)
                result_sets.append(set(tool['tool_id'] for tool in keyword_tools))
            
            if level:
                level_tools = self.find_tools_by_level(level)
                result_sets.append(set(tool['tool_id'] for tool in level_tools))
            
            if intent:
                intent_tools = self.find_tools_by_intent(intent)
                result_sets.append(set(tool['tool_id'] for tool in intent_tools))
            
            # Intersection des résultats
            if result_sets:
                final_ids = result_sets[0]
                for result_set in result_sets[1:]:
                    final_ids = final_ids.intersection(result_set)
            else:
                # Aucun critère : tous les outils
                all_tools = self._get_all_tools()
                final_ids = set(tool['tool_id'] for tool in all_tools)
            
            # Récupération des métadonnées complètes
            final_tools = []
            for tool_id in list(final_ids)[:limit]:
                tool = self.get_tool_info(tool_id)
                if tool:
                    final_tools.append(tool)
            
            return final_tools
            
        except Exception as e:
            print(f"❌ Erreur recherche combinée: {e}")
            return []
    
    def get_tool_info(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations complètes d'un outil.
        
        Args:
            tool_id: Identifiant de l'outil
        
        Returns:
            Métadonnées de l'outil ou None
        """
        # Cache local d'abord
        if tool_id in self._tool_cache:
            return self._tool_cache[tool_id]
        
        if not self.indexed:
            self.index_all_tools()
        
        try:
            # Recherche par ID
            tool_paths = self.memory_engine.find_memories_by_keyword(tool_id)
            
            for path in tool_paths:
                if path.startswith(self.tools_namespace) and path.endswith(f"/{tool_id}"):
                    tool = self._get_tool_from_path(path)
                    if tool:
                        self._tool_cache[tool_id] = tool
                        return tool
            
            return None
            
        except Exception as e:
            print(f"❌ Erreur récupération info {tool_id}: {e}")
            return None
    
    def list_all_tool_types(self) -> List[str]:
        """
        Liste tous les types mystiques d'outils disponibles.

        Returns:
            Liste des types uniques
        """
        if not self.indexed:
            self.index_all_tools()

        all_tools = self._get_all_tools()
        types = set(tool.get('type') for tool in all_tools if tool.get('type'))
        return sorted(list(types))

    def list_tool_types_with_descriptions(self) -> Dict[str, Dict[str, Any]]:
        """
        Liste tous les types mystiques avec descriptions et exemples.

        Returns:
            Dict avec type -> {description, count, examples}
        """
        if not self.indexed:
            self.index_all_tools()

        all_tools = self._get_all_tools()
        types_info = {}

        # Descriptions mystiques des types
        type_descriptions = {
            'divination': 'Révéler les patterns cachés et scruter les mystères du code',
            'protection': 'Garder et sauvegarder les grimoires sacrés contre la corruption',
            'transmutation': 'Transformer le néant en réalité par la magie des templates',
            'scrying': 'Comparer et scruter les différences entre les visions',
            'augury': 'Lire les présages et métriques cachés dans les fichiers',
            'inscription': 'Graver de nouveaux grimoires dans la réalité',
            'revelation': 'Révéler les secrets contenus dans les fichiers existants',
            'metamorphosis': 'Transformer et métamorphoser le contenu existant',
            'filesystem': 'Manipuler la structure mystique des répertoires',
            'modification': 'Modifier et éditer le contenu des grimoires',
            'writing': 'Écrire et créer du contenu dans les fichiers',
            'listing': 'Énumérer et lister les éléments mystiques'
        }

        # Collecte des informations par type
        for tool in all_tools:
            tool_type = tool.get('type')
            if not tool_type:
                continue

            if tool_type not in types_info:
                types_info[tool_type] = {
                    'description': type_descriptions.get(tool_type, 'Type mystique sans description'),
                    'count': 0,
                    'examples': []
                }

            types_info[tool_type]['count'] += 1

            # Ajouter des exemples (max 3 par type)
            if len(types_info[tool_type]['examples']) < 3:
                types_info[tool_type]['examples'].append({
                    'tool_id': tool.get('tool_id'),
                    'intent': tool.get('intent', '')[:60] + '...' if len(tool.get('intent', '')) > 60 else tool.get('intent', ''),
                    'level': tool.get('level')
                })

        return types_info

    def unregister_tool(self, tool_id: str) -> bool:
        """
        Désenregistre un outil du MemoryEngine.

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
                    # Suppression du MemoryEngine
                    success = self.memory_engine.forget_memory(path)

                    if success:
                        # Suppression du cache local
                        if tool_id in self._tool_cache:
                            del self._tool_cache[tool_id]
                        print(f"✅ Outil {tool_id} désenregistré")
                        return True
                    else:
                        print(f"❌ Échec suppression {tool_id} du MemoryEngine")
                        return False

            print(f"⚠️ Outil {tool_id} non trouvé")
            return False

        except Exception as e:
            print(f"❌ Erreur désenregistrement {tool_id}: {e}")
            return False

    def format_tool_types_help(self) -> str:
        """
        Formate l'aide sur les types d'outils pour affichage.

        Returns:
            String formatée avec tous les types et descriptions
        """
        types_info = self.list_tool_types_with_descriptions()

        output = []
        output.append("⛧ Types Mystiques d'Outils Disponibles ⛧")
        output.append("═" * 60)
        output.append("")

        for tool_type in sorted(types_info.keys()):
            info = types_info[tool_type]
            output.append(f"🎭 **{tool_type.upper()}** ({info['count']} outils)")
            output.append(f"   {info['description']}")
            output.append("")
            output.append("   Exemples :")

            for example in info['examples']:
                level_icon = {"fondamental": "🟢", "intermédiaire": "🟡", "avancé": "🔴"}.get(example['level'], "⚪")
                output.append(f"   {level_icon} {example['tool_id']}: {example['intent']}")

            output.append("")

        output.append("═" * 60)
        output.append("💡 Usage: find_tools_by_type('nom_du_type')")
        output.append("💡 Exemple: find_tools_by_type('divination')")

        return "\n".join(output)

    def get_tools_statistics(self) -> Dict[str, Any]:
        """
        Formate l'aide sur les types d'outils pour affichage.

        Returns:
            String formatée avec tous les types et descriptions
        """
        types_info = self.list_tool_types_with_descriptions()

        output = []
        output.append("⛧ Types Mystiques d'Outils Disponibles ⛧")
        output.append("═" * 60)
        output.append("")

        for tool_type in sorted(types_info.keys()):
            info = types_info[tool_type]
            output.append(f"🎭 **{tool_type.upper()}** ({info['count']} outils)")
            output.append(f"   {info['description']}")
            output.append("")
            output.append("   Exemples :")

            for example in info['examples']:
                level_icon = {"fondamental": "🟢", "intermédiaire": "🟡", "avancé": "🔴"}.get(example['level'], "⚪")
                output.append(f"   {level_icon} {example['tool_id']}: {example['intent']}")

            output.append("")

        output.append("═" * 60)
        output.append("💡 Usage: find_tools_by_type('nom_du_type')")
        output.append("💡 Exemple: find_tools_by_type('divination')")

        return "\n".join(output)
    
    def get_tools_statistics(self) -> Dict[str, Any]:
        """
        Retourne des statistiques sur les outils indexés.
        
        Returns:
            Dict avec statistiques
        """
        if not self.indexed:
            self.index_all_tools()
        
        all_tools = self._get_all_tools()
        return self.parser.get_statistics(all_tools)
    
    def _get_tool_from_path(self, path: str) -> Optional[Dict[str, Any]]:
        """Récupère un outil depuis son chemin dans le MemoryEngine."""
        try:
            node = self.memory_engine.get_memory_node(path)
            if node and node.content:
                return json.loads(node.content)
        except Exception as e:
            print(f"⚠️ Erreur lecture outil {path}: {e}")
        return None
    
    def _get_all_tools(self) -> List[Dict[str, Any]]:
        """Récupère tous les outils indexés."""
        return list(self._tool_cache.values())
    
    def _tool_contains_keyword(self, tool: Dict[str, Any], keyword: str) -> bool:
        """Vérifie si un outil contient un mot-clé."""
        keyword_lower = keyword.lower()
        
        # Vérification dans les champs textuels
        text_fields = ['tool_id', 'type', 'intent', 'level', 'signature', 'symbolic_layer', 'usage_context']
        for field in text_fields:
            value = tool.get(field, '')
            if isinstance(value, str) and keyword_lower in value.lower():
                return True
        
        # Vérification dans les keywords
        keywords = tool.get('keywords', [])
        for kw in keywords:
            if keyword_lower in kw.lower():
                return True
        
        return False
