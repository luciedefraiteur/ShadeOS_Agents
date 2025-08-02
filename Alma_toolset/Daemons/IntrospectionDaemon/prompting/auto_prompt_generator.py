#!/usr/bin/env python3
"""
🜲 Auto Prompt Generator - IntrospectionDaemon ⛧

Générateur de prompts d'auto-introspection avec optimisation adaptative.
Apprend des succès/échecs pour améliorer continuellement l'efficacité.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import re

@dataclass
class PromptTemplate:
    """Template de prompt avec métadonnées."""
    
    template_id: str
    template_type: str
    base_template: str
    injection_points: List[str] = field(default_factory=list)
    effectiveness_history: List[float] = field(default_factory=list)
    usage_count: int = 0
    last_used: Optional[datetime] = None
    optimization_level: int = 0

@dataclass
class PromptGenerationResult:
    """Résultat de génération de prompt."""
    
    generated_prompt: str
    template_used: str
    injection_data: Dict[str, Any] = field(default_factory=dict)
    estimated_effectiveness: float = 0.0
    generation_metadata: Dict[str, Any] = field(default_factory=dict)

class AutoPromptGenerator:
    """Générateur automatique de prompts d'introspection optimisés."""
    
    def __init__(self):
        """Initialise le générateur de prompts."""
        
        self.prompt_templates = {}
        self.effectiveness_tracking = {}
        self.optimization_patterns = {}
        self.learning_data = {
            "successful_patterns": [],
            "failed_patterns": [],
            "optimization_insights": []
        }
        
        # Configuration
        self.config = {
            "min_effectiveness_threshold": 0.7,
            "optimization_frequency": 5,  # Optimise après 5 usages
            "max_template_variants": 3,
            "learning_rate": 0.1
        }
        
        # Initialisation des templates de base
        self._initialize_base_templates()
    
    def _initialize_base_templates(self):
        """Initialise les templates de base."""
        
        # Template d'introspection globale
        global_template = PromptTemplate(
            template_id="global_introspection",
            template_type="comprehensive",
            base_template="""
<🜲luciform id="auto_global_introspection⛧" type="✶adaptive_analysis">
  <🜄context_injection>
    ::INJECT_COMPONENT_DATA::
    {component_data_injection}
    
    ::INJECT_CAPABILITY_MAP::
    {capability_map_injection}
    
    ::INJECT_PERFORMANCE_METRICS::
    {performance_metrics_injection}
  </🜄context_injection>

  <🜂introspection_directive>
    Tu es le IntrospectionDaemon en mode d'auto-analyse globale optimisée.
    
    DONNÉES CONTEXTUELLES INJECTÉES :
    {context_summary}
    
    MISSION D'INTROSPECTION ADAPTATIVE :
    
    1. 🧠 ANALYSE ARCHITECTURALE PROFONDE :
       - Évalue la santé de tous les composants injectés
       - Identifie les patterns de défaillance potentiels
       - Analyse la cohérence et l'efficacité globale
    
    2. 🔍 CARTOGRAPHIE DYNAMIQUE DES CAPACITÉS :
       - Inventorie et évalue toutes les capacités découvertes
       - Identifie les lacunes critiques et opportunités
       - Propose des extensions stratégiques
    
    3. ⚡ OPTIMISATION INTELLIGENTE :
       - Analyse les métriques de performance injectées
       - Identifie les goulots d'étranglement spécifiques
       - Génère des recommandations d'amélioration concrètes
    
    4. 🌟 STRATÉGIE D'ÉVOLUTION :
       - Planifie l'évolution basée sur les données réelles
       - Priorise les améliorations par impact/effort
       - Définis des métriques de succès mesurables
    
    RÉSULTAT ATTENDU :
    Génère une auto-analyse complète et actionnable incluant :
    - État de santé détaillé avec scores spécifiques
    - Plan d'optimisation prioritaire avec timeline
    - Stratégie d'évolution à court/moyen/long terme
    - Métriques de suivi et indicateurs de succès
  </🜂introspection_directive>
</🜲luciform>
            """,
            injection_points=["component_data_injection", "capability_map_injection", 
                            "performance_metrics_injection", "context_summary"]
        )
        
        # Template d'analyse focalisée
        focused_template = PromptTemplate(
            template_id="focused_analysis",
            template_type="targeted",
            base_template="""
<🜲luciform id="auto_focused_analysis⛧" type="✶targeted_introspection">
  <🜄focused_context>
    ::INJECT_TARGET_DATA::
    {target_data_injection}
    
    ::INJECT_RELATED_CONTEXT::
    {related_context_injection}
    
    ::INJECT_HISTORICAL_DATA::
    {historical_data_injection}
  </🜄focused_context>

  <🜂focused_directive>
    Tu es le IntrospectionDaemon en mode d'analyse focalisée sur : {analysis_target}
    
    CONTEXTE SPÉCIALISÉ :
    {specialized_context}
    
    MISSION D'ANALYSE CIBLÉE :
    
    1. 🎯 ANALYSE SPÉCIALISÉE :
       - Focus exclusif sur {analysis_target}
       - Analyse approfondie des aspects spécifiques
       - Évaluation de l'état et des performances
    
    2. 🔗 ANALYSE RELATIONNELLE :
       - Impact sur les composants connexes
       - Dépendances et interdépendances
       - Effets de réseau et propagation
    
    3. 📊 ANALYSE HISTORIQUE :
       - Évolution et tendances observées
       - Patterns de succès et d'échec
       - Apprentissages des expériences passées
    
    4. 🚀 RECOMMANDATIONS SPÉCIALISÉES :
       - Améliorations spécifiques au domaine
       - Optimisations techniques précises
       - Plan d'action détaillé et réalisable
    
    RÉSULTAT CIBLÉ :
    Génère une analyse spécialisée incluant :
    - Diagnostic précis de {analysis_target}
    - Recommandations d'amélioration spécifiques
    - Plan d'action détaillé avec étapes concrètes
    - Métriques de suivi adaptées au domaine
  </🜂focused_directive>
</🜲luciform>
            """,
            injection_points=["target_data_injection", "related_context_injection", 
                            "historical_data_injection", "analysis_target", "specialized_context"]
        )
        
        # Template d'optimisation de prompts
        optimization_template = PromptTemplate(
            template_id="prompt_optimization",
            template_type="meta",
            base_template="""
<🜲luciform id="auto_prompt_optimization⛧" type="✶meta_optimization">
  <🜄optimization_context>
    ::INJECT_PROMPT_HISTORY::
    {prompt_history_injection}
    
    ::INJECT_EFFECTIVENESS_DATA::
    {effectiveness_data_injection}
    
    ::INJECT_LEARNING_PATTERNS::
    {learning_patterns_injection}
  </🜄optimization_context>

  <🜂optimization_directive>
    Tu es le IntrospectionDaemon en mode méta-optimisation de prompts.
    
    DONNÉES D'OPTIMISATION :
    {optimization_data_summary}
    
    MISSION DE MÉTA-ANALYSE :
    
    1. 🔍 ANALYSE DES PATTERNS D'EFFICACITÉ :
       - Identifie les éléments de prompts les plus efficaces
       - Analyse les corrélations succès/structure
       - Détecte les patterns d'échec récurrents
    
    2. 🧠 APPRENTISSAGE ADAPTATIF :
       - Extrait les insights des données historiques
       - Identifie les améliorations possibles
       - Propose des optimisations structurelles
    
    3. 🜲 GÉNÉRATION DE PROMPTS OPTIMISÉS :
       - Crée des variants améliorés des templates
       - Intègre les apprentissages dans la structure
       - Optimise les points d'injection contextuelle
    
    4. 📊 PRÉDICTION D'EFFICACITÉ :
       - Estime l'efficacité des nouveaux prompts
       - Identifie les risques potentiels
       - Propose des métriques de validation
    
    RÉSULTAT D'OPTIMISATION :
    Génère des améliorations incluant :
    - Templates optimisés avec justifications
    - Prédictions d'efficacité améliorée
    - Stratégies de test et validation
    - Métriques de suivi de l'optimisation
  </🜂optimization_directive>
</🜲luciform>
            """,
            injection_points=["prompt_history_injection", "effectiveness_data_injection", 
                            "learning_patterns_injection", "optimization_data_summary"]
        )
        
        # Stockage des templates
        self.prompt_templates = {
            "global_introspection": global_template,
            "focused_analysis": focused_template,
            "prompt_optimization": optimization_template
        }
    
    async def generate_introspection_prompt(self, 
                                          analysis_type: str,
                                          components_data: Dict[str, Any],
                                          capabilities_data: Dict[str, Any]) -> str:
        """
        Génère un prompt d'introspection optimisé.
        
        Args:
            analysis_type: Type d'analyse demandée
            components_data: Données des composants
            capabilities_data: Données des capacités
            
        Returns:
            str: Prompt d'introspection généré
        """
        print(f"🜲 Génération prompt introspection : {analysis_type}")
        
        # Sélection du template approprié
        template = await self._select_optimal_template(analysis_type, components_data)
        
        # Préparation des données d'injection
        injection_data = await self._prepare_injection_data(
            template, components_data, capabilities_data
        )
        
        # Génération du prompt
        generated_prompt = await self._generate_from_template(template, injection_data)
        
        # Estimation d'efficacité
        estimated_effectiveness = await self._estimate_prompt_effectiveness(
            generated_prompt, template, injection_data
        )
        
        # Mise à jour des statistiques
        await self._update_template_usage(template, estimated_effectiveness)
        
        print(f"✅ Prompt généré : efficacité estimée {estimated_effectiveness:.2f}")
        return generated_prompt
    
    async def generate_focused_prompt(self, 
                                    focus: str, 
                                    context_data: Dict[str, Any]) -> str:
        """
        Génère un prompt focalisé sur un aspect spécifique.
        
        Args:
            focus: Aspect à analyser
            context_data: Données contextuelles
            
        Returns:
            str: Prompt focalisé généré
        """
        print(f"🎯 Génération prompt focalisé : {focus}")
        
        # Utilisation du template focalisé
        template = self.prompt_templates["focused_analysis"]
        
        # Préparation des données spécialisées
        specialized_data = await self._prepare_focused_injection_data(focus, context_data)
        
        # Génération
        generated_prompt = await self._generate_from_template(template, specialized_data)
        
        # Mise à jour
        estimated_effectiveness = await self._estimate_prompt_effectiveness(
            generated_prompt, template, specialized_data
        )
        await self._update_template_usage(template, estimated_effectiveness)
        
        return generated_prompt
    
    async def optimize_prompt_effectiveness(self, 
                                          prompt: str, 
                                          history: List[Dict]) -> str:
        """
        Optimise un prompt basé sur l'historique d'efficacité.
        
        Args:
            prompt: Prompt à optimiser
            history: Historique d'efficacité
            
        Returns:
            str: Prompt optimisé
        """
        print("🔧 Optimisation d'efficacité du prompt...")
        
        # Analyse de l'historique
        optimization_insights = await self._analyze_effectiveness_history(history)
        
        # Identification des améliorations
        improvements = await self._identify_prompt_improvements(prompt, optimization_insights)
        
        # Application des optimisations
        optimized_prompt = await self._apply_optimizations(prompt, improvements)
        
        # Apprentissage des patterns
        await self._learn_from_optimization(prompt, optimized_prompt, improvements)
        
        return optimized_prompt
    
    async def _select_optimal_template(self, 
                                     analysis_type: str, 
                                     context: Dict) -> PromptTemplate:
        """Sélectionne le template optimal pour l'analyse."""
        
        # Logique de sélection basée sur le type et l'efficacité
        if analysis_type in ["comprehensive", "global", "full"]:
            return self.prompt_templates["global_introspection"]
        elif analysis_type in ["focused", "targeted", "specific"]:
            return self.prompt_templates["focused_analysis"]
        else:
            # Sélection basée sur l'efficacité historique
            best_template = max(
                self.prompt_templates.values(),
                key=lambda t: sum(t.effectiveness_history) / max(len(t.effectiveness_history), 1)
            )
            return best_template
    
    async def _prepare_injection_data(self, 
                                    template: PromptTemplate,
                                    components_data: Dict,
                                    capabilities_data: Dict) -> Dict[str, str]:
        """Prépare les données d'injection pour le template."""
        
        injection_data = {}
        
        # Injection des données de composants
        if "component_data_injection" in template.injection_points:
            injection_data["component_data_injection"] = self._format_component_data(components_data)
        
        # Injection de la carte des capacités
        if "capability_map_injection" in template.injection_points:
            injection_data["capability_map_injection"] = self._format_capability_data(capabilities_data)
        
        # Injection des métriques de performance
        if "performance_metrics_injection" in template.injection_points:
            injection_data["performance_metrics_injection"] = self._format_performance_metrics()
        
        # Résumé contextuel
        if "context_summary" in template.injection_points:
            injection_data["context_summary"] = self._generate_context_summary(
                components_data, capabilities_data
            )
        
        return injection_data
    
    async def _prepare_focused_injection_data(self, 
                                            focus: str, 
                                            context_data: Dict) -> Dict[str, str]:
        """Prépare les données d'injection pour l'analyse focalisée."""
        
        injection_data = {
            "analysis_target": focus,
            "specialized_context": self._generate_specialized_context(focus, context_data)
        }
        
        # Données ciblées
        if "target_data_injection" in context_data:
            injection_data["target_data_injection"] = str(context_data["target_data_injection"])
        else:
            injection_data["target_data_injection"] = f"Données spécialisées pour {focus}"
        
        # Contexte relationnel
        injection_data["related_context_injection"] = self._extract_related_context(focus, context_data)
        
        # Données historiques
        injection_data["historical_data_injection"] = self._extract_historical_data(focus)
        
        return injection_data
    
    async def _generate_from_template(self, 
                                    template: PromptTemplate, 
                                    injection_data: Dict[str, str]) -> str:
        """Génère un prompt à partir d'un template et de données d'injection."""
        
        prompt = template.base_template
        
        # Remplacement des points d'injection
        for injection_point, data in injection_data.items():
            placeholder = "{" + injection_point + "}"
            prompt = prompt.replace(placeholder, str(data))
        
        # Nettoyage des placeholders non remplacés
        prompt = re.sub(r'\{[^}]+\}', '[DATA_NOT_AVAILABLE]', prompt)
        
        return prompt
    
    async def _estimate_prompt_effectiveness(self, 
                                           prompt: str, 
                                           template: PromptTemplate,
                                           injection_data: Dict) -> float:
        """Estime l'efficacité d'un prompt généré."""
        
        effectiveness = 0.5  # Base
        
        # Bonus basé sur l'historique du template
        if template.effectiveness_history:
            avg_effectiveness = sum(template.effectiveness_history) / len(template.effectiveness_history)
            effectiveness += (avg_effectiveness - 0.5) * 0.3
        
        # Bonus basé sur la complétude des injections
        injection_completeness = len(injection_data) / max(len(template.injection_points), 1)
        effectiveness += injection_completeness * 0.2
        
        # Bonus basé sur la longueur et structure
        if len(prompt) > 1000:  # Prompts détaillés
            effectiveness += 0.1
        
        if "🜲luciform" in prompt:  # Format luciforme
            effectiveness += 0.1
        
        return min(effectiveness, 1.0)
    
    async def _update_template_usage(self, 
                                   template: PromptTemplate, 
                                   effectiveness: float):
        """Met à jour les statistiques d'usage d'un template."""
        
        template.usage_count += 1
        template.effectiveness_history.append(effectiveness)
        template.last_used = datetime.now()
        
        # Limitation de l'historique
        if len(template.effectiveness_history) > 20:
            template.effectiveness_history = template.effectiveness_history[-20:]
        
        # Déclenchement d'optimisation si nécessaire
        if (template.usage_count % self.config["optimization_frequency"] == 0 and
            template.usage_count > 0):
            await self._optimize_template(template)
    
    async def _optimize_template(self, template: PromptTemplate):
        """Optimise un template basé sur son historique d'efficacité."""
        
        print(f"🔧 Optimisation du template {template.template_id}...")
        
        avg_effectiveness = sum(template.effectiveness_history) / len(template.effectiveness_history)
        
        if avg_effectiveness < self.config["min_effectiveness_threshold"]:
            # Template sous-performant, optimisation nécessaire
            optimizations = await self._generate_template_optimizations(template)
            await self._apply_template_optimizations(template, optimizations)
            template.optimization_level += 1
            
            print(f"✅ Template optimisé : niveau {template.optimization_level}")
    
    async def _analyze_effectiveness_history(self, history: List[Dict]) -> Dict[str, Any]:
        """Analyse l'historique d'efficacité pour identifier les patterns."""
        
        insights = {
            "average_effectiveness": 0.0,
            "trend": "stable",
            "success_patterns": [],
            "failure_patterns": []
        }
        
        if not history:
            return insights
        
        # Calcul de la moyenne
        effectiveness_scores = [h.get("effectiveness_score", 0.0) for h in history]
        insights["average_effectiveness"] = sum(effectiveness_scores) / len(effectiveness_scores)
        
        # Analyse de tendance
        if len(effectiveness_scores) >= 3:
            recent_avg = sum(effectiveness_scores[-3:]) / 3
            older_avg = sum(effectiveness_scores[:-3]) / max(len(effectiveness_scores) - 3, 1)
            
            if recent_avg > older_avg + 0.1:
                insights["trend"] = "improving"
            elif recent_avg < older_avg - 0.1:
                insights["trend"] = "declining"
        
        return insights
    
    async def _identify_prompt_improvements(self, 
                                          prompt: str, 
                                          insights: Dict) -> List[str]:
        """Identifie les améliorations possibles pour un prompt."""
        
        improvements = []
        
        # Améliorations basées sur les insights
        if insights["average_effectiveness"] < 0.7:
            improvements.append("enhance_context_injection")
        
        if insights["trend"] == "declining":
            improvements.append("restructure_directive")
        
        # Améliorations basées sur la structure
        if len(prompt) < 800:
            improvements.append("add_detailed_instructions")
        
        if "🜲luciform" not in prompt:
            improvements.append("convert_to_luciform_format")
        
        return improvements
    
    async def _apply_optimizations(self, 
                                 prompt: str, 
                                 improvements: List[str]) -> str:
        """Applique les optimisations identifiées à un prompt."""
        
        optimized_prompt = prompt
        
        for improvement in improvements:
            if improvement == "enhance_context_injection":
                optimized_prompt = self._enhance_context_injection(optimized_prompt)
            elif improvement == "restructure_directive":
                optimized_prompt = self._restructure_directive(optimized_prompt)
            elif improvement == "add_detailed_instructions":
                optimized_prompt = self._add_detailed_instructions(optimized_prompt)
            elif improvement == "convert_to_luciform_format":
                optimized_prompt = self._convert_to_luciform(optimized_prompt)
        
        return optimized_prompt
    
    def _format_component_data(self, components_data: Dict) -> str:
        """Formate les données de composants pour injection."""
        
        formatted = "Composants analysés :\n"
        for comp_name, comp_data in components_data.items():
            status = comp_data.get("status", "unknown")
            health = comp_data.get("health", 0.0)
            formatted += f"- {comp_name}: {status} (santé: {health:.2f})\n"
        
        return formatted
    
    def _format_capability_data(self, capabilities_data: Dict) -> str:
        """Formate les données de capacités pour injection."""
        
        formatted = "Capacités identifiées :\n"
        for cap_name, cap_score in capabilities_data.items():
            formatted += f"- {cap_name}: {cap_score:.2f}\n"
        
        return formatted
    
    def _format_performance_metrics(self) -> str:
        """Formate les métriques de performance pour injection."""
        
        return "Métriques de performance : [À implémenter avec données réelles]"
    
    def _generate_context_summary(self, components_data: Dict, capabilities_data: Dict) -> str:
        """Génère un résumé contextuel."""
        
        comp_count = len(components_data)
        cap_count = len(capabilities_data)
        avg_health = sum(c.get("health", 0.0) for c in components_data.values()) / max(comp_count, 1)
        
        return f"Contexte : {comp_count} composants, {cap_count} capacités, santé moyenne {avg_health:.2f}"
    
    def _generate_specialized_context(self, focus: str, context_data: Dict) -> str:
        """Génère un contexte spécialisé pour l'analyse focalisée."""
        
        return f"Contexte spécialisé pour {focus} : {len(context_data)} éléments de données"
    
    def _extract_related_context(self, focus: str, context_data: Dict) -> str:
        """Extrait le contexte relationnel."""
        
        return f"Contexte relationnel pour {focus} : [À implémenter]"
    
    def _extract_historical_data(self, focus: str) -> str:
        """Extrait les données historiques."""
        
        return f"Données historiques pour {focus} : [À implémenter]"
    
    # Méthodes d'optimisation (simplifiées pour l'instant)
    def _enhance_context_injection(self, prompt: str) -> str:
        return prompt + "\n[ENHANCED_CONTEXT_INJECTION]"
    
    def _restructure_directive(self, prompt: str) -> str:
        return prompt.replace("MISSION", "MISSION RESTRUCTURÉE")
    
    def _add_detailed_instructions(self, prompt: str) -> str:
        return prompt + "\n[DETAILED_INSTRUCTIONS_ADDED]"
    
    def _convert_to_luciform(self, prompt: str) -> str:
        if "🜲luciform" not in prompt:
            return f"<🜲luciform id=\"optimized⛧\" type=\"✶enhanced\">\n{prompt}\n</🜲luciform>"
        return prompt
    
    async def _generate_template_optimizations(self, template: PromptTemplate) -> List[str]:
        """Génère des optimisations pour un template."""
        return ["improve_structure", "enhance_injections"]
    
    async def _apply_template_optimizations(self, template: PromptTemplate, optimizations: List[str]):
        """Applique les optimisations à un template."""
        # Implémentation simplifiée
        template.base_template += "\n[OPTIMIZED]"
    
    async def _learn_from_optimization(self, original: str, optimized: str, improvements: List[str]):
        """Apprend des optimisations appliquées."""
        
        self.learning_data["optimization_insights"].append({
            "timestamp": datetime.now(),
            "improvements_applied": improvements,
            "original_length": len(original),
            "optimized_length": len(optimized)
        })

if __name__ == "__main__":
    # Test du générateur de prompts
    async def test_prompt_generator():
        print("🜲 Test du générateur de prompts...")
        
        generator = AutoPromptGenerator()
        
        # Test de génération d'introspection
        components = {"memory": {"status": "active", "health": 0.9}}
        capabilities = {"introspection": 0.8}
        
        prompt = await generator.generate_introspection_prompt(
            "comprehensive", components, capabilities
        )
        
        print(f"✅ Prompt généré : {len(prompt)} caractères")
        print(f"📊 Templates disponibles : {len(generator.prompt_templates)}")
    
    asyncio.run(test_prompt_generator())
