#!/usr/bin/env python3
"""
⛧ Anthropic (Claude) Provider ⛧

Provider minimal pour vérifier la validité des clés via HTTP /v1/models.
"""
from __future__ import annotations

import os
import time
import asyncio
from typing import Dict, Any, Optional
from urllib import request, error as urlerror

from ..llm_provider import LLMProvider, ProviderStatus, LLMResponse, ProviderType, ErrorType


class AnthropicProvider(LLMProvider):
    def __init__(self, config: Dict[str, Any]):
        cfg = {
            'model': config.get('model', 'claude-3-opus-20240229'),
            'timeout': config.get('timeout', 30),
            'temperature': config.get('temperature', 0.7),
        }
        super().__init__(ProviderType.ANTHROPIC, cfg)
        self.api_key: Optional[str] = config.get('api_key') or os.getenv('ANTHROPIC_API_KEY') or os.getenv('CLAUDE_API_KEY')

    async def test_connection(self) -> ProviderStatus:
        start = time.time()
        if not self.api_key:
            return ProviderStatus(
                valid=False,
                provider_type=self.provider_type,
                capabilities=[],
                error="Clé ANTHROPIC manquante",
                error_type=ErrorType.API_KEY_MISSING,
                response_time=0.0,
                model_info={"model": self.config.get('model', '')}
            )
        ok, err, etype = await self._http_check_models(self.api_key)
        return ProviderStatus(
            valid=ok,
            provider_type=self.provider_type,
            capabilities=["text_generation", "chat_completion"] if ok else [],
            error=None if ok else err,
            error_type=etype,
            response_time=time.time() - start,
            model_info={"model": self.config.get('model', '')}
        )

    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        # Placeholder: non implémenté ici
        return self._create_error_response("Non implémenté", ErrorType.UNKNOWN_ERROR, 0.0)

    async def _http_check_models(self, api_key: str) -> tuple[bool, Optional[str], Optional[ErrorType]]:
        url = "https://api.anthropic.com/v1/models"
        def _do_get() -> tuple[int, str]:
            try:
                req = request.Request(url)
                req.add_header('x-api-key', api_key)
                req.add_header('anthropic-version', '2023-06-01')
                with request.urlopen(req, timeout=self.timeout) as resp:
                    data = resp.read().decode('utf-8', errors='ignore')
                    return resp.getcode(), data
            except urlerror.HTTPError as e:
                try:
                    data = e.read().decode('utf-8', errors='ignore')
                except Exception:
                    data = str(e)
                return e.code, data
            except Exception as e:
                return 0, str(e)
        code, body = await asyncio.to_thread(_do_get)
        if code == 200:
            return True, None, None
        if code in (401, 403):
            return False, "Clé Anthropic invalide ou accès refusé", ErrorType.API_KEY_INVALID
        if code == 429:
            return False, "Rate limit/Quota Anthropic atteint", ErrorType.RATE_LIMIT
        if code == 0:
            return False, f"Erreur réseau: {body}", ErrorType.NETWORK_ERROR
        return False, f"Erreur HTTP {code}: {body[:200]}", ErrorType.UNKNOWN_ERROR
