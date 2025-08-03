import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from queue import Queue, Empty


class UserRequestTemporalMemory:
    """Mémoire temporelle linéaire pour les requêtes utilisateurs avec thread parallèle."""
    
    def __init__(self, base_path: str, polling_interval: float = 1.0):
        self.base_path = Path(base_path)
        self.temporal_dir = self.base_path / "memory" / "user_requests"
        self.temporal_dir.mkdir(parents=True, exist_ok=True)
        
        # Stack linéaire des requêtes
        self.pending_requests = []  # Requêtes en attente
        self.processed_requests = []  # Requêtes traitées
        
        # Thread parallèle pour l'Orchestrateur
        self.orchestrator_thread = None
        self.orchestrator_running = False
        self.polling_interval = polling_interval
        
        # Communication thread-safe
        self.request_queue = Queue()
        self.orchestrator_queue = Queue()
        self.lock = threading.Lock()
        
        # Index temporel
        self.temporal_index = {
            "pending": [],
            "processed": [],
            "by_intention": {},
            "by_priority": {"critical": [], "high": [], "normal": [], "low": []}
        }
        
        # Chargement des données existantes
        self._load_temporal_data()
        
        # Démarrage du thread Orchestrateur
        self._start_orchestrator_thread()
    
    def _load_temporal_data(self):
        """Charge les données temporelles existantes."""
        pending_file = self.temporal_dir / "pending_requests.json"
        processed_file = self.temporal_dir / "processed_requests.json"
        
        if pending_file.exists():
            with open(pending_file, 'r', encoding='utf-8') as f:
                self.pending_requests = json.load(f)
        
        if processed_file.exists():
            with open(processed_file, 'r', encoding='utf-8') as f:
                self.processed_requests = json.load(f)
    
    def _save_temporal_data(self):
        """Sauvegarde les données temporelles."""
        pending_file = self.temporal_dir / "pending_requests.json"
        processed_file = self.temporal_dir / "processed_requests.json"
        
        with open(pending_file, 'w', encoding='utf-8') as f:
            json.dump(self.pending_requests, f, indent=2, ensure_ascii=False)
        
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump(self.processed_requests, f, indent=2, ensure_ascii=False)
    
    def _start_orchestrator_thread(self):
        """Démarre le thread parallèle de l'Orchestrateur."""
        self.orchestrator_running = True
        self.orchestrator_thread = threading.Thread(
            target=self._orchestrator_loop,
            daemon=True,
            name="OrchestratorThread"
        )
        self.orchestrator_thread.start()
        print(f"🚀 Thread Orchestrateur démarré (polling: {self.polling_interval}s)")
    
    def _orchestrator_loop(self):
        """Boucle principale du thread Orchestrateur."""
        while self.orchestrator_running:
            try:
                # Polling des requêtes en attente
                with self.lock:
                    if self.pending_requests:
                        batch = self._prepare_batch_for_orchestrator()
                        if batch:
                            self._send_to_orchestrator(batch)
                            self._mark_requests_as_processed(batch["requests"])
                
                # Traitement des messages de l'Orchestrateur
                try:
                    while True:
                        message = self.orchestrator_queue.get_nowait()
                        self._handle_orchestrator_message(message)
                except Empty:
                    pass
                
                # Attente avant prochain polling
                time.sleep(self.polling_interval)
                
            except Exception as e:
                print(f"❌ Erreur dans le thread Orchestrateur: {e}")
                time.sleep(self.polling_interval)
    
    def _prepare_batch_for_orchestrator(self) -> Optional[Dict[str, Any]]:
        """Prépare un batch de requêtes pour l'Orchestrateur."""
        if not self.pending_requests:
            return None
        
        # Sélection des requêtes par priorité (critical → high → normal → low)
        critical_priority = [req for req in self.pending_requests if req["priority"] == "critical"]
        high_priority = [req for req in self.pending_requests if req["priority"] == "high"]
        normal_priority = [req for req in self.pending_requests if req["priority"] == "normal"]
        low_priority = [req for req in self.pending_requests if req["priority"] == "low"]
        
        # Batch par priorité (critical en premier)
        batch_requests = critical_priority + high_priority + normal_priority + low_priority
        
        return {
            "type": "USER_REQUESTS_BATCH",
            "requests": batch_requests,
            "batch_size": len(batch_requests),
            "timestamp": datetime.now().isoformat(),
            "priorities": {
                "critical": len(critical_priority),
                "high": len(high_priority),
                "normal": len(normal_priority),
                "low": len(low_priority)
            }
        }
    
    def _mark_requests_as_processed(self, requests: List[Dict[str, Any]]):
        """Marque les requêtes comme traitées."""
        request_uuids = [req["uuid"] for req in requests]
        
        # Transition : en attente → traitées
        for request in self.pending_requests[:]:
            if request["uuid"] in request_uuids:
                request["status"] = "processed"
                request["processed_timestamp"] = datetime.now().isoformat()
                self.processed_requests.append(request)
                self.pending_requests.remove(request)
        
        # Sauvegarde
        self._save_temporal_data()
        
        print(f"✅ {len(requests)} requêtes marquées comme traitées")
    
    def _send_to_orchestrator(self, batch_message: Dict[str, Any]):
        """Envoie un batch de requêtes à l'Orchestrateur."""
        # Simulation de l'envoi vers l'Orchestrateur
        print(f"📤 Envoi batch vers Orchestrateur: {batch_message['batch_size']} requêtes")
        print(f"   Priorités: {batch_message['priorities']}")
        
        # Envoi vers l'Orchestrateur via la queue
        if hasattr(self, 'orchestrator_queue'):
            self.orchestrator_queue.put({
                "type": "USER_REQUESTS_BATCH",
                "batch": batch_message,
                "timestamp": datetime.now().isoformat()
            })
        
        # Dans l'implémentation réelle, ce sera via le système de communication
        # avec l'Orchestrateur qui tourne en parallèle
        pass
    
    def _handle_orchestrator_message(self, message: Dict[str, Any]):
        """Gère les messages de l'Orchestrateur."""
        message_type = message.get("type")
        
        if message_type == "REQUEST_PENDING_REQUESTS":
            # L'Orchestrateur demande les requêtes en attente
            with self.lock:
                pending_count = len(self.pending_requests)
                print(f"🎯 Orchestrateur demande requêtes en attente: {pending_count}")
        
        elif message_type == "REQUEST_PROCESSED":
            # L'Orchestrateur confirme le traitement
            request_uuid = message.get("request_uuid")
            print(f"✅ Orchestrateur confirme traitement: {request_uuid}")
    
    def add_user_request(self, request_text: str, request_type: str = "terminal", metadata: Dict = None):
        """Ajoute une requête utilisateur au stack temporel (thread-safe)."""
        import uuid
        
        request_entry = {
            "uuid": str(uuid.uuid4()),
            "text": request_text,
            "type": request_type,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "intention": self._analyze_intention(request_text),
            "priority": self._calculate_priority(request_text)
        }
        
        # Ajout thread-safe au stack en attente
        with self.lock:
            self.pending_requests.append(request_entry)
            self._index_request(request_entry)
            self._save_temporal_data()
        
        print(f"🕷️ Requête ajoutée au stack: {request_text[:50]}...")
        print(f"   Intention: {request_entry['intention']['type']} (priorité: {request_entry['priority']})")
    
    def _analyze_intention(self, request_text: str) -> Dict[str, Any]:
        """Analyse l'intention d'une requête."""
        text = request_text.lower()
        
        intention = {
            "type": "unknown",
            "confidence": 0.0,
            "keywords": [],
            "actions": []
        }
        
        # Analyse par mots-clés
        if any(word in text for word in ["debug", "bug", "erreur", "corriger", "fix"]):
            intention["type"] = "debugging"
            intention["confidence"] = 0.8
            intention["actions"] = ["analyze_code", "find_bugs", "suggest_fixes"]
        
        elif any(word in text for word in ["créer", "nouveau", "ajouter", "générer", "make"]):
            intention["type"] = "creation"
            intention["confidence"] = 0.7
            intention["actions"] = ["create_file", "generate_code", "setup_project"]
        
        elif any(word in text for word in ["test", "vérifier", "valider", "check"]):
            intention["type"] = "testing"
            intention["confidence"] = 0.6
            intention["actions"] = ["run_tests", "validate_code", "check_performance"]
        
        elif any(word in text for word in ["expliquer", "comment", "pourquoi", "explain"]):
            intention["type"] = "explanation"
            intention["confidence"] = 0.5
            intention["actions"] = ["explain_code", "document_function", "clarify_logic"]
        
        # Extraction de mots-clés
        intention["keywords"] = [word for word in text.split() if len(word) > 3]
        
        return intention
    
    def _calculate_priority(self, request_text: str) -> str:
        """Calcule la priorité d'une requête."""
        text = request_text.lower()
        
        # Commandes strictes (priorité critique)
        if any(word in text for word in ["exit", "stop", "kill", "emergency", "urgent", "critical"]):
            return "critical"
        
        # Priorité haute pour les commandes importantes
        if any(word in text for word in ["debug", "fix", "corriger", "erreur"]):
            return "high"
        
        # Priorité basse pour les requêtes d'information
        if any(word in text for word in ["explain", "what", "how", "info", "help"]):
            return "low"
        
        # Priorité normale par défaut
        return "normal"
    
    def _index_request(self, request_entry: Dict[str, Any]):
        """Indexe une requête dans l'index temporel."""
        # Indexation par intention
        intention_type = request_entry["intention"]["type"]
        if intention_type not in self.temporal_index["by_intention"]:
            self.temporal_index["by_intention"][intention_type] = []
        self.temporal_index["by_intention"][intention_type].append(request_entry["uuid"])
        
        # Indexation par priorité
        priority = request_entry["priority"]
        self.temporal_index["by_priority"][priority].append(request_entry["uuid"])
    
    def get_temporal_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques temporelles (thread-safe)."""
        with self.lock:
            return {
                "pending_count": len(self.pending_requests),
                "processed_count": len(self.processed_requests),
                "orchestrator_running": self.orchestrator_running,
                "polling_interval": self.polling_interval,
                "by_intention": {intent: len(uuids) for intent, uuids in self.temporal_index["by_intention"].items()},
                "by_priority": {priority: len(uuids) for priority, uuids in self.temporal_index["by_priority"].items()},
                "recent_processed": [req for req in self.processed_requests[-10:]]
            }
    
    def search_temporal_requests(self, query_type: str, query_value: str) -> List[Dict[str, Any]]:
        """Recherche dans les requêtes temporelles (thread-safe)."""
        with self.lock:
            results = []
            
            if query_type == "intention":
                uuids = self.temporal_index["by_intention"].get(query_value, [])
                results = [req for req in self.processed_requests if req["uuid"] in uuids]
            
            elif query_type == "priority":
                uuids = self.temporal_index["by_priority"].get(query_value, [])
                results = [req for req in self.processed_requests if req["uuid"] in uuids]
            
            elif query_type == "text":
                # Recherche textuelle
                results = [req for req in self.processed_requests if query_value.lower() in req["text"].lower()]
            
            return results
    
    def stop_orchestrator_thread(self):
        """Arrête le thread Orchestrateur."""
        self.orchestrator_running = False
        if self.orchestrator_thread and self.orchestrator_thread.is_alive():
            self.orchestrator_thread.join(timeout=5.0)
            print("🛑 Thread Orchestrateur arrêté")
    
    def __del__(self):
        """Destructeur pour arrêter le thread proprement."""
        self.stop_orchestrator_thread() 