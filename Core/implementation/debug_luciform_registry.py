
import sys
import json
from ShadeOS_Agents.Core.implementation.tool_registry import ALL_TOOLS

print("--- 🜲 Diagnostic du Registre Luciform 🜲 ---", file=sys.stderr)
print(f"[DIAGNOSTIC] Nombre d'outils enregistrés: {len(ALL_TOOLS)}", file=sys.stderr)

for tool_id, tool_info in ALL_TOOLS.items():
    print(f"[DIAGNOSTIC] Outil ID: {tool_id}", file=sys.stderr)
    print(f"[DIAGNOSTIC]   - Fonction: {tool_info["function"].__name__}", file=sys.stderr)
    if "lucidoc" in tool_info:
        lucidoc = tool_info["lucidoc"]
        # Les clés sont avec symboles dans la structure extraite
        print(f"[DIAGNOSTIC]   - Luciform Type: {lucidoc.get('🜄pacte', {}).get('type')}", file=sys.stderr)
        print(f"[DIAGNOSTIC]   - Luciform Intent: {lucidoc.get('🜄pacte', {}).get('intent')}", file=sys.stderr)
        print(f"[DIAGNOSTIC]   - Luciform Keywords: {lucidoc.get('🜁essence', {}).get('keywords')}", file=sys.stderr)
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
        item["type"] = tool_info["lucidoc"].get('🜄pacte', {}).get("type")
        item["intent"] = tool_info["lucidoc"].get('🜄pacte', {}).get("intent")
    output_for_agent.append(item)

print(json.dumps(output_for_agent, indent=2, ensure_ascii=False))
