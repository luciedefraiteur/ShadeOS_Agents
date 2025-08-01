#!/usr/bin/env python3
"""
⛧ Liste des Outils Disponibles ⛧
Architecte Démoniaque du Nexus Luciforme

Script pour lister tous les outils disponibles dans le registre.
"""

import os
import sys

# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

# Import du registre d'outils
os.environ['PYTHONPATH'] = os.path.abspath('.')
from Core.implementation.tool_registry import ALL_TOOLS, initialize_tool_registry
from Core.Archivist.MemoryEngine.engine import MemoryEngine

def list_tools_by_category():
    """Liste les outils par catégorie."""
    
    # Initialise le registre
    memory_engine = MemoryEngine()
    initialize_tool_registry(memory_engine)
    
    print("⛧ Arsenal Mystique des Outils Disponibles")
    print("⛧" + "═" * 60)
    print(f"⛧ Total: {len(ALL_TOOLS)} outils enregistrés")
    print()
    
    # Groupe par type
    categories = {}
    for tool_id, tool_info in ALL_TOOLS.items():
        lucidoc = tool_info.get('lucidoc', {})
        pacte = lucidoc.get('🜄pacte', {})
        tool_type = pacte.get('type', 'unknown')
        
        if tool_type not in categories:
            categories[tool_type] = []
        
        categories[tool_type].append({
            'id': tool_id,
            'intent': pacte.get('intent', 'Intention non documentée'),
            'level': pacte.get('level', 'unknown'),
            'signature': lucidoc.get('🜂invocation', {}).get('signature', 'Signature non documentée')
        })
    
    # Affiche par catégorie
    for category, tools in sorted(categories.items()):
        print(f"🔮 **{category.upper()}** ({len(tools)} outils)")
        print("⛧" + "─" * 50)
        
        for tool in sorted(tools, key=lambda x: x['id']):
            print(f"  📜 **{tool['id']}** [{tool['level']}]")
            print(f"     Intent: {tool['intent']}")
            print(f"     Signature: {tool['signature']}")
            print()
        
        print()
    
    return categories

def generate_tools_summary():
    """Génère un résumé des outils pour le README."""
    
    categories = list_tools_by_category()
    
    summary = []
    summary.append("# 🜲 Arsenal Mystique des Outils")
    summary.append("")
    summary.append(f"**{len(ALL_TOOLS)} outils** répartis en **{len(categories)} catégories** :")
    summary.append("")
    
    for category, tools in sorted(categories.items()):
        summary.append(f"## 🔮 {category.title()} ({len(tools)} outils)")
        summary.append("")
        
        for tool in sorted(tools, key=lambda x: x['id']):
            summary.append(f"- **`{tool['id']}`** [{tool['level']}] : {tool['intent']}")
        
        summary.append("")
    
    return "\n".join(summary)

if __name__ == "__main__":
    try:
        categories = list_tools_by_category()
        
        print("⛧" + "═" * 60)
        print("⛧ RÉSUMÉ PAR CATÉGORIE")
        print("⛧" + "═" * 60)
        
        for category, tools in sorted(categories.items()):
            print(f"🔮 {category.upper()}: {len(tools)} outils")
        
        print(f"\n⛧ TOTAL: {len(ALL_TOOLS)} outils mystiques disponibles")
        
        # Génère le résumé pour le README
        summary = generate_tools_summary()
        with open("TOOLS_SUMMARY.md", "w", encoding="utf-8") as f:
            f.write(summary)
        
        print(f"\n✅ Résumé généré dans TOOLS_SUMMARY.md")
        
    except Exception as e:
        print(f"⛧ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
