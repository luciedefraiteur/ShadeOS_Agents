#!/usr/bin/env python3
"""
⛧ OpenAI Initializer ⛧
Alma's OpenAI Client Initialization

Initialisation sécurisée du client OpenAI avec vérification des clés API.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import sys
from typing import Optional, Dict, Any
from pathlib import Path


class OpenAIInitializer:
    """Initialiseur sécurisé pour OpenAI avec vérification des clés API."""
    
    def __init__(self):
        self.client = None
        self.api_key = None
        self.is_initialized = False
        
    def load_api_key(self) -> Optional[str]:
        """Charge la clé API OpenAI depuis l'environnement."""
        # Essayer plusieurs sources possibles
        api_key = (
            os.environ.get('OPENAI_API_KEY') or
            os.environ.get('OPENAI_KEY') or
            os.environ.get('OPENAI_SECRET_KEY')
        )
        
        if api_key:
            self.api_key = api_key
            return api_key
        
        return None
    
    def verify_api_key(self, api_key: str) -> Dict[str, Any]:
        """Vérifie la validité d'une clé API OpenAI."""
        if not api_key:
            return {
                "valid": False,
                "error": "Clé API manquante",
                "status": "missing"
            }
        
        # Vérification basique du format
        if not api_key.startswith('sk-'):
            return {
                "valid": False,
                "error": "Format de clé API invalide (doit commencer par 'sk-')",
                "status": "invalid_format"
            }
        
        if len(api_key) < 20:
            return {
                "valid": False,
                "error": "Clé API trop courte",
                "status": "too_short"
            }
        
        return {
            "valid": True,
            "status": "valid",
            "masked_key": f"{api_key[:4]}...{api_key[-4:]}"
        }
    
    def initialize_client(self) -> Dict[str, Any]:
        """Initialise le client OpenAI avec vérification."""
        try:
            # Charger la clé API
            api_key = self.load_api_key()
            if not api_key:
                return {
                    "success": False,
                    "error": "Clé API OpenAI non trouvée dans l'environnement",
                    "status": "no_api_key"
                }
            
            # Vérifier la clé
            verification = self.verify_api_key(api_key)
            if not verification["valid"]:
                return {
                    "success": False,
                    "error": verification["error"],
                    "status": verification["status"]
                }
            
            # Importer OpenAI
            try:
                from openai import OpenAI
            except ImportError:
                return {
                    "success": False,
                    "error": "SDK OpenAI non installé. Installer avec: pip install openai",
                    "status": "sdk_missing"
                }
            
            # Créer le client
            self.client = OpenAI(api_key=api_key)
            self.is_initialized = True
            
            return {
                "success": True,
                "status": "initialized",
                "masked_key": verification["masked_key"],
                "client": self.client
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur d'initialisation: {str(e)}",
                "status": "initialization_error"
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Teste la connexion avec l'API OpenAI."""
        if not self.is_initialized or not self.client:
            return {
                "success": False,
                "error": "Client OpenAI non initialisé",
                "status": "not_initialized"
            }
        
        try:
            # Test simple avec un appel à l'API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            
            return {
                "success": True,
                "status": "connected",
                "model_available": "gpt-3.5-turbo",
                "response_time": "ok"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur de connexion: {str(e)}",
                "status": "connection_failed"
            }
    
    def get_client(self) -> Optional[Any]:
        """Récupère le client OpenAI initialisé."""
        if self.is_initialized and self.client:
            return self.client
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Récupère le statut complet de l'initialisation."""
        return {
            "initialized": self.is_initialized,
            "has_api_key": bool(self.api_key),
            "has_client": bool(self.client),
            "masked_key": f"{self.api_key[:4]}...{self.api_key[-4:]}" if self.api_key else None
        }


def initialize_openai_for_agents() -> Dict[str, Any]:
    """Fonction utilitaire pour initialiser OpenAI pour les agents."""
    print("⛧ Initialisation OpenAI pour Agents...")
    
    initializer = OpenAIInitializer()
    
    # Initialiser le client
    init_result = initializer.initialize_client()
    
    if not init_result["success"]:
        print(f"❌ Échec d'initialisation: {init_result['error']}")
        return init_result
    
    print(f"✅ Client OpenAI initialisé avec la clé: {init_result['masked_key']}")
    
    # Tester la connexion
    test_result = initializer.test_connection()
    
    if test_result["success"]:
        print(f"✅ Connexion API testée avec succès")
        return {
            "success": True,
            "client": initializer.get_client(),
            "status": "ready",
            "test_result": test_result
        }
    else:
        print(f"⚠️  Connexion API échouée: {test_result['error']}")
        return {
            "success": False,
            "client": initializer.get_client(),
            "status": "client_ready_connection_failed",
            "error": test_result["error"]
        }


def create_openai_agent_with_tools(memory_engine) -> Dict[str, Any]:
    """Crée un agent OpenAI complet avec intégration des outils."""
    print("⛧ Création d'agent OpenAI avec outils...")
    
    # Initialiser OpenAI
    openai_result = initialize_openai_for_agents()
    
    if not openai_result["success"]:
        return {
            "success": False,
            "error": f"Impossible d'initialiser OpenAI: {openai_result.get('error', 'Erreur inconnue')}",
            "agent": None
        }
    
    # Initialiser les outils
    try:
        from .openai_integration import create_openai_agent_tools
        openai_tools = create_openai_agent_tools(memory_engine)
        
        return {
            "success": True,
            "client": openai_result["client"],
            "tools": openai_tools,
            "status": "ready",
            "agent": {
                "client": openai_result["client"],
                "tools": openai_tools,
                "tools_config": openai_tools.get_openai_tools_config()
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Erreur lors de l'initialisation des outils: {str(e)}",
            "client": openai_result.get("client")
        }


def main():
    """Test d'initialisation OpenAI."""
    print("⛧ Test d'Initialisation OpenAI")
    print("=" * 50)
    
    # Test d'initialisation simple
    result = initialize_openai_for_agents()
    
    if result["success"]:
        print("✅ Initialisation réussie!")
        print(f"   Statut: {result['status']}")
        if "test_result" in result:
            print(f"   Test: {result['test_result']['status']}")
    else:
        print("❌ Échec d'initialisation")
        print(f"   Erreur: {result['error']}")
        print(f"   Statut: {result['status']}")
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main()) 