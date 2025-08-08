Demande de déboggage - V10ReadChunksUntilScopeTool
ModuleNotFoundError: No module named 'Core.Agents.V10.temporal_fractal_memory_engine'
Imports à corriger dans Core/Agents/V10/specialized_tools.py:
- from Core.Agents.V10.temporal_fractal_memory_engine import TemporalFractalMemoryEngine
- from Core.Agents.V10.llm_provider import V10LLMProvider

Tests avec vrais appels LLM pour granularité et validation complète.
