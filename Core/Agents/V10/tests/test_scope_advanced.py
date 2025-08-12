#!/usr/bin/env python3
import os
import pytest
from Core.Agents.V10.specialized_tools import V10SpecializedToolsRegistry

ADV = os.path.join(os.path.dirname(__file__), 'fixtures', 'advanced')

@pytest.mark.asyncio
async def test_decorators_stacked_method():
    path = os.path.join(ADV, 'decorators_stacked.py')
    reg = V10SpecializedToolsRegistry()
    res = await reg.execute_tool('read_chunks_until_scope', {
        'file_path': path,
        'start_line': 6,  # inside method body
        'include_analysis': False,
        'debug': True,
    })
    assert res.success is True
    b = res.data['scope_boundaries']
    assert b['start_line'] == 4  # first decorator
    assert b['end_line'] == 8

@pytest.mark.asyncio
async def test_multiline_signature():
    path = os.path.join(ADV, 'multiline_signature.py')
    reg = V10SpecializedToolsRegistry()
    res = await reg.execute_tool('read_chunks_until_scope', {
        'file_path': path,
        'start_line': 3,  # mid signature
        'include_analysis': False,
        'debug': True,
    })
    assert res.success is True
    b = res.data['scope_boundaries']
    assert b['start_line'] == 3
    assert b['end_line'] == 12

@pytest.mark.asyncio
async def test_docstrings_edges():
    path = os.path.join(ADV, 'docstrings_edges.py')
    reg = V10SpecializedToolsRegistry()
    res = await reg.execute_tool('read_chunks_until_scope', {
        'file_path': path,
        'start_line': 2,
        'include_analysis': False,
        'debug': True,
    })
    assert res.success is True
    b = res.data['scope_boundaries']
    assert b['start_line'] == 3
    assert b['end_line'] == 9

@pytest.mark.asyncio
async def test_control_dense():
    path = os.path.join(ADV, 'control_dense.py')
    reg = V10SpecializedToolsRegistry()
    res = await reg.execute_tool('read_chunks_until_scope', {
        'file_path': path,
        'start_line': 3,
        'include_analysis': False,
        'debug': True,
    })
    assert res.success is True
    b = res.data['scope_boundaries']
    assert b['start_line'] == 3
    assert b['end_line'] == 15

@pytest.mark.asyncio
async def test_async_match():
    path = os.path.join(ADV, 'async_match.py')
    reg = V10SpecializedToolsRegistry()
    res = await reg.execute_tool('read_chunks_until_scope', {
        'file_path': path,
        'start_line': 3,
        'include_analysis': False,
        'debug': True,
    })
    assert res.success is True
    b = res.data['scope_boundaries']
    assert b['start_line'] == 3
    assert b['end_line'] == 8

@pytest.mark.asyncio
async def test_continuations():
    path = os.path.join(ADV, 'continuations.py')
    reg = V10SpecializedToolsRegistry()
    res = await reg.execute_tool('read_chunks_until_scope', {
        'file_path': path,
        'start_line': 3,
        'include_analysis': False,
        'debug': True,
    })
    assert res.success is True
    b = res.data['scope_boundaries']
    assert b['start_line'] == 3
    assert b['end_line'] == 8

@pytest.mark.asyncio
async def test_unterminated_string_flag():
    path = os.path.join(ADV, 'unterminated_string.py')
    reg = V10SpecializedToolsRegistry()
    res = await reg.execute_tool('read_chunks_until_scope', {
        'file_path': path,
        'start_line': 3,
        'include_analysis': False,
        'debug': True,
    })
    assert res.success is True
    b = res.data['scope_boundaries']
    assert b['start_line'] == 3
    # tokenizer should flag unterminated string
    assert 'unterminated_string' in b.get('issues', []) or 'ast_invalid_snippet' in res.metadata.get('ast_notes', [])
