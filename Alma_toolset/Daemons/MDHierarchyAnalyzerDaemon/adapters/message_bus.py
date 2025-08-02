#!/usr/bin/env python3
"""
📡 Message Bus System

Système de bus de messages pour communication inter-composants
avec protocoles standardisés, gestion d'erreurs et monitoring.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import json
import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict
from enum import Enum


class MessageType(Enum):
    """Types de messages."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class Priority(Enum):
    """Priorités de messages."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Message:
    """Structure de message standardisée."""
    
    protocol_version: str = "1.0"
    message_id: str = ""
    timestamp: str = ""
    source: str = ""
    target: str = ""
    message_type: MessageType = MessageType.REQUEST
    method: str = ""
    params: Dict[str, Any] = None
    result: Dict[str, Any] = None
    error: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.params is None:
            self.params = {}
        if self.result is None:
            self.result = {}
        if self.error is None:
            self.error = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ProtocolMetrics:
    """Métriques de protocole."""
    
    messages_sent: int = 0
    messages_received: int = 0
    errors_count: int = 0
    total_response_time: float = 0.0
    active_requests: int = 0
    retry_count: int = 0
    
    @property
    def average_response_time(self) -> float:
        """Temps de réponse moyen."""
        if self.messages_sent == 0:
            return 0.0
        return self.total_response_time / self.messages_sent


class ProtocolError(Exception):
    """Erreur de protocole standardisée."""
    
    def __init__(self, code: int, message: str, data: Dict[str, Any] = None):
        self.code = code
        self.message = message
        self.data = data or {}
        super().__init__(f"Protocol Error {code}: {message}")


# Codes d'erreur standardisés
ERROR_CODES = {
    1000: "Generic Protocol Error",
    1001: "Content Detection Error", 
    1002: "AI Analysis Error",
    1003: "Memory Operation Error",
    1004: "Partitioning Error",
    1005: "Communication Timeout",
    1006: "Invalid Message Format",
    1007: "Component Unavailable",
    1008: "Method Not Found",
    1009: "Invalid Parameters"
}


class MessageBus:
    """Bus de messages centralisé."""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_queue = asyncio.Queue()
        self.active_requests: Dict[str, asyncio.Future] = {}
        self.metrics: Dict[str, ProtocolMetrics] = defaultdict(ProtocolMetrics)
        self.message_log: List[Message] = []
        self.running = False
        
        print("📡 MessageBus initialized")
    
    async def start(self):
        """Démarre le bus de messages."""
        self.running = True
        print("📡 MessageBus started")
        
        # Démarrage du processeur de messages
        asyncio.create_task(self._process_messages())
    
    async def stop(self):
        """Arrête le bus de messages."""
        self.running = False
        print("📡 MessageBus stopped")
    
    async def send_request(self, target: str, method: str, params: Dict[str, Any], 
                          timeout: float = 30.0, priority: Priority = Priority.MEDIUM) -> Dict[str, Any]:
        """Envoie une requête et attend la réponse."""
        
        message = Message(
            source="message_bus",
            target=target,
            message_type=MessageType.REQUEST,
            method=method,
            params=params,
            metadata={
                "priority": priority.value,
                "timeout": timeout,
                "correlation_id": str(uuid.uuid4())
            }
        )
        
        # Création du Future pour la réponse
        response_future = asyncio.Future()
        self.active_requests[message.message_id] = response_future
        
        # Envoi du message
        await self._send_message(message)
        
        try:
            # Attente de la réponse avec timeout
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            # Nettoyage en cas de timeout
            self.active_requests.pop(message.message_id, None)
            self._record_error(target, 1005, "Communication Timeout")
            raise ProtocolError(1005, f"Request to {target}.{method} timed out")
        finally:
            self.active_requests.pop(message.message_id, None)
    
    async def send_notification(self, target: str, method: str, params: Dict[str, Any],
                              priority: Priority = Priority.MEDIUM):
        """Envoie une notification sans attendre de réponse."""
        
        message = Message(
            source="message_bus",
            target=target,
            message_type=MessageType.NOTIFICATION,
            method=method,
            params=params,
            metadata={
                "priority": priority.value,
                "correlation_id": str(uuid.uuid4())
            }
        )
        
        await self._send_message(message)
    
    async def send_response(self, original_message: Message, result: Dict[str, Any]):
        """Envoie une réponse à une requête."""
        
        response = Message(
            source=original_message.target,
            target=original_message.source,
            message_type=MessageType.RESPONSE,
            method=original_message.method,
            result=result,
            metadata={
                "correlation_id": original_message.metadata.get("correlation_id"),
                "original_message_id": original_message.message_id
            }
        )
        
        # Si c'est une réponse à une requête active, résoudre le Future
        if original_message.message_id in self.active_requests:
            future = self.active_requests[original_message.message_id]
            if not future.done():
                future.set_result(result)
        
        await self._send_message(response)
    
    async def send_error(self, original_message: Message, error_code: int, error_message: str, 
                        error_data: Dict[str, Any] = None):
        """Envoie une erreur en réponse à une requête."""
        
        error_response = Message(
            source=original_message.target,
            target=original_message.source,
            message_type=MessageType.ERROR,
            method=original_message.method,
            error={
                "code": error_code,
                "message": error_message,
                "data": error_data or {}
            },
            metadata={
                "correlation_id": original_message.metadata.get("correlation_id"),
                "original_message_id": original_message.message_id
            }
        )
        
        # Si c'est une réponse à une requête active, rejeter le Future
        if original_message.message_id in self.active_requests:
            future = self.active_requests[original_message.message_id]
            if not future.done():
                future.set_exception(ProtocolError(error_code, error_message, error_data))
        
        await self._send_message(error_response)
    
    def subscribe(self, component: str, handler: Callable):
        """Abonne un composant aux messages."""
        self.subscribers[component].append(handler)
        print(f"📡 Component {component} subscribed to MessageBus")
    
    def unsubscribe(self, component: str, handler: Callable):
        """Désabonne un composant."""
        if component in self.subscribers:
            self.subscribers[component].remove(handler)
            print(f"📡 Component {component} unsubscribed from MessageBus")
    
    async def _send_message(self, message: Message):
        """Envoie un message dans la queue."""
        await self.message_queue.put(message)
        self._record_message_sent(message.target)
        self._log_message(message)
    
    async def _process_messages(self):
        """Traite les messages en continu."""
        while self.running:
            try:
                # Récupération du message avec timeout
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                # Traitement du message
                await self._handle_message(message)
                
            except asyncio.TimeoutError:
                # Timeout normal, continue la boucle
                continue
            except Exception as e:
                print(f"📡 Error processing message: {e}")
    
    async def _handle_message(self, message: Message):
        """Traite un message reçu."""
        
        start_time = time.time()
        
        try:
            # Recherche des handlers pour le composant cible
            if message.target in self.subscribers:
                handlers = self.subscribers[message.target]
                
                if handlers:
                    # Appel du premier handler disponible
                    handler = handlers[0]
                    await handler(message)
                    
                    self._record_message_received(message.target)
                else:
                    # Aucun handler disponible
                    if message.message_type == MessageType.REQUEST:
                        await self.send_error(message, 1007, f"Component {message.target} unavailable")
            else:
                # Composant non trouvé
                if message.message_type == MessageType.REQUEST:
                    await self.send_error(message, 1007, f"Component {message.target} not found")
        
        except Exception as e:
            # Erreur lors du traitement
            if message.message_type == MessageType.REQUEST:
                await self.send_error(message, 1000, f"Message processing error: {e}")
            
            self._record_error(message.target, 1000, str(e))
        
        finally:
            # Enregistrement du temps de traitement
            processing_time = time.time() - start_time
            self._record_response_time(message.target, processing_time)
    
    def _record_message_sent(self, target: str):
        """Enregistre l'envoi d'un message."""
        self.metrics[target].messages_sent += 1
    
    def _record_message_received(self, target: str):
        """Enregistre la réception d'un message."""
        self.metrics[target].messages_received += 1
    
    def _record_error(self, target: str, error_code: int, error_message: str):
        """Enregistre une erreur."""
        self.metrics[target].errors_count += 1
        print(f"📡 Protocol Error {error_code} for {target}: {error_message}")
    
    def _record_response_time(self, target: str, response_time: float):
        """Enregistre le temps de réponse."""
        self.metrics[target].total_response_time += response_time
    
    def _log_message(self, message: Message):
        """Log un message pour debugging."""
        self.message_log.append(message)
        
        # Limite la taille du log
        if len(self.message_log) > 1000:
            self.message_log = self.message_log[-500:]
    
    def get_metrics(self, component: str = None) -> Dict[str, ProtocolMetrics]:
        """Retourne les métriques."""
        if component:
            return {component: self.metrics[component]}
        return dict(self.metrics)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Retourne le statut de santé du bus."""
        total_messages = sum(m.messages_sent + m.messages_received for m in self.metrics.values())
        total_errors = sum(m.errors_count for m in self.metrics.values())
        
        return {
            "status": "healthy" if total_errors / max(1, total_messages) < 0.1 else "degraded",
            "total_messages": total_messages,
            "total_errors": total_errors,
            "active_requests": len(self.active_requests),
            "connected_components": len(self.subscribers),
            "queue_size": self.message_queue.qsize()
        }


class MessageHandler:
    """Gestionnaire de messages pour un composant."""
    
    def __init__(self, component_name: str, message_bus: MessageBus):
        self.component_name = component_name
        self.message_bus = message_bus
        self.handlers: Dict[str, Callable] = {}
        
        # Abonnement au bus
        self.message_bus.subscribe(component_name, self._handle_message)
        
        # Handlers par défaut
        self.register_handler("health_check", self._handle_health_check)
        self.register_handler("get_metrics", self._handle_get_metrics)
        
        print(f"📡 MessageHandler for {component_name} initialized")
    
    def register_handler(self, method: str, handler: Callable):
        """Enregistre un handler pour une méthode."""
        self.handlers[method] = handler
        print(f"📡 Handler registered: {self.component_name}.{method}")
    
    async def _handle_message(self, message: Message):
        """Traite un message reçu."""
        
        try:
            if message.method in self.handlers:
                handler = self.handlers[message.method]
                
                if message.message_type == MessageType.REQUEST:
                    # Appel du handler et envoi de la réponse
                    result = await handler(message.params)
                    await self.message_bus.send_response(message, result)
                    
                elif message.message_type == MessageType.NOTIFICATION:
                    # Appel du handler sans réponse
                    await handler(message.params)
            else:
                # Méthode non trouvée
                if message.message_type == MessageType.REQUEST:
                    await self.message_bus.send_error(
                        message, 1008, f"Method {message.method} not found"
                    )
        
        except Exception as e:
            # Erreur lors de l'exécution du handler
            if message.message_type == MessageType.REQUEST:
                await self.message_bus.send_error(
                    message, 1000, f"Handler error: {e}"
                )
    
    async def _handle_health_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handler de health check par défaut."""
        return {
            "component": self.component_name,
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "registered_methods": list(self.handlers.keys())
        }
    
    async def _handle_get_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handler de métriques par défaut."""
        metrics = self.message_bus.get_metrics(self.component_name)
        return {
            "component": self.component_name,
            "metrics": {k: asdict(v) for k, v in metrics.items()}
        }


async def test_message_bus():
    """Test du système de bus de messages."""
    
    print("📡 Testing Message Bus System...")
    
    # Création du bus
    bus = MessageBus()
    await bus.start()
    
    # Création d'un composant de test
    test_handler = MessageHandler("test_component", bus)
    
    # Enregistrement d'un handler de test
    async def echo_handler(params: Dict[str, Any]) -> Dict[str, Any]:
        return {"echo": params.get("message", "no message")}
    
    test_handler.register_handler("echo", echo_handler)
    
    # Test de requête
    try:
        result = await bus.send_request("test_component", "echo", {"message": "Hello World!"})
        print(f"📡 Echo result: {result}")
        
        # Test de health check
        health = await bus.send_request("test_component", "health_check", {})
        print(f"📡 Health check: {health}")
        
        # Test de métriques
        metrics = await bus.send_request("test_component", "get_metrics", {})
        print(f"📡 Metrics: {metrics}")
        
    except ProtocolError as e:
        print(f"📡 Protocol error: {e}")
    
    # Statut du bus
    status = bus.get_health_status()
    print(f"📡 Bus status: {status}")
    
    await bus.stop()


if __name__ == "__main__":
    asyncio.run(test_message_bus())
