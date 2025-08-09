#!/usr/bin/env python3
"""
Pytest bootstrap for ShadeOS_Agents
- Ensures project root is on sys.path for absolute imports like `from Core...`
- Loads ~/.shadeos_env via secure_env_manager so providers/env are available in tests
"""
import sys
import os

# Prepend project root to sys.path for absolute imports
repo_root = os.getcwd()
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Load project environment (safe-noop if not available)
try:
    from Core.Config.secure_env_manager import load_project_environment
    load_project_environment()
except Exception:
    pass
