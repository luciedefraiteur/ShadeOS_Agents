#!/usr/bin/env python3
"""
🎭 Intelligent Orchestrator

Orchestrateur intelligent basé sur des prompts qui génèrent des instructions
d'orchestration pour les adaptateurs. L'IA décide de la stratégie optimale.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Imports conditionnels
try:
    from ..adapters.message_bus import MessageBus, ProtocolError
    from ..core.openai_analyzer import OpenAIAnalyzer
    from ..prompts.dynamic_injection_system import LuciformDynamicPromptSystem
except ImportError:
    try:
        from message_bus import MessageBus, ProtocolError
        from openai_analyzer import OpenAIAnalyzer
        from dynamic_injection_system import LuciformDynamicPromptSystem
    except ImportError:
        # Fallback complet
        class MessageBus:
            def __init__(self): pass
        class ProtocolError(Exception):
            def __init__(self, code, message): super().__init__(message)
        class OpenAIAnalyzer:
            def __init__(self, *args, **kwargs): pass
        class LuciformDynamicPromptSystem:
            def __init__(self): pass


@dataclass
class OrchestrationResult:
    """Résultat d'orchestration."""
    
    original_instructions: Dict[str, Any]
    execution_results: Dict[str, Any]
    orchestration_success: bool
    total_components_executed: int
    processing_time: float
    enhancement_applied: bool = False


class PromptTemplateManager:
    """Gestionnaire de templates de prompts intelligents."""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.dynamic_templates = {}
    
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialise les templates de prompts."""
        
        return {
            "master_orchestration": """
You are an intelligent document analysis orchestrator. Analyze the content and generate structured instructions for system components.

Content to analyze:
{content}

File context:
- Path: {file_path}
- Size: {content_size} characters
- Extension: {file_extension}

Available components:
- content_detector: detect_content_type, analyze_characteristics
- partitioner: adaptive_partition, regex_partition, textual_partition
- ai_analyzer: analyze_content, deep_analysis
- memory_engine: inject_contextual_memory, retrieve_contextual_memories, create_memory

Generate orchestration instructions in this JSON format:
{{
  "analysis": {{
    "content_type": "code|documentation|mixed|configuration",
    "complexity": "low|medium|high", 
    "domain": "detected_domain",
    "confidence": 0.85,
    "key_characteristics": ["trait1", "trait2"]
  }},
  "orchestration_instructions": {{
    "priority": "high|medium|low",
    "parallel_execution": false,
    "components": [
      {{
        "adapter": "component_name",
        "method": "method_name",
        "params": {{}},
        "depends_on": [],
        "timeout": 30
      }}
    ]
  }},
  "expected_outcomes": {{
    "processing_time_estimate": 15,
    "quality_score_estimate": 0.8
  }}
}}

Focus on intelligent orchestration that maximizes analysis quality.
""",
            
            "code_orchestration": """
Analyze this code and generate intelligent orchestration for code-specific processing.

Code content:
{content}

Language: {language}
File: {file_path}

Generate orchestration focusing on:
1. Structural analysis (functions, classes, dependencies)
2. Code quality assessment  
3. Architecture pattern detection

Return JSON orchestration instructions optimized for code analysis.
""",
            
            "documentation_orchestration": """
Analyze this documentation and generate intelligent orchestration for documentation-specific processing.

Documentation content:
{content}

Document type: {doc_type}
File: {file_path}

Generate orchestration focusing on:
1. Information architecture analysis
2. Knowledge gap identification
3. Content quality assessment

Return JSON orchestration instructions optimized for documentation analysis.
""",
            
            "contextual_enhancement": """
Based on retrieved contextual memories, enhance the analysis and generate follow-up orchestration.

Original analysis:
{original_analysis}

Retrieved contextual memories:
{contextual_memories}

Generate enhanced orchestration that leverages contextual insights for deeper analysis.
Return JSON format with additional orchestration steps.
"""
        }
    
    def get_template(self, template_name: str) -> str:
        """Récupère un template de prompt."""
        return self.templates.get(template_name, self.templates["master_orchestration"])
    
    def select_optimal_template(self, content: str, file_path: str) -> str:
        """Sélectionne le template optimal selon le contexte."""
        
        ext = Path(file_path).suffix.lower()
        
        # Templates spécialisés par type
        if ext in ['.py', '.js', '.ts', '.rs', '.go', '.java', '.cpp']:
            return self.get_template("code_orchestration")
        elif ext in ['.md', '.rst', '.txt', '.adoc']:
            return self.get_template("documentation_orchestration")
        else:
            return self.get_template("master_orchestration")


class IntelligentOrchestrator:
    """Orchestrateur intelligent basé sur les prompts."""
    
    def __init__(self, message_bus: MessageBus, ai_analyzer: OpenAIAnalyzer):
        self.message_bus = message_bus
        self.ai_analyzer = ai_analyzer
        self.prompt_manager = PromptTemplateManager()
        self.dynamic_prompt_system = LuciformDynamicPromptSystem()
        self.orchestration_history = []

        print("🎭 IntelligentOrchestrator initialized with dynamic injections")
    
    async def orchestrate_analysis(self, file_path: str, content: str) -> OrchestrationResult:
        """Orchestration intelligente complète."""
        
        start_time = time.time()
        
        try:
            print(f"🎭 Starting intelligent orchestration for {Path(file_path).name}")
            
            # 1. Génération des instructions d'orchestration
            orchestration_instructions = await self._generate_orchestration_instructions(
                file_path, content
            )
            
            print(f"🎭 Generated orchestration with {len(orchestration_instructions.get('orchestration_instructions', {}).get('components', []))} components")
            
            # 2. Exécution des instructions
            execution_results = await self._execute_orchestration(orchestration_instructions)
            
            # 3. Analyse contextuelle récursive (si applicable)
            enhancement_applied = False
            if self._should_enhance_with_context(execution_results):
                enhanced_results = await self._enhance_with_context(
                    orchestration_instructions, execution_results
                )
                execution_results.update(enhanced_results)
                enhancement_applied = True
            
            processing_time = time.time() - start_time
            
            result = OrchestrationResult(
                original_instructions=orchestration_instructions,
                execution_results=execution_results,
                orchestration_success=True,
                total_components_executed=len(execution_results),
                processing_time=processing_time,
                enhancement_applied=enhancement_applied
            )
            
            # Historique pour apprentissage
            self._record_orchestration(file_path, result)
            
            print(f"🎭 Orchestration completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"🎭 Orchestration failed: {e}")
            
            return OrchestrationResult(
                original_instructions={},
                execution_results={"error": str(e)},
                orchestration_success=False,
                total_components_executed=0,
                processing_time=processing_time
            )
    
    async def _generate_orchestration_instructions(self, file_path: str, 
                                                 content: str) -> Dict[str, Any]:
        """Génère les instructions d'orchestration via IA."""
        
        # Préparation du contexte
        context = {
            "content": content[:3000],  # Limite pour le prompt
            "file_path": file_path,
            "content_size": len(content),
            "file_extension": Path(file_path).suffix,
            "language": self._detect_language(file_path),
            "doc_type": self._detect_doc_type(file_path)
        }
        
        # Sélection du prompt optimal
        template = self.prompt_manager.select_optimal_template(content, file_path)
        formatted_prompt = template.format(**context)
        
        try:
            # Analyse IA pour générer les instructions
            print("🎭 Generating orchestration instructions via AI...")
            ai_response = await self.ai_analyzer.analyze_content(
                formatted_prompt, 
                file_path
            )
            
            # Parsing de la réponse JSON
            instructions_text = ai_response.summary
            
            # Extraction du JSON de la réponse (méthodes multiples)
            instructions = self._extract_json_from_response(instructions_text)
            if instructions:
                return instructions
            else:
                raise ValueError("No valid JSON found in AI response")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"🎭 Failed to parse AI instructions: {e}")
            # Fallback vers instructions par défaut
            return self._generate_fallback_instructions(content, file_path)
    
    async def _execute_orchestration(self, instructions: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute les instructions d'orchestration."""
        
        components = instructions.get("orchestration_instructions", {}).get("components", [])
        results = {}
        
        print(f"🎭 Executing {len(components)} orchestration components")
        
        # Exécution séquentielle (parallèle à implémenter plus tard)
        for i, component in enumerate(components):
            try:
                print(f"🎭 Executing component {i+1}/{len(components)}: {component['adapter']}.{component['method']}")
                
                result = await self._execute_component(component, results)
                results[f"{component['adapter']}_{i}"] = result
                
                # Délai entre composants pour éviter la surcharge
                if i < len(components) - 1:
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                print(f"🎭 Component {component['adapter']} failed: {e}")
                results[f"{component['adapter']}_{i}"] = {"error": str(e)}
        
        return results
    
    async def _execute_component(self, component: Dict[str, Any], 
                               previous_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """Exécute un composant selon les instructions."""
        
        adapter = component["adapter"]
        method = component["method"]
        params = component.get("params", {})
        timeout = component.get("timeout", 30)
        
        # Injection des résultats précédents si nécessaire
        if previous_results and component.get("depends_on"):
            for dependency in component["depends_on"]:
                matching_results = [k for k in previous_results.keys() if dependency in k]
                if matching_results:
                    params[f"{dependency}_result"] = previous_results[matching_results[0]]
        
        # Appel via MessageBus
        try:
            result = await self.message_bus.send_request(
                adapter, method, params, timeout=timeout
            )
            return result
        except ProtocolError as e:
            return {"error": f"Component execution failed: {e}"}
    
    def _should_enhance_with_context(self, execution_results: Dict[str, Any]) -> bool:
        """Détermine si une amélioration contextuelle est nécessaire."""
        
        # Recherche de résultats de memory_engine
        memory_results = [v for k, v in execution_results.items() if "memory_engine" in k]
        
        # Si des mémoires contextuelles ont été trouvées
        for result in memory_results:
            if isinstance(result, dict) and "contextual_memories" in result:
                if len(result["contextual_memories"]) > 0:
                    return True
        
        return False
    
    async def _enhance_with_context(self, original_instructions: Dict[str, Any],
                                  execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Amélioration contextuelle récursive."""
        
        print("🎭 Applying contextual enhancement...")
        
        # Extraction des mémoires contextuelles
        contextual_memories = []
        for result in execution_results.values():
            if isinstance(result, dict) and "contextual_memories" in result:
                contextual_memories.extend(result["contextual_memories"][:3])
        
        if not contextual_memories:
            return {}
        
        # Génération d'instructions d'amélioration
        enhancement_context = {
            "original_analysis": json.dumps(original_instructions, indent=2),
            "contextual_memories": json.dumps(contextual_memories, indent=2)
        }
        
        enhancement_template = self.prompt_manager.get_template("contextual_enhancement")
        enhancement_prompt = enhancement_template.format(**enhancement_context)
        
        try:
            # Analyse d'amélioration
            enhancement_response = await self.ai_analyzer.analyze_content(
                enhancement_prompt,
                "contextual_enhancement"
            )
            
            # Parsing des instructions d'amélioration
            enhancement_text = enhancement_response.summary
            json_start = enhancement_text.find('{')
            json_end = enhancement_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = enhancement_text[json_start:json_end]
                enhancement_instructions = json.loads(json_text)
                
                # Exécution des améliorations
                enhancement_results = await self._execute_orchestration(enhancement_instructions)
                
                return {"contextual_enhancement": enhancement_results}
            
        except Exception as e:
            print(f"🎭 Contextual enhancement failed: {e}")
            return {"contextual_enhancement": {"error": str(e)}}
        
        return {}
    
    def _generate_fallback_instructions(self, content: str, file_path: str) -> Dict[str, Any]:
        """Génère des instructions de fallback."""
        
        ext = Path(file_path).suffix.lower()
        
        # Instructions basiques selon le type
        if ext in ['.py', '.js', '.ts', '.rs', '.go']:
            content_type = "code"
            partitioning_method = "regex_partition"
        elif ext in ['.md', '.rst', '.txt']:
            content_type = "documentation"
            partitioning_method = "textual_partition"
        else:
            content_type = "mixed"
            partitioning_method = "adaptive_partition"
        
        return {
            "analysis": {
                "content_type": content_type,
                "complexity": "medium",
                "domain": "general",
                "confidence": 0.5
            },
            "orchestration_instructions": {
                "priority": "medium",
                "parallel_execution": False,
                "components": [
                    {
                        "adapter": "content_detector",
                        "method": "detect_content_type",
                        "params": {
                            "file_path": file_path,
                            "content": content,
                            "options": {"include_characteristics": True}
                        },
                        "timeout": 15
                    },
                    {
                        "adapter": "ai_analyzer",
                        "method": "analyze_content",
                        "params": {
                            "content": content,
                            "file_path": file_path
                        },
                        "timeout": 30
                    }
                ]
            }
        }
    
    def _detect_language(self, file_path: str) -> str:
        """Détecte le langage de programmation."""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.rs': 'rust', '.go': 'go', '.java': 'java', '.cpp': 'cpp'
        }
        return language_map.get(ext, 'unknown')
    
    def _detect_doc_type(self, file_path: str) -> str:
        """Détecte le type de document."""
        ext = Path(file_path).suffix.lower()
        doc_map = {
            '.md': 'markdown', '.rst': 'restructuredtext', 
            '.txt': 'plaintext', '.adoc': 'asciidoc'
        }
        return doc_map.get(ext, 'unknown')
    
    def _record_orchestration(self, file_path: str, result: OrchestrationResult):
        """Enregistre l'orchestration pour apprentissage."""
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "success": result.orchestration_success,
            "processing_time": result.processing_time,
            "components_executed": result.total_components_executed,
            "enhancement_applied": result.enhancement_applied
        }
        
        self.orchestration_history.append(record)
        
        # Limite l'historique
        if len(self.orchestration_history) > 100:
            self.orchestration_history = self.orchestration_history[-50:]

    def _extract_json_from_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extrait le JSON de la réponse IA avec plusieurs méthodes."""

        # Méthode 1: Recherche de blocs JSON complets
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        if json_start >= 0 and json_end > json_start:
            try:
                json_text = response_text[json_start:json_end]
                return json.loads(json_text)
            except json.JSONDecodeError:
                pass

        # Méthode 2: Recherche de blocs de code JSON
        import re
        json_blocks = re.findall(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        for block in json_blocks:
            try:
                return json.loads(block)
            except json.JSONDecodeError:
                continue

        # Méthode 3: Recherche de structures JSON partielles
        json_patterns = [
            r'\{[^{}]*"analysis"[^{}]*\}',
            r'\{[^{}]*"orchestration_instructions"[^{}]*\}',
            r'\{.*?"components".*?\}',
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue

        # Méthode 4: Construction JSON à partir de mots-clés
        if "content_type" in response_text and "orchestration" in response_text:
            return self._construct_json_from_keywords(response_text)

        return None

    def _construct_json_from_keywords(self, response_text: str) -> Dict[str, Any]:
        """Construit un JSON basique à partir de mots-clés détectés."""

        # Détection de type de contenu
        content_type = "mixed"
        if "code" in response_text.lower():
            content_type = "code"
        elif "documentation" in response_text.lower():
            content_type = "documentation"

        # Détection de complexité
        complexity = "medium"
        if "high" in response_text.lower() and "complex" in response_text.lower():
            complexity = "high"
        elif "low" in response_text.lower() and "simple" in response_text.lower():
            complexity = "low"

        # Construction JSON basique
        return {
            "analysis": {
                "content_type": content_type,
                "complexity": complexity,
                "domain": "general",
                "confidence": 0.6
            },
            "orchestration_instructions": {
                "priority": "medium",
                "parallel_execution": False,
                "components": [
                    {
                        "adapter": "content_detector",
                        "method": "detect_content_type",
                        "params": {"include_characteristics": True},
                        "timeout": 15
                    },
                    {
                        "adapter": "ai_analyzer",
                        "method": "analyze_content",
                        "params": {},
                        "timeout": 30
                    }
                ]
            }
        }
    
    def get_orchestration_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'orchestration."""
        
        if not self.orchestration_history:
            return {"total_orchestrations": 0}
        
        total = len(self.orchestration_history)
        successful = sum(1 for r in self.orchestration_history if r["success"])
        avg_time = sum(r["processing_time"] for r in self.orchestration_history) / total
        avg_components = sum(r["components_executed"] for r in self.orchestration_history) / total
        
        return {
            "total_orchestrations": total,
            "success_rate": successful / total,
            "average_processing_time": avg_time,
            "average_components_per_orchestration": avg_components,
            "enhancement_usage_rate": sum(1 for r in self.orchestration_history if r["enhancement_applied"]) / total
        }


async def test_intelligent_orchestrator():
    """Test de l'orchestrateur intelligent."""
    
    print("🎭 Testing Intelligent Orchestrator...")
    
    # Imports pour test
    from message_bus import MessageBus
    from openai_analyzer import OpenAIAnalyzer
    
    # Création des composants
    bus = MessageBus()
    await bus.start()
    
    analyzer = OpenAIAnalyzer(force_ollama=True)
    orchestrator = IntelligentOrchestrator(bus, analyzer)
    
    # Test content
    test_content = """
# Architecture Document

This document describes our microservices architecture.

## Components
- API Gateway: Routes requests to appropriate services
- User Service: Handles authentication and user management
- Payment Service: Processes payments and billing

## Code Example
```python
class UserService:
    def authenticate(self, token):
        return validate_jwt(token)
    
    def get_user_profile(self, user_id):
        return self.db.get_user(user_id)
```

The architecture follows domain-driven design principles.
"""
    
    # Test d'orchestration
    try:
        result = await orchestrator.orchestrate_analysis("architecture.md", test_content)
        
        print(f"\n🎭 Orchestration Results:")
        print(f"  ✅ Success: {result.orchestration_success}")
        print(f"  ⏱️ Processing time: {result.processing_time:.2f}s")
        print(f"  🔧 Components executed: {result.total_components_executed}")
        print(f"  🧠 Enhancement applied: {result.enhancement_applied}")
        
        # Statistiques
        stats = orchestrator.get_orchestration_stats()
        print(f"\n📊 Orchestration Stats:")
        print(f"  📈 Success rate: {stats['success_rate']:.2f}")
        print(f"  ⏱️ Average time: {stats['average_processing_time']:.2f}s")
        
    except Exception as e:
        print(f"🎭 Test failed: {e}")
    
    await bus.stop()


if __name__ == "__main__":
    asyncio.run(test_intelligent_orchestrator())
