#!/usr/bin/env python3
"""
⛧ Feature Flags for Core ⛧
Alma's centralized feature toggles for runtime switching between mocks and real integrations.

Environment variables:
- LLM_MODE: "auto" | "gemini" | "openai" | "local_http" | "local_subprocess" | "mock" (default: auto)
- TEMPORAL_ENGINE: "on" | "off" (default: "off")
- MCP_ENABLED: "1" | "0" | "true" | "false" (default: "0")
"""
from __future__ import annotations
import os

def _get_env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    value_lower = value.strip().lower()
    return value_lower in {"1", "true", "yes", "on"}

def get_llm_mode() -> str:
    """Returns the configured LLM mode.

    auto detection order:
    - If GEMINI_CONFIG/GEMINI_API_KEYS/GEMINI_API_KEY present → gemini
    - Else if OPENAI_API_KEY present → openai
    - Else if OLLAMA_HOST present → local_http
    - Else → mock
    """
    mode = os.getenv("LLM_MODE", "auto").strip().lower()
    if mode and mode != "auto":
        return mode
    # auto-detect
    if os.getenv("GEMINI_CONFIG") or os.getenv("GEMINI_API_KEYS") or os.getenv("GEMINI_API_KEY"):
        return "gemini"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("OLLAMA_HOST"):
        return "local_http"
    return "mock"

def is_temporal_engine_enabled() -> bool:
    """Whether to enable TemporalFractalMemoryEngine (filesystem backend by default)."""
    value = os.getenv("TEMPORAL_ENGINE", "off").strip().lower()
    return value in {"1", "true", "yes", "on"}

def is_mcp_enabled() -> bool:
    """Whether MCP integration should be attempted at runtime."""
    return _get_env_bool("MCP_ENABLED", default=False)
