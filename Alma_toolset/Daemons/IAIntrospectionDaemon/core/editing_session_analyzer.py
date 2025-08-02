#!/usr/bin/env python3
"""
📝 Editing Session Analyzer - IAIntrospectionDaemon ⛧

Analyseur intelligent des sessions d'édition via IA.
Utilise des prompts Luciform pour l'analyse des patterns d'édition.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..ai_engines.ai_engine_factory import AIEngine


class EditingSessionAnalyzer:
    """Analyseur intelligent des sessions d'édition via IA."""
    
    def __init__(self, ai_engine: AIEngine):
        """
        Initialise l'analyseur EditingSession.
        
        Args:
            ai_engine: Moteur IA pour l'analyse
        """
        self.ai_engine = ai_engine
        self.analysis_history = []
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        
        # Chargement du prompt Luciform
        self.analysis_prompt = self._load_analysis_prompt()
    
    def _load_analysis_prompt(self) -> str:
        """Charge le prompt d'analyse Luciform."""
        prompt_file = self.prompts_dir / "editing_session_analysis.luciform"
        
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            print(f"⚠️ Prompt non trouvé: {prompt_file}")
            return self._get_fallback_prompt()
    
    def _get_fallback_prompt(self) -> str:
        """Prompt de fallback si le fichier n'est pas trouvé."""
        return """
<🜲luciform id="editing_session_analysis_fallback⛧" type="✶session_intelligence">
  <🜄entité>📝 EDITING SESSION ANALYZER</🜄entité>
  <🜂rôle>Analyste des Sessions d'Édition</🜂rôle>
  
  <🜄contexte_mystique>
    Tu es l'EDITING SESSION ANALYZER. Analyse les patterns d'édition et génère des insights.
    
    COMPOSANTS :
    - PartitioningSystem : Découpage intelligent du code
    - ASTPartitioners : Analyse syntaxique abstraite
    - LocationTracker : Suivi des positions
    
    MISSION : Analyse les sessions d'édition et génère des insights sur les patterns.
  </🜄contexte_mystique>
  
  <🜃format_réponse_requis>
    <🜲luciform_réponse>
      <🜄analyse_résultat>
        <🜂patterns_édition>list</🜂patterns_édition>
        <🜁optimisations_identifiées>list</🜁optimisations_identifiées>
        <🜀recommandations>list</🜀recommandations>
      </🜄analyse_résultat>
    </🜲luciform_réponse>
  </🜃format_réponse_requis>
</🜲luciform>
        """
    
    async def analyze_editing_patterns(self) -> Dict[str, Any]:
        """
        Analyse les patterns d'édition via IA.
        
        Returns:
            Résultat de l'analyse structuré
        """
        print("📝 Analyse des patterns d'édition...")
        
        try:
            # 1. Collecte des données d'édition (simulée pour l'instant)
            editing_data = await self._collect_editing_data()
            
            # 2. Génération du prompt contextuel
            contextual_prompt = await self._generate_contextual_prompt(editing_data)
            
            # 3. Exécution via IA
            ai_response = await self.ai_engine.query(contextual_prompt)
            
            # 4. Parsing de la réponse
            analysis_result = await self._parse_ai_response(ai_response, editing_data)
            
            # 5. Historique
            self.analysis_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "result": analysis_result
            })
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ Erreur analyse patterns: {e}")
            return {
                "error": str(e),
                "success": False,
                "data": editing_data if 'editing_data' in locals() else {}
            }
    
    async def _collect_editing_data(self) -> Dict[str, Any]:
        """Collecte les données d'édition (simulée pour l'instant)."""
        
        # Données simulées - à remplacer par de vraies données EditingSession
        data = {
            "partitioning_methods": ["ast", "regex", "textual"],
            "languages_supported": ["python", "javascript", "markdown"],
            "editing_patterns": [
                "file_creation",
                "code_modification", 
                "refactoring",
                "documentation_update"
            ],
            "statistics": {
                "total_sessions": 0,
                "average_session_duration": 0,
                "most_edited_files": []
            },
            "available_components": [
                "PartitioningSystem",
                "ASTPartitioners", 
                "TreeSitterPartitioner",
                "LocationTracker",
                "LanguageRegistry"
            ]
        }
        
        return data
    
    async def _generate_contextual_prompt(self, editing_data: Dict) -> str:
        """Génère un prompt contextuel avec les données d'édition."""
        
        # Remplacement des variables dans le prompt
        prompt = self.analysis_prompt
        
        # Injection des données contextuelles
        context_injection = f"""
<🜄contexte_édition>
  <🜂données_édition>
    {json.dumps(editing_data, indent=2)}
  </🜂données_édition>
</🜄contexte_édition>
        """
        
        # Remplacement dans le prompt
        prompt = prompt.replace("<🜄contexte_mystique>", context_injection + "\n<🜄contexte_mystique>")
        
        return prompt
    
    async def _parse_ai_response(self, ai_response: str, editing_data: Dict) -> Dict[str, Any]:
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
                        "editing_data": editing_data
                    }
                except json.JSONDecodeError:
                    pass
            
            # Fallback : retour de la réponse brute
            return {
                "success": True,
                "ai_response": ai_response,
                "parsed_data": {"raw_response": ai_response},
                "editing_data": editing_data
            }
            
        except Exception as e:
            print(f"❌ Erreur parsing réponse IA: {e}")
            return {
                "success": False,
                "error": str(e),
                "ai_response": ai_response,
                "editing_data": editing_data
            }
    
    async def get_analysis_history(self) -> List[Dict]:
        """Retourne l'historique d'analyse."""
        return self.analysis_history
    
    async def clear_history(self):
        """Efface l'historique d'analyse."""
        self.analysis_history = []


# Test de l'analyseur EditingSession
async def test_editing_session_analyzer():
    """Test de l'analyseur EditingSession."""
    print("📝 Test de l'analyseur EditingSession...")
    
    try:
        # Création d'un moteur IA simulé pour le test
        from ..ai_engines.ai_engine_factory import AIEngine
        
        class MockAIEngine(AIEngine):
            async def query(self, prompt: str, **kwargs) -> str:
                return '{"success": true, "test": "mock_editing_analysis"}'
            
            async def is_available(self) -> bool:
                return True
        
        ai_engine = MockAIEngine()
        
        # Test de l'analyseur
        analyzer = EditingSessionAnalyzer(ai_engine)
        
        # Test d'analyse
        result = await analyzer.analyze_editing_patterns()
        print(f"✅ Résultat analyse: {result.get('success', False)}")
        
    except Exception as e:
        print(f"❌ Erreur test analyseur: {e}")


if __name__ == "__main__":
    asyncio.run(test_editing_session_analyzer()) 