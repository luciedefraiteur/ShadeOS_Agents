#!/usr/bin/env python3
"""
🧪 Comprehensive Daemon Test - IntrospectionDaemon ⛧

Tests complets du IntrospectionDaemon avec validation d'efficacité et évolution.
Teste toutes les fonctionnalités et déclenche l'évolution si inefficace.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import sys
import os

# Ajout du chemin pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
daemon_dir = os.path.dirname(current_dir)
sys.path.append(daemon_dir)

@dataclass
class TestResult:
    """Résultat d'un test."""
    
    test_name: str
    success: bool
    execution_time: float
    effectiveness_score: float
    details: Dict[str, Any]
    error_message: Optional[str] = None

@dataclass
class DaemonTestSuite:
    """Suite de tests complète pour le daemon."""
    
    test_results: List[TestResult]
    overall_success: bool
    total_execution_time: float
    average_effectiveness: float
    evolution_triggered: bool = False

class IntrospectionDaemonTester:
    """Testeur complet du IntrospectionDaemon."""
    
    def __init__(self):
        """Initialise le testeur."""
        
        self.test_results = []
        self.effectiveness_threshold = 0.7
        self.evolution_threshold = 0.6
        
        # Configuration des tests
        self.test_config = {
            "run_basic_tests": True,
            "run_integration_tests": True,
            "run_performance_tests": True,
            "run_evolution_tests": True,
            "max_test_duration": 30.0,  # secondes
            "verbose_output": True
        }
    
    async def run_comprehensive_test_suite(self) -> DaemonTestSuite:
        """
        Exécute la suite complète de tests du daemon.
        
        Returns:
            DaemonTestSuite: Résultats complets des tests
        """
        print("🧪 Démarrage de la suite de tests complète du IntrospectionDaemon...")
        start_time = time.time()
        
        # Initialisation du daemon
        daemon = await self._initialize_daemon()
        
        # Exécution des tests
        if self.test_config["run_basic_tests"]:
            await self._run_basic_functionality_tests(daemon)
        
        if self.test_config["run_integration_tests"]:
            await self._run_integration_tests(daemon)
        
        if self.test_config["run_performance_tests"]:
            await self._run_performance_tests(daemon)
        
        if self.test_config["run_evolution_tests"]:
            await self._run_evolution_tests(daemon)
        
        # Analyse des résultats
        total_time = time.time() - start_time
        test_suite = await self._analyze_test_results(total_time)
        
        # Déclenchement d'évolution si nécessaire
        if test_suite.average_effectiveness < self.evolution_threshold:
            print("🔄 Efficacité insuffisante, déclenchement de l'évolution...")
            await self._trigger_daemon_evolution(daemon, test_suite)
            test_suite.evolution_triggered = True
        
        # Rapport final
        await self._generate_test_report(test_suite)
        
        return test_suite
    
    async def _initialize_daemon(self):
        """Initialise le daemon pour les tests."""
        
        print("🧠 Initialisation du IntrospectionDaemon...")
        
        try:
            from core.introspection_conductor import IntrospectionConductor
            
            # Composants de test
            test_ecosystem = {
                "memory_engine": {
                    "status": "active",
                    "backend_type": "neo4j",
                    "health": 0.9
                },
                "tool_registry": {
                    "status": "active", 
                    "indexed": True,
                    "tool_count": 23,
                    "health": 0.8
                },
                "editing_session": {
                    "status": "active",
                    "partitioning_support": True,
                    "health": 0.85
                }
            }
            
            daemon = IntrospectionConductor(test_ecosystem)
            print("✅ Daemon initialisé avec succès")
            return daemon
            
        except Exception as e:
            print(f"❌ Erreur d'initialisation : {e}")
            return None
    
    async def _run_basic_functionality_tests(self, daemon):
        """Teste les fonctionnalités de base du daemon."""
        
        print("🔧 Tests de fonctionnalités de base...")
        
        # Test 1: Introspection complète
        await self._test_full_introspection(daemon)
        
        # Test 2: Génération de prompts
        await self._test_prompt_generation(daemon)
        
        # Test 3: Injection contextuelle
        await self._test_context_injection(daemon)
        
        # Test 4: Analyse d'efficacité
        await self._test_effectiveness_analysis(daemon)
    
    async def _test_full_introspection(self, daemon):
        """Teste l'introspection complète."""
        
        test_name = "full_introspection"
        start_time = time.time()
        
        try:
            print("  🧠 Test d'introspection complète...")
            
            result = await daemon.conduct_full_introspection("test_comprehensive")
            
            execution_time = time.time() - start_time
            effectiveness = result.effectiveness_score
            
            success = (
                result is not None and
                result.effectiveness_score > 0.0 and
                len(result.components_analyzed) > 0 and
                execution_time < self.test_config["max_test_duration"]
            )
            
            test_result = TestResult(
                test_name=test_name,
                success=success,
                execution_time=execution_time,
                effectiveness_score=effectiveness,
                details={
                    "components_analyzed": len(result.components_analyzed),
                    "capabilities_discovered": len(result.capabilities_discovered),
                    "improvement_suggestions": len(result.improvement_suggestions),
                    "analysis_type": result.analysis_type
                }
            )
            
            self.test_results.append(test_result)
            
            if success:
                print(f"    ✅ Introspection réussie (score: {effectiveness:.2f})")
            else:
                print(f"    ❌ Introspection échouée")
                
        except Exception as e:
            execution_time = time.time() - start_time
            test_result = TestResult(
                test_name=test_name,
                success=False,
                execution_time=execution_time,
                effectiveness_score=0.0,
                details={},
                error_message=str(e)
            )
            self.test_results.append(test_result)
            print(f"    ❌ Erreur lors de l'introspection : {e}")
    
    async def _test_prompt_generation(self, daemon):
        """Teste la génération de prompts."""
        
        test_name = "prompt_generation"
        start_time = time.time()
        
        try:
            print("  🜲 Test de génération de prompts...")
            
            # Test de différents types de prompts
            test_focuses = ["memory_analysis", "tool_inventory", "capability_assessment"]
            generated_prompts = []
            
            for focus in test_focuses:
                prompt = await daemon.generate_auto_prompt(focus)
                generated_prompts.append({
                    "focus": focus,
                    "prompt_length": len(prompt),
                    "has_luciform": "🜲luciform" in prompt
                })
            
            execution_time = time.time() - start_time
            
            # Évaluation de la qualité
            avg_length = sum(p["prompt_length"] for p in generated_prompts) / len(generated_prompts)
            luciform_ratio = sum(1 for p in generated_prompts if p["has_luciform"]) / len(generated_prompts)
            
            effectiveness = min(
                (avg_length / 1000) * 0.5 +  # Bonus pour prompts détaillés
                luciform_ratio * 0.5,        # Bonus pour format luciforme
                1.0
            )
            
            success = (
                len(generated_prompts) == len(test_focuses) and
                avg_length > 500 and  # Prompts suffisamment détaillés
                execution_time < self.test_config["max_test_duration"]
            )
            
            test_result = TestResult(
                test_name=test_name,
                success=success,
                execution_time=execution_time,
                effectiveness_score=effectiveness,
                details={
                    "prompts_generated": len(generated_prompts),
                    "average_length": avg_length,
                    "luciform_ratio": luciform_ratio,
                    "generated_prompts": generated_prompts
                }
            )
            
            self.test_results.append(test_result)
            
            if success:
                print(f"    ✅ Génération réussie (efficacité: {effectiveness:.2f})")
            else:
                print(f"    ❌ Génération échouée")
                
        except Exception as e:
            execution_time = time.time() - start_time
            test_result = TestResult(
                test_name=test_name,
                success=False,
                execution_time=execution_time,
                effectiveness_score=0.0,
                details={},
                error_message=str(e)
            )
            self.test_results.append(test_result)
            print(f"    ❌ Erreur lors de la génération : {e}")
    
    async def _test_context_injection(self, daemon):
        """Teste l'injection contextuelle."""
        
        test_name = "context_injection"
        start_time = time.time()
        
        try:
            print("  💉 Test d'injection contextuelle...")
            
            # Test d'injection sur différents types
            base_prompt = "Analyse ::INJECT_MEMORY_CONTEXT:: et ::INJECT_TOOL_CONTEXT::"
            
            enriched_prompt = await daemon.inject_contextual_data(
                base_prompt, "comprehensive", daemon.ecosystem_components
            )
            
            execution_time = time.time() - start_time
            
            # Évaluation de l'injection
            injection_success = (
                len(enriched_prompt) > len(base_prompt) and
                "::INJECT_" not in enriched_prompt  # Tous les patterns remplacés
            )
            
            context_richness = len(enriched_prompt) / len(base_prompt)
            effectiveness = min(context_richness / 3.0, 1.0)  # Facteur d'enrichissement
            
            success = (
                injection_success and
                context_richness > 1.5 and  # Au moins 50% d'enrichissement
                execution_time < self.test_config["max_test_duration"]
            )
            
            test_result = TestResult(
                test_name=test_name,
                success=success,
                execution_time=execution_time,
                effectiveness_score=effectiveness,
                details={
                    "original_length": len(base_prompt),
                    "enriched_length": len(enriched_prompt),
                    "enrichment_ratio": context_richness,
                    "injection_patterns_resolved": "::INJECT_" not in enriched_prompt
                }
            )
            
            self.test_results.append(test_result)
            
            if success:
                print(f"    ✅ Injection réussie (enrichissement: {context_richness:.2f}x)")
            else:
                print(f"    ❌ Injection échouée")
                
        except Exception as e:
            execution_time = time.time() - start_time
            test_result = TestResult(
                test_name=test_name,
                success=False,
                execution_time=execution_time,
                effectiveness_score=0.0,
                details={},
                error_message=str(e)
            )
            self.test_results.append(test_result)
            print(f"    ❌ Erreur lors de l'injection : {e}")
    
    async def _test_effectiveness_analysis(self, daemon):
        """Teste l'analyse d'efficacité."""
        
        test_name = "effectiveness_analysis"
        start_time = time.time()
        
        try:
            print("  📊 Test d'analyse d'efficacité...")
            
            # Création d'un résultat de test
            test_result_data = {
                "analysis_type": "test",
                "components_found": 3,
                "capabilities_identified": 5,
                "insights": ["Test insight 1", "Test insight 2"]
            }
            
            effectiveness = await daemon.analyze_effectiveness(
                test_result_data, ["expected_outcome_1", "expected_outcome_2"]
            )
            
            execution_time = time.time() - start_time
            
            success = (
                effectiveness is not None and
                hasattr(effectiveness, 'overall_score') and
                0.0 <= effectiveness.overall_score <= 1.0 and
                execution_time < self.test_config["max_test_duration"]
            )
            
            test_result = TestResult(
                test_name=test_name,
                success=success,
                execution_time=execution_time,
                effectiveness_score=effectiveness.overall_score if effectiveness else 0.0,
                details={
                    "effectiveness_score": effectiveness.overall_score if effectiveness else 0.0,
                    "component_scores": effectiveness.component_scores if effectiveness else {},
                    "feedback_count": len(effectiveness.feedback) if effectiveness else 0
                }
            )
            
            self.test_results.append(test_result)
            
            if success:
                print(f"    ✅ Analyse réussie (score: {effectiveness.overall_score:.2f})")
            else:
                print(f"    ❌ Analyse échouée")
                
        except Exception as e:
            execution_time = time.time() - start_time
            test_result = TestResult(
                test_name=test_name,
                success=False,
                execution_time=execution_time,
                effectiveness_score=0.0,
                details={},
                error_message=str(e)
            )
            self.test_results.append(test_result)
            print(f"    ❌ Erreur lors de l'analyse : {e}")
    
    async def _run_integration_tests(self, daemon):
        """Teste l'intégration avec l'écosystème."""
        
        print("🔗 Tests d'intégration...")
        
        # Test d'intégration avec les composants de l'écosystème
        await self._test_ecosystem_integration(daemon)
    
    async def _test_ecosystem_integration(self, daemon):
        """Teste l'intégration avec l'écosystème."""
        
        test_name = "ecosystem_integration"
        start_time = time.time()
        
        try:
            print("  🌐 Test d'intégration écosystème...")
            
            # Vérification de la disponibilité des composants
            performance_summary = daemon.get_performance_summary()
            
            execution_time = time.time() - start_time
            
            # Évaluation de l'intégration
            integration_health = 0.0
            if "performance_metrics" in performance_summary:
                metrics = performance_summary["performance_metrics"]
                integration_health = metrics.get("average_effectiveness", 0.0)
            
            success = (
                performance_summary is not None and
                "health_status" in performance_summary and
                execution_time < self.test_config["max_test_duration"]
            )
            
            test_result = TestResult(
                test_name=test_name,
                success=success,
                execution_time=execution_time,
                effectiveness_score=integration_health,
                details={
                    "health_status": performance_summary.get("health_status", "unknown"),
                    "evolution_cycles": performance_summary.get("evolution_cycles", 0),
                    "performance_metrics": performance_summary.get("performance_metrics", {})
                }
            )
            
            self.test_results.append(test_result)
            
            if success:
                print(f"    ✅ Intégration réussie (santé: {integration_health:.2f})")
            else:
                print(f"    ❌ Intégration échouée")
                
        except Exception as e:
            execution_time = time.time() - start_time
            test_result = TestResult(
                test_name=test_name,
                success=False,
                execution_time=execution_time,
                effectiveness_score=0.0,
                details={},
                error_message=str(e)
            )
            self.test_results.append(test_result)
            print(f"    ❌ Erreur d'intégration : {e}")
    
    async def _run_performance_tests(self, daemon):
        """Teste les performances du daemon."""
        
        print("⚡ Tests de performance...")
        
        # Test de performance sous charge
        await self._test_performance_under_load(daemon)
    
    async def _test_performance_under_load(self, daemon):
        """Teste les performances sous charge."""
        
        test_name = "performance_under_load"
        start_time = time.time()
        
        try:
            print("  ⚡ Test de performance sous charge...")
            
            # Exécution de plusieurs introspections en parallèle
            tasks = []
            for i in range(3):  # 3 introspections simultanées
                task = daemon.conduct_full_introspection(f"load_test_{i}")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            execution_time = time.time() - start_time
            
            # Analyse des résultats
            successful_results = [r for r in results if not isinstance(r, Exception)]
            avg_effectiveness = 0.0
            
            if successful_results:
                avg_effectiveness = sum(r.effectiveness_score for r in successful_results) / len(successful_results)
            
            success = (
                len(successful_results) >= 2 and  # Au moins 2/3 réussis
                avg_effectiveness > 0.5 and
                execution_time < self.test_config["max_test_duration"]
            )
            
            test_result = TestResult(
                test_name=test_name,
                success=success,
                execution_time=execution_time,
                effectiveness_score=avg_effectiveness,
                details={
                    "total_tasks": len(tasks),
                    "successful_tasks": len(successful_results),
                    "failed_tasks": len(results) - len(successful_results),
                    "average_effectiveness": avg_effectiveness
                }
            )
            
            self.test_results.append(test_result)
            
            if success:
                print(f"    ✅ Performance acceptable ({len(successful_results)}/{len(tasks)} réussis)")
            else:
                print(f"    ❌ Performance insuffisante")
                
        except Exception as e:
            execution_time = time.time() - start_time
            test_result = TestResult(
                test_name=test_name,
                success=False,
                execution_time=execution_time,
                effectiveness_score=0.0,
                details={},
                error_message=str(e)
            )
            self.test_results.append(test_result)
            print(f"    ❌ Erreur de performance : {e}")
    
    async def _run_evolution_tests(self, daemon):
        """Teste les capacités d'évolution du daemon."""
        
        print("🌟 Tests d'évolution...")
        
        # Test d'évolution des capacités
        await self._test_capability_evolution(daemon)
    
    async def _test_capability_evolution(self, daemon):
        """Teste l'évolution des capacités."""
        
        test_name = "capability_evolution"
        start_time = time.time()
        
        try:
            print("  🌟 Test d'évolution des capacités...")
            
            # Simulation d'un feedback d'efficacité faible
            from core.introspection_conductor import EffectivenessScore
            
            low_effectiveness = EffectivenessScore(
                overall_score=0.5,
                feedback=["Needs improvement", "Low context injection"],
                improvement_areas=["context_injection", "prompt_optimization"]
            )
            
            evolution_result = await daemon.evolve_capabilities(low_effectiveness)
            
            execution_time = time.time() - start_time
            
            success = (
                evolution_result is not None and
                evolution_result.get("success", False) and
                execution_time < self.test_config["max_test_duration"]
            )
            
            effectiveness = 0.8 if success else 0.3  # Score basé sur le succès
            
            test_result = TestResult(
                test_name=test_name,
                success=success,
                execution_time=execution_time,
                effectiveness_score=effectiveness,
                details={
                    "evolution_success": evolution_result.get("success", False),
                    "improvements": evolution_result.get("improvements", []),
                    "config_updates": evolution_result.get("config_updates", {})
                }
            )
            
            self.test_results.append(test_result)
            
            if success:
                print(f"    ✅ Évolution réussie")
            else:
                print(f"    ❌ Évolution échouée")
                
        except Exception as e:
            execution_time = time.time() - start_time
            test_result = TestResult(
                test_name=test_name,
                success=False,
                execution_time=execution_time,
                effectiveness_score=0.0,
                details={},
                error_message=str(e)
            )
            self.test_results.append(test_result)
            print(f"    ❌ Erreur d'évolution : {e}")
    
    async def _analyze_test_results(self, total_time: float) -> DaemonTestSuite:
        """Analyse les résultats des tests."""
        
        successful_tests = [t for t in self.test_results if t.success]
        failed_tests = [t for t in self.test_results if not t.success]
        
        overall_success = len(failed_tests) == 0
        average_effectiveness = sum(t.effectiveness_score for t in self.test_results) / len(self.test_results)
        
        return DaemonTestSuite(
            test_results=self.test_results,
            overall_success=overall_success,
            total_execution_time=total_time,
            average_effectiveness=average_effectiveness
        )
    
    async def _trigger_daemon_evolution(self, daemon, test_suite: DaemonTestSuite):
        """Déclenche l'évolution du daemon si nécessaire."""
        
        print("🔄 Déclenchement de l'évolution du daemon...")
        
        # Analyse des échecs pour créer un feedback d'évolution
        failed_tests = [t for t in test_suite.test_results if not t.success]
        improvement_areas = []
        
        for test in failed_tests:
            if "prompt" in test.test_name:
                improvement_areas.append("prompt_generation")
            elif "context" in test.test_name:
                improvement_areas.append("context_injection")
            elif "performance" in test.test_name:
                improvement_areas.append("performance_optimization")
            else:
                improvement_areas.append("general_improvement")
        
        # Création du feedback d'évolution
        from core.introspection_conductor import EffectivenessScore
        
        evolution_feedback = EffectivenessScore(
            overall_score=test_suite.average_effectiveness,
            feedback=[f"Test failed: {t.test_name}" for t in failed_tests],
            improvement_areas=list(set(improvement_areas))
        )
        
        # Déclenchement de l'évolution
        try:
            evolution_result = await daemon.evolve_capabilities(evolution_feedback)
            
            if evolution_result.get("success", False):
                print("✅ Évolution du daemon réussie")
                print(f"   Améliorations : {evolution_result.get('improvements', [])}")
            else:
                print("⚠️ Évolution du daemon partielle")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'évolution : {e}")
    
    async def _generate_test_report(self, test_suite: DaemonTestSuite):
        """Génère un rapport de tests détaillé."""
        
        print("\n" + "="*60)
        print("📊 RAPPORT DE TESTS - INTROSPECTION DAEMON")
        print("="*60)
        
        # Résumé global
        print(f"🎯 Résultat global : {'✅ SUCCÈS' if test_suite.overall_success else '❌ ÉCHEC'}")
        print(f"⏱️ Temps total : {test_suite.total_execution_time:.2f}s")
        print(f"📊 Efficacité moyenne : {test_suite.average_effectiveness:.2f}")
        print(f"🔄 Évolution déclenchée : {'Oui' if test_suite.evolution_triggered else 'Non'}")
        
        # Détails par test
        print(f"\n📋 Détails des tests ({len(test_suite.test_results)} tests) :")
        
        for test in test_suite.test_results:
            status = "✅" if test.success else "❌"
            print(f"  {status} {test.test_name}")
            print(f"     Temps: {test.execution_time:.2f}s | Efficacité: {test.effectiveness_score:.2f}")
            
            if test.error_message:
                print(f"     Erreur: {test.error_message}")
        
        # Recommandations
        print(f"\n🎯 Recommandations :")
        
        if test_suite.average_effectiveness < 0.7:
            print("  - Améliorer l'efficacité globale du daemon")
        
        failed_tests = [t for t in test_suite.test_results if not t.success]
        if failed_tests:
            print(f"  - Corriger les {len(failed_tests)} tests échoués")
        
        if test_suite.total_execution_time > 20.0:
            print("  - Optimiser les performances (temps d'exécution élevé)")
        
        print("="*60)

# Fonction principale de test
async def run_introspection_daemon_tests():
    """Exécute les tests complets du IntrospectionDaemon."""
    
    print("🧪 Démarrage des tests complets du IntrospectionDaemon...")
    
    tester = IntrospectionDaemonTester()
    test_suite = await tester.run_comprehensive_test_suite()
    
    # Retour du résultat
    return test_suite.overall_success, test_suite.average_effectiveness

if __name__ == "__main__":
    # Exécution des tests
    async def main():
        success, effectiveness = await run_introspection_daemon_tests()
        
        print(f"\n🎯 Résultat final :")
        print(f"   Succès : {'✅' if success else '❌'}")
        print(f"   Efficacité : {effectiveness:.2f}")
        
        # Code de sortie
        exit_code = 0 if success and effectiveness > 0.7 else 1
        print(f"   Code de sortie : {exit_code}")
        
        return exit_code
    
    exit_code = asyncio.run(main())
    exit(exit_code)
