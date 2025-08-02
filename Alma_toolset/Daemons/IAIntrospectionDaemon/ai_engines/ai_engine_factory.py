#!/usr/bin/env python3
"""
🏭 AI Engine Factory - IAIntrospectionDaemon ⛧

Factory pour créer et gérer les moteurs IA (Ollama/OpenAI).
Gestion d'erreurs, fallbacks et configuration dynamique.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class AIEngine(ABC):
    """Classe abstraite pour les moteurs IA."""
    
    @abstractmethod
    async def query(self, prompt: str, **kwargs) -> str:
        """Exécute une requête IA et retourne la réponse."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Vérifie si le moteur IA est disponible."""
        pass


class AIEngineFactory:
    """Factory pour créer des moteurs IA (Ollama/OpenAI)."""
    
    def __init__(self, primary_engine: str = "ollama", fallback_engine: str = "openai"):
        """
        Initialise la factory de moteurs IA.
        
        Args:
            primary_engine: Moteur principal ("ollama" ou "openai")
            fallback_engine: Moteur de secours
        """
        self.primary_engine = primary_engine
        self.fallback_engine = fallback_engine
        self.engines = {}
        self.engine_configs = {
            "ollama": {
                "model": "qwen2.5:7b-instruct",
                "timeout": 30,
                "max_retries": 3
            },
            "openai": {
                "model": "gpt-4",
                "timeout": 60,
                "max_retries": 2
            }
        }
    
    async def get_engine(self, engine_type: str = None) -> AIEngine:
        """
        Retourne un moteur IA configuré.
        
        Args:
            engine_type: Type de moteur ("ollama" ou "openai")
            
        Returns:
            Instance du moteur IA configuré
        """
        engine_type = engine_type or self.primary_engine
        
        if engine_type not in self.engines:
            self.engines[engine_type] = await self._create_engine(engine_type)
        
        return self.engines[engine_type]
    
    async def get_available_engine(self) -> Optional[AIEngine]:
        """
        Retourne le premier moteur IA disponible.
        
        Returns:
            Premier moteur disponible ou None
        """
        # Essaie le moteur principal
        primary = await self.get_engine(self.primary_engine)
        if await primary.is_available():
            return primary
        
        # Essaie le moteur de secours
        if self.fallback_engine != self.primary_engine:
            fallback = await self.get_engine(self.fallback_engine)
            if await fallback.is_available():
                return fallback
        
        return None
    
    async def _create_engine(self, engine_type: str) -> AIEngine:
        """
        Crée un moteur IA du type spécifié.
        
        Args:
            engine_type: Type de moteur à créer
            
        Returns:
            Instance du moteur IA
        """
        if engine_type == "ollama":
            return await self._create_ollama_engine()
        elif engine_type == "openai":
            return await self._create_openai_engine()
        else:
            raise ValueError(f"Type de moteur non supporté: {engine_type}")
    
    async def _create_ollama_engine(self) -> 'OllamaEngine':
        """Crée un moteur Ollama."""
        from .ollama_engine import OllamaEngine
        config = self.engine_configs["ollama"]
        return OllamaEngine(
            model=config["model"],
            timeout=config["timeout"],
            max_retries=config["max_retries"]
        )
    
    async def _create_openai_engine(self) -> 'OpenAIEngine':
        """Crée un moteur OpenAI."""
        from .openai_engine import OpenAIEngine
        config = self.engine_configs["openai"]
        return OpenAIEngine(
            model=config["model"],
            timeout=config["timeout"],
            max_retries=config["max_retries"]
        )
    
    def configure_engine(self, engine_type: str, **config):
        """
        Configure un moteur IA.
        
        Args:
            engine_type: Type de moteur à configurer
            **config: Configuration à appliquer
        """
        if engine_type in self.engine_configs:
            self.engine_configs[engine_type].update(config)
            # Réinitialise le moteur si déjà créé
            if engine_type in self.engines:
                del self.engines[engine_type]
    
    async def test_all_engines(self) -> Dict[str, bool]:
        """
        Teste tous les moteurs IA disponibles.
        
        Returns:
            Dict avec statut de disponibilité de chaque moteur
        """
        results = {}
        
        for engine_type in ["ollama", "openai"]:
            try:
                engine = await self.get_engine(engine_type)
                results[engine_type] = await engine.is_available()
            except Exception as e:
                print(f"❌ Erreur test {engine_type}: {e}")
                results[engine_type] = False
        
        return results


# Instance globale de la factory
_ai_factory = None

async def get_ai_factory() -> AIEngineFactory:
    """Retourne l'instance globale de la factory IA."""
    global _ai_factory
    if _ai_factory is None:
        _ai_factory = AIEngineFactory()
    return _ai_factory 