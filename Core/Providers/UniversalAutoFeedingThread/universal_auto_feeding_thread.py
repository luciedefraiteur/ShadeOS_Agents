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

class UniversalAutoFeedingThreadLogger:
    """Logger universel pour tous les types de threads auto-feed."""
    
    def __init__(self, thread_type: str, entity_id: str):
        self.thread_type = thread_type  # "legion", "v9", "general", etc.
        self.entity_id = entity_id
        self.session_id = f"session_{int(time.time())}"
        
        # Répertoire de logs classé par type de thread
        self.log_dir = Path(f"logs/auto_feeding_threads/{thread_type}/{time.strftime('%Y%m%d')}")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichiers de log spécifiques au type de thread
        self.thread_log = self.log_dir / f"{self.session_id}_thread.jsonl"
        self.prompt_log = self.log_dir / f"{self.session_id}_prompts.jsonl"
        self.response_log = self.log_dir / f"{self.session_id}_responses.jsonl"
        self.debug_log = self.log_dir / f"{self.session_id}_debug.jsonl"
        
        # Données de session
        self.thread_messages = []
        self.prompts = []
        self.responses = []
        self.debug_actions = []
        
        # Log initial
        self.log_debug_action("initialization", {
            "thread_type": thread_type,
            "entity_id": entity_id,
            "session_id": self.session_id
        })
    
    def log_thread_message(self, message: AutoFeedMessage):
        """Enregistre un message du thread."""
        self.thread_messages.append(message)
        
        entry = {
            "timestamp": message.timestamp,
            "role": message.role,
            "content": message.content,
            "metadata": message.metadata or {},
            "thread_type": self.thread_type,
            "entity_id": self.entity_id
        }
        
        with open(self.thread_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def log_prompt(self, prompt: str, user_input: str, metadata: Dict[str, Any] = None):
        """Enregistre un prompt envoyé au LLM."""
        entry = {
            "timestamp": time.time(),
            "prompt": prompt,
            "user_input": user_input,
            "metadata": metadata or {},
            "thread_type": self.thread_type,
            "entity_id": self.entity_id,
            "prompt_length": len(prompt)
        }
        self.prompts.append(entry)
        
        with open(self.prompt_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def log_response(self, response: str, prompt_length: int, metadata: Dict[str, Any] = None):
        """Enregistre une réponse du LLM."""
        entry = {
            "timestamp": time.time(),
            "response": response,
            "response_length": len(response),
            "prompt_length": prompt_length,
            "metadata": metadata or {},
            "thread_type": self.thread_type,
            "entity_id": self.entity_id
        }
        self.responses.append(entry)
        
        with open(self.response_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def log_debug_action(self, action: str, details: Dict[str, Any]):
        """Enregistre une action de debug."""
        entry = {
            "timestamp": time.time(),
            "action": action,
            "details": details,
            "thread_type": self.thread_type,
            "entity_id": self.entity_id
        }
        self.debug_actions.append(entry)
        
        with open(self.debug_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def save_session_summary(self):
        """Sauvegarde un résumé de la session."""
        summary = {
            "session_id": self.session_id,
            "thread_type": self.thread_type,
            "entity_id": self.entity_id,
            "total_thread_messages": len(self.thread_messages),
            "total_prompts": len(self.prompts),
            "total_responses": len(self.responses),
            "total_debug_actions": len(self.debug_actions),
            "duration": time.time() - float(self.thread_messages[0].timestamp) if self.thread_messages else 0,
            "log_files": {
                "thread": str(self.thread_log),
                "prompts": str(self.prompt_log),
                "responses": str(self.response_log),
                "debug": str(self.debug_log)
            }
        }
        
        summary_file = self.log_dir / f"{self.session_id}_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return summary

class UniversalAutoFeedingThread:
    """Thread auto-feed universel simple et réutilisable avec logging intégré."""
    
    def __init__(self, entity_id: str, entity_type: str, max_history: int = 100, enable_logging: bool = True):
        """Initialise le thread auto-feed."""
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.max_history = max_history
        self.enable_logging = enable_logging
        
        # Historique simple
        self.messages = deque(maxlen=max_history)
        self.session_start = time.time()
        
        # État du thread
        self.is_active = True
        self.current_context = ""
        
        # Logger intégré
        self.logger = None
        if self.enable_logging:
            try:
                self.logger = UniversalAutoFeedingThreadLogger(entity_type, entity_id)
                self.logger.log_debug_action("thread_initialized", {
                    "max_history": max_history,
                    "enable_logging": enable_logging
                })
            except Exception as e:
                print(f"⚠️ Erreur initialisation logger: {e}")
        
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
        
        # Logging automatique
        if self.logger:
            try:
                self.logger.log_thread_message(message)
            except Exception as e:
                print(f"⚠️ Erreur logging message: {e}")
        
        return message
    
    def log_prompt(self, prompt: str, user_input: str, metadata: Dict[str, Any] = None):
        """Log un prompt envoyé au LLM."""
        if self.logger:
            try:
                self.logger.log_prompt(prompt, user_input, metadata)
            except Exception as e:
                print(f"⚠️ Erreur logging prompt: {e}")
    
    def log_response(self, response: str, prompt_length: int, metadata: Dict[str, Any] = None):
        """Log une réponse du LLM."""
        if self.logger:
            try:
                self.logger.log_response(response, prompt_length, metadata)
            except Exception as e:
                print(f"⚠️ Erreur logging response: {e}")
    
    def log_debug_action(self, action: str, details: Dict[str, Any]):
        """Log une action de debug."""
        if self.logger:
            try:
                self.logger.log_debug_action(action, details)
            except Exception as e:
                print(f"⚠️ Erreur logging debug: {e}")
    
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
        
        stats = {
            "total_messages": len(self.messages),
            "duration": time.time() - self.session_start,
            "roles": roles,
            "is_active": self.is_active,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type
        }
        
        # Ajouter les stats du logger si disponible
        if self.logger:
            try:
                logger_summary = self.logger.save_session_summary()
                stats["logger_summary"] = logger_summary
            except Exception as e:
                stats["logger_error"] = str(e)
        
        return stats
    
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
def create_auto_feeding_thread(entity_id: str, entity_type: str, max_history: int = 100, enable_logging: bool = True) -> UniversalAutoFeedingThread:
    """Crée un nouveau thread auto-feed."""
    return UniversalAutoFeedingThread(entity_id, entity_type, max_history, enable_logging)


# Test simple
if __name__ == "__main__":
    # Test du thread auto-feed avec logging
    thread = create_auto_feeding_thread("test_agent", "assistant", enable_logging=True)
    
    # Ajouter quelques messages
    thread.add_user_message("Peux-tu analyser ce code ?")
    thread.add_self_message("Je vais commencer par examiner la structure du projet")
    thread.add_self_message("J'ai trouvé 3 fichiers Python à analyser")
    thread.add_system_message("WorkspaceLayer activé")
    thread.add_self_message("Analyse terminée, 2 bugs détectés")
    
    # Tester le logging de prompt/réponse
    test_prompt = "Analyse ce code Python"
    test_response = "J'ai analysé le code et trouvé 2 bugs"
    thread.log_prompt(test_prompt, "Analyse code", {"test": True})
    thread.log_response(test_response, len(test_prompt), {"test": True})
    
    # Afficher le contexte
    print("=== CONTEXTE DU THREAD ===")
    print(thread.get_context_summary())
    
    # Afficher les stats
    print("\n=== STATISTIQUES ===")
    stats = thread.get_thread_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print(f"\n{thread}") 