#!/usr/bin/env python3
"""
⛧ Gemini Provider (Google Generative AI) ⛧

Provider minimal avec rotation de multiples clés API définies dans ~/.shadeos_env.
Cette implémentation est un placeholder et n'appelle pas l'API réelle pour l'instant.
"""

from __future__ import annotations

import os
import time
import json
from typing import Dict, Any, List, Optional

from ..llm_provider import LLMProvider, ProviderStatus, LLMResponse, ProviderType, ErrorType


class GeminiProvider(LLMProvider):
    def __init__(self, config: Dict[str, Any]):
        cfg = {
            'model': config.get('model', 'gemini-1.5-pro'),
            'timeout': config.get('timeout', 30),
            'temperature': config.get('temperature', 0.7),
        }
        super().__init__(ProviderType.GEMINI, cfg)

        self.api_keys: List[str] = []
        self._load_keys_from_environment()
        self._key_index: int = 0

    def _load_keys_from_environment(self) -> None:
        raw_cfg = os.getenv('GEMINI_CONFIG')
        if raw_cfg:
            try:
                parsed = json.loads(raw_cfg)
                keys = parsed.get('api_keys')
                if isinstance(keys, list):
                    for k in keys:
                        if isinstance(k, str) and k and k not in self.api_keys:
                            self.api_keys.append(k)
            except Exception:
                pass

        raw_list = os.getenv('GEMINI_API_KEYS')
        if raw_list and not self.api_keys:
            try:
                parsed = json.loads(raw_list)
                if isinstance(parsed, list):
                    for k in parsed:
                        if isinstance(k, str) and k and k not in self.api_keys:
                            self.api_keys.append(k)
            except Exception:
                pass

        if not self.api_keys:
            single = os.getenv('GEMINI_API_KEY')
            if single:
                self.api_keys.append(single)

    def _get_active_key(self) -> Optional[str]:
        if not self.api_keys:
            return None
        return self.api_keys[self._key_index % len(self.api_keys)]

    def _rotate_key(self) -> None:
        if self.api_keys:
            self._key_index = (self._key_index + 1) % len(self.api_keys)

    async def test_connection(self) -> ProviderStatus:
        has_key = bool(self._get_active_key())
        return ProviderStatus(
            valid=has_key,
            provider_type=self.provider_type,
            capabilities=["text_generation", "chat_completion"],
            error=None if has_key else "Clé(s) GEMINI manquante(s)",
            error_type=None if has_key else ErrorType.API_KEY_MISSING,
            response_time=0.0,
            model_info={"model": self.config.get('model', '')}
        )

    async def generate_response(self, prompt: str, **kwargs) -> LLMResponse:
        start = time.time()
        api_key = self._get_active_key()
        if not api_key:
            return self._create_error_response("Aucune clé GEMINI disponible", ErrorType.API_KEY_MISSING, time.time() - start)

        content = f"[Gemini placeholder] {prompt[:200]}"
        return self._create_success_response(
            content=content,
            model_used=self.config.get('model', 'gemini'),
            response_time=time.time() - start,
            tokens_used=None,
            prompt_size=len(prompt)
        )
