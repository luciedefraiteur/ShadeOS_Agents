
import sys
import os
import json

# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Core.Archivist.MemoryEngine.engine import MemoryEngine
from Core.implementation.tool_registry import ALL_TOOLS, initialize_tool_registry

# Initialise le registre
memory_engine = MemoryEngine()
initialize_tool_registry(memory_engine)

print("--- 🜲 Diagnostic du Registre Luciform 🜲 ---", file=sys.stderr)
print(f"[DIAGNOSTIC] Nombre d'outils enregistrés: {len(ALL_TOOLS)}", file=sys.stderr)

for tool_id, tool_info in ALL_TOOLS.items():
    print(f"[DIAGNOSTIC] Outil ID: {tool_id}", file=sys.stderr)
    print(f"[DIAGNOSTIC]   - Fonction: {tool_info["function"].__name__}", file=sys.stderr)
    if "lucidoc" in tool_info:
        lucidoc = tool_info["lucidoc"]
        # Les clés sont normalisées (sans symboles) dans la structure extraite
        pacte = lucidoc.get('pacte', {})
        essence = lucidoc.get('essence', {})
        invocation = lucidoc.get('invocation', {})

        print(f"[DIAGNOSTIC]   - Luciform Type: {pacte.get('type')}", file=sys.stderr)
        print(f"[DIAGNOSTIC]   - Luciform Intent: {pacte.get('intent')}", file=sys.stderr)
        print(f"[DIAGNOSTIC]   - Luciform Level: {pacte.get('level')}", file=sys.stderr)
        print(f"[DIAGNOSTIC]   - Luciform Keywords: {essence.get('keywords')}", file=sys.stderr)
        print(f"[DIAGNOSTIC]   - Luciform Signature: {invocation.get('signature')}", file=sys.stderr)
    else:
        print("[DIAGNOSTIC]   - Pas de luciform associé.", file=sys.stderr)

print("--- 🜲 Fin du Diagnostic 🜲 ---", file=sys.stderr)

# Pour que le script puisse être exécuté et que la sortie soit capturée
# par un autre agent, nous pouvons imprimer une version simplifiée du registre
# sur stdout.
output_for_agent = []
for tool_id, tool_info in ALL_TOOLS.items():
    item = {"id": tool_id}
    if "lucidoc" in tool_info:
        lucidoc = tool_info["lucidoc"]
        pacte = lucidoc.get('pacte', {})
        essence = lucidoc.get('essence', {})
        invocation = lucidoc.get('invocation', {})

        item["type"] = pacte.get("type")
        item["intent"] = pacte.get("intent")
        item["level"] = pacte.get("level")
        item["keywords"] = essence.get("keywords")
        item["signature"] = invocation.get("signature")
    output_for_agent.append(item)

print(json.dumps(output_for_agent, indent=2, ensure_ascii=False))
