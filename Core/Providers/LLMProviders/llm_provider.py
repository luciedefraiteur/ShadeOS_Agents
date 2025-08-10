#!/usr/bin/env python3
"""
⛧ LLM Provider Abstrait - Base pour tous les providers LLM ⛧

Provider abstrait avec validation, gestion d'erreurs, estimation de taille
et configuration flexible pour l'Archiviste Daemon.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum


class ProviderType(Enum):
    """Types de providers LLM supportés"""
    OPENAI = "openai"
    LOCAL = "local"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"


class ErrorType(Enum):
    """Types d'erreurs LLM"""
    API_KEY_MISSING = "api_key_missing"
    API_KEY_INVALID = "api_key_invalid"
    TOKENS_EXHAUSTED = "tokens_exhausted"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    MODEL_UNAVAILABLE = "model_unavailable"
    NETWORK_ERROR = "network_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class ProviderStatus:
    """Statut d'un provider LLM"""
    valid: bool
    provider_type: ProviderType
    capabilities: List[str]
    error: Optional[str] = None
    error_type: Optional[ErrorType] = None
    response_time: Optional[float] = None
    model_info: Optional[Dict[str, Any]] = None


@dataclass
class LLMResponse:
    """Réponse d'un LLM"""
    content: str
    provider_type: ProviderType
    model_used: str
    response_time: float
    tokens_used: Optional[int] = None
    prompt_size: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """Résultat de validation d'un provider"""
    valid: bool
    provider_type: ProviderType
    capabilities: List[str]
    test_time: float
    error: Optional[str] = None
    error_type: Optional[ErrorType] = None


class LLMProvider(ABC):
    """Provider abstrait pour différents LLMs"""
    
    def __init__(self, provider_type: ProviderType, config: Dict[str, Any]):
        self.provider_type = provider_type
        self.config = config
        self.timeout = config.get('timeout', 30)
        self.max_tokens = config.get('max_tokens', None)
        self.temperature = config.get('temperature', 0.7)
        self.enable_timeout = config.get('enable_timeout', True)
        self.estimate_prompt_size = config.get('estimate_prompt_size', True)
        
        # Validation de la configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validation de la configuration du provider"""
        if self.timeout <= 0:
            raise ValueError("Timeout doit être positif")
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("max_tokens doit être positif")
        if not 0 <= self.temperature <= 2:
            raise ValueError("Temperature doit être entre 0 et 2")
    
    @abstractmethod
    async def test_connection(self) -> ProviderStatus:
        """Test de connexion et validation du provider"""
        pass
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        """Génération de réponse avec gestion d'erreurs"""
        pass
    
    def estimate_prompt_size(self, prompt: str) -> int:
        """Estimation de la taille du prompt en tokens"""
        if not self.estimate_prompt_size:
            return 0
        
        # Estimation basique : ~4 caractères par token
        estimated_tokens = len(prompt) // 4
        return max(1, estimated_tokens)
    
    def _handle_timeout(self, timeout: float) -> float:
        """Gestion du timeout selon la configuration"""
        if not self.enable_timeout:
            return None
        return timeout or self.timeout
    
    def _create_error_response(self, error: str, error_type: ErrorType, 
                             response_time: float = 0.0) -> LLMResponse:
        """Création d'une réponse d'erreur standardisée"""
        return LLMResponse(
            content=f"ERREUR: {error}",
            provider_type=self.provider_type,
            model_used="error",
            response_time=response_time,
            metadata={"error_type": error_type.value, "error": error}
        )
    
    def _create_success_response(self, content: str, model_used: str,
                               response_time: float, tokens_used: Optional[int] = None,
                               prompt_size: Optional[int] = None) -> LLMResponse:
        """Création d'une réponse de succès standardisée"""
        return LLMResponse(
            content=content,
            provider_type=self.provider_type,
            model_used=model_used,
            tokens_used=tokens_used,
            response_time=response_time,
            prompt_size=prompt_size
        )
    
    async def _execute_with_timeout(self, coro, timeout: Optional[float] = None) -> Any:
        """Exécution avec gestion de timeout"""
        if timeout is None:
            return await coro
        
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Timeout après {timeout} secondes")
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Informations sur le provider"""
        return {
            "provider_type": self.provider_type.value,
            "timeout": self.timeout,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "enable_timeout": self.enable_timeout,
            "estimate_prompt_size": self.estimate_prompt_size
        } 