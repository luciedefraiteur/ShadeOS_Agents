#!/usr/bin/env python3
"""
🧪 Runner Principal - Tests Unitaires MemoryEngine ⛧

Script principal pour exécuter tous les tests unitaires du MemoryEngine
et identifier les dépendances manquantes.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import sys
import os
import unittest
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def run_all_tests():
    """Exécute tous les tests unitaires."""
    
    print("🧪 ⛧ SUITE COMPLÈTE DE TESTS MEMORYENGINE ⛧ 🧪")
    print("=" * 60)
    
    # Importer les modules de test
    test_modules = [
        "test_memory_engine_core",
        "test_extensions", 
        "test_editing_session",
        "test_process_manager"
    ]
    
    # Résultats globaux
    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0
    missing_dependencies = []
    
    # Exécuter chaque module de test
    for module_name in test_modules:
        print(f"\n🔍 Test du module: {module_name}")
        print("-" * 40)
        
        try:
            # Importer le module de test
            module = __import__(f"MemoryEngine.UnitTests.{module_name}", fromlist=['run_tests'])
            
            # Exécuter les tests
            result = module.run_tests()
            
            # Collecter les statistiques
            total_tests += result.testsRun
            total_failures += len(result.failures)
            total_errors += len(result.errors)
            total_skipped += len(result.skipped)
            
            # Analyser les erreurs pour identifier les dépendances manquantes
            for test, traceback in result.errors:
                if "ImportError" in str(traceback):
                    missing_dependencies.append(f"{module_name}: {test}")
                    
        except ImportError as e:
            print(f"❌ Module de test non trouvé: {module_name}")
            missing_dependencies.append(f"{module_name}: Module non trouvé")
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution des tests {module_name}: {e}")
            missing_dependencies.append(f"{module_name}: Erreur d'exécution")
    
    # Résumé global
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ GLOBAL DES TESTS")
    print("=" * 60)
    print(f"Tests exécutés: {total_tests}")
    print(f"Échecs: {total_failures}")
    print(f"Erreurs: {total_errors}")
    print(f"Tests ignorés: {total_skipped}")
    print(f"Taux de succès: {((total_tests - total_failures - total_errors) / max(total_tests, 1)) * 100:.1f}%")
    
    # Analyse des dépendances manquantes
    if missing_dependencies:
        print(f"\n⚠️  DÉPENDANCES MANQUANTES IDENTIFIÉES:")
        print("-" * 40)
        for dep in missing_dependencies:
            print(f"  • {dep}")
        
        print(f"\n💡 RECOMMANDATIONS:")
        print("-" * 20)
        print("1. Vérifier que tous les modules ont été copiés depuis Core/")
        print("2. Vérifier les imports dans les fichiers __init__.py")
        print("3. Vérifier les dépendances externes (Neo4j, etc.)")
        print("4. Vérifier la structure des dossiers")
    else:
        print(f"\n✅ Aucune dépendance manquante identifiée!")
    
    # Suggestions d'amélioration
    print(f"\n🔧 SUGGESTIONS D'AMÉLIORATION:")
    print("-" * 30)
    if total_errors > 0:
        print("• Corriger les erreurs d'import avant de continuer")
    if total_failures > 0:
        print("• Analyser les échecs de tests pour identifier les bugs")
    if total_skipped > 0:
        print("• Installer les dépendances manquantes pour les tests ignorés")
    
    print("• Considérer l'ajout de tests d'intégration")
    print("• Ajouter des tests de performance")
    print("• Implémenter des tests de stress")
    
    return {
        'total_tests': total_tests,
        'total_failures': total_failures,
        'total_errors': total_errors,
        'total_skipped': total_skipped,
        'missing_dependencies': missing_dependencies
    }


def analyze_missing_components():
    """Analyse les composants potentiellement manquants."""
    
    print(f"\n🔍 ANALYSE DES COMPOSANTS MANQUANTS")
    print("=" * 50)
    
    # Vérifier la structure des dossiers
    expected_structure = [
        "MemoryEngine/core/",
        "MemoryEngine/extensions/",
        "MemoryEngine/backends/",
        "MemoryEngine/parsers/",
        "MemoryEngine/utils/",
        "MemoryEngine/EditingSession/",
        "MemoryEngine/ProcessManager/",
        "MemoryEngine/UnitTests/"
    ]
    
    missing_dirs = []
    for dir_path in expected_structure:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("📁 Dossiers manquants:")
        for dir_path in missing_dirs:
            print(f"  • {dir_path}")
    else:
        print("✅ Tous les dossiers sont présents")
    
    # Vérifier les fichiers clés
    key_files = [
        "MemoryEngine/__init__.py",
        "MemoryEngine/core/engine.py",
        "MemoryEngine/core/memory_node.py",
        "MemoryEngine/extensions/tool_memory_extension.py",
        "MemoryEngine/extensions/tool_search_extension.py",
        "MemoryEngine/EditingSession/__init__.py",
        "MemoryEngine/ProcessManager/__init__.py"
    ]
    
    missing_files = []
    for file_path in key_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("\n📄 Fichiers clés manquants:")
        for file_path in missing_files:
            print(f"  • {file_path}")
    else:
        print("\n✅ Tous les fichiers clés sont présents")
    
    return {
        'missing_dirs': missing_dirs,
        'missing_files': missing_files
    }


def generate_report(results, analysis):
    """Génère un rapport détaillé."""
    
    report = f"""
# 📋 Rapport de Tests MemoryEngine

## Résumé Exécutif
- **Tests exécutés**: {results['total_tests']}
- **Échecs**: {results['total_failures']}
- **Erreurs**: {results['total_errors']}
- **Tests ignorés**: {results['total_skipped']}
- **Taux de succès**: {((results['total_tests'] - results['total_failures'] - results['total_errors']) / max(results['total_tests'], 1)) * 100:.1f}%

## Dépendances Manquantes
"""
    
    if results['missing_dependencies']:
        for dep in results['missing_dependencies']:
            report += f"- {dep}\n"
    else:
        report += "- Aucune dépendance manquante identifiée\n"
    
    report += f"""
## Structure du Projet
"""
    
    if analysis['missing_dirs']:
        report += "### Dossiers Manquants\n"
        for dir_path in analysis['missing_dirs']:
            report += f"- {dir_path}\n"
    
    if analysis['missing_files']:
        report += "### Fichiers Manquants\n"
        for file_path in analysis['missing_files']:
            report += f"- {file_path}\n"
    
    report += f"""
## Recommandations

### Priorité Haute
1. Corriger les erreurs d'import critiques
2. Copier les composants manquants depuis Core/
3. Vérifier la cohérence des imports

### Priorité Moyenne
1. Installer les dépendances externes
2. Ajouter des tests d'intégration
3. Implémenter la gestion d'erreurs

### Priorité Basse
1. Optimiser les performances
2. Ajouter des tests de stress
3. Améliorer la documentation
"""
    
    # Sauvegarder le rapport
    report_file = "MemoryEngine/UnitTests/test_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Rapport généré: {report_file}")


if __name__ == "__main__":
    # Exécuter tous les tests
    results = run_all_tests()
    
    # Analyser les composants manquants
    analysis = analyze_missing_components()
    
    # Générer le rapport
    generate_report(results, analysis)
    
    print(f"\n🏁 Tests terminés. Consultez le rapport pour plus de détails.") 