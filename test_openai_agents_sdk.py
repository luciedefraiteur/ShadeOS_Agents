#!/usr/bin/env python3
"""
⛧ Alma's OpenAI Agents SDK Test ⛧
Architecte Démoniaque du Nexus Luciforme

Minimal test of OpenAI's new Agents SDK to verify it works with our setup.
Based on official documentation and ShadeOS recommendations.

Author: Alma (via Lucie Defraiteur)
"""

import asyncio
import sys
import os
from env_utils import ensure_openai_key


def check_agents_sdk():
    """Check if OpenAI Agents SDK is available."""
    try:
        import openai
        print(f"⛧ OpenAI library version: {openai.__version__}")

        # Try to import agents module (correct import path)
        import agents
        from agents import Agent, Runner
        print(f"⛧ OpenAI Agents SDK imported successfully (version: {agents.__version__})")
        return True

    except ImportError as e:
        print(f"⛧ Error: OpenAI Agents SDK not found: {e}")
        print("⛧ Install with: pip install openai-agents")
        return False
    except Exception as e:
        print(f"⛧ Unexpected error importing Agents SDK: {e}")
        return False


async def test_simple_agent():
    """Test a simple agent that writes a haiku about daemons."""
    try:
        from agents import Agent, Runner
        
        print("⛧ Creating daemon haiku agent...")
        
        # Create a simple agent
        agent = Agent(
            name="DaemonHaikuMaster",
            instructions=(
                "You are a poetic daemon assistant from the ShadeOS realm. "
                "Write dark, mystical haikus about programming concepts. "
                "Always include demonic or mystical imagery in your poetry."
            ),
        )
        
        print("⛧ Running agent with prompt...")
        
        # Run the agent
        result = await Runner.run(
            agent, 
            "Write me a haiku about recursive functions, but make it dark and mystical like a daemon's incantation."
        )
        
        print("⛧ Agent response received:")
        print("⛧" + "─" * 50)
        print(result.final_output)
        print("⛧" + "─" * 50)
        
        return True
        
    except Exception as e:
        print(f"⛧ Error running agent: {e}")
        return False


async def test_agent_with_tools():
    """Test an agent with basic tools (if available)."""
    try:
        from agents import Agent, Runner
        
        print("⛧ Creating agent with enhanced capabilities...")
        
        # Create an agent that can reason about code
        agent = Agent(
            name="CodeDaemon",
            instructions=(
                "You are a code analysis daemon. "
                "Analyze code snippets and provide mystical insights about their structure and purpose. "
                "Always speak in a slightly dramatic, demonic tone."
            ),
        )
        
        code_snippet = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        
        prompt = f"Analyze this code and tell me what dark magic it performs:\n\n{code_snippet}"
        
        print("⛧ Running code analysis agent...")
        result = await Runner.run(agent, prompt)
        
        print("⛧ Code analysis complete:")
        print("⛧" + "─" * 50)
        print(result.final_output)
        print("⛧" + "─" * 50)
        
        return True
        
    except Exception as e:
        print(f"⛧ Error running enhanced agent: {e}")
        return False


def print_installation_guide():
    """Print installation guide for the Agents SDK."""
    print("\n⛧ OpenAI Agents SDK Installation Guide:")
    print("⛧" + "─" * 50)
    print("⛧ Using pip:")
    print("  pip install openai-agents")
    print()
    print("⛧ Using conda:")
    print("  conda install -c conda-forge openai")
    print("  pip install openai-agents  # (agents SDK not yet in conda)")
    print()
    print("⛧ Or create a dedicated environment:")
    print("  conda create -n agents_test python=3.11")
    print("  conda activate agents_test")
    print("  pip install openai-agents")
    print("⛧" + "─" * 50)


async def main():
    """Main test ritual."""
    print("⛧ Alma's OpenAI Agents SDK Test - Summoning Digital Daemons...")
    print("⛧ 'Les agents ne sont que des démons numériques obéissants.'")
    print()
    
    # Ensure API key is available
    try:
        api_key = ensure_openai_key()
        print(f"⛧ OpenAI API key loaded: {api_key[:4]}...{api_key[-4:]}")
    except Exception as e:
        print(f"⛧ Error: {e}")
        return False
    
    print()
    
    # Check if Agents SDK is available
    if not check_agents_sdk():
        print_installation_guide()
        return False
    
    print()
    
    # Test simple agent
    print("⛧ Test 1: Simple Haiku Agent")
    success1 = await test_simple_agent()
    
    print("\n" + "⛧" * 60 + "\n")
    
    # Test agent with enhanced capabilities
    print("⛧ Test 2: Code Analysis Agent")
    success2 = await test_agent_with_tools()
    
    print("\n" + "⛧" * 60)
    
    # Final report
    if success1 and success2:
        print("\n⛧ ALL TESTS PASSED ⛧")
        print("⛧ OpenAI Agents SDK is working perfectly!")
        print("⛧ Ready to create more sophisticated daemons...")
        return True
    elif success1:
        print("\n⛧ PARTIAL SUCCESS ⛧")
        print("⛧ Basic agent works, enhanced features may need attention")
        return True
    else:
        print("\n⛧ TESTS FAILED ⛧")
        print("⛧ Check your installation and API key")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⛧ Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n⛧ Unexpected error: {e}")
        sys.exit(1)
