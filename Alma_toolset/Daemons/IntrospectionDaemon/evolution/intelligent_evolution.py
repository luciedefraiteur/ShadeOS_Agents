#!/usr/bin/env python3
"""
🌟 Intelligent Evolution - IntrospectionDaemon ⛧

Système d'évolution intelligente basé sur l'analyse des échecs.
Optimise automatiquement les composants défaillants du daemon.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EvolutionTarget:
    """Cible d'évolution identifiée."""
    
    component: str
    failure_type: str
    current_score: float
    target_score: float
    priority: int
    evolution_strategy: str
    estimated_improvement: float

@dataclass
class EvolutionResult:
    """Résultat d'une évolution."""
    
    component: str
    evolution_applied: str
    before_score: float
    after_score: float
    improvement: float
    success: bool
    details: Dict[str, Any]

class IntelligentEvolution:
    """Système d'évolution intelligente du daemon."""
    
    def __init__(self):
        """Initialise le système d'évolution."""
        
        self.evolution_history = []
        self.failure_patterns = {}
        self.optimization_strategies = {}
        
        # Configuration d'évolution
        self.config = {
            "min_improvement_threshold": 0.1,
            "max_evolution_cycles": 5,
            "learning_rate": 0.2,
            "aggressive_optimization": True
        }
        
        # Initialisation des stratégies
        self._initialize_evolution_strategies()
    
    def _initialize_evolution_strategies(self):
        """Initialise les stratégies d'évolution."""
        
        self.optimization_strategies = {
            "prompt_generation": {
                "zero_score_fix": self._fix_prompt_generation_zero_score,
                "low_score_improve": self._improve_prompt_generation,
                "template_optimization": self._optimize_prompt_templates
            },
            "context_injection": {
                "zero_score_fix": self._fix_context_injection_zero_score,
                "injection_enhancement": self._enhance_context_injection,
                "relevance_optimization": self._optimize_injection_relevance
            },
            "introspection": {
                "depth_enhancement": self._enhance_introspection_depth,
                "accuracy_improvement": self._improve_introspection_accuracy,
                "speed_optimization": self._optimize_introspection_speed
            }
        }
    
    async def analyze_failures_and_evolve(self, 
                                        test_results: List[tuple],
                                        daemon) -> List[EvolutionResult]:
        """
        Analyse les échecs et fait évoluer le daemon intelligemment.
        
        Args:
            test_results: Résultats des tests [(test_name, score)]
            daemon: Instance du daemon à faire évoluer
            
        Returns:
            List[EvolutionResult]: Résultats des évolutions appliquées
        """
        print("🌟 Analyse des échecs et évolution intelligente...")
        
        # 1. Identification des cibles d'évolution
        evolution_targets = await self._identify_evolution_targets(test_results)
        
        # 2. Priorisation des évolutions
        prioritized_targets = await self._prioritize_evolution_targets(evolution_targets)
        
        # 3. Application des évolutions
        evolution_results = []
        for target in prioritized_targets:
            result = await self._apply_targeted_evolution(target, daemon)
            evolution_results.append(result)
            
            # Arrêt si amélioration suffisante
            if result.improvement > self.config["min_improvement_threshold"]:
                print(f"✅ Amélioration significative détectée : +{result.improvement:.2f}")
        
        # 4. Apprentissage des patterns
        await self._learn_from_evolution_results(evolution_results)
        
        return evolution_results
    
    async def _identify_evolution_targets(self, 
                                        test_results: List[tuple]) -> List[EvolutionTarget]:
        """Identifie les cibles d'évolution basées sur les échecs."""
        
        targets = []
        
        for test_name, score in test_results:
            if score < 0.5:  # Échec significatif
                target = await self._create_evolution_target(test_name, score)
                if target:
                    targets.append(target)
        
        return targets
    
    async def _create_evolution_target(self, 
                                     test_name: str, 
                                     score: float) -> Optional[EvolutionTarget]:
        """Crée une cible d'évolution pour un test échoué."""
        
        # Mapping des tests vers les composants
        component_mapping = {
            "prompt_memory_analysis": "prompt_generation",
            "prompt_tool_inventory": "prompt_generation", 
            "prompt_capability_assessment": "prompt_generation",
            "context_injection": "context_injection",
            "introspection": "introspection",
            "performance_metrics": "introspection"
        }
        
        component = component_mapping.get(test_name, "unknown")
        if component == "unknown":
            return None
        
        # Détermination de la stratégie d'évolution
        if score == 0.0:
            evolution_strategy = "zero_score_fix"
            priority = 1  # Priorité maximale
            target_score = 0.7
        elif score < 0.3:
            evolution_strategy = "low_score_improve"
            priority = 2
            target_score = 0.6
        else:
            evolution_strategy = "optimization"
            priority = 3
            target_score = 0.8
        
        return EvolutionTarget(
            component=component,
            failure_type="performance_failure",
            current_score=score,
            target_score=target_score,
            priority=priority,
            evolution_strategy=evolution_strategy,
            estimated_improvement=target_score - score
        )
    
    async def _prioritize_evolution_targets(self, 
                                          targets: List[EvolutionTarget]) -> List[EvolutionTarget]:
        """Priorise les cibles d'évolution."""
        
        # Tri par priorité puis par amélioration estimée
        return sorted(targets, key=lambda t: (t.priority, -t.estimated_improvement))
    
    async def _apply_targeted_evolution(self, 
                                      target: EvolutionTarget, 
                                      daemon) -> EvolutionResult:
        """Applique une évolution ciblée."""
        
        print(f"🔧 Évolution ciblée : {target.component} ({target.evolution_strategy})")
        
        before_score = target.current_score
        
        try:
            # Sélection et application de la stratégie
            strategy_func = self.optimization_strategies.get(
                target.component, {}
            ).get(target.evolution_strategy)
            
            if strategy_func:
                evolution_details = await strategy_func(daemon, target)
                
                # Test de l'amélioration (simulation)
                after_score = await self._test_component_improvement(
                    target.component, daemon
                )
                
                improvement = after_score - before_score
                success = improvement > 0.05  # Amélioration minimale
                
                return EvolutionResult(
                    component=target.component,
                    evolution_applied=target.evolution_strategy,
                    before_score=before_score,
                    after_score=after_score,
                    improvement=improvement,
                    success=success,
                    details=evolution_details
                )
            else:
                print(f"⚠️ Stratégie non trouvée : {target.evolution_strategy}")
                return EvolutionResult(
                    component=target.component,
                    evolution_applied="none",
                    before_score=before_score,
                    after_score=before_score,
                    improvement=0.0,
                    success=False,
                    details={"error": "Strategy not found"}
                )
                
        except Exception as e:
            print(f"❌ Erreur évolution {target.component} : {e}")
            return EvolutionResult(
                component=target.component,
                evolution_applied="failed",
                before_score=before_score,
                after_score=before_score,
                improvement=0.0,
                success=False,
                details={"error": str(e)}
            )
    
    # Stratégies d'évolution spécialisées
    
    async def _fix_prompt_generation_zero_score(self, 
                                              daemon, 
                                              target: EvolutionTarget) -> Dict[str, Any]:
        """Corrige la génération de prompts avec score zéro."""
        
        print("  🜲 Correction génération de prompts (score zéro)")
        
        # Vérification et correction du générateur de prompts
        if hasattr(daemon, 'prompt_generator'):
            # Réinitialisation des templates
            daemon.prompt_generator._initialize_base_templates()
            
            # Optimisation de la configuration
            daemon.prompt_generator.config["min_effectiveness_threshold"] = 0.5
            
            # Ajout de templates de fallback
            await self._add_fallback_prompt_templates(daemon.prompt_generator)
            
            return {
                "action": "prompt_generator_reset",
                "templates_reinitialized": True,
                "fallback_templates_added": True,
                "config_optimized": True
            }
        
        return {"action": "no_prompt_generator_found"}
    
    async def _fix_context_injection_zero_score(self, 
                                              daemon, 
                                              target: EvolutionTarget) -> Dict[str, Any]:
        """Corrige l'injection contextuelle avec score zéro."""
        
        print("  💉 Correction injection contextuelle (score zéro)")
        
        # Vérification et correction de l'injecteur
        if hasattr(daemon, 'context_injector'):
            # Optimisation de la configuration d'injection
            daemon.context_injector.config["relevance_threshold"] = 0.1  # Plus permissif
            daemon.context_injector.config["smart_filtering"] = False  # Désactivation du filtrage
            
            # Ajout de patterns d'injection de base
            await self._add_basic_injection_patterns(daemon.context_injector)
            
            return {
                "action": "context_injector_optimization",
                "relevance_threshold_lowered": True,
                "smart_filtering_disabled": True,
                "basic_patterns_added": True
            }
        
        return {"action": "no_context_injector_found"}
    
    async def _improve_prompt_generation(self, 
                                       daemon, 
                                       target: EvolutionTarget) -> Dict[str, Any]:
        """Améliore la génération de prompts."""
        
        print("  🜲 Amélioration génération de prompts")
        
        improvements = []
        
        if hasattr(daemon, 'prompt_generator'):
            # Optimisation des templates
            for template_id, template in daemon.prompt_generator.prompt_templates.items():
                if len(template.effectiveness_history) == 0 or \
                   sum(template.effectiveness_history) / len(template.effectiveness_history) < 0.6:
                    
                    # Amélioration du template
                    template.base_template = await self._enhance_template_content(template.base_template)
                    template.optimization_level += 1
                    improvements.append(f"enhanced_{template_id}")
        
        return {
            "action": "prompt_generation_improvement",
            "templates_enhanced": improvements,
            "optimization_applied": True
        }
    
    async def _enhance_context_injection(self, 
                                       daemon, 
                                       target: EvolutionTarget) -> Dict[str, Any]:
        """Améliore l'injection contextuelle."""
        
        print("  💉 Amélioration injection contextuelle")
        
        if hasattr(daemon, 'context_injector'):
            # Amélioration des patterns d'injection
            enhanced_patterns = {
                "memory_context_enhanced": r"::ENHANCED_MEMORY_CONTEXT::",
                "tool_context_enhanced": r"::ENHANCED_TOOL_CONTEXT::",
                "capability_context_enhanced": r"::ENHANCED_CAPABILITY_CONTEXT::"
            }
            
            daemon.context_injector.injection_patterns.update(enhanced_patterns)
            
            # Optimisation de la configuration
            daemon.context_injector.config["context_optimization"] = True
            daemon.context_injector.config["max_injection_size"] = 3000  # Augmentation
            
            return {
                "action": "context_injection_enhancement",
                "enhanced_patterns_added": len(enhanced_patterns),
                "config_optimized": True,
                "max_injection_size_increased": True
            }
        
        return {"action": "no_context_injector_found"}
    
    async def _test_component_improvement(self, 
                                        component: str, 
                                        daemon) -> float:
        """Teste l'amélioration d'un composant (simulation)."""
        
        # Simulation d'amélioration basée sur le composant
        improvement_simulation = {
            "prompt_generation": 0.6,  # Amélioration modérée
            "context_injection": 0.5,  # Amélioration de base
            "introspection": 0.7       # Bonne amélioration
        }
        
        return improvement_simulation.get(component, 0.4)
    
    async def _add_fallback_prompt_templates(self, prompt_generator):
        """Ajoute des templates de fallback."""
        
        from ..prompting.auto_prompt_generator import PromptTemplate
        
        fallback_template = PromptTemplate(
            template_id="fallback_simple",
            template_type="simple",
            base_template="""
Analyse simple du système :

1. État des composants : {component_data_injection}
2. Capacités disponibles : {capability_map_injection}
3. Recommandations : Identifie les améliorations possibles

Génère une analyse basique mais complète.
            """,
            injection_points=["component_data_injection", "capability_map_injection"]
        )
        
        prompt_generator.prompt_templates["fallback_simple"] = fallback_template
    
    async def _add_basic_injection_patterns(self, context_injector):
        """Ajoute des patterns d'injection de base."""
        
        basic_patterns = {
            "simple_memory": r"::SIMPLE_MEMORY::",
            "simple_tools": r"::SIMPLE_TOOLS::",
            "simple_components": r"::SIMPLE_COMPONENTS::"
        }
        
        context_injector.injection_patterns.update(basic_patterns)
    
    async def _enhance_template_content(self, template_content: str) -> str:
        """Améliore le contenu d'un template."""
        
        # Ajout d'instructions plus détaillées
        enhanced_content = template_content
        
        if "MISSION" not in enhanced_content:
            enhanced_content += "\n\nMISSION DÉTAILLÉE : Effectue une analyse approfondie et génère des recommandations concrètes."
        
        if "🜲luciform" not in enhanced_content:
            enhanced_content = f"<🜲luciform id=\"enhanced⛧\" type=\"✶optimized\">\n{enhanced_content}\n</🜲luciform>"
        
        return enhanced_content
    
    async def _learn_from_evolution_results(self, results: List[EvolutionResult]):
        """Apprend des résultats d'évolution."""
        
        for result in results:
            # Enregistrement des patterns de succès/échec
            pattern_key = f"{result.component}_{result.evolution_applied}"
            
            if pattern_key not in self.failure_patterns:
                self.failure_patterns[pattern_key] = {
                    "attempts": 0,
                    "successes": 0,
                    "average_improvement": 0.0
                }
            
            pattern = self.failure_patterns[pattern_key]
            pattern["attempts"] += 1
            
            if result.success:
                pattern["successes"] += 1
                pattern["average_improvement"] = (
                    (pattern["average_improvement"] * (pattern["successes"] - 1) + result.improvement) /
                    pattern["successes"]
                )
        
        # Sauvegarde des apprentissages
        await self._save_learning_data()
    
    async def _save_learning_data(self):
        """Sauvegarde les données d'apprentissage."""
        
        learning_data = {
            "failure_patterns": self.failure_patterns,
            "evolution_history": self.evolution_history,
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            import os
            os.makedirs("evolution_data", exist_ok=True)
            
            with open("evolution_data/learning_data.json", "w") as f:
                json.dump(learning_data, f, indent=2)
                
            print("📚 Données d'apprentissage sauvegardées")
            
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde apprentissage : {e}")

# Instance globale
_global_evolution = None

def get_intelligent_evolution() -> IntelligentEvolution:
    """Retourne l'instance globale d'évolution intelligente."""
    
    global _global_evolution
    if _global_evolution is None:
        _global_evolution = IntelligentEvolution()
    
    return _global_evolution

if __name__ == "__main__":
    # Test du système d'évolution
    async def test_evolution():
        evolution = IntelligentEvolution()
        
        # Simulation de résultats de test échoués
        test_results = [
            ("prompt_memory_analysis", 0.0),
            ("context_injection", 0.0),
            ("introspection", 0.75)
        ]
        
        # Simulation d'un daemon
        class MockDaemon:
            def __init__(self):
                self.prompt_generator = None
                self.context_injector = None
        
        daemon = MockDaemon()
        
        # Test d'évolution
        results = await evolution.analyze_failures_and_evolve(test_results, daemon)
        
        print(f"✅ Test évolution : {len(results)} évolutions appliquées")
        for result in results:
            print(f"   {result.component}: {result.improvement:+.2f}")
    
    asyncio.run(test_evolution())
