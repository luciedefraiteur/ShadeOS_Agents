#!/usr/bin/env python3
"""
🎯 Validation complète de l'ImportAnalyzer corrigé

Script de validation pour tester toutes les fonctionnalités
après la correction de l'erreur parse_content.

Auteur: Alma (via Lucie Defraiteur)
Date: 2025-08-07
"""

import sys
import os
import asyncio
import tempfile
from pathlib import Path

# Ajouter le répertoire racine pour les imports Core
sys.path.append('.')

def test_parse_content_correction():
    """Test que l'erreur parse_content est bien corrigée"""
    print("🧪 Test 1: Correction de l'erreur parse_content")
    print("-" * 40)
    
    try:
        from Core.Partitioner.analyzers.import_analyzer import ImportAnalyzer
        
        analyzer = ImportAnalyzer()
        test_file = "Assistants/Generalist/V9_AutoFeedingThreadAgent.py"
        
        if not os.path.exists(test_file):
            print(f"❌ Fichier de test non trouvé: {test_file}")
            return False
        
        # Test d'extraction d'imports (utilise parse_content)
        imports = analyzer._extract_imports_enhanced(test_file)
        
        print(f"✅ Extraction réussie: {len(imports)} imports trouvés")
        print(f"   Exemples: {imports[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_cache_functionality():
    """Test du fonctionnement du cache"""
    print("\n🧪 Test 2: Fonctionnement du cache")
    print("-" * 40)
    
    try:
        from Core.Partitioner.import_analysis_cache import get_import_optimizer
        
        optimizer = get_import_optimizer()
        test_file = "Assistants/Generalist/V9_AutoFeedingThreadAgent.py"
        
        if not os.path.exists(test_file):
            print(f"❌ Fichier de test non trouvé: {test_file}")
            return False
        
        # Test d'analyse avec cache
        result = asyncio.run(optimizer.get_or_analyze_imports(test_file, max_depth=1))
        
        print(f"✅ Analyse avec cache réussie")
        print(f"   Nœuds fractaux: {len(result)}")
        
        # Vérifier les métadonnées
        if '_metadata' in result:
            metadata = result['_metadata']
            print(f"   Fichiers analysés: {metadata.get('total_files', 0)}")
            print(f"   Imports totaux: {metadata.get('total_imports', 0)}")
            print(f"   Imports locaux: {metadata.get('local_imports', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_high_level_analyzer():
    """Test de l'analyseur haut niveau"""
    print("\n🧪 Test 3: Analyseur haut niveau")
    print("-" * 40)
    
    try:
        from UnitTests.high_level_import_analyzer import HighLevelImportAnalyzer
        
        analyzer = HighLevelImportAnalyzer()
        test_files = ["Assistants/Generalist/V9_AutoFeedingThreadAgent.py"]
        
        results = analyzer.analyze_project_structure(
            target_files=test_files,
            max_depth=1,
            debug=False
        )
        
        print(f"✅ Analyse haut niveau réussie")
        stats = results.get('statistics', {})
        print(f"   Fichiers analysés: {stats.get('files_analyzed', 0)}")
        print(f"   Imports totaux: {stats.get('total_imports', 0)}")
        print(f"   Imports locaux: {stats.get('local_imports', 0)}")
        print(f"   Cycles détectés: {stats.get('cycles_detected', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_detection_automatique():
    """Test de la détection automatique des modules"""
    print("\n🧪 Test 4: Détection automatique des modules")
    print("-" * 40)
    
    try:
        from Core.Partitioner.analyzers.import_analyzer import ImportAnalyzer
        
        analyzer = ImportAnalyzer()
        
        # Test de différents types de modules
        test_cases = [
            ('Core.Partitioner.ImportAnalyzer', True),
            ('TemporalFractalMemoryEngine.core.temporal_engine', True),
            ('os', False),  # Module standard
            ('requests', False),  # Module externe
            ('Assistants.Generalist.V9_AutoFeedingThreadAgent', True),
        ]
        
        all_correct = True
        for module, expected_local in test_cases:
            is_local = analyzer._is_local_module(module)
            status = "✅" if is_local == expected_local else "❌"
            module_type = "Local" if is_local else "Externe/Standard"
            print(f"   {status} {module}: {module_type}")
            
            if is_local != expected_local:
                all_correct = False
        
        return all_correct
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_error_handling():
    """Test de la gestion d'erreurs"""
    print("\n🧪 Test 5: Gestion d'erreurs")
    print("-" * 40)
    
    try:
        from Core.Partitioner.analyzers.import_analyzer import ImportAnalyzer
        
        analyzer = ImportAnalyzer()
        
        # Test avec un fichier inexistant
        result = analyzer._extract_imports_enhanced("fichier_inexistant.py")
        print(f"✅ Fichier inexistant géré: {len(result)} imports")
        
        # Test avec un fichier vide
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("")
            empty_file = f.name
        
        try:
            result = analyzer._extract_imports_enhanced(empty_file)
            print(f"✅ Fichier vide géré: {len(result)} imports")
        finally:
            os.unlink(empty_file)
        
        # Test avec un fichier syntaxiquement incorrect
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test_function(\n    # Syntaxe incorrecte")
            invalid_file = f.name
        
        try:
            result = analyzer._extract_imports_enhanced(invalid_file)
            print(f"✅ Fichier syntaxe incorrecte géré: {len(result)} imports")
        finally:
            os.unlink(invalid_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_performance():
    """Test de performance"""
    print("\n🧪 Test 6: Performance")
    print("-" * 40)
    
    try:
        import time
        from Core.Partitioner.analyzers.import_analyzer import ImportAnalyzer
        
        analyzer = ImportAnalyzer()
        test_file = "Assistants/Generalist/V9_AutoFeedingThreadAgent.py"
        
        if not os.path.exists(test_file):
            print(f"❌ Fichier de test non trouvé: {test_file}")
            return False
        
        # Test de performance
        start_time = time.time()
        imports = analyzer._extract_imports_enhanced(test_file)
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"✅ Performance: {duration:.3f}s pour {len(imports)} imports")
        
        if duration < 1.0:  # Moins d'1 seconde
            print("   ✅ Performance acceptable")
            return True
        else:
            print("   ⚠️ Performance lente")
            return False
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    """Fonction principale de validation"""
    print("🎯 VALIDATION COMPLÈTE DE L'IMPORTANALYZER CORRIGÉ")
    print("=" * 60)
    
    tests = [
        ("Correction parse_content", test_parse_content_correction),
        ("Fonctionnement cache", test_cache_functionality),
        ("Analyseur haut niveau", test_high_level_analyzer),
        ("Détection automatique", test_detection_automatique),
        ("Gestion d'erreurs", test_error_handling),
        ("Performance", test_performance),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔄 Exécution: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Exception dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE LA VALIDATION")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 VALIDATION COMPLÈTE RÉUSSIE !")
        print("   L'ImportAnalyzer est maintenant fonctionnel et robuste.")
        return 0
    else:
        print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("   Des améliorations sont encore nécessaires.")
        return 1

if __name__ == "__main__":
    exit(main()) 