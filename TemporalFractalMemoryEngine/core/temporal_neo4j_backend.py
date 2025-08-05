#!/usr/bin/env python3
"""
⛧ MemoryEngine V2 - TemporalNeo4jBackend ⛧

Migration de Neo4jBackend vers l'architecture temporelle universelle.
Compatibilité totale avec l'existant + dimension temporelle.
"""

import os
import uuid
from typing import List, Dict, Optional, Any
from dataclasses import asdict

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("⛧ Warning: neo4j package not installed. Install with: pip install neo4j")

from .temporal_base import TemporalRegistry, register_temporal_entity
from .temporal_memory_node import TemporalMemoryNode


class TemporalNeo4jBackend(TemporalRegistry):
    """Migration de Neo4jBackend vers l'architecture temporelle universelle"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        # Initialisation de la base temporelle
        super().__init__("neo4j_temporal", auto_organize=True)
        
        if not NEO4J_AVAILABLE:
            raise ImportError("Neo4j driver not available. Install with: pip install neo4j")
        
        # Propriétés héritées de Neo4jBackend
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.uri = uri
        self.user = user
        
        # Initialisation des contraintes
        self._initialize_constraints()
        
        # Évolution temporelle de l'initialisation
        self.temporal_dimension.evolve("temporal_neo4j_backend_initialized", {
            "uri": uri,
            "user": user,
            "neo4j_available": NEO4J_AVAILABLE
        })
    
    def close(self):
        """Ferme la connexion Neo4j avec tracking temporel"""
        if self.driver:
            self.driver.close()
            
            # Évolution temporelle de la fermeture
            self.temporal_dimension.evolve("neo4j_connection_closed", {
                "connection_duration": self.temporal_dimension.modified_at - self.temporal_dimension.created_at
            })
    
    def _initialize_constraints(self):
        """Initialise les contraintes Neo4j avec tracking temporel"""
        try:
            with self.driver.session() as session:
                # Contrainte unique sur les chemins de nœuds
                session.run("""
                    CREATE CONSTRAINT memory_node_path IF NOT EXISTS
                    FOR (n:MemoryNode) REQUIRE n.path IS UNIQUE
                """)
                
                # Index pour requêtes efficaces
                session.run("CREATE INDEX memory_keywords IF NOT EXISTS FOR (n:MemoryNode) ON (n.keywords)")
                session.run("CREATE INDEX memory_strata IF NOT EXISTS FOR (n:MemoryNode) ON (n.strata)")
                session.run("CREATE INDEX memory_summary IF NOT EXISTS FOR (n:MemoryNode) ON (n.summary)")
                
                # Index temporels
                session.run("CREATE INDEX memory_temporal_created IF NOT EXISTS FOR (n:MemoryNode) ON (n.temporal_created_at)")
                session.run("CREATE INDEX memory_temporal_modified IF NOT EXISTS FOR (n:MemoryNode) ON (n.temporal_modified_at)")
                session.run("CREATE INDEX memory_consciousness_level IF NOT EXISTS FOR (n:MemoryNode) ON (n.consciousness_level)")
            
            # Évolution temporelle de l'initialisation des contraintes
            self.temporal_dimension.evolve("neo4j_constraints_initialized", {
                "constraints_created": True,
                "indexes_created": True
            })
            
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("neo4j_constraints_error", {
                "error": str(e)
            })
    
    def write(self, path: str, content: str, summary: str, keywords: List[str], 
              links: List[str] = None, strata: str = "somatic", 
              transcendence_links: List[str] = None, immanence_links: List[str] = None):
        """Crée ou met à jour un nœud mémoire avec tracking temporel"""
        try:
            with self.driver.session() as session:
                # ID du nœud
                node_id = str(uuid.uuid4())
                
                # Création du nœud mémoire principal avec métadonnées temporelles
                session.run("""
                    MERGE (n:MemoryNode {path: $path})
                    SET n.id = $node_id,
                        n.descriptor = $content,
                        n.summary = $summary,
                        n.keywords = $keywords,
                        n.strata = $strata,
                        n.temporal_created_at = datetime(),
                        n.temporal_modified_at = datetime(),
                        n.consciousness_level = $consciousness_level,
                        n.temporal_entity_id = $temporal_entity_id
                """, path=path, node_id=node_id, content=content, summary=summary,
                    keywords=keywords, strata=strata, consciousness_level=0.0,
                    temporal_entity_id=self.temporal_dimension.entity_id)

                # Ajout du label spécifique à la strate
                if strata == "somatic":
                    session.run("MATCH (n:MemoryNode {path: $path}) SET n:Somatic", path=path)
                elif strata == "cognitive":
                    session.run("MATCH (n:MemoryNode {path: $path}) SET n:Cognitive", path=path)
                elif strata == "metaphysical":
                    session.run("MATCH (n:MemoryNode {path: $path}) SET n:Metaphysical", path=path)
                
                # Création de la relation parent-enfant si applicable
                parent_path = self._get_parent_path(path)
                if parent_path:
                    session.run("""
                        MATCH (parent:MemoryNode {path: $parent_path})
                        MATCH (child:MemoryNode {path: $child_path})
                        MERGE (parent)-[:HAS_CHILD]->(child)
                    """, parent_path=parent_path, child_path=path)
                
                # Création des liens de transcendance
                if transcendence_links:
                    for link_path in transcendence_links:
                        session.run("""
                            MATCH (source:MemoryNode {path: $source_path})
                            MATCH (target:MemoryNode {path: $target_path})
                            MERGE (source)-[:TRANSCENDS_TO]->(target)
                        """, source_path=path, target_path=link_path)
                
                # Création des liens d'immanence
                if immanence_links:
                    for link_path in immanence_links:
                        session.run("""
                            MATCH (source:MemoryNode {path: $source_path})
                            MATCH (target:MemoryNode {path: $target_path})
                            MERGE (source)-[:IMMANENT_TO]->(target)
                        """, source_path=path, target_path=link_path)
                
                # Création des liens associatifs
                if links:
                    for link_path in links:
                        session.run("""
                            MATCH (source:MemoryNode {path: $source_path})
                            MATCH (target:MemoryNode {path: $target_path})
                            MERGE (source)-[:ASSOCIATED_WITH]->(target)
                        """, source_path=path, target_path=link_path)
            
            # Création du nœud temporel correspondant
            temporal_node = TemporalMemoryNode(
                content=content,
                metadata={
                    "path": path,
                    "summary": summary,
                    "strata": strata,
                    "neo4j_node_id": node_id
                },
                strata=strata,
                keywords=keywords
            )
            
            # Enregistrement dans le registre temporel
            self.add_entity(node_id, temporal_node)
            
            # Évolution temporelle de l'écriture
            self.temporal_dimension.evolve("neo4j_memory_written", {
                "path": path,
                "strata": strata,
                "keywords_count": len(keywords),
                "links_count": len(links) if links else 0,
                "transcendence_links_count": len(transcendence_links) if transcendence_links else 0,
                "immanence_links_count": len(immanence_links) if immanence_links else 0
            })
            
            # Apprentissage temporel
            self.learn_from_interaction({
                "type": "neo4j_memory_write",
                "path": path,
                "strata": strata,
                "content_length": len(content)
            })
            
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("neo4j_write_error", {
                "path": path,
                "error": str(e)
            })
    
    def read(self, path: str) -> TemporalMemoryNode:
        """Lit un nœud mémoire avec tracking temporel"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:MemoryNode {path: $path})
                    RETURN n
                """, path=path)
                
                record = result.single()
                if record:
                    node_data = record["n"]
                    
                    # Création du nœud temporel
                    temporal_node = TemporalMemoryNode(
                        content=node_data.get("descriptor", ""),
                        metadata={
                            "path": path,
                            "summary": node_data.get("summary", ""),
                            "strata": node_data.get("strata", "somatic"),
                            "neo4j_node_id": node_data.get("id")
                        },
                        strata=node_data.get("strata", "somatic"),
                        keywords=node_data.get("keywords", [])
                    )
                    
                    # Mise à jour de la conscience depuis Neo4j
                    consciousness_level = node_data.get("consciousness_level", 0.0)
                    temporal_node.consciousness.consciousness_level = consciousness_level
                    
                    # Évolution temporelle de la lecture
                    self.temporal_dimension.evolve("neo4j_memory_read", {
                        "path": path,
                        "consciousness_level": consciousness_level
                    })
                    
                    return temporal_node
                
                return None
                
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("neo4j_read_error", {
                "path": path,
                "error": str(e)
            })
            return None
    
    def find_by_keyword(self, keyword: str) -> List[str]:
        """Recherche par mot-clé avec tracking temporel"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:MemoryNode)
                    WHERE $keyword IN n.keywords
                    RETURN n.path
                """, keyword=keyword)
                
                paths = [record["n.path"] for record in result]
                
                # Évolution temporelle de la recherche
                self.temporal_dimension.evolve("neo4j_keyword_search", {
                    "keyword": keyword,
                    "results_count": len(paths)
                })
                
                return paths
                
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("neo4j_keyword_search_error", {
                "keyword": keyword,
                "error": str(e)
            })
            return []
    
    def find_by_strata(self, strata: str) -> List[str]:
        """Recherche par strate avec tracking temporel"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:MemoryNode)
                    WHERE n.strata = $strata
                    RETURN n.path
                """, strata=strata)
                
                paths = [record["n.path"] for record in result]
                
                # Évolution temporelle de la recherche
                self.temporal_dimension.evolve("neo4j_strata_search", {
                    "strata": strata,
                    "results_count": len(paths)
                })
                
                return paths
                
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("neo4j_strata_search_error", {
                "strata": strata,
                "error": str(e)
            })
            return []
    
    def traverse_transcendence_path(self, start_path: str, max_depth: int = 5) -> List[Dict]:
        """Traverse le chemin de transcendance avec tracking temporel"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH path = (start:MemoryNode {path: $start_path})-[:TRANSCENDS_TO*1..$max_depth]->(target:MemoryNode)
                    RETURN path
                    ORDER BY length(path)
                """, start_path=start_path, max_depth=max_depth)
                
                paths = []
                for record in result:
                    path_data = record["path"]
                    paths.append({
                        "path": path_data,
                        "depth": len(path_data.relationships)
                    })
                
                # Évolution temporelle de la traversée
                self.temporal_dimension.evolve("neo4j_transcendence_traversal", {
                    "start_path": start_path,
                    "max_depth": max_depth,
                    "paths_found": len(paths)
                })
                
                return paths
                
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("neo4j_transcendence_traversal_error", {
                "start_path": start_path,
                "error": str(e)
            })
            return []
    
    def traverse_immanence_path(self, start_path: str, max_depth: int = 5) -> List[Dict]:
        """Traverse le chemin d'immanence avec tracking temporel"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH path = (start:MemoryNode {path: $start_path})-[:IMMANENT_TO*1..$max_depth]->(target:MemoryNode)
                    RETURN path
                    ORDER BY length(path)
                """, start_path=start_path, max_depth=max_depth)
                
                paths = []
                for record in result:
                    path_data = record["path"]
                    paths.append({
                        "path": path_data,
                        "depth": len(path_data.relationships)
                    })
                
                # Évolution temporelle de la traversée
                self.temporal_dimension.evolve("neo4j_immanence_traversal", {
                    "start_path": start_path,
                    "max_depth": max_depth,
                    "paths_found": len(paths)
                })
                
                return paths
                
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("neo4j_immanence_traversal_error", {
                "start_path": start_path,
                "error": str(e)
            })
            return []
    
    def _get_parent_path(self, path: str) -> Optional[str]:
        """Récupère le chemin parent"""
        if "/" in path:
            return "/".join(path.split("/")[:-1])
        return None
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques avec métadonnées temporelles"""
        try:
            with self.driver.session() as session:
                # Statistiques de base
                total_nodes = session.run("MATCH (n:MemoryNode) RETURN count(n) as count").single()["count"]
                somatic_nodes = session.run("MATCH (n:Somatic) RETURN count(n) as count").single()["count"]
                cognitive_nodes = session.run("MATCH (n:Cognitive) RETURN count(n) as count").single()["count"]
                metaphysical_nodes = session.run("MATCH (n:Metaphysical) RETURN count(n) as count").single()["count"]
                
                # Statistiques temporelles
                avg_consciousness = session.run("""
                    MATCH (n:MemoryNode)
                    WHERE n.consciousness_level IS NOT NULL
                    RETURN avg(n.consciousness_level) as avg_consciousness
                """).single()["avg_consciousness"] or 0.0
                
                high_consciousness = session.run("""
                    MATCH (n:MemoryNode)
                    WHERE n.consciousness_level >= 0.8
                    RETURN count(n) as count
                """).single()["count"]
                
                stats = {
                    "total_nodes": total_nodes,
                    "strata_distribution": {
                        "somatic": somatic_nodes,
                        "cognitive": cognitive_nodes,
                        "metaphysical": metaphysical_nodes
                    },
                    "consciousness_stats": {
                        "average_consciousness": avg_consciousness,
                        "high_consciousness_nodes": high_consciousness
                    },
                    "temporal_metadata": {
                        "consciousness_level": self.get_consciousness_level(),
                        "evolution_count": len(self.temporal_dimension.evolution_history)
                    }
                }
                
                # Évolution temporelle des statistiques
                self.temporal_dimension.evolve("neo4j_statistics_retrieved", {
                    "total_nodes": total_nodes,
                    "avg_consciousness": avg_consciousness
                })
                
                return stats
                
        except Exception as e:
            # Gestion d'erreur avec évolution temporelle
            self.temporal_dimension.evolve("neo4j_statistics_error", {
                "error": str(e)
            })
            return {}
    
    def get_entity_specific_data(self) -> Dict[str, Any]:
        """Données spécifiques au backend Neo4j temporel"""
        return {
            "uri": self.uri,
            "user": self.user,
            "neo4j_available": NEO4J_AVAILABLE,
            "driver_initialized": self.driver is not None
        } 