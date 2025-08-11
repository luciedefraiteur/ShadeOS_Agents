#!/usr/bin/env python3
import asyncio
import os
import pytest
from Core.Agents.V10.specialized_tools import V10SpecializedToolsRegistry

BASE = os.path.join(os.path.dirname(__file__), 'fixtures')

@pytest.mark.asyncio
async def test_mid_scope_nested_function_start_shift_and_end():
    path = os.path.join(BASE, 'nested_heavy.py')
    # Start mid-scope inside inner for body (line ~7)
    params = {"file_path": path, "start_line": 8, "include_analysis": False, "debug": True}
    reg = V10SpecializedToolsRegistry()
    res = await reg.execute_tool("read_chunks_until_scope", params)
    assert res.success is True
    b = res.data["scope_boundaries"]
    # Expect shift to inner def header and end including final return
    assert b['start_line'] == 5
    assert b['end_line'] == 12
    assert b.get('valid') is True

@pytest.mark.asyncio
async def test_mid_scope_decorated_docstring_method():
    path = os.path.join(BASE, 'decorated_docstring.py')
    # Start mid-scope inside method body (line ~10)
    params = {"file_path": path, "start_line": 10, "include_analysis": False, "debug": True}
    reg = V10SpecializedToolsRegistry()
    res = await reg.execute_tool("read_chunks_until_scope", params)
    assert res.success is True
    b = res.data["scope_boundaries"]
    # Expect start to include decorator + def, end at method dedent including final return
    assert b['start_line'] == 4  # @staticmethod
    assert b['end_line'] == 12

@pytest.mark.asyncio
async def test_mid_scope_control_heavy_no_premature_return_cut():
    path = os.path.join(BASE, 'control_heavy.py')
    # Start inside elif block (line ~6)
    params = {"file_path": path, "start_line": 6, "include_analysis": False, "debug": True}
    reg = V10SpecializedToolsRegistry()
    res = await reg.execute_tool("read_chunks_until_scope", params)
    assert res.success is True
    b = res.data["scope_boundaries"]
    # Should capture the whole function body including final return
    assert b['start_line'] == 3
    assert b['end_line'] == 15

@pytest.mark.asyncio
async def test_unterminated_scope_eof_flagged_invalid():
    path = os.path.join(BASE, 'unterminated.py')
    params = {"file_path": path, "start_line": 3, "include_analysis": False, "debug": True}
    reg = V10SpecializedToolsRegistry()
    res = await reg.execute_tool("read_chunks_until_scope", params)
    assert res.success is True
    b = res.data["scope_boundaries"]
    assert b['start_line'] == 3
    # No dedent before EOF; accept partial range and flag an issue
    assert 'unterminated_scope_eof' in b.get('issues', [])
