#!/usr/bin/env python3
"""
⛧ Démonstration OpenAI + MemoryEngine Integration ⛧

Script de démonstration pour montrer l'intégration entre OpenAI Agents SDK et MemoryEngine.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import sys
import os
import json
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from MemoryEngine.core.engine import MemoryEngine
from MemoryEngine.EditingSession.Tools import (
    ToolRegistry, 
    ToolInvoker, 
    ToolSearchEngine, 
    OpenAIAgentTools,
    initialize_tool_registry
)


def demo_tool_registry_with_mock_tools():
    """Démonstration avec des outils simulés."""
    print("🎭 Démonstration avec outils simulés")
    print("=" * 50)
    
    # Initialiser MemoryEngine
    memory_engine = MemoryEngine()
    
    # Créer un registre avec des outils simulés
    tool_registry = ToolRegistry(memory_engine)
    
    # Ajouter des outils simulés
    mock_tools = {
        "safe_create_file": {
            "function": lambda file_path, content: {"success": True, "file_path": file_path},
            "lucidoc": {
                "id": "safe_create_file",
                "🜄pacte": {
                    "type": "inscription",
                    "intent": "Créer un fichier de manière sécurisée",
                    "level": "fondamental"
                },
                "🜂invocation": {
                    "requires": ["file_path", "content"],
                    "optional": [],
                    "returns": "Dict avec statut de création"
                },
                "🜁essence": {
                    "keywords": ["file", "create", "safe"],
                    "symbolic_layer": "Création sécurisée de fichiers",
                    "usage_context": "Création de nouveaux fichiers dans le projet"
                }
            },
            "source": "demo",
            "file_path": "demo/safe_create_file.luciform"
        },
        "safe_replace_text_in_file": {
            "function": lambda file_path, old_text, new_text: {"success": True, "lines_modified": [1, 2]},
            "lucidoc": {
                "id": "safe_replace_text_in_file",
                "🜄pacte": {
                    "type": "inscription",
                    "intent": "Remplacer du texte dans un fichier de manière sécurisée",
                    "level": "intermédiaire"
                },
                "🜂invocation": {
                    "requires": ["file_path", "old_text", "new_text"],
                    "optional": [],
                    "returns": "Dict avec lignes modifiées"
                },
                "🜁essence": {
                    "keywords": ["file", "replace", "text", "safe"],
                    "symbolic_layer": "Modification sécurisée de contenu",
                    "usage_context": "Remplacement de texte dans des fichiers existants"
                }
            },
            "source": "demo",
            "file_path": "demo/safe_replace_text_in_file.luciform"
        },
        "analyze_file_structure": {
            "function": lambda file_path: {"scopes": 5, "complexity": "medium"},
            "lucidoc": {
                "id": "analyze_file_structure",
                "🜄pacte": {
                    "type": "divination",
                    "intent": "Analyser la structure d'un fichier",
                    "level": "avancé"
                },
                "🜂invocation": {
                    "requires": ["file_path"],
                    "optional": [],
                    "returns": "Dict avec analyse de structure"
                },
                "🜁essence": {
                    "keywords": ["analyze", "structure", "file", "code"],
                    "symbolic_layer": "Analyse structurelle de code",
                    "usage_context": "Compréhension de l'architecture de fichiers"
                }
            },
            "source": "demo",
            "file_path": "demo/analyze_file_structure.luciform"
        }
    }
    
    tool_registry.tools = mock_tools
    print(f"✅ {len(tool_registry.tools)} outils simulés ajoutés")
    
    return tool_registry


def demo_tool_search(tool_registry):
    """Démonstration du moteur de recherche."""
    print("\n🔍 Démonstration du moteur de recherche")
    print("-" * 40)
    
    search_engine = ToolSearchEngine(tool_registry)
    
    # Recherche par mot-clé
    print("📁 Recherche 'file':")
    results = search_engine.search_by_keyword("file", limit=5)
    for result in results:
        print(f"  - {result['tool_id']} (score: {result['score']})")
        print(f"    Intent: {result['intent']}")
    
    # Recherche par type
    print("\n🔮 Outils divination:")
    divination_tools = search_engine.search_by_type("divination")
    for tool in divination_tools:
        print(f"  - {tool['tool_id']}: {tool['intent']}")
    
    # Recherche par niveau
    print("\n📊 Outils fondamentaux:")
    basic_tools = search_engine.search_by_level("fondamental")
    for tool in basic_tools:
        print(f"  - {tool['tool_id']}: {tool['intent']}")
    
    # Statistiques
    stats = search_engine.get_tool_statistics()
    print(f"\n📈 Statistiques: {stats['total_tools']} outils au total")
    print(f"   Par type: {stats['by_type']}")
    print(f"   Par niveau: {stats['by_level']}")


def demo_tool_invoker(tool_registry):
    """Démonstration du moteur d'invocation."""
    print("\n⚡ Démonstration du moteur d'invocation")
    print("-" * 40)
    
    invoker = ToolInvoker(tool_registry)
    
    # Test d'invocation directe
    print("🧪 Test d'invocation directe:")
    result = invoker.invoke_tool("safe_create_file", 
                                file_path="demo_file.py", 
                                content="print('Hello, World!')")
    print(f"  Résultat: {result['success']}")
    print(f"  Temps d'exécution: {result['execution_time']:.3f}s")
    
    # Test d'invocation OpenAI
    print("\n🤖 Test d'invocation OpenAI:")
    tool_call = {
        "id": "demo_call_1",
        "function": {
            "name": "safe_replace_text_in_file",
            "arguments": '{"file_path": "demo_file.py", "old_text": "Hello", "new_text": "Bonjour"}'
        }
    }
    
    result = invoker.invoke_tool_for_openai("safe_replace_text_in_file", 
                                           '{"file_path": "demo_file.py", "old_text": "Hello", "new_text": "Bonjour"}')
    print(f"  Résultat: {result['success']}")
    print(f"  Temps d'exécution: {result['execution_time']:.3f}s")
    
    # Statistiques d'exécution
    stats = invoker.get_tool_statistics()
    print(f"\n📊 Statistiques d'exécution:")
    print(f"  Total: {stats['total_executions']}")
    print(f"  Succès: {stats['successful_executions']}")
    print(f"  Échecs: {stats['failed_executions']}")
    print(f"  Temps moyen: {stats['average_execution_time']:.3f}s")


def demo_openai_integration(tool_registry):
    """Démonstration de l'intégration OpenAI."""
    print("\n🤖 Démonstration de l'intégration OpenAI")
    print("-" * 40)
    
    openai_tools = OpenAIAgentTools(tool_registry)
    
    # Configuration des outils pour OpenAI
    tools_config = openai_tools.get_openai_tools_config()
    print(f"🔧 Configuration OpenAI: {len(tools_config)} outils configurés")
    
    # Afficher un exemple de configuration
    if tools_config:
        example_tool = tools_config[0]
        print(f"\n📝 Exemple de configuration d'outil:")
        print(f"  Nom: {example_tool['function']['name']}")
        print(f"  Description: {example_tool['function']['description']}")
        print(f"  Paramètres requis: {example_tool['function']['parameters']['required']}")
    
    # Contexte pour agent
    print(f"\n🎯 Contexte généré pour agent:")
    context = openai_tools.get_context_for_agent("créer et modifier un fichier Python")
    print(context)
    
    # Suggestions d'outils
    print(f"\n💡 Suggestions pour 'créer et modifier un fichier':")
    suggestions = openai_tools.suggest_tools_for_task("créer et modifier un fichier")
    for suggestion in suggestions:
        print(f"  - {suggestion['tool_id']}: {suggestion['intent']}")
    
    # Workflow exemple
    print(f"\n🔄 Workflow exemple pour édition de fichier:")
    workflow = openai_tools.create_workflow_example("file_editing")
    print(f"  Description: {workflow['description']}")
    for step in workflow['steps']:
        print(f"  Étape {step['step']}: {step['action']}")
        print(f"    Outils suggérés: {', '.join(step['suggested_tools'])}")


def demo_complete_workflow():
    """Démonstration d'un workflow complet."""
    print("\n🚀 Démonstration d'un workflow complet")
    print("=" * 50)
    
    # Initialiser avec des outils simulés
    tool_registry = demo_tool_registry_with_mock_tools()
    openai_tools = OpenAIAgentTools(tool_registry)
    
    # Simuler une conversation avec un agent
    print("🤖 Simulation d'une conversation avec agent OpenAI...")
    
    # 1. L'utilisateur demande de créer un module Python
    user_query = "Crée un module Python pour calculer des statistiques"
    
    print(f"\n👤 Utilisateur: {user_query}")
    
    # 2. L'agent analyse la demande
    context = openai_tools.get_context_for_agent(user_query)
    print(f"\n🤖 Agent (contexte): {context[:100]}...")
    
    # 3. L'agent suggère des outils
    suggested_tools = openai_tools.suggest_tools_for_task(user_query)
    print(f"\n🔧 Outils suggérés:")
    for tool in suggested_tools:
        print(f"  - {tool['tool_id']}: {tool['intent']}")
    
    # 4. L'agent exécute les actions
    print(f"\n⚡ Exécution des actions:")
    
    # Créer le fichier
    invoker = ToolInvoker(tool_registry)
    result1 = invoker.invoke_tool("safe_create_file", 
                                 file_path="statistics.py", 
                                 content="""
def calculate_mean(numbers):
    return sum(numbers) / len(numbers)

def calculate_median(numbers):
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    if n % 2 == 0:
        return (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
    else:
        return sorted_numbers[n//2]

def calculate_standard_deviation(numbers):
    mean = calculate_mean(numbers)
    variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
    return variance ** 0.5
""")
    print(f"  ✅ Création du fichier: {result1['success']}")
    
    # Analyser la structure
    result2 = invoker.invoke_tool("analyze_file_structure", file_path="statistics.py")
    print(f"  ✅ Analyse de structure: {result2['success']}")
    print(f"     Scopes: {result2['result']['scopes']}, Complexité: {result2['result']['complexity']}")
    
    # Modifier le fichier pour ajouter une fonction
    result3 = invoker.invoke_tool("safe_replace_text_in_file", 
                                 file_path="statistics.py", 
                                 old_text="def calculate_standard_deviation(numbers):",
                                 new_text="""def calculate_variance(numbers):
    mean = calculate_mean(numbers)
    return sum((x - mean) ** 2 for x in numbers) / len(numbers)

def calculate_standard_deviation(numbers):""")
    print(f"  ✅ Ajout de fonction variance: {result3['success']}")
    
    # 5. Résumé final
    print(f"\n📊 Résumé du workflow:")
    stats = openai_tools.get_agent_statistics()
    print(f"  - Outils disponibles: {stats['total_tools_available']}")
    print(f"  - Exécutions: {stats['tool_executions']['total_executions']}")
    print(f"  - Succès: {stats['tool_executions']['successful_executions']}")
    print(f"  - Temps moyen: {stats['tool_executions']['average_execution_time']:.3f}s")
    
    # Nettoyage
    if os.path.exists("statistics.py"):
        os.remove("statistics.py")
        print(f"\n🧹 Fichier de démonstration supprimé")


def main():
    """Démonstration principale."""
    print("⛧ Démonstration OpenAI + MemoryEngine Integration ⛧")
    print("=" * 60)
    
    try:
        # Démonstrations individuelles
        tool_registry = demo_tool_registry_with_mock_tools()
        demo_tool_search(tool_registry)
        demo_tool_invoker(tool_registry)
        demo_openai_integration(tool_registry)
        
        # Démonstration de workflow complet
        demo_complete_workflow()
        
        print("\n" + "=" * 60)
        print("🎉 Démonstration terminée avec succès !")
        print("L'intégration OpenAI + MemoryEngine est prête pour l'utilisation !")
        
    except Exception as e:
        print(f"❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 