#!/usr/bin/env python3
"""
⛧ Moteur de Réflexion Autonome - Archiviste ⛧
Système de boucles de réflexion avec auto-injection de contexte
"""

import json
import time
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field

from .memory_registry import MemoryRegistry, initialize_memory_registry


@dataclass
class ReflectionCycle:
    """Un cycle de réflexion de l'Archiviste"""
    cycle_id: str
    iteration: int
    query: str
    current_understanding: Dict[str, Any]
    context_injected: List[Dict[str, Any]] = field(default_factory=list)
    memory_explorations: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0
    is_satisfactory: bool = False
    timestamp: float = field(default_factory=time.time)


class ReflectionEngine:
    """Moteur de réflexion autonome pour l'Archiviste"""
    
    def __init__(self, memory_engine, model: str = "qwen2.5:7b-instruct", max_cycles: int = 5, debug: bool = True):
        self.memory_engine = memory_engine
        self.model = model
        self.max_cycles = max_cycles
        self.timeout = 30
        self.debug = debug
        
        # Initialiser le MemoryRegistry
        self.memory_registry = initialize_memory_registry(memory_engine)
        
        # Charger les prompts
        self.prompts = self._load_prompts()
        
        # Historique des cycles
        self.reflection_history: List[ReflectionCycle] = []
        
    def _load_prompts(self) -> Dict[str, str]:
        """Charge tous les prompts nécessaires"""
        prompts_dir = Path(__file__).parent / "prompts"
        prompts = {}
        
        prompt_files = [
            "initial_analysis.luciform",
            "context_exploration.luciform", 
            "context_injection.luciform",
            "satisfaction_evaluation.luciform",
            "final_synthesis.luciform"
        ]
        
        for prompt_file in prompt_files:
            try:
                with open(prompts_dir / prompt_file, 'r', encoding='utf-8') as f:
                    prompts[prompt_file.replace('.luciform', '')] = f.read()
            except FileNotFoundError:
                print(f"⚠️ Prompt non trouvé: {prompt_file}")
                prompts[prompt_file.replace('.luciform', '')] = f"# {prompt_file}"
        
        return prompts
    
    def process_query_with_reflection(self, query: str, sender: str = "alma") -> str:
        """
        Traite une requête avec des cycles de réflexion autonomes
        """
        print(f"🔄 Début du traitement réflexif pour: {query[:50]}...")
        
        # Cycle initial
        current_cycle = ReflectionCycle(
            cycle_id=f"cycle_{int(time.time())}",
            iteration=0,
            query=query,
            current_understanding={}
        )
        
        # Boucle de réflexion
        for iteration in range(self.max_cycles):
            current_cycle.iteration = iteration
            print(f"🔄 Cycle {iteration + 1}/{self.max_cycles}")
            
            # 1. Analyse initiale ou ré-analyse
            if iteration == 0:
                understanding = self._initial_analysis(query)
            else:
                understanding = self._re_analyze_with_context(current_cycle)
            
            current_cycle.current_understanding = understanding
            
            # 2. Évaluation de satisfaction
            satisfaction = self._evaluate_satisfaction(current_cycle)
            current_cycle.confidence_score = satisfaction.get("confidence", 0.0)
            current_cycle.is_satisfactory = satisfaction.get("is_satisfactory", False)
            
            print(f"📊 Confiance: {current_cycle.confidence_score:.2f} - Satisfaisant: {current_cycle.is_satisfactory}")
            
            # 3. Si satisfaisant, sortir de la boucle
            if current_cycle.is_satisfactory:
                print(f"✅ Réponse satisfaisante atteinte au cycle {iteration + 1}")
                break
            
            # 4. Exploration de contexte pour améliorer
            if iteration < self.max_cycles - 1:
                context_data = self._explore_relevant_context(current_cycle)
                current_cycle.context_injected.append(context_data)
                current_cycle.memory_explorations.append(context_data)
                print(f"🔍 Contexte injecté: {len(context_data.get('results', []))} éléments")
            
            # 5. Sauvegarder le cycle
            self.reflection_history.append(current_cycle)
        
        # Génération de la réponse finale
        final_response = self._generate_final_response(current_cycle)
        
        print(f"🎯 Traitement réflexif terminé en {len(self.reflection_history)} cycles")
        return final_response
    
    def _initial_analysis(self, query: str) -> Dict[str, Any]:
        """Analyse initiale de la requête avec injection du MemoryRegistry"""
        
        # Injecter le contexte mémoire
        memory_context = self.memory_registry.format_for_prompt_injection()
        
        prompt = f"""{self.prompts.get('initial_analysis', '')}

{memory_context}

**REQUÊTE À ANALYSER :**
{query}

**TÂCHE :** Analyse cette requête et détermine :
1. L'intention principale
2. Le type de mémoire concerné
3. Les paramètres nécessaires
4. Le niveau de complexité

**RÉPONSE EN JSON :**
{{
  "intention": "description|search|explore|store|general",
  "memory_type": "fractal|temporal|user_requests|discussion|all",
  "complexity": "simple|medium|complex",
  "parameters_needed": ["param1", "param2"],
  "confidence": 0.75,
  "missing_context": ["contexte1", "contexte2"]
}}"""

        if self.debug:
            print(f"\n🔍 PROMPT ANALYSE INITIALE:")
            print("=" * 50)
            print(prompt)
            print("=" * 50)

        response = self._call_ai(prompt)
        
        if self.debug:
            print(f"\n🤖 RÉPONSE ANALYSE INITIALE:")
            print("=" * 50)
            print(response)
            print("=" * 50)
        
        return self._extract_json(response) or {"intention": "general", "confidence": 0.5}
    
    def _re_analyze_with_context(self, cycle: ReflectionCycle) -> Dict[str, Any]:
        """Ré-analyse avec le contexte injecté"""
        context_summary = self._summarize_injected_context(cycle.context_injected)
        
        # Injecter le contexte mémoire spécifique
        memory_context = self.memory_registry.get_context_for_query(
            cycle.current_understanding.get("intention", "general"),
            cycle.current_understanding.get("memory_type")
        )
        
        prompt = f"""{self.prompts.get('context_injection', '')}

{memory_context}

**REQUÊTE ORIGINALE :**
{cycle.query}

**CONTEXTE INJECTÉ :**
{context_summary}

**COMPRÉHENSION ACTUELLE :**
{json.dumps(cycle.current_understanding, indent=2)}

**TÂCHE :** Ré-analyse la requête avec ce nouveau contexte et améliore la compréhension.

**RÉPONSE EN JSON :**
{{
  "intention": "description|search|explore|store|general",
  "memory_type": "fractal|temporal|user_requests|discussion|all",
  "complexity": "simple|medium|complex",
  "parameters_needed": ["param1", "param2"],
  "confidence": 0.85,
  "context_used": ["contexte1", "contexte2"],
  "improvements": ["amélioration1", "amélioration2"]
}}"""

        if self.debug:
            print(f"\n🔍 PROMPT RÉ-ANALYSE (Cycle {cycle.iteration + 1}):")
            print("=" * 50)
            print(prompt)
            print("=" * 50)

        response = self._call_ai(prompt)
        
        if self.debug:
            print(f"\n🤖 RÉPONSE RÉ-ANALYSE (Cycle {cycle.iteration + 1}):")
            print("=" * 50)
            print(response)
            print("=" * 50)
        
        return self._extract_json(response) or cycle.current_understanding
    
    def _explore_relevant_context(self, cycle: ReflectionCycle) -> Dict[str, Any]:
        """Explore la mémoire pour trouver du contexte pertinent"""
        understanding = cycle.current_understanding
        
        # Injecter le contexte mémoire pour l'exploration
        memory_context = self.memory_registry.format_for_prompt_injection()
        
        # Déterminer quoi explorer basé sur la compréhension actuelle
        exploration_prompt = f"""{self.prompts.get('context_exploration', '')}

{memory_context}

**REQUÊTE :** {cycle.query}
**COMPRÉHENSION ACTUELLE :** {json.dumps(understanding, indent=2)}
**CONTEXTE DÉJÀ INJECTÉ :** {len(cycle.context_injected)} éléments

**TÂCHE :** Détermine quels éléments de mémoire explorer pour améliorer la compréhension.

**RÉPONSE EN JSON :**
{{
  "exploration_targets": [
    {{
      "memory_type": "fractal|temporal|user_requests|discussion",
      "search_terms": ["terme1", "terme2"],
      "reason": "pourquoi explorer cela"
    }}
  ],
  "priority": "high|medium|low"
}}"""

        if self.debug:
            print(f"\n🔍 PROMPT EXPLORATION (Cycle {cycle.iteration + 1}):")
            print("=" * 50)
            print(exploration_prompt)
            print("=" * 50)

        exploration_plan = self._call_ai(exploration_prompt)
        
        if self.debug:
            print(f"\n🤖 RÉPONSE EXPLORATION (Cycle {cycle.iteration + 1}):")
            print("=" * 50)
            print(exploration_plan)
            print("=" * 50)
        
        plan_data = self._extract_json(exploration_plan) or {"exploration_targets": []}
        
        # Exécuter l'exploration
        results = []
        for target in plan_data.get("exploration_targets", []):
            memory_type = target.get("memory_type", "fractal")
            search_terms = target.get("search_terms", [])
            
            # Explorer la mémoire selon le type
            if memory_type == "fractal":
                for term in search_terms:
                    try:
                        fractal_results = self.memory_engine.find_memories_by_keyword(term)
                        results.extend(fractal_results[:3])  # Limiter à 3 résultats
                    except Exception as e:
                        print(f"⚠️ Erreur exploration fractal {term}: {e}")
            
            elif memory_type == "temporal":
                # Exploration temporelle
                for term in search_terms:
                    try:
                        temporal_results = self.memory_engine.temporal_index.search_temporal("keywords", term, self.memory_engine)
                        results.extend(temporal_results[:3])
                    except Exception as e:
                        print(f"⚠️ Erreur exploration temporelle {term}: {e}")
        
        return {
            "exploration_plan": plan_data,
            "results": results,
            "timestamp": time.time()
        }
    
    def _evaluate_satisfaction(self, cycle: ReflectionCycle) -> Dict[str, Any]:
        """Évalue si la compréhension actuelle est satisfaisante"""
        
        # Injecter le contexte mémoire
        memory_context = self.memory_registry.get_available_tools_summary()
        
        prompt = f"""{self.prompts.get('satisfaction_evaluation', '')}

{memory_context}

**REQUÊTE :** {cycle.query}
**COMPRÉHENSION ACTUELLE :** {json.dumps(cycle.current_understanding, indent=2)}
**CONTEXTE INJECTÉ :** {len(cycle.context_injected)} éléments
**CYCLE :** {cycle.iteration + 1}/{self.max_cycles}

**TÂCHE :** Évalue si la compréhension actuelle est suffisante pour répondre.

**RÉPONSE EN JSON :**
{{
  "is_satisfactory": true|false,
  "confidence": 0.85,
  "reasoning": "pourquoi satisfaisant ou non",
  "missing_elements": ["élément1", "élément2"],
  "suggested_improvements": ["amélioration1", "amélioration2"]
}}"""

        if self.debug:
            print(f"\n🔍 PROMPT ÉVALUATION (Cycle {cycle.iteration + 1}):")
            print("=" * 50)
            print(prompt)
            print("=" * 50)

        response = self._call_ai(prompt)
        
        if self.debug:
            print(f"\n🤖 RÉPONSE ÉVALUATION (Cycle {cycle.iteration + 1}):")
            print("=" * 50)
            print(response)
            print("=" * 50)
        
        return self._extract_json(response) or {"is_satisfactory": False, "confidence": 0.5}
    
    def _generate_final_response(self, cycle: ReflectionCycle) -> str:
        """Génère la réponse finale basée sur tous les cycles"""
        context_summary = self._summarize_injected_context(cycle.context_injected)
        
        # Injecter le contexte mémoire complet
        memory_context = self.memory_registry.format_for_prompt_injection()
        
        prompt = f"""{self.prompts.get('final_synthesis', '')}

{memory_context}

**REQUÊTE :** {cycle.query}
**COMPRÉHENSION FINALE :** {json.dumps(cycle.current_understanding, indent=2)}
**CONTEXTE TOTAL :** {context_summary}
**CYCLES EFFECTUÉS :** {cycle.iteration + 1}

**TÂCHE :** Génère une réponse complète et naturelle basée sur toute l'analyse.

**FORMAT :** Réponse naturelle + JSON structuré

**JSON REQUIS :**
{{
  "type": "ARCHIVISTE_REFLECTION_RESPONSE",
  "query_type": "describe_memory_types|contextual_search|explore_workspace|store_context|explore_timeline|general_query",
  "confidence": 0.95,
  "cycles_used": {cycle.iteration + 1},
  "context_elements": {len(cycle.context_injected)},
  "results": {{...}},
  "insights": ["insight1", "insight2"]
}}"""

        if self.debug:
            print(f"\n🔍 PROMPT RÉPONSE FINALE:")
            print("=" * 50)
            print(prompt)
            print("=" * 50)

        response = self._call_ai(prompt)
        
        if self.debug:
            print(f"\n🤖 RÉPONSE FINALE:")
            print("=" * 50)
            print(response)
            print("=" * 50)
        
        return response
    
    def _call_ai(self, prompt: str) -> str:
        """Appel à l'IA avec gestion d'erreur"""
        try:
            cmd = ["ollama", "run", self.model, prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"❌ Erreur Ollama: {result.stderr}")
                return ""
                
        except Exception as e:
            print(f"❌ Erreur lors de l'appel IA: {e}")
            return ""
    
    def _extract_json(self, response: str) -> Optional[Dict[str, Any]]:
        """Extrait le JSON de la réponse IA"""
        try:
            # Chercher dans les blocs de code
            json_start = response.find('```json')
            if json_start != -1:
                json_end = response.find('```', json_start + 7)
                if json_end != -1:
                    json_str = response[json_start + 7:json_end].strip()
                    return json.loads(json_str)
            
            # Chercher du JSON direct
            return json.loads(response.strip())
            
        except (json.JSONDecodeError, ValueError):
            return None
    
    def _summarize_injected_context(self, context_list: List[Dict[str, Any]]) -> str:
        """Résume le contexte injecté"""
        if not context_list:
            return "Aucun contexte injecté"
        
        summary = []
        for i, context in enumerate(context_list):
            results = context.get("results", [])
            summary.append(f"Contexte {i+1}: {len(results)} éléments")
        
        return " | ".join(summary)
    
    def get_reflection_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de réflexion"""
        return {
            "total_cycles": len(self.reflection_history),
            "average_cycles_per_query": len(self.reflection_history) / max(1, len(set(c.cycle_id for c in self.reflection_history))),
            "average_confidence": sum(c.confidence_score for c in self.reflection_history) / max(1, len(self.reflection_history)),
            "satisfaction_rate": sum(1 for c in self.reflection_history if c.is_satisfactory) / max(1, len(self.reflection_history))
        }


if __name__ == "__main__":
    # Test du moteur de réflexion
    print("🧪 Test du moteur de réflexion")
    print("=" * 50)
    
    # Simulation d'un memory_engine
    class MockMemoryEngine:
        def find_memories_by_keyword(self, term):
            return [{"path": f"/test/{term}", "content": f"Contenu pour {term}"}]
    
    engine = ReflectionEngine(MockMemoryEngine(), debug=True)
    
    test_queries = [
        "Décris-moi les types de mémoire disponibles",
        "Cherche 'daemon' dans la mémoire",
        "Comment ça va ?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Test: {query}")
        response = engine.process_query_with_reflection(query)
        print(f"📝 Réponse: {response[:100]}...")
        print("-" * 30) 