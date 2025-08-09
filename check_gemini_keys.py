#!/usr/bin/env python3
"""
Check Gemini API keys validity using ~/.shadeos_env configuration.

- Loads ~/.shadeos_env via Core.Config.secure_env_manager
- Uses GeminiProvider.validate_all_keys() to check each key with a lightweight HTTP call
- Prints a clear report with per-key status and a final summary
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
except Exception as e:
    print(f"[error] Cannot import GeminiProvider: {e}\nDid you pull the latest code?")
    sys.exit(2)


def print_header(title: str) -> None:
    print("\n" + title)
    print("=" * len(title))


async def main() -> int:
    # Load env from ~/.shadeos_env (and apply to os.environ)
    env_vars = load_project_environment()

    provider = GeminiProvider({"model": env_vars.get("GEMINI_MODEL", "gemini-1.5-pro")})
    if not provider.api_keys:
        print("[warn] No Gemini keys found in environment. Configure GEMINI_CONFIG/GEMINI_API_KEYS/GEMINI_API_KEY in ~/.shadeos_env.")
        return 1

    print_header("Gemini keys detected")
    for i, key in enumerate(provider.api_keys):
        preview = f"{key[:6]}...{key[-4:]}" if isinstance(key, str) and len(key) > 10 else "(hidden)"
        print(f"- [{i}] {preview}")

    print_header("Validation results")
    results = await provider.validate_all_keys()
    valid_count = 0
    for r in results:
        status = "VALID" if r.get("valid") else "INVALID"
        err = r.get("error")
        etype = r.get("error_type")
        print(f"- [{r['index']}] {r['key_preview']}: {status}" + (f" | {etype}: {err}" if err else ""))
        if r.get("valid"):
            valid_count += 1

    print_header("Summary")
    print(f"Total keys: {len(results)}; valid: {valid_count}; invalid: {len(results) - valid_count}")

    # Exit with 0 if at least one valid key, else 1
    return 0 if valid_count > 0 else 1


if __name__ == "__main__":
    rc = asyncio.run(main())
    sys.exit(rc)
