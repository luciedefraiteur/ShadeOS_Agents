#!/usr/bin/env python3
import os
import sys
import asyncio
from typing import Any, Dict, List

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from Core.Agents.V10.specialized_tools import V10SpecializedToolsRegistry  # noqa: E402

FIX = os.path.join('Core', 'Agents', 'V10', 'tests', 'fixtures', 'advanced', 'big_fixture.py')

def load_markers(path: str) -> Dict[str, int]:
    markers: Dict[str, int] = {}
    with open(path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f, start=1):
            if '# MARK:' in line:
                try:
                    tag = line.split('# MARK:')[1].strip()
                    # keep only first token before spaces
                    tag = tag.split()[0]
                    markers[tag] = idx
                except Exception:
                    pass
    return markers

def build_queries(markers: Dict[str, int]) -> List[Dict[str, Any]]:
    q: List[Dict[str, Any]] = []
    def add(name: str, tag: str, offset: int, note: str):
        if tag in markers:
            q.append({'name': name, 'line': markers[tag] + offset, 'note': note})
    # Alpha.decorated
    add('Alpha.decorated — decorator line', 'DECORATORS_DECOR1', 0, 'Dans les décorateurs (empilés).')
    add('Alpha.decorated — header line', 'DECORATORS_HEADER', 1, 'Sur le header def.')
    add('Alpha.decorated — body inside', 'DECORATORS_BODY', 1, 'Dans le corps (après docstring).')
    # Alpha.multi_sig
    add('Alpha.multi_sig — header start', 'MULTISIG_HEADER', 1, 'Début signature multi-lignes.')
    add('Alpha.multi_sig — mid signature', 'MULTISIG_MID', 0, 'Milieu signature (entre args).')
    add('Alpha.multi_sig — body line', 'MULTISIG_BODY', 1, 'Dans le corps (après docstring).')
    # Alpha.Inner
    add('Alpha.Inner.inner_func — header', 'INNER_HEADER', 1, 'Header fonction imbriquée.')
    add('Alpha.Inner.inner_func — body', 'INNER_BODY', 1, 'Dans le corps après nested.')
    # beta
    add('beta — header', 'BETA_HEADER', 1, 'Début fonction de contrôle dense.')
    add('beta — mid body', 'BETA_BODY', -2, 'Dans le else/try (avant marque).')
    add('beta — end body', 'BETA_BODY', 1, 'Juste avant return y.')
    # gamma
    add('gamma — header', 'GAMMA_HEADER', 1, 'Header avec continuations ensuite.')
    add('gamma — body', 'GAMMA_BODY', 1, 'Après continuations, dans le corps.')
    # delta
    add('delta — header', 'DELTA_HEADER', 1, 'Header async + match/case.')
    add('delta — body', 'DELTA_BODY', 1, 'Dans la branche case _.')
    # bad_string
    add('bad_string — header', 'BAD_STRING_HEADER', 1, 'Fonction avec chaîne non terminée.')
    add('bad_string — body', 'BAD_STRING_BODY', 1, 'Dans la zone du body problématique.')
    # near_eof
    add('near_eof — header', 'EOF_FUNC_HEADER', 1, 'Fonction proche EOF sans dédent.')
    return q


def fmt_range(tag: str, pair):
    if not pair:
        return f"{tag}: -"
    a, b = pair
    if a is None and b is None:
        return f"{tag}: -"
    return f"{tag}: {a if a else '-'}..{b if b else '-'}"


async def run_case(idx: int, total: int, line: int, name: str, note: str) -> int:
    reg = V10SpecializedToolsRegistry()
    res = await reg.execute_tool('read_chunks_until_scope', {
        'file_path': FIX,
        'start_line': line,
        'include_analysis': False,
        'debug': True,
    })
    abs_path = os.path.abspath(FIX)

    print(f"\n===== Test {idx}/{total} — {name} =====")
    print(f"Note: {note}")
    print(f"File: {abs_path}")
    print(f"Query start_line: {line}")

    if not res.success:
        print(f"Result: ERROR -> {res.error}")
        return 1

    b: Dict[str, Any] = res.data['scope_boundaries']
    meta: Dict[str, Any] = b.get('meta', {}) or {}
    issues = b.get('issues', []) or []
    ast_notes = (res.metadata or {}).get('ast_notes', []) or []

    print(f"Result: OK")
    print(f"Scope: {b['start_line']}..{b['end_line']}  | valid={b.get('valid', True)}  | end_reason={b.get('end_reason')}  | type={b.get('scope_type')}")

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
        print(fmt_range('Meta.header.signature', [sig.get('start'), sig.get('end')] if sig else None))
        body = meta.get('body') or {}
        bspan = (body.get('span') or {})
        print(fmt_range('Meta.body', [bspan.get('start'), bspan.get('end')] if bspan else None))
        bdoc = (body.get('docstring') or {})
        bdocspan = bdoc.get('span') if bdoc else None
        print(fmt_range('Meta.body.docstring', [bdocspan.get('start'), bdocspan.get('end')] if isinstance(bdocspan, dict) else None))
        bcode = (body.get('code') or {})
        bcodespan = bcode.get('span') if bcode else None
        print(fmt_range('Meta.body.code', [bcodespan.get('start'), bcodespan.get('end')] if isinstance(bcodespan, dict) else None))
    else:
        # Legacy
        ds = meta.get('decorators_start'); de = meta.get('decorators_end')
        hl = meta.get('header_line')
        hs = meta.get('header_signature')
        bd = meta.get('body_docstring')
        bex = meta.get('body_executable')
        bs = meta.get('body_start'); be = meta.get('body_end')
        if ds and de:
            print(f"Meta.decorators: {ds}..{de} | anchors: {abs_path}:{ds} {abs_path}:{de}")
        else:
            print("Meta.decorators: -")
        print(f"Meta.header_line: {hl if hl else '-'}", (f"| anchor: {abs_path}:{hl}" if hl else ''))
        print(fmt_range('Meta.header_signature', hs))
        print(fmt_range('Meta.body_docstring', bd))
        print(fmt_range('Meta.body_executable', bex))
        print(f"Meta.body: {bs if bs else '-'}..{be if be else '-'}")

    print(f"Issues: {issues if issues else '[]'}")
    print(f"AST notes: {ast_notes if ast_notes else '[]'}")

    # Compact preview
    try:
        with open(FIX, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        s, e = b['start_line'], b['end_line']
        for i in range(max(0, s-1), min(len(lines), e)):
            print(f"{i+1:6d}: {lines[i].rstrip()}")
    except Exception as e:
        print(f"[WARN] Could not read file preview: {e}")

    return 0


async def main() -> int:
    print("\n/!\\ TESTS COMMENCENT ICI /!\\")
    markers = load_markers(FIX)
    QUERIES = build_queries(markers)
    total = len(QUERIES)
    failures = 0
    for idx, q in enumerate(QUERIES, start=1):
        failures += await run_case(idx, total, q['line'], q['name'], q.get('note',''))
    print("\\n/!\\ TESTS TERMINÉS /!\\")
    print(f"SUMMARY: total={total} failures={failures} status={'ALL GREEN' if failures==0 else 'SOME FAILURES'}")
    return 0 if failures == 0 else 1


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
