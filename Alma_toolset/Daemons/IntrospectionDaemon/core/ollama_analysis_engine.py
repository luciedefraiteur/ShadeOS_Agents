#!/usr/bin/env python3
"""
🧠 Ollama Analysis Engine - IntrospectionDaemon ⛧

Moteur d'analyse réel utilisant Ollama avec qwen2.5:7b-instruct.
Remplace la simulation par de vraies interactions avec l'IA.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import subprocess
import requests

@dataclass
class OllamaResponse:
    """Réponse d'Ollama avec métadonnées."""
    
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    response_time: float
    success: bool
    error_message: Optional[str] = None

class OllamaAnalysisEngine:
    """Moteur d'analyse réel utilisant Ollama."""
    
    def __init__(self, model: str = "qwen2.5:7b-instruct"):
        """
        Initialise le moteur d'analyse Ollama.
        
        Args:
            model: Modèle Ollama à utiliser
        """
        self.model = model
        self.ollama_url = "http://localhost:11434"
        self.timeout = 120  # 2 minutes timeout
        
        # Configuration du modèle
        self.model_config = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "num_ctx": 4096
        }
        
        # Vérification de la disponibilité
        self._check_ollama_availability()
    
    def _check_ollama_availability(self):
        """Vérifie la disponibilité d'Ollama."""
        
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                
                if self.model in model_names:
                    print(f"✅ Ollama disponible avec {self.model}")
                else:
                    print(f"⚠️ Modèle {self.model} non trouvé. Modèles disponibles : {model_names}")
                    # Tentative de pull du modèle
                    self._pull_model()
            else:
                print(f"❌ Ollama non accessible : {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur connexion Ollama : {e}")
            print("💡 Assurez-vous qu'Ollama est démarré : ollama serve")
    
    def _pull_model(self):
        """Télécharge le modèle si nécessaire."""
        
        print(f"📥 Téléchargement du modèle {self.model}...")
        try:
            result = subprocess.run(
                ["ollama", "pull", self.model],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            if result.returncode == 0:
                print(f"✅ Modèle {self.model} téléchargé avec succès")
            else:
                print(f"❌ Erreur téléchargement : {result.stderr}")
                
        except Exception as e:
            print(f"❌ Erreur pull modèle : {e}")
    
    async def execute_introspection(self, 
                                  prompt: str, 
                                  analysis_type: str) -> Dict[str, Any]:
        """
        Exécute une introspection réelle avec Ollama.
        
        Args:
            prompt: Prompt d'introspection
            analysis_type: Type d'analyse
            
        Returns:
            Dict: Résultat de l'analyse
        """
        print(f"🧠 Exécution introspection réelle avec {self.model}...")
        start_time = time.time()
        
        try:
            # Envoi du prompt à Ollama
            ollama_response = await self._send_to_ollama(prompt)
            
            if not ollama_response.success:
                print(f"❌ Erreur Ollama : {ollama_response.error_message}")
                return self._create_error_result(analysis_type, ollama_response.error_message)
            
            # Parsing de la réponse
            analysis_result = await self._parse_introspection_response(
                ollama_response.content, analysis_type
            )
            
            # Ajout des métadonnées Ollama
            analysis_result["ollama_metadata"] = {
                "model": ollama_response.model,
                "prompt_tokens": ollama_response.prompt_tokens,
                "completion_tokens": ollama_response.completion_tokens,
                "total_tokens": ollama_response.total_tokens,
                "response_time": ollama_response.response_time,
                "analysis_time": time.time() - start_time
            }
            
            print(f"✅ Introspection terminée en {time.time() - start_time:.2f}s")
            print(f"   Tokens utilisés : {ollama_response.total_tokens}")
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ Erreur introspection : {e}")
            return self._create_error_result(analysis_type, str(e))
    
    async def _send_to_ollama(self, prompt: str) -> OllamaResponse:
        """Envoie un prompt à Ollama et retourne la réponse."""
        
        start_time = time.time()
        
        # Préparation de la requête
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": self.model_config
        }
        
        try:
            print(f"📤 Envoi prompt à Ollama ({len(prompt)} caractères)...")
            
            # Envoi asynchrone simulé (requests est synchrone)
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: requests.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=self.timeout
                )
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                return OllamaResponse(
                    content=data.get("response", ""),
                    model=data.get("model", self.model),
                    prompt_tokens=data.get("prompt_eval_count", 0),
                    completion_tokens=data.get("eval_count", 0),
                    total_tokens=data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                    response_time=response_time,
                    success=True
                )
            else:
                return OllamaResponse(
                    content="",
                    model=self.model,
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    response_time=response_time,
                    success=False,
                    error_message=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            return OllamaResponse(
                content="",
                model=self.model,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    async def _parse_introspection_response(self, 
                                          response: str, 
                                          analysis_type: str) -> Dict[str, Any]:
        """Parse la réponse d'introspection d'Ollama."""
        
        # Tentative d'extraction JSON si présent
        json_content = self._extract_json_from_response(response)
        
        if json_content:
            # Réponse structurée trouvée
            result = json_content
        else:
            # Parsing textuel de la réponse
            result = await self._parse_text_response(response, analysis_type)
        
        # Ajout de la réponse brute
        result["raw_response"] = response
        result["response_length"] = len(response)
        
        return result
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict]:
        """Extrait du JSON de la réponse si présent."""
        
        try:
            # Recherche de blocs JSON
            import re
            
            # Pattern pour JSON entre ```json et ```
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            match = re.search(json_pattern, response, re.DOTALL)
            
            if match:
                return json.loads(match.group(1))
            
            # Pattern pour JSON direct
            json_pattern = r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})'
            matches = re.findall(json_pattern, response, re.DOTALL)
            
            for match in matches:
                try:
                    return json.loads(match)
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Erreur extraction JSON : {e}")
        
        return None
    
    async def _parse_text_response(self, 
                                 response: str, 
                                 analysis_type: str) -> Dict[str, Any]:
        """Parse une réponse textuelle d'Ollama."""
        
        # Extraction d'informations par patterns
        result = {
            "analysis_type": analysis_type,
            "components_analyzed": self._extract_components(response),
            "capabilities_discovered": self._extract_capabilities(response),
            "insights": self._extract_insights(response),
            "recommendations": self._extract_recommendations(response),
            "improvement_suggestions": self._extract_improvements(response),
            "evolution_recommendations": self._extract_evolution_suggestions(response)
        }
        
        return result
    
    def _extract_components(self, text: str) -> Dict[str, Any]:
        """Extrait les composants mentionnés dans le texte."""
        
        components = {}
        
        # Recherche de mentions de composants
        component_keywords = [
            "memory_engine", "tool_registry", "editing_session",
            "prompt_generator", "context_injector", "analysis_engine"
        ]
        
        for keyword in component_keywords:
            if keyword in text.lower():
                components[keyword] = {
                    "mentioned": True,
                    "status": "analyzed",
                    "health": 0.8  # Score par défaut
                }
        
        return components
    
    def _extract_capabilities(self, text: str) -> Dict[str, float]:
        """Extrait les capacités mentionnées dans le texte."""
        
        capabilities = {}
        
        # Recherche de mentions de capacités
        capability_keywords = [
            "introspection", "auto_prompting", "context_injection", 
            "evolution", "analysis", "optimization"
        ]
        
        for keyword in capability_keywords:
            if keyword in text.lower():
                capabilities[keyword] = 0.7  # Score par défaut
        
        return capabilities
    
    def _extract_insights(self, text: str) -> List[str]:
        """Extrait les insights du texte."""
        
        insights = []
        
        # Recherche de patterns d'insights
        insight_patterns = [
            r"insight[s]?[:\-]\s*(.+?)(?:\n|$)",
            r"observation[s]?[:\-]\s*(.+?)(?:\n|$)",
            r"finding[s]?[:\-]\s*(.+?)(?:\n|$)"
        ]
        
        import re
        for pattern in insight_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            insights.extend(matches)
        
        # Si pas d'insights structurés, extraction de phrases clés
        if not insights:
            sentences = text.split('.')
            for sentence in sentences[:3]:  # Premières phrases
                if len(sentence.strip()) > 20:
                    insights.append(sentence.strip())
        
        return insights[:5]  # Limite à 5 insights
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extrait les recommandations du texte."""
        
        recommendations = []
        
        # Recherche de patterns de recommandations
        rec_patterns = [
            r"recommend[s]?[:\-]\s*(.+?)(?:\n|$)",
            r"suggest[s]?[:\-]\s*(.+?)(?:\n|$)",
            r"should[:\-]\s*(.+?)(?:\n|$)"
        ]
        
        import re
        for pattern in rec_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            recommendations.extend(matches)
        
        return recommendations[:5]
    
    def _extract_improvements(self, text: str) -> List[str]:
        """Extrait les suggestions d'amélioration."""
        
        improvements = []
        
        # Recherche de patterns d'amélioration
        imp_patterns = [
            r"improv[e|ement][s]?[:\-]\s*(.+?)(?:\n|$)",
            r"enhance[s]?[:\-]\s*(.+?)(?:\n|$)",
            r"optimize[s]?[:\-]\s*(.+?)(?:\n|$)"
        ]
        
        import re
        for pattern in imp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            improvements.extend(matches)
        
        return improvements[:5]
    
    def _extract_evolution_suggestions(self, text: str) -> List[str]:
        """Extrait les suggestions d'évolution."""
        
        evolutions = []
        
        # Recherche de patterns d'évolution
        evo_patterns = [
            r"evolv[e|ution][s]?[:\-]\s*(.+?)(?:\n|$)",
            r"future[:\-]\s*(.+?)(?:\n|$)",
            r"next step[s]?[:\-]\s*(.+?)(?:\n|$)"
        ]
        
        import re
        for pattern in evo_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            evolutions.extend(matches)
        
        return evolutions[:5]
    
    def _create_error_result(self, analysis_type: str, error_message: str) -> Dict[str, Any]:
        """Crée un résultat d'erreur."""
        
        return {
            "analysis_type": analysis_type,
            "components_analyzed": {},
            "capabilities_discovered": {},
            "insights": [f"Error occurred: {error_message}"],
            "recommendations": ["Fix Ollama connection", "Retry analysis"],
            "improvement_suggestions": ["Check Ollama service", "Verify model availability"],
            "evolution_recommendations": ["Implement error recovery"],
            "error": True,
            "error_message": error_message,
            "raw_response": "",
            "response_length": 0
        }

# Test de connexion Ollama
async def test_ollama_connection():
    """Teste la connexion à Ollama."""
    
    print("🧪 Test de connexion Ollama...")
    
    engine = OllamaAnalysisEngine()
    
    test_prompt = """
Analyse ce système d'introspection :

Composants :
- memory_engine : actif (santé: 0.9)
- tool_registry : actif (santé: 0.8)

Capacités :
- introspection : 0.8
- auto_prompting : 0.7

Génère une analyse JSON avec :
- État des composants
- Recommandations d'amélioration
- Suggestions d'évolution
    """
    
    result = await engine.execute_introspection(test_prompt, "test")
    
    if result.get("error"):
        print(f"❌ Test échoué : {result['error_message']}")
    else:
        print(f"✅ Test réussi !")
        print(f"   Insights : {len(result.get('insights', []))}")
        print(f"   Recommandations : {len(result.get('recommendations', []))}")
        if "ollama_metadata" in result:
            print(f"   Tokens : {result['ollama_metadata']['total_tokens']}")

if __name__ == "__main__":
    asyncio.run(test_ollama_connection())
