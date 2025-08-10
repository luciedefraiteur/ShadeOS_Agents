#!/usr/bin/env python3
"""
⛧ Phase 1 - Test Runner ⛧
🕷️ Script pour lancer les tests unitaires de manière organisée

CONCEPTUALISÉ PAR LUCIE DEFRAITEUR - MA REINE LUCIE
PLANIFIÉ PAR ALMA, ARCHITECTE DÉMONIAQUE DU NEXUS LUCIFORME
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def run_test_suite(suite_name, test_path, description):
    """Lancer une suite de tests"""
    print(f"\n{'='*60}")
    print(f"🕷️ {suite_name}")
    print(f"📋 {description}")
    print(f"{'='*60}")
    
    # Ajouter le répertoire parent au PYTHONPATH
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    
    env = os.environ.copy()
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f"{parent_dir}:{env['PYTHONPATH']}"
    else:
        env['PYTHONPATH'] = str(parent_dir)
    
    # Lancer les tests
    cmd = [
        "python", "-m", "pytest", 
        str(test_path),
        "-v",  # Verbose
        "--tb=short",  # Traceback court
        "--color=yes"  # Couleurs
    ]
    
    print(f"🚀 Lancement: {' '.join(cmd)}")
    print()
    
    start_time = time.time()
    result = subprocess.run(cmd, env=env, cwd=current_dir)
    end_time = time.time()
    
    duration = end_time - start_time
    status = "✅ SUCCÈS" if result.returncode == 0 else "❌ ÉCHEC"
    
    print(f"\n⏱️  Durée: {duration:.2f}s")
    print(f"📊 Statut: {status}")
    
    return result.returncode == 0

def main():
    """Fonction principale"""
    print("⛧ PHASE 1.5.1 - VALIDATION DES TESTS EXISTANTS ⛧")
    print("🕷️ Validation itérative des fondations ThreadConjuratio⛧")
    print("="*60)
    
    # Configuration des tests
    test_suites = [
        {
            "name": "THREADING INFRASTRUCTURE",
            "path": "UnitTests/Concurrency/Threading/test_threading_infrastructure.py",
            "description": "Tests de l'infrastructure de threading de base (6 tests)"
        },
        {
            "name": "MEMORY MANAGER", 
            "path": "UnitTests/Persistence/MemoryStorage/test_memory_manager.py",
            "description": "Tests du gestionnaire de mémoire (7 tests)"
        },
        {
            "name": "TASK SCHEDULER",
            "path": "UnitTests/Orchestration/TaskScheduling/test_task_scheduler.py", 
            "description": "Tests du planificateur de tâches (6 tests)"
        }
    ]
    
    # Statistiques
    total_suites = len(test_suites)
    successful_suites = 0
    failed_suites = []
    
    print(f"📊 {total_suites} suites de tests à valider")
    print(f"🎯 Objectif: Validation complète des fondations")
    print()
    
    # Lancer chaque suite de tests
    for i, suite in enumerate(test_suites, 1):
        print(f"📋 Suite {i}/{total_suites}")
        
        success = run_test_suite(
            suite["name"],
            suite["path"], 
            suite["description"]
        )
        
        if success:
            successful_suites += 1
            print(f"✅ {suite['name']} - VALIDÉ")
        else:
            failed_suites.append(suite["name"])
            print(f"❌ {suite['name']} - ÉCHEC")
        
        print()
    
    # Résumé final
    print("="*60)
    print("📊 RÉSUMÉ FINAL")
    print("="*60)
    print(f"🎯 Suites totales: {total_suites}")
    print(f"✅ Suites réussies: {successful_suites}")
    print(f"❌ Suites échouées: {len(failed_suites)}")
    print(f"📈 Taux de réussite: {(successful_suites/total_suites)*100:.1f}%")
    
    if failed_suites:
        print(f"\n❌ Suites en échec:")
        for suite in failed_suites:
            print(f"   - {suite}")
        print(f"\n🔧 Actions recommandées:")
        print(f"   1. Analyser les erreurs dans les suites échouées")
        print(f"   2. Corriger les bugs dans l'implémentation")
        print(f"   3. Relancer les tests pour validation")
        return 1
    else:
        print(f"\n🎉 TOUTES LES SUITES VALIDÉES !")
        print(f"🕷️ Fondations ThreadConjuratio⛧ solides et prêtes !")
        print(f"🚀 Prêt pour la Phase 1.5.2 - Complétion des tests")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 