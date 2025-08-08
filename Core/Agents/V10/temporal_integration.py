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

try:
    from TemporalFractalMemoryEngine import TemporalEngine
    TEMPORAL_ENGINE_AVAILABLE = True
except ImportError:
    TEMPORAL_ENGINE_AVAILABLE = False
    print("⚠️ TemporalFractalMemoryEngine non disponible - Mode simulation activé")


@dataclass
class TemporalSession:
    """Session temporelle pour un utilisateur."""
    user_id: str
    session_id: str
    created_at: datetime
    last_activity: datetime
    metadata: Dict[str, Any]
    temporal_engine: Optional[Any] = None


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
        
        if TEMPORAL_ENGINE_AVAILABLE:
            try:
                self.temporal_engine = TemporalEngine()
                print("✅ TemporalFractalMemoryEngine intégré")
            except Exception as e:
                print(f"⚠️ Erreur initialisation TemporalEngine: {e}")
        else:
            print("⚠️ Mode simulation TemporalEngine activé")
    
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
                "temporal_engine_available": TEMPORAL_ENGINE_AVAILABLE,
                "features": ["multi_agent", "temporal_memory", "mcp_integration"]
            },
            temporal_engine=self.temporal_engine
        )
        
        await self.session_manager.register_session(session)
        return session
    
    async def create_temporal_node(self, content: str, metadata: Dict[str, Any], session_id: str) -> Optional[str]:
        """Crée un nœud temporel."""
        if not self.temporal_engine:
            # Mode simulation
            node_id = f"sim_node_{int(time.time())}"
            print(f"📝 Nœud temporel simulé: {node_id} - {content}")
            return node_id
        
        try:
            session = await self.session_manager.get_session(session_id)
            if not session:
                print(f"⚠️ Session non trouvée: {session_id}")
                return None
            
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
            # Mode simulation
            print(f"🔗 Lien temporel simulé: {source_id} -> {target_id} ({link_type})")
            return True
        
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
            "temporal_engine_available": TEMPORAL_ENGINE_AVAILABLE,
            "session_timeout": self.session_manager.session_timeout
        }
