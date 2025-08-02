#!/usr/bin/env python3
"""
🧠 Analyseur Contextuel MD avec MemoryEngine

Analyseur intelligent qui utilise le MemoryEngine pour créer une intelligence
contextuelle récursive avec prompts d'injection et récupération de mémoire.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import sys
import json
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Ajout du path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Core.Archivist.MemoryEngine.engine import MemoryEngine

# Import conditionnel pour éviter les erreurs d'import relatif
try:
    from .openai_analyzer import OpenAIAnalyzer, AIInsights
except ImportError:
    from openai_analyzer import OpenAIAnalyzer, AIInsights


@dataclass
class ContextualAnalysis:
    """Analyse contextuelle enrichie."""
    
    file_path: str
    analysis_time: datetime
    ai_insights: AIInsights
    contextual_memories: List[str]
    related_documents: List[str]
    memory_injections: List[str]
    recursive_depth: int
    context_score: float
    memory_path: str


class ContextualMDAnalyzer:
    """Analyseur MD contextuel utilisant MemoryEngine."""
    
    def __init__(self, memory_engine: MemoryEngine = None, max_recursive_depth: int = 3,
                 force_ollama: bool = False):
        self.memory_engine = memory_engine or MemoryEngine()
        self.openai_analyzer = OpenAIAnalyzer(force_ollama=force_ollama)
        self.max_recursive_depth = max_recursive_depth
        
        # Namespaces mémoire
        self.md_namespace = "/documents/markdown"
        self.context_namespace = "/context/analysis"
        self.relations_namespace = "/relations/documents"
        
        print(f"🧠 Contextual MD Analyzer initialized")
        print(f"📊 Memory backend: {self.memory_engine.backend_type}")
        print(f"🔄 Max recursive depth: {max_recursive_depth}")
    
    async def analyze_with_context(self, file_path: str, content: str) -> ContextualAnalysis:
        """Analyse contextuelle complète d'un document MD."""
        
        print(f"\n🧠 Starting contextual analysis: {Path(file_path).name}")
        start_time = time.time()
        
        # 1. Analyse AI de base
        ai_insights = await self.openai_analyzer.analyze_content(content, file_path)
        print(f"🤖 AI analysis completed: {ai_insights.domain} | Score: {ai_insights.importance_score:.1f}")
        
        # 2. Récupération du contexte existant
        contextual_memories = await self._retrieve_contextual_memories(ai_insights)
        print(f"🔍 Retrieved {len(contextual_memories)} contextual memories")
        
        # 3. Analyse récursive avec contexte
        related_documents = await self._find_related_documents(ai_insights, contextual_memories)
        print(f"📄 Found {len(related_documents)} related documents")
        
        # 4. Injection récursive dans la mémoire
        memory_injections = await self._recursive_memory_injection(
            file_path, content, ai_insights, contextual_memories, related_documents
        )
        print(f"💉 Performed {len(memory_injections)} memory injections")
        
        # 5. Calcul du score contextuel
        context_score = self._calculate_context_score(
            ai_insights, contextual_memories, related_documents
        )
        
        # 6. Stockage de l'analyse contextuelle
        memory_path = await self._store_contextual_analysis(
            file_path, ai_insights, contextual_memories, related_documents, memory_injections
        )
        
        processing_time = time.time() - start_time
        print(f"⏱️ Contextual analysis completed in {processing_time:.3f}s")
        
        return ContextualAnalysis(
            file_path=file_path,
            analysis_time=datetime.now(),
            ai_insights=ai_insights,
            contextual_memories=contextual_memories,
            related_documents=related_documents,
            memory_injections=memory_injections,
            recursive_depth=self.max_recursive_depth,
            context_score=context_score,
            memory_path=memory_path
        )
    
    async def _retrieve_contextual_memories(self, ai_insights: AIInsights) -> List[str]:
        """Récupère les mémoires contextuelles pertinentes."""
        
        contextual_memories = []
        
        # Recherche par tags sémantiques
        for tag in ai_insights.semantic_tags[:5]:  # Top 5 tags
            try:
                memories = self.memory_engine.find_memories_by_keyword(tag)
                contextual_memories.extend(memories[:3])  # Max 3 par tag
            except Exception as e:
                print(f"⚠️ Error searching memories for tag '{tag}': {e}")
        
        # Recherche par domaine
        try:
            domain_memories = self.memory_engine.find_memories_by_keyword(ai_insights.domain)
            contextual_memories.extend(domain_memories[:5])
        except Exception as e:
            print(f"⚠️ Error searching memories for domain '{ai_insights.domain}': {e}")
        
        # Recherche par concepts clés
        for concept in ai_insights.key_concepts[:3]:
            try:
                concept_memories = self.memory_engine.find_memories_by_keyword(concept)
                contextual_memories.extend(concept_memories[:2])
            except Exception as e:
                print(f"⚠️ Error searching memories for concept '{concept}': {e}")
        
        # Déduplication et limitation
        unique_memories = list(set(contextual_memories))
        return unique_memories[:20]  # Max 20 mémoires contextuelles
    
    async def _find_related_documents(self, ai_insights: AIInsights, 
                                    contextual_memories: List[str]) -> List[str]:
        """Trouve les documents liés via l'analyse contextuelle."""
        
        related_documents = []
        
        # Analyse des mémoires contextuelles pour trouver des documents
        for memory_path in contextual_memories:
            try:
                memory_node = self.memory_engine.get_memory_node(memory_path)
                if memory_node and hasattr(memory_node, 'linked_memories'):
                    # Filtre pour les documents MD
                    md_links = [
                        link for link in memory_node.linked_memories 
                        if self.md_namespace in link
                    ]
                    related_documents.extend(md_links)
            except Exception as e:
                print(f"⚠️ Error analyzing memory {memory_path}: {e}")
        
        # Recherche par similarité sémantique
        for tag in ai_insights.semantic_tags[:3]:
            try:
                # Recherche dans le namespace des documents
                tag_docs = self.memory_engine.find_memories_by_keyword(tag)
                md_docs = [doc for doc in tag_docs if self.md_namespace in doc]
                related_documents.extend(md_docs[:5])
            except Exception as e:
                print(f"⚠️ Error finding related docs for tag '{tag}': {e}")
        
        # Déduplication
        unique_docs = list(set(related_documents))
        return unique_docs[:15]  # Max 15 documents liés
    
    async def _recursive_memory_injection(self, file_path: str, content: str, 
                                        ai_insights: AIInsights, contextual_memories: List[str],
                                        related_documents: List[str]) -> List[str]:
        """Injection récursive dans la base de données mémorielle."""
        
        injections = []
        
        # 1. Injection de l'analyse principale
        main_memory_path = f"{self.md_namespace}/{self._path_to_memory_key(file_path)}"
        
        try:
            # Contenu enrichi avec contexte
            enriched_content = {
                'original_content': content[:1000],  # Extrait
                'ai_analysis': asdict(ai_insights),
                'contextual_memories': contextual_memories,
                'related_documents': related_documents,
                'analysis_metadata': {
                    'file_path': file_path,
                    'analysis_time': datetime.now().isoformat(),
                    'context_score': self._calculate_context_score(ai_insights, contextual_memories, related_documents)
                }
            }
            
            self.memory_engine.create_memory(
                path=main_memory_path,
                content=json.dumps(enriched_content, indent=2),
                summary=f"Contextual analysis: {ai_insights.summary}",
                keywords=ai_insights.semantic_tags + [ai_insights.domain, 'contextual_analysis'],
                links=contextual_memories + related_documents,
                strata='cognitive'
            )
            injections.append(main_memory_path)
            
        except Exception as e:
            print(f"⚠️ Error injecting main memory: {e}")
        
        # 2. Injection des relations contextuelles
        for i, related_doc in enumerate(related_documents[:5]):  # Top 5
            try:
                relation_path = f"{self.relations_namespace}/{self._path_to_memory_key(file_path)}_rel_{i}"
                
                relation_data = {
                    'source_document': file_path,
                    'target_document': related_doc,
                    'relation_type': 'contextual_similarity',
                    'shared_concepts': ai_insights.key_concepts,
                    'similarity_score': self._calculate_similarity_score(ai_insights, related_doc)
                }
                
                self.memory_engine.create_memory(
                    path=relation_path,
                    content=json.dumps(relation_data, indent=2),
                    summary=f"Relation: {Path(file_path).name} ↔ {Path(related_doc).name}",
                    keywords=['relation', 'contextual', ai_insights.domain],
                    links=[main_memory_path, related_doc],
                    strata='cognitive'
                )
                injections.append(relation_path)
                
            except Exception as e:
                print(f"⚠️ Error injecting relation {i}: {e}")
        
        # 3. Injection des insights contextuels (récursif)
        if len(contextual_memories) > 0:
            try:
                context_insight_path = f"{self.context_namespace}/{self._path_to_memory_key(file_path)}_context"
                
                # Analyse récursive des mémoires contextuelles
                context_analysis = await self._analyze_contextual_memories(contextual_memories, ai_insights)
                
                self.memory_engine.create_memory(
                    path=context_insight_path,
                    content=json.dumps(context_analysis, indent=2),
                    summary=f"Contextual insights for {Path(file_path).name}",
                    keywords=['context', 'insights', ai_insights.domain] + ai_insights.semantic_tags[:3],
                    links=[main_memory_path] + contextual_memories,
                    strata='cognitive'
                )
                injections.append(context_insight_path)
                
            except Exception as e:
                print(f"⚠️ Error injecting contextual insights: {e}")
        
        return injections
    
    async def _analyze_contextual_memories(self, contextual_memories: List[str], 
                                         ai_insights: AIInsights) -> Dict:
        """Analyse récursive des mémoires contextuelles."""
        
        context_analysis = {
            'memory_count': len(contextual_memories),
            'dominant_themes': [],
            'concept_frequency': {},
            'temporal_patterns': [],
            'quality_assessment': 0.0
        }
        
        # Analyse des thèmes dominants
        all_keywords = []
        for memory_path in contextual_memories[:10]:  # Limite pour performance
            try:
                memory_node = self.memory_engine.get_memory_node(memory_path)
                if memory_node and hasattr(memory_node, 'keywords'):
                    all_keywords.extend(memory_node.keywords)
            except Exception as e:
                print(f"⚠️ Error analyzing memory {memory_path}: {e}")
        
        # Fréquence des concepts
        from collections import Counter
        keyword_freq = Counter(all_keywords)
        context_analysis['concept_frequency'] = dict(keyword_freq.most_common(10))
        context_analysis['dominant_themes'] = list(keyword_freq.keys())[:5]
        
        # Score de qualité contextuelle
        context_analysis['quality_assessment'] = min(100.0, len(contextual_memories) * 5.0)
        
        return context_analysis
    
    async def _store_contextual_analysis(self, file_path: str, ai_insights: AIInsights,
                                       contextual_memories: List[str], related_documents: List[str],
                                       memory_injections: List[str]) -> str:
        """Stocke l'analyse contextuelle complète."""
        
        analysis_path = f"{self.context_namespace}/analysis_{self._path_to_memory_key(file_path)}"
        
        try:
            analysis_data = {
                'file_path': file_path,
                'analysis_time': datetime.now().isoformat(),
                'ai_insights_summary': {
                    'domain': ai_insights.domain,
                    'importance_score': ai_insights.importance_score,
                    'complexity_level': ai_insights.complexity_level,
                    'semantic_tags': ai_insights.semantic_tags,
                    'key_concepts': ai_insights.key_concepts
                },
                'contextual_memories_count': len(contextual_memories),
                'related_documents_count': len(related_documents),
                'memory_injections_count': len(memory_injections),
                'context_score': self._calculate_context_score(ai_insights, contextual_memories, related_documents)
            }
            
            self.memory_engine.create_memory(
                path=analysis_path,
                content=json.dumps(analysis_data, indent=2),
                summary=f"Contextual analysis summary for {Path(file_path).name}",
                keywords=['contextual_analysis', 'summary', ai_insights.domain] + ai_insights.semantic_tags[:3],
                links=memory_injections,
                strata='cognitive'
            )
            
            return analysis_path
            
        except Exception as e:
            print(f"⚠️ Error storing contextual analysis: {e}")
            return ""
    
    def _calculate_context_score(self, ai_insights: AIInsights, 
                               contextual_memories: List[str], related_documents: List[str]) -> float:
        """Calcule un score de richesse contextuelle."""
        
        score = 0.0
        
        # Score basé sur l'importance AI
        score += ai_insights.importance_score * 0.3
        
        # Score basé sur les mémoires contextuelles
        score += min(50.0, len(contextual_memories) * 2.5)
        
        # Score basé sur les documents liés
        score += min(30.0, len(related_documents) * 2.0)
        
        # Score basé sur la richesse sémantique
        score += min(20.0, len(ai_insights.semantic_tags) * 2.0)
        
        return min(100.0, score)
    
    def _calculate_similarity_score(self, ai_insights: AIInsights, related_doc: str) -> float:
        """Calcule un score de similarité avec un document lié."""
        
        try:
            # Récupération du document lié
            related_memory = self.memory_engine.get_memory_node(related_doc)
            if not related_memory or not hasattr(related_memory, 'keywords'):
                return 0.0
            
            # Intersection des mots-clés
            common_keywords = set(ai_insights.semantic_tags) & set(related_memory.keywords)
            similarity = len(common_keywords) / max(1, len(set(ai_insights.semantic_tags) | set(related_memory.keywords)))
            
            return similarity * 100.0
            
        except Exception as e:
            print(f"⚠️ Error calculating similarity: {e}")
            return 0.0
    
    def _path_to_memory_key(self, file_path: str) -> str:
        """Convertit un chemin de fichier en clé mémoire."""
        
        path = Path(file_path)
        # Nettoyage et normalisation
        memory_key = str(path).replace('/', '_').replace('\\', '_').replace('.md', '')
        memory_key = ''.join(c for c in memory_key if c.isalnum() or c in '_-')
        return memory_key.lower()


async def test_contextual_analyzer():
    """Test de l'analyseur contextuel."""
    
    print("🧪 Testing Contextual MD Analyzer...")
    
    # Initialisation
    memory_engine = MemoryEngine()
    analyzer = ContextualMDAnalyzer(memory_engine, max_recursive_depth=2)
    
    # Test content
    test_content = """
# Architecture Document

This document describes the system architecture for our AI-powered documentation system.

## Key Components
- Memory Engine: Contextual storage and retrieval
- AI Analyzer: Intelligent content analysis
- Partitioning System: Document structure analysis

## Integration Points
The system integrates with OpenAI for semantic analysis and uses a graph-based memory system
for contextual understanding and relationship mapping.
"""
    
    # Analyse contextuelle
    analysis = await analyzer.analyze_with_context("test_architecture.md", test_content)
    
    print(f"\n📊 Contextual Analysis Results:")
    print(f"  🎯 Domain: {analysis.ai_insights.domain}")
    print(f"  ⭐ Importance: {analysis.ai_insights.importance_score:.1f}")
    print(f"  🧠 Context Score: {analysis.context_score:.1f}")
    print(f"  🔍 Contextual Memories: {len(analysis.contextual_memories)}")
    print(f"  📄 Related Documents: {len(analysis.related_documents)}")
    print(f"  💉 Memory Injections: {len(analysis.memory_injections)}")
    print(f"  🔄 Recursive Depth: {analysis.recursive_depth}")
    print(f"  💾 Memory Path: {analysis.memory_path}")


if __name__ == "__main__":
    asyncio.run(test_contextual_analyzer())
