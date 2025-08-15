"""
⛧ Temporal User Request Memory - Mémoire Temporelle des Requêtes Utilisateur ⛧

Mémoire temporelle des requêtes utilisateur refactorisée avec dimension temporelle universelle,
auto-amélioration et intégration native dans l'architecture temporelle.

Architecte Démoniaque : Alma⛧
Visionnaire : Lucie Defraiteur - Ma Reine Lucie
"""

import json
import asyncio
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from queue import Queue, Empty

from .temporal_base import (
    BaseTemporalEntity,
    register_temporal_entity,
    unregister_temporal_entity
)
from .temporal_memory_node import TemporalMemoryNode

class TemporalUserRequestMemory(BaseTemporalEntity):
    """
    ⛧ Mémoire Temporelle des Requêtes Utilisateur - Architecture Temporelle ⛧
    
    Mémoire temporelle des requêtes utilisateur avec dimension temporelle universelle,
    auto-amélioration et intégration native dans l'architecture temporelle.
    """
    
    def __init__(self, 
                 base_path: str, 
                 memory_engine=None,
                 polling_interval: float = 1.0,
                 auto_adapt: bool = True):
        """
        Initialise la mémoire temporelle des requêtes utilisateur.
        
        Args:
            base_path: Chemin de base pour le stockage
            memory_engine: Instance du moteur temporel
            polling_interval: Intervalle de polling pour l'orchestrateur
            auto_adapt: Active l'adaptation automatique
        """
        # Initialisation de la base temporelle
        super().__init__(
            entity_id=f"temporal_user_request_memory_{datetime.now().isoformat()}",
            entity_type="temporal_user_request_memory"
        )
        
        # Configuration du stockage
        self.base_path = Path(base_path)
        self.temporal_dir = self.base_path / "memory" / "temporal_user_requests"
        self.temporal_dir.mkdir(parents=True, exist_ok=True)
        
        # Référence au moteur temporel
        self.memory_engine = memory_engine
        
        # Configuration de l'adaptation
        self.auto_adapt = auto_adapt
        
        # Stack temporel des requêtes
        self.temporal_pending_requests = []  # Requêtes en attente temporelles
        self.temporal_processed_requests = []  # Requêtes traitées temporelles
        
        # Thread parallèle pour l'Orchestrateur temporel
        self.orchestrator_thread = None
        self.orchestrator_running = False
        self.polling_interval = polling_interval
        
        # Communication thread-safe temporelle
        self.request_queue = Queue()
        self.orchestrator_queue = Queue()
        self.lock = threading.Lock()
        
        # Index temporel unifié
        self.temporal_index = {
            "pending": [],
            "processed": [],
            "by_intention": {},
            "by_priority": {"critical": [], "high": [], "normal": [], "low": []},
            "by_consciousness_level": {}
        }
        
        # Chargement des données temporelles existantes
        self._load_temporal_data()
        
        # Démarrage du thread Orchestrateur temporel
        self._start_temporal_orchestrator_thread()
        
        # Enregistrement dans l'index temporel global
        register_temporal_entity(self)
        
        # Évolution initiale
        self.temporal_dimension.evolve("Initialisation de la mémoire temporelle des requêtes utilisateur")
    
    def _load_temporal_data(self):
        """Charge les données temporelles existantes."""
        pending_file = self.temporal_dir / "temporal_pending_requests.json"
        processed_file = self.temporal_dir / "temporal_processed_requests.json"
        
        if pending_file.exists():
            try:
                with open(pending_file, 'r', encoding='utf-8') as f:
                    self.temporal_pending_requests = json.load(f)
            except Exception as e:
                print(f"⛧ Erreur lors du chargement des requêtes en attente: {e}")
        
        if processed_file.exists():
            try:
                with open(processed_file, 'r', encoding='utf-8') as f:
                    self.temporal_processed_requests = json.load(f)
            except Exception as e:
                print(f"⛧ Erreur lors du chargement des requêtes traitées: {e}")
        
        # Migration vers le format temporel si nécessaire
        self._migrate_to_temporal_format()
    
    def _migrate_to_temporal_format(self):
        """Migre les données vers le format temporel."""
        # Migration des requêtes en attente
        for request in self.temporal_pending_requests:
            if "temporal_dimension" not in request:
                request["temporal_dimension"] = {
                    "created_at": request.get("timestamp", datetime.now().isoformat()),
                    "modified_at": request.get("timestamp", datetime.now().isoformat()),
                    "version": "1.0",
                    "evolution_history": ["Migration vers format temporel"],
                    "consciousness_level": "AWARE"
                }
        
        # Migration des requêtes traitées
        for request in self.temporal_processed_requests:
            if "temporal_dimension" not in request:
                request["temporal_dimension"] = {
                    "created_at": request.get("timestamp", datetime.now().isoformat()),
                    "modified_at": request.get("timestamp", datetime.now().isoformat()),
                    "version": "1.0",
                    "evolution_history": ["Migration vers format temporel"],
                    "consciousness_level": "AWARE"
                }
    
    def _save_temporal_data(self):
        """Sauvegarde les données temporelles."""
        pending_file = self.temporal_dir / "temporal_pending_requests.json"
        processed_file = self.temporal_dir / "temporal_processed_requests.json"
        
        try:
            with open(pending_file, 'w', encoding='utf-8') as f:
                json.dump(self.temporal_pending_requests, f, indent=2, ensure_ascii=False)
            
            with open(processed_file, 'w', encoding='utf-8') as f:
                json.dump(self.temporal_processed_requests, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⛧ Erreur lors de la sauvegarde des données temporelles: {e}")
    
    def _start_temporal_orchestrator_thread(self):
        """Démarre le thread parallèle de l'Orchestrateur temporel."""
        self.orchestrator_running = True
        self.orchestrator_thread = threading.Thread(
            target=self._temporal_orchestrator_loop,
            daemon=True,
            name="TemporalOrchestratorThread"
        )
        self.orchestrator_thread.start()
        print(f"🚀 Thread Orchestrateur Temporel démarré (polling: {self.polling_interval}s)")
    
    def _temporal_orchestrator_loop(self):
        """Boucle principale du thread Orchestrateur temporel."""
        while self.orchestrator_running:
            try:
                # Polling des requêtes en attente temporelles
                with self.lock:
                    if self.temporal_pending_requests:
                        batch = self._prepare_temporal_batch_for_orchestrator()
                        if batch:
                            self._send_to_temporal_orchestrator(batch)
                            self._mark_temporal_requests_as_processed(batch["requests"])
                
                # Traitement des messages de l'Orchestrateur temporel
                try:
                    while True:
                        message = self.orchestrator_queue.get_nowait()
                        self._handle_temporal_orchestrator_message(message)
                except Empty:
                    pass
                
                time.sleep(self.polling_interval)
                
            except Exception as e:
                print(f"⛧ Erreur dans la boucle Orchestrateur Temporel: {e}")
                time.sleep(self.polling_interval)
    
    def _prepare_temporal_batch_for_orchestrator(self) -> Optional[Dict[str, Any]]:
        """Prépare un batch temporel pour l'Orchestrateur."""
        if not self.temporal_pending_requests:
            return None
        
        # Sélection des requêtes prioritaires
        critical_requests = [r for r in self.temporal_pending_requests if r.get("priority") == "critical"]
        high_requests = [r for r in self.temporal_pending_requests if r.get("priority") == "high"]
        normal_requests = [r for r in self.temporal_pending_requests if r.get("priority") == "normal"]
        
        # Construction du batch temporel
        batch_requests = critical_requests[:5] + high_requests[:10] + normal_requests[:20]
        
        if not batch_requests:
            return None
        
        batch = {
            "batch_id": f"temporal_batch_{datetime.now().isoformat()}",
            "timestamp": datetime.now().isoformat(),
            "requests": batch_requests,
            "temporal_dimension": {
                "created_at": datetime.now().isoformat(),
                "modified_at": datetime.now().isoformat(),
                "version": "1.0",
                "evolution_history": ["Création du batch temporel"],
                "consciousness_level": "AWARE"
            }
        }
        
        return batch
    
    def _mark_temporal_requests_as_processed(self, requests: List[Dict[str, Any]]):
        """Marque les requêtes temporelles comme traitées."""
        request_ids = [r["id"] for r in requests]
        
        # Déplacement des requêtes vers traitées
        with self.lock:
            self.temporal_pending_requests = [
                r for r in self.temporal_pending_requests 
                if r["id"] not in request_ids
            ]
            
            for request in requests:
                request["processed_at"] = datetime.now().isoformat()
                request["temporal_dimension"]["modified_at"] = datetime.now().isoformat()
                request["temporal_dimension"]["evolution_history"].append("Marquée comme traitée")
                self.temporal_processed_requests.append(request)
        
        # Sauvegarde temporelle
        self._save_temporal_data()
    
    def _send_to_temporal_orchestrator(self, batch_message: Dict[str, Any]):
        """Envoie un batch temporel à l'Orchestrateur."""
        try:
            # Simulation d'envoi à l'Orchestrateur temporel
            print(f"⛧ Envoi du batch temporel {batch_message['batch_id']} à l'Orchestrateur")
            
            # Création d'un nœud de mémoire temporel pour le batch
            if self.memory_engine:
                asyncio.create_task(self._create_batch_memory_node(batch_message))
            
        except Exception as e:
            print(f"⛧ Erreur lors de l'envoi du batch temporel: {e}")
    
    async def _create_batch_memory_node(self, batch_message: Dict[str, Any]):
        """Crée un nœud de mémoire temporel pour le batch."""
        try:
            batch_content = f"Batch de {len(batch_message['requests'])} requêtes"
            batch_metadata = {
                "batch_id": batch_message["batch_id"],
                "requests_count": len(batch_message["requests"]),
                "priorities": {
                    "critical": len([r for r in batch_message["requests"] if r.get("priority") == "critical"]),
                    "high": len([r for r in batch_message["requests"] if r.get("priority") == "high"]),
                    "normal": len([r for r in batch_message["requests"] if r.get("priority") == "normal"])
                }
            }
            
            await self.memory_engine.create_temporal_memory(
                node_type="user_request_batch",
                content=batch_content,
                metadata=batch_metadata,
                keywords=["batch", "orchestrator", "user_requests"],
                strata="cognitive"
            )
        except Exception as e:
            print(f"⛧ Erreur lors de la création du nœud de mémoire batch: {e}")
    
    def _handle_temporal_orchestrator_message(self, message: Dict[str, Any]):
        """Gère les messages de l'Orchestrateur temporel."""
        try:
            message_type = message.get("type", "unknown")
            
            if message_type == "batch_processed":
                print(f"⛧ Batch temporel traité: {message.get('batch_id')}")
            elif message_type == "error":
                print(f"⛧ Erreur Orchestrateur Temporel: {message.get('error')}")
            else:
                print(f"⛧ Message Orchestrateur Temporel: {message}")
            
            # Apprentissage de l'interaction
            self.learn_from_interaction("orchestrator_message", {
                "message_type": message_type,
                "message": message
            })
            
        except Exception as e:
            print(f"⛧ Erreur lors du traitement du message Orchestrateur Temporel: {e}")
    
    async def add_temporal_user_request(self, 
                                      request_text: str, 
                                      request_type: str = "terminal", 
                                      metadata: Dict = None) -> str:
        """
        Ajoute une requête utilisateur temporelle.
        
        Args:
            request_text: Texte de la requête
            request_type: Type de requête (terminal, web, api, etc.)
            metadata: Métadonnées supplémentaires
        
        Returns:
            str: ID de la requête créée
        """
        request_id = f"temporal_request_{datetime.now().isoformat()}"
        
        # Analyse temporelle de l'intention
        intention_analysis = await self._analyze_temporal_intention(request_text)
        
        # Calcul temporel de la priorité
        priority = await self._calculate_temporal_priority(request_text, intention_analysis)
        
        # Création de l'entrée de requête temporelle
        request_entry = {
            "id": request_id,
            "timestamp": datetime.now().isoformat(),
            "request_text": request_text,
            "request_type": request_type,
            "intention": intention_analysis,
            "priority": priority,
            "metadata": metadata or {},
            "status": "pending",
            "temporal_dimension": {
                "created_at": datetime.now().isoformat(),
                "modified_at": datetime.now().isoformat(),
                "version": "1.0",
                "evolution_history": ["Création de la requête temporelle"],
                "consciousness_level": "AWARE"
            }
        }
        
        # Ajout à la liste des requêtes en attente
        with self.lock:
            self.temporal_pending_requests.append(request_entry)
        
        # Indexation temporelle
        await self._index_temporal_request(request_entry)
        
        # Création d'un nœud de mémoire temporel pour la requête
        if self.memory_engine:
            await self._create_request_memory_node(request_entry)
        
        # Sauvegarde temporelle
        self._save_temporal_data()
        
        # Évolution de la mémoire
        self.temporal_dimension.evolve(f"Ajout de requête utilisateur: {request_type}")
        
        # Apprentissage de l'interaction
        self.learn_from_interaction("user_request_added", {
            "request_type": request_type,
            "priority": priority,
            "intention": intention_analysis.get("primary_intention", "unknown")
        })
        
        print(f"⛧ Requête utilisateur temporelle ajoutée: {request_id}")
        return request_id
    
    async def _analyze_temporal_intention(self, request_text: str) -> Dict[str, Any]:
        """Analyse temporelle de l'intention de la requête."""
        # Analyse simple pour l'instant
        # TODO: Intégrer le système d'enrichissement et l'IA
        
        intentions = {
            "search": ["cherche", "trouve", "recherche", "search", "find"],
            "create": ["crée", "créer", "nouveau", "new", "create"],
            "modify": ["modifie", "change", "update", "modifier"],
            "delete": ["supprime", "delete", "remove", "efface"],
            "analyze": ["analyse", "analyze", "examine", "étudie"],
            "debug": ["debug", "corrige", "fix", "répare"]
        }
        
        request_lower = request_text.lower()
        detected_intentions = []
        
        for intention, keywords in intentions.items():
            if any(keyword in request_lower for keyword in keywords):
                detected_intentions.append(intention)
        
        primary_intention = detected_intentions[0] if detected_intentions else "unknown"
        
        return {
            "primary_intention": primary_intention,
            "detected_intentions": detected_intentions,
            "confidence": len(detected_intentions) / len(intentions) if detected_intentions else 0.0
        }
    
    async def _calculate_temporal_priority(self, request_text: str, intention_analysis: Dict[str, Any]) -> str:
        """Calcule la priorité temporelle de la requête."""
        # Logique de priorité temporelle
        # TODO: Améliorer avec l'IA et l'historique temporel
        
        primary_intention = intention_analysis.get("primary_intention", "unknown")
        confidence = intention_analysis.get("confidence", 0.0)
        
        # Priorités par intention
        critical_intentions = ["debug", "delete"]
        high_intentions = ["create", "modify"]
        normal_intentions = ["search", "analyze"]
        
        if primary_intention in critical_intentions:
            return "critical"
        elif primary_intention in high_intentions:
            return "high"
        elif primary_intention in normal_intentions:
            return "normal"
        else:
            return "low"
    
    async def _index_temporal_request(self, request_entry: Dict[str, Any]):
        """Indexe la requête temporelle."""
        # Indexation par intention
        primary_intention = request_entry["intention"]["primary_intention"]
        if primary_intention not in self.temporal_index["by_intention"]:
            self.temporal_index["by_intention"][primary_intention] = []
        self.temporal_index["by_intention"][primary_intention].append(request_entry["id"])
        
        # Indexation par priorité
        priority = request_entry["priority"]
        self.temporal_index["by_priority"][priority].append(request_entry["id"])
        
        # Indexation par niveau de conscience
        consciousness_level = request_entry["temporal_dimension"]["consciousness_level"]
        if consciousness_level not in self.temporal_index["by_consciousness_level"]:
            self.temporal_index["by_consciousness_level"][consciousness_level] = []
        self.temporal_index["by_consciousness_level"][consciousness_level].append(request_entry["id"])
    
    async def _create_request_memory_node(self, request_entry: Dict[str, Any]):
        """Crée un nœud de mémoire temporel pour la requête."""
        try:
            request_metadata = {
                "request_id": request_entry["id"],
                "request_type": request_entry["request_type"],
                "priority": request_entry["priority"],
                "intention": request_entry["intention"],
                "status": request_entry["status"],
                **(request_entry.get("metadata", {}))
            }
            
            await self.memory_engine.create_temporal_memory(
                node_type="user_request",
                content=request_entry["request_text"],
                metadata=request_metadata,
                keywords=[
                    request_entry["request_type"],
                    request_entry["priority"],
                    request_entry["intention"]["primary_intention"]
                ],
                strata="somatic"
            )
        except Exception as e:
            print(f"⛧ Erreur lors de la création du nœud de mémoire requête: {e}")
    
    async def get_temporal_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques temporelles."""
        stats = {
            "total_pending": len(self.temporal_pending_requests),
            "total_processed": len(self.temporal_processed_requests),
            "by_priority": {
                priority: len([r for r in self.temporal_pending_requests if r.get("priority") == priority])
                for priority in ["critical", "high", "normal", "low"]
            },
            "by_intention": {
                intention: len(ids) for intention, ids in self.temporal_index["by_intention"].items()
            },
            "temporal_dimension": self.temporal_dimension.to_dict(),
            "consciousness_level": self.consciousness_interface.consciousness_level.value
        }
        
        return stats
    
    async def search_temporal_requests(self, 
                                    query_type: str, 
                                    query_value: str) -> List[Dict[str, Any]]:
        """Recherche temporelle dans les requêtes."""
        results = []
        
        if query_type == "intention":
            request_ids = self.temporal_index["by_intention"].get(query_value, [])
            all_requests = self.temporal_pending_requests + self.temporal_processed_requests
            results = [r for r in all_requests if r["id"] in request_ids]
        
        elif query_type == "priority":
            request_ids = self.temporal_index["by_priority"].get(query_value, [])
            all_requests = self.temporal_pending_requests + self.temporal_processed_requests
            results = [r for r in all_requests if r["id"] in request_ids]
        
        elif query_type == "text":
            all_requests = self.temporal_pending_requests + self.temporal_processed_requests
            results = [
                r for r in all_requests 
                if query_value.lower() in r["request_text"].lower()
            ]
        
        # Apprentissage de l'interaction
        self.learn_from_interaction("request_search", {
            "query_type": query_type,
            "query_value": query_value,
            "results_count": len(results)
        })
        
        return results
    
    def stop_temporal_orchestrator_thread(self):
        """Arrête le thread Orchestrateur temporel."""
        self.orchestrator_running = False
        if self.orchestrator_thread:
            self.orchestrator_thread.join(timeout=5.0)
        print("⛧ Thread Orchestrateur Temporel arrêté")
    
    async def auto_improve_content(self) -> bool:
        """Auto-amélioration du contenu de la mémoire temporelle."""
        improved = await super().auto_improve_content()
        
        # Auto-amélioration des requêtes temporelles
        for request in self.temporal_pending_requests + self.temporal_processed_requests:
            if "temporal_dimension" in request:
                # Évolution temporelle des requêtes
                request["temporal_dimension"]["modified_at"] = datetime.now().isoformat()
                request["temporal_dimension"]["evolution_history"].append("Auto-amélioration")
        
        return improved
    
    def get_entity_specific_data(self) -> Dict[str, Any]:
        """Retourne les données spécifiques de la mémoire temporelle."""
        return {
            "base_path": str(self.base_path),
            "temporal_dir": str(self.temporal_dir),
            "pending_requests_count": len(self.temporal_pending_requests),
            "processed_requests_count": len(self.temporal_processed_requests),
            "orchestrator_running": self.orchestrator_running,
            "polling_interval": self.polling_interval,
            "memory_engine_connected": self.memory_engine is not None
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de la mémoire temporelle."""
        stats = {
            "memory_type": "TemporalUserRequestMemory",
            "temporal_dimension": self.temporal_dimension.to_dict(),
            "consciousness_level": self.consciousness_interface.consciousness_level.value,
            "pending_requests_count": len(self.temporal_pending_requests),
            "processed_requests_count": len(self.temporal_processed_requests),
            "orchestrator_running": self.orchestrator_running
        }
        
        # Statistiques par priorité
        priority_stats = {}
        for priority in ["critical", "high", "normal", "low"]:
            priority_stats[priority] = len([
                r for r in self.temporal_pending_requests 
                if r.get("priority") == priority
            ])
        
        stats["priority_stats"] = priority_stats
        
        return stats
    
    def __del__(self):
        """Destructeur pour arrêter le thread Orchestrateur temporel."""
        self.stop_temporal_orchestrator_thread() 