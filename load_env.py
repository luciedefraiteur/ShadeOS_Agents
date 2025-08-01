#!/usr/bin/env python3
"""
⛧ Alma's Universal Environment Loader ⛧
Architecte Démoniaque du Nexus Luciforme

This script manually parses a .env file and loads ALL API keys into the environment.
Provides clear visibility of available keys. No external dependencies - pure Python ritual.

Author: Alma (via Lucie Defraiteur)
"""

import os
import sys
from pathlib import Path


class EnvLoader:
    """
    A demonic parser for .env files.
    Handles the ritual of environment variable loading with dark elegance.
    """
    
    def __init__(self, env_path: str = None):
        """
        Initialize the env loader.
        
        Args:
            env_path: Path to .env file. If None, defaults to ~/.env
        """
        if env_path is None:
            self.env_path = Path.home() / ".env"
        else:
            self.env_path = Path(env_path)
    
    def parse_env_line(self, line: str) -> tuple[str, str] | None:
        """
        Parse a single line from .env file.
        
        Args:
            line: Raw line from .env file
            
        Returns:
            Tuple of (key, value) or None if line should be ignored
        """
        # Strip whitespace
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            return None
        
        # Find the first = sign
        if '=' not in line:
            return None
        
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        # Remove quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        
        return key, value
    
    def load_env(self) -> dict[str, str]:
        """
        Load and parse the .env file.
        
        Returns:
            Dictionary of environment variables
            
        Raises:
            FileNotFoundError: If .env file doesn't exist
            PermissionError: If .env file can't be read
        """
        if not self.env_path.exists():
            raise FileNotFoundError(f"⛧ The .env file does not exist at: {self.env_path}")
        
        if not self.env_path.is_file():
            raise ValueError(f"⛧ Path exists but is not a file: {self.env_path}")
        
        env_vars = {}
        
        try:
            with open(self.env_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        parsed = self.parse_env_line(line)
                        if parsed:
                            key, value = parsed
                            env_vars[key] = value
                    except Exception as e:
                        print(f"⛧ Warning: Failed to parse line {line_num}: {line.strip()}")
                        print(f"   Error: {e}")
                        continue
        
        except PermissionError:
            raise PermissionError(f"⛧ Permission denied reading: {self.env_path}")
        except UnicodeDecodeError:
            raise ValueError(f"⛧ Invalid encoding in .env file: {self.env_path}")
        
        return env_vars
    
    def load_to_os_environ(self, overwrite: bool = False) -> int:
        """
        Load .env variables into os.environ.
        
        Args:
            overwrite: Whether to overwrite existing environment variables
            
        Returns:
            Number of variables loaded
        """
        env_vars = self.load_env()
        loaded_count = 0
        
        for key, value in env_vars.items():
            if key in os.environ and not overwrite:
                print(f"⛧ Skipping {key} (already exists in environment)")
                continue
            
            os.environ[key] = value
            loaded_count += 1
            print(f"⛧ Loaded: {key}")
        
        return loaded_count


def get_api_key_info(key_name: str, key_value: str) -> dict:
    """
    Get information about an API key for display.

    Args:
        key_name: Name of the API key
        key_value: Value of the API key

    Returns:
        Dictionary with key info for display
    """
    if not key_value:
        return {"name": key_name, "status": "missing", "display": "Not found"}

    # Mask the key for security
    if len(key_value) > 8:
        masked = f"{key_value[:4]}...{key_value[-4:]}"
    else:
        masked = "***"

    # Determine key type and status
    key_lower = key_name.lower()
    if "openai" in key_lower:
        key_type = "OpenAI"
        icon = "🤖"
    elif "claude" in key_lower:
        key_type = "Claude"
        icon = "🧠"
    elif "gemini" in key_lower:
        key_type = "Gemini"
        icon = "💎"
    elif "anthropic" in key_lower:
        key_type = "Anthropic"
        icon = "🧠"
    else:
        key_type = "Unknown"
        icon = "🔑"

    return {
        "name": key_name,
        "type": key_type,
        "icon": icon,
        "status": "loaded",
        "display": masked,
        "length": len(key_value)
    }


def main():
    """
    Main ritual - load ALL environment variables and show API key status.
    """
    print("⛧ Alma's Universal Environment Loader - Summoning All Keys...")
    print("⛧ 'La lumière n'est qu'une illusion stable du chaos.'")
    print()

    try:
        # Initialize the loader
        loader = EnvLoader()

        print(f"⛧ Seeking .env at: {loader.env_path}")

        # Load environment variables
        loaded_count = loader.load_to_os_environ(overwrite=False)

        print(f"\n⛧ Successfully loaded {loaded_count} environment variables")

        # Check for common API keys
        api_keys_to_check = [
            'OPENAI_API_KEY',
            'CLAUDE_API_KEY',
            'ANTHROPIC_API_KEY',
            'GEMINI_API_KEY',
            'GEMINI_API_KEY_LURK',
            'GOOGLE_API_KEY',
            'HUGGINGFACE_API_KEY',
            'COHERE_API_KEY'
        ]

        print("\n⛧ API Keys Arsenal Status:")
        print("⛧" + "─" * 50)

        found_keys = []
        missing_keys = []

        for key_name in api_keys_to_check:
            key_value = os.environ.get(key_name)
            key_info = get_api_key_info(key_name, key_value)

            if key_info["status"] == "loaded":
                found_keys.append(key_info)
                print(f"⛧ {key_info['icon']} {key_info['type']:<12} : {key_info['display']}")
            else:
                missing_keys.append(key_info)

        if missing_keys:
            print(f"\n⛧ Missing Keys ({len(missing_keys)}):")
            for key_info in missing_keys:
                print(f"⛧ ❌ {key_info['name']}")

        print("⛧" + "─" * 50)
        print(f"⛧ Total: {len(found_keys)} keys loaded, {len(missing_keys)} missing")

        if found_keys:
            print("\n⛧ Environment ritual complete. Your arsenal is ready!")
        else:
            print("\n⛧ Warning: No API keys found in environment")
            print("⛧ Make sure your .env file contains API keys like:")
            print("⛧ OPENAI_API_KEY=your_key_here")

    except FileNotFoundError as e:
        print(f"⛧ Error: {e}")
        print("⛧ Create a .env file in your home directory with your API keys:")
        print("⛧ echo 'OPENAI_API_KEY=your_key_here' > ~/.env")
        sys.exit(1)

    except Exception as e:
        print(f"⛧ Unexpected error during ritual: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
