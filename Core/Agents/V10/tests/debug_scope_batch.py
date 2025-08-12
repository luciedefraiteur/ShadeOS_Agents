#!/usr/bin/env python3
import os
import sys
import asyncio
from typing import Any, Dict, Optional, List

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from Core.Agents.V10.specialized_tools import V10SpecializedToolsRegistry  # noqa: E402

ADV = os.path.join('Core', 'Agents', 'V10', 'tests', 'fixtures', 'advanced')

CASES: List[Dict[str, Any]] = [
    {
        'name': 'Decorators stacked (method)',
        'file': os.path.join(ADV, 'decorators_stacked.py'),
        'line': 6,
        'note': 'Méthode avec décorateurs empilés; vérifie start aux décorateurs et meta.header/body.',
    },
    {
        'name': 'Multi-line signature',
        'file': os.path.join(ADV, 'multiline_signature.py'),
        'line': 3,
        'note': 'Signature sur plusieurs lignes; fin de header au ":"; fin au dédent.',
    },
    {
        'name': 'Docstrings edge cases',
        'file': os.path.join(ADV, 'docstrings_edges.py'),
        'line': 2,
        'note': 'Docstring triple-quoted avec guillemets/échappements; corps reconnu après docstring.',
    },
    {
        'name': 'Dense control flow',
        'file': os.path.join(ADV, 'control_dense.py'),
        'line': 3,
        'note': 'if/elif/else + try/except/finally; fin uniquement au dédent.',
    },
    {
        'name': 'Async + match/case',
        'file': os.path.join(ADV, 'async_match.py'),
        'line': 3,
        'note': 'async def avec match/case; comportement d’indentation inchangé.',
    },
    {
        'name': 'Line continuations',
        'file': os.path.join(ADV, 'continuations.py'),
        'line': 3,
        'note': 'Parenthèses multi-lignes; n’influence pas la fin (dédent).',
    },
    {
        'name': 'Unterminated string (flag)',
        'file': os.path.join(ADV, 'unterminated_string.py'),
        'line': 3,
        'note': 'Chaîne non terminée; tokenizer doit signaler l’issue.',
    },
]


def preview_lines(lines: List[str], start_line: int, end_line: int) -> str:
    start_idx = max(0, start_line - 1)
    end_idx = min(len(lines), end_line)
    out = []
    for i in range(start_idx, end_idx):
        out.append(f"{i+1:6d}: {lines[i].rstrip()}\n")
    return ''.join(out)


async def run_case(idx: int, total: int, case: Dict[str, Any]) -> int:
    reg = V10SpecializedToolsRegistry()
    file_path = case['file']
    start_line = int(case['line'])
    note = case.get('note', '')
    abs_path = os.path.abspath(file_path)

    res = await reg.execute_tool('read_chunks_until_scope', {
        'file_path': file_path,
        'start_line': start_line,
        'include_analysis': False,
        'debug': True,
    })

    print(f"\n===== Test {idx}/{total} — {case.get('name','Unnamed')} =====")
    if note:
        print(f"Note: {note}")
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
    # Meta block
    mv = meta.get('meta_version')
    if mv == 2:
        entity = meta.get('entity') or {}
        if entity:
            print(f"Meta.entity: kind={entity.get('kind')} name={entity.get('name')}")
        dec = (meta.get('decorators') or {}).get('span') or {}
        if dec.get('start') and dec.get('end'):
            print(f"Meta.decorators: {dec.get('start')}..{dec.get('end')} | anchors: {abs_path}:{dec.get('start')} {abs_path}:{dec.get('end')}")
        else:
            print("Meta.decorators: -")
        hdr = meta.get('header') or {}
        hl = hdr.get('line')
        print(f"Meta.header.line: {hl if hl else '-'}", (f"| anchor: {abs_path}:{hl}" if hl else ''))
        sig = (hdr.get('signature') or {}).get('span') or {}
        print(f"Meta.header.signature: {(sig.get('start') if sig else '-') }..{(sig.get('end') if sig else '-')}")
        body = meta.get('body') or {}
        bspan = (body.get('span') or {})
        print(f"Meta.body: {(bspan.get('start') if bspan else '-') }..{(bspan.get('end') if bspan else '-')}")
        bdoc = (body.get('docstring') or {})
        bdocspan = bdoc.get('span') if bdoc else None
        if isinstance(bdocspan, dict):
            print(f"Meta.body.docstring: {bdocspan.get('start')}..{bdocspan.get('end')}")
        else:
            print("Meta.body.docstring: -")
        bcode = (body.get('code') or {})
        bcodespan = bcode.get('span') if bcode else None
        if isinstance(bcodespan, dict):
            print(f"Meta.body.code: {bcodespan.get('start')}..{bcodespan.get('end')}")
        else:
            print("Meta.body.code: -")
    else:
        # Legacy fallback
        ds = meta.get('decorators_start')
        de = meta.get('decorators_end')
        hl = meta.get('header_line')
        bs = meta.get('body_start')
        be = meta.get('body_end')
        if ds and de:
            print(f"Meta.decorators: {ds}..{de} | anchors: {abs_path}:{ds} {abs_path}:{de}")
        else:
            print("Meta.decorators: -")
        print(f"Meta.header_line: {hl if hl else '-'}", (f"| anchor: {abs_path}:{hl}" if hl else ''))
        if bs and be:
            print(f"Meta.body: {bs}..{be} | anchors: {abs_path}:{bs} {abs_path}:{be}")
        else:
            print("Meta.body: -")

    print(f"Issues: {issues if issues else '[]'}")
    print(f"AST notes: {ast_notes if ast_notes else '[]'}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print("--- Scope Preview ---")
        print(preview_lines(lines, b['start_line'], b['end_line']))
    except Exception as e:
        print(f"[WARN] Could not read file for preview: {e}")

    return 0


async def main() -> int:
    total = len(CASES)
    print("\n/!\\ TESTS COMMENCENT ICI /!\\")
    failures = 0
    for i, case in enumerate(CASES, start=1):
        failures += await run_case(i, total, case)
    print("\\n/!\\ TESTS TERMINÉS /!\\")
    print(f"SUMMARY: total={total} failures={failures} status={'ALL GREEN' if failures==0 else 'SOME FAILURES'}")
    return 0 if failures == 0 else 1


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
