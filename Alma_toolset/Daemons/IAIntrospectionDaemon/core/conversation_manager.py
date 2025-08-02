"""
Gestionnaire de conversation interne pour le Daemon Introspectif
Permet au daemon de s'auto-messager et de maintenir un historique de conversation
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ConversationMessage:
    """Représente un message dans la conversation interne du daemon"""
    timestamp: str
    sender: str  # "daemon", "memory_engine", "tool_memory", "editing_session", "ai_engine"
    message_type: str  # "request", "response", "insight", "error", "context_injection"
    content: str
    metadata: Dict[str, Any]
    conversation_id: str
    parent_message_id: Optional[str] = None


@dataclass
class ConversationSession:
    """Représente une session de conversation complète"""
    session_id: str
    start_time: str
    end_time: Optional[str]
    messages: List[ConversationMessage]
    context: Dict[str, Any]
    insights: List[str]
    request_history: List[str]


class ConversationManager:
    """Gestionnaire de conversation interne pour le daemon"""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        
        self.current_session: Optional[ConversationSession] = None
        self.message_counter = 0
        
    async def start_session(self, context: Dict[str, Any] = None) -> str:
        """Démarre une nouvelle session de conversation"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = ConversationSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            end_time=None,
            messages=[],
            context=context or {},
            insights=[],
            request_history=[]
        )
        
        # Message initial du daemon
        await self.add_message(
            sender="daemon",
            message_type="session_start",
            content="🧠 Session d'introspection démarrée",
            metadata={"session_id": session_id}
        )
        
        return session_id
    
    async def end_session(self) -> Dict[str, Any]:
        """Termine la session courante et retourne le résumé"""
        if not self.current_session:
            raise ValueError("Aucune session active")
        
        self.current_session.end_time = datetime.now().isoformat()
        
        # Message de fin
        await self.add_message(
            sender="daemon",
            message_type="session_end",
            content="🏁 Session d'introspection terminée",
            metadata={"duration": self._calculate_session_duration()}
        )
        
        # Sauvegarde de la session
        await self._save_session()
        
        # Résumé de la session
        summary = self._generate_session_summary()
        
        # Reset pour nouvelle session
        self.current_session = None
        self.message_counter = 0
        
        return summary
    
    async def add_message(self, 
                         sender: str, 
                         message_type: str, 
                         content: str, 
                         metadata: Dict[str, Any] = None,
                         parent_message_id: Optional[str] = None) -> str:
        """Ajoute un message à la conversation courante"""
        if not self.current_session:
            raise ValueError("Aucune session active")
        
        message_id = f"msg_{self.message_counter:04d}"
        self.message_counter += 1
        
        message = ConversationMessage(
            timestamp=datetime.now().isoformat(),
            sender=sender,
            message_type=message_type,
            content=content,
            metadata=metadata or {},
            conversation_id=self.current_session.session_id,
            parent_message_id=parent_message_id
        )
        
        self.current_session.messages.append(message)
        
        # Log en temps réel
        await self._log_message(message)
        
        return message_id
    
    async def add_insight(self, insight: str, source: str = "daemon") -> str:
        """Ajoute un insight à la session"""
        if not self.current_session:
            raise ValueError("Aucune session active")
        
        self.current_session.insights.append(insight)
        
        return await self.add_message(
            sender=source,
            message_type="insight",
            content=insight,
            metadata={"insight_type": "discovery"}
        )
    
    async def add_request(self, request: str, request_type: str) -> str:
        """Ajoute une requête à l'historique"""
        if not self.current_session:
            raise ValueError("Aucune session active")
        
        self.current_session.request_history.append(request)
        
        return await self.add_message(
            sender="daemon",
            message_type="request",
            content=request,
            metadata={"request_type": request_type}
        )
    
    async def get_conversation_history(self, 
                                     message_type: Optional[str] = None,
                                     sender: Optional[str] = None,
                                     limit: Optional[int] = None) -> List[ConversationMessage]:
        """Récupère l'historique de conversation avec filtres"""
        if not self.current_session:
            return []
        
        messages = self.current_session.messages
        
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]
        
        if sender:
            messages = [m for m in messages if m.sender == sender]
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    async def get_context_summary(self) -> Dict[str, Any]:
        """Récupère un résumé du contexte de la conversation"""
        if not self.current_session:
            return {}
        
        messages = self.current_session.messages
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        
        return {
            "session_id": self.current_session.session_id,
            "message_count": len(messages),
            "insights_count": len(self.current_session.insights),
            "requests_count": len(self.current_session.request_history),
            "recent_messages": [
                {
                    "timestamp": msg.timestamp,
                    "sender": msg.sender,
                    "type": msg.message_type,
                    "content_preview": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                }
                for msg in recent_messages
            ],
            "current_context": self.current_session.context
        }
    
    async def inject_context_into_prompt(self, prompt: str) -> str:
        """Injecte le contexte de conversation dans un prompt"""
        if not self.current_session:
            return prompt
        
        context_summary = await self.get_context_summary()
        
        context_injection = f"""
<🜃contexte_conversation_interne>
  <🜄session_info>
    Session: {context_summary['session_id']}
    Messages: {context_summary['message_count']}
    Insights: {context_summary['insights_count']}
    Requêtes: {context_summary['requests_count']}
  </🜄session_info>
  
  <🜂messages_récents>
    {self._format_recent_messages(context_summary['recent_messages'])}
  </🜂messages_récents>
  
  <🜁contexte_actuel>
    {json.dumps(self.current_session.context, indent=2, ensure_ascii=False)}
  </🜁contexte_actuel>
</🜃contexte_conversation_interne>

"""
        
        return prompt.replace("<🜃contexte_conversation_interne>", context_injection)
    
    def _format_recent_messages(self, messages: List[Dict]) -> str:
        """Formate les messages récents pour l'injection contextuelle"""
        if not messages:
            return "Aucun message récent"
        
        formatted = []
        for msg in messages:
            formatted.append(f"  [{msg['timestamp']}] {msg['sender']} ({msg['type']}): {msg['content_preview']}")
        
        return "\n".join(formatted)
    
    def _calculate_session_duration(self) -> str:
        """Calcule la durée de la session"""
        if not self.current_session or not self.current_session.end_time:
            return "en cours"
        
        start = datetime.fromisoformat(self.current_session.start_time)
        end = datetime.fromisoformat(self.current_session.end_time)
        duration = end - start
        
        return str(duration)
    
    def _generate_session_summary(self) -> Dict[str, Any]:
        """Génère un résumé de la session"""
        if not self.current_session:
            return {}
        
        return {
            "session_id": self.current_session.session_id,
            "start_time": self.current_session.start_time,
            "end_time": self.current_session.end_time,
            "duration": self._calculate_session_duration(),
            "total_messages": len(self.current_session.messages),
            "total_insights": len(self.current_session.insights),
            "total_requests": len(self.current_session.request_history),
            "message_types": self._count_message_types(),
            "senders": self._count_senders(),
            "insights": self.current_session.insights,
            "request_history": self.current_session.request_history
        }
    
    def _count_message_types(self) -> Dict[str, int]:
        """Compte les types de messages"""
        if not self.current_session:
            return {}
        
        counts = {}
        for msg in self.current_session.messages:
            counts[msg.message_type] = counts.get(msg.message_type, 0) + 1
        
        return counts
    
    def _count_senders(self) -> Dict[str, int]:
        """Compte les expéditeurs de messages"""
        if not self.current_session:
            return {}
        
        counts = {}
        for msg in self.current_session.messages:
            counts[msg.sender] = counts.get(msg.sender, 0) + 1
        
        return counts
    
    async def _save_session(self):
        """Sauvegarde la session dans un fichier JSON"""
        if not self.current_session:
            return
        
        session_file = self.logs_dir / f"conversation_{self.current_session.session_id}.json"
        
        session_data = {
            "session": asdict(self.current_session),
            "summary": self._generate_session_summary()
        }
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    async def _log_message(self, message: ConversationMessage):
        """Log un message en temps réel"""
        log_file = self.logs_dir / f"realtime_{self.current_session.session_id}.log"
        
        log_entry = f"[{message.timestamp}] {message.sender} ({message.message_type}): {message.content}\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry) 