#!/usr/bin/env python3
"""
🔍 High-Level Import Analyzer - Interface avancée

Version haut niveau qui utilise le Core/Partitioner/import_analyzer.py redesigné
avec une interface simplifiée et des fonctionnalités avancées.

Fonctionnalités:
- Interface simple et intuitive
- Intégration avec TemporalFractalMemoryEngine
- Rapports personnalisés
- Analyse comparative
- Export de données pour intégration

Auteur: Assistant IA (via Lucie Defraiteur)
Date: 2025-08-07
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Ajouter le répertoire racine pour les imports Core
sys.path.append('.')

try:
    from Core.Partitioner.import_analyzer import ImportAnalyzer
    print("✅ ImportAnalyzer importé avec succès!")
except ImportError as e:
    print(f"❌ Erreur import ImportAnalyzer: {e}")
    sys.exit(1)


class HighLevelImportAnalyzer:
    """Interface haut niveau pour l'analyseur d'imports"""
    
    def __init__(self, project_root: str = '.'):
        self.project_root = os.path.abspath(project_root)
        self.analyzer = ImportAnalyzer(project_root=self.project_root)
        self.analysis_history = []
    
    def analyze_project_structure(self, target_files: List[str] = None, 
                                max_depth: int = None, debug: bool = False) -> Dict[str, Any]:
        """
        Analyse la structure complète du projet
        
        Args:
            target_files: Liste des fichiers à analyser (si None, analyse tout le projet)
            max_depth: Profondeur maximale d'analyse
            debug: Mode debug
        
        Returns:
            Résultats d'analyse enrichis
        """
        if target_files is None:
            # Analyser tous les fichiers Python du projet
            target_files = self._discover_python_files()
        
        print(f"🔍 Analyse de la structure du projet...")
        print(f"   Fichiers cibles: {len(target_files)}")
        print(f"   Profondeur max: {max_depth or '∞'}")
        print(f"   Mode debug: {'✅' if debug else '❌'}")
        
        # Effectuer l'analyse
        results = self.analyzer.analyze_files(
            target_files, 
            max_depth=max_depth, 
            debug=debug
        )
        
        # Enrichir les résultats
        enriched_results = self._enrich_analysis_results(results)
        
        # Sauvegarder dans l'historique
        self.analysis_history.append({
            'timestamp': datetime.now().isoformat(),
            'results': enriched_results
        })
        
        return enriched_results
    
    def _discover_python_files(self) -> List[str]:
        """Découvre automatiquement tous les fichiers Python du projet"""
        python_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Ignorer les dossiers système et de cache
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
                '__pycache__', 'node_modules', '.git', '.vscode', 'venv', 'env'
            }]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)
        
        return python_files
    
    def _enrich_analysis_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit les résultats d'analyse avec des métadonnées supplémentaires"""
        enriched = results.copy()
        
        # Ajouter des métadonnées de projet
        enriched['project_metadata'] = {
            'project_root': self.project_root,
            'analysis_timestamp': datetime.now().isoformat(),
            'python_version': sys.version,
            'total_python_files': len(self._discover_python_files())
        }
        
        # Analyser la complexité des dépendances
        stats = results.get('statistics', {})
        files_analysis = results.get('files_analysis', {})
        
        # Calculer des métriques avancées
        complexity_metrics = self._calculate_complexity_metrics(files_analysis)
        enriched['complexity_analysis'] = complexity_metrics
        
        # Identifier les modules critiques
        critical_modules = self._identify_critical_modules(files_analysis)
        enriched['critical_modules'] = critical_modules
        
        return enriched
    
    def _calculate_complexity_metrics(self, files_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule des métriques de complexité des dépendances"""
        if not files_analysis:
            return {}
        
        total_files = len(files_analysis)
        total_imports = sum(len(data.get('imports', [])) for data in files_analysis.values())
        total_local_imports = sum(len(data.get('local_imports', [])) for data in files_analysis.values())
        
        # Calculer la complexité moyenne
        avg_imports_per_file = total_imports / total_files if total_files > 0 else 0
        avg_local_imports_per_file = total_local_imports / total_files if total_files > 0 else 0
        
        # Identifier les fichiers les plus complexes
        files_by_complexity = sorted(
            files_analysis.items(),
            key=lambda x: len(x[1].get('imports', [])),
            reverse=True
        )[:5]
        
        return {
            'total_files': total_files,
            'total_imports': total_imports,
            'total_local_imports': total_local_imports,
            'avg_imports_per_file': round(avg_imports_per_file, 2),
            'avg_local_imports_per_file': round(avg_local_imports_per_file, 2),
            'most_complex_files': [
                {
                    'file': file_path,
                    'import_count': len(data.get('imports', [])),
                    'local_import_count': len(data.get('local_imports', []))
                }
                for file_path, data in files_by_complexity
            ]
        }
    
    def _identify_critical_modules(self, files_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifie les modules critiques (fortement dépendus)"""
        if not files_analysis:
            return []
        
        # Compter les dépendances vers chaque module
        dependency_counts = {}
        
        for file_path, data in files_analysis.items():
            for import_name in data.get('local_imports', []):
                # Extraire le module principal
                module_name = import_name.split('.')[0]
                dependency_counts[module_name] = dependency_counts.get(module_name, 0) + 1
        
        # Identifier les modules les plus dépendus
        critical_modules = sorted(
            dependency_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return [
            {
                'module': module,
                'dependency_count': count,
                'criticality_level': 'HIGH' if count > 5 else 'MEDIUM' if count > 2 else 'LOW'
            }
            for module, count in critical_modules
        ]
    
    def generate_comprehensive_report(self, results: Dict[str, Any], 
                                    output_dir: str = "reports") -> str:
        """Génère un rapport complet et détaillé"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(output_dir, f"comprehensive_analysis_{timestamp}.md")
        
        # Générer le rapport Markdown
        markdown_content = self._generate_markdown_report(results)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Générer le rapport JSON
        json_file = os.path.join(output_dir, f"analysis_data_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"📊 Rapport complet généré:")
        print(f"   Markdown: {report_file}")
        print(f"   JSON: {json_file}")
        
        return report_file
    
    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Génère un rapport Markdown complet"""
        project_meta = results.get('project_metadata', {})
        stats = results.get('statistics', {})
        complexity = results.get('complexity_analysis', {})
        critical_modules = results.get('critical_modules', [])
        
        report = f"""# 📊 Rapport d'Analyse Complète - Import Analyzer

## 🎯 Résumé Exécutif

**Date d'analyse:** {project_meta.get('analysis_timestamp', 'N/A')}  
**Racine du projet:** {project_meta.get('project_root', 'N/A')}  
**Version Python:** {project_meta.get('python_version', 'N/A')}

### 📈 Métriques Clés

- **Fichiers analysés:** {stats.get('files_analyzed', 0)}
- **Imports totaux:** {stats.get('total_imports', 0)}
- **Imports locaux:** {stats.get('local_imports', 0)}
- **Imports externes:** {stats.get('external_imports', 0)}
- **Cycles détectés:** {stats.get('cycles_detected', 0)}
- **Durée d'analyse:** {stats.get('duration', 0):.2f}s

---

## 🔍 Analyse de Complexité

### Métriques de Complexité

- **Fichiers Python totaux:** {complexity.get('total_files', 0)}
- **Imports moyens par fichier:** {complexity.get('avg_imports_per_file', 0)}
- **Imports locaux moyens par fichier:** {complexity.get('avg_local_imports_per_file', 0)}

### 📋 Fichiers les Plus Complexes

"""
        
        for file_info in complexity.get('most_complex_files', []):
            report += f"""
#### {file_info['file']}
- **Imports totaux:** {file_info['import_count']}
- **Imports locaux:** {file_info['local_import_count']}
"""
        
        report += f"""

---

## ⚠️ Modules Critiques

### Modules les Plus Dépendus

"""
        
        for module_info in critical_modules:
            level_emoji = "🔴" if module_info['criticality_level'] == 'HIGH' else "🟡" if module_info['criticality_level'] == 'MEDIUM' else "🟢"
            report += f"""
{level_emoji} **{module_info['module']}**
- **Dépendances:** {module_info['dependency_count']}
- **Niveau de criticité:** {module_info['criticality_level']}
"""
        
        report += f"""

---

## 📊 Détails Techniques

### Statistiques Détaillées

- **Imports standard:** {stats.get('standard_imports', 0)}
- **Fichiers avec erreurs:** {stats.get('files_with_errors', 0)}
- **Profondeur maximale:** {stats.get('max_depth', 0)}

### 🔄 Cycles de Dépendances

"""
        
        cycles = results.get('cycles', [])
        if cycles:
            for i, cycle in enumerate(cycles, 1):
                report += f"**Cycle {i}:** {' → '.join(cycle)}\n\n"
        else:
            report += "Aucun cycle de dépendances détecté.\n\n"
        
        report += f"""

---

## 🎯 Recommandations

### Optimisations Suggérées

1. **Modules critiques:** Surveiller les modules avec un niveau de criticité HIGH
2. **Complexité:** Considérer la refactorisation des fichiers avec plus de 10 imports
3. **Cycles:** Éviter les cycles de dépendances pour maintenir la maintenabilité

---

*Rapport généré automatiquement par HighLevelImportAnalyzer*
"""
        
        return report
    
    def export_for_temporal_fractal(self, results: Dict[str, Any], 
                                   output_file: str = "temporal_fractal_data.json") -> str:
        """Exporte les données pour intégration avec TemporalFractalMemoryEngine"""
        
        # Formater les données pour TemporalFractalMemoryEngine
        fractal_data = {
            'metadata': {
                'source': 'import_analyzer',
                'timestamp': datetime.now().isoformat(),
                'version': '2.0'
            },
            'dependency_graph': {
                'nodes': [],
                'edges': [],
                'cycles': results.get('cycles', [])
            },
            'complexity_metrics': results.get('complexity_analysis', {}),
            'critical_modules': results.get('critical_modules', [])
        }
        
        # Convertir les fichiers en nœuds
        files_analysis = results.get('files_analysis', {})
        for file_path, data in files_analysis.items():
            node = {
                'id': file_path,
                'type': 'python_file',
                'properties': {
                    'import_count': len(data.get('imports', [])),
                    'local_import_count': len(data.get('local_imports', [])),
                    'external_import_count': len(data.get('external_imports', [])),
                    'standard_import_count': len(data.get('standard_imports', [])),
                    'depth': data.get('dependency_depth', 0)
                }
            }
            fractal_data['dependency_graph']['nodes'].append(node)
        
        # Sauvegarder
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(fractal_data, f, indent=2, default=str)
        
        print(f"📤 Données exportées pour TemporalFractalMemoryEngine: {output_file}")
        return output_file
    
    def compare_analyses(self, analysis1: Dict[str, Any], analysis2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare deux analyses et génère un rapport de différences"""
        
        stats1 = analysis1.get('statistics', {})
        stats2 = analysis2.get('statistics', {})
        
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'metrics_comparison': {
                'files_analyzed': {
                    'before': stats1.get('files_analyzed', 0),
                    'after': stats2.get('files_analyzed', 0),
                    'difference': stats2.get('files_analyzed', 0) - stats1.get('files_analyzed', 0)
                },
                'total_imports': {
                    'before': stats1.get('total_imports', 0),
                    'after': stats2.get('total_imports', 0),
                    'difference': stats2.get('total_imports', 0) - stats1.get('total_imports', 0)
                },
                'local_imports': {
                    'before': stats1.get('local_imports', 0),
                    'after': stats2.get('local_imports', 0),
                    'difference': stats2.get('local_imports', 0) - stats1.get('local_imports', 0)
                },
                'cycles_detected': {
                    'before': stats1.get('cycles_detected', 0),
                    'after': stats2.get('cycles_detected', 0),
                    'difference': stats2.get('cycles_detected', 0) - stats1.get('cycles_detected', 0)
                }
            }
        }
        
        return comparison


def main():
    """Fonction principale du High-Level Import Analyzer"""
    parser = argparse.ArgumentParser(
        description='🔍 High-Level Import Analyzer - Interface avancée',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python high_level_import_analyzer.py --project-root . --comprehensive
  python high_level_import_analyzer.py --files file1.py file2.py --max-depth 3
  python high_level_import_analyzer.py --discover-all --export-fractal
  python high_level_import_analyzer.py --debug --show-modules
        """
    )
    
    parser.add_argument('--project-root', type=str, default='.',
                       help='Racine du projet à analyser')
    parser.add_argument('--files', nargs='+',
                       help='Fichiers spécifiques à analyser')
    parser.add_argument('--discover-all', action='store_true',
                       help='Découvrir automatiquement tous les fichiers Python')
    parser.add_argument('--max-depth', type=int, default=None,
                       help='Profondeur maximale d\'analyse')
    parser.add_argument('--debug', action='store_true',
                       help='Mode debug avec informations détaillées')
    parser.add_argument('--comprehensive', action='store_true',
                       help='Générer un rapport complet')
    parser.add_argument('--export-fractal', action='store_true',
                       help='Exporter les données pour TemporalFractalMemoryEngine')
    parser.add_argument('--output-dir', type=str, default='reports',
                       help='Répertoire de sortie pour les rapports')
    parser.add_argument('--show-modules', action='store_true',
                       help='Afficher les modules détectés')
    
    args = parser.parse_args()
    
    # Créer l'analyseur haut niveau
    analyzer = HighLevelImportAnalyzer(project_root=args.project_root)
    
    # Déterminer les fichiers à analyser
    if args.files:
        target_files = args.files
        print(f"🎯 Analyse de fichiers spécifiques: {len(target_files)} fichiers")
    elif args.discover_all:
        target_files = None  # Découverte automatique
        print("🔍 Découverte automatique de tous les fichiers Python...")
    else:
        # Par défaut, analyser quelques fichiers représentatifs
        target_files = [
            'Assistants/Generalist/V9_AutoFeedingThreadAgent.py',
            'Core/Partitioner/import_analyzer.py'
        ]
        print(f"📋 Analyse par défaut: {len(target_files)} fichiers")
    
    # Effectuer l'analyse
    print("🚀 Début de l'analyse...")
    results = analyzer.analyze_project_structure(
        target_files=target_files,
        max_depth=args.max_depth,
        debug=args.debug
    )
    
    # Afficher les résultats de base
    stats = results.get('statistics', {})
    print(f"\n📊 Résultats de l'analyse:")
    print(f"   Fichiers analysés: {stats.get('files_analyzed', 0)}")
    print(f"   Imports totaux: {stats.get('total_imports', 0)}")
    print(f"   Imports locaux: {stats.get('local_imports', 0)}")
    print(f"   Cycles détectés: {stats.get('cycles_detected', 0)}")
    
    # Afficher les modules détectés si demandé
    if args.show_modules:
        print("\n🔍 Modules détectés:")
        detected_modules = analyzer.analyzer.get_detected_local_modules()
        for module, is_local in sorted(detected_modules.items()):
            status = "✅" if is_local else "❌"
            print(f"  {status} {module}")
    
    # Générer le rapport complet si demandé
    if args.comprehensive:
        report_file = analyzer.generate_comprehensive_report(results, args.output_dir)
        print(f"\n📄 Rapport complet généré: {report_file}")
    
    # Exporter pour TemporalFractalMemoryEngine si demandé
    if args.export_fractal:
        fractal_file = analyzer.export_for_temporal_fractal(results)
        print(f"\n📤 Données exportées pour TemporalFractalMemoryEngine: {fractal_file}")
    
    print(f"\n✅ Analyse terminée!")


if __name__ == '__main__':
    main() 