#!/usr/bin/env python3
"""
🦙 Ollama Engine - IAIntrospectionDaemon ⛧

Moteur IA utilisant Ollama avec vraie API.
Support complet avec gestion d'erreurs et retry.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import aiohttp
import json
from typing import Optional, Dict, Any
from .ai_engine_factory import AIEngine


class OllamaEngine(AIEngine):
    """Moteur IA utilisant Ollama."""
    
    def __init__(self, model: str = "qwen2.5:7b-instruct", 
                 base_url: str = "http://localhost:11434",
                 timeout: int = 30, max_retries: int = 3):
        """
        Initialise le moteur Ollama.
        
        Args:
            model: Modèle Ollama à utiliser
            base_url: URL de base d'Ollama
            timeout: Timeout en secondes
            max_retries: Nombre maximum de tentatives
        """
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = None
        self._available = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Retourne une session HTTP réutilisable."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def is_available(self) -> bool:
        """
        Vérifie si Ollama est disponible.
        
        Returns:
            True si Ollama est disponible
        """
        if self._available is not None:
            return self._available
        
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model["name"] for model in data.get("models", [])]
                    self._available = self.model in models
                    return self._available
                else:
                    self._available = False
                    return False
        except Exception as e:
            print(f"⚠️ Erreur vérification Ollama: {e}")
            self._available = False
            return False
    
    async def query(self, prompt: str, **kwargs) -> str:
        """
        Exécute une requête via Ollama.
        
        Args:
            prompt: Prompt à envoyer
            **kwargs: Paramètres supplémentaires
            
        Returns:
            Réponse du modèle
        """
        if not await self.is_available():
            raise RuntimeError(f"Ollama non disponible ou modèle {self.model} non trouvé")
        
        # Paramètres de la requête
        params = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "top_k": kwargs.get("top_k", 40),
                "num_predict": kwargs.get("max_tokens", 2048)
            }
        }
        
        # Tentatives avec retry
        for attempt in range(self.max_retries):
            try:
                session = await self._get_session()
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "")
                    else:
                        error_text = await response.text()
                        print(f"❌ Erreur Ollama (tentative {attempt + 1}): {error_text}")
                        
            except asyncio.TimeoutError:
                print(f"⏰ Timeout Ollama (tentative {attempt + 1})")
            except Exception as e:
                print(f"❌ Erreur Ollama (tentative {attempt + 1}): {e}")
            
            # Attente avant retry
            if attempt < self.max_retries - 1:
                await asyncio.sleep(1 * (attempt + 1))
        
        raise RuntimeError(f"Échec après {self.max_retries} tentatives")
    
    async def list_models(self) -> list:
        """
        Liste les modèles disponibles.
        
        Returns:
            Liste des modèles disponibles
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return [model["name"] for model in data.get("models", [])]
                else:
                    return []
        except Exception as e:
            print(f"❌ Erreur liste modèles: {e}")
            return []
    
    async def pull_model(self, model: str) -> bool:
        """
        Télécharge un modèle.
        
        Args:
            model: Nom du modèle à télécharger
            
        Returns:
            True si succès
        """
        try:
            session = await self._get_session()
            params = {"name": model}
            async with session.post(f"{self.base_url}/api/pull", json=params) as response:
                return response.status == 200
        except Exception as e:
            print(f"❌ Erreur téléchargement modèle {model}: {e}")
            return False
    
    async def close(self):
        """Ferme la session HTTP."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Destructeur pour fermer la session."""
        if self.session and not self.session.closed:
            asyncio.create_task(self.session.close())


# Test du moteur Ollama
async def test_ollama_engine():
    """Test du moteur Ollama."""
    print("🦙 Test du moteur Ollama...")
    
    engine = OllamaEngine()
    
    # Test de disponibilité
    available = await engine.is_available()
    print(f"✅ Ollama disponible: {available}")
    
    if available:
        # Test de requête
        try:
            response = await engine.query("Dis-moi bonjour en français.")
            print(f"✅ Réponse: {response[:100]}...")
        except Exception as e:
            print(f"❌ Erreur requête: {e}")
    
    await engine.close()


if __name__ == "__main__":
    asyncio.run(test_ollama_engine()) 