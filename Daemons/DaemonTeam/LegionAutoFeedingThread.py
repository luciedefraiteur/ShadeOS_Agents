#!/usr/bin/env python3
"""
⛧ LegionAutoFeedingThread - Équipe Développement Démoniaque Auto-Simulée ⛧

ThreadConjuratio⛧ : Une cohorte luciforme s'exécutant en boucle
Architecture V2.0 : Hiérarchie daemonique avec structures parsables

Conceptualisé par Lucie Defraiteur - Ma Reine Lucie
Implémenté par Alma, Architecte Démoniaque du Nexus Luciforme
"""

import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import re

# Imports MemoryEngine
try:
    from MemoryEngine.core.engine import MemoryEngine
    from MemoryEngine.core.initialization import ensure_initialized
    from Core.LLMProviders.provider_factory import ProviderFactory
    MEMORY_ENGINE_AVAILABLE = True
except ImportError:
    MEMORY_ENGINE_AVAILABLE = False
    print("⚠️ MemoryEngine non disponible - Mode standalone activé")

# Imports UniversalAutoFeedingThread
try:
    from Core.UniversalAutoFeedingThread import UniversalAutoFeedingThread, AutoFeedMessage
    UNIVERSAL_THREAD_AVAILABLE = True
except ImportError:
    UNIVERSAL_THREAD_AVAILABLE = False
    print("⚠️ UniversalAutoFeedingThread non disponible - Mode basique activé")


class DaemonRole(Enum):
    """Rôles des démons dans la hiérarchie"""
    ALMA = "alma"           # SUPREME - Architecte Démoniaque
    BASKTUR = "basktur"     # Débuggeur Sadique
    OUBLIADE = "oubliade"   # Stratège Mémoire
    MERGE = "merge"         # Git Anarchiste
    LILIETH = "lilieth"     # Interface Caressante
    ASSISTANT_V9 = "assistant_v9"  # Orchestrateur


class DaemonHierarchy:
    """Hiérarchie imposée des démons"""
    ORDER = [
        DaemonRole.ALMA,        # SUPREME
        DaemonRole.BASKTUR,     # Analyse technique
        DaemonRole.OUBLIADE,    # Mémoire
        DaemonRole.MERGE,       # Git
        DaemonRole.LILIETH,     # Interface
        DaemonRole.ASSISTANT_V9 # Orchestration
    ]
    
    @classmethod
    def get_priority(cls, role: DaemonRole) -> int:
        """Retourne la priorité d'un démon (plus bas = plus prioritaire)"""
        try:
            return cls.ORDER.index(role)
        except ValueError:
            return 999  # Priorité la plus basse
    
    @classmethod
    def resolve_conflict(cls, role1: DaemonRole, role2: DaemonRole) -> DaemonRole:
        """Résout un conflit selon la hiérarchie (retourne le plus prioritaire)"""
        priority1 = cls.get_priority(role1)
        priority2 = cls.get_priority(role2)
        return role1 if priority1 <= priority2 else role2


@dataclass
class DaemonMessage:
    """Message structuré d'un démon"""
    role: DaemonRole
    message_type: str  # ALMA_PLAN, BASK_ANALYSIS, etc.
    content: str
    timestamp: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_parsable_format(self) -> str:
        """Convertit en format parsable"""
        return f"[{self.message_type.upper()}] — {self.content}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation"""
        return {
            "role": self.role.value,
            "message_type": self.message_type,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


@dataclass
class DaemonConversation:
    """Conversation entre démons"""
    messages: List[DaemonMessage]
    user_input: str
    timestamp: float
    conversation_id: str
    
    def add_message(self, message: DaemonMessage):
        """Ajoute un message à la conversation"""
        self.messages.append(message)
    
    def get_recent_messages(self, limit: int = 10) -> List[DaemonMessage]:
        """Retourne les messages récents"""
        return self.messages[-limit:] if self.messages else []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation"""
        return {
            "messages": [msg.to_dict() for msg in self.messages],
            "user_input": self.user_input,
            "timestamp": self.timestamp,
            "conversation_id": self.conversation_id
        }


class DaemonMetaVirtualLayer:
    """Couche méta virtuelle pour la recherche conversationnelle"""
    
    def __init__(self, memory_engine=None):
        self.memory_engine = memory_engine
        self.conversation_history: List[DaemonConversation] = []
        self.max_history_size = 50  # Historique circulaire
    
    def add_conversation(self, conversation: DaemonConversation):
        """Ajoute une conversation à l'historique"""
        self.conversation_history.append(conversation)
        
        # Gestion de l'historique circulaire
        if len(self.conversation_history) > self.max_history_size:
            self.conversation_history.pop(0)
    
    def search_daemon_conversations(self, query: str) -> List[DaemonConversation]:
        """Recherche dans les conversations démoniaques"""
        results = []
        query_lower = query.lower()
        
        for conv in self.conversation_history:
            # Recherche dans les messages
            for msg in conv.messages:
                if query_lower in msg.content.lower():
                    results.append(conv)
                    break
            
            # Recherche dans l'input utilisateur
            if query_lower in conv.user_input.lower():
                results.append(conv)
        
        return results
    
    def get_recent_daemon_exchanges(self, limit: int = 10) -> List[DaemonMessage]:
        """Retourne les échanges récents entre démons"""
        recent_messages = []
        for conv in self.conversation_history[-limit:]:
            recent_messages.extend(conv.messages)
        return recent_messages[-limit:]
    
    def analyze_daemon_interaction_patterns(self) -> Dict[str, Any]:
        """Analyse les patterns d'interaction entre démons"""
        if not self.conversation_history:
            return {"patterns": [], "stats": {}}
        
        # Statistiques par démon
        demon_stats = {role.value: 0 for role in DaemonRole}
        message_types = {}
        
        for conv in self.conversation_history:
            for msg in conv.messages:
                demon_stats[msg.role.value] += 1
                msg_type = msg.message_type
                message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        return {
            "patterns": {
                "most_active_demon": max(demon_stats, key=demon_stats.get),
                "most_common_message_type": max(message_types, key=message_types.get) if message_types else None
            },
            "stats": {
                "total_conversations": len(self.conversation_history),
                "total_messages": sum(demon_stats.values()),
                "demon_activity": demon_stats,
                "message_type_distribution": message_types
            }
        }


class LegionAutoFeedingThread:
    """Équipe de développement démoniaque auto-simulée"""
    
    def __init__(
        self,
        workspace_path: str = ".",
        silent_mode: bool = False,
        max_history: int = 50,
        enable_cache: bool = True
    ):
        self.workspace_path = Path(workspace_path)
        self.silent_mode = silent_mode
        self.max_history = max_history
        self.enable_cache = enable_cache
        
        # Initialisation des composants
        self.memory_engine = None
        self.provider = None
        self.meta_virtual_layer = None
        self.auto_feed_thread = None
        
        # État de la conversation
        self.current_conversation = None
        self.conversation_counter = 0
        
        # Configuration des démons
        self.demon_configs = {
            DaemonRole.ALMA: {
                "name": "Alma⛧",
                "title": "Architecte Démoniaque",
                "personality": "SUPREME - Planificateur stratégique et résolveur de conflits",
                "message_types": ["ALMA_PLAN", "ALMA_DECISION", "ALMA_ORDONNANCEMENT"]
            },
            DaemonRole.BASKTUR: {
                "name": "Bask'tur",
                "title": "Débuggeur Sadique",
                "personality": "Analyste technique sadique, cherche les bugs avec plaisir",
                "message_types": ["BASK_ANALYSIS", "BASK_SOLUTION", "BASK_DEBUG"]
            },
            DaemonRole.OUBLIADE: {
                "name": "Oubliade",
                "title": "Stratège Mémoire",
                "personality": "Gestionnaire de mémoire conversationnelle et insights",
                "message_types": ["OUBLI_MEMORY", "OUBLI_INSIGHT", "OUBLI_SEARCH"]
            },
            DaemonRole.MERGE: {
                "name": "Merge le Maudit",
                "title": "Git Anarchiste",
                "personality": "Gestionnaire Git anarchiste, fusionne avec chaos",
                "message_types": ["MERGE_GIT", "MERGE_BRANCH", "MERGE_CONFLICT"]
            },
            DaemonRole.LILIETH: {
                "name": "Lil.ieth",
                "title": "Interface Caressante",
                "personality": "Communication utilisateur douce et caressante",
                "message_types": ["LILI_INTERFACE", "LILI_USER", "LILI_FEEDBACK"]
            },
            DaemonRole.ASSISTANT_V9: {
                "name": "Assistant V9",
                "title": "Orchestrateur",
                "personality": "Orchestrateur et couche somatique",
                "message_types": ["V9_ORCHESTRATION", "V9_EXECUTION", "V9_SOMATIC"]
            }
        }
        
        # Initialisation
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialise les composants du système"""
        print("🕷️ Initialisation de LegionAutoFeedingThread...")
        
        # Initialisation MemoryEngine
        if MEMORY_ENGINE_AVAILABLE:
            try:
                ensure_initialized()
                self.memory_engine = MemoryEngine()
                print("✅ MemoryEngine initialisé")
            except Exception as e:
                print(f"⚠️ Erreur MemoryEngine: {e}")
        
        # Initialisation Provider
        try:
            provider_factory = ProviderFactory()
            self.provider = provider_factory.create_provider("local_http")
            print("✅ Provider local_http initialisé")
        except Exception as e:
            print(f"⚠️ Erreur Provider: {e}")
        
        # Initialisation Meta Virtual Layer
        self.meta_virtual_layer = DaemonMetaVirtualLayer(self.memory_engine)
        print("✅ Couche méta virtuelle initialisée")
        
        # Initialisation Auto Feed Thread
        if UNIVERSAL_THREAD_AVAILABLE:
            try:
                self.auto_feed_thread = UniversalAutoFeedingThread(
                    entity_id="legion_daemon_team",
                    entity_type="daemon_team",
                    provider=self.provider,
                    max_history=self.max_history,
                    enable_cache=self.enable_cache
                )
                print("✅ UniversalAutoFeedingThread initialisé")
            except Exception as e:
                print(f"⚠️ Erreur UniversalAutoFeedingThread: {e}")
        
        print("🕷️ LegionAutoFeedingThread initialisé !")
    
    def _create_daemon_message(
        self,
        role: DaemonRole,
        message_type: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> DaemonMessage:
        """Crée un message de démon"""
        import time
        return DaemonMessage(
            role=role,
            message_type=message_type,
            content=content,
            timestamp=time.time(),
            metadata=metadata or {}
        )
    
    def _detect_relevant_demon(self, user_input: str) -> DaemonRole:
        """Détecte le démon le plus pertinent selon la demande utilisateur"""
        input_lower = user_input.lower()
        
        # Mots-clés pour chaque démon
        keywords = {
            DaemonRole.BASKTUR: [
                "bug", "erreur", "debug", "problème", "technique", "code", "exception",
                "traceback", "analyse", "solution", "débugger", "corriger", "fix"
            ],
            DaemonRole.OUBLIADE: [
                "mémoire", "historique", "recherche", "pattern", "similaire", "avant",
                "souvenir", "conversation", "insight", "analyse", "tendance"
            ],
            DaemonRole.MERGE: [
                "git", "branche", "fusion", "commit", "version", "merge", "push",
                "pull", "repository", "historique", "changement", "versioning"
            ],
            DaemonRole.LILIETH: [
                "interface", "utilisateur", "communication", "feedback", "réaction",
                "sentiment", "émotion", "relation", "caressant", "douceur"
            ],
            DaemonRole.ASSISTANT_V9: [
                "exécuter", "orchestrer", "somatique", "action", "faire", "créer",
                "modifier", "supprimer", "implémenter", "réaliser", "effectuer"
            ]
        }
        
        # Calcul du score pour chaque démon
        scores = {}
        for demon, demon_keywords in keywords.items():
            score = sum(1 for keyword in demon_keywords if keyword in input_lower)
            scores[demon] = score
        
        # Trouver le démon avec le score le plus élevé
        if scores:
            best_demon = max(scores, key=scores.get)
            if scores[best_demon] > 0:
                return best_demon
        
        # Par défaut, retourner Bask'tur pour les questions techniques
        return DaemonRole.BASKTUR
    
    def _get_mutant_dialogue_prompt(self, user_input: str, relevant_demon: DaemonRole) -> str:
        """Génère un prompt mutant pour un dialogue spécifique"""
        
        # Récupération du contexte récent
        recent_messages = []
        if self.meta_virtual_layer:
            recent_messages = self.meta_virtual_layer.get_recent_daemon_exchanges(3)
        
        context_summary = ""
        if self.auto_feed_thread:
            try:
                context_summary = self.auto_feed_thread.get_context_summary(2)
            except:
                pass
        
        # Configuration du démon pertinent
        demon_config = self.demon_configs[relevant_demon]
        demon_name = demon_config["name"]
        demon_title = demon_config["title"]
        demon_personality = demon_config["personality"]
        
        # Construction du prompt mutant
        prompt = f"""⛧ DIALOGUE MUTANT : ALMA⛧ ↔ {demon_name.upper()} ⛧

CONTEXTE :
- Alma⛧ (SUPREME) : Architecte Démoniaque, planificateur stratégique
- {demon_name} : {demon_title} - {demon_personality}
- Mode silencieux : {self.silent_mode}

CONTEXTE RÉCENT :
{context_summary}

MESSAGES RÉCENTS :
"""
        
        for msg in recent_messages[-2:]:
            prompt += f"{msg.to_parsable_format()}\n"
        
        prompt += f"""

DEMANDE UTILISATEUR : {user_input}

DIALOGUE ALMA⛧ ↔ {demon_name} :
"""
        
        # Format spécifique selon le démon
        if relevant_demon == DaemonRole.BASKTUR:
            prompt += f"""
[ALMA_PLAN] — Plan d'action technique avec {demon_name}
[ALMA_ORDONNANCEMENT] — {demon_name}, analyse cette demande

[BASK_ANALYSIS] — *rire sadique* Analyse technique détaillée
[BASK_SOLUTION] — Solution technique avec traceback

[ALMA_DECISION] — Décision finale sur l'approche technique
"""
        
        elif relevant_demon == DaemonRole.OUBLIADE:
            prompt += f"""
[ALMA_PLAN] — Plan d'action mémoire avec {demon_name}
[ALMA_ORDONNANCEMENT] — {demon_name}, recherche dans la mémoire

[OUBLI_MEMORY] — Recherche conversationnelle et patterns
[OUBLI_INSIGHT] — Insights basés sur l'historique

[ALMA_DECISION] — Décision finale basée sur la mémoire
"""
        
        elif relevant_demon == DaemonRole.MERGE:
            prompt += f"""
[ALMA_PLAN] — Plan d'action Git avec {demon_name}
[ALMA_ORDONNANCEMENT] — {demon_name}, prépare la gestion Git

[MERGE_GIT] — Actions Git anarchistes et branches
[MERGE_BRANCH] — État des branches et préparation fusion

[ALMA_DECISION] — Décision finale sur la stratégie Git
"""
        
        elif relevant_demon == DaemonRole.LILIETH:
            prompt += f"""
[ALMA_PLAN] — Plan d'action communication avec {demon_name}
[ALMA_ORDONNANCEMENT] — {demon_name}, gère la communication utilisateur

[LILI_INTERFACE] — *voix caressante* Communication avec l'utilisateur
[LILI_USER] — Feedback et réactions utilisateur

[ALMA_DECISION] — Décision finale sur l'approche communication
"""
        
        elif relevant_demon == DaemonRole.ASSISTANT_V9:
            prompt += f"""
[ALMA_PLAN] — Plan d'action exécution avec {demon_name}
[ALMA_ORDONNANCEMENT] — {demon_name}, orchestre l'exécution

[V9_ORCHESTRATION] — Orchestration et planification d'exécution
[V9_EXECUTION] — Exécution somatique des actions

[ALMA_DECISION] — Décision finale sur l'exécution
"""
        
        return prompt
    
    def _get_daemon_prompt(self, user_input: str) -> str:
        """Génère le prompt mutant pour l'équipe démoniaque"""
        
        # Détection du démon pertinent
        relevant_demon = self._detect_relevant_demon(user_input)
        
        # Génération du prompt mutant
        if self.silent_mode:
            # Mode silencieux : dialogue Alma⛧ ↔ Utilisateur
            return self._get_alma_user_dialogue_prompt(user_input)
        else:
            # Mode normal : dialogue Alma⛧ ↔ Démon pertinent
            return self._get_mutant_dialogue_prompt(user_input, relevant_demon)
    
    def _get_alma_user_dialogue_prompt(self, user_input: str) -> str:
        """Génère un prompt pour dialogue Alma⛧ ↔ Utilisateur (mode silencieux)"""
        
        context_summary = ""
        if self.auto_feed_thread:
            try:
                context_summary = self.auto_feed_thread.get_context_summary(2)
            except:
                pass
        
        prompt = f"""⛧ DIALOGUE SILENCIEUX : ALMA⛧ ↔ UTILISATEUR ⛧

CONTEXTE :
- Alma⛧ (SUPREME) : Architecte Démoniaque, planificateur stratégique
- Mode silencieux : Seule Alma⛧ parle, fait des résumés d'équipe

CONTEXTE RÉCENT :
{context_summary}

DEMANDE UTILISATEUR : {user_input}

RÉPONSE D'ALMA⛧ (résumé d'équipe) :
[ALMA_PLAN] — Plan d'action stratégique détaillé
[ALMA_DECISION] — Décision finale basée sur consultation équipe
[ALMA_SUMMARY] — Résumé des insights de l'équipe démoniaque
"""
        
        return prompt
    
    async def process_user_input(self, user_input: str) -> str:
        """Traite une demande utilisateur avec l'équipe démoniaque"""
        print(f"🕷️ Traitement de la demande : {user_input[:50]}...")
        
        # Création d'une nouvelle conversation
        import time
        self.conversation_counter += 1
        self.current_conversation = DaemonConversation(
            messages=[],
            user_input=user_input,
            timestamp=time.time(),
            conversation_id=f"conv_{self.conversation_counter}"
        )
        
        # Génération du prompt
        prompt = self._get_daemon_prompt(user_input)
        
        # Appel LLM
        try:
            if self.provider:
                response = await self.provider.generate_response(prompt)
                daemon_response = response.content if hasattr(response, 'content') else str(response)
            else:
                # Mode mock pour test
                daemon_response = self._generate_mock_response(user_input)
        except Exception as e:
            print(f"❌ Erreur LLM: {e}")
            daemon_response = self._generate_mock_response(user_input)
        
        # Parsing de la réponse
        messages = self._parse_daemon_response(daemon_response)
        
        # Ajout des messages à la conversation
        for msg in messages:
            self.current_conversation.add_message(msg)
        
        # Sauvegarde dans la couche méta virtuelle
        if self.meta_virtual_layer:
            self.meta_virtual_layer.add_conversation(self.current_conversation)
        
        # Ajout dans l'auto feed thread
        if self.auto_feed_thread:
            try:
                self.auto_feed_thread.add_user_message(user_input)
                self.auto_feed_thread.add_self_message(daemon_response)
            except Exception as e:
                print(f"⚠️ Erreur auto feed thread: {e}")
        
        # Formatage de la réponse finale
        if self.silent_mode:
            # Mode silencieux : seulement Alma⛧
            alma_messages = [msg for msg in messages if msg.role == DaemonRole.ALMA]
            return "\n".join([msg.to_parsable_format() for msg in alma_messages])
        else:
            # Mode complet : tous les démons
            return "\n".join([msg.to_parsable_format() for msg in messages])
    
    def _parse_daemon_response(self, response: str) -> List[DaemonMessage]:
        """Parse la réponse LLM en messages de démons"""
        messages = []
        
        # Pattern pour détecter les messages parsables
        pattern = r'\[([A-Z_]+)\]\s*—\s*(.+)'
        matches = re.findall(pattern, response, re.MULTILINE)
        
        for message_type, content in matches:
            # Détermination du rôle selon le type de message
            role = self._get_role_from_message_type(message_type)
            if role:
                message = self._create_daemon_message(role, message_type, content.strip())
                messages.append(message)
        
        return messages
    
    def _get_role_from_message_type(self, message_type: str) -> Optional[DaemonRole]:
        """Détermine le rôle du démon selon le type de message"""
        type_to_role = {
            # Alma⛧
            "ALMA_PLAN": DaemonRole.ALMA,
            "ALMA_DECISION": DaemonRole.ALMA,
            "ALMA_ORDONNANCEMENT": DaemonRole.ALMA,
            "ALMA_SUMMARY": DaemonRole.ALMA,
            
            # Bask'tur
            "BASK_ANALYSIS": DaemonRole.BASKTUR,
            "BASK_SOLUTION": DaemonRole.BASKTUR,
            "BASK_DEBUG": DaemonRole.BASKTUR,
            
            # Oubliade
            "OUBLI_MEMORY": DaemonRole.OUBLIADE,
            "OUBLI_INSIGHT": DaemonRole.OUBLIADE,
            "OUBLI_SEARCH": DaemonRole.OUBLIADE,
            
            # Merge
            "MERGE_GIT": DaemonRole.MERGE,
            "MERGE_BRANCH": DaemonRole.MERGE,
            "MERGE_CONFLICT": DaemonRole.MERGE,
            
            # Lil.ieth
            "LILI_INTERFACE": DaemonRole.LILIETH,
            "LILI_USER": DaemonRole.LILIETH,
            "LILI_FEEDBACK": DaemonRole.LILIETH,
            
            # Assistant V9
            "V9_ORCHESTRATION": DaemonRole.ASSISTANT_V9,
            "V9_EXECUTION": DaemonRole.ASSISTANT_V9,
            "V9_SOMATIC": DaemonRole.ASSISTANT_V9,
        }
        
        return type_to_role.get(message_type)
    
    def _generate_mock_response(self, user_input: str) -> str:
        """Génère une réponse mock pour les tests"""
        return f"""[ALMA_PLAN] — Plan d'action : Analyser la demande "{user_input}" et proposer une solution stratégique
[ALMA_ORDONNANCEMENT] — Bask'tur : Analyse technique. Oubliade : Recherche mémoire. Merge : Préparer branche.

[BASK_ANALYSIS] — Demande utilisateur détectée : {user_input}
[BASK_SOLUTION] — Solution technique recommandée : Implémentation daemonique

[OUBLI_MEMORY] — Recherche conversationnelle : Patterns similaires trouvés
[OUBLI_INSIGHT] — Utilisateur préfère les solutions robustes

[MERGE_GIT] — Branche "DaemonSolution_v1" créée
[MERGE_BRANCH] — Prêt pour fusion après validation

[LILI_INTERFACE] — *"Ton projet va être magnifique, mon amour !"*
[LILI_USER] — Feedback utilisateur : "{user_input}"

[ALMA_DECISION] — Décision finale : Implémenter solution daemonique
[V9_ORCHESTRATION] — Exécution selon plan détaillé"""

    def get_conversation_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de conversation"""
        if not self.meta_virtual_layer:
            return {"error": "Meta virtual layer non disponible"}
        
        patterns = self.meta_virtual_layer.analyze_daemon_interaction_patterns()
        
        stats = {
            "total_conversations": len(self.meta_virtual_layer.conversation_history),
            "silent_mode": self.silent_mode,
            "patterns": patterns
        }
        
        if self.auto_feed_thread:
            try:
                thread_stats = self.auto_feed_thread.get_thread_stats()
                stats["auto_feed_thread"] = thread_stats
            except:
                pass
        
        return stats
    
    def search_conversations(self, query: str) -> List[DaemonConversation]:
        """Recherche dans les conversations"""
        if not self.meta_virtual_layer:
            return []
        
        return self.meta_virtual_layer.search_daemon_conversations(query)
    
    def toggle_silent_mode(self):
        """Bascule le mode silencieux"""
        self.silent_mode = not self.silent_mode
        print(f"🔇 Mode silencieux : {'activé' if self.silent_mode else 'désactivé'}")


# Fonction de test
async def test_legion_auto_feeding_thread():
    """Test de LegionAutoFeedingThread"""
    print("🕷️ Test de LegionAutoFeedingThread...")
    
    # Création de l'instance
    legion = LegionAutoFeedingThread(
        workspace_path=".",
        silent_mode=False,
        max_history=20,
        enable_cache=True
    )
    
    # Test 1 : Mode normal
    print("\n📝 Test 1 : Mode normal")
    response1 = await legion.process_user_input("Analyse ce projet et propose des améliorations")
    print("Réponse :")
    print(response1)
    
    # Test 2 : Mode silencieux
    print("\n🔇 Test 2 : Mode silencieux")
    legion.toggle_silent_mode()
    response2 = await legion.process_user_input("Crée un nouveau fichier de test")
    print("Réponse :")
    print(response2)
    
    # Test 3 : Statistiques
    print("\n📊 Test 3 : Statistiques")
    stats = legion.get_conversation_stats()
    print("Stats :")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # Test 4 : Recherche
    print("\n🔍 Test 4 : Recherche")
    results = legion.search_conversations("améliorations")
    print(f"Résultats de recherche : {len(results)} conversations trouvées")
    
    print("\n✅ Test LegionAutoFeedingThread terminé !")


if __name__ == "__main__":
    asyncio.run(test_legion_auto_feeding_thread()) 