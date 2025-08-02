#!/usr/bin/env python3
"""
🧠 IAIntrospectionDaemon - Script Principal ⛧

Script principal pour tester et utiliser le Daemon Introspectif IA.
Utilise de vrais moteurs IA (Ollama/OpenAI) pour l'introspection.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Ajout du répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from core.ia_introspection_conductor import IAIntrospectionConductor


async def main():
    """Fonction principale du daemon."""
    
    parser = argparse.ArgumentParser(
        description="🧠 IAIntrospectionDaemon - Daemon d'introspection IA-powered",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python main.py --focus comprehensive
  python main.py --engine ollama --model qwen2.5:7b-instruct
  python main.py --focus memory --save-results
  python main.py --test-engines
        """
    )
    
    parser.add_argument(
        "--focus", 
        choices=["comprehensive", "memory", "tools", "editing"],
        default="comprehensive",
        help="Focus de l'introspection (défaut: comprehensive)"
    )
    
    parser.add_argument(
        "--engine",
        choices=["ollama", "openai"],
        default="ollama",
        help="Moteur IA principal (défaut: ollama)"
    )
    
    parser.add_argument(
        "--fallback-engine",
        choices=["ollama", "openai"],
        default="openai",
        help="Moteur IA de secours (défaut: openai)"
    )
    
    parser.add_argument(
        "--model",
        default=None,
        help="Modèle spécifique à utiliser (ex: qwen2.5:7b-instruct)"
    )
    
    parser.add_argument(
        "--test-engines",
        action="store_true",
        help="Teste tous les moteurs IA disponibles"
    )
    
    parser.add_argument(
        "--save-results",
        action="store_true",
        help="Sauvegarde les résultats dans les logs"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Mode verbeux"
    )
    
    args = parser.parse_args()
    
    print("🧠 IAIntrospectionDaemon - Démarrage")
    print("=" * 50)
    
    try:
        # Création du chef d'orchestre
        conductor = IAIntrospectionConductor(
            primary_engine=args.engine,
            fallback_engine=args.fallback_engine
        )
        
        # Configuration du modèle si spécifié
        if args.model:
            conductor.ai_factory.configure_engine(args.engine, model=args.model)
        
        # Configuration de la sauvegarde
        conductor.config["save_results"] = args.save_results
        
        # Test des moteurs IA si demandé
        if args.test_engines:
            print("🤖 Test des moteurs IA...")
            engine_status = await conductor.test_ai_engines()
            
            print("\n📊 Statut des moteurs IA:")
            for engine, status in engine_status.items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {engine}: {'Disponible' if status else 'Non disponible'}")
            
            if not any(engine_status.values()):
                print("\n❌ Aucun moteur IA disponible. Vérifiez:")
                print("  - Ollama: ollama serve")
                print("  - OpenAI: OPENAI_API_KEY")
                return 1
            
            print()
        
        # Initialisation du daemon
        print("🔧 Initialisation du daemon...")
        success = await conductor.initialize()
        
        if not success:
            print("❌ Échec d'initialisation du daemon")
            return 1
        
        print("✅ Daemon initialisé avec succès")
        
        # Exécution de l'introspection
        print(f"\n🧠 Démarrage introspection: {args.focus}")
        print("-" * 30)
        
        result = await conductor.conduct_ai_introspection(args.focus)
        
        # Affichage des résultats
        print(f"\n📊 Résultats de l'introspection:")
        print(f"  ✅ Succès: {result.success}")
        print(f"  ⏱️ Temps d'exécution: {result.execution_time:.2f}s")
        print(f"  🤖 Moteur utilisé: {result.ai_engine_used}")
        
        if result.errors:
            print(f"  ❌ Erreurs: {len(result.errors)}")
            for error in result.errors:
                print(f"    - {error}")
        
        # Affichage détaillé si mode verbeux
        if args.verbose:
            print(f"\n🔍 Détails des analyses:")
            
            if result.memory_analysis:
                print(f"  🧠 MemoryEngine: {'✅' if result.memory_analysis.get('success') else '❌'}")
            
            if result.tool_analysis:
                print(f"  🛠️ ToolRegistry: {'✅' if result.tool_analysis.get('success') else '❌'}")
            
            if result.editing_analysis:
                print(f"  📝 EditingSession: {'✅' if result.editing_analysis.get('success') else '❌'}")
            
            if result.synthesis_insights:
                print(f"  🧠 Synthèse: {'✅' if result.synthesis_insights.get('success') else '❌'}")
        
        # Sauvegarde des résultats
        if args.save_results:
            print(f"\n💾 Résultats sauvegardés dans les logs")
        
        print(f"\n🎉 Introspection terminée avec succès!")
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Interruption utilisateur")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


async def test_individual_components():
    """Test des composants individuels."""
    print("🧪 Test des composants individuels...")
    
    try:
        # Test des moteurs IA
        from ai_engines.ai_engine_factory import AIEngineFactory
        factory = AIEngineFactory()
        
        print("🤖 Test des moteurs IA...")
        engine_status = await factory.test_all_engines()
        print(f"Statut: {engine_status}")
        
        # Test du navigateur MemoryEngine
        if engine_status.get("ollama", False):
            print("🧠 Test du navigateur MemoryEngine...")
            from ai_engines.ollama_engine import OllamaEngine
            from core.memory_engine_navigator import MemoryEngineNavigator
            
            ai_engine = OllamaEngine()
            
            # Test avec MemoryEngine simulé
            class MockMemoryEngine:
                def get_memory_statistics(self):
                    return {"total": 0, "strata": {}}
                def find_by_strata(self, strata):
                    return []
                backend_type = "filesystem"
            
            navigator = MemoryEngineNavigator(MockMemoryEngine(), ai_engine)
            result = await navigator.explore_memory_strata()
            print(f"Résultat navigation: {result.get('success', False)}")
        
        print("✅ Tests terminés")
        
    except Exception as e:
        print(f"❌ Erreur tests: {e}")


if __name__ == "__main__":
    # Vérification des arguments pour les tests
    if len(sys.argv) > 1 and sys.argv[1] == "--test-components":
        asyncio.run(test_individual_components())
    else:
        exit_code = asyncio.run(main())
        sys.exit(exit_code) 