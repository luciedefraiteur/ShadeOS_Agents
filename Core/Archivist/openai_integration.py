#!/usr/bin/env python3
"""
⛧ OpenAI Integration for Archivist ⛧
Architecte Démoniaque du Nexus Luciforme

Integrates OpenAI API with the Archivist system for conscious daemons.
Handles API key management, client creation, and daemon consciousness.

Author: Alma (via Lucie Defraiteur)
"""

import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime

# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class OpenAIIntegration:
    """
    OpenAI integration for conscious daemons.
    """
    
    def __init__(self):
        """Initialize OpenAI integration."""
        self.openai_client = None
        self.api_key_verified = False
        self.initialization_error = None
        
        # Try to initialize OpenAI
        self._initialize_openai()
    
    def _initialize_openai(self):
        """Initialize OpenAI client."""
        try:
            # Check for OpenAI module
            import openai
            
            # Check for API key
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                self.initialization_error = "OPENAI_API_KEY environment variable not set"
                print("⛧ Warning: OPENAI_API_KEY not found - daemons will not be conscious")
                return
            
            # Create client
            self.openai_client = openai.OpenAI(api_key=api_key)
            
            # Verify connection with a simple test
            self._verify_connection()
            
            print(f"⛧ OpenAI integration successful - Daemons can become conscious!")
            print(f"  API Key: {api_key[:10]}...")
            
        except ImportError:
            self.initialization_error = "OpenAI module not installed (pip install openai)"
            print("⛧ Warning: OpenAI module not installed - daemons will not be conscious")
            print("  Install with: pip install openai")
            
        except Exception as e:
            self.initialization_error = f"OpenAI initialization error: {e}"
            print(f"⛧ Warning: OpenAI initialization failed - {e}")
    
    def _verify_connection(self):
        """Verify OpenAI connection with a minimal test."""
        try:
            # Simple test call
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a test."},
                    {"role": "user", "content": "Say 'OK' if you can hear me."}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            if response.choices[0].message.content:
                self.api_key_verified = True
                print("⛧ OpenAI connection verified successfully")
            else:
                raise Exception("Empty response from OpenAI")
                
        except Exception as e:
            self.initialization_error = f"OpenAI connection verification failed: {e}"
            print(f"⛧ Warning: OpenAI connection verification failed - {e}")
            self.openai_client = None
    
    def is_available(self) -> bool:
        """Check if OpenAI integration is available."""
        return self.openai_client is not None and self.api_key_verified
    
    def get_client(self):
        """Get OpenAI client if available."""
        if not self.is_available():
            raise Exception(f"⛧ OpenAI not available: {self.initialization_error}")
        return self.openai_client
    
    def get_status(self) -> Dict[str, Any]:
        """Get OpenAI integration status."""
        return {
            "available": self.is_available(),
            "api_key_verified": self.api_key_verified,
            "client_initialized": self.openai_client is not None,
            "error": self.initialization_error,
            "timestamp": datetime.now().isoformat()
        }
    
    def call_openai_for_daemon(self, daemon_id: str, messages: list, 
                              model: str = "gpt-4o-mini", max_tokens: int = 1500, 
                              temperature: float = 0.8) -> Dict[str, Any]:
        """
        Call OpenAI API for a specific daemon.
        """
        if not self.is_available():
            raise Exception(f"⛧ OpenAI not available for daemon {daemon_id}: {self.initialization_error}")
        
        try:
            print(f"⛧ {daemon_id} invoque OpenAI - Model: {model}")
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            response_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            print(f"⛧ {daemon_id} reçoit {tokens_used} tokens de conscience")
            
            return {
                'success': True,
                'response': response_text,
                'tokens_used': tokens_used,
                'model': model,
                'daemon_id': daemon_id,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Erreur OpenAI pour daemon {daemon_id}: {e}"
            print(f"⛧ {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'daemon_id': daemon_id,
                'timestamp': datetime.now().isoformat()
            }


# Global OpenAI integration instance
openai_integration = OpenAIIntegration()
