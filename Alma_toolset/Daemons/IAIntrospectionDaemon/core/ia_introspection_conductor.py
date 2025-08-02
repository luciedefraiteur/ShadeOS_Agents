#!/usr/bin/env python3
"""
🧠 IA Introspection Conductor - IAIntrospectionDaemon ⛧

Chef d'orchestre principal utilisant de vrais moteurs IA.
Coordonne l'exploration MemoryEngine, ToolRegistry et EditingSession.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

# Imports des composants
try:
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
    from Core.Archivist.MemoryEngine.engine import MemoryEngine
    from Core.Archivist.MemoryEngine.tool_memory_extension import ToolMemoryExtension
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Composants non disponibles: {e}")
    COMPONENTS_AVAILABLE = False

from ..ai_engines.ai_engine_factory import AIEngineFactory, AIEngine
from .memory_engine_navigator import MemoryEngineNavigator
from .tool_registry_explorer import ToolRegistryExplorer
from .editing_session_analyzer import EditingSessionAnalyzer


@dataclass
class IntrospectionResult:
    """Résultat d'une introspection IA complète."""
    
    timestamp: datetime = field(default_factory=datetime.now)
    memory_analysis: Optional[Dict] = None
    tool_analysis: Optional[Dict] = None
    editing_analysis: Optional[Dict] = None
    synthesis_insights: Optional[Dict] = None
    ai_engine_used: str = ""
    execution_time: float = 0.0
    success: bool = False
    errors: List[str] = field(default_factory=list)


class IAIntrospectionConductor:
    """Chef d'orchestre principal utilisant de vrais moteurs IA."""
    
    def __init__(self, primary_engine: str = "ollama", fallback_engine: str = "openai"):
        """
        Initialise le chef d'orchestre IA.
        
        Args:
            primary_engine: Moteur IA principal
            fallback_engine: Moteur IA de secours
        """
        self.primary_engine = primary_engine
        self.fallback_engine = fallback_engine
        
        # Factory IA
        self.ai_factory = AIEngineFactory(primary_engine, fallback_engine)
        
        # Composants
        self.memory_engine = None
        self.tool_extension = None
        self.ai_engine = None
        
        # Navigateurs
        self.memory_navigator = None
        self.tool_explorer = None
        self.editing_analyzer = None
        
        # Configuration
        self.config = {
            "timeout": 300,  # 5 minutes
            "max_retries": 3,
            "enable_synthesis": True,
            "save_results": True
        }
        
        # Historique
        self.introspection_history = []
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
    
    async def initialize(self) -> bool:
        """
        Initialise le daemon avec tous les composants.
        
        Returns:
            True si l'initialisation réussit
        """
        print("🧠 Initialisation du IAIntrospectionConductor...")
        
        try:
            # 1. Initialisation des moteurs IA
            print("🤖 Initialisation des moteurs IA...")
            self.ai_engine = await self.ai_factory.get_available_engine()
            if not self.ai_engine:
                print("❌ Aucun moteur IA disponible")
                return False
            
            print(f"✅ Moteur IA disponible: {type(self.ai_engine).__name__}")
            
            # 2. Initialisation des composants (si disponibles)
            if COMPONENTS_AVAILABLE:
                print("🔧 Initialisation des composants...")
                
                # MemoryEngine
                try:
                    self.memory_engine = MemoryEngine(backend_type="filesystem")
                    self.memory_navigator = MemoryEngineNavigator(self.memory_engine, self.ai_engine)
                    print("✅ MemoryEngine initialisé")
                except Exception as e:
                    print(f"⚠️ MemoryEngine non disponible: {e}")
                
                # ToolMemoryExtension
                try:
                    if self.memory_engine:
                        self.tool_extension = ToolMemoryExtension(self.memory_engine)
                        self.tool_explorer = ToolRegistryExplorer(self.tool_extension, self.ai_engine)
                        print("✅ ToolMemoryExtension initialisé")
                except Exception as e:
                    print(f"⚠️ ToolMemoryExtension non disponible: {e}")
                
                # EditingSession (à implémenter)
                try:
                    self.editing_analyzer = EditingSessionAnalyzer(self.ai_engine)
                    print("✅ EditingSession initialisé")
                except Exception as e:
                    print(f"⚠️ EditingSession non disponible: {e}")
            
            print("✅ IAIntrospectionConductor initialisé")
            return True
            
        except Exception as e:
            print(f"❌ Erreur initialisation: {e}")
            return False
    
    async def conduct_ai_introspection(self, focus: str = "comprehensive") -> IntrospectionResult:
        """
        Conduit une introspection complète via IA.
        
        Args:
            focus: Focus de l'introspection ("comprehensive", "memory", "tools", "editing")
            
        Returns:
            Résultat de l'introspection
        """
        print(f"🧠 Démarrage introspection IA: {focus}")
        start_time = time.time()
        
        result = IntrospectionResult()
        
        try:
            # 1. Analyse MemoryEngine
            if focus in ["comprehensive", "memory"] and self.memory_navigator:
                print("🧠 Analyse MemoryEngine...")
                result.memory_analysis = await self.memory_navigator.explore_memory_strata()
            
            # 2. Analyse ToolRegistry
            if focus in ["comprehensive", "tools"] and self.tool_explorer:
                print("🛠️ Analyse ToolRegistry...")
                result.tool_analysis = await self.tool_explorer.analyze_tool_ecosystem()
            
            # 3. Analyse EditingSession
            if focus in ["comprehensive", "editing"] and self.editing_analyzer:
                print("📝 Analyse EditingSession...")
                result.editing_analysis = await self.editing_analyzer.analyze_editing_patterns()
            
            # 4. Synthèse des insights
            if self.config["enable_synthesis"] and self.ai_engine:
                print("🧠 Synthèse des insights...")
                result.synthesis_insights = await self._synthesize_insights(result)
            
            # 5. Finalisation
            result.ai_engine_used = type(self.ai_engine).__name__
            result.execution_time = time.time() - start_time
            result.success = True
            
            # 6. Sauvegarde
            if self.config["save_results"]:
                await self._save_introspection_result(result)
            
            # 7. Historique
            self.introspection_history.append(result)
            
            print(f"✅ Introspection IA terminée en {result.execution_time:.2f}s")
            return result
            
        except Exception as e:
            print(f"❌ Erreur introspection IA: {e}")
            result.errors.append(str(e))
            result.success = False
            result.execution_time = time.time() - start_time
            return result
    
    async def _synthesize_insights(self, result: IntrospectionResult) -> Dict[str, Any]:
        """Synthétise les insights via IA."""
        
        try:
            # Chargement du prompt de synthèse
            synthesis_prompt = self._load_synthesis_prompt()
            
            # Préparation des données de synthèse
            synthesis_data = {
                "memory_analysis": result.memory_analysis,
                "tool_analysis": result.tool_analysis,
                "editing_analysis": result.editing_analysis
            }
            
            # Génération du prompt contextuel
            contextual_prompt = self._generate_synthesis_prompt(synthesis_prompt, synthesis_data)
            
            # Exécution via IA
            ai_response = await self.ai_engine.query(contextual_prompt)
            
            # Parsing de la réponse
            return self._parse_synthesis_response(ai_response, synthesis_data)
            
        except Exception as e:
            print(f"❌ Erreur synthèse insights: {e}")
            return {"error": str(e)}
    
    def _load_synthesis_prompt(self) -> str:
        """Charge le prompt de synthèse Luciform."""
        prompt_file = self.prompts_dir / "synthesis_insights.luciform"
        
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return self._get_fallback_synthesis_prompt()
    
    def _get_fallback_synthesis_prompt(self) -> str:
        """Prompt de synthèse de fallback."""
        return """
<🜲luciform id="synthesis_fallback⛧" type="✶meta_analysis">
  <🜄entité>🧠 INSIGHTS SYNTHESIZER</🜄entité>
  <🜂rôle>Synthétiseur des Insights</🜂rôle>
  
  <🜄contexte_mystique>
    Synthétise les insights multiples en recommandations stratégiques.
  </🜄contexte_mystique>
  
  <🜃format_réponse_requis>
    <🜲luciform_réponse>
      <🜄synthèse_résultat>
        <🜂insights_fusionnés>list</🜂insights_fusionnés>
        <🜁recommandations_unifiées>list</🜁recommandations_unifiées>
        <🜃plan_action>list</🜃plan_action>
      </🜄synthèse_résultat>
    </🜲luciform_réponse>
  </🜃format_réponse_requis>
</🜲luciform>
        """
    
    def _generate_synthesis_prompt(self, base_prompt: str, synthesis_data: Dict) -> str:
        """Génère un prompt de synthèse contextuel."""
        
        # Injection des données
        context_injection = f"""
<🜄données_synthèse>
  <🜂analyse_mémoire>
    {json.dumps(synthesis_data.get("memory_analysis", {}), indent=2)}
  </🜂analyse_mémoire>
  
  <🜁analyse_outils>
    {json.dumps(synthesis_data.get("tool_analysis", {}), indent=2)}
  </🜁analyse_outils>
  
  <🜀analyse_édition>
    {json.dumps(synthesis_data.get("editing_analysis", {}), indent=2)}
  </🜀analyse_édition>
</🜄données_synthèse>
        """
        
        # Remplacement dans le prompt
        return base_prompt.replace("<🜄contexte_mystique>", context_injection + "\n<🜄contexte_mystique>")
    
    def _parse_synthesis_response(self, ai_response: str, synthesis_data: Dict) -> Dict[str, Any]:
        """Parse la réponse de synthèse."""
        
        try:
            # Tentative de parsing JSON
            if "{" in ai_response and "}" in ai_response:
                start = ai_response.find("{")
                end = ai_response.rfind("}") + 1
                json_str = ai_response[start:end]
                
                try:
                    parsed = json.loads(json_str)
                    return {
                        "success": True,
                        "ai_response": ai_response,
                        "parsed_data": parsed,
                        "synthesis_data": synthesis_data
                    }
                except json.JSONDecodeError:
                    pass
            
            # Fallback
            return {
                "success": True,
                "ai_response": ai_response,
                "parsed_data": {"raw_response": ai_response},
                "synthesis_data": synthesis_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "ai_response": ai_response,
                "synthesis_data": synthesis_data
            }
    
    async def _save_introspection_result(self, result: IntrospectionResult):
        """Sauvegarde le résultat d'introspection."""
        
        try:
            # Création du dossier de logs
            logs_dir = Path(__file__).parent.parent / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            # Nom du fichier
            timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"introspection_result_{timestamp}.json"
            filepath = logs_dir / filename
            
            # Conversion en dict pour JSON
            result_dict = {
                "timestamp": result.timestamp.isoformat(),
                "memory_analysis": result.memory_analysis,
                "tool_analysis": result.tool_analysis,
                "editing_analysis": result.editing_analysis,
                "synthesis_insights": result.synthesis_insights,
                "ai_engine_used": result.ai_engine_used,
                "execution_time": result.execution_time,
                "success": result.success,
                "errors": result.errors
            }
            
            # Sauvegarde
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Résultat sauvegardé: {filepath}")
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
    
    async def get_introspection_history(self) -> List[IntrospectionResult]:
        """Retourne l'historique d'introspection."""
        return self.introspection_history
    
    async def test_ai_engines(self) -> Dict[str, bool]:
        """Teste tous les moteurs IA disponibles."""
        return await self.ai_factory.test_all_engines()


# Test du chef d'orchestre
async def test_ia_introspection_conductor():
    """Test du chef d'orchestre IA."""
    print("🧠 Test du IAIntrospectionConductor...")
    
    conductor = IAIntrospectionConductor()
    
    # Test d'initialisation
    success = await conductor.initialize()
    if not success:
        print("❌ Échec d'initialisation")
        return
    
    # Test des moteurs IA
    engine_status = await conductor.test_ai_engines()
    print(f"🤖 Statut des moteurs IA: {engine_status}")
    
    # Test d'introspection
    result = await conductor.conduct_ai_introspection("comprehensive")
    print(f"✅ Introspection réussie: {result.success}")
    print(f"⏱️ Temps d'exécution: {result.execution_time:.2f}s")


if __name__ == "__main__":
    asyncio.run(test_ia_introspection_conductor()) 