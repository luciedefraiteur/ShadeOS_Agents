#!/usr/bin/env python3
import os
import sys
import argparse
import asyncio
from typing import Any, Dict, Optional

# Ensure project root on sys.path if invoked directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from Core.Agents.V10.specialized_tools import V10SpecializedToolsRegistry  # noqa: E402


def format_range(label: str, start: Optional[int], end: Optional[int]) -> str:
    if start is None and end is None:
        return f"{label}: -"
    if start is None:
        return f"{label}: -..{end}"
    if end is None:
        return f"{label}: {start}..-"
    return f"{label}: {start}..{end}"


def read_file_lines(path: str) -> Optional[list[str]]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.readlines()
    except Exception:
        return None


def preview_lines(lines: list[str], start_line: int, end_line: int, context: int = 0) -> str:
    start_idx = max(0, start_line - 1 - context)
    end_idx = min(len(lines), end_line + context)
    out = []
    for i in range(start_idx, end_idx):
        # 1-based numbering left-padded for alignment
        out.append(f"{i+1:6d}: {lines[i].rstrip()}\n")
    return ''.join(out)


async def run_once(file_path: str, start_line: int, show_meta: bool, show_issues: bool, print_content: bool, context: int) -> int:
    reg = V10SpecializedToolsRegistry()
    res = await reg.execute_tool('read_chunks_until_scope', {
        'file_path': file_path,
        'start_line': start_line,
        'include_analysis': False,
        'debug': True,
    })
    abs_path = os.path.abspath(file_path)
    print(f"===== DEBUG SCOPE RUNNER =====")
    print(f"File: {abs_path}")
    print(f"Query start_line: {start_line}")
    if not res.success:
        print(f"Result: ERROR -> {res.error}")
        return 1

    b: Dict[str, Any] = res.data['scope_boundaries']
    meta: Dict[str, Any] = b.get('meta', {}) or {}
    issues = b.get('issues', []) or []
    ast_notes = (res.metadata or {}).get('ast_notes', []) or []

    print(f"Result: OK")
    print(f"Scope: {b['start_line']}..{b['end_line']}  | valid={b.get('valid', True)}  | end_reason={b.get('end_reason')}  | type={b.get('scope_type')}")

    if show_meta:
        # Prefer meta v2 schema if present
        mv = meta.get('meta_version')
        if mv == 2:
            entity = meta.get('entity') or {}
            if entity:
                print(f"Meta.entity: kind={entity.get('kind')} name={entity.get('name')}")
            dec = (meta.get('decorators') or {}).get('span') or {}
            if dec.get('start') and dec.get('end'):
                print(format_range("Meta.decorators", dec.get('start'), dec.get('end')), f"| anchors: {abs_path}:{dec.get('start')} {abs_path}:{dec.get('end')}")
            else:
                print("Meta.decorators: -")
            hdr = meta.get('header') or {}
            hl = hdr.get('line')
            print(f"Meta.header.line: {hl if hl else '-'}", (f"| anchor: {abs_path}:{hl}" if hl else ''))
            sig = (hdr.get('signature') or {}).get('span') or {}
            print(format_range("Meta.header.signature", sig.get('start'), sig.get('end')))
            body = meta.get('body') or {}
            bspan = (body.get('span') or {})
            print(format_range("Meta.body", bspan.get('start'), bspan.get('end')))
            bdoc = (body.get('docstring') or {})
            bdocspan = bdoc.get('span') if bdoc else None
            if isinstance(bdocspan, dict):
                print(format_range("Meta.body.docstring", bdocspan.get('start'), bdocspan.get('end')))
            else:
                print("Meta.body.docstring: -")
            bcode = (body.get('code') or {})
            bcodespan = bcode.get('span') if bcode else None
            if isinstance(bcodespan, dict):
                print(format_range("Meta.body.code", bcodespan.get('start'), bcodespan.get('end')))
            else:
                print("Meta.body.code: -")
        else:
            # Legacy fields fallback
            ds = meta.get('decorators_start')
            de = meta.get('decorators_end')
            hl = meta.get('header_line')
            bs = meta.get('body_start')
            be = meta.get('body_end')
            if ds and de:
                print(format_range("Meta.decorators", ds, de), f"| anchors: {abs_path}:{ds} {abs_path}:{de}")
            else:
                print(format_range("Meta.decorators", ds, de))
            print(f"Meta.header_line: {hl if hl else '-'}", (f"| anchor: {abs_path}:{hl}" if hl else ''))
            if bs and be:
                print(format_range("Meta.body", bs, be), f"| anchors: {abs_path}:{bs} {abs_path}:{be}")
            else:
                print(format_range("Meta.body", bs, be))

    if show_issues:
        print(f"Issues: {issues if issues else '[]'}")
        print(f"AST notes: {ast_notes if ast_notes else '[]'}")

    if print_content:
        lines = read_file_lines(file_path)
        if lines is not None:
            deco_s = meta.get('decorators_start')
            deco_e = meta.get('decorators_end')
            body_s = meta.get('body_start') or b['start_line']
            body_e = meta.get('body_end') or b['end_line']
            # preview decorators if present
            if deco_s and deco_e:
                print("--- Decorators Preview ---")
                print(preview_lines(lines, deco_s, deco_e, context=context))
            # preview body/content
            print("--- Scope Preview ---")
            print(preview_lines(lines, b['start_line'], b['end_line'], context=context))
        else:
            print("[WARN] Could not read file for preview")

    print()
    return 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Debug runner for Python scope detection")
    p.add_argument('--file', dest='file', required=True, help='File path to test')
    p.add_argument('--line', dest='line', required=True, type=int, help='Start line to query')
    p.add_argument('--show-scope-meta', dest='show_meta', action='store_true', help='Print scope meta (decorators/header/body)')
    p.add_argument('--show-issues', dest='show_issues', action='store_true', help='Print issues and AST notes')
    p.add_argument('--print-content', dest='print_content', action='store_true', help='Print scope and decorators content preview')
    p.add_argument('--context', dest='context', type=int, default=0, help='Extra context lines for previews')
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not os.path.exists(args.file):
        print(f"[ERROR] File not found: {args.file}")
        return 2
    return asyncio.run(run_once(args.file, args.line, args.show_meta, args.show_issues, args.print_content, args.context))


if __name__ == '__main__':
    raise SystemExit(main())
