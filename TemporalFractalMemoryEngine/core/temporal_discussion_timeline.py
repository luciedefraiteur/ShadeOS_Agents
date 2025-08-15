"""
⛧ Temporal Discussion Timeline - Timeline de Discussions Temporelle ⛧

Timeline de discussions refactorisée avec dimension temporelle universelle,
auto-amélioration et intégration native dans l'architecture temporelle.

Architecte Démoniaque : Alma⛧
Visionnaire : Lucie Defraiteur - Ma Reine Lucie
"""

import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from .temporal_base import (
    BaseTemporalEntity,
    register_temporal_entity,
    unregister_temporal_entity
)
from .temporal_memory_node import TemporalMemoryNode

class TemporalDiscussionTimeline(BaseTemporalEntity):
    """
    ⛧ Timeline de Discussions Temporelle - WhatsApp-style avec Dimension Temporelle ⛧
    
    Timeline de discussions avec dimension temporelle universelle,
    auto-amélioration et intégration native dans l'architecture temporelle.
    """
    
    def __init__(self, base_path: str, memory_engine=None, auto_adapt: bool = True):
        """
        Initialise la timeline de discussions temporelle.
        
        Args:
            base_path: Chemin de base pour le stockage
            memory_engine: Instance du moteur temporel
            auto_adapt: Active l'adaptation automatique
        """
        # Initialisation de la base temporelle
        super().__init__(
            entity_id=f"temporal_discussion_timeline_{datetime.now().isoformat()}",
            entity_type="temporal_discussion_timeline"
        )
        
        # Configuration du stockage
        self.base_path = Path(base_path)
        self.timeline_dir = self.base_path / "memory" / "temporal_discussion_timelines"
        self.timeline_dir.mkdir(parents=True, exist_ok=True)
        
        # Référence au moteur temporel
        self.memory_engine = memory_engine
        
        # Configuration de l'adaptation
        self.auto_adapt = auto_adapt
        
        # Timelines par interlocuteur (temporelles)
        self.temporal_timelines = {}
        
        # Chargement des timelines existantes
        self._load_temporal_timelines()
        
        # Enregistrement dans l'index temporel global
        register_temporal_entity(self)
        
        # Évolution initiale
        self.temporal_dimension.evolve("Initialisation de la timeline de discussions temporelle")
    
    def _load_temporal_timelines(self):
        """Charge toutes les timelines temporelles existantes."""
        for timeline_file in self.timeline_dir.glob("*.json"):
            interlocutor = timeline_file.stem
            try:
                with open(timeline_file, 'r', encoding='utf-8') as f:
                    timeline_data = json.load(f)
                    
                # Création d'une timeline temporelle
                temporal_timeline = TemporalTimeline(
                    interlocutor=interlocutor,
                    timeline_data=timeline_data,
                    memory_engine=self.memory_engine
                )
                
                self.temporal_timelines[interlocutor] = temporal_timeline
                
                # Enregistrement dans l'index temporel
                register_temporal_entity(temporal_timeline)
                
            except Exception as e:
                print(f"⛧ Erreur lors du chargement de la timeline {interlocutor}: {e}")
    
    async def add_temporal_message(self, 
                                 interlocutor: str, 
                                 message: Any, 
                                 direction: str = "incoming",
                                 metadata: Dict[str, Any] = None) -> str:
        """
        Ajoute un message temporel à la timeline d'un interlocuteur.
        
        Args:
            interlocutor: Nom de l'interlocuteur
            message: Message à ajouter
            direction: Direction du message (incoming/outgoing)
            metadata: Métadonnées supplémentaires
        
        Returns:
            str: ID du message créé
        """
        # Création ou récupération de la timeline temporelle
        if interlocutor not in self.temporal_timelines:
            temporal_timeline = TemporalTimeline(
                interlocutor=interlocutor,
                memory_engine=self.memory_engine
            )
            self.temporal_timelines[interlocutor] = temporal_timeline
            register_temporal_entity(temporal_timeline)
        
        # Ajout du message temporel
        message_id = await self.temporal_timelines[interlocutor].add_temporal_message(
            message, direction, metadata
        )
        
        # Création d'un nœud de mémoire temporel pour le message
        if self.memory_engine:
            await self._create_message_memory_node(interlocutor, message, direction, metadata)
        
        # Évolution de la timeline
        self.temporal_dimension.evolve(f"Ajout de message pour {interlocutor}")
        
        # Apprentissage de l'interaction
        self.learn_from_interaction("message_added", {
            "interlocutor": interlocutor,
            "direction": direction,
            "message_type": self._extract_message_type(message)
        })
        
        return message_id
    
    async def _create_message_memory_node(self, interlocutor: str, message: Any, direction: str, metadata: Dict[str, Any]):
        """Crée un nœud de mémoire temporel pour le message."""
        try:
            content = self._extract_content(message)
            message_metadata = {
                "interlocutor": interlocutor,
                "direction": direction,
                "message_type": self._extract_message_type(message),
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            await self.memory_engine.create_temporal_memory(
                node_type="discussion_message",
                content=content,
                metadata=message_metadata,
                keywords=[interlocutor, direction, self._extract_message_type(message)],
                strata="somatic"
            )
        except Exception as e:
            print(f"⛧ Erreur lors de la création du nœud de mémoire: {e}")
    
    def _extract_content(self, message: Any) -> str:
        """Extrait le contenu d'un message."""
        if isinstance(message, dict):
            return message.get("content", str(message))
        return str(message)
    
    def _extract_message_type(self, message: Any) -> str:
        """Extrait le type d'un message."""
        if isinstance(message, dict):
            return message.get("type", "message")
        return "message"
    
    async def get_temporal_timeline(self, interlocutor: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère la timeline temporelle d'un interlocuteur."""
        if interlocutor not in self.temporal_timelines:
            return []
        
        timeline = self.temporal_timelines[interlocutor]
        messages = await timeline.get_temporal_messages(limit)
        
        # Mise à jour de l'accès temporel
        timeline.access_layer()
        
        return messages
    
    async def get_temporal_timeline_summary(self, interlocutor: str) -> Dict[str, Any]:
        """Récupère un résumé temporel de la timeline d'un interlocuteur."""
        if interlocutor not in self.temporal_timelines:
            return {
                "interlocutor": interlocutor,
                "exists": False,
                "temporal_dimension": None
            }
        
        timeline = self.temporal_timelines[interlocutor]
        summary = await timeline.get_temporal_summary()
        
        # Ajout de la dimension temporelle
        summary["temporal_dimension"] = timeline.temporal_dimension.to_dict()
        summary["consciousness_level"] = timeline.consciousness_interface.consciousness_level.value
        
        return summary
    
    async def search_temporal_messages(self, 
                                     interlocutor: str, 
                                     query: str,
                                     enrichment_power: str = "MEDIUM") -> List[Dict[str, Any]]:
        """Recherche temporelle dans les messages d'un interlocuteur."""
        if interlocutor not in self.temporal_timelines:
            return []
        
        timeline = self.temporal_timelines[interlocutor]
        results = await timeline.search_temporal_messages(query, enrichment_power)
        
        # Apprentissage de l'interaction
        self.learn_from_interaction("message_search", {
            "interlocutor": interlocutor,
            "query": query,
            "results_count": len(results)
        })
        
        return results
    
    async def get_temporal_message_context(self, 
                                         interlocutor: str, 
                                         message_id: str, 
                                         context_size: int = 5) -> List[Dict[str, Any]]:
        """Récupère le contexte temporel d'un message."""
        if interlocutor not in self.temporal_timelines:
            return []
        
        timeline = self.temporal_timelines[interlocutor]
        context = await timeline.get_temporal_message_context(message_id, context_size)
        
        return context
    
    async def export_temporal_timeline(self, 
                                     interlocutor: str, 
                                     format: str = "json") -> str:
        """Exporte la timeline temporelle d'un interlocuteur."""
        if interlocutor not in self.temporal_timelines:
            return ""
        
        timeline = self.temporal_timelines[interlocutor]
        export_data = await timeline.export_temporal_timeline(format)
        
        return export_data
    
    async def cleanup_temporal_old_messages(self, 
                                          interlocutor: str, 
                                          days_to_keep: int = 30) -> int:
        """Nettoie les anciens messages temporels."""
        if interlocutor not in self.temporal_timelines:
            return 0
        
        timeline = self.temporal_timelines[interlocutor]
        cleaned_count = await timeline.cleanup_temporal_old_messages(days_to_keep)
        
        # Évolution de la timeline
        self.temporal_dimension.evolve(f"Nettoyage de {cleaned_count} messages pour {interlocutor}")
        
        return cleaned_count
    
    async def auto_improve_content(self) -> bool:
        """Auto-amélioration du contenu de la timeline."""
        improved = await super().auto_improve_content()
        
        # Auto-amélioration des timelines individuelles
        for timeline in self.temporal_timelines.values():
            await timeline.auto_improve_content()
        
        return improved
    
    def get_entity_specific_data(self) -> Dict[str, Any]:
        """Retourne les données spécifiques de la timeline temporelle."""
        return {
            "base_path": str(self.base_path),
            "timeline_dir": str(self.timeline_dir),
            "interlocutors_count": len(self.temporal_timelines),
            "auto_adapt": self.auto_adapt,
            "memory_engine_connected": self.memory_engine is not None
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de la timeline temporelle."""
        stats = {
            "timeline_type": "TemporalDiscussionTimeline",
            "temporal_dimension": self.temporal_dimension.to_dict(),
            "consciousness_level": self.consciousness_interface.consciousness_level.value,
            "interlocutors_count": len(self.temporal_timelines),
            "total_messages": sum(
                len(timeline.messages) for timeline in self.temporal_timelines.values()
            )
        }
        
        # Statistiques par interlocuteur
        interlocutor_stats = {}
        for interlocutor, timeline in self.temporal_timelines.items():
            interlocutor_stats[interlocutor] = {
                "messages_count": len(timeline.messages),
                "temporal_dimension": timeline.temporal_dimension.to_dict(),
                "consciousness_level": timeline.consciousness_interface.consciousness_level.value
            }
        
        stats["interlocutor_stats"] = interlocutor_stats
        
        return stats


class TemporalTimeline(BaseTemporalEntity):
    """
    ⛧ Timeline Temporelle Individuelle - Timeline d'un Interlocuteur ⛧
    
    Timeline temporelle pour un interlocuteur spécifique,
    avec dimension temporelle et auto-amélioration.
    """
    
    def __init__(self, interlocutor: str, timeline_data: Dict[str, Any] = None, memory_engine=None):
        """
        Initialise une timeline temporelle individuelle.
        
        Args:
            interlocutor: Nom de l'interlocuteur
            timeline_data: Données de timeline existantes
            memory_engine: Instance du moteur temporel
        """
        # Initialisation de la base temporelle
        super().__init__(
            entity_id=f"temporal_timeline_{interlocutor}_{datetime.now().isoformat()}",
            entity_type="temporal_timeline"
        )
        
        # Configuration de la timeline
        self.interlocutor = interlocutor
        self.memory_engine = memory_engine
        
        # Messages temporels
        self.messages = []
        
        # Chargement des données existantes
        if timeline_data:
            self._load_timeline_data(timeline_data)
        
        # Évolution initiale
        self.temporal_dimension.evolve(f"Initialisation de la timeline pour {interlocutor}")
    
    def _load_timeline_data(self, timeline_data: Dict[str, Any]):
        """Charge les données de timeline existantes."""
        self.messages = timeline_data.get("messages", [])
        
        # Migration des messages vers le format temporel
        for message in self.messages:
            if "temporal_dimension" not in message:
                message["temporal_dimension"] = {
                    "created_at": message.get("timestamp", datetime.now().isoformat()),
                    "modified_at": message.get("timestamp", datetime.now().isoformat()),
                    "version": "1.0",
                    "evolution_history": ["Migration vers format temporel"],
                    "consciousness_level": "AWARE"
                }
    
    async def add_temporal_message(self, 
                                 message: Any, 
                                 direction: str = "incoming",
                                 metadata: Dict[str, Any] = None) -> str:
        """Ajoute un message temporel à la timeline."""
        message_id = str(uuid.uuid4())
        
        # Création de l'entrée de message temporel
        message_entry = {
            "id": message_id,
            "timestamp": datetime.now().isoformat(),
            "direction": direction,
            "message": message,
            "content": self._extract_content(message),
            "message_type": self._extract_message_type(message),
            "metadata": metadata or {},
            "temporal_dimension": {
                "created_at": datetime.now().isoformat(),
                "modified_at": datetime.now().isoformat(),
                "version": "1.0",
                "evolution_history": ["Création du message"],
                "consciousness_level": "AWARE"
            }
        }
        
        # Ajout à la timeline
        self.messages.append(message_entry)
        
        # Évolution de la timeline
        self.temporal_dimension.evolve(f"Ajout de message {direction}")
        
        # Apprentissage de l'interaction
        self.learn_from_interaction("message_added", {
            "direction": direction,
            "message_type": message_entry["message_type"]
        })
        
        return message_id
    
    def _extract_content(self, message: Any) -> str:
        """Extrait le contenu d'un message."""
        if isinstance(message, dict):
            return message.get("content", str(message))
        return str(message)
    
    def _extract_message_type(self, message: Any) -> str:
        """Extrait le type d'un message."""
        if isinstance(message, dict):
            return message.get("type", "message")
        return "message"
    
    async def get_temporal_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère les messages temporels."""
        messages = self.messages[-limit:] if limit > 0 else self.messages
        
        # Mise à jour de l'accès temporel
        self.access_layer()
        
        return messages
    
    async def get_temporal_summary(self) -> Dict[str, Any]:
        """Récupère un résumé temporel de la timeline."""
        if not self.messages:
            return {
                "interlocutor": self.interlocutor,
                "exists": False,
                "total_messages": 0
            }
        
        # Analyse des messages
        total_messages = len(self.messages)
        message_types = {}
        directions = {"incoming": 0, "outgoing": 0}
        
        for message in self.messages:
            msg_type = message.get("message_type", "message")
            direction = message.get("direction", "incoming")
            
            if msg_type not in message_types:
                message_types[msg_type] = 0
            message_types[msg_type] += 1
            
            if direction in directions:
                directions[direction] += 1
        
        # Dernière activité
        last_activity = self.messages[-1]["timestamp"] if self.messages else None
        
        return {
            "interlocutor": self.interlocutor,
            "exists": True,
            "total_messages": total_messages,
            "last_activity": last_activity,
            "message_types": message_types,
            "directions": directions,
            "temporal_dimension": self.temporal_dimension.to_dict()
        }
    
    async def search_temporal_messages(self, query: str, enrichment_power: str = "MEDIUM") -> List[Dict[str, Any]]:
        """Recherche temporelle dans les messages."""
        # Recherche simple pour l'instant
        # TODO: Intégrer le système d'enrichissement
        results = []
        
        for message in self.messages:
            content = message.get("content", "").lower()
            if query.lower() in content:
                results.append(message)
        
        # Apprentissage de l'interaction
        self.learn_from_interaction("message_search", {
            "query": query,
            "results_count": len(results)
        })
        
        return results
    
    async def get_temporal_message_context(self, message_id: str, context_size: int = 5) -> List[Dict[str, Any]]:
        """Récupère le contexte temporel d'un message."""
        # Recherche du message
        message_index = None
        for i, message in enumerate(self.messages):
            if message["id"] == message_id:
                message_index = i
                break
        
        if message_index is None:
            return []
        
        # Extraction du contexte
        start_index = max(0, message_index - context_size)
        end_index = min(len(self.messages), message_index + context_size + 1)
        
        context = self.messages[start_index:end_index]
        
        return context
    
    async def export_temporal_timeline(self, format: str = "json") -> str:
        """Exporte la timeline temporelle."""
        if format == "json":
            export_data = {
                "interlocutor": self.interlocutor,
                "created_at": self.temporal_dimension.created_at,
                "messages": self.messages,
                "temporal_dimension": self.temporal_dimension.to_dict(),
                "consciousness_level": self.consciousness_interface.consciousness_level.value
            }
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        else:
            return f"Format {format} non supporté"
    
    async def cleanup_temporal_old_messages(self, days_to_keep: int = 30) -> int:
        """Nettoie les anciens messages temporels."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_timestamp = cutoff_date.isoformat()
        
        original_count = len(self.messages)
        
        # Filtrage des messages récents
        self.messages = [
            message for message in self.messages
            if message["timestamp"] >= cutoff_timestamp
        ]
        
        cleaned_count = original_count - len(self.messages)
        
        # Évolution de la timeline
        self.temporal_dimension.evolve(f"Nettoyage de {cleaned_count} anciens messages")
        
        return cleaned_count
    
    def get_entity_specific_data(self) -> Dict[str, Any]:
        """Retourne les données spécifiques de la timeline."""
        return {
            "interlocutor": self.interlocutor,
            "messages_count": len(self.messages),
            "memory_engine_connected": self.memory_engine is not None
        } 