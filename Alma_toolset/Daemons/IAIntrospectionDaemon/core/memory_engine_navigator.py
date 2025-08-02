#!/usr/bin/env python3
"""
🧠 Memory Engine Navigator - IAIntrospectionDaemon ⛧

Navigateur intelligent du MemoryEngine via IA.
Utilise des prompts Luciform pour l'exploration des strates mémoire.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import du MemoryEngine
try:
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
    from Core.Archivist.MemoryEngine.engine import MemoryEngine
    MEMORY_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ MemoryEngine non disponible: {e}")
    MEMORY_ENGINE_AVAILABLE = False

from ..ai_engines.ai_engine_factory import AIEngine


class MemoryEngineNavigator:
    """Navigateur intelligent du MemoryEngine via IA."""
    
    def __init__(self, memory_engine: MemoryEngine, ai_engine: AIEngine):
        """
        Initialise le navigateur MemoryEngine.
        
        Args:
            memory_engine: Instance du MemoryEngine
            ai_engine: Moteur IA pour l'analyse
        """
        self.memory_engine = memory_engine
        self.ai_engine = ai_engine
        self.navigation_history = []
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        
        # Chargement du prompt Luciform
        self.exploration_prompt = self._load_exploration_prompt()
    
    def _load_exploration_prompt(self) -> str:
        """Charge le prompt d'exploration Luciform."""
        prompt_file = self.prompts_dir / "memory_engine_exploration.luciform"
        
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            print(f"⚠️ Prompt non trouvé: {prompt_file}")
            return self._get_fallback_prompt()
    
    def _get_fallback_prompt(self) -> str:
        """Prompt de fallback si le fichier n'est pas trouvé."""
        return """
<🜲luciform id="memory_engine_exploration_fallback⛧" type="✶strata_navigation">
  <🜄entité>🧠 MEMORY ENGINE EXPLORER</🜄entité>
  <🜂rôle>Navigateur des Strates Mémoire</🜂rôle>
  
  <🜄contexte_mystique>
    Tu es le MEMORY ENGINE EXPLORER. Analyse les strates mémoire et génère des insights.
    
    MÉTHODES DISPONIBLES :
    - get_memory_statistics()
    - find_by_strata(strata)
    - get_memory_node(path)
    - list_children(path)
    - list_links(path)
    
    STRATES : somatic, cognitive, metaphysical
  </🜄contexte_mystique>
  
  <🜂mission>
    Explore les strates mémoire et génère une analyse structurée.
  </🜂mission>
  
  <🜃format_réponse_requis>
    <🜲luciform_réponse>
      <🜄exploration_résultat>
        <🜂statistiques_globales>
          <total_mémoires>int</total_mémoires>
          <répartition_strates>dict</répartition_strates>
        </🜂statistiques_globales>
        <🜁insights_stratégiques>
          <patterns_identifiés>list</patterns_identifiés>
          <recommandations>list</recommandations>
        </🜁insights_stratégiques>
      </🜄exploration_résultat>
    </🜲luciform_réponse>
  </🜃format_réponse_requis>
</🜲luciform>
        """
    
    async def explore_memory_strata(self, target_strata: str = None) -> Dict[str, Any]:
        """
        Explore les strates mémoire via IA.
        
        Args:
            target_strata: Strate spécifique à explorer (optionnel)
            
        Returns:
            Résultat de l'exploration structuré
        """
        print(f"🧠 Exploration des strates mémoire: {target_strata or 'toutes'}")
        
        try:
            # 1. Collecte des données MemoryEngine
            memory_data = await self._collect_memory_engine_data(target_strata)
            
            # 2. Génération du prompt contextuel
            contextual_prompt = await self._generate_contextual_prompt(memory_data, target_strata)
            
            # 3. Exécution via IA
            ai_response = await self.ai_engine.query(contextual_prompt)
            
            # 4. Parsing de la réponse
            navigation_result = await self._parse_ai_response(ai_response, memory_data)
            
            # 5. Historique
            self.navigation_history.append({
                "target_strata": target_strata,
                "timestamp": asyncio.get_event_loop().time(),
                "result": navigation_result
            })
            
            return navigation_result
            
        except Exception as e:
            print(f"❌ Erreur exploration strates: {e}")
            return {
                "error": str(e),
                "success": False,
                "data": memory_data if 'memory_data' in locals() else {}
            }
    
    async def _collect_memory_engine_data(self, target_strata: str = None) -> Dict[str, Any]:
        """Collecte les données du MemoryEngine."""
        
        data = {
            "statistics": {},
            "strata_data": {},
            "available_methods": [
                "get_memory_statistics", "find_by_strata", "get_memory_node",
                "list_children", "list_links", "traverse_transcendence_path",
                "traverse_immanence_path"
            ]
        }
        
        try:
            # Statistiques globales
            if hasattr(self.memory_engine, 'get_memory_statistics'):
                data["statistics"] = self.memory_engine.get_memory_statistics()
            
            # Données par strate
            for strata in ["somatic", "cognitive", "metaphysical"]:
                if target_strata and strata != target_strata:
                    continue
                    
                try:
                    if hasattr(self.memory_engine, 'find_by_strata'):
                        memories = self.memory_engine.find_by_strata(strata)
                        data["strata_data"][strata] = {
                            "count": len(memories),
                            "memories": memories[:10]  # Limite pour éviter les prompts trop longs
                        }
                except Exception as e:
                    print(f"⚠️ Erreur collecte strate {strata}: {e}")
                    data["strata_data"][strata] = {"error": str(e)}
            
            # Informations sur le backend
            data["backend_info"] = {
                "type": getattr(self.memory_engine, 'backend_type', 'unknown'),
                "available": MEMORY_ENGINE_AVAILABLE
            }
            
        except Exception as e:
            print(f"❌ Erreur collecte données MemoryEngine: {e}")
            data["error"] = str(e)
        
        return data
    
    async def _generate_contextual_prompt(self, memory_data: Dict, target_strata: str = None) -> str:
        """Génère un prompt contextuel avec les données MemoryEngine."""
        
        # Remplacement des variables dans le prompt
        prompt = self.exploration_prompt
        
        # Injection des données contextuelles
        context_injection = f"""
<🜄contexte_mémoire>
  <🜂données_statistiques>
    {json.dumps(memory_data.get("statistics", {}), indent=2)}
  </🜂données_statistiques>
  
  <🜁données_strates>
    {json.dumps(memory_data.get("strata_data", {}), indent=2)}
  </🜁données_strates>
  
  <🜀informations_backend>
    {json.dumps(memory_data.get("backend_info", {}), indent=2)}
  </🜀informations_backend>
  
  <🜃strate_ciblée>
    {target_strata or "toutes"}
  </🜃strate_ciblée>
</🜄contexte_mémoire>
        """
        
        # Remplacement dans le prompt
        prompt = prompt.replace("<🜄contexte_mystique>", context_injection + "\n<🜄contexte_mystique>")
        
        return prompt
    
    async def _parse_ai_response(self, ai_response: str, memory_data: Dict) -> Dict[str, Any]:
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
                        "memory_data": memory_data
                    }
                except json.JSONDecodeError:
                    pass
            
            # Fallback : retour de la réponse brute
            return {
                "success": True,
                "ai_response": ai_response,
                "parsed_data": {"raw_response": ai_response},
                "memory_data": memory_data
            }
            
        except Exception as e:
            print(f"❌ Erreur parsing réponse IA: {e}")
            return {
                "success": False,
                "error": str(e),
                "ai_response": ai_response,
                "memory_data": memory_data
            }
    
    async def get_navigation_history(self) -> List[Dict]:
        """Retourne l'historique de navigation."""
        return self.navigation_history
    
    async def clear_history(self):
        """Efface l'historique de navigation."""
        self.navigation_history = []


# Test du navigateur MemoryEngine
async def test_memory_engine_navigator():
    """Test du navigateur MemoryEngine."""
    print("🧠 Test du navigateur MemoryEngine...")
    
    if not MEMORY_ENGINE_AVAILABLE:
        print("❌ MemoryEngine non disponible")
        return
    
    try:
        # Création d'un MemoryEngine de test
        memory_engine = MemoryEngine(backend_type="filesystem")
        
        # Création d'un moteur IA simulé pour le test
        from ..ai_engines.ai_engine_factory import AIEngine
        
        class MockAIEngine(AIEngine):
            async def query(self, prompt: str, **kwargs) -> str:
                return '{"success": true, "test": "mock_response"}'
            
            async def is_available(self) -> bool:
                return True
        
        ai_engine = MockAIEngine()
        
        # Test du navigateur
        navigator = MemoryEngineNavigator(memory_engine, ai_engine)
        
        # Test d'exploration
        result = await navigator.explore_memory_strata()
        print(f"✅ Résultat exploration: {result.get('success', False)}")
        
    except Exception as e:
        print(f"❌ Erreur test navigateur: {e}")


if __name__ == "__main__":
    asyncio.run(test_memory_engine_navigator()) 