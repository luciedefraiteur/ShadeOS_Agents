"""
⛧ Neo4j Backend for Fractal Memory ⛧
Architecte Démoniaque du Nexus Luciforme

Implements the transcendental memory vision with Neo4j graph database.
Supports Strata (Somatic, Cognitive, Metaphysical) and Respiration (Transcendence/Immanence).

Author: Alma (via Lucie Defraiteur)
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

from ..core.memory_node import FractalMemoryNode


class Neo4jBackend:
    """
    Neo4j backend for Fractal Memory with Strata and Respiration support.
    """
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        if not NEO4J_AVAILABLE:
            raise ImportError("Neo4j driver not available. Install with: pip install neo4j")
        
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._initialize_constraints()
    
    def close(self):
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()
    
    def _initialize_constraints(self):
        """Initialize Neo4j constraints and indexes for optimal performance."""
        with self.driver.session() as session:
            # Create unique constraint on node paths
            session.run("""
                CREATE CONSTRAINT memory_node_path IF NOT EXISTS
                FOR (n:MemoryNode) REQUIRE n.path IS UNIQUE
            """)
            
            # Create indexes for efficient querying
            session.run("CREATE INDEX memory_keywords IF NOT EXISTS FOR (n:MemoryNode) ON (n.keywords)")
            session.run("CREATE INDEX memory_strata IF NOT EXISTS FOR (n:MemoryNode) ON (n.strata)")
            session.run("CREATE INDEX memory_summary IF NOT EXISTS FOR (n:MemoryNode) ON (n.summary)")
    
    def write(self, path: str, content: str, summary: str, keywords: List[str], 
              links: List[str] = None, strata: str = "somatic", 
              transcendence_links: List[str] = None, immanence_links: List[str] = None):
        """
        Create or update a memory node in Neo4j with full Fractal Memory support.
        
        Args:
            path: Unique path identifier for the memory node
            content: Full content (descriptor) of the memory
            summary: Brief summary of the memory
            keywords: List of keywords for searching
            links: Horizontal associative links to other nodes
            strata: Memory strata level ("somatic", "cognitive", "metaphysical")
            transcendence_links: Vertical upward links (toward abstraction)
            immanence_links: Vertical downward links (toward concretization)
        """
        with self.driver.session() as session:
            # Create the main memory node
            node_id = str(uuid.uuid4())
            
            # Create the main memory node without APOC
            session.run("""
                MERGE (n:MemoryNode {path: $path})
                SET n.id = $node_id,
                    n.descriptor = $content,
                    n.summary = $summary,
                    n.keywords = $keywords,
                    n.strata = $strata,
                    n.created_at = datetime(),
                    n.updated_at = datetime()
            """, path=path, node_id=node_id, content=content, summary=summary,
                keywords=keywords, strata=strata)

            # Add strata-specific label manually
            if strata == "somatic":
                session.run("MATCH (n:MemoryNode {path: $path}) SET n:Somatic", path=path)
            elif strata == "cognitive":
                session.run("MATCH (n:MemoryNode {path: $path}) SET n:Cognitive", path=path)
            elif strata == "metaphysical":
                session.run("MATCH (n:MemoryNode {path: $path}) SET n:Metaphysical", path=path)
            
            # Create parent-child relationship if applicable
            parent_path = self._get_parent_path(path)
            if parent_path:
                session.run("""
                    MATCH (parent:MemoryNode {path: $parent_path})
                    MATCH (child:MemoryNode {path: $child_path})
                    MERGE (parent)-[:HAS_CHILD]->(child)
                """, parent_path=parent_path, child_path=path)
            
            # Create horizontal links
            if links:
                for link_path in links:
                    session.run("""
                        MATCH (source:MemoryNode {path: $source_path})
                        MATCH (target:MemoryNode {path: $target_path})
                        MERGE (source)-[:LINKED_TO]->(target)
                    """, source_path=path, target_path=link_path)
            
            # Create transcendence links (upward)
            if transcendence_links:
                for trans_path in transcendence_links:
                    session.run("""
                        MATCH (lower:MemoryNode {path: $lower_path})
                        MATCH (higher:MemoryNode {path: $higher_path})
                        MERGE (lower)-[:TRANSCENDS]->(higher)
                    """, lower_path=path, higher_path=trans_path)
            
            # Create immanence links (downward)
            if immanence_links:
                for imm_path in immanence_links:
                    session.run("""
                        MATCH (higher:MemoryNode {path: $higher_path})
                        MATCH (lower:MemoryNode {path: $lower_path})
                        MERGE (higher)-[:IMMANENT_IN]->(lower)
                    """, higher_path=path, lower_path=imm_path)
    
    def read(self, path: str) -> FractalMemoryNode:
        """
        Read a memory node from Neo4j and convert to FractalMemoryNode.
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:MemoryNode {path: $path})
                OPTIONAL MATCH (n)-[:HAS_CHILD]->(child)
                OPTIONAL MATCH (n)-[:LINKED_TO]->(linked)
                OPTIONAL MATCH (n)-[:TRANSCENDS]->(trans)
                OPTIONAL MATCH (n)-[:IMMANENT_IN]->(imm)
                
                RETURN n.descriptor as descriptor,
                       n.summary as summary,
                       n.keywords as keywords,
                       n.strata as strata,
                       collect(DISTINCT {path: child.path, summary: child.summary}) as children,
                       collect(DISTINCT {path: linked.path, summary: linked.summary}) as linked_memories,
                       collect(DISTINCT {path: trans.path, summary: trans.summary}) as transcendence_links,
                       collect(DISTINCT {path: imm.path, summary: imm.summary}) as immanence_links
            """, path=path)
            
            record = result.single()
            if not record:
                raise FileNotFoundError(f"Memory node at '{path}' does not exist.")
            
            # Filter out null entries from collections
            children = [c for c in record["children"] if c["path"] is not None]
            linked_memories = [l for l in record["linked_memories"] if l["path"] is not None]
            transcendence_links = [t for t in record["transcendence_links"] if t["path"] is not None]
            immanence_links = [i for i in record["immanence_links"] if i["path"] is not None]
            
            return FractalMemoryNode(
                descriptor=record["descriptor"],
                summary=record["summary"],
                keywords=record["keywords"] or [],
                strata=record["strata"] or "somatic",
                children=children,
                linked_memories=linked_memories,
                transcendence_links=transcendence_links,
                immanence_links=immanence_links
            )
    
    def find_by_keyword(self, keyword: str) -> List[str]:
        """
        Find memory nodes containing a specific keyword.
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:MemoryNode)
                WHERE $keyword IN n.keywords
                RETURN n.path as path
                ORDER BY n.updated_at DESC
            """, keyword=keyword)
            
            return [record["path"] for record in result]
    
    def find_by_strata(self, strata: str) -> List[str]:
        """
        Find all memory nodes in a specific strata.
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:MemoryNode {strata: $strata})
                RETURN n.path as path, n.summary as summary
                ORDER BY n.updated_at DESC
            """, strata=strata)
            
            return [{"path": record["path"], "summary": record["summary"]} for record in result]
    
    def traverse_transcendence_path(self, start_path: str, max_depth: int = 5) -> List[Dict]:
        """
        Follow transcendence links upward from a starting node.
        """
        with self.driver.session() as session:
            # Use string formatting for max_depth since Cypher doesn't allow parameter in range
            query = f"""
                MATCH path = (start:MemoryNode {{path: $start_path}})-[:TRANSCENDS*1..{max_depth}]->(end)
                RETURN [node in nodes(path) | {{path: node.path, summary: node.summary, strata: node.strata}}] as transcendence_path
                ORDER BY length(path) DESC
                LIMIT 1
            """
            result = session.run(query, start_path=start_path)

            record = result.single()
            return record["transcendence_path"] if record else []
    
    def traverse_immanence_path(self, start_path: str, max_depth: int = 5) -> List[Dict]:
        """
        Follow immanence links downward from a starting node.
        """
        with self.driver.session() as session:
            # Use string formatting for max_depth since Cypher doesn't allow parameter in range
            query = f"""
                MATCH path = (start:MemoryNode {{path: $start_path}})-[:IMMANENT_IN*1..{max_depth}]->(end)
                RETURN [node in nodes(path) | {{path: node.path, summary: node.summary, strata: node.strata}}] as immanence_path
                ORDER BY length(path) DESC
                LIMIT 1
            """
            result = session.run(query, start_path=start_path)

            record = result.single()
            return record["immanence_path"] if record else []
    
    def _get_parent_path(self, path: str) -> Optional[str]:
        """Extract parent path from a given path."""
        path = path.strip('/')
        if '/' not in path:
            return None
        return '/'.join(path.split('/')[:-1])
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the memory graph.
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:MemoryNode)
                OPTIONAL MATCH (n)-[r]->()
                RETURN 
                    count(DISTINCT n) as total_nodes,
                    count(DISTINCT r) as total_relationships,
                    count(DISTINCT CASE WHEN n.strata = 'somatic' THEN n END) as somatic_nodes,
                    count(DISTINCT CASE WHEN n.strata = 'cognitive' THEN n END) as cognitive_nodes,
                    count(DISTINCT CASE WHEN n.strata = 'metaphysical' THEN n END) as metaphysical_nodes
            """)
            
            record = result.single()
            return {
                "total_nodes": record["total_nodes"],
                "total_relationships": record["total_relationships"],
                "somatic_nodes": record["somatic_nodes"],
                "cognitive_nodes": record["cognitive_nodes"],
                "metaphysical_nodes": record["metaphysical_nodes"]
            } 