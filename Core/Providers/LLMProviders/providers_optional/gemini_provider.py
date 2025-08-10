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
import asyncio
from typing import Dict, Any, List, Optional
from urllib import request, error as urlerror

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
        start = time.time()
        api_key = self._get_active_key()
        if not api_key:
            return ProviderStatus(
                valid=False,
                provider_type=self.provider_type,
                capabilities=[],
                error="Clé(s) GEMINI manquante(s)",
                error_type=ErrorType.API_KEY_MISSING,
                response_time=0.0,
                model_info={"model": self.config.get('model', '')}
            )

        ok, err, etype = await self._http_check_models(api_key)
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
        start = time.time()
        prompt_size = len(prompt)
        tries = 0
        max_tries = max(1, len(self.api_keys))
        last_err: Optional[str] = None
        last_err_type: Optional[ErrorType] = None

        while tries < max_tries:
            api_key = self._get_active_key()
            if not api_key:
                return self._create_error_response("Aucune clé GEMINI disponible", ErrorType.API_KEY_MISSING, time.time() - start)

            ok, text, etype, err = await self._post_generate_content(api_key, prompt, **kwargs)
            if ok:
                return self._create_success_response(
                    content=text or "",
                    model_used=self.config.get('model', 'gemini'),
                    response_time=time.time() - start,
                    tokens_used=None,
                    prompt_size=prompt_size
                )

            # En cas de quota/rate-limit/invalid, on essaie la clé suivante
            last_err, last_err_type = err, etype
            if etype in (ErrorType.RATE_LIMIT, ErrorType.TOKENS_EXHAUSTED, ErrorType.API_KEY_INVALID):
                self._rotate_key()
                tries += 1
                # Backoff simple pour 429
                if etype == ErrorType.RATE_LIMIT:
                    await asyncio.sleep(min(1.0 * tries, 3.0))
                continue
            else:
                break

        return self._create_error_response(last_err or "Echec génération Gemini", last_err_type or ErrorType.UNKNOWN_ERROR, time.time() - start)

    async def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Alias de compatibilité pour certains appels V10."""
        return await self.generate_response(prompt, **kwargs)

    async def validate_all_keys(self) -> List[Dict[str, Any]]:
        """Valide toutes les clés connues et retourne leur statut."""
        results: List[Dict[str, Any]] = []
        for idx, key in enumerate(self.api_keys):
            ok, err, etype = await self._http_check_models(key)
            results.append({
                "index": idx,
                "valid": ok,
                "error": err,
                "error_type": etype.value if etype else None,
                "key_preview": f"{key[:6]}...{key[-4:]}" if isinstance(key, str) and len(key) > 10 else "hidden"
            })
        return results

    async def _http_check_models(self, api_key: str) -> tuple[bool, Optional[str], Optional[ErrorType]]:
        """Appel HTTP simple (GET models) pour vérifier la validité de la clé."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        def _do_get() -> tuple[int, str]:
            try:
                with request.urlopen(url, timeout=self.timeout) as resp:
                    data = resp.read().decode("utf-8", errors="ignore")
                    return resp.getcode(), data
            except urlerror.HTTPError as e:
                try:
                    data = e.read().decode("utf-8", errors="ignore")
                except Exception:
                    data = str(e)
                return e.code, data
            except Exception as e:
                return 0, str(e)

        code, body = await asyncio.to_thread(_do_get)
        if code == 200:
            return True, None, None
        if code in (401, 403):
            return False, "Clé GEMINI invalide ou accès refusé", ErrorType.API_KEY_INVALID
        if code == 429:
            return False, "Rate limit/Quota atteint pour cette clé", ErrorType.RATE_LIMIT
        if code == 0:
            return False, f"Erreur réseau: {body}", ErrorType.NETWORK_ERROR
        return False, f"Erreur HTTP {code}: {body[:200]}", ErrorType.UNKNOWN_ERROR

    async def _post_generate_content(self, api_key: str, prompt: str, **kwargs) -> tuple[bool, Optional[str], Optional[ErrorType], Optional[str]]:
        """Appel REST generateContent; retourne (ok, text, error_type, error_message)."""
        model = kwargs.get('model', self.config.get('model', 'gemini-1.5-pro'))
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload: Dict[str, Any] = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt}]
            }]
        }
        gen_cfg: Dict[str, Any] = {}
        temperature = kwargs.get('temperature', self.temperature)
        if temperature is not None:
            gen_cfg["temperature"] = float(temperature)
        max_tokens = kwargs.get('max_tokens', self.max_tokens)
        if max_tokens is not None:
            gen_cfg["maxOutputTokens"] = int(max_tokens)
        if gen_cfg:
            payload["generationConfig"] = gen_cfg

        data = json.dumps(payload).encode('utf-8')
        req = request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')

        def _do_post() -> tuple[int, str]:
            try:
                with request.urlopen(req, timeout=self.timeout) as resp:
                    body = resp.read().decode('utf-8', errors='ignore')
                    return resp.getcode(), body
            except urlerror.HTTPError as e:
                try:
                    body = e.read().decode('utf-8', errors='ignore')
                except Exception:
                    body = str(e)
                return e.code, body
            except Exception as e:
                return 0, str(e)

        code, body = await asyncio.to_thread(_do_post)
        if code == 200:
            try:
                parsed = json.loads(body)
                # candidates[0].content.parts[0].text
                candidates = parsed.get('candidates') or []
                if candidates:
                    content = candidates[0].get('content') or {}
                    parts = content.get('parts') or []
                    if parts:
                        text = parts[0].get('text') or ""
                        return True, text, None, None
                return True, "", None, None
            except Exception:
                return True, body, None, None
        if code in (401, 403):
            return False, None, ErrorType.API_KEY_INVALID, f"HTTP {code}: {body[:200]}"
        if code == 429:
            return False, None, ErrorType.RATE_LIMIT, f"HTTP 429: {body[:200]}"
        if code == 0:
            return False, None, ErrorType.NETWORK_ERROR, body
        return False, None, ErrorType.UNKNOWN_ERROR, f"HTTP {code}: {body[:200]}"
