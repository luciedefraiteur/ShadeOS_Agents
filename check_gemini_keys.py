#!/usr/bin/env python3
"""
Check LLM API keys validity using ~/.shadeos_env configuration.

- Loads ~/.shadeos_env via Core.Config.secure_env_manager
- Checks Gemini keys via GeminiProvider.validate_all_keys()
- Checks OpenAI key via OpenAIProvider.test_connection()
- Checks Anthropic key via AnthropicProvider.test_connection()
- Prints a clear report and exits non-zero if none are valid
"""

import asyncio
import sys
from typing import List

try:
    from Core.Config.secure_env_manager import load_project_environment
except Exception as e:
    print(f"[error] Cannot import secure_env_manager: {e}")
    sys.exit(2)

try:
    from Core.Providers.LLMProviders.providers_optional.gemini_provider import GeminiProvider
except Exception:
    GeminiProvider = None
try:
    from Core.Providers.LLMProviders.openai_provider import OpenAIProvider
except Exception:
    OpenAIProvider = None
try:
    from Core.Providers.LLMProviders.providers_optional.anthropic_provider import AnthropicProvider
except Exception:
    AnthropicProvider = None


def print_header(title: str) -> None:
    print("\n" + title)
    print("=" * len(title))


async def main() -> int:
    # Load env from ~/.shadeos_env (and apply to os.environ)
    env_vars = load_project_environment()

    any_valid = False

    # Gemini
    if GeminiProvider is not None:
        gprov = GeminiProvider({"model": env_vars.get("GEMINI_MODEL", "gemini-1.5-pro")})
        if gprov.api_keys:
            print_header("Gemini keys detected")
            for i, key in enumerate(gprov.api_keys):
                preview = f"{key[:6]}...{key[-4:]}" if isinstance(key, str) and len(key) > 10 else "(hidden)"
                print(f"- [{i}] {preview}")
            print_header("Gemini validation")
            gres = await gprov.validate_all_keys()
            for r in gres:
                status = "VALID" if r.get("valid") else "INVALID"
                err = r.get("error")
                etype = r.get("error_type")
                print(f"- [{r['index']}] {r['key_preview']}: {status}" + (f" | {etype}: {err}" if err else ""))
            any_valid = any_valid or any(r.get("valid") for r in gres)
        else:
            print("[warn] No Gemini keys found.")
    else:
        print("[warn] GeminiProvider unavailable.")

    # OpenAI
    if OpenAIProvider is not None:
        print_header("OpenAI validation")
        try:
            oprov = OpenAIProvider({"model": env_vars.get("OPENAI_MODEL", "gpt-4o-mini")})
            ostatus = await oprov.test_connection()
            print(f"- OPENAI_API_KEY: {'VALID' if ostatus.valid else 'INVALID'}" + (f" | {ostatus.error_type}: {ostatus.error}" if ostatus.error else ""))
            any_valid = any_valid or ostatus.valid
        except Exception as e:
            print(f"- OpenAI: error during test: {e}")
    else:
        print("[warn] OpenAIProvider unavailable.")

    # Anthropic
    if AnthropicProvider is not None:
        print_header("Anthropic validation")
        try:
            aprov = AnthropicProvider({"model": env_vars.get("ANTHROPIC_MODEL", "claude-3-haiku-20240307")})
            astatus = await aprov.test_connection()
            print(f"- ANTHROPIC_API_KEY/CLAUDE_API_KEY: {'VALID' if astatus.valid else 'INVALID'}" + (f" | {astatus.error_type}: {astatus.error}" if astatus.error else ""))
            any_valid = any_valid or astatus.valid
        except Exception as e:
            print(f"- Anthropic: error during test: {e}")
    else:
        print("[warn] AnthropicProvider unavailable.")

    print_header("Summary")
    print(f"At least one valid key: {'YES' if any_valid else 'NO'}")
    return 0 if any_valid else 1


if __name__ == "__main__":
    rc = asyncio.run(main())
    sys.exit(rc)
