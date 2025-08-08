#!/usr/bin/env python3
"""
⛧ Local Provider HTTP - Provider Ollama Local via API HTTP ⛧

Provider Ollama local utilisant l'API HTTP avec gestion d'erreurs, timeout configurable
et test de connexion robuste.
"""

import asyncio
import time
import json
import aiohttp
from typing import Dict, Any, Optional
from .llm_provider import LLMProvider, ProviderStatus, LLMResponse, ProviderType, ErrorType


class LocalProviderHTTP(LLMProvider):
    """Provider Ollama local via API HTTP avec validation et gestion d'erreurs"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(ProviderType.LOCAL, config)
        
        # Configuration Ollama spécifique
        self.model = config.get('model', 'qwen2.5:7b-instruct')
        self.ollama_host = config.get('ollama_host', 'http://localhost:11434')
        self.api_base_url = f"{self.ollama_host}/api"
        
        # Validation du modèle
        if not self.model:
            raise ValueError("Modèle Ollama non spécifié")
    
    async def test_connection(self) -> ProviderStatus:
        """Test de connexion et validation du provider Ollama via API HTTP"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test de santé
                async with session.get(f"{self.api_base_url}/version", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status != 200:
                        return ProviderStatus(
                            valid=False,
                            provider_type=self.provider_type,
                            capabilities=[],
                            error=f"Ollama non accessible: HTTP {response.status}",
                            error_type=ErrorType.UNKNOWN_ERROR,
                            response_time=time.time() - start_time
                        )
                
                # Vérification que le modèle est disponible
                async with session.get(f"{self.api_base_url}/tags", timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get('models', [])
                        model_found = any(model['name'] == self.model for model in models)
                        
                        if not model_found:
                            return ProviderStatus(
                                valid=False,
                                provider_type=self.provider_type,
                                capabilities=[],
                                error=f"Modèle Ollama '{self.model}' non trouvé. Modèles disponibles: {[m['name'] for m in models]}",
                                error_type=ErrorType.MODEL_UNAVAILABLE,
                                response_time=time.time() - start_time
                            )
                    else:
                        return ProviderStatus(
                            valid=False,
                            provider_type=self.provider_type,
                            capabilities=[],
                            error=f"Impossible de récupérer la liste des modèles: HTTP {response.status}",
                            error_type=ErrorType.UNKNOWN_ERROR,
                            response_time=time.time() - start_time
                        )
                
                # Test simple avec le modèle
                test_prompt = "Test de connexion Ollama - Réponds simplement 'OK'"
                test_response = await self._call_api_generate(session, test_prompt)
                
                response_time = time.time() - start_time
                
                return ProviderStatus(
                    valid=True,
                    provider_type=self.provider_type,
                    capabilities=[
                        "text_generation",
                        "chat_completion",
                        "local_inference"
                    ],
                    response_time=response_time,
                    model_info={
                        "model": self.model,
                        "ollama_host": self.ollama_host,
                        "test_response": test_response
                    }
                )
                
        except aiohttp.ClientConnectorError:
            return ProviderStatus(
                valid=False,
                provider_type=self.provider_type,
                capabilities=[],
                error=f"Impossible de se connecter à Ollama: {self.ollama_host}. Vérifiez que Ollama est démarré.",
                error_type=ErrorType.UNKNOWN_ERROR,
                response_time=time.time() - start_time
            )
            
        except asyncio.TimeoutError:
            return ProviderStatus(
                valid=False,
                provider_type=self.provider_type,
                capabilities=[],
                error=f"Timeout Ollama après {self.timeout} secondes",
                error_type=ErrorType.TIMEOUT,
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            return ProviderStatus(
                valid=False,
                provider_type=self.provider_type,
                capabilities=[],
                error=f"Erreur Ollama inconnue: {str(e)}",
                error_type=ErrorType.UNKNOWN_ERROR,
                response_time=time.time() - start_time
            )
    
    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Génération de réponse avec gestion d'erreurs Ollama via API HTTP"""
        start_time = time.time()
        
        try:
            # Paramètres de génération
            model = kwargs.get('model', self.model)
            temperature = kwargs.get('temperature', self.temperature)
            
            # Estimation de la taille du prompt
            prompt_size = len(prompt) if self.estimate_prompt_size else None
            
            async with aiohttp.ClientSession() as session:
                # Appel à l'API
                response_text = await self._call_api_generate(
                    session, 
                    prompt, 
                    model=model, 
                    temperature=temperature
                )
            
            response_time = time.time() - start_time
            
            return self._create_success_response(
                content=response_text,
                model_used=model,
                response_time=response_time,
                prompt_size=prompt_size
            )
            
        except asyncio.TimeoutError:
            return self._create_error_response(
                f"Timeout Ollama après {self.timeout} secondes",
                ErrorType.TIMEOUT,
                time.time() - start_time
            )
            
        except Exception as e:
            return self._create_error_response(
                f"Erreur Ollama inconnue: {str(e)}",
                ErrorType.UNKNOWN_ERROR,
                time.time() - start_time
            )
    
    async def _call_api_generate(self, session: aiohttp.ClientSession, prompt: str, 
                                model: str = None, temperature: float = None) -> str:
        """Appel à l'API generate d'Ollama"""
        model = model or self.model
        temperature = temperature or self.temperature
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        # Ajouter les paramètres optionnels
        if temperature != 0.7:  # Valeur par défaut
            payload["options"] = {"temperature": temperature}
        
        async with session.post(
            f"{self.api_base_url}/generate",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as response:
            
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Erreur API Ollama: HTTP {response.status} - {error_text}")
            
            data = await response.json()
            return data.get('response', '')
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Informations spécifiques au provider Ollama HTTP"""
        base_info = super().get_provider_info()
        base_info.update({
            "model": self.model,
            "ollama_host": self.ollama_host,
            "api_base_url": self.api_base_url,
            "provider_type": "http_api"
        })
        return base_info 