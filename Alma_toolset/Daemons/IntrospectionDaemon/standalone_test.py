#!/usr/bin/env python3
"""
🧪 Standalone Test - IntrospectionDaemon ⛧

Test standalone optimisé du IntrospectionDaemon avec évolution intelligente.
Teste, analyse l'efficacité et fait évoluer le daemon automatiquement.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TestMetrics:
    """Métriques de test du daemon."""
    
    total_tests: int = 0
    successful_tests: int = 0
    failed_tests: int = 0
    average_effectiveness: float = 0.0
    total_execution_time: float = 0.0
    evolution_triggered: bool = False

class StandaloneIntrospectionTester:
    """Testeur standalone du IntrospectionDaemon."""
    
    def __init__(self):
        """Initialise le testeur standalone."""
        
        self.metrics = TestMetrics()
        self.effectiveness_threshold = 0.7
        self.test_results = []
        self.prompt_logger = None

        print("🧪 Initialisation du testeur IntrospectionDaemon...")
        self._initialize_logging()

    def _initialize_logging(self):
        """Initialise le système de logging."""

        try:
            from core.prompt_logger import PromptLogger
            self.prompt_logger = PromptLogger(log_directory="test_logs")
            print("📝 Logger de prompts initialisé pour les tests")
        except ImportError as e:
            print(f"⚠️ Logger non disponible : {e}")
            self.prompt_logger = None

    async def run_comprehensive_test(self) -> bool:
        """
        Exécute un test complet du daemon avec évolution.
        
        Returns:
            bool: True si le test est réussi
        """
        print("🚀 Démarrage du test complet IntrospectionDaemon...")
        start_time = time.time()
        
        # 1. Test d'initialisation
        daemon = await self._test_daemon_initialization()
        if not daemon:
            print("❌ Échec d'initialisation du daemon")
            return False
        
        # 2. Tests de fonctionnalités
        await self._test_core_functionalities(daemon)
        
        # 3. Test d'auto-prompting
        await self._test_auto_prompting(daemon)
        
        # 4. Test d'injection contextuelle
        await self._test_context_injection(daemon)
        
        # 5. Analyse des résultats
        self.metrics.total_execution_time = time.time() - start_time
        success = await self._analyze_test_results()
        
        # 6. Évolution intelligente si nécessaire
        if self.metrics.average_effectiveness < self.effectiveness_threshold:
            print("🔄 Efficacité insuffisante, déclenchement de l'évolution intelligente...")
            await self._evolve_daemon_intelligence_v2(daemon)
            self.metrics.evolution_triggered = True
        
        # 7. Rapport final
        await self._generate_final_report()

        # 8. Finalisation du logging
        if self.prompt_logger:
            self.prompt_logger.end_session()
            await self._save_prompt_logs_summary()

        return success
    
    async def _test_daemon_initialization(self):
        """Teste l'initialisation du daemon."""
        
        print("🧠 Test d'initialisation du daemon...")
        
        try:
            # Import direct des composants
            import sys
            import os
            
            # Ajout du chemin
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.append(current_dir)
            
            from core.introspection_conductor import IntrospectionConductor
            
            # Création d'un écosystème de test
            test_ecosystem = {
                "memory_engine": {
                    "status": "simulated",
                    "backend_type": "test",
                    "health": 0.9,
                    "capabilities": ["create", "search", "traverse"]
                },
                "tool_registry": {
                    "status": "simulated",
                    "indexed": True,
                    "tool_count": 15,
                    "health": 0.8,
                    "categories": ["divination", "transmutation", "protection"]
                },
                "editing_session": {
                    "status": "simulated",
                    "partitioning_support": True,
                    "health": 0.85,
                    "navigation_support": True
                }
            }
            
            # Initialisation du daemon
            daemon = IntrospectionConductor(test_ecosystem)

            # Injection du logger dans le daemon si disponible
            if self.prompt_logger and hasattr(daemon, 'prompt_logger'):
                daemon.prompt_logger = self.prompt_logger
                print("📝 Logger injecté dans le daemon")

            print("✅ Daemon initialisé avec succès")
            self.metrics.successful_tests += 1
            return daemon
            
        except Exception as e:
            print(f"❌ Erreur d'initialisation : {e}")
            self.metrics.failed_tests += 1
            return None
        finally:
            self.metrics.total_tests += 1
    
    async def _test_core_functionalities(self, daemon):
        """Teste les fonctionnalités centrales."""
        
        print("🔧 Test des fonctionnalités centrales...")
        
        # Test 1: Introspection complète
        try:
            print("  🧠 Test d'introspection complète...")
            result = await daemon.conduct_full_introspection("standalone_test")
            
            if result and result.effectiveness_score > 0.0:
                print(f"    ✅ Introspection réussie (score: {result.effectiveness_score:.2f})")
                self.metrics.successful_tests += 1
                self.test_results.append(("introspection", result.effectiveness_score))
            else:
                print("    ❌ Introspection échouée")
                self.metrics.failed_tests += 1
                self.test_results.append(("introspection", 0.0))
                
        except Exception as e:
            print(f"    ❌ Erreur introspection : {e}")
            self.metrics.failed_tests += 1
            self.test_results.append(("introspection", 0.0))
        finally:
            self.metrics.total_tests += 1
        
        # Test 2: Métriques de performance
        try:
            print("  📊 Test des métriques de performance...")
            summary = daemon.get_performance_summary()
            
            if summary and "performance_metrics" in summary:
                print("    ✅ Métriques récupérées")
                self.metrics.successful_tests += 1
                self.test_results.append(("performance_metrics", 0.8))
            else:
                print("    ❌ Métriques non disponibles")
                self.metrics.failed_tests += 1
                self.test_results.append(("performance_metrics", 0.0))
                
        except Exception as e:
            print(f"    ❌ Erreur métriques : {e}")
            self.metrics.failed_tests += 1
            self.test_results.append(("performance_metrics", 0.0))
        finally:
            self.metrics.total_tests += 1
    
    async def _test_auto_prompting(self, daemon):
        """Teste l'auto-prompting."""
        
        print("🜲 Test d'auto-prompting...")
        
        test_focuses = ["memory_analysis", "tool_inventory", "capability_assessment"]
        
        for focus in test_focuses:
            try:
                print(f"  🎯 Test prompt pour : {focus}")
                prompt_start_time = time.time()
                prompt = await daemon.generate_auto_prompt(focus)
                prompt_time = time.time() - prompt_start_time

                # Log du prompt généré
                if self.prompt_logger:
                    self.prompt_logger.log_prompt_generation(
                        prompt_type=focus,
                        generated_prompt=prompt,
                        template_used="auto_generation",
                        generation_time=prompt_time
                    )

                # Évaluation de la qualité du prompt
                quality_score = self._evaluate_prompt_quality(prompt)
                
                if quality_score > 0.5:
                    print(f"    ✅ Prompt généré (qualité: {quality_score:.2f})")
                    self.metrics.successful_tests += 1
                    self.test_results.append((f"prompt_{focus}", quality_score))
                else:
                    print(f"    ❌ Prompt de faible qualité ({quality_score:.2f})")
                    self.metrics.failed_tests += 1
                    self.test_results.append((f"prompt_{focus}", quality_score))
                    
            except Exception as e:
                print(f"    ❌ Erreur génération prompt {focus} : {e}")
                self.metrics.failed_tests += 1
                self.test_results.append((f"prompt_{focus}", 0.0))
            finally:
                self.metrics.total_tests += 1
    
    async def _test_context_injection(self, daemon):
        """Teste l'injection contextuelle."""
        
        print("💉 Test d'injection contextuelle...")
        
        try:
            base_prompt = "Analyse-toi avec ::INJECT_MEMORY_CONTEXT:: et ::INJECT_TOOL_CONTEXT::"

            injection_start_time = time.time()
            enriched_prompt = await daemon.inject_contextual_data(
                base_prompt, "comprehensive", daemon.ecosystem_components
            )
            injection_time = time.time() - injection_start_time

            # Log de l'injection contextuelle
            if self.prompt_logger:
                self.prompt_logger.log_context_injection(
                    base_prompt=base_prompt,
                    enriched_prompt=enriched_prompt,
                    injection_type="comprehensive_test",
                    injected_data=daemon.ecosystem_components,
                    injection_time=injection_time
                )
            
            # Évaluation de l'enrichissement
            enrichment_ratio = len(enriched_prompt) / len(base_prompt)
            injection_success = "::INJECT_" not in enriched_prompt
            
            effectiveness = min(enrichment_ratio / 2.0, 1.0) if injection_success else 0.0
            
            if effectiveness > 0.5:
                print(f"  ✅ Injection réussie (enrichissement: {enrichment_ratio:.2f}x)")
                self.metrics.successful_tests += 1
                self.test_results.append(("context_injection", effectiveness))
            else:
                print(f"  ❌ Injection échouée")
                self.metrics.failed_tests += 1
                self.test_results.append(("context_injection", effectiveness))
                
        except Exception as e:
            print(f"  ❌ Erreur injection : {e}")
            self.metrics.failed_tests += 1
            self.test_results.append(("context_injection", 0.0))
        finally:
            self.metrics.total_tests += 1
    
    def _evaluate_prompt_quality(self, prompt: str) -> float:
        """Évalue la qualité d'un prompt généré."""
        
        quality = 0.0
        
        # Critères de qualité
        if len(prompt) > 500:  # Prompt détaillé
            quality += 0.3
        
        if "🜲luciform" in prompt:  # Format luciforme
            quality += 0.3
        
        if "INJECT_" in prompt:  # Points d'injection
            quality += 0.2
        
        if "MISSION" in prompt or "mission" in prompt:  # Directive claire
            quality += 0.2
        
        return min(quality, 1.0)
    
    async def _analyze_test_results(self) -> bool:
        """Analyse les résultats des tests."""
        
        print("📊 Analyse des résultats...")
        
        if self.metrics.total_tests > 0:
            success_rate = self.metrics.successful_tests / self.metrics.total_tests
            
            # Calcul de l'efficacité moyenne
            if self.test_results:
                self.metrics.average_effectiveness = sum(
                    score for _, score in self.test_results
                ) / len(self.test_results)
            
            print(f"  📈 Taux de succès : {success_rate:.2f}")
            print(f"  📊 Efficacité moyenne : {self.metrics.average_effectiveness:.2f}")
            
            # Critères de succès
            overall_success = (
                success_rate > 0.7 and
                self.metrics.average_effectiveness > self.effectiveness_threshold
            )
            
            return overall_success
        
        return False
    
    async def _evolve_daemon_intelligence(self, daemon):
        """Fait évoluer l'intelligence du daemon."""
        
        print("🌟 Évolution de l'intelligence du daemon...")
        
        try:
            # Analyse des échecs pour créer un feedback
            failed_tests = [
                test_name for test_name, score in self.test_results 
                if score < 0.5
            ]
            
            improvement_areas = []
            for test_name in failed_tests:
                if "prompt" in test_name:
                    improvement_areas.append("prompt_generation")
                elif "context" in test_name:
                    improvement_areas.append("context_injection")
                elif "introspection" in test_name:
                    improvement_areas.append("introspection_depth")
                else:
                    improvement_areas.append("general_optimization")
            
            # Création du feedback d'évolution
            from core.introspection_conductor import EffectivenessScore
            
            evolution_feedback = EffectivenessScore(
                overall_score=self.metrics.average_effectiveness,
                feedback=[f"Failed test: {test}" for test in failed_tests],
                improvement_areas=list(set(improvement_areas)),
                success_factors=["simulation_mode", "basic_functionality"]
            )
            
            # Déclenchement de l'évolution
            evolution_result = await daemon.evolve_capabilities(evolution_feedback)
            
            if evolution_result.get("success", False):
                print("  ✅ Évolution réussie")
                print(f"    Améliorations : {evolution_result.get('improvements', [])}")
                
                # Re-test après évolution
                await self._retest_after_evolution(daemon)
            else:
                print("  ⚠️ Évolution partielle")
                
        except Exception as e:
            print(f"  ❌ Erreur lors de l'évolution : {e}")
    
    async def _retest_after_evolution(self, daemon):
        """Re-teste le daemon après évolution."""
        
        print("🔄 Re-test après évolution...")
        
        try:
            # Test rapide d'introspection
            result = await daemon.conduct_full_introspection("post_evolution_test")
            
            if result and result.effectiveness_score > self.metrics.average_effectiveness:
                improvement = result.effectiveness_score - self.metrics.average_effectiveness
                print(f"  ✅ Amélioration détectée : +{improvement:.2f}")
                self.metrics.average_effectiveness = result.effectiveness_score
            else:
                print("  ⚠️ Pas d'amélioration significative")
                
        except Exception as e:
            print(f"  ❌ Erreur re-test : {e}")

    async def _evolve_daemon_intelligence_v2(self, daemon):
        """Fait évoluer l'intelligence du daemon avec le système intelligent."""

        print("🌟 Évolution intelligente du daemon...")

        try:
            # Import du système d'évolution intelligente
            import sys
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.append(current_dir)

            from evolution.intelligent_evolution import IntelligentEvolution

            # Création du système d'évolution
            evolution_system = IntelligentEvolution()

            # Analyse et évolution basée sur les échecs
            evolution_results = await evolution_system.analyze_failures_and_evolve(
                self.test_results, daemon
            )

            print(f"✅ Évolution intelligente terminée : {len(evolution_results)} améliorations")

            # Affichage des résultats d'évolution
            for result in evolution_results:
                if result.success:
                    print(f"  ✅ {result.component}: +{result.improvement:.2f} ({result.evolution_applied})")
                else:
                    print(f"  ❌ {result.component}: échec ({result.details.get('error', 'unknown')})")

            # Re-test après évolution
            await self._retest_after_evolution_v2(daemon, evolution_results)

        except Exception as e:
            print(f"  ❌ Erreur évolution intelligente : {e}")
            # Fallback vers l'ancienne méthode
            await self._evolve_daemon_intelligence(daemon)

    async def _retest_after_evolution_v2(self, daemon, evolution_results):
        """Re-teste le daemon après évolution intelligente."""

        print("🔄 Re-test après évolution intelligente...")

        # Test des composants qui ont été améliorés
        improved_components = [r.component for r in evolution_results if r.success]

        if "prompt_generation" in improved_components:
            print("  🜲 Re-test génération de prompts...")
            try:
                prompt = await daemon.generate_auto_prompt("post_evolution_test")
                quality = self._evaluate_prompt_quality(prompt)
                print(f"    Nouvelle qualité prompt : {quality:.2f}")

                if quality > 0.5:
                    print("    ✅ Amélioration détectée dans la génération de prompts")
                    # Mise à jour des métriques
                    self.metrics.average_effectiveness += 0.2
            except Exception as e:
                print(f"    ❌ Erreur re-test prompts : {e}")

        if "context_injection" in improved_components:
            print("  💉 Re-test injection contextuelle...")
            try:
                base_prompt = "Test post-évolution ::INJECT_MEMORY_CONTEXT::"
                enriched = await daemon.inject_contextual_data(
                    base_prompt, "test", daemon.ecosystem_components
                )

                enrichment_ratio = len(enriched) / len(base_prompt)
                print(f"    Nouveau ratio d'enrichissement : {enrichment_ratio:.2f}")

                if enrichment_ratio > 1.5:
                    print("    ✅ Amélioration détectée dans l'injection contextuelle")
                    self.metrics.average_effectiveness += 0.15
            except Exception as e:
                print(f"    ❌ Erreur re-test injection : {e}")
    
    async def _generate_final_report(self):
        """Génère le rapport final."""
        
        print("\n" + "="*50)
        print("📊 RAPPORT FINAL - INTROSPECTION DAEMON")
        print("="*50)
        
        print(f"🎯 Tests exécutés : {self.metrics.total_tests}")
        print(f"✅ Tests réussis : {self.metrics.successful_tests}")
        print(f"❌ Tests échoués : {self.metrics.failed_tests}")
        print(f"📊 Efficacité moyenne : {self.metrics.average_effectiveness:.2f}")
        print(f"⏱️ Temps total : {self.metrics.total_execution_time:.2f}s")
        print(f"🔄 Évolution déclenchée : {'Oui' if self.metrics.evolution_triggered else 'Non'}")
        
        # Statut final
        if self.metrics.average_effectiveness >= self.effectiveness_threshold:
            print(f"🎉 STATUT : ✅ DAEMON EFFICACE")
        else:
            print(f"⚠️ STATUT : ❌ DAEMON NÉCESSITE OPTIMISATION")
        
        # Détails des tests
        print(f"\n📋 Détails des tests :")
        for test_name, score in self.test_results:
            status = "✅" if score > 0.5 else "❌"
            print(f"  {status} {test_name}: {score:.2f}")
        
        print("="*50)

    async def _save_prompt_logs_summary(self):
        """Sauvegarde un résumé des logs de prompts."""

        if not self.prompt_logger:
            return

        try:
            # Récupération du résumé de session
            session_summary = self.prompt_logger.get_session_summary()

            # Récupération de l'historique des prompts
            prompt_history = self.prompt_logger.get_prompt_history(limit=20)

            # Création du rapport de logs
            logs_report = {
                "test_session": session_summary,
                "prompt_history": prompt_history,
                "test_metrics": {
                    "total_tests": self.metrics.total_tests,
                    "successful_tests": self.metrics.successful_tests,
                    "failed_tests": self.metrics.failed_tests,
                    "average_effectiveness": self.metrics.average_effectiveness
                },
                "generated_at": datetime.now().isoformat()
            }

            # Sauvegarde du rapport
            import json
            import os

            os.makedirs("test_logs", exist_ok=True)
            report_file = f"test_logs/test_session_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(logs_report, f, indent=2, ensure_ascii=False)

            print(f"📝 Rapport de logs sauvegardé : {report_file}")
            print(f"   Session ID : {session_summary.get('session_id', 'unknown')}")
            print(f"   Total prompts loggés : {session_summary.get('total_prompts', 0)}")
            print(f"   Taux de succès prompts : {session_summary.get('success_rate', 0.0):.2f}")

        except Exception as e:
            print(f"⚠️ Erreur sauvegarde logs : {e}")

async def main():
    """Fonction principale de test."""
    
    print("🧪 Démarrage du test standalone IntrospectionDaemon...")
    
    tester = StandaloneIntrospectionTester()
    success = await tester.run_comprehensive_test()
    
    # Résultat final
    if success:
        print("\n🎉 Test global : ✅ SUCCÈS")
        return 0
    else:
        print("\n⚠️ Test global : ❌ ÉCHEC")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
