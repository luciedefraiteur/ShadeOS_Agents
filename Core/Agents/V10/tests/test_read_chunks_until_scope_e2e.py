#!/usr/bin/env python3
"""
E2E tests for V10ReadChunksUntilScopeTool via V10SpecializedToolsRegistry.

These tests avoid hitting real LLMs by forcing LLM_MODE=mock and using include_analysis flags.
"""
import os
import tempfile
import asyncio
import pytest

from Core.Agents.V10.specialized_tools import V10SpecializedToolsRegistry


@pytest.fixture(autouse=True)
def mock_llm_mode(monkeypatch):
    # Force mock mode to avoid real provider initialization and network
    monkeypatch.setenv("LLM_MODE", "mock")
    # Make sure strict mode doesn't break tests
    monkeypatch.delenv("LLM_FALLBACK_MOCK", raising=False)
    monkeypatch.delenv("SHADEOS_DEBUG_MOCK", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)


@pytest.mark.asyncio
async def test_read_chunks_basic_no_analysis():
    registry = V10SpecializedToolsRegistry()

    content = """
# header

def hello(x):
    y = x + 1
    return y

class Sample:
    def m(self):
        return 42
""".lstrip()

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(content)
        path = f.name
    try:
        params = {
            "file_path": path,
            "start_line": 3,  # points to def hello
            "scope_type": "function",
            "max_chunks": 10,
            "include_analysis": False,
        }
        res = await registry.execute_tool("read_chunks_until_scope", params)
        assert res.success is True
        assert res.data is not None
        assert "scope_content" in res.data
        assert "def hello" in res.data["scope_content"]
        assert res.data["scope_boundaries"]["start_line"] <= 3
        assert res.data["scope_boundaries"]["end_line"] >= res.data["scope_boundaries"]["start_line"]
    finally:
        os.unlink(path)


@pytest.mark.asyncio
async def test_read_chunks_with_mock_analysis():
    registry = V10SpecializedToolsRegistry()

    content = """
class A:
    def foo(self):
        return 'ok'
""".lstrip()

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(content)
        path = f.name
    try:
        params = {
            "file_path": path,
            "start_line": 1,  # class A
            "scope_type": "class",
            "max_chunks": 10,
            "include_analysis": True,  # uses internal mock llm
        }
        res = await registry.execute_tool("read_chunks_until_scope", params)
        assert res.success is True
        assert res.data is not None
        assert res.data.get("analysis") is not None
        assert res.data["scope_boundaries"]["start_line"] == 1
    finally:
        os.unlink(path)


@pytest.mark.asyncio
async def test_read_chunks_missing_file():
    registry = V10SpecializedToolsRegistry()
    res = await registry.execute_tool("read_chunks_until_scope", {
        "file_path": "/path/that/does/not/exist.py",
        "start_line": 1,
        "include_analysis": False,
    })
    assert res.success is False
    assert res.error is not None
