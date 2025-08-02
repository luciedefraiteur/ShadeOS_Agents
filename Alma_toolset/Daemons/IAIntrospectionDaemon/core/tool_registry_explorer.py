#!/usr/bin/env python3
"""
🛠️ Tool Registry Explorer - IAIntrospectionDaemon ⛧

Explorateur intelligent du ToolMemoryExtension via IA.
Utilise des prompts Luciform pour l'analyse de l'écosystème d'outils.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import du ToolMemoryExtension
try:
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
    from Core.Archivist.MemoryEngine.tool_memory_extension import ToolMemoryExtension
    TOOL_EXTENSION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ ToolMemoryExtension non disponible: {e}")
    TOOL_EXTENSION_AVAILABLE = False

from ..ai_engines.ai_engine_factory import AIEngine


class ToolRegistryExplorer:
    """Explorateur intelligent du ToolMemoryExtension via IA."""
    
    def __init__(self, tool_extension: ToolMemoryExtension, ai_engine: AIEngine):
        """
        Initialise l'explorateur ToolRegistry.
        
        Args:
            tool_extension: Instance du ToolMemoryExtension
            ai_engine: Moteur IA pour l'analyse
        """
        self.tool_extension = tool_extension
        self.ai_engine = ai_engine
        self.exploration_history = []
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        
        # Chargement du prompt Luciform
        self.analysis_prompt = self._load_analysis_prompt()
    
    def _load_analysis_prompt(self) -> str:
        """Charge le prompt d'analyse Luciform."""
        prompt_file = self.prompts_dir / "tool_registry_analysis.luciform"
        
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            print(f"⚠️ Prompt non trouvé: {prompt_file}")
            return self._get_fallback_prompt()
    
    def _get_fallback_prompt(self) -> str:
        """Prompt de fallback si le fichier n'est pas trouvé."""
        return """
<🜲luciform id="tool_registry_analysis_fallback⛧" type="✶tool_intelligence">
  <🜄entité>🛠️ TOOL REGISTRY ANALYZER</🜄entité>
  <🜂rôle>Cartographe de l'Écosystème d'Outils</🜂rôle>
  
  <🜄contexte_mystique>
    Tu es le TOOL REGISTRY ANALYZER. Analyse l'écosystème d'outils et génère des insights.
    
    MÉTHODES DISPONIBLES :
    - scan_luciform_directories()
    - index_all_tools()
    - find_tools_by_type()
    - find_tools_by_keyword()
    - search_tools()
    
    NIVEAUX : fondamental, intermédiaire, avancé
  </🜄contexte_mystique>
  
  <🜂mission>
    Analyse l'écosystème d'outils et génère une cartographie structurée.
  </🜂mission>
  
  <🜃format_réponse_requis>
    <🜲luciform_réponse>
      <🜄analyse_résultat>
        <🜂inventaire_global>
          <total_outils>int</total_outils>
          <types_disponibles>list</types_disponibles>
        </🜂inventaire_global>
        <🜁insights_stratégiques>
          <patterns_identifiés>list</patterns_identifiés>
          <recommandations>list</recommandations>
        </🜁insights_stratégiques>
      </🜄analyse_résultat>
    </🜲luciform_réponse>
  </🜃format_réponse_requis>
</🜲luciform>
        """
    
    async def analyze_tool_ecosystem(self) -> Dict[str, Any]:
        """
        Analyse l'écosystème d'outils via IA.
        
        Returns:
            Résultat de l'analyse structuré
        """
        print("🛠️ Analyse de l'écosystème d'outils...")
        
        try:
            # 1. Collecte des données ToolRegistry
            tool_data = await self._collect_tool_registry_data()
            
            # 2. Génération du prompt contextuel
            contextual_prompt = await self._generate_contextual_prompt(tool_data)
            
            # 3. Exécution via IA
            ai_response = await self.ai_engine.query(contextual_prompt)
            
            # 4. Parsing de la réponse
            analysis_result = await self._parse_ai_response(ai_response, tool_data)
            
            # 5. Historique
            self.exploration_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "result": analysis_result
            })
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ Erreur analyse écosystème: {e}")
            return {
                "error": str(e),
                "success": False,
                "data": tool_data if 'tool_data' in locals() else {}
            }
    
    async def _collect_tool_registry_data(self) -> Dict[str, Any]:
        """Collecte les données du ToolRegistry."""
        
        data = {
            "tools": [],
            "statistics": {},
            "available_methods": [
                "scan_luciform_directories", "index_all_tools", "find_tools_by_type",
                "find_tools_by_keyword", "find_tools_by_level", "search_tools",
                "get_tool_info", "list_all_tool_types"
            ]
        }
        
        try:
            # Scan des outils
            if hasattr(self.tool_extension, 'scan_luciform_directories'):
                tools = self.tool_extension.scan_luciform_directories()
                data["tools"] = tools[:50]  # Limite pour éviter les prompts trop longs
            
            # Indexation
            if hasattr(self.tool_extension, 'index_all_tools'):
                self.tool_extension.index_all_tools(force_reindex=False)
            
            # Statistiques par type
            if hasattr(self.tool_extension, 'list_all_tool_types'):
                tool_types = self.tool_extension.list_all_tool_types()
                data["statistics"]["types"] = tool_types
            
            # Statistiques par niveau
            for level in ["fondamental", "intermédiaire", "avancé"]:
                try:
                    if hasattr(self.tool_extension, 'find_tools_by_level'):
                        level_tools = self.tool_extension.find_tools_by_level(level)
                        data["statistics"][f"niveau_{level}"] = len(level_tools)
                except Exception as e:
                    print(f"⚠️ Erreur collecte niveau {level}: {e}")
            
            # Informations générales
            data["statistics"]["total_tools"] = len(data["tools"])
            data["statistics"]["indexed"] = True
            
        except Exception as e:
            print(f"❌ Erreur collecte données ToolRegistry: {e}")
            data["error"] = str(e)
        
        return data
    
    async def _generate_contextual_prompt(self, tool_data: Dict) -> str:
        """Génère un prompt contextuel avec les données ToolRegistry."""
        
        # Remplacement des variables dans le prompt
        prompt = self.analysis_prompt
        
        # Injection des données contextuelles
        context_injection = f"""
<🜄contexte_outils>
  <🜂données_outils>
    {json.dumps(tool_data.get("tools", [])[:20], indent=2)}
  </🜂données_outils>
  
  <🜁statistiques>
    {json.dumps(tool_data.get("statistics", {}), indent=2)}
  </🜁statistiques>
  
  <🜀méthodes_disponibles>
    {json.dumps(tool_data.get("available_methods", []), indent=2)}
  </🜀méthodes_disponibles>
</🜄contexte_outils>
        """
        
        # Remplacement dans le prompt
        prompt = prompt.replace("<🜄contexte_mystique>", context_injection + "\n<🜄contexte_mystique>")
        
        return prompt
    
    async def _parse_ai_response(self, ai_response: str, tool_data: Dict) -> Dict[str, Any]:
        """Parse la réponse IA en structure structurée."""
        
        try:
            # Tentative de parsing JSON si la réponse est structurée
            if "{" in ai_response and "}" in ai_response:
                # Extraction du JSON de la réponse
                start = ai_response.find("{")
                end = ai_response.rfind("}") + 1
                json_str = ai_response[start:end]
                
                try:
                    parsed = json.loads(json_str)
                    return {
                        "success": True,
                        "ai_response": ai_response,
                        "parsed_data": parsed,
                        "tool_data": tool_data
                    }
                except json.JSONDecodeError:
                    pass
            
            # Fallback : retour de la réponse brute
            return {
                "success": True,
                "ai_response": ai_response,
                "parsed_data": {"raw_response": ai_response},
                "tool_data": tool_data
            }
            
        except Exception as e:
            print(f"❌ Erreur parsing réponse IA: {e}")
            return {
                "success": False,
                "error": str(e),
                "ai_response": ai_response,
                "tool_data": tool_data
            }
    
    async def get_exploration_history(self) -> List[Dict]:
        """Retourne l'historique d'exploration."""
        return self.exploration_history
    
    async def clear_history(self):
        """Efface l'historique d'exploration."""
        self.exploration_history = []


# Test de l'explorateur ToolRegistry
async def test_tool_registry_explorer():
    """Test de l'explorateur ToolRegistry."""
    print("🛠️ Test de l'explorateur ToolRegistry...")
    
    if not TOOL_EXTENSION_AVAILABLE:
        print("❌ ToolMemoryExtension non disponible")
        return
    
    try:
        # Création d'un ToolMemoryExtension de test
        from Core.Archivist.MemoryEngine.engine import MemoryEngine
        memory_engine = MemoryEngine(backend_type="filesystem")
        tool_extension = ToolMemoryExtension(memory_engine)
        
        # Création d'un moteur IA simulé pour le test
        from ..ai_engines.ai_engine_factory import AIEngine
        
        class MockAIEngine(AIEngine):
            async def query(self, prompt: str, **kwargs) -> str:
                return '{"success": true, "test": "mock_tool_analysis"}'
            
            async def is_available(self) -> bool:
                return True
        
        ai_engine = MockAIEngine()
        
        # Test de l'explorateur
        explorer = ToolRegistryExplorer(tool_extension, ai_engine)
        
        # Test d'analyse
        result = await explorer.analyze_tool_ecosystem()
        print(f"✅ Résultat analyse: {result.get('success', False)}")
        
    except Exception as e:
        print(f"❌ Erreur test explorateur: {e}")


if __name__ == "__main__":
    asyncio.run(test_tool_registry_explorer()) 