# README Architecture Proposal (2025-08-10 15:41:13)

## Positioning
- Center the project around TemporalFractalMemoryEngine (TFME) as the memory/consciousness substrate, replacing references to the legacy MemoryEngine.
- Present V10 agents/tools as first-class users of TFME (temporal nodes, fractal links, enrichment systems).
- Emphasize research capability (ML experiments, LLM providers) and dev velocity (tooling, terminal injection).

## Top-level structure
- TemporalFractalMemoryEngine/: core temporal substrate (dimension temporelle, index unifié, couches virtuelles, systèmes d’enrichissement, auto-amélioration)
- Core/: Agents, Providers, Tools/EditingSession, ProcessManager, Config, Partitioner
- Assistants/: UX layers around agents and editing tools
- Reports/: Research notes, diagnostics, and strategies (organized)

## Quickstart (fresh)
- Install deps (Python >=3.10, pytest, optional openai/gemini sdk)
- Configure `~/.shadeos_env` (OPENAI_API_KEY, GEMINI_CONFIG, etc.)
- Start terminal listener for human-in-the-loop E2E: `python shadeos_start_listener.py`
- Run tests quickly: `python run_tests.py --e2e --timeout 20`
- Use V10 CLI: list-tools, read-chunks (with debug), exec-tool

## V10 Specialized Tools
- `read_chunks_until_scope`: chunk reading with scope boundaries (debug mode, mid-scope heuristics, LLM fallback)
- Design goals: robustness, honesty (valid/issues flags), visibility (debug trace)

## Providers
- LLMProviders: OpenAI, Gemini (multi-keys rotation), Local
- DI into V10: auto-detect via feature flags; tests force mock

## Terminal Injection Toolkit
- `shadeos_start_listener.py` -> daemon listener + state file for auto-discovery
- `shadeos_term_exec.py` -> free-form command injection (auto-detect FIFO), logging, prompt restore

## Research & Hardware
- Current hardware: single laptop RTX 2070 mobile; research limited by GPU VRAM and thermals
- Ask: better workstation/GPU to accelerate ML experiments (pretraining/fine-tuning, retrieval, on-device inference)
- Roadmap: incremental ML experiments integrated with TFME’s temporal learning (auto-improvement hooks)

## Action items for README
- Replace MemoryEngine mentions with TemporalFractalMemoryEngine (and link its README)
- Insert Quickstart (CLI/Tests/Terminal Injection)
- Add V10 tools (debug+fallback), Providers DI, and testing philosophy (mock by default, LLM E2E opt-in)
- Add a Research & Hardware section (call for support/collaboration)
