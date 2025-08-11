#!/usr/bin/env python3
"""
⛧ V10 Temporal Integration ⛧
Alma's Temporal Memory Integration for V10

Intégration temporelle pour l'Assistant V10 avec gestion des sessions.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import uuid

try:
    from Core.Config.feature_flags import is_temporal_engine_enabled
except Exception:
    def is_temporal_engine_enabled() -> bool:
        return False

try:
    from TemporalFractalMemoryEngine import TemporalEngine
    _TFME_IMPORTED = True
except ImportError:
    _TFME_IMPORTED = False
    print("⚠️ TemporalFractalMemoryEngine non disponible - Mode simulation activé")


@dataclass
class TemporalSession:
    """Session temporelle interne pour un utilisateur (utilisée par l'intégration)."""
    user_id: str
    session_id: str
    created_at: datetime
    last_activity: datetime
    metadata: Dict[str, Any]
    temporal_engine: Optional[Any] = None


# Classes attendues par les tests unitaires (API de façade minimale)
@dataclass
class V10Session:
    """Dataclass simple pour représenter une session (API test)."""
    user_id: str
    session_id: str = None
    created_at: datetime = None
    last_activity: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        now = datetime.now()
        if self.session_id is None:
            # Use high-resolution time + UUID to avoid collisions in tests
            self.session_id = f"v10_session_{self.user_id}_{int(time.time()*1000)}_{uuid.uuid4().hex[:8]}"
        if self.created_at is None:
            self.created_at = now
        if self.last_activity is None:
            self.last_activity = now
        if self.metadata is None:
            self.metadata = {}


@dataclass
class V10TemporalNode:
    """Dataclass simple pour représenter un nœud temporel (API test)."""
    content: str
    metadata: Dict[str, Any]
    node_id: str = None
    created_at: datetime = None

    def __post_init__(self):
        if self.node_id is None:
            self.node_id = f"v10_node_{int(time.time()*1000)}"
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class V10TemporalLink:
    """Dataclass simple pour représenter un lien temporel (API test)."""
    source_id: str
    target_id: str
    link_type: str
    link_id: str = None
    created_at: datetime = None

    def __post_init__(self):
        if self.link_id is None:
            self.link_id = f"v10_link_{int(time.time()*1000)}"
        if self.created_at is None:
            self.created_at = datetime.now()


class V10SessionManager:
    """Gestionnaire de sessions temporelles pour V10."""
    
    def __init__(self):
        """Initialise le gestionnaire de sessions."""
        self.active_sessions: Dict[str, TemporalSession] = {}
        self.session_timeout = 3600  # 1 heure
    
    async def register_session(self, session: TemporalSession) -> None:
        """Enregistre une nouvelle session."""
        self.active_sessions[session.session_id] = session
        print(f"✅ Session enregistrée: {session.session_id} pour {session.user_id}")
    
    async def get_session(self, session_id: str) -> Optional[TemporalSession]:
        """Récupère une session active."""
        session = self.active_sessions.get(session_id)
        if session:
            # Vérifier le timeout
            if (datetime.now() - session.last_activity).seconds > self.session_timeout:
                await self.cleanup_session(session_id)
                return None
            # Mettre à jour l'activité
            session.last_activity = datetime.now()
        return session
    
    async def cleanup_session(self, session_id: str) -> None:
        """Nettoie une session expirée."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            print(f"🧹 Session nettoyée: {session_id}")
    
    async def cleanup_expired_sessions(self) -> int:
        """Nettoie toutes les sessions expirées."""
        expired_count = 0
        current_time = datetime.now()
        
        for session_id, session in list(self.active_sessions.items()):
            if (current_time - session.last_activity).seconds > self.session_timeout:
                await self.cleanup_session(session_id)
                expired_count += 1
        
        return expired_count
    
    def get_active_sessions_count(self) -> int:
        """Retourne le nombre de sessions actives."""
        return len(self.active_sessions)


class V10TemporalIntegration:
    """Intégration temporelle pour V10."""
    
    def __init__(self):
        """Initialise l'intégration temporelle."""
        self.temporal_engine = None
        self.session_manager = V10SessionManager()
        self.temporal_engine_available = False
        # Espace de simulation des nœuds (mode sans moteur)
        self._sim_nodes: set[str] = set()
        
        # Activation contrôlée par feature flag
        self.temporal_engine_available = _TFME_IMPORTED and is_temporal_engine_enabled()
        if self.temporal_engine_available:
            try:
                self.temporal_engine = TemporalEngine()
                print("✅ TemporalFractalMemoryEngine intégré")
            except Exception as e:
                print(f"⚠️ Erreur initialisation TemporalEngine: {e}")
        else:
            print("ℹ️ TemporalEngine désactivé ou indisponible - Mode simulation activé")
    
    async def initialize_session(self, user_id: str) -> TemporalSession:
        """Initialise une session temporelle pour l'utilisateur."""
        session_id = f"v10_session_{user_id}_{int(time.time())}"
        
        session = TemporalSession(
            user_id=user_id,
            session_id=session_id,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            metadata={
                "version": "V10",
                "temporal_engine_available": self.temporal_engine_available,
                "features": ["multi_agent", "temporal_memory", "mcp_integration"]
            },
            temporal_engine=self.temporal_engine
        )
        
        await self.session_manager.register_session(session)
        return session
    
    async def create_temporal_node(self, content: str, metadata: Dict[str, Any], session_id: str, **kwargs) -> Optional[str]:
        """Crée un nœud temporel."""
        # Vérifier la session même en mode simulation
        session = await self.session_manager.get_session(session_id)
        if not session:
            print(f"⚠️ Session non trouvée: {session_id}")
            return None

        if not self.temporal_engine:
            # Mode simulation: générer et stocker un ID local
            node_id = f"sim_node_{int(time.time()*1000)}"
            self._sim_nodes.add(node_id)
            print(f"📝 Nœud temporel simulé: {node_id} - {content}")
            return node_id
        
        try:
            node = await self.temporal_engine.create_temporal_node(
                content=content,
                metadata=metadata
            )
            
            print(f"📝 Nœud temporel créé: {node.id} - {content}")
            return node.id
            
        except Exception as e:
            print(f"❌ Erreur création nœud temporel: {e}")
            return None
    
    async def create_temporal_link(self, source_id: str, target_id: str, link_type: str = "default", session_id: str = None) -> bool:
        """Crée un lien temporel entre deux nœuds."""
        if not self.temporal_engine:
            # Mode simulation avec validation basique d'existence
            if source_id in self._sim_nodes and target_id in self._sim_nodes:
                print(f"🔗 Lien temporel simulé: {source_id} -> {target_id} ({link_type})")
                return True
            print(f"❌ Lien temporel simulé invalide: {source_id} -> {target_id} ({link_type})")
            return False
        
        try:
            await self.temporal_engine.create_temporal_link(
                source_id=source_id,
                target_id=target_id,
                link_type=link_type
            )
            
            print(f"🔗 Lien temporel créé: {source_id} -> {target_id} ({link_type})")
            return True
            
        except Exception as e:
            print(f"❌ Erreur création lien temporel: {e}")
            return False
    
    async def get_relevant_context(self, query: str, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère le contexte pertinent pour une requête."""
        if not self.temporal_engine:
            # Mode simulation
            return [{"content": "Contexte simulé", "relevance": 0.8}]
        
        try:
            session = await self.session_manager.get_session(session_id)
            if not session:
                return []
            
            context = await self.temporal_engine.search_temporal_context(
                query=query,
                limit=limit
            )
            
            return context
            
        except Exception as e:
            print(f"❌ Erreur récupération contexte: {e}")
            return []
    
    async def cleanup_expired_sessions(self) -> int:
        """Nettoie les sessions expirées."""
        return await self.session_manager.cleanup_expired_sessions()
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des sessions."""
        return {
            "active_sessions": self.session_manager.get_active_sessions_count(),
            "temporal_engine_available": self.temporal_engine_available,
            "session_timeout": self.session_manager.session_timeout
        }

    async def update_session_activity(self, session_id: str) -> bool:
        """Met à jour l'activité d'une session (API test)."""
        session = await self.session_manager.get_session(session_id)
        if not session:
            return False
        session.last_activity = datetime.now()
        return True
