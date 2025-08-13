from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Minimal import path, adjust if running standalone
try:
    from Core.Providers.LLMProviders.provider_factory import ProviderFactory
    from Core.Config.secure_env_manager import load_project_environment
except Exception:
    from ...Providers.LLMProviders.provider_factory import ProviderFactory  # type: ignore
    from ...Config.secure_env_manager import load_project_environment  # type: ignore


def _read_tail_lines(path: Path, max_lines: int = 500) -> List[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return lines[-max_lines:]


def plan_next_targets(
    summaries_path: Path,
    handles_path: Path,
    provider: str = "gemini",
    model: str = "gemini-1.5-pro",
    max_items: int = 12,
    save_prompt_to: Optional[Path] = None,
    save_raw_to: Optional[Path] = None,
) -> Dict[str, Any]:
    """Use an LLM provider to propose next targets (GH boards, DDG queries, non-GH targets).

    Returns a dict with greenhouse_boards, ddg_queries, non_gh_targets, rationale, confidence.
    """
    # Load env (ensures GEMINI/OPENAI keys from ~/.shadeos_env are available)
    try:
        load_project_environment()
    except Exception:
        pass

    # Prepare compact context
    summaries_tail = _read_tail_lines(summaries_path, 200)
    handles_tail = _read_tail_lines(handles_path, 200)

    prompt = (
        "SYSTEM: Tu planifies des bursts pour découvrir des offres IA. \n"
        "Lis les résumés et proposes des cibles concises, actionnables, diverses (GH/Ashby/Workday/SmartRecruiters…).\n"
        f"CONTEXT_SUMMARIES:\n{chr(10).join(summaries_tail)}\n"
        f"CONTEXT_HANDLES:\n{chr(10).join(handles_tail)}\n"
        "TASK: Retourne un JSON strict avec les clés: greenhouse_boards (liste), ddg_queries (liste), "
        "non_gh_targets (liste d'objets {provider, handle}), rationale (string courte), confidence (0..1). "
        f"Max {max_items} cibles au total, pas de doublons, favorise la diversité des providers.\n"
        "FORMAT UNIQUEMENT JSON, PAS DE TEXTE AUTOUR.\n"
    )

    # Optional: persist the exact prompt for debugging/observability
    try:
        if save_prompt_to:
            save_prompt_to.parent.mkdir(parents=True, exist_ok=True)
            save_prompt_to.write_text(prompt, encoding="utf-8")
    except Exception:
        pass

    # Build provider
    prov = ProviderFactory.create_provider(provider, model=model)

    # Call the provider (sync wrapper; TFME providers are async, but often expose sync helpers)
    import anyio

    async def _call() -> str:
        try:
            resp = await prov.generate_response(prompt)
            # openai providers return an object sometimes; normalize to string content
            if hasattr(resp, "content"):
                return getattr(resp, "content")
            return str(resp)
        except Exception as e:
            return json.dumps({
                "greenhouse_boards": [],
                "ddg_queries": [],
                "non_gh_targets": [],
                "rationale": f"error: {e}",
                "confidence": 0.0,
            })

    content = anyio.run(_call)

    # Persist raw content for observability/debugging
    try:
        if save_raw_to:
            save_raw_to.parent.mkdir(parents=True, exist_ok=True)
            save_raw_to.write_text(str(content), encoding="utf-8")
    except Exception:
        pass

    try:
        data = json.loads(content)
        # Basic shape check
        data.setdefault("greenhouse_boards", [])
        data.setdefault("ddg_queries", [])
        data.setdefault("non_gh_targets", [])
        data.setdefault("rationale", "")
        data.setdefault("confidence", 0.0)
        # Trim lengths
        data["greenhouse_boards"] = list(dict.fromkeys(list(map(str, data["greenhouse_boards"])) ))[:max_items]
        data["ddg_queries"] = list(dict.fromkeys(list(map(str, data["ddg_queries"])) ))[:max_items]
        if isinstance(data["non_gh_targets"], list):
            data["non_gh_targets"] = data["non_gh_targets"][:max_items]
        return data
    except Exception as e:
        return {
            "greenhouse_boards": [],
            "ddg_queries": [],
            "non_gh_targets": [],
            "rationale": f"parse_error: {e}",
            "confidence": 0.0,
            "raw_path": str(save_raw_to) if save_raw_to else None,
        }
