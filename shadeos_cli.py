#!/usr/bin/env python3
"""
ShadeOS CLI — Minimal terminal interface for V10 specialized tools

Commands:
  - list-tools
  - exec-tool --tool <name> --params-json '{...}'
  - read-chunks --file <path> [--start-line N] [--scope-type auto|function|class|block]
               [--max-chunks N] [--include-analysis/--no-analysis]

Flags:
  - --llm-mode auto|gemini|openai|local_http|local_subprocess|mock
  - --llm-fallback-mock (allows mock fallback in strict mode)

Examples:
  python shadeos_cli.py list-tools
  python shadeos_cli.py exec-tool --tool read_lines --params-json '{"file_path":"/etc/hosts","start_line":1,"end_line":5}'
  python shadeos_cli.py read-chunks --file ./Core/Agents/V10/specialized_tools.py --start-line 715 --scope-type auto --no-analysis
"""

from __future__ import annotations

import os
import sys
import json
import argparse
import asyncio
from typing import Any, Dict

# Ensure project env is loaded
try:
    from Core.Config.secure_env_manager import load_project_environment
except Exception as e:
    print(f"[error] Failed to import secure_env_manager: {e}")
    sys.exit(2)

try:
    from Core.Agents.V10.specialized_tools import V10SpecializedToolsRegistry
except Exception as e:
    print(f"[error] Failed to import V10SpecializedToolsRegistry: {e}")
    sys.exit(2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ShadeOS CLI for specialized tools")

    parser.add_argument(
        "--llm-mode", dest="llm_mode", default=None,
        help="LLM mode: auto|gemini|openai|local_http|local_subprocess|mock"
    )
    parser.add_argument(
        "--llm-fallback-mock", dest="llm_fallback_mock", action="store_true",
        help="Allow mock fallback when real provider is unavailable"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-tools", help="List available specialized tools")

    p_exec = sub.add_parser("exec-tool", help="Execute a tool by name with JSON parameters")
    p_exec.add_argument("--tool", required=True, help="Tool name")
    p_exec.add_argument("--params-json", required=True, help="JSON string with parameters for the tool")

    p_read = sub.add_parser("read-chunks", help="Run read_chunks_until_scope tool with convenience flags")
    p_read.add_argument("--file", dest="file_path", required=True)
    p_read.add_argument("--start-line", type=int, default=1)
    p_read.add_argument("--max-chunks", type=int, default=10)
    p_read.add_argument(
        "--scope-type", choices=["auto", "function", "class", "block"], default="auto"
    )
    inc = p_read.add_mutually_exclusive_group()
    inc.add_argument("--include-analysis", dest="include_analysis", action="store_true")
    inc.add_argument("--no-analysis", dest="include_analysis", action="store_false")
    p_read.set_defaults(include_analysis=False)

    return parser.parse_args()


async def run_list_tools(registry: V10SpecializedToolsRegistry) -> int:
    tools = registry.list_tools()
    print(json.dumps({"tools": tools}, indent=2, ensure_ascii=False))
    return 0


async def run_exec_tool(registry: V10SpecializedToolsRegistry, tool: str, params_json: str) -> int:
    try:
        params: Dict[str, Any] = json.loads(params_json)
    except Exception as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}, ensure_ascii=False))
        return 2
    result = await registry.execute_tool(tool, params)
    out = {
        "success": result.success,
        "tool_name": result.tool_name,
        "data": result.data,
        "error": result.error,
        "execution_time": result.execution_time,
        "metadata": result.metadata,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if result.success else 1


async def run_read_chunks(registry: V10SpecializedToolsRegistry, ns: argparse.Namespace) -> int:
    params = {
        "file_path": ns.file_path,
        "start_line": ns.start_line,
        "max_chunks": ns.max_chunks,
        "scope_type": ns.scope_type,
        "include_analysis": ns.include_analysis,
    }
    result = await registry.execute_tool("read_chunks_until_scope", params)
    out = {
        "success": result.success,
        "tool_name": result.tool_name,
        "data": result.data,
        "error": result.error,
        "execution_time": result.execution_time,
        "metadata": result.metadata,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if result.success else 1


def main() -> int:
    # Load environment (.shadeos_env)
    try:
        load_project_environment()
    except Exception as e:
        print(f"[warn] Could not load project environment: {e}")

    ns = parse_args()

    # Apply LLM flags to environment
    if ns.llm_mode:
        os.environ["LLM_MODE"] = ns.llm_mode
    if ns.llm_fallback_mock:
        os.environ["LLM_FALLBACK_MOCK"] = "1"

    # Create registry
    registry = V10SpecializedToolsRegistry()

    # Dispatch
    if ns.command == "list-tools":
        return asyncio.run(run_list_tools(registry))
    if ns.command == "exec-tool":
        return asyncio.run(run_exec_tool(registry, ns.tool, ns.params_json))
    if ns.command == "read-chunks":
        return asyncio.run(run_read_chunks(registry, ns))

    print("Unknown command")
    return 2


if __name__ == "__main__":
    sys.exit(main())
