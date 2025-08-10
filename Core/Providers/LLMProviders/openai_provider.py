#!/usr/bin/env python3
"""
⛧ OpenAI Provider - Provider OpenAI pour l'Archiviste ⛧

Provider OpenAI avec validation complète, gestion d'erreurs détaillée
et test de connexion robuste.
"""

import os
import time
import asyncio
from typing import Dict, Any, Optional
from .llm_provider import LLMProvider, ProviderStatus, LLMResponse, ProviderType, ErrorType


class OpenAIProvider(LLMProvider):
    """Provider OpenAI avec validation et gestion d'erreurs"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(ProviderType.OPENAI, config)
        
        # Configuration OpenAI spécifique
        self.api_key = config.get('api_key') or os.getenv('OPENAI_API_KEY')
        self.model = config.get('model', 'gpt-4')
        self.organization = config.get('organization')
        
        # Validation de la clé API
        if not self.api_key:
            raise ValueError("Clé API OpenAI manquante")
    
    async def test_connection(self) -> ProviderStatus:
        """Test de connexion et validation du provider OpenAI"""
        start_time = time.time()
        
        try:
            # Import OpenAI ici pour éviter les dépendances
            import openai
            
            # Configuration du client
            client_config = {"api_key": self.api_key}
            if self.organization:
                client_config["organization"] = self.organization
            
            client = openai.AsyncOpenAI(**client_config)
            
            # Test simple avec un prompt minimal
            test_prompt = "Test de connexion OpenAI - Réponds simplement 'OK'"
            
            response = await self._execute_with_timeout(
                client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": test_prompt}],
                    max_tokens=10,
                    temperature=0
                ),
                self.timeout
            )
            
            response_time = time.time() - start_time
            
            return ProviderStatus(
                valid=True,
                provider_type=self.provider_type,
                capabilities=[
                    "chat_completion",
                    "text_generation", 
                    "streaming",
                    "function_calling"
                ],
                response_time=response_time,
                model_info={
                    "model": self.model,
                    "organization": self.organization,
                    "response": response.choices[0].message.content
                }
            )
            
        except ImportError:
            return ProviderStatus(
                valid=False,
                provider_type=self.provider_type,
                capabilities=[],
                error="Module OpenAI non installé. Installez avec: pip install openai",
                error_type=ErrorType.UNKNOWN_ERROR,
                response_time=time.time() - start_time
            )
            
        except openai.AuthenticationError:
            return ProviderStatus(
                valid=False,
                provider_type=self.provider_type,
                capabilities=[],
                error="Clé API OpenAI invalide ou expirée",
                error_type=ErrorType.API_KEY_INVALID,
                response_time=time.time() - start_time
            )
            
        except openai.RateLimitError:
            return ProviderStatus(
                valid=False,
                provider_type=self.provider_type,
                capabilities=[],
                error="Limite de taux OpenAI dépassée",
                error_type=ErrorType.RATE_LIMIT,
                response_time=time.time() - start_time
            )
            
        except openai.QuotaExceededError:
            return ProviderStatus(
                valid=False,
                provider_type=self.provider_type,
                capabilities=[],
                error="Quota OpenAI épuisé",
                error_type=ErrorType.TOKENS_EXHAUSTED,
                response_time=time.time() - start_time
            )
            
        except openai.ModelNotFoundError:
            return ProviderStatus(
                valid=False,
                provider_type=self.provider_type,
                capabilities=[],
                error=f"Modèle OpenAI '{self.model}' non disponible",
                error_type=ErrorType.MODEL_UNAVAILABLE,
                response_time=time.time() - start_time
            )
            
        except asyncio.TimeoutError:
            return ProviderStatus(
                valid=False,
                provider_type=self.provider_type,
                capabilities=[],
                error=f"Timeout OpenAI après {self.timeout} secondes",
                error_type=ErrorType.TIMEOUT,
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            return ProviderStatus(
                valid=False,
                provider_type=self.provider_type,
                capabilities=[],
                error=f"Erreur OpenAI inconnue: {str(e)}",
                error_type=ErrorType.UNKNOWN_ERROR,
                response_time=time.time() - start_time
            )
    
    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Génération de réponse avec gestion d'erreurs OpenAI"""
        start_time = time.time()
        
        try:
            import openai
            
            # Configuration du client
            client_config = {"api_key": self.api_key}
            if self.organization:
                client_config["organization"] = self.organization
            
            client = openai.AsyncOpenAI(**client_config)
            
            # Paramètres de génération
            generation_params = {
                "model": kwargs.get('model', self.model),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get('temperature', self.temperature),
                "max_tokens": kwargs.get('max_tokens', self.max_tokens),
            }
            
            # Suppression des paramètres None
            generation_params = {k: v for k, v in generation_params.items() if v is not None}
            
            # Estimation de la taille du prompt
            prompt_size = self.estimate_prompt_size(prompt) if self.estimate_prompt_size else None
            
            # Génération de la réponse
            response = await self._execute_with_timeout(
                client.chat.completions.create(**generation_params),
                kwargs.get('timeout', self.timeout)
            )
            
            response_time = time.time() - start_time
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            return self._create_success_response(
                content=content,
                model_used=generation_params["model"],
                response_time=response_time,
                tokens_used=tokens_used,
                prompt_size=prompt_size
            )
            
        except ImportError:
            return self._create_error_response(
                "Module OpenAI non installé. Installez avec: pip install openai",
                ErrorType.UNKNOWN_ERROR,
                time.time() - start_time
            )
            
        except openai.AuthenticationError:
            return self._create_error_response(
                "Clé API OpenAI invalide ou expirée",
                ErrorType.API_KEY_INVALID,
                time.time() - start_time
            )
            
        except openai.RateLimitError:
            return self._create_error_response(
                "Limite de taux OpenAI dépassée",
                ErrorType.RATE_LIMIT,
                time.time() - start_time
            )
            
        except openai.QuotaExceededError:
            return self._create_error_response(
                "Quota OpenAI épuisé",
                ErrorType.TOKENS_EXHAUSTED,
                time.time() - start_time
            )
            
        except openai.ModelNotFoundError:
            return self._create_error_response(
                f"Modèle OpenAI '{self.model}' non disponible",
                ErrorType.MODEL_UNAVAILABLE,
                time.time() - start_time
            )
            
        except asyncio.TimeoutError:
            return self._create_error_response(
                f"Timeout OpenAI après {self.timeout} secondes",
                ErrorType.TIMEOUT,
                time.time() - start_time
            )
            
        except Exception as e:
            return self._create_error_response(
                f"Erreur OpenAI inconnue: {str(e)}",
                ErrorType.UNKNOWN_ERROR,
                time.time() - start_time
            )
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Informations spécifiques au provider OpenAI"""
        base_info = super().get_provider_info()
        base_info.update({
            "model": self.model,
            "organization": self.organization,
            "api_key_configured": bool(self.api_key)
        })
        return base_info 