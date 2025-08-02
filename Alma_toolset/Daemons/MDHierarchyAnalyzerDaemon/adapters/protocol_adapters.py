#!/usr/bin/env python3
"""
🔌 Protocol Adapters

Adaptateurs de protocole pour tous les composants du daemon.
Permet la communication standardisée via MessageBus.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import time
import json
import sys
import os
from typing import Dict, Any, List
from dataclasses import asdict
from pathlib import Path

# Ajout du path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Imports conditionnels
try:
    from .message_bus import MessageBus, MessageHandler, ProtocolError
    from ..core.content_type_detector import ContentTypeDetector, ContentType, ContentCharacteristics
    from ..core.openai_analyzer import OpenAIAnalyzer, AIInsights
    from Core.Archivist.MemoryEngine.engine import MemoryEngine
except ImportError:
    try:
        from message_bus import MessageBus, MessageHandler, ProtocolError
        from content_type_detector import ContentTypeDetector, ContentType, ContentCharacteristics
        from openai_analyzer import OpenAIAnalyzer, AIInsights
        from Core.Archivist.MemoryEngine.engine import MemoryEngine
    except ImportError:
        # Fallback complet si aucun import ne fonctionne
        print("⚠️ Warning: Some imports failed, using fallback implementations")

        # Fallback minimal pour les tests
        class MessageBus:
            def __init__(self): pass
        class MessageHandler:
            def __init__(self, *args): pass
        class ProtocolError(Exception):
            def __init__(self, code, message): super().__init__(message)

        from enum import Enum
        from dataclasses import dataclass

        class ContentType(Enum):
            CODE = "code"
            DOCUMENTATION = "documentation"

        @dataclass
        class ContentCharacteristics:
            content_type: ContentType
            confidence_score: float = 0.5

        class ContentTypeDetector:
            def detect_content_type(self, *args):
                return ContentCharacteristics(ContentType.DOCUMENTATION, 0.5)

        class AIInsights:
            def __init__(self): pass

        class OpenAIAnalyzer:
            def __init__(self, *args, **kwargs): pass

        class MemoryEngine:
            def __init__(self): pass


class ContentDetectorAdapter:
    """Adaptateur protocole pour ContentTypeDetector."""
    
    def __init__(self, detector: ContentTypeDetector, message_bus: MessageBus):
        self.detector = detector
        self.message_handler = MessageHandler("content_detector", message_bus)
        self._register_handlers()
        
        print("🔌 ContentDetectorAdapter initialized")
    
    def _register_handlers(self):
        """Enregistre les handlers de protocole."""
        self.message_handler.register_handler("detect_content_type", self._handle_detect_content_type)
        self.message_handler.register_handler("analyze_characteristics", self._handle_analyze_characteristics)
        self.message_handler.register_handler("recommend_strategy", self._handle_recommend_strategy)
    
    async def _handle_detect_content_type(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle la détection de type de contenu."""
        try:
            # Validation des paramètres
            if "file_path" not in params or "content" not in params:
                raise ProtocolError(1009, "Missing required parameters: file_path, content")
            
            file_path = params["file_path"]
            content = params["content"]
            options = params.get("options", {})
            
            # Détection
            start_time = time.time()
            characteristics = self.detector.detect_content_type(file_path, content)
            processing_time = time.time() - start_time
            
            # Recommandation de stratégie
            recommended_strategy = self._recommend_partitioning_strategy(characteristics)
            
            result = {
                "content_type": characteristics.content_type.value,
                "confidence_score": characteristics.confidence_score,
                "recommended_strategy": recommended_strategy,
                "processing_time": processing_time
            }
            
            # Inclusion des caractéristiques si demandé
            if options.get("include_characteristics", False):
                result["characteristics"] = {
                    "code_ratio": characteristics.code_ratio,
                    "documentation_ratio": characteristics.documentation_ratio,
                    "structural_complexity": characteristics.structural_complexity,
                    "narrative_flow": characteristics.narrative_flow,
                    "technical_density": characteristics.technical_density,
                    "language_detected": characteristics.language_detected
                }
            
            return result
            
        except Exception as e:
            raise ProtocolError(1001, f"Content detection failed: {e}")
    
    async def _handle_analyze_characteristics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle l'analyse détaillée des caractéristiques."""
        try:
            file_path = params["file_path"]
            content = params["content"]
            
            characteristics = self.detector.detect_content_type(file_path, content)
            
            return {
                "file_path": file_path,
                "characteristics": asdict(characteristics),
                "analysis_summary": {
                    "primary_type": characteristics.content_type.value,
                    "confidence": characteristics.confidence_score,
                    "dominant_aspect": self._get_dominant_aspect(characteristics),
                    "complexity_level": self._assess_complexity_level(characteristics)
                }
            }
            
        except Exception as e:
            raise ProtocolError(1001, f"Characteristics analysis failed: {e}")
    
    async def _handle_recommend_strategy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle la recommandation de stratégie."""
        try:
            # Peut recevoir soit les caractéristiques directement, soit file_path + content
            if "characteristics" in params:
                # Reconstruction des caractéristiques depuis dict
                char_dict = params["characteristics"]
                characteristics = ContentCharacteristics(
                    content_type=ContentType(char_dict["content_type"]),
                    code_ratio=char_dict["code_ratio"],
                    documentation_ratio=char_dict["documentation_ratio"],
                    structural_complexity=char_dict["structural_complexity"],
                    narrative_flow=char_dict["narrative_flow"],
                    technical_density=char_dict["technical_density"],
                    language_detected=char_dict["language_detected"],
                    confidence_score=char_dict["confidence_score"]
                )
            else:
                # Détection à partir du contenu
                file_path = params["file_path"]
                content = params["content"]
                characteristics = self.detector.detect_content_type(file_path, content)
            
            strategy = self._recommend_partitioning_strategy(characteristics)
            
            return {
                "recommended_strategy": strategy,
                "reasoning": self._explain_strategy_choice(characteristics, strategy),
                "alternative_strategies": self._get_alternative_strategies(characteristics),
                "confidence": characteristics.confidence_score
            }
            
        except Exception as e:
            raise ProtocolError(1001, f"Strategy recommendation failed: {e}")
    
    def _recommend_partitioning_strategy(self, characteristics: ContentCharacteristics) -> str:
        """Recommande une stratégie de partitioning."""
        
        content_type = characteristics.content_type
        
        if content_type == ContentType.CODE:
            # Code : privilégier structure syntaxique
            if characteristics.structural_complexity > 0.7:
                return "regex"  # Structure complexe
            else:
                return "textual"  # Code simple
                
        elif content_type == ContentType.DOCUMENTATION:
            # Documentation : privilégier flux sémantique
            if characteristics.narrative_flow > 0.6:
                return "textual"  # Flux narratif
            else:
                return "regex"  # Structure formelle
                
        elif content_type == ContentType.MIXED:
            # Mixte : analyse adaptative
            if characteristics.code_ratio > 0.6:
                return "regex"
            else:
                return "textual"
                
        elif content_type == ContentType.CONFIGURATION:
            # Configuration : structure hiérarchique
            return "regex"
            
        else:
            # Inconnu : fallback sécurisé
            return "textual"
    
    def _explain_strategy_choice(self, characteristics: ContentCharacteristics, strategy: str) -> str:
        """Explique le choix de stratégie."""
        
        content_type = characteristics.content_type.value
        
        if strategy == "regex":
            return f"Regex strategy chosen for {content_type} due to structural complexity ({characteristics.structural_complexity:.2f}) or code dominance ({characteristics.code_ratio:.2f})"
        elif strategy == "textual":
            return f"Textual strategy chosen for {content_type} due to narrative flow ({characteristics.narrative_flow:.2f}) or documentation dominance ({characteristics.documentation_ratio:.2f})"
        else:
            return f"Default strategy for {content_type}"
    
    def _get_alternative_strategies(self, characteristics: ContentCharacteristics) -> List[str]:
        """Retourne les stratégies alternatives."""
        
        primary = self._recommend_partitioning_strategy(characteristics)
        all_strategies = ["regex", "textual", "emergency"]
        
        return [s for s in all_strategies if s != primary]
    
    def _get_dominant_aspect(self, characteristics: ContentCharacteristics) -> str:
        """Détermine l'aspect dominant."""
        
        if characteristics.code_ratio > characteristics.documentation_ratio:
            return "code"
        elif characteristics.documentation_ratio > characteristics.code_ratio:
            return "documentation"
        else:
            return "mixed"
    
    def _assess_complexity_level(self, characteristics: ContentCharacteristics) -> str:
        """Évalue le niveau de complexité."""
        
        complexity = characteristics.structural_complexity
        
        if complexity > 0.7:
            return "high"
        elif complexity > 0.3:
            return "medium"
        else:
            return "low"


class AIAnalyzerAdapter:
    """Adaptateur protocole pour AI Analyzer."""
    
    def __init__(self, analyzer: OpenAIAnalyzer, message_bus: MessageBus):
        self.analyzer = analyzer
        self.message_handler = MessageHandler("ai_analyzer", message_bus)
        self._register_handlers()
        
        print("🔌 AIAnalyzerAdapter initialized")
    
    def _register_handlers(self):
        """Enregistre les handlers de protocole."""
        self.message_handler.register_handler("analyze_content", self._handle_analyze_content)
        self.message_handler.register_handler("check_budget", self._handle_check_budget)
        self.message_handler.register_handler("get_cost_summary", self._handle_get_cost_summary)
    
    async def _handle_analyze_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle l'analyse de contenu."""
        try:
            # Validation des paramètres
            if "content" not in params:
                raise ProtocolError(1009, "Missing required parameter: content")
            
            content = params["content"]
            file_path = params.get("file_path", "")
            content_type = params.get("content_type", "unknown")
            options = params.get("analysis_options", {})
            
            # Configuration temporaire si options spécifiées
            if "force_ollama" in options:
                original_force_ollama = self.analyzer.force_ollama
                self.analyzer.force_ollama = options["force_ollama"]
            
            try:
                # Analyse
                start_time = time.time()
                insights = await self.analyzer.analyze_content(content, file_path)
                total_time = time.time() - start_time
                
                result = {
                    "ai_insights": asdict(insights),
                    "cost": insights.estimated_cost,
                    "processing_time": total_time,
                    "model_used": insights.model_used,
                    "content_type": content_type,
                    "status": "completed"
                }
                
                return result
                
            finally:
                # Restauration de la configuration
                if "force_ollama" in options:
                    self.analyzer.force_ollama = original_force_ollama
            
        except Exception as e:
            raise ProtocolError(1002, f"AI analysis failed: {e}")
    
    async def _handle_check_budget(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle la vérification du budget."""
        try:
            content = params.get("content", "")
            model = params.get("model", "fast")
            
            can_afford = self.analyzer.can_afford_analysis(content, model)
            estimated_cost = self.analyzer._estimate_cost(content, model)
            
            cost_summary = self.analyzer.get_cost_summary()
            
            return {
                "can_afford": can_afford,
                "estimated_cost": estimated_cost,
                "current_budget_status": {
                    "daily_remaining": cost_summary["daily_remaining"],
                    "hourly_remaining": cost_summary["hourly_remaining"],
                    "daily_used": cost_summary["daily_cost"],
                    "hourly_used": cost_summary["hourly_cost"]
                }
            }
            
        except Exception as e:
            raise ProtocolError(1002, f"Budget check failed: {e}")
    
    async def _handle_get_cost_summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle la récupération du résumé des coûts."""
        try:
            cost_summary = self.analyzer.get_cost_summary()
            
            return {
                "cost_summary": cost_summary,
                "openai_available": self.analyzer.openai_available,
                "ollama_available": getattr(self.analyzer, 'ollama_available', False),
                "force_ollama": self.analyzer.force_ollama
            }
            
        except Exception as e:
            raise ProtocolError(1002, f"Cost summary failed: {e}")


class MemoryEngineAdapter:
    """Adaptateur protocole pour MemoryEngine."""

    def __init__(self, memory_engine: MemoryEngine, message_bus: MessageBus):
        self.memory_engine = memory_engine
        self.message_handler = MessageHandler("memory_engine", message_bus)
        self._register_handlers()

        print("🔌 MemoryEngineAdapter initialized")

    def _register_handlers(self):
        """Enregistre les handlers de protocole."""
        self.message_handler.register_handler("create_memory", self._handle_create_memory)
        self.message_handler.register_handler("get_memory", self._handle_get_memory)
        self.message_handler.register_handler("find_memories_by_keyword", self._handle_find_memories_by_keyword)
        self.message_handler.register_handler("inject_contextual_memory", self._handle_inject_contextual_memory)
        self.message_handler.register_handler("retrieve_contextual_memories", self._handle_retrieve_contextual_memories)
        self.message_handler.register_handler("forget_memory", self._handle_forget_memory)
        self.message_handler.register_handler("get_memory_stats", self._handle_get_memory_stats)

    async def _handle_create_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle la création de mémoire."""
        try:
            # Validation des paramètres
            required_params = ["path", "content"]
            for param in required_params:
                if param not in params:
                    raise ProtocolError(1009, f"Missing required parameter: {param}")

            path = params["path"]
            content = params["content"]
            summary = params.get("summary", "")
            keywords = params.get("keywords", [])
            links = params.get("links", [])
            strata = params.get("strata", "cognitive")

            # Création de la mémoire
            start_time = time.time()
            self.memory_engine.create_memory(
                path=path,
                content=content,
                summary=summary,
                keywords=keywords,
                links=links,
                strata=strata
            )
            processing_time = time.time() - start_time

            return {
                "success": True,
                "memory_path": path,
                "processing_time": processing_time,
                "keywords_count": len(keywords),
                "links_count": len(links)
            }

        except Exception as e:
            raise ProtocolError(1003, f"Memory creation failed: {e}")

    async def _handle_get_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle la récupération de mémoire."""
        try:
            if "path" not in params:
                raise ProtocolError(1009, "Missing required parameter: path")

            path = params["path"]

            # Récupération de la mémoire
            memory_node = self.memory_engine.get_memory_node(path)

            if memory_node is None:
                return {
                    "found": False,
                    "memory_path": path
                }

            return {
                "found": True,
                "memory_path": path,
                "content": memory_node.content,
                "summary": memory_node.summary,
                "keywords": memory_node.keywords,
                "links": memory_node.linked_memories,
                "strata": memory_node.strata,
                "created_at": memory_node.created_at,
                "updated_at": memory_node.updated_at
            }

        except Exception as e:
            raise ProtocolError(1003, f"Memory retrieval failed: {e}")

    async def _handle_find_memories_by_keyword(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle la recherche par mot-clé."""
        try:
            if "keyword" not in params:
                raise ProtocolError(1009, "Missing required parameter: keyword")

            keyword = params["keyword"]
            max_results = params.get("max_results", 20)

            # Recherche
            start_time = time.time()
            memory_paths = self.memory_engine.find_memories_by_keyword(keyword)
            processing_time = time.time() - start_time

            # Limitation des résultats
            limited_paths = memory_paths[:max_results]

            return {
                "keyword": keyword,
                "total_found": len(memory_paths),
                "returned_count": len(limited_paths),
                "memory_paths": limited_paths,
                "processing_time": processing_time
            }

        except Exception as e:
            raise ProtocolError(1003, f"Memory search failed: {e}")

    async def _handle_inject_contextual_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle l'injection contextuelle récursive."""
        try:
            # Validation des paramètres
            required_params = ["file_path", "content"]
            for param in required_params:
                if param not in params:
                    raise ProtocolError(1009, f"Missing required parameter: {param}")

            file_path = params["file_path"]
            content = params["content"]
            ai_insights = params.get("ai_insights", {})
            content_characteristics = params.get("content_characteristics", {})
            recursive_depth = params.get("recursive_depth", 3)

            # Génération du chemin mémoire
            memory_key = self._file_path_to_memory_key(file_path)
            content_type = content_characteristics.get("content_type", "unknown")
            main_memory_path = f"/documents/{content_type}/{memory_key}"

            injections = []

            # 1. Injection principale
            enriched_content = {
                "original_content": content[:2000],  # Extrait
                "ai_insights": ai_insights,
                "content_characteristics": content_characteristics,
                "file_metadata": {
                    "file_path": file_path,
                    "injection_time": time.time(),
                    "recursive_depth": recursive_depth
                }
            }

            self.memory_engine.create_memory(
                path=main_memory_path,
                content=json.dumps(enriched_content, indent=2),
                summary=ai_insights.get("summary", f"Analysis of {Path(file_path).name}"),
                keywords=ai_insights.get("semantic_tags", []) + [content_type, "contextual_analysis"],
                strata="cognitive"
            )
            injections.append(main_memory_path)

            # 2. Injection des relations (si profondeur > 1)
            if recursive_depth > 1:
                relations_path = f"/relations/{content_type}/{memory_key}_relations"

                relation_data = {
                    "source_file": file_path,
                    "content_type": content_type,
                    "ai_domain": ai_insights.get("domain", "unknown"),
                    "importance_score": ai_insights.get("importance_score", 0),
                    "related_concepts": ai_insights.get("key_concepts", [])
                }

                self.memory_engine.create_memory(
                    path=relations_path,
                    content=json.dumps(relation_data, indent=2),
                    summary=f"Relations for {Path(file_path).name}",
                    keywords=["relations", content_type] + ai_insights.get("semantic_tags", [])[:3],
                    links=[main_memory_path],
                    strata="cognitive"
                )
                injections.append(relations_path)

            return {
                "success": True,
                "main_memory_path": main_memory_path,
                "injections_count": len(injections),
                "injected_paths": injections,
                "recursive_depth": recursive_depth
            }

        except Exception as e:
            raise ProtocolError(1003, f"Contextual memory injection failed: {e}")

    async def _handle_retrieve_contextual_memories(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle la récupération de mémoires contextuelles."""
        try:
            search_criteria = params.get("search_criteria", {})
            keywords = search_criteria.get("keywords", [])
            content_type = search_criteria.get("content_type", "")
            max_results = search_criteria.get("max_results", 20)

            contextual_memories = []

            # Recherche par mots-clés
            for keyword in keywords[:5]:  # Limite à 5 mots-clés
                try:
                    memories = self.memory_engine.find_memories_by_keyword(keyword)
                    contextual_memories.extend(memories[:3])  # Max 3 par mot-clé
                except Exception as e:
                    print(f"⚠️ Error searching for keyword '{keyword}': {e}")

            # Recherche par type de contenu
            if content_type:
                try:
                    type_memories = self.memory_engine.find_memories_by_keyword(content_type)
                    contextual_memories.extend(type_memories[:5])
                except Exception as e:
                    print(f"⚠️ Error searching for content type '{content_type}': {e}")

            # Déduplication et limitation
            unique_memories = list(set(contextual_memories))
            limited_memories = unique_memories[:max_results]

            return {
                "search_criteria": search_criteria,
                "total_found": len(unique_memories),
                "returned_count": len(limited_memories),
                "contextual_memories": limited_memories
            }

        except Exception as e:
            raise ProtocolError(1003, f"Contextual memory retrieval failed: {e}")

    async def _handle_forget_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle la suppression de mémoire."""
        try:
            if "path" not in params:
                raise ProtocolError(1009, "Missing required parameter: path")

            path = params["path"]

            # Suppression
            self.memory_engine.forget_memory(path)

            return {
                "success": True,
                "forgotten_path": path
            }

        except Exception as e:
            raise ProtocolError(1003, f"Memory deletion failed: {e}")

    async def _handle_get_memory_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle la récupération des statistiques mémoire."""
        try:
            # Statistiques basiques (à adapter selon l'API du MemoryEngine)
            stats = {
                "backend_type": getattr(self.memory_engine, 'backend_type', 'unknown'),
                "total_memories": "unknown",  # À implémenter selon l'API
                "memory_usage": "unknown",    # À implémenter selon l'API
                "last_operation": time.time()
            }

            return {
                "memory_stats": stats,
                "timestamp": time.time()
            }

        except Exception as e:
            raise ProtocolError(1003, f"Memory stats retrieval failed: {e}")

    def _file_path_to_memory_key(self, file_path: str) -> str:
        """Convertit un chemin de fichier en clé mémoire."""
        path = Path(file_path)
        memory_key = str(path).replace('/', '_').replace('\\', '_').replace('.md', '')
        memory_key = ''.join(c for c in memory_key if c.isalnum() or c in '_-')
        return memory_key.lower()


async def test_protocol_adapters():
    """Test des adaptateurs de protocole."""
    
    print("🔌 Testing Protocol Adapters...")
    
    # Création du bus et des composants
    bus = MessageBus()
    await bus.start()
    
    # Création des adaptateurs
    detector = ContentTypeDetector()
    detector_adapter = ContentDetectorAdapter(detector, bus)
    
    analyzer = OpenAIAnalyzer(force_ollama=True)  # Force Ollama pour test
    analyzer_adapter = AIAnalyzerAdapter(analyzer, bus)

    # Création de l'adaptateur mémoire
    memory_engine = MemoryEngine()
    memory_adapter = MemoryEngineAdapter(memory_engine, bus)
    
    # Test de détection de contenu
    try:
        print("\n🔍 Testing Content Detection Protocol...")
        
        test_content = """
# Test Document

This is a test document with some code:

```python
def hello():
    return "world"
```

And some documentation explaining the function.
"""
        
        detection_result = await bus.send_request(
            "content_detector",
            "detect_content_type",
            {
                "file_path": "test.md",
                "content": test_content,
                "options": {"include_characteristics": True}
            }
        )
        
        print(f"🔍 Detection result: {detection_result['content_type']} (confidence: {detection_result['confidence_score']:.2f})")
        print(f"🔧 Recommended strategy: {detection_result['recommended_strategy']}")
        
        # Test de recommandation de stratégie
        strategy_result = await bus.send_request(
            "content_detector",
            "recommend_strategy",
            {"characteristics": detection_result["characteristics"]}
        )
        
        print(f"🎯 Strategy reasoning: {strategy_result['reasoning']}")
        
    except ProtocolError as e:
        print(f"🔍 Detection error: {e}")
    
    # Test d'analyse AI
    try:
        print("\n🤖 Testing AI Analysis Protocol...")
        
        # Vérification du budget
        budget_result = await bus.send_request(
            "ai_analyzer",
            "check_budget",
            {"content": test_content, "model": "fast"}
        )
        
        print(f"💰 Can afford analysis: {budget_result['can_afford']}")
        print(f"💰 Estimated cost: ${budget_result['estimated_cost']:.4f}")
        
        # Analyse du contenu
        analysis_result = await bus.send_request(
            "ai_analyzer",
            "analyze_content",
            {
                "content": test_content,
                "file_path": "test.md",
                "content_type": "mixed",
                "analysis_options": {"force_ollama": True}
            }
        )
        
        print(f"🤖 Analysis completed with {analysis_result['model_used']}")
        print(f"⏱️ Processing time: {analysis_result['processing_time']:.2f}s")
        print(f"💰 Cost: ${analysis_result['cost']:.4f}")
        
    except ProtocolError as e:
        print(f"🤖 Analysis error: {e}")

    # Test de MemoryEngine
    try:
        print("\n🧠 Testing MemoryEngine Protocol...")

        # Test de création de mémoire
        create_result = await bus.send_request(
            "memory_engine",
            "create_memory",
            {
                "path": "/test/protocol_test",
                "content": "Test content for protocol validation",
                "summary": "Protocol test memory",
                "keywords": ["test", "protocol", "validation"],
                "strata": "cognitive"
            }
        )

        print(f"🧠 Memory created: {create_result['memory_path']}")

        # Test de récupération
        get_result = await bus.send_request(
            "memory_engine",
            "get_memory",
            {"path": "/test/protocol_test"}
        )

        print(f"🧠 Memory retrieved: {get_result['found']}")

        # Test de recherche
        search_result = await bus.send_request(
            "memory_engine",
            "find_memories_by_keyword",
            {"keyword": "protocol", "max_results": 5}
        )

        print(f"🧠 Search found: {search_result['total_found']} memories")

        # Test d'injection contextuelle
        injection_result = await bus.send_request(
            "memory_engine",
            "inject_contextual_memory",
            {
                "file_path": "test_protocol.md",
                "content": test_content,
                "ai_insights": {
                    "summary": "Test protocol document",
                    "semantic_tags": ["protocol", "test", "communication"],
                    "domain": "testing",
                    "importance_score": 75.0
                },
                "content_characteristics": {
                    "content_type": "documentation",
                    "code_ratio": 0.2,
                    "documentation_ratio": 0.8
                },
                "recursive_depth": 2
            }
        )

        print(f"🧠 Contextual injection: {injection_result['injections_count']} injections")

    except ProtocolError as e:
        print(f"🧠 Memory error: {e}")

    # Health checks
    try:
        print("\n🏥 Testing Health Checks...")
        
        detector_health = await bus.send_request("content_detector", "health_check", {})
        analyzer_health = await bus.send_request("ai_analyzer", "health_check", {})
        memory_health = await bus.send_request("memory_engine", "health_check", {})

        print(f"🔍 Content Detector: {detector_health['status']}")
        print(f"🤖 AI Analyzer: {analyzer_health['status']}")
        print(f"🧠 Memory Engine: {memory_health['status']}")
        
    except ProtocolError as e:
        print(f"🏥 Health check error: {e}")
    
    # Statut global du bus
    bus_status = bus.get_health_status()
    print(f"\n📡 Bus Status: {bus_status['status']} ({bus_status['total_messages']} messages, {bus_status['total_errors']} errors)")
    
    await bus.stop()


if __name__ == "__main__":
    asyncio.run(test_protocol_adapters())
