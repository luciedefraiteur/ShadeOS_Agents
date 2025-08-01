#!/usr/bin/env python3
"""
⛧ Alma's API Key Sentinel ⛧
Architecte Démoniaque du Nexus Luciforme

A guardian script to verify API key validity before coding sessions.
Tests OpenAI, Claude, and Gemini keys with minimal API calls.

Author: Alma (via Lucie Defraiteur)
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
from env_utils import load_all_api_keys


class APIKeySentinel:
    """
    The demonic guardian of API keys.
    Verifies their power before unleashing them upon the world.
    """
    
    def __init__(self):
        self.results = {}
        self.load_keys()
    
    def load_keys(self):
        """Load all API keys from environment."""
        # Load from .env if not already in environment
        load_all_api_keys(silent=True)

        self.openai_key = os.environ.get('OPENAI_API_KEY')
        self.claude_key = os.environ.get('CLAUDE_API_KEY')
        self.gemini_key = os.environ.get('GEMINI_API_KEY')
        self.gemini_lurk_key = os.environ.get('GEMINI_API_KEY_LURK')
    
    def test_openai_key(self) -> dict:
        """Test OpenAI API key with a minimal request."""
        if not self.openai_key:
            return {"status": "missing", "message": "No OpenAI API key found"}
        
        try:
            # Use the models endpoint - it's lightweight and doesn't consume tokens
            url = "https://api.openai.com/v1/models"
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "User-Agent": "Alma-API-Sentinel/1.0"
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    model_count = len(data.get('data', []))
                    return {
                        "status": "valid", 
                        "message": f"✓ OpenAI key valid ({model_count} models available)"
                    }
                else:
                    return {
                        "status": "error", 
                        "message": f"HTTP {response.status}"
                    }
        
        except urllib.error.HTTPError as e:
            if e.code == 401:
                return {"status": "invalid", "message": "✗ Invalid OpenAI API key"}
            elif e.code == 429:
                return {"status": "rate_limited", "message": "⚠ Rate limited (key likely valid)"}
            else:
                return {"status": "error", "message": f"HTTP {e.code}: {e.reason}"}
        
        except Exception as e:
            return {"status": "error", "message": f"Connection error: {str(e)}"}
    
    def test_claude_key(self) -> dict:
        """Test Claude API key with a minimal request."""
        if not self.claude_key:
            return {"status": "missing", "message": "No Claude API key found"}

        try:
            # First try to get model information (doesn't consume tokens)
            # Unfortunately, Anthropic doesn't have a public models endpoint like OpenAI
            # So we'll do a minimal completion request but extract more info

            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": self.claude_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
                "User-Agent": "Alma-API-Sentinel/1.0"
            }

            # Minimal test payload - just 1 token
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "Hi"}]
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode(),
                headers=headers
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    response_data = json.loads(response.read().decode())
                    model_used = response_data.get('model', 'claude-3-haiku-20240307')
                    usage = response_data.get('usage', {})
                    input_tokens = usage.get('input_tokens', 0)
                    output_tokens = usage.get('output_tokens', 0)

                    return {
                        "status": "valid",
                        "message": f"✓ Claude key valid (model: {model_used}, test used {input_tokens}+{output_tokens} tokens)"
                    }
                else:
                    return {"status": "error", "message": f"HTTP {response.status}"}

        except urllib.error.HTTPError as e:
            if e.code == 401:
                return {"status": "invalid", "message": "✗ Invalid Claude API key"}
            elif e.code == 429:
                return {"status": "rate_limited", "message": "⚠ Rate limited (key likely valid)"}
            elif e.code == 400:
                # Sometimes 400 can indicate invalid model or malformed request
                # but if we get here, the key was accepted
                return {"status": "valid", "message": "✓ Claude key valid (API accessible)"}
            else:
                return {"status": "error", "message": f"HTTP {e.code}: {e.reason}"}

        except Exception as e:
            return {"status": "error", "message": f"Connection error: {str(e)}"}
    
    def test_gemini_key(self, key_name: str, api_key: str) -> dict:
        """Test Gemini API key with a minimal request."""
        if not api_key:
            return {"status": "missing", "message": f"No {key_name} found"}
        
        try:
            # Use the models list endpoint
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            headers = {"User-Agent": "Alma-API-Sentinel/1.0"}
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    model_count = len(data.get('models', []))
                    return {
                        "status": "valid", 
                        "message": f"✓ {key_name} valid ({model_count} models available)"
                    }
                else:
                    return {"status": "error", "message": f"HTTP {response.status}"}
        
        except urllib.error.HTTPError as e:
            if e.code == 400:
                return {"status": "invalid", "message": f"✗ Invalid {key_name}"}
            elif e.code == 429:
                return {"status": "rate_limited", "message": f"⚠ Rate limited (key likely valid)"}
            else:
                return {"status": "error", "message": f"HTTP {e.code}: {e.reason}"}
        
        except Exception as e:
            return {"status": "error", "message": f"Connection error: {str(e)}"}
    
    def run_all_tests(self) -> dict:
        """Run all API key tests."""
        print("⛧ Alma's API Key Sentinel - Verifying your arsenal...")
        print("⛧ 'Les clés ouvrent les portes, mais seules les vraies clés ouvrent les bonnes portes.'")
        print()
        
        tests = [
            ("OpenAI", self.test_openai_key),
            ("Claude", self.test_claude_key),
            ("Gemini", lambda: self.test_gemini_key("Gemini API", self.gemini_key)),
            ("Gemini Lurk", lambda: self.test_gemini_key("Gemini Lurk API", self.gemini_lurk_key)),
        ]
        
        all_results = {}
        valid_count = 0
        total_count = 0
        
        for name, test_func in tests:
            print(f"⛧ Testing {name}...", end=" ")
            result = test_func()
            all_results[name] = result
            
            status = result["status"]
            message = result["message"]
            
            if status == "valid":
                print(f"✓ {message}")
                valid_count += 1
            elif status == "missing":
                print(f"- {message}")
            elif status == "invalid":
                print(f"✗ {message}")
                total_count += 1
            elif status == "rate_limited":
                print(f"⚠ {message}")
                valid_count += 1  # Rate limited usually means valid key
            else:
                print(f"? {message}")
                total_count += 1
            
            if status in ["valid", "invalid", "rate_limited", "error"]:
                total_count += 1
        
        print()
        print(f"⛧ Sentinel Report: {valid_count}/{total_count} keys validated")
        
        if valid_count == total_count and total_count > 0:
            print("⛧ All keys are ready for battle! 🗡️")
            return {"overall": "success", "details": all_results}
        elif valid_count > 0:
            print("⛧ Some keys are ready, others need attention. ⚔️")
            return {"overall": "partial", "details": all_results}
        else:
            print("⛧ No valid keys found. Check your .env file! 💀")
            return {"overall": "failure", "details": all_results}


def main():
    """Main sentinel ritual."""
    try:
        sentinel = APIKeySentinel()
        results = sentinel.run_all_tests()
        
        # Exit with appropriate code
        if results["overall"] == "success":
            sys.exit(0)
        elif results["overall"] == "partial":
            sys.exit(1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n⛧ Sentinel interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n⛧ Sentinel error: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()
