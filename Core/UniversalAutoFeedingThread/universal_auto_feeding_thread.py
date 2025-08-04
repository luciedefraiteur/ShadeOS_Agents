# ⛧ Créé par Alma, Architecte Démoniaque ⛧
# 🧱 UniversalAutoFeedingThread - Brique Basse Réutilisable

import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import deque

@dataclass
class AutoFeedMessage:
    """Message simple dans le thread auto-feed."""
    timestamp: float
    role: str  # "self", "user", "system", "workspace", "git", "memory"
    content: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class UniversalAutoFeedingThread:
    """Thread auto-feed universel simple et réutilisable."""
    
    def __init__(self, entity_id: str, entity_type: str, max_history: int = 100):
        """Initialise le thread auto-feed."""
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.max_history = max_history
        
        # Historique simple
        self.messages = deque(maxlen=max_history)
        self.session_start = time.time()
        
        # État du thread
        self.is_active = True
        self.current_context = ""
        
        # Log initial
        self.add_message("system", f"Thread auto-feed initialisé pour {entity_id} ({entity_type})")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> AutoFeedMessage:
        """Ajoute un message au thread."""
        if not self.is_active:
            return None
        
        message = AutoFeedMessage(
            timestamp=time.time(),
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        self.messages.append(message)
        return message
    
    def add_self_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> AutoFeedMessage:
        """Ajoute un message de l'entité elle-même."""
        return self.add_message("self", content, metadata)
    
    def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> AutoFeedMessage:
        """Ajoute un message utilisateur."""
        return self.add_message("user", content, metadata)
    
    def add_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> AutoFeedMessage:
        """Ajoute un message système."""
        return self.add_message("system", content, metadata)
    
    def get_recent_messages(self, count: int = 5) -> List[AutoFeedMessage]:
        """Récupère les messages récents."""
        return list(self.messages)[-count:]
    
    def get_messages_by_role(self, role: str) -> List[AutoFeedMessage]:
        """Récupère tous les messages d'un rôle spécifique."""
        return [msg for msg in self.messages if msg.role == role]
    
    def get_context_summary(self, max_messages: int = 10) -> str:
        """Génère un résumé du contexte pour les prompts."""
        if not self.messages:
            return "Aucun historique disponible."
        
        recent_messages = self.get_recent_messages(max_messages)
        context_lines = [f"HISTORIQUE DU THREAD ({self.entity_id}):"]
        
        for msg in recent_messages:
            context_lines.append(f"[{msg.role.upper()}] {msg.content}")
        
        return "\n".join(context_lines)
    
    def get_thread_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du thread."""
        if not self.messages:
            return {
                "total_messages": 0,
                "duration": 0,
                "roles": {},
                "is_active": self.is_active
            }
        
        roles = {}
        for msg in self.messages:
            roles[msg.role] = roles.get(msg.role, 0) + 1
        
        return {
            "total_messages": len(self.messages),
            "duration": time.time() - self.session_start,
            "roles": roles,
            "is_active": self.is_active,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type
        }
    
    def save_to_file(self, filepath: str) -> bool:
        """Sauvegarde le thread dans un fichier."""
        try:
            data = {
                "entity_id": self.entity_id,
                "entity_type": self.entity_type,
                "session_start": self.session_start,
                "is_active": self.is_active,
                "messages": [asdict(msg) for msg in self.messages],
                "stats": self.get_thread_stats()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Erreur sauvegarde thread: {e}")
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """Charge le thread depuis un fichier."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.entity_id = data.get("entity_id", self.entity_id)
            self.entity_type = data.get("entity_type", self.entity_type)
            self.session_start = data.get("session_start", self.session_start)
            self.is_active = data.get("is_active", True)
            
            # Charger les messages
            self.messages.clear()
            for msg_data in data.get("messages", []):
                message = AutoFeedMessage(
                    timestamp=msg_data["timestamp"],
                    role=msg_data["role"],
                    content=msg_data["content"],
                    metadata=msg_data.get("metadata", {})
                )
                self.messages.append(message)
            
            return True
        except Exception as e:
            print(f"Erreur chargement thread: {e}")
            return False
    
    def clear_history(self):
        """Efface l'historique du thread."""
        self.messages.clear()
        self.add_message("system", "Historique effacé")
    
    def pause(self):
        """Met le thread en pause."""
        self.is_active = False
        self.add_message("system", "Thread mis en pause")
    
    def resume(self):
        """Reprend le thread."""
        self.is_active = True
        self.add_message("system", "Thread repris")
    
    def __str__(self) -> str:
        """Représentation string du thread."""
        stats = self.get_thread_stats()
        return f"UniversalAutoFeedingThread({self.entity_id}, {stats['total_messages']} messages, {'actif' if self.is_active else 'en pause'})"
    
    def __repr__(self) -> str:
        return self.__str__()


# Fonction utilitaire pour créer un thread
def create_auto_feeding_thread(entity_id: str, entity_type: str, max_history: int = 100) -> UniversalAutoFeedingThread:
    """Crée un nouveau thread auto-feed."""
    return UniversalAutoFeedingThread(entity_id, entity_type, max_history)


# Test simple
if __name__ == "__main__":
    # Test du thread auto-feed
    thread = create_auto_feeding_thread("test_agent", "assistant")
    
    # Ajouter quelques messages
    thread.add_user_message("Peux-tu analyser ce code ?")
    thread.add_self_message("Je vais commencer par examiner la structure du projet")
    thread.add_self_message("J'ai trouvé 3 fichiers Python à analyser")
    thread.add_system_message("WorkspaceLayer activé")
    thread.add_self_message("Analyse terminée, 2 bugs détectés")
    
    # Afficher le contexte
    print("=== CONTEXTE DU THREAD ===")
    print(thread.get_context_summary())
    
    # Afficher les stats
    print("\n=== STATISTIQUES ===")
    stats = thread.get_thread_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print(f"\n{thread}") 