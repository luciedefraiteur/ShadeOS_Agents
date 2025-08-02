#!/usr/bin/env python3
"""
🤖 OpenAI Engine - IAIntrospectionDaemon ⛧

Moteur IA utilisant OpenAI avec vraie API.
Support complet avec gestion d'erreurs et retry.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import os
from typing import Optional, Dict, Any
from .ai_engine_factory import AIEngine

# Import OpenAI (optionnel)
try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI non installé. Installez avec: pip install openai")


class OpenAIEngine(AIEngine):
    """Moteur IA utilisant OpenAI."""
    
    def __init__(self, model: str = "gpt-4", 
                 api_key: str = None,
                 timeout: int = 60, max_retries: int = 2):
        """
        Initialise le moteur OpenAI.
        
        Args:
            model: Modèle OpenAI à utiliser
            api_key: Clé API OpenAI (ou variable d'environnement)
            timeout: Timeout en secondes
            max_retries: Nombre maximum de tentatives
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI non disponible. Installez avec: pip install openai")
        
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = None
        
        # Configuration de la clé API
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Clé API OpenAI requise (OPENAI_API_KEY ou paramètre api_key)")
        
        self.api_key = api_key
        self._available = None
    
    def _get_client(self) -> AsyncOpenAI:
        """Retourne le client OpenAI configuré."""
        if self.client is None:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                timeout=self.timeout
            )
        return self.client
    
    async def is_available(self) -> bool:
        """
        Vérifie si OpenAI est disponible.
        
        Returns:
            True si OpenAI est disponible
        """
        if self._available is not None:
            return self._available
        
        try:
            client = self._get_client()
            # Test simple avec un prompt court
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            self._available = True
            return True
        except Exception as e:
            print(f"⚠️ Erreur vérification OpenAI: {e}")
            self._available = False
            return False
    
    async def query(self, prompt: str, **kwargs) -> str:
        """
        Exécute une requête via OpenAI.
        
        Args:
            prompt: Prompt à envoyer
            **kwargs: Paramètres supplémentaires
            
        Returns:
            Réponse du modèle
        """
        if not await self.is_available():
            raise RuntimeError("OpenAI non disponible")
        
        # Paramètres de la requête
        params = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", 2048),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
            "presence_penalty": kwargs.get("presence_penalty", 0.0)
        }
        
        # Tentatives avec retry
        for attempt in range(self.max_retries):
            try:
                client = self._get_client()
                response = await client.chat.completions.create(**params)
                
                if response.choices and len(response.choices) > 0:
                    return response.choices[0].message.content
                else:
                    raise RuntimeError("Réponse OpenAI vide")
                    
            except Exception as e:
                print(f"❌ Erreur OpenAI (tentative {attempt + 1}): {e}")
                
                # Attente avant retry
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 * (attempt + 1))
        
        raise RuntimeError(f"Échec après {self.max_retries} tentatives")
    
    async def list_models(self) -> list:
        """
        Liste les modèles disponibles.
        
        Returns:
            Liste des modèles disponibles
        """
        try:
            client = self._get_client()
            response = await client.models.list()
            return [model.id for model in response.data]
        except Exception as e:
            print(f"❌ Erreur liste modèles OpenAI: {e}")
            return []
    
    async def get_usage(self) -> Dict[str, Any]:
        """
        Récupère les informations d'utilisation.
        
        Returns:
            Dict avec informations d'utilisation
        """
        try:
            client = self._get_client()
            # Note: OpenAI n'a pas d'API directe pour l'usage, 
            # mais on peut implémenter un tracking local
            return {
                "provider": "openai",
                "model": self.model,
                "status": "available"
            }
        except Exception as e:
            print(f"❌ Erreur récupération usage: {e}")
            return {"error": str(e)}


# Test du moteur OpenAI
async def test_openai_engine():
    """Test du moteur OpenAI."""
    print("🤖 Test du moteur OpenAI...")
    
    try:
        engine = OpenAIEngine()
        
        # Test de disponibilité
        available = await engine.is_available()
        print(f"✅ OpenAI disponible: {available}")
        
        if available:
            # Test de requête
            try:
                response = await engine.query("Dis-moi bonjour en français.")
                print(f"✅ Réponse: {response[:100]}...")
            except Exception as e:
                print(f"❌ Erreur requête: {e}")
        
    except Exception as e:
        print(f"❌ Erreur initialisation OpenAI: {e}")


if __name__ == "__main__":
    asyncio.run(test_openai_engine()) 