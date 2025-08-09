#!/usr/bin/env python3
"""
⛧ Provider Factory - Factory pour les Providers LLM ⛧

Factory pattern pour créer et valider les providers LLM
avec gestion d'erreurs et configuration flexible.
"""

import time
from typing import Dict, Any, Optional
from .llm_provider import LLMProvider, ProviderType, ValidationResult, ErrorType
from .openai_provider import OpenAIProvider
from .local_provider import LocalProvider
from .local_provider_http import LocalProviderHTTP


class ProviderFactory:
    """Factory pour créer et valider les providers LLM"""
    
    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> LLMProvider:
        """Création d'un provider selon le type spécifié"""
        
        # Normalisation du type
        provider_type = provider_type.lower().strip()
        
        if provider_type == "openai":
            return OpenAIProvider(kwargs)
        elif provider_type == "local":
            # Utiliser le provider HTTP par défaut
            return LocalProviderHTTP(kwargs)
        elif provider_type == "local_subprocess":
            # Ancien provider subprocess (pour compatibilité)
            return LocalProvider(kwargs)
        elif provider_type == "gemini":
            # Charge paresseuse pour éviter dépendances manquantes
            from .providers_optional.gemini_provider import GeminiProvider
            return GeminiProvider(kwargs)
        elif provider_type == "anthropic":
            from .providers_optional.anthropic_provider import AnthropicProvider
            return AnthropicProvider(kwargs)
        else:
            raise ValueError(f"Provider inconnu: {provider_type}. Types supportés: openai, local, gemini, anthropic")
    
    @staticmethod
    async def validate_provider(provider: LLMProvider) -> ValidationResult:
        """Validation complète d'un provider"""
        start_time = time.time()
        
        try:
            # Test de connexion
            status = await provider.test_connection()
            
            return ValidationResult(
                valid=status.valid,
                provider_type=provider.provider_type,
                capabilities=status.capabilities,
                error=status.error,
                error_type=status.error_type,
                test_time=time.time() - start_time
            )
            
        except Exception as e:
            return ValidationResult(
                valid=False,
                provider_type=provider.provider_type,
                capabilities=[],
                error=str(e),
                error_type=ErrorType.UNKNOWN_ERROR,
                test_time=time.time() - start_time
            )
    
    @staticmethod
    async def create_and_validate_provider(provider_type: str, **kwargs) -> tuple[LLMProvider, ValidationResult]:
        """Création et validation d'un provider en une seule opération"""
        
        # Création du provider
        provider = ProviderFactory.create_provider(provider_type, **kwargs)
        
        # Validation du provider
        validation = await ProviderFactory.validate_provider(provider)
        
        return provider, validation
    
    @staticmethod
    def get_available_providers() -> Dict[str, Dict[str, Any]]:
        """Liste des providers disponibles avec leurs configurations"""
        return {
            "openai": {
                "description": "Provider OpenAI GPT-4",
                "required_config": ["api_key"],
                "optional_config": ["model", "organization", "timeout", "max_tokens"],
                "capabilities": ["chat_completion", "text_generation", "streaming", "function_calling"]
            },
            "local": {
                "description": "Provider Ollama Local (API HTTP)",
                "required_config": ["model"],
                "optional_config": ["ollama_host", "timeout", "temperature"],
                "capabilities": ["text_generation", "chat_completion", "local_inference"]
            },
            "local_subprocess": {
                "description": "Provider Ollama Local (Subprocess)",
                "required_config": ["model"],
                "optional_config": ["ollama_host", "ollama_binary", "timeout", "temperature"],
                "capabilities": ["text_generation", "chat_completion", "local_inference"]
            },
            "gemini": {
                "description": "Google Gemini (multi-clés via ~/.shadeos_env)",
                "required_config": ["model"],
                "optional_config": ["timeout", "temperature"],
                "capabilities": ["text_generation", "chat_completion"]
            },
            "anthropic": {
                "description": "Anthropic Claude",
                "required_config": ["model"],
                "optional_config": ["timeout", "temperature"],
                "capabilities": ["text_generation", "chat_completion"]
            }
        }
    
    @staticmethod
    def validate_config(provider_type: str, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validation de la configuration d'un provider"""
        
        providers_info = ProviderFactory.get_available_providers()
        
        if provider_type not in providers_info:
            return False, f"Provider inconnu: {provider_type}"
        
        provider_info = providers_info[provider_type]
        
        # Vérification des configurations requises
        for required in provider_info["required_config"]:
            if required not in config and required != "api_key":  # api_key peut venir de l'environnement
                return False, f"Configuration requise manquante: {required}"
        
        # Vérification spécifique pour OpenAI
        if provider_type == "openai":
            api_key = config.get('api_key')
            if not api_key:
                import os
                if not os.getenv('OPENAI_API_KEY'):
                    return False, "Clé API OpenAI manquante (api_key ou OPENAI_API_KEY)"
        
        return True, None
    
    @staticmethod
    def create_default_config(provider_type: str) -> Dict[str, Any]:
        """Création d'une configuration par défaut pour un provider"""
        
        if provider_type == "openai":
            return {
                "model": "gpt-4",
                "timeout": 30,
                "temperature": 0.7,
                "enable_timeout": True,
                "estimate_prompt_size": True
            }
        elif provider_type == "gemini":
            return {
                "model": "gemini-1.5-pro",
                "timeout": 30,
                "temperature": 0.7,
                "enable_timeout": True,
                "estimate_prompt_size": True
            }
        elif provider_type == "local":
            return {
                "model": "qwen2.5:7b-instruct",
                "ollama_host": "http://localhost:11434",
                "ollama_binary": "ollama",
                "timeout": 60,  # Plus long pour les LLMs locaux
                "temperature": 0.7,
                "enable_timeout": True,
                "estimate_prompt_size": True
            }
        else:
            raise ValueError(f"Provider inconnu: {provider_type}")
    
    @staticmethod
    def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Fusion de configurations avec override"""
        merged = base_config.copy()
        merged.update(override_config)
        return merged 