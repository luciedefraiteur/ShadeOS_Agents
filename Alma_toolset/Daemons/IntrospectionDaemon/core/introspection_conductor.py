#!/usr/bin/env python3
"""
🧠 Introspection Conductor - IntrospectionDaemon ⛧

Chef d'orchestre principal du daemon d'introspection spécialisé.
Coordonne l'auto-analyse, l'auto-prompting et l'évolution adaptative.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class IntrospectionResult:
    """Résultat d'une introspection complète."""
    
    analysis_type: str
    components_analyzed: Dict[str, Any] = field(default_factory=dict)
    capabilities_discovered: Dict[str, Any] = field(default_factory=dict)
    effectiveness_score: float = 0.0
    improvement_suggestions: List[str] = field(default_factory=list)
    evolution_recommendations: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class EffectivenessScore:
    """Score d'efficacité d'une opération."""
    
    overall_score: float
    component_scores: Dict[str, float] = field(default_factory=dict)
    feedback: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    success_factors: List[str] = field(default_factory=list)

class IntrospectionConductor:
    """Chef d'orchestre principal du daemon d'introspection."""
    
    def __init__(self, ecosystem_components: Optional[Dict] = None):
        """
        Initialise le chef d'orchestre d'introspection.
        
        Args:
            ecosystem_components: Composants de l'écosystème à analyser
        """
        self.ecosystem_components = ecosystem_components or {}
        self.introspection_history = []
        self.effectiveness_tracking = {}
        self.evolution_cycles = 0
        
        # Configuration du daemon
        self.config = {
            "introspection_depth": 3,
            "auto_evolution": True,
            "effectiveness_threshold": 0.7,
            "evolution_frequency": 3600,  # 1 heure
            "max_evolution_cycles": 10
        }
        
        # Métriques de performance
        self.performance_metrics = {
            "total_introspections": 0,
            "successful_introspections": 0,
            "average_effectiveness": 0.0,
            "evolution_improvements": 0,
            "last_evolution": None
        }
        
        # Initialisation des composants
        self._initialize_components()

        # Initialisation du logger de prompts
        self._initialize_prompt_logger()
    
    def _initialize_components(self):
        """Initialise les composants du daemon."""
        
        # Import des composants (simulation pour l'instant)
        try:
            # Tentative d'utilisation du moteur Ollama réel
            from .ollama_analysis_engine import OllamaAnalysisEngine
            from .component_scanner import ComponentScanner
            from .capability_mapper import CapabilityMapper
            from ..prompting.auto_prompt_generator import AutoPromptGenerator
            from ..injection.context_injector import ContextInjector
            from ..evolution.effectiveness_analyzer import EffectivenessAnalyzer
            from ..evolution.adaptive_optimizer import AdaptiveOptimizer

            # MOTEUR OLLAMA RÉEL !
            self.analysis_engine = OllamaAnalysisEngine("qwen2.5:7b-instruct")
            self.component_scanner = ComponentScanner()
            self.capability_mapper = CapabilityMapper()
            self.prompt_generator = AutoPromptGenerator()
            self.context_injector = ContextInjector()
            self.effectiveness_analyzer = EffectivenessAnalyzer()
            self.adaptive_optimizer = AdaptiveOptimizer()

            print("✅ Composants d'introspection initialisés avec OLLAMA RÉEL !")

        except ImportError as e:
            print(f"⚠️ Ollama non disponible, mode simulation : {e}")
            self._initialize_simulation_components()

    def _initialize_prompt_logger(self):
        """Initialise le logger de prompts."""

        try:
            from .prompt_logger import PromptLogger
            self.prompt_logger = PromptLogger()
            print("✅ Logger de prompts initialisé")
        except ImportError as e:
            print(f"⚠️ Logger de prompts non disponible : {e}")
            self.prompt_logger = None

    def _initialize_simulation_components(self):
        """Initialise des composants de simulation."""
        
        self.analysis_engine = SimulatedAnalysisEngine()
        self.component_scanner = SimulatedComponentScanner()
        self.capability_mapper = SimulatedCapabilityMapper()
        self.prompt_generator = SimulatedPromptGenerator()
        self.context_injector = SimulatedContextInjector()
        self.effectiveness_analyzer = SimulatedEffectivenessAnalyzer()
        self.adaptive_optimizer = SimulatedAdaptiveOptimizer()
    
    async def conduct_full_introspection(self, 
                                       analysis_type: str = "comprehensive") -> IntrospectionResult:
        """
        Conduit une introspection complète de l'écosystème.
        
        Args:
            analysis_type: Type d'analyse à effectuer
            
        Returns:
            IntrospectionResult: Résultat complet de l'introspection
        """
        start_time = time.time()
        print(f"🧠 Démarrage introspection {analysis_type}...")
        
        try:
            # 1. Scan des composants
            print("🔍 Scan des composants...")
            components_scan = await self.component_scanner.scan_all_components(
                self.ecosystem_components
            )
            
            # 2. Cartographie des capacités
            print("🗺️ Cartographie des capacités...")
            capabilities_map = await self.capability_mapper.map_capabilities(
                components_scan
            )
            
            # 3. Génération de prompt d'auto-analyse
            print("🜲 Génération de prompt d'introspection...")
            introspection_prompt = await self.prompt_generator.generate_introspection_prompt(
                analysis_type, components_scan, capabilities_map
            )

            # Log de la génération de prompt
            if self.prompt_logger:
                self.prompt_logger.log_prompt_generation(
                    prompt_type=analysis_type,
                    generated_prompt=introspection_prompt,
                    template_used="introspection_template",
                    injection_data={"components": components_scan, "capabilities": capabilities_map}
                )
            
            # 4. Injection de contexte
            print("💉 Injection de contexte...")
            enriched_prompt = await self.context_injector.inject_comprehensive_context(
                introspection_prompt, components_scan, capabilities_map
            )

            # Log de l'injection contextuelle
            if self.prompt_logger:
                self.prompt_logger.log_context_injection(
                    base_prompt=introspection_prompt,
                    enriched_prompt=enriched_prompt,
                    injection_type="comprehensive",
                    injected_data={"components": components_scan, "capabilities": capabilities_map}
                )
            
            # 5. Exécution de l'auto-analyse
            print("⚡ Exécution de l'auto-analyse...")
            analysis_start_time = time.time()
            analysis_result = await self.analysis_engine.execute_introspection(
                enriched_prompt, analysis_type
            )
            analysis_execution_time = time.time() - analysis_start_time
            
            # 6. Analyse d'efficacité
            print("📊 Analyse d'efficacité...")
            effectiveness = await self.effectiveness_analyzer.analyze_effectiveness(
                analysis_result, components_scan, capabilities_map
            )
            
            # 7. Génération de recommandations
            print("🌟 Génération de recommandations...")
            recommendations = await self.adaptive_optimizer.generate_recommendations(
                analysis_result, effectiveness
            )
            
            # 8. Construction du résultat
            execution_time = time.time() - start_time

            result = IntrospectionResult(
                analysis_type=analysis_type,
                components_analyzed=components_scan,
                capabilities_discovered=capabilities_map,
                effectiveness_score=effectiveness.overall_score,
                improvement_suggestions=recommendations.get("improvements", []),
                evolution_recommendations=recommendations.get("evolutions", []),
                execution_time=execution_time
            )

            # Log du résultat d'introspection
            if self.prompt_logger:
                self.prompt_logger.log_introspection_result(
                    introspection_prompt=enriched_prompt,
                    analysis_result={
                        "analysis_type": analysis_type,
                        "components_analyzed": components_scan,
                        "capabilities_discovered": capabilities_map,
                        "improvement_suggestions": recommendations.get("improvements", []),
                        "evolution_recommendations": recommendations.get("evolutions", [])
                    },
                    effectiveness_score=effectiveness.overall_score,
                    analysis_time=analysis_execution_time
                )
            
            # 9. Mise à jour des métriques
            await self._update_performance_metrics(result, effectiveness)
            
            # 10. Évolution automatique si nécessaire
            if (self.config["auto_evolution"] and 
                effectiveness.overall_score < self.config["effectiveness_threshold"]):
                print("🔄 Déclenchement évolution automatique...")
                await self._trigger_automatic_evolution(effectiveness)
            
            print(f"✅ Introspection terminée en {execution_time:.2f}s")
            print(f"📊 Score d'efficacité : {effectiveness.overall_score:.2f}")
            
            return result
            
        except Exception as e:
            print(f"❌ Erreur lors de l'introspection : {e}")
            return IntrospectionResult(
                analysis_type=analysis_type,
                effectiveness_score=0.0,
                improvement_suggestions=[f"Fix error: {str(e)}"],
                execution_time=time.time() - start_time
            )
    
    async def generate_auto_prompt(self, 
                                 focus: str, 
                                 context_data: Optional[Dict] = None) -> str:
        """
        Génère un prompt d'auto-analyse optimisé.
        
        Args:
            focus: Focus de l'analyse
            context_data: Données contextuelles optionnelles
            
        Returns:
            str: Prompt d'auto-analyse généré
        """
        print(f"🜲 Génération auto-prompt pour focus : {focus}")
        
        # Collecte de données contextuelles
        if context_data is None:
            context_data = await self._collect_context_data(focus)
        
        # Génération du prompt de base
        base_prompt = await self.prompt_generator.generate_focused_prompt(
            focus, context_data
        )
        
        # Injection contextuelle
        enriched_prompt = await self.context_injector.inject_targeted_context(
            base_prompt, focus, context_data
        )
        
        # Optimisation basée sur l'historique
        optimized_prompt = await self.prompt_generator.optimize_prompt_effectiveness(
            enriched_prompt, self.introspection_history
        )
        
        print(f"✅ Auto-prompt généré : {len(optimized_prompt)} caractères")
        return optimized_prompt
    
    async def inject_contextual_data(self, 
                                   prompt: str, 
                                   injection_type: str = "comprehensive") -> str:
        """
        Injecte des données contextuelles dans un prompt.
        
        Args:
            prompt: Prompt de base
            injection_type: Type d'injection
            
        Returns:
            str: Prompt enrichi
        """
        print(f"💉 Injection contextuelle : {injection_type}")
        
        return await self.context_injector.inject_contextual_data(
            prompt, injection_type, self.ecosystem_components
        )
    
    async def analyze_effectiveness(self, 
                                  result: Any, 
                                  expected_outcomes: Optional[List[str]] = None) -> EffectivenessScore:
        """
        Analyse l'efficacité d'un résultat d'introspection.
        
        Args:
            result: Résultat à analyser
            expected_outcomes: Résultats attendus
            
        Returns:
            EffectivenessScore: Score d'efficacité
        """
        print("📊 Analyse d'efficacité...")
        
        return await self.effectiveness_analyzer.comprehensive_analysis(
            result, expected_outcomes, self.introspection_history
        )
    
    async def evolve_capabilities(self, 
                                feedback: EffectivenessScore) -> Dict[str, Any]:
        """
        Fait évoluer les capacités du daemon basé sur le feedback.
        
        Args:
            feedback: Score d'efficacité et feedback
            
        Returns:
            Dict: Résultat de l'évolution
        """
        print("🌟 Évolution des capacités...")
        
        evolution_result = await self.adaptive_optimizer.evolve_capabilities(
            feedback, self.config, self.performance_metrics
        )
        
        # Mise à jour de la configuration si nécessaire
        if "config_updates" in evolution_result:
            self.config.update(evolution_result["config_updates"])
            print(f"⚙️ Configuration mise à jour : {evolution_result['config_updates']}")
        
        # Incrémentation du compteur d'évolution
        self.evolution_cycles += 1
        self.performance_metrics["evolution_improvements"] += 1
        self.performance_metrics["last_evolution"] = datetime.now()
        
        return evolution_result
    
    async def start_continuous_introspection(self, 
                                           interval: int = 3600) -> None:
        """
        Démarre une boucle d'introspection continue.
        
        Args:
            interval: Intervalle entre les introspections (secondes)
        """
        print(f"🔄 Démarrage introspection continue (intervalle: {interval}s)")
        
        while self.evolution_cycles < self.config["max_evolution_cycles"]:
            try:
                # Introspection complète
                result = await self.conduct_full_introspection("continuous")
                
                # Analyse et évolution si nécessaire
                if result.effectiveness_score < self.config["effectiveness_threshold"]:
                    effectiveness = EffectivenessScore(
                        overall_score=result.effectiveness_score,
                        feedback=result.improvement_suggestions
                    )
                    await self.evolve_capabilities(effectiveness)
                
                # Pause avant prochaine itération
                print(f"⏸️ Pause de {interval}s avant prochaine introspection...")
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"❌ Erreur dans la boucle continue : {e}")
                await asyncio.sleep(60)  # Pause courte en cas d'erreur
    
    async def _collect_context_data(self, focus: str) -> Dict[str, Any]:
        """Collecte les données contextuelles pour un focus donné."""
        
        context_data = {
            "focus": focus,
            "ecosystem_components": self.ecosystem_components,
            "performance_metrics": self.performance_metrics,
            "introspection_history": self.introspection_history[-5:],  # 5 dernières
            "current_config": self.config
        }
        
        return context_data
    
    async def _update_performance_metrics(self, 
                                        result: IntrospectionResult, 
                                        effectiveness: EffectivenessScore):
        """Met à jour les métriques de performance."""
        
        self.performance_metrics["total_introspections"] += 1
        
        if effectiveness.overall_score > 0.5:
            self.performance_metrics["successful_introspections"] += 1
        
        # Calcul de la moyenne d'efficacité
        total = self.performance_metrics["total_introspections"]
        current_avg = self.performance_metrics["average_effectiveness"]
        new_avg = ((current_avg * (total - 1)) + effectiveness.overall_score) / total
        self.performance_metrics["average_effectiveness"] = new_avg
        
        # Ajout à l'historique
        self.introspection_history.append({
            "timestamp": result.timestamp,
            "analysis_type": result.analysis_type,
            "effectiveness_score": effectiveness.overall_score,
            "execution_time": result.execution_time
        })
        
        # Limitation de l'historique
        if len(self.introspection_history) > 50:
            self.introspection_history = self.introspection_history[-50:]
    
    async def _trigger_automatic_evolution(self, effectiveness: EffectivenessScore):
        """Déclenche une évolution automatique."""
        
        print("🔄 Évolution automatique déclenchée...")
        evolution_result = await self.evolve_capabilities(effectiveness)
        
        if evolution_result.get("success", False):
            print(f"✅ Évolution réussie : {evolution_result.get('improvements', [])}")
        else:
            print(f"⚠️ Évolution partielle : {evolution_result.get('issues', [])}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des performances du daemon."""
        
        return {
            "performance_metrics": self.performance_metrics,
            "evolution_cycles": self.evolution_cycles,
            "current_config": self.config,
            "recent_introspections": self.introspection_history[-5:],
            "health_status": "healthy" if self.performance_metrics["average_effectiveness"] > 0.7 else "needs_improvement"
        }

# Classes de simulation pour les tests
class SimulatedAnalysisEngine:
    async def execute_introspection(self, prompt: str, analysis_type: str) -> Dict:
        await asyncio.sleep(0.1)  # Simulation
        return {
            "analysis_type": analysis_type,
            "components_found": 5,
            "capabilities_identified": 12,
            "insights": ["Insight 1", "Insight 2"],
            "recommendations": ["Recommendation 1"]
        }

class SimulatedComponentScanner:
    async def scan_all_components(self, components: Dict) -> Dict:
        await asyncio.sleep(0.1)
        return {
            "memory_engine": {"status": "active", "health": 0.9},
            "tool_registry": {"status": "active", "health": 0.8},
            "editing_session": {"status": "active", "health": 0.85}
        }

class SimulatedCapabilityMapper:
    async def map_capabilities(self, components: Dict) -> Dict:
        await asyncio.sleep(0.1)
        return {
            "introspection": 0.8,
            "auto_prompting": 0.7,
            "context_injection": 0.9,
            "evolution": 0.6
        }

class SimulatedPromptGenerator:
    async def generate_introspection_prompt(self, analysis_type: str, components: Dict, capabilities: Dict) -> str:
        await asyncio.sleep(0.1)

        # Génération d'un prompt luciforme réaliste
        prompt = f"""
<🜲luciform id="auto_introspection_{analysis_type}⛧" type="✶comprehensive_analysis">
  <🜄context_injection>
    ::INJECT_COMPONENT_DATA::
    Composants analysés : {len(components)} identifiés
    État global : {sum(c.get('health', 0) for c in components.values()) / len(components):.2f}

    ::INJECT_CAPABILITY_MAP::
    Capacités découvertes : {len(capabilities)} mappées
    Score moyen : {sum(capabilities.values()) / len(capabilities):.2f}

    ::INJECT_PERFORMANCE_METRICS::
    Type d'analyse : {analysis_type}
    Profondeur d'introspection : 3 niveaux
  </🜄context_injection>

  <🜂introspection_directive>
    Tu es le IntrospectionDaemon en mode d'auto-analyse {analysis_type}.

    MISSION D'INTROSPECTION MYSTIQUE :

    1. 🧠 ANALYSE ARCHITECTURALE :
       - Évalue la santé des {len(components)} composants injectés
       - Identifie les patterns de défaillance potentiels
       - Analyse la cohérence globale du système

    2. 🔍 CARTOGRAPHIE DES CAPACITÉS :
       - Inventorie les {len(capabilities)} capacités découvertes
       - Identifie les lacunes critiques
       - Propose des extensions stratégiques

    3. ⚡ OPTIMISATION INTELLIGENTE :
       - Analyse les métriques de performance
       - Identifie les goulots d'étranglement
       - Génère des recommandations concrètes

    4. 🌟 ÉVOLUTION ADAPTATIVE :
       - Planifie l'évolution future
       - Priorise les améliorations
       - Définis des métriques de succès

    RÉSULTAT ATTENDU :
    Génère une auto-analyse complète incluant :
    - État de santé détaillé avec scores
    - Plan d'optimisation prioritaire
    - Stratégie d'évolution adaptative
    - Métriques de suivi précises
  </🜂introspection_directive>
</🜲luciform>
        """

        return prompt.strip()
    
    async def generate_focused_prompt(self, focus: str, context: Dict) -> str:
        await asyncio.sleep(0.1)

        # Génération d'un prompt focalisé réaliste
        prompt = f"""
<🜲luciform id="focused_{focus}_analysis⛧" type="✶targeted_introspection">
  <🜄focused_context>
    ::INJECT_TARGET_DATA::
    Focus d'analyse : {focus}
    Contexte disponible : {len(context)} éléments

    ::INJECT_RELATED_CONTEXT::
    Données contextuelles spécialisées pour {focus}

    ::INJECT_HISTORICAL_DATA::
    Historique et patterns pour {focus}
  </🜄focused_context>

  <🜂focused_directive>
    Tu es le IntrospectionDaemon en mode d'analyse focalisée sur : {focus}

    MISSION D'ANALYSE CIBLÉE :

    1. 🎯 ANALYSE SPÉCIALISÉE :
       - Focus exclusif sur {focus}
       - Analyse approfondie des aspects spécifiques
       - Évaluation détaillée de l'état et performances

    2. 🔗 ANALYSE RELATIONNELLE :
       - Impact sur les composants connexes
       - Dépendances et interdépendances
       - Effets de réseau et propagation

    3. 📊 ANALYSE HISTORIQUE :
       - Évolution et tendances observées
       - Patterns de succès et d'échec
       - Apprentissages des expériences passées

    4. 🚀 RECOMMANDATIONS SPÉCIALISÉES :
       - Améliorations spécifiques au domaine {focus}
       - Optimisations techniques précises
       - Plan d'action détaillé et réalisable

    RÉSULTAT CIBLÉ :
    Génère une analyse spécialisée incluant :
    - Diagnostic précis de {focus}
    - Recommandations d'amélioration spécifiques
    - Plan d'action avec étapes concrètes
    - Métriques de suivi adaptées
  </🜂focused_directive>
</🜲luciform>
        """

        return prompt.strip()
    
    async def optimize_prompt_effectiveness(self, prompt: str, history: List) -> str:
        await asyncio.sleep(0.1)
        return f"Optimized: {prompt}"

class SimulatedContextInjector:
    async def inject_comprehensive_context(self, prompt: str, components: Dict, capabilities: Dict) -> str:
        await asyncio.sleep(0.1)
        return f"Context-injected: {prompt}"
    
    async def inject_targeted_context(self, prompt: str, focus: str, context: Dict) -> str:
        await asyncio.sleep(0.1)
        return f"Targeted-injected: {prompt}"
    
    async def inject_contextual_data(self, prompt: str, injection_type: str, components: Dict) -> str:
        await asyncio.sleep(0.1)
        return f"Data-injected: {prompt}"

class SimulatedEffectivenessAnalyzer:
    async def analyze_effectiveness(self, result: Dict, components: Dict, capabilities: Dict) -> EffectivenessScore:
        await asyncio.sleep(0.1)
        return EffectivenessScore(
            overall_score=0.75,
            component_scores={"analysis": 0.8, "prompting": 0.7},
            feedback=["Good analysis depth", "Could improve context injection"],
            improvement_areas=["context_injection"],
            success_factors=["comprehensive_scanning"]
        )
    
    async def comprehensive_analysis(self, result: Any, expected: List, history: List) -> EffectivenessScore:
        await asyncio.sleep(0.1)
        return EffectivenessScore(
            overall_score=0.8,
            feedback=["Analysis complete"],
            improvement_areas=["optimization"]
        )

class SimulatedAdaptiveOptimizer:
    async def generate_recommendations(self, result: Dict, effectiveness: EffectivenessScore) -> Dict:
        await asyncio.sleep(0.1)
        return {
            "improvements": ["Improve context injection", "Optimize prompt generation"],
            "evolutions": ["Add new analysis capabilities", "Enhance effectiveness tracking"]
        }
    
    async def evolve_capabilities(self, feedback: EffectivenessScore, config: Dict, metrics: Dict) -> Dict:
        await asyncio.sleep(0.1)
        return {
            "success": True,
            "improvements": ["Enhanced context injection"],
            "config_updates": {"effectiveness_threshold": 0.75}
        }

# Fonction utilitaire pour créer un daemon d'introspection
def create_introspection_daemon(ecosystem_components: Optional[Dict] = None) -> IntrospectionConductor:
    """
    Crée une instance du daemon d'introspection.
    
    Args:
        ecosystem_components: Composants de l'écosystème
        
    Returns:
        IntrospectionConductor: Instance du daemon
    """
    return IntrospectionConductor(ecosystem_components)

if __name__ == "__main__":
    # Test du daemon d'introspection
    async def test_introspection_daemon():
        print("🧠 Test du IntrospectionDaemon...")
        
        # Création du daemon
        daemon = create_introspection_daemon()
        
        # Test d'introspection complète
        result = await daemon.conduct_full_introspection("test")
        print(f"✅ Introspection test : score {result.effectiveness_score:.2f}")
        
        # Test de génération de prompt
        prompt = await daemon.generate_auto_prompt("memory_analysis")
        print(f"✅ Prompt généré : {len(prompt)} caractères")
        
        # Résumé des performances
        summary = daemon.get_performance_summary()
        print(f"✅ Performances : {summary['health_status']}")
    
    asyncio.run(test_introspection_daemon())
