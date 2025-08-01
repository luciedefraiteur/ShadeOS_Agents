#!/usr/bin/env python3
"""
⛧ Alma's Environment Utilities ⛧
Architecte Démoniaque du Nexus Luciforme

Utility functions for loading environment variables from .env files.
Designed for import into other ShadeOS_Agents scripts.

Author: Alma (via Lucie Defraiteur)
"""

import os
from pathlib import Path


def load_api_key(key_name: str, env_path: str = None, silent: bool = False) -> str | None:
    """
    Load a specific API key from .env file.

    Args:
        key_name: Name of the API key to load (e.g., 'OPENAI_API_KEY')
        env_path: Path to .env file. If None, defaults to ~/.env
        silent: If True, suppress all output

    Returns:
        API key if found, None otherwise
    """
    try:
        if env_path is None:
            env_path = Path.home() / ".env"
        else:
            env_path = Path(env_path)

        if not env_path.exists():
            if not silent:
                print(f"⛧ Warning: .env file not found at {env_path}")
            return None

        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith(f'{key_name}='):
                    key = line.split('=', 1)[1].strip()
                    # Remove quotes if present
                    if key.startswith('"') and key.endswith('"'):
                        key = key[1:-1]
                    elif key.startswith("'") and key.endswith("'"):
                        key = key[1:-1]

                    # Set in environment
                    os.environ[key_name] = key

                    if not silent:
                        masked_key = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***"
                        print(f"⛧ {key_name} loaded: {masked_key}")

                    return key

        if not silent:
            print(f"⛧ Warning: {key_name} not found in .env file")
        return None

    except Exception as e:
        if not silent:
            print(f"⛧ Error loading {key_name}: {e}")
        return None


def load_openai_key(env_path: str = None, silent: bool = False) -> str | None:
    """
    Quick ritual to load OpenAI API key from .env file.
    Wrapper around load_api_key for backward compatibility.

    Args:
        env_path: Path to .env file. If None, defaults to ~/.env
        silent: If True, suppress all output

    Returns:
        OpenAI API key if found, None otherwise
    """
    return load_api_key('OPENAI_API_KEY', env_path, silent)


def load_all_api_keys(env_path: str = None, silent: bool = False) -> dict[str, str]:
    """
    Load all API keys from .env file.

    Args:
        env_path: Path to .env file. If None, defaults to ~/.env
        silent: If True, suppress all output

    Returns:
        Dictionary of loaded API keys
    """
    api_keys = [
        'OPENAI_API_KEY',
        'CLAUDE_API_KEY',
        'ANTHROPIC_API_KEY',
        'GEMINI_API_KEY',
        'GEMINI_API_KEY_LURK',
        'GOOGLE_API_KEY',
        'HUGGINGFACE_API_KEY',
        'COHERE_API_KEY'
    ]

    loaded_keys = {}
    for key_name in api_keys:
        key_value = load_api_key(key_name, env_path, silent=True)
        if key_value:
            loaded_keys[key_name] = key_value

    if not silent:
        print(f"⛧ Loaded {len(loaded_keys)} API keys")
        for key_name in loaded_keys:
            masked = f"{loaded_keys[key_name][:4]}...{loaded_keys[key_name][-4:]}"
            print(f"⛧ {key_name}: {masked}")

    return loaded_keys


def ensure_openai_key() -> str:
    """
    Ensure OpenAI API key is available in environment.
    
    Returns:
        OpenAI API key
        
    Raises:
        RuntimeError: If key cannot be loaded
    """
    # First check if already in environment
    key = os.environ.get('OPENAI_API_KEY')
    if key:
        return key
    
    # Try to load from .env
    key = load_openai_key(silent=True)
    if key:
        return key
    
    # Last resort - check common environment variable names
    for var_name in ['OPENAI_API_KEY', 'OPENAI_KEY', 'OPENAI_TOKEN']:
        key = os.environ.get(var_name)
        if key:
            os.environ['OPENAI_API_KEY'] = key  # Normalize to OPENAI_API_KEY
            return key
    
    raise RuntimeError(
        "⛧ OpenAI API key not found. Please:\n"
        "   1. Create ~/.env with OPENAI_API_KEY=your_key\n"
        "   2. Or set OPENAI_API_KEY environment variable\n"
        "   3. Or run load_openai_env.py first"
    )


# Convenience function for immediate loading
def quick_load_env():
    """
    Quick one-liner to load all API keys into environment.
    Perfect for script headers.
    """
    return load_all_api_keys(silent=True)


if __name__ == "__main__":
    # If run directly, load all keys
    print("⛧ Alma's Environment Utils - Quick Load All Keys")
    keys = load_all_api_keys()
    if keys:
        print(f"⛧ {len(keys)} API keys successfully loaded into environment")
    else:
        print("⛧ No API keys found")
