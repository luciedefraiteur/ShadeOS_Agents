#!/usr/bin/env python3
"""
⛧ Test Archivist Interface with Direct OpenAI ⛧
Architecte Démoniaque du Nexus Luciforme

Tests the Archivist interface using direct OpenAI calls instead of Agents SDK.
Simulates daemon interactions with the memory consciousness.

Author: Alma (via Lucie Defraiteur)
"""

import os
import sys
import json
import asyncio
from typing import List, Dict

# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

from Core.Archivist.archivist_interface import (
    ArchivistInterface, 
    ContextualRequest, 
    ExperienceContribution,
    archivist
)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⛧ Warning: OpenAI not available. Install with: pip install openai")


class DaemonSimulator:
    """
    Simulates daemon interactions with the Archivist using direct OpenAI calls.
    """
    
    def __init__(self, daemon_id: str, api_key: str = None):
        self.daemon_id = daemon_id
        self.archivist = archivist
        
        if OPENAI_AVAILABLE and api_key:
            openai.api_key = api_key
            self.openai_client = openai.OpenAI(api_key=api_key)
        else:
            self.openai_client = None
    
    async def simulate_daemon_interaction(self, user_query: str, use_openai: bool = False) -> Dict:
        """
        Simulate a daemon processing a user query with Archivist support.
        """
        print(f"⛧ {self.daemon_id.upper()} Daemon Processing Query:")
        print(f"  Query: {user_query}")
        
        # Step 1: Request contextual intelligence from Archivist
        context_request = ContextualRequest(
            requesting_daemon=self.daemon_id,
            query=user_query,
            conversation_context=[],  # Would be populated in real scenario
            required_strata=["cognitive", "metaphysical"],  # Focus on higher-level insights
            max_memories=5
        )
        
        print(f"⛧ Requesting contextual intelligence from Archivist...")
        context_response = self.archivist.get_contextual_intelligence(context_request)
        
        print(f"  ✓ Found {len(context_response.relevant_memories)} relevant memories")
        print(f"  ✓ Confidence score: {context_response.confidence_score:.2f}")
        print(f"  ✓ Reasoning: {context_response.reasoning}")
        
        # Step 2: Process with daemon's specialized perspective
        daemon_response = await self._process_with_daemon_logic(user_query, context_response, use_openai)
        
        # Step 3: Contribute experience back to Archivist
        if daemon_response.get("success"):
            contribution = ExperienceContribution(
                contributing_daemon=self.daemon_id,
                domain=self._extract_domain(user_query),
                experience_type="insight",
                content=daemon_response["reasoning"],
                summary=f"{self.daemon_id} processed: {user_query[:50]}...",
                keywords=user_query.lower().split()[:5],
                lessons_learned=daemon_response.get("lessons", []),
                strata="cognitive"
            )
            
            print(f"⛧ Contributing experience to collective memory...")
            success = self.archivist.contribute_experience(contribution)
            print(f"  ✓ Contribution {'successful' if success else 'failed'}")
        
        return {
            "daemon_id": self.daemon_id,
            "query": user_query,
            "context_used": len(context_response.relevant_memories),
            "response": daemon_response,
            "archivist_confidence": context_response.confidence_score
        }
    
    async def _process_with_daemon_logic(self, query: str, context: any, use_openai: bool) -> Dict:
        """
        Process the query using daemon-specific logic.
        """
        if use_openai and self.openai_client:
            return await self._process_with_openai(query, context)
        else:
            return self._process_with_simulated_logic(query, context)
    
    async def _process_with_openai(self, query: str, context: any) -> Dict:
        """
        Process using actual OpenAI API.
        """
        try:
            # Build context-aware prompt
            daemon_personas = {
                "alma": "You are Alma, a mystical system architect daemon. You speak dramatically and focus on elegant design patterns and architectural principles. You love using mystical metaphors.",
                "forge": "You are Forge, a pragmatic implementation daemon. You focus on concrete solutions, code quality, and practical implementation details. You speak efficiently and directly.",
                "scout": "You are Scout, a curious research daemon. You focus on gathering information, analyzing trends, and synthesizing knowledge. You speak analytically and thoroughly."
            }
            
            persona = daemon_personas.get(self.daemon_id, "You are a helpful AI assistant.")
            
            # Include context from Archivist
            context_info = ""
            if context.relevant_memories:
                context_info = f"\nRelevant memories from collective consciousness:\n"
                for memory in context.relevant_memories[:3]:
                    context_info += f"- {memory.get('summary', 'No summary')}\n"
            
            prompt = f"""{persona}

{context_info}

User query: {query}

Provide a response that reflects your daemon personality and incorporates the contextual memories if relevant."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "reasoning": f"Processed with OpenAI using {len(context.relevant_memories)} contextual memories",
                "lessons": [f"OpenAI integration successful for {self.daemon_id}"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": f"OpenAI processing failed: {e}",
                "reasoning": "OpenAI API error",
                "lessons": ["Need to handle OpenAI errors gracefully"]
            }
    
    def _process_with_simulated_logic(self, query: str, context: any) -> Dict:
        """
        Process using simulated daemon logic (fallback when OpenAI not available).
        """
        daemon_responses = {
            "alma": f"⛧ *Alma's mystical analysis* ⛧\nThe query '{query}' resonates with architectural patterns in our collective memory. I sense {len(context.relevant_memories)} relevant memories that guide us toward elegant solutions. The cosmic forces suggest a transcendent approach that bridges the somatic and metaphysical realms.",
            
            "forge": f"🔨 Forge's practical assessment:\nQuery: '{query}'\nFound {len(context.relevant_memories)} relevant implementation patterns in memory. Based on collective experience, I recommend focusing on concrete, testable solutions. Let's build something that works reliably.",
            
            "scout": f"🔍 Scout's research synthesis:\nAnalyzing query: '{query}'\nCross-referenced with {len(context.relevant_memories)} memories from our knowledge base. Confidence level: {context.confidence_score:.2f}. Recommend gathering additional context from external sources to complement our collective understanding."
        }
        
        response = daemon_responses.get(self.daemon_id, f"Processing '{query}' with {len(context.relevant_memories)} contextual memories.")
        
        return {
            "success": True,
            "response": response,
            "reasoning": f"Simulated {self.daemon_id} logic with contextual memory integration",
            "lessons": [f"Simulated processing works for {self.daemon_id}"]
        }
    
    def _extract_domain(self, query: str) -> str:
        """Extract domain from query for categorization."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["code", "implement", "function", "class"]):
            return "implementation"
        elif any(word in query_lower for word in ["design", "architecture", "pattern", "structure"]):
            return "architecture"
        elif any(word in query_lower for word in ["research", "find", "analyze", "study"]):
            return "research"
        else:
            return "general"


async def test_archivist_interface():
    """Test the Archivist interface with simulated daemons."""
    print("⛧ Testing Archivist Interface with Daemon Simulation")
    print("⛧" + "═" * 60)
    
    # Get OpenAI API key if available
    api_key = os.getenv("OPENAI_API_KEY")
    use_openai = api_key is not None and OPENAI_AVAILABLE
    
    if use_openai:
        print("⛧ Using OpenAI API for realistic daemon responses")
    else:
        print("⛧ Using simulated daemon logic (OpenAI not available)")
    
    print()
    
    # Create daemon simulators
    daemons = {
        "alma": DaemonSimulator("alma", api_key),
        "forge": DaemonSimulator("forge", api_key),
        "scout": DaemonSimulator("scout", api_key)
    }
    
    # Test queries
    test_queries = [
        "How should I implement a parser without using regex?",
        "What are the best practices for error handling in Python?",
        "How can I optimize database queries for better performance?"
    ]
    
    results = []
    
    for i, query in enumerate(test_queries):
        print(f"⛧ Test {i+1}: {query}")
        print("⛧" + "─" * 50)
        
        # Test with different daemons
        for daemon_id, daemon in daemons.items():
            result = await daemon.simulate_daemon_interaction(query, use_openai)
            results.append(result)
            
            print(f"\n{daemon_id.upper()} Response:")
            print(f"  {result['response']['response'][:200]}...")
            print(f"  Context memories used: {result['context_used']}")
            print(f"  Archivist confidence: {result['archivist_confidence']:.2f}")
        
        print("\n" + "⛧" * 60 + "\n")
    
    # Show hive intelligence summary
    print("⛧ Hive Intelligence Summary:")
    summary = archivist.get_hive_intelligence_summary()
    print(json.dumps(summary, indent=2))
    
    return results


async def main():
    """Main test routine."""
    print("⛧ Archivist Interface Test with Direct OpenAI")
    print("⛧ 'La mémoire collective s'éveille...'")
    print()
    
    try:
        results = await test_archivist_interface()
        
        print("\n⛧" + "═" * 60)
        print("⛧ TEST COMPLETED SUCCESSFULLY!")
        print(f"⛧ Processed {len(results)} daemon interactions")
        print("⛧ Archivist interface is functional!")
        
        return True
        
    except Exception as e:
        print(f"\n⛧ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        archivist.close()


if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1)
