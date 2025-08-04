# ⛧ Créé par Alma, Architecte Démoniaque ⛧
# 🕷️ Comparaison OpenAI vs Local LLM Assistant

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

from Assistants.EditingSession.Tools.openai_assistants import OpenAIAssistantsIntegration
from Assistants.Specialist.V7_safe import create_local_llm_assistant_v7_phase2_enhanced
from MemoryEngine.core.engine import MemoryEngine


class ComparisonLogger:
    """Logger pour la comparaison OpenAI vs Local LLM."""
    
    def __init__(self):
        self.logs_dir = Path("IAIntrospectionDaemons/logs") / datetime.now().strftime('%Y-%m-%d')
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.comparison_file = self.logs_dir / f"comparison_openai_local_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.comparison_data = {
            "test_time": datetime.now().isoformat(),
            "test_scenarios": [],
            "summary": {}
        }
    
    def log_scenario(self, scenario_name: str, openai_result: Dict, local_result: Dict):
        """Log un scénario de test."""
        scenario_data = {
            "scenario": scenario_name,
            "openai": openai_result,
            "local": local_result,
            "comparison": self._compare_results(openai_result, local_result)
        }
        
        self.comparison_data["test_scenarios"].append(scenario_data)
    
    def _compare_results(self, openai_result: Dict, local_result: Dict) -> Dict:
        """Compare les résultats OpenAI et Local."""
        comparison = {
            "response_time": {
                "openai": openai_result.get("duration", 0),
                "local": local_result.get("duration", 0),
                "difference": local_result.get("duration", 0) - openai_result.get("duration", 0)
            },
            "success_rate": {
                "openai": openai_result.get("success", False),
                "local": local_result.get("success", False)
            },
            "tool_calls": {
                "openai": openai_result.get("tool_calls", 0),
                "local": local_result.get("tool_calls", 0)
            },
            "response_quality": {
                "openai": len(openai_result.get("response", "")),
                "local": len(local_result.get("response", ""))
            }
        }
        
        return comparison
    
    def save_comparison(self):
        """Sauvegarde la comparaison."""
        with open(self.comparison_file, 'w', encoding='utf-8') as f:
            json.dump(self.comparison_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Comparaison sauvegardée: {self.comparison_file}")


class OpenAIvsLocalComparison:
    """
    Comparaison entre OpenAI Assistants et notre assistant local LLM.
    """
    
    def __init__(self):
        self.logger = ComparisonLogger()
        self.memory_engine = MemoryEngine()
        
        # Initialiser OpenAI (si disponible)
        try:
            from Assistants.EditingSession.Tools.tool_registry import ToolRegistry
            tool_registry = ToolRegistry(self.memory_engine)
            tool_registry.initialize()
            self.openai_integration = OpenAIAssistantsIntegration(tool_registry)
            
            # Créer l'assistant avec les outils
            self.openai_integration.create_assistant_with_tools()
            
            self.openai_available = True
            print("✅ OpenAI Assistants disponible")
        except Exception as e:
            self.openai_available = False
            print(f"❌ OpenAI Assistants non disponible: {e}")
        
        # Initialiser notre assistant local
        self.local_assistant = create_local_llm_assistant_v7_phase2_enhanced("Alma Local LLM Comparison", self.memory_engine)
        print("✅ Assistant local initialisé")
    
    def test_scenario(self, scenario_name: str, message: str) -> Dict[str, Any]:
        """Teste un scénario avec les deux assistants."""
        print(f"\n🔍 Test du scénario: {scenario_name}")
        print(f"📝 Message: {message}")
        
        results = {
            "scenario": scenario_name,
            "message": message,
            "openai": None,
            "local": None
        }
        
        # Test OpenAI
        if self.openai_available:
            print("\n🤖 Test OpenAI...")
            start_time = time.time()
            try:
                openai_response = self.openai_integration.send_message(message)
                openai_duration = time.time() - start_time
                
                results["openai"] = {
                    "success": True,
                    "response": openai_response,
                    "duration": openai_duration,
                    "tool_calls": 0  # À extraire des logs si nécessaire
                }
                print(f"✅ OpenAI: {openai_duration:.2f}s")
                
            except Exception as e:
                results["openai"] = {
                    "success": False,
                    "error": str(e),
                    "duration": time.time() - start_time,
                    "tool_calls": 0
                }
                print(f"❌ OpenAI: {e}")
        else:
            results["openai"] = {
                "success": False,
                "error": "OpenAI non disponible",
                "duration": 0,
                "tool_calls": 0
            }
        
        # Test Local LLM
        print("\n🕷️ Test Local LLM...")
        start_time = time.time()
        try:
            local_response = self.local_assistant.send_message(message)
            local_duration = time.time() - start_time
            
            results["local"] = {
                "success": True,
                "response": local_response,
                "duration": local_duration,
                "tool_calls": len(self.local_assistant.logger.conversation_data["tool_executions"])
            }
            print(f"✅ Local LLM: {local_duration:.2f}s")
            
        except Exception as e:
            results["local"] = {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time,
                "tool_calls": 0
            }
            print(f"❌ Local LLM: {e}")
        
        # Log du scénario
        self.logger.log_scenario(scenario_name, results["openai"], results["local"])
        
        return results
    
    def run_comparison_tests(self):
        """Exécute tous les tests de comparaison."""
        print("🕷️ Comparaison OpenAI vs Local LLM Assistant")
        print("=" * 60)
        
        test_scenarios = [
            {
                "name": "Liste des outils",
                "message": "Quels outils as-tu disponibles ?"
            },
            {
                "name": "Analyse de fichier",
                "message": "Peux-tu analyser le fichier TestProject/buggy_calculator.py ?"
            },
            {
                "name": "Demande de correction",
                "message": "Peux-tu corriger les bugs détectés dans le fichier ?"
            }
        ]
        
        all_results = []
        
        for scenario in test_scenarios:
            result = self.test_scenario(scenario["name"], scenario["message"])
            all_results.append(result)
            
            # Afficher la comparaison
            self._display_scenario_comparison(result)
        
        # Sauvegarder les résultats
        self.logger.save_comparison()
        
        # Afficher le résumé
        self._display_summary(all_results)
    
    def _display_scenario_comparison(self, result: Dict):
        """Affiche la comparaison d'un scénario."""
        print(f"\n📊 Comparaison - {result['scenario']}:")
        print("-" * 40)
        
        openai_result = result["openai"]
        local_result = result["local"]
        
        # Temps de réponse
        print(f"⏱️  Temps de réponse:")
        print(f"   OpenAI: {openai_result['duration']:.2f}s")
        print(f"   Local:  {local_result['duration']:.2f}s")
        
        if openai_result['success'] and local_result['success']:
            diff = local_result['duration'] - openai_result['duration']
            print(f"   Différence: {diff:+.2f}s ({'plus rapide' if diff < 0 else 'plus lent'})")
        
        # Succès
        print(f"✅ Succès:")
        print(f"   OpenAI: {'Oui' if openai_result['success'] else 'Non'}")
        print(f"   Local:  {'Oui' if local_result['success'] else 'Non'}")
        
        # Appels d'outils
        print(f"🔧 Appels d'outils:")
        print(f"   OpenAI: {openai_result['tool_calls']}")
        print(f"   Local:  {local_result['tool_calls']}")
        
        # Qualité de réponse
        if openai_result['success'] and local_result['success']:
            openai_length = len(openai_result['response'])
            local_length = len(local_result['response'])
            print(f"📝 Longueur de réponse:")
            print(f"   OpenAI: {openai_length} caractères")
            print(f"   Local:  {local_length} caractères")
    
    def _display_summary(self, results: List[Dict]):
        """Affiche le résumé de la comparaison."""
        print(f"\n🎯 RÉSUMÉ DE LA COMPARAISON")
        print("=" * 60)
        
        # Statistiques globales
        total_scenarios = len(results)
        openai_success = sum(1 for r in results if r["openai"]["success"])
        local_success = sum(1 for r in results if r["local"]["success"])
        
        openai_total_time = sum(r["openai"]["duration"] for r in results if r["openai"]["success"])
        local_total_time = sum(r["local"]["duration"] for r in results if r["local"]["success"])
        
        openai_total_tools = sum(r["openai"].get("tool_calls", 0) for r in results)
        local_total_tools = sum(r["local"].get("tool_calls", 0) for r in results)
        
        print(f"📊 Statistiques globales:")
        print(f"   Scénarios testés: {total_scenarios}")
        print(f"   Succès OpenAI: {openai_success}/{total_scenarios} ({openai_success/total_scenarios*100:.1f}%)")
        print(f"   Succès Local: {local_success}/{total_scenarios} ({local_success/total_scenarios*100:.1f}%)")
        
        if openai_success > 0 and local_success > 0:
            print(f"   Temps total OpenAI: {openai_total_time:.2f}s")
            print(f"   Temps total Local: {local_total_time:.2f}s")
            print(f"   Différence: {local_total_time - openai_total_time:+.2f}s")
        
        print(f"   Outils OpenAI: {openai_total_tools}")
        print(f"   Outils Local: {local_total_tools}")
        
        # Recommandations
        print(f"\n💡 Recommandations:")
        
        if local_success == total_scenarios:
            print("   ✅ Assistant local: Très fiable")
        elif local_success > openai_success:
            print("   ✅ Assistant local: Plus fiable que OpenAI")
        elif local_success < openai_success:
            print("   ⚠️  Assistant local: Moins fiable que OpenAI")
        else:
            print("   🤝 Assistant local: Fiabilité similaire à OpenAI")
        
        if local_total_time < openai_total_time:
            print("   ⚡ Assistant local: Plus rapide")
        elif local_total_time > openai_total_time:
            print("   🐌 Assistant local: Plus lent")
        else:
            print("   ⏱️  Assistant local: Vitesse similaire")
        
        if local_total_tools > openai_total_tools:
            print("   🔧 Assistant local: Plus d'outils utilisés")
        elif local_total_tools < openai_total_tools:
            print("   🔧 Assistant local: Moins d'outils utilisés")
        else:
            print("   🔧 Assistant local: Utilisation d'outils similaire")


def main():
    """Test de comparaison OpenAI vs Local LLM."""
    comparison = OpenAIvsLocalComparison()
    comparison.run_comparison_tests()


if __name__ == "__main__":
    main() 