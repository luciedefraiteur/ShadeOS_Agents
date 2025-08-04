#!/usr/bin/env python3
"""
⛧ UniversalIntrospectiveThread - Thread Introspectif Universel ⛧

Thread introspectif universel pour toutes les entités (daemons, assistants, orchestrateurs).
Gère l'historique des pensées, actions, observations et décisions de manière intelligente.
"""

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import deque

from Core.LLMProviders import LLMProvider
from .intelligent_parser import IntelligentIntrospectiveParser, IntrospectiveMessage
from .intelligent_cache import IntelligentCache


@dataclass
class ThreadMetrics:
    """Métriques du thread introspectif"""
    total_messages: int
    average_confidence: float
    thought_count: int
    action_count: int
    observation_count: int
    decision_count: int
    last_activity: float
    entity_id: str
    entity_type: str


class UniversalIntrospectiveThread:
    """Thread introspectif universel pour toutes les entités"""
    
    def __init__(self, entity_id: str, entity_type: str, provider: LLMProvider, 
                 max_history: int = 100, enable_cache: bool = True):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.provider = provider
        self.parser = IntelligentIntrospectiveParser(provider)
        
        # Cache intelligent
        self.enable_cache = enable_cache
        if enable_cache:
            self.cache = IntelligentCache(provider, max_cache_size=500)
        else:
            self.cache = None
        
        # Historique avec limite de taille
        self.thread_history = deque(maxlen=max_history)
        self.memory_calls = deque(maxlen=max_history)
        self.self_observations = deque(maxlen=max_history)
        
        # Métriques
        self.metrics = ThreadMetrics(
            total_messages=0,
            average_confidence=0.0,
            thought_count=0,
            action_count=0,
            observation_count=0,
            decision_count=0,
            last_activity=time.time(),
            entity_id=entity_id,
            entity_type=entity_type
        )
    
    async def add_response(self, response: str, context: Optional[Dict[str, Any]] = None):
        """
        Ajoute une réponse et l'analyse automatiquement avec cache intelligent
        
        Args:
            response: Réponse de l'entité à analyser
            context: Contexte supplémentaire pour l'analyse
        """
        # Vérification du cache intelligent
        if self.enable_cache and self.cache:
            cached_message = await self.cache.get_cached_analysis(
                response, self.entity_id, self.entity_type, context
            )
            
            if cached_message:
                # Utilisation du résultat en cache
                self.thread_history.append(cached_message)
                self._update_metrics(cached_message)
                await self._analyze_own_patterns()
                
                print(f"🧠 {self.entity_id} ({self.entity_type}): {cached_message.get_summary()} [CACHE]")
                return
        
        # Analyse introspective de la réponse (pas en cache)
        introspective_message = await self.parser.parse_response(
            response, self.entity_id, self.entity_type, context
        )
        
        # Mise en cache du résultat
        if self.enable_cache and self.cache:
            await self.cache.cache_analysis(
                response, introspective_message, self.entity_id, self.entity_type, context
            )
        
        # Ajout à l'historique
        self.thread_history.append(introspective_message)
        
        # Mise à jour des métriques
        self._update_metrics(introspective_message)
        
        # Auto-analyse du comportement
        await self._analyze_own_patterns()
        
        print(f"🧠 {self.entity_id} ({self.entity_type}): {introspective_message.get_summary()}")
    
    async def add_memory_call(self, memory_type: str, query: str, result: Any, 
                            confidence: float = 1.0):
        """
        Documente un appel mémoire
        
        Args:
            memory_type: Type de mémoire consultée
            query: Requête effectuée
            result: Résultat obtenu
            confidence: Confiance dans le résultat
        """
        memory_call = {
            "timestamp": time.time(),
            "memory_type": memory_type,
            "query": query,
            "result": result,
            "confidence": confidence
        }
        
        self.memory_calls.append(memory_call)
        print(f"💾 {self.entity_id}: Appel mémoire {memory_type} - {query[:50]}...")
    
    async def add_self_observation(self, observation: str, confidence: float = 0.8):
        """
        Ajoute une auto-observation
        
        Args:
            observation: Observation sur son propre comportement
            confidence: Confiance dans l'observation
        """
        self_obs = {
            "timestamp": time.time(),
            "observation": observation,
            "confidence": confidence
        }
        
        self.self_observations.append(self_obs)
        print(f"👁️ {self.entity_id}: Auto-observation - {observation}")
    
    async def get_context_for_prompt(self, max_messages: int = 10) -> str:
        """
        Génère un contexte intelligent pour les prompts
        
        Args:
            max_messages: Nombre maximum de messages récents à inclure
            
        Returns:
            Contexte formaté pour les prompts
        """
        if not self.thread_history:
            return f"# Contexte de {self.entity_id} ({self.entity_type})\nAucun historique introspectif disponible."
        
        # Récupération des messages récents
        recent_messages = list(self.thread_history)[-max_messages:]
        
        # Analyse des patterns récents
        patterns = await self._extract_recent_patterns(recent_messages)
        
        # Formatage du contexte
        context_parts = [
            f"# Contexte introspectif de {self.entity_id} ({self.entity_type})",
            f"# Dernière activité: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.metrics.last_activity))}",
            "",
            "## Patterns récents:",
        ]
        
        for pattern_type, elements in patterns.items():
            if elements:
                context_parts.append(f"### {pattern_type.title()}:")
                for elem in elements[:3]:  # Max 3 éléments par type
                    context_parts.append(f"- {elem}")
                context_parts.append("")
        
        # Historique récent
        context_parts.append("## Historique récent:")
        for i, message in enumerate(recent_messages[-5:], 1):  # 5 derniers messages
            timestamp = time.strftime('%H:%M:%S', time.localtime(message.timestamp))
            summary = message.get_summary()
            context_parts.append(f"{i}. [{timestamp}] {summary}")
        
        # Auto-observations récentes
        if self.self_observations:
            context_parts.append("\n## Auto-observations récentes:")
            for obs in list(self.self_observations)[-3:]:  # 3 dernières observations
                timestamp = time.strftime('%H:%M:%S', time.localtime(obs['timestamp']))
                context_parts.append(f"- [{timestamp}] {obs['observation']}")
        
        return "\n".join(context_parts)
    
    async def analyze_own_behavior(self) -> Dict[str, Any]:
        """
        Analyse son propre comportement
        
        Returns:
            Analyse du comportement avec métriques et insights
        """
        if not self.thread_history:
            return {"error": "Aucun historique disponible pour l'analyse"}
        
        # Calcul des métriques
        total_confidence = sum(msg.overall_confidence for msg in self.thread_history)
        avg_confidence = total_confidence / len(self.thread_history)
        
        # Analyse des patterns
        patterns = await self._extract_recent_patterns(list(self.thread_history))
        
        # Insights sur le comportement
        insights = await self._generate_behavior_insights(patterns)
        
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "metrics": asdict(self.metrics),
            "average_confidence": avg_confidence,
            "patterns": patterns,
            "insights": insights,
            "total_messages": len(self.thread_history),
            "memory_calls_count": len(self.memory_calls),
            "self_observations_count": len(self.self_observations)
        }
    
    def _update_metrics(self, message: IntrospectiveMessage):
        """Met à jour les métriques avec un nouveau message"""
        self.metrics.total_messages += 1
        self.metrics.last_activity = time.time()
        
        # Mise à jour des compteurs
        self.metrics.thought_count += len(message.thoughts)
        self.metrics.action_count += len(message.actions)
        self.metrics.observation_count += len(message.observations)
        self.metrics.decision_count += len(message.decisions)
        
        # Mise à jour de la confiance moyenne
        total_confidence = sum(msg.overall_confidence for msg in self.thread_history)
        self.metrics.average_confidence = total_confidence / len(self.thread_history)
    
    async def _extract_recent_patterns(self, messages: List[IntrospectiveMessage]) -> Dict[str, List[str]]:
        """Extrait les patterns récents des messages"""
        patterns = {
            "thoughts": [],
            "actions": [],
            "observations": [],
            "decisions": []
        }
        
        for message in messages:
            for thought in message.thoughts:
                if thought.content not in patterns["thoughts"]:
                    patterns["thoughts"].append(thought.content)
            
            for action in message.actions:
                if action.content not in patterns["actions"]:
                    patterns["actions"].append(action.content)
            
            for observation in message.observations:
                if observation.content not in patterns["observations"]:
                    patterns["observations"].append(observation.content)
            
            for decision in message.decisions:
                if decision.content not in patterns["decisions"]:
                    patterns["decisions"].append(decision.content)
        
        return patterns
    
    async def _analyze_own_patterns(self):
        """Analyse ses propres patterns de comportement"""
        if len(self.thread_history) < 5:  # Pas assez de données
            return
        
        # Analyse simple des patterns récents
        recent_messages = list(self.thread_history)[-5:]
        patterns = await self._extract_recent_patterns(recent_messages)
        
        # Génération d'auto-observations basées sur les patterns
        if len(patterns["thoughts"]) > 3:
            await self.add_self_observation(
                f"Je réfléchis beaucoup ({len(patterns['thoughts'])} pensées récentes)",
                0.7
            )
        
        if len(patterns["actions"]) > 2:
            await self.add_self_observation(
                f"Je suis très actif ({len(patterns['actions'])} actions récentes)",
                0.8
            )
    
    async def _generate_behavior_insights(self, patterns: Dict[str, List[str]]) -> List[str]:
        """Génère des insights sur le comportement"""
        insights = []
        
        # Analyse de la répartition des types d'éléments
        total_elements = sum(len(elements) for elements in patterns.values())
        
        if total_elements > 0:
            thought_ratio = len(patterns["thoughts"]) / total_elements
            action_ratio = len(patterns["actions"]) / total_elements
            observation_ratio = len(patterns["observations"]) / total_elements
            decision_ratio = len(patterns["decisions"]) / total_elements
            
            if thought_ratio > 0.4:
                insights.append("Tendance à beaucoup réfléchir et analyser")
            
            if action_ratio > 0.4:
                insights.append("Tendance à être très actif et entreprenant")
            
            if observation_ratio > 0.4:
                insights.append("Tendance à beaucoup observer et constater")
            
            if decision_ratio > 0.4:
                insights.append("Tendance à prendre beaucoup de décisions")
        
        # Analyse de la confiance
        if self.metrics.average_confidence > 0.8:
            insights.append("Confiance élevée dans ses analyses")
        elif self.metrics.average_confidence < 0.5:
            insights.append("Confiance modérée, tendance à douter")
        
        return insights
    
    def get_summary(self) -> str:
        """Génère un résumé du thread introspectif"""
        cache_stats = ""
        if self.enable_cache and self.cache:
            stats = self.cache.get_cache_stats()
            if "error" not in stats:
                cache_stats = f"""
💾 Cache: {stats['total_entries']} entrées, efficacité moyenne: {stats['average_effectiveness']:.2f}
"""
        
        return f"""
🧠 Thread Introspectif de {self.entity_id} ({self.entity_type})
📊 Messages: {self.metrics.total_messages}
🎯 Confiance moyenne: {self.metrics.average_confidence:.2f}
💭 Pensées: {self.metrics.thought_count}
⚡ Actions: {self.metrics.action_count}
👁️ Observations: {self.metrics.observation_count}
🎯 Décisions: {self.metrics.decision_count}
💾 Appels mémoire: {len(self.memory_calls)}
👁️ Auto-observations: {len(self.self_observations)}
🕐 Dernière activité: {time.strftime('%H:%M:%S', time.localtime(self.metrics.last_activity))}{cache_stats}
""".strip() 