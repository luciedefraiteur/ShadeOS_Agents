#!/usr/bin/env python3
"""
⛧ Fil de Discussion Introspectif - Archiviste ⛧
Système où l'Archiviste se parle à lui-même et documente ses appels mémoire
Géré dynamiquement par le système (pas par l'IA)

INTÉGRATION AVEC LE SYSTÈME D'INTROSPECTION INTELLIGENTE
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

# Import du nouveau système d'introspection intelligente
from Core.IntrospectiveParser import UniversalIntrospectiveThread, IntelligentIntrospectiveParser
from Core.LLMProviders import LLMProvider


@dataclass
class IntrospectiveMessage:
    """Un message dans le fil de discussion introspectif"""
    timestamp: float
    speaker: str  # "archiviste", "memory_registry", "reflection"
    message_type: str  # "thought", "action", "observation", "decision"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryCall:
    """Un appel au registre de mémoire"""
    timestamp: float
    memory_type: str  # "fractal", "temporal", "user_requests", "discussion"
    method: str  # "find_memories_by_keyword", "search_temporal", etc.
    parameters: Dict[str, Any]
    results: List[Any]
    duration: float
    success: bool = True


@dataclass
class IntrospectiveThread:
    """Fil de discussion introspectif complet"""
    thread_id: str
    query: str
    messages: List[IntrospectiveMessage] = field(default_factory=list)
    memory_calls: List[MemoryCall] = field(default_factory=list)
    current_understanding: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    is_satisfactory: bool = False
    start_time: float = field(default_factory=time.time)
    
    def add_message(self, speaker: str, message_type: str, content: str, metadata: Dict[str, Any] = None):
        """Ajoute un message au fil de discussion"""
        message = IntrospectiveMessage(
            timestamp=time.time(),
            speaker=speaker,
            message_type=message_type,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
    
    def add_memory_call(self, memory_type: str, method: str, parameters: Dict[str, Any], 
                       results: List[Any], duration: float, success: bool = True):
        """Ajoute un appel au registre de mémoire"""
        call = MemoryCall(
            timestamp=time.time(),
            memory_type=memory_type,
            method=method,
            parameters=parameters,
            results=results,
            duration=duration,
            success=success
        )
        self.memory_calls.append(call)
        
        # Ajouter un message d'observation sur l'appel
        status = "✅" if success else "❌"
        self.add_message(
            "archiviste",
            "observation",
            f"{status} Appel mémoire {memory_type}.{method} : {len(results)} résultats en {duration:.2f}s",
            {"memory_call": call.__dict__}
        )
    
    def get_thread_summary(self) -> str:
        """Génère un résumé du fil de discussion"""
        summary = []
        summary.append(f"🧵 Fil de discussion {self.thread_id}")
        summary.append(f"📝 Requête : {self.query}")
        summary.append(f"⏱️ Durée : {time.time() - self.start_time:.2f}s")
        summary.append(f"💭 Messages : {len(self.messages)}")
        summary.append(f"🔍 Appels mémoire : {len(self.memory_calls)}")
        summary.append(f"📊 Confiance : {self.confidence_score:.2f}")
        summary.append(f"✅ Satisfaisant : {self.is_satisfactory}")
        
        return "\n".join(summary)
    
    def get_recent_messages(self, limit: int = 5) -> List[IntrospectiveMessage]:
        """Récupère les messages récents"""
        return self.messages[-limit:] if limit > 0 else self.messages
    
    def get_memory_calls_summary(self) -> str:
        """Génère un résumé des appels mémoire"""
        if not self.memory_calls:
            return "Aucun appel mémoire effectué"
        
        summary = []
        for call in self.memory_calls:
            status = "✅" if call.success else "❌"
            summary.append(f"{status} {call.memory_type}.{call.method} : {len(call.results)} résultats")
        
        return " | ".join(summary)
    
    def get_context_for_prompt(self) -> str:
        """Génère le contexte du fil de discussion pour injection dans les prompts"""
        if not self.messages:
            return "Aucun historique de discussion disponible."
        
        context_lines = []
        context_lines.append("## 🧵 FIL DE DISCUSSION INTROSPECTIF")
        context_lines.append(f"**Requête initiale :** {self.query}")
        context_lines.append(f"**Durée :** {time.time() - self.start_time:.2f}s")
        context_lines.append(f"**Messages :** {len(self.messages)}")
        context_lines.append(f"**Appels mémoire :** {len(self.memory_calls)}")
        context_lines.append("")
        
        # Messages récents (derniers 3)
        recent_messages = self.get_recent_messages(3)
        if recent_messages:
            context_lines.append("### 💭 DERNIERS MESSAGES :")
            for msg in recent_messages:
                icon = {
                    "thought": "💭",
                    "action": "⚡", 
                    "observation": "👁️",
                    "decision": "🎯"
                }.get(msg.message_type, "💬")
                
                context_lines.append(f"{icon} **{msg.message_type.upper()}** : {msg.content}")
            context_lines.append("")
        
        # Appels mémoire récents
        if self.memory_calls:
            context_lines.append("### 🔍 DERNIERS APPELS MÉMOIRE :")
            for call in self.memory_calls[-3:]:  # Derniers 3 appels
                status = "✅" if call.success else "❌"
                context_lines.append(f"{status} {call.memory_type}.{call.method} : {len(call.results)} résultats")
            context_lines.append("")
        
        return "\n".join(context_lines)
    
    def to_json(self) -> Dict[str, Any]:
        """Convertit le fil en JSON"""
        return {
            "thread_id": self.thread_id,
            "query": self.query,
            "start_time": self.start_time,
            "duration": time.time() - self.start_time,
            "messages": [msg.__dict__ for msg in self.messages],
            "memory_calls": [call.__dict__ for call in self.memory_calls],
            "current_understanding": self.current_understanding,
            "confidence_score": self.confidence_score,
            "is_satisfactory": self.is_satisfactory,
            "summary": self.get_thread_summary()
        }


# L'ancien IntrospectiveParser basé sur des regex rigides a été supprimé
# Remplacé par le système d'introspection intelligente basé sur LLM (IntelligentIntrospectiveParser)


class IntrospectiveArchiviste:
    """Archiviste avec introspection intelligente basée sur LLM"""
    
    def __init__(self, memory_engine, memory_registry, provider: LLMProvider):
        self.memory_engine = memory_engine
        self.memory_registry = memory_registry
        self.provider = provider
        
        # Nouveau système d'introspection intelligente
        self.intelligent_thread = UniversalIntrospectiveThread(
            entity_id="archiviste",
            entity_type="daemon",
            provider=provider,
            max_history=100,
            enable_cache=True  # Cache intelligent activé
        )
        
        # Compatibilité avec l'ancien système
        self.current_thread: Optional[IntrospectiveThread] = None
    
    def start_introspection(self, query: str) -> IntrospectiveThread:
        """Démarre un nouveau fil de discussion introspectif"""
        thread_id = f"introspection_{int(time.time())}"
        self.current_thread = IntrospectiveThread(
            thread_id=thread_id,
            query=query
        )
        
        # Message initial du système
        self.current_thread.add_message(
            "system",
            "thought",
            f"Démarrage de l'analyse introspective pour : '{query}'"
        )
        
        return self.current_thread
    
    async def process_ai_response(self, response: str, cycle: int = 1, context: Optional[Dict[str, Any]] = None) -> None:
        """Traite une réponse de l'IA avec le nouveau système d'introspection intelligente"""
        
        # Utilisation du nouveau système intelligent
        await self.intelligent_thread.add_response(response, context)
        
        # Compatibilité avec l'ancien système si nécessaire
        if self.current_thread:
            # Ajouter un message simple pour la compatibilité
            self.current_thread.add_message(
                "archiviste",
                "thought",
                f"Réponse traitée par le système d'introspection intelligente (cycle {cycle})",
                {"intelligent_processing": True, "cycle": cycle}
            )
    
    async def execute_memory_call(self, memory_type: str, method: str, parameters: Dict[str, Any]) -> List[Any]:
        """Exécute un appel mémoire et le documente avec le nouveau système intelligent"""
        
        start_time = time.time()
        
        try:
            # Exécuter l'appel selon le type de mémoire
            if memory_type == "fractal":
                if method == "find_memories_by_keyword":
                    results = self.memory_engine.find_memories_by_keyword(parameters.get("keyword", ""))
                elif method == "find_by_strata":
                    results = self.memory_engine.find_by_strata(parameters.get("strata", ""))
                else:
                    results = []
                    
            elif memory_type == "temporal":
                if method == "search_temporal":
                    results = self.memory_engine.temporal_index.search_temporal(parameters.get("query", ""))
                else:
                    results = []
                    
            elif memory_type == "registry":
                if method == "get_all_memory_types":
                    results = [self.memory_registry.get_all_memory_types()]
                else:
                    results = []
                    
            else:
                results = []
            
            duration = time.time() - start_time
            
            # Documentation avec le nouveau système intelligent
            await self.intelligent_thread.add_memory_call(
                memory_type=memory_type,
                query=f"{method}({parameters})",
                result=results,
                confidence=1.0 if results else 0.5
            )
            
            # Compatibilité avec l'ancien système
            if self.current_thread:
                self.current_thread.add_memory_call(
                    memory_type=memory_type,
                    method=method,
                    parameters=parameters,
                    results=results,
                    duration=duration,
                    success=True
                )
            
            return results
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Documentation de l'erreur avec le nouveau système
            await self.intelligent_thread.add_self_observation(
                f"Erreur appel mémoire {memory_type}.{method}: {e}",
                confidence=0.9
            )
            
            # Compatibilité avec l'ancien système
            if self.current_thread:
                self.current_thread.add_memory_call(
                    memory_type=memory_type,
                    method=method,
                    parameters=parameters,
                    results=[],
                    duration=duration,
                    success=False
                )
            
            print(f"❌ Erreur appel mémoire {memory_type}.{method}: {e}")
            return []
    
    async def get_context_for_next_prompt(self) -> str:
        """Génère le contexte à injecter dans le prochain prompt avec le nouveau système intelligent"""
        
        # Utilisation du nouveau système intelligent
        intelligent_context = await self.intelligent_thread.get_context_for_prompt()
        
        # Compatibilité avec l'ancien système
        if self.current_thread:
            old_context = self.current_thread.get_context_for_prompt()
            return f"{intelligent_context}\n\n{old_context}"
        
        return intelligent_context
    
    async def get_introspective_response(self) -> Dict[str, Any]:
        """Génère la réponse finale avec le nouveau système d'introspection intelligente"""
        
        # Analyse du comportement avec le nouveau système
        behavior_analysis = await self.intelligent_thread.analyze_own_behavior()
        
        # Contexte intelligent
        intelligent_context = await self.intelligent_thread.get_context_for_prompt()
        
        # Compatibilité avec l'ancien système
        old_response = {}
        if self.current_thread:
            thread = self.current_thread
            old_response = {
                "thread_id": thread.thread_id,
                "query": thread.query,
                "duration": time.time() - thread.start_time,
                "confidence": thread.confidence_score,
                "satisfactory": thread.is_satisfactory,
                "introspective_thread": {
                    "summary": thread.get_thread_summary(),
                    "messages": [msg.__dict__ for msg in thread.messages],
                    "memory_calls_summary": thread.get_memory_calls_summary(),
                    "recent_thoughts": [msg.content for msg in thread.get_recent_messages(3) if msg.message_type == "thought"]
                },
                "memory_calls": [call.__dict__ for call in thread.memory_calls],
                "results_count": len([call for call in thread.memory_calls if call.success]),
                "full_thread": thread.to_json()
            }
        
        return {
            "type": "ARCHIVISTE_INTROSPECTIVE_RESPONSE",
            "intelligent_analysis": behavior_analysis,
            "intelligent_context": intelligent_context,
            "intelligent_summary": self.intelligent_thread.get_summary(),
            "legacy_compatibility": old_response,
            "cache_stats": self.intelligent_thread.cache.get_cache_stats() if self.intelligent_thread.cache else None
        }


if __name__ == "__main__":
    # Test du système introspectif
    print("🧵 Test du Fil de Discussion Introspectif (Géré Dynamiquement)")
    print("=" * 60)
    
    # Simulation
    class MockMemoryEngine:
        def find_memories_by_keyword(self, keyword):
            return [{"path": f"/test/{keyword}", "content": f"Contenu pour {keyword}"}]
        
        def find_by_strata(self, strata):
            return [{"path": f"/test/{strata}", "content": f"Contenu pour {strata}"}]
        
        def temporal_index(self):
            class MockTemporalIndex:
                def search_temporal(self, query):
                    return [{"path": f"/temporal/{query}", "content": f"Résultat temporel pour {query}"}]
            return MockTemporalIndex()
    
    class MockMemoryRegistry:
        def get_all_memory_types(self):
            return {
                "fractal": {"name": "Mémoire Fractale", "description": "Mémoire profonde", "capabilities": ["stockage"], "access_methods": ["find"]},
                "temporal": {"name": "Mémoire Temporelle", "description": "Index temporel", "capabilities": ["recherche"], "access_methods": ["search"]}
            }
    
    archiviste = IntrospectiveArchiviste(MockMemoryEngine(), MockMemoryRegistry())
    
    # Test
    query = "Décris-moi les types de mémoire disponibles"
    thread = archiviste.start_introspection(query)
    
    # Simuler une réponse de l'IA
    ai_response = """
    Je vais commencer par analyser cette requête sur les types de mémoire. 
    Je pense que l'utilisateur veut une vue d'ensemble complète. 
    Je vais donc consulter le registre de mémoire pour obtenir toutes les informations disponibles.
    J'ai trouvé 2 types de mémoire dans le registre : fractal et temporal.
    Je constate que cela me donne une bonne base pour répondre.
    """
    
    # Traiter la réponse de l'IA
    archiviste.process_ai_response(ai_response)
    
    # Exécuter un appel mémoire
    results = archiviste.execute_memory_call("registry", "get_all_memory_types", {})
    
    # Générer le contexte pour le prochain prompt
    context = archiviste.get_context_for_next_prompt()
    
    print("📝 Contexte généré pour le prochain prompt :")
    print(context)
    print("\n" + "=" * 60)
    
    final_response = archiviste.get_introspective_response()
    
    print("📊 Réponse finale :")
    print(json.dumps(final_response, indent=2, ensure_ascii=False)) 