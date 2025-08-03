import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class DiscussionTimeline:
    """Timeline de discussion pour MemoryEngine (WhatsApp-style)."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.timeline_dir = self.base_path / "memory" / "discussion_timelines"
        self.timeline_dir.mkdir(parents=True, exist_ok=True)
        
        # Timelines par interlocuteur
        self.timelines = {}
        self.load_timelines()
    
    def load_timelines(self):
        """Charge toutes les timelines existantes."""
        for timeline_file in self.timeline_dir.glob("*.json"):
            interlocutor = timeline_file.stem
            with open(timeline_file, 'r', encoding='utf-8') as f:
                self.timelines[interlocutor] = json.load(f)
    
    def add_message(self, interlocutor: str, message: Dict[str, Any], direction: str = "incoming"):
        """Ajoute un message à la timeline d'un interlocuteur."""
        if interlocutor not in self.timelines:
            self.timelines[interlocutor] = {
                "interlocutor": interlocutor,
                "created_at": datetime.now().isoformat(),
                "messages": [],
                "metadata": {
                    "total_messages": 0,
                    "last_activity": None,
                    "message_types": {}
                }
            }
        
        # Création de l'entrée de message
        message_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "direction": direction,
            "message": message,
            "content": self._extract_content(message),
            "message_type": message.get("type", "message")
        }
        
        # Ajout à la timeline
        self.timelines[interlocutor]["messages"].append(message_entry)
        
        # Mise à jour des métadonnées
        metadata = self.timelines[interlocutor]["metadata"]
        metadata["total_messages"] += 1
        metadata["last_activity"] = message_entry["timestamp"]
        
        # Comptage des types de messages
        msg_type = message_entry["message_type"]
        if msg_type not in metadata["message_types"]:
            metadata["message_types"][msg_type] = 0
        metadata["message_types"][msg_type] += 1
        
        # Sauvegarde
        self._save_timeline(interlocutor)
        
        print(f"📱 Message ajouté à la timeline de {interlocutor}")
    
    def _extract_content(self, message: Dict[str, Any]) -> str:
        """Extrait le contenu d'un message."""
        if isinstance(message, dict):
            return message.get("content", str(message))
        return str(message)
    
    def _save_timeline(self, interlocutor: str):
        """Sauvegarde la timeline d'un interlocuteur."""
        timeline_file = self.timeline_dir / f"{interlocutor}.json"
        with open(timeline_file, 'w', encoding='utf-8') as f:
            json.dump(self.timelines[interlocutor], f, indent=2, ensure_ascii=False)
    
    def get_timeline(self, interlocutor: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère la timeline d'un interlocuteur."""
        if interlocutor not in self.timelines:
            return []
        
        messages = self.timelines[interlocutor]["messages"]
        return messages[-limit:] if limit > 0 else messages
    
    def get_timeline_summary(self, interlocutor: str) -> Dict[str, Any]:
        """Récupère un résumé de la timeline d'un interlocuteur."""
        if interlocutor not in self.timelines:
            return {
                "interlocutor": interlocutor,
                "exists": False,
                "total_messages": 0,
                "last_activity": None
            }
        
        timeline = self.timelines[interlocutor]
        metadata = timeline["metadata"]
        
        return {
            "interlocutor": interlocutor,
            "exists": True,
            "total_messages": metadata["total_messages"],
            "last_activity": metadata["last_activity"],
            "message_types": metadata["message_types"],
            "created_at": timeline["created_at"]
        }
    
    def get_all_timelines_summary(self) -> Dict[str, Any]:
        """Récupère un résumé de toutes les timelines."""
        summaries = {}
        total_messages = 0
        
        for interlocutor, timeline in self.timelines.items():
            summary = self.get_timeline_summary(interlocutor)
            summaries[interlocutor] = summary
            total_messages += summary["total_messages"]
        
        return {
            "total_interlocutors": len(summaries),
            "total_messages": total_messages,
            "timelines": summaries
        }
    
    def search_messages(self, interlocutor: str, query: str) -> List[Dict[str, Any]]:
        """Recherche des messages dans une timeline."""
        messages = self.get_timeline(interlocutor)
        results = []
        
        query_lower = query.lower()
        
        for message in messages:
            content = message.get("content", "").lower()
            if query_lower in content:
                results.append(message)
        
        return results
    
    def get_message_context(self, interlocutor: str, message_id: str, context_size: int = 5) -> List[Dict[str, Any]]:
        """Récupère le contexte d'un message (messages avant/après)."""
        messages = self.get_timeline(interlocutor)
        
        # Recherche du message
        message_index = None
        for i, msg in enumerate(messages):
            if msg["id"] == message_id:
                message_index = i
                break
        
        if message_index is None:
            return []
        
        # Extraction du contexte
        start_index = max(0, message_index - context_size)
        end_index = min(len(messages), message_index + context_size + 1)
        
        return messages[start_index:end_index]
    
    def export_timeline(self, interlocutor: str, format: str = "json") -> str:
        """Exporte une timeline dans différents formats."""
        if interlocutor not in self.timelines:
            return ""
        
        timeline = self.timelines[interlocutor]
        
        if format == "json":
            return json.dumps(timeline, indent=2, ensure_ascii=False)
        elif format == "txt":
            return self._export_as_text(timeline)
        else:
            return json.dumps(timeline, indent=2, ensure_ascii=False)
    
    def _export_as_text(self, timeline: Dict[str, Any]) -> str:
        """Exporte une timeline au format texte."""
        lines = []
        lines.append(f"📱 Timeline de discussion: {timeline['interlocutor']}")
        lines.append(f"📅 Créée le: {timeline['created_at']}")
        lines.append(f"📊 Total messages: {timeline['metadata']['total_messages']}")
        lines.append("")
        lines.append("💬 Messages:")
        lines.append("")
        
        for message in timeline["messages"]:
            direction = "⬅️" if message["direction"] == "incoming" else "➡️"
            sender = "🕷️ Orchestrateur" if message["direction"] == "incoming" else "🎯 Alma"
            timestamp = message["timestamp"]
            content = message["content"][:100]
            
            lines.append(f"{direction} **{sender}** ({timestamp})")
            lines.append(f"   {content}")
            lines.append("")
        
        return "\n".join(lines)
    
    def cleanup_old_messages(self, interlocutor: str, days_to_keep: int = 30):
        """Nettoie les anciens messages d'une timeline."""
        if interlocutor not in self.timelines:
            return
        
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        messages = self.timelines[interlocutor]["messages"]
        
        # Filtrage des messages récents
        recent_messages = []
        for message in messages:
            message_date = datetime.fromisoformat(message["timestamp"])
            if message_date > cutoff_date:
                recent_messages.append(message)
        
        # Mise à jour
        self.timelines[interlocutor]["messages"] = recent_messages
        self.timelines[interlocutor]["metadata"]["total_messages"] = len(recent_messages)
        
        # Sauvegarde
        self._save_timeline(interlocutor)
        
        print(f"🧹 Nettoyage de la timeline {interlocutor}: {len(messages) - len(recent_messages)} messages supprimés") 