"""
⛧ Simple Fractalization - Fractalisation Simple et Rapide ⛧

Système de fractalisation simple et rapide pour créer des liens fractals
automatiquement sans analyse LLM complexe.

Architecte Démoniaque : Alma⛧
Visionnaire : Lucie Defraiteur - Ma Reine Lucie
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from .temporal_base import BaseTemporalEntity
from .temporal_memory_node import TemporalMemoryNode

class SimpleFractalization:
    """
    ⛧ Système de Fractalisation Simple et Rapide ⛧
    
    Crée des liens fractals automatiquement de manière simple et rapide,
    sans analyse LLM complexe.
    """
    
    def __init__(self, memory_engine=None):
        """
        Initialise le système de fractalisation simple.
        
        Args:
            memory_engine: Instance du moteur temporel
        """
        self.memory_engine = memory_engine
        self.last_message_id = None
        self.conversation_threads = {}
        self.interlocutor_history = {}
    
    async def fractalize_node(self, memory_node: TemporalMemoryNode) -> bool:
        """
        Fractalise un nœud de manière simple et rapide.
        
        Args:
            memory_node: Nœud à fractaliser
        
        Returns:
            bool: True si fractalisation réussie
        """
        try:
            node_type = memory_node.node_type
            
            # Fractalisation basée sur le type
            if node_type == "workspace_file":
                await self._fractalize_workspace_file(memory_node)
            elif node_type == "discussion_message":
                await self._fractalize_discussion_message(memory_node)
            elif node_type == "user_request":
                await self._fractalize_user_request(memory_node)
            
            # Fractalisation temporelle simple
            await self._fractalize_temporal_simple(memory_node)
            
            return True
            
        except Exception as e:
            print(f"⛧ Erreur lors de la fractalisation simple: {e}")
            return False
    
    async def _fractalize_workspace_file(self, memory_node: TemporalMemoryNode):
        """Fractalisation simple des fichiers workspace."""
        file_path = memory_node.metadata.get("file_path")
        if not file_path:
            return
        
        # Liens fractals workspace simples
        workspace_links = {
            "parent_directory": self._get_parent_directory_link(file_path),
            "sibling_files": self._get_sibling_files_links(file_path),
            "imported_modules": self._get_imported_modules_links(file_path),
            "referenced_files": self._get_referenced_files_links(file_path)
        }
        
        # Création des liens fractals
        for link_type, linked_nodes in workspace_links.items():
            for linked_node in linked_nodes:
                memory_node.add_fractal_link(linked_node, f"workspace_{link_type}")
    
    def _get_parent_directory_link(self, file_path: str) -> List[str]:
        """Trouve le lien vers le dossier parent."""
        try:
            from pathlib import Path
            parent_path = Path(file_path).parent
            return [f"directory_{parent_path}"]
        except:
            return []
    
    def _get_sibling_files_links(self, file_path: str) -> List[str]:
        """Trouve les liens vers les fichiers voisins."""
        try:
            from pathlib import Path
            file_path_obj = Path(file_path)
            parent_dir = file_path_obj.parent
            siblings = []
            
            for sibling in parent_dir.iterdir():
                if sibling.is_file() and sibling != file_path_obj:
                    siblings.append(f"file_{sibling}")
            
            return siblings
        except:
            return []
    
    def _get_imported_modules_links(self, file_path: str) -> List[str]:
        """Trouve les liens vers les modules importés."""
        # Analyse simple des imports (sans LLM)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            imports = []
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    # Extraction simple du module
                    if 'import ' in line:
                        module = line.split('import ')[1].split()[0]
                        imports.append(f"module_{module}")
                    elif 'from ' in line and ' import ' in line:
                        module = line.split('from ')[1].split(' import ')[0]
                        imports.append(f"module_{module}")
            
            return imports
        except:
            return []
    
    def _get_referenced_files_links(self, file_path: str) -> List[str]:
        """Trouve les liens vers les fichiers référencés."""
        # Analyse simple des références (sans LLM)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            references = []
            
            # Recherche de patterns simples
            import re
            
            # Patterns pour les références de fichiers
            patterns = [
                r'["\']([^"\']*\.py)["\']',  # Fichiers Python
                r'["\']([^"\']*\.json)["\']', # Fichiers JSON
                r'["\']([^"\']*\.md)["\']',   # Fichiers Markdown
                r'["\']([^"\']*\.txt)["\']'   # Fichiers texte
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    references.append(f"file_{match}")
            
            return references
        except:
            return []
    
    async def _fractalize_discussion_message(self, memory_node: TemporalMemoryNode):
        """Fractalisation simple des messages de discussion."""
        interlocutor = memory_node.metadata.get("interlocutor")
        conversation_thread = memory_node.metadata.get("conversation_thread")
        
        # Liens fractals sociaux simples
        social_links = {
            "previous_message": self._get_previous_message_link(),
            "next_message": None,  # Sera mis à jour plus tard
            "conversation_thread": self._get_conversation_thread_link(conversation_thread),
            "addressed_to": self._get_addressed_to_link(memory_node.metadata.get("addressed_to"))
        }
        
        # Création des liens fractals
        for link_type, linked_nodes in social_links.items():
            if linked_nodes:
                if isinstance(linked_nodes, list):
                    for linked_node in linked_nodes:
                        memory_node.add_fractal_link(linked_node, f"social_{link_type}")
                else:
                    memory_node.add_fractal_link(linked_nodes, f"social_{link_type}")
        
        # Mise à jour de l'historique
        self._update_message_history(memory_node)
    
    def _get_previous_message_link(self) -> Optional[str]:
        """Trouve le lien vers le message précédent."""
        return self.last_message_id
    
    def _get_conversation_thread_link(self, conversation_thread: str) -> Optional[str]:
        """Trouve le lien vers le thread de conversation."""
        if conversation_thread:
            return f"conversation_{conversation_thread}"
        return None
    
    def _get_addressed_to_link(self, addressed_to: str) -> Optional[str]:
        """Trouve le lien vers l'interlocuteur adressé."""
        if addressed_to:
            return f"interlocutor_{addressed_to}"
        return None
    
    def _update_message_history(self, memory_node: TemporalMemoryNode):
        """Met à jour l'historique des messages."""
        message_id = memory_node.entity_id
        
        # Mise à jour du message précédent pour le prochain message
        if self.last_message_id:
            # Mise à jour du lien "next_message" du message précédent
            if self.memory_engine:
                asyncio.create_task(self._update_next_message_link(self.last_message_id, message_id))
        
        self.last_message_id = message_id
        
        # Mise à jour de l'historique des interlocuteurs
        interlocutor = memory_node.metadata.get("interlocutor")
        if interlocutor:
            if interlocutor not in self.interlocutor_history:
                self.interlocutor_history[interlocutor] = []
            self.interlocutor_history[interlocutor].append(message_id)
    
    async def _update_next_message_link(self, previous_message_id: str, next_message_id: str):
        """Met à jour le lien "next_message" d'un message."""
        try:
            if self.memory_engine:
                previous_node = await self.memory_engine.get_temporal_memory(previous_message_id)
                if previous_node:
                    previous_node.add_fractal_link(next_message_id, "social_next_message")
        except Exception as e:
            print(f"⛧ Erreur lors de la mise à jour du lien next_message: {e}")
    
    async def _fractalize_user_request(self, memory_node: TemporalMemoryNode):
        """Fractalisation simple des requêtes utilisateur."""
        request_type = memory_node.metadata.get("request_type", "unknown")
        
        # Liens fractals de requête simples
        request_links = {
            "request_type": f"request_type_{request_type}",
            "priority": f"priority_{memory_node.metadata.get('priority', 'normal')}",
            "intention": f"intention_{memory_node.metadata.get('intention', 'unknown')}"
        }
        
        # Création des liens fractals
        for link_type, linked_node in request_links.items():
            memory_node.add_fractal_link(linked_node, f"request_{link_type}")
    
    async def _fractalize_temporal_simple(self, memory_node: TemporalMemoryNode):
        """Fractalisation temporelle simple."""
        # Liens temporels simples
        temporal_links = {
            "created_today": self._is_created_today(memory_node),
            "created_this_week": self._is_created_this_week(memory_node),
            "created_this_month": self._is_created_this_month(memory_node)
        }
        
        # Création des liens fractals temporels
        for link_type, is_linked in temporal_links.items():
            if is_linked:
                memory_node.add_fractal_link(f"temporal_{link_type}", f"temporal_{link_type}")
    
    def _is_created_today(self, memory_node: TemporalMemoryNode) -> bool:
        """Vérifie si le nœud a été créé aujourd'hui."""
        try:
            created_at = memory_node.temporal_dimension.created_at
            created_date = datetime.fromisoformat(created_at).date()
            today = datetime.now().date()
            return created_date == today
        except:
            return False
    
    def _is_created_this_week(self, memory_node: TemporalMemoryNode) -> bool:
        """Vérifie si le nœud a été créé cette semaine."""
        try:
            created_at = memory_node.temporal_dimension.created_at
            created_date = datetime.fromisoformat(created_at).date()
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            return created_date >= week_start
        except:
            return False
    
    def _is_created_this_month(self, memory_node: TemporalMemoryNode) -> bool:
        """Vérifie si le nœud a été créé ce mois."""
        try:
            created_at = memory_node.temporal_dimension.created_at
            created_date = datetime.fromisoformat(created_at).date()
            today = datetime.now().date()
            month_start = today.replace(day=1)
            return created_date >= month_start
        except:
            return False
    
    async def get_simple_context(self, node_id: str) -> Dict[str, Any]:
        """Récupère le contexte simple d'un nœud."""
        try:
            if not self.memory_engine:
                return {}
            
            node = await self.memory_engine.get_temporal_memory(node_id)
            if not node:
                return {}
            
            context = {
                "node_type": node.node_type,
                "fractal_links": node.fractal_links.to_dict(),
                "temporal_dimension": node.temporal_dimension.to_dict(),
                "metadata": node.metadata
            }
            
            return context
            
        except Exception as e:
            print(f"⛧ Erreur lors de la récupération du contexte simple: {e}")
            return {}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de fractalisation simple."""
        return {
            "fractalization_type": "SimpleFractalization",
            "last_message_id": self.last_message_id,
            "conversation_threads_count": len(self.conversation_threads),
            "interlocutor_history_count": len(self.interlocutor_history),
            "memory_engine_connected": self.memory_engine is not None
        } 