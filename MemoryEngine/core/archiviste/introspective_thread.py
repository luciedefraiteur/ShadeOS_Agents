#!/usr/bin/env python3
"""
⛧ Fil de Discussion Introspectif - Archiviste ⛧
Système où l'Archiviste se parle à lui-même et documente ses appels mémoire
Géré dynamiquement par le système (pas par l'IA)
"""

import json
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path


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


class IntrospectiveParser:
    """Parse les réponses de l'IA pour extraire le fil de discussion"""
    
    def __init__(self):
        self.thought_patterns = [
            r"je pense que",
            r"je me dis que", 
            r"je réfléchis",
            r"je me demande",
            r"je vois que",
            r"je constate que",
            r"je remarque que"
        ]
        
        self.action_patterns = [
            r"je vais",
            r"je dois",
            r"je commence par",
            r"je continue avec",
            r"je passe à",
            r"je cherche",
            r"je consulte"
        ]
        
        self.observation_patterns = [
            r"j'ai trouvé",
            r"j'ai obtenu",
            r"le résultat est",
            r"cela me donne",
            r"je vois",
            r"je constate"
        ]
        
        self.decision_patterns = [
            r"je décide de",
            r"je choisis de",
            r"je vais donc",
            r"par conséquent",
            r"donc je"
        ]
    
    def parse_ai_response(self, response: str) -> List[IntrospectiveMessage]:
        """Parse une réponse de l'IA pour extraire les messages introspectifs"""
        messages = []
        
        # Diviser en phrases
        sentences = re.split(r'[.!?]+', response)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_lower = sentence.lower()
            
            # Détecter le type de message
            message_type = None
            if any(pattern in sentence_lower for pattern in self.thought_patterns):
                message_type = "thought"
            elif any(pattern in sentence_lower for pattern in self.action_patterns):
                message_type = "action"
            elif any(pattern in sentence_lower for pattern in self.observation_patterns):
                message_type = "observation"
            elif any(pattern in sentence_lower for pattern in self.decision_patterns):
                message_type = "decision"
            
            if message_type:
                messages.append(IntrospectiveMessage(
                    timestamp=time.time(),
                    speaker="archiviste",
                    message_type=message_type,
                    content=sentence
                ))
        
        return messages
    
    def extract_memory_calls(self, response: str) -> List[Dict[str, Any]]:
        """Extrait les appels mémoire mentionnés dans la réponse"""
        memory_calls = []
        
        # Patterns pour détecter les appels mémoire
        patterns = [
            r"appel.*mémoire.*(\w+)\.(\w+)",
            r"(\w+)\.(\w+)\(.*\)",
            r"recherche.*(\w+)",
            r"consultation.*(\w+)"
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, response, re.IGNORECASE)
            for match in matches:
                memory_calls.append({
                    "detected": match.group(0),
                    "full_match": match.group(0)
                })
        
        return memory_calls


class IntrospectiveArchiviste:
    """Archiviste avec fil de discussion introspectif géré dynamiquement"""
    
    def __init__(self, memory_engine, memory_registry):
        self.memory_engine = memory_engine
        self.memory_registry = memory_registry
        self.current_thread: Optional[IntrospectiveThread] = None
        self.parser = IntrospectiveParser()
    
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
    
    def process_ai_response(self, response: str, cycle: int = 1) -> None:
        """Traite une réponse de l'IA et met à jour le fil de discussion"""
        if not self.current_thread:
            return
        
        # Parser la réponse pour extraire les messages introspectifs
        introspective_messages = self.parser.parse_ai_response(response)
        
        # Ajouter les messages au fil de discussion
        for msg in introspective_messages:
            self.current_thread.add_message(
                msg.speaker,
                msg.message_type,
                msg.content,
                msg.metadata
            )
        
        # Extraire les appels mémoire mentionnés
        memory_calls = self.parser.extract_memory_calls(response)
        if memory_calls:
            self.current_thread.add_message(
                "system",
                "observation",
                f"Appels mémoire détectés dans la réponse : {len(memory_calls)}",
                {"detected_calls": memory_calls}
            )
    
    def execute_memory_call(self, memory_type: str, method: str, parameters: Dict[str, Any]) -> List[Any]:
        """Exécute un appel mémoire et le documente"""
        if not self.current_thread:
            return []
        
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
            
            # Documenter l'appel
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
            
            # Documenter l'erreur
            self.current_thread.add_memory_call(
                memory_type=memory_type,
                method=method,
                parameters=parameters,
                results=[],
                duration=duration,
                success=False
            )
            
            return []
    
    def get_context_for_next_prompt(self) -> str:
        """Génère le contexte à injecter dans le prochain prompt"""
        if not self.current_thread:
            return ""
        
        return self.current_thread.get_context_for_prompt()
    
    def get_introspective_response(self) -> Dict[str, Any]:
        """Génère la réponse finale avec le fil introspectif"""
        if not self.current_thread:
            return {"error": "Aucun fil de discussion actif"}
        
        thread = self.current_thread
        
        return {
            "type": "ARCHIVISTE_INTROSPECTIVE_RESPONSE",
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