# ⛧ Créé par Alma, Architecte Démoniaque ⛧
# 🧱 LegionAutoFeedingThread - Sous-classe de BaseAutoFeedingThread

import asyncio
import json
import re
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import time

# Ajout du chemin du projet pour les imports absolus
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import de la base class
from Core.UniversalAutoFeedingThread.base_auto_feeding_thread import BaseAutoFeedingThread, AutoFeedMessage

# Imports MemoryEngine
try:
    from MemoryEngine.core.engine import MemoryEngine
    from MemoryEngine.core.initialization import ensure_initialized
    MEMORY_ENGINE_AVAILABLE = True
except ImportError:
    MEMORY_ENGINE_AVAILABLE = False
    print("⚠️ MemoryEngine non disponible - Mode standalone activé")

# Imports LLM Providers
try:
    from Core.LLMProviders.provider_factory import ProviderFactory
    PROVIDER_AVAILABLE = True
except ImportError:
    PROVIDER_AVAILABLE = False
    print("⚠️ ProviderFactory non disponible - Mode mock activé")

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
    """Couche méta virtuelle pour l'analyse des conversations démoniaques"""
    
    def __init__(self, memory_engine=None):
        self.memory_engine = memory_engine
        self.conversation_history = []
    
    def add_conversation(self, conversation: DaemonConversation):
        """Ajoute une conversation à l'historique"""
        self.conversation_history.append(conversation)
        
        # Limiter l'historique
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
    
    def search_daemon_conversations(self, query: str) -> List[DaemonConversation]:
        """Recherche dans les conversations démoniaques"""
        results = []
        query_lower = query.lower()
        
        for conv in self.conversation_history:
            # Recherche dans l'input utilisateur
            if query_lower in conv.user_input.lower():
                results.append(conv)
                continue
            
            # Recherche dans les messages
            for msg in conv.messages:
                if query_lower in msg.content.lower():
                    results.append(conv)
                    break
        
        return results
    
    def get_recent_daemon_exchanges(self, limit: int = 10) -> List[DaemonMessage]:
        """Récupère les échanges démoniaques récents"""
        all_messages = []
        for conv in self.conversation_history[-limit:]:
            all_messages.extend(conv.messages)
        
        return all_messages[-limit:]
    
    def analyze_daemon_interaction_patterns(self) -> Dict[str, Any]:
        """Analyse les patterns d'interaction entre démons"""
        if not self.conversation_history:
            return {"patterns": {}, "stats": {}}
        
        # Statistiques de base
        total_conversations = len(self.conversation_history)
        total_messages = sum(len(conv.messages) for conv in self.conversation_history)
        
        # Analyse des démons les plus actifs
        demon_activity = {role.value: 0 for role in DaemonRole}
        message_type_distribution = {}
        
        for conv in self.conversation_history:
            for msg in conv.messages:
                demon_activity[msg.role.value] += 1
                message_type_distribution[msg.message_type] = message_type_distribution.get(msg.message_type, 0) + 1
        
        # Démon le plus actif
        most_active_demon = max(demon_activity.items(), key=lambda x: x[1])[0] if demon_activity else None
        most_common_message_type = max(message_type_distribution.items(), key=lambda x: x[1])[0] if message_type_distribution else None
        
        return {
            "patterns": {
                "most_active_demon": most_active_demon,
                "most_common_message_type": most_common_message_type
            },
            "stats": {
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "demon_activity": demon_activity,
                "message_type_distribution": message_type_distribution
            }
        }

class LegionAutoFeedingThread(BaseAutoFeedingThread):
    """Équipe de développement démoniaque auto-simulée - Version 2.0"""
    
    def __init__(
        self,
        workspace_path: str = ".",
        silent_mode: bool = False,
        max_history: int = 50,
        enable_cache: bool = True
    ):
        # Initialisation de la base class
        super().__init__(
            entity_id="legion_daemon_team",
            entity_type="legion",
            max_history=max_history,
            enable_logging=True
        )
        
        self.workspace_path = Path(workspace_path)
        self.silent_mode = silent_mode
        self.enable_cache = enable_cache
        
        # Initialisation des composants
        self.memory_engine = None
        self.meta_virtual_layer = None
        
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
        self.log_debug_action("initialization_start", {"workspace_path": str(self.workspace_path)})
        
        # Initialisation MemoryEngine
        if MEMORY_ENGINE_AVAILABLE:
            try:
                ensure_initialized()
                self.memory_engine = MemoryEngine()
                self.log_debug_action("memory_engine_initialized", {"status": "success"})
            except Exception as e:
                self.log_debug_action("memory_engine_error", {"error": str(e)})
        
        # Initialisation Provider
        if PROVIDER_AVAILABLE:
            try:
                # Configuration rituelle pour Ollama local
                config = {
                    "model": "qwen2.5:7b-instruct",
                    "ollama_host": "http://localhost:11434",
                    "timeout": 60,
                    "temperature": 0.666  # Rituel démoniaque
                }
                self.provider = ProviderFactory.create_provider("local", **config)
                self.log_debug_action("provider_initialized", {
                    "provider_type": "local",
                    "temperature": 0.666,
                    "model": "qwen2.5:7b-instruct"
                })
            except Exception as e:
                self.log_debug_action("provider_error", {"error": str(e)})
                self.provider = None
        else:
            self.log_debug_action("provider_unavailable", {"fallback": "mock_mode"})
            self.provider = None
        
        # Initialisation Meta Virtual Layer
        try:
            self.meta_virtual_layer = DaemonMetaVirtualLayer(self.memory_engine)
            self.log_debug_action("meta_virtual_layer_initialized", {"status": "success"})
        except Exception as e:
            self.log_debug_action("meta_virtual_layer_error", {"error": str(e)})
    
    async def _initialize_provider(self):
        """Initialise le provider LLM (implémentation de la base class)"""
        if self.provider is None and PROVIDER_AVAILABLE:
            try:
                config = {
                    "model": "qwen2.5:7b-instruct",
                    "ollama_host": "http://localhost:11434",
                    "timeout": 60,
                    "temperature": 0.666
                }
                self.provider = ProviderFactory.create_provider("local", **config)
                self.log_debug_action("provider_async_initialized", {"status": "success"})
            except Exception as e:
                self.log_debug_action("provider_async_error", {"error": str(e)})
    
    async def _call_llm(self, prompt: str) -> str:
        """Appelle le LLM (implémentation de la base class)"""
        try:
            await self._initialize_provider()
            
            if self.provider:
                response = await self.provider.generate_response(prompt)
                daemon_response = response.content if hasattr(response, 'content') else str(response)
                self.log_debug_action("llm_call_success", {
                    "prompt_length": len(prompt),
                    "response_length": len(daemon_response)
                })
                return daemon_response
            else:
                # Mode mock
                mock_response = self._generate_mock_response("mock_input")
                self.log_debug_action("llm_call_mock", {"reason": "provider_unavailable"})
                return mock_response
        except Exception as e:
            self.log_debug_action("llm_call_error", {"error": str(e)})
            return self._generate_mock_response("error_fallback")
    
    def _get_prompt(self, user_input: str) -> str:
        """Génère le prompt pour le LLM (implémentation de la base class)"""
        return self._get_daemon_prompt(user_input)
    
    async def process_request(self, user_input: str) -> str:
        """Traite une demande utilisateur (implémentation de la base class)"""
        return await self.process_user_input(user_input)
    
    def _create_daemon_message(
        self,
        role: DaemonRole,
        message_type: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> DaemonMessage:
        """Crée un message de démon"""
        return DaemonMessage(
            role=role,
            message_type=message_type,
            content=content,
            timestamp=time.time(),
            metadata=metadata or {}
        )
    
    def _detect_relevant_demon(self, user_input: str) -> DaemonRole:
        """Détecte le démon le plus pertinent pour la demande"""
        user_input_lower = user_input.lower()
        
        # Mots-clés pour chaque démon
        demon_keywords = {
            DaemonRole.BASKTUR: ["bug", "debug", "erreur", "problème", "corriger", "analyser", "technique"],
            DaemonRole.OUBLIADE: ["mémoire", "historique", "recherche", "pattern", "conversation"],
            DaemonRole.MERGE: ["git", "commit", "branche", "fusion", "version", "historique"],
            DaemonRole.LILIETH: ["interface", "utilisateur", "communication", "feedback", "expérience"],
            DaemonRole.ASSISTANT_V9: ["exécuter", "orchestrer", "planifier", "coordonner", "action"]
        }
        
        # Calcul du score pour chaque démon
        demon_scores = {}
        for demon, keywords in demon_keywords.items():
            score = sum(1 for keyword in keywords if keyword in user_input_lower)
            demon_scores[demon] = score
        
        # Retourner le démon avec le score le plus élevé, ou Alma par défaut
        if any(demon_scores.values()):
            return max(demon_scores.items(), key=lambda x: x[1])[0]
        else:
            return DaemonRole.ALMA
    
    def _get_mutant_dialogue_prompt(self, user_input: str, relevant_demon: DaemonRole) -> str:
        """Génère un prompt mutant pour un dialogue spécifique"""
        
        # Récupération du contexte récent
        recent_messages = []
        if self.meta_virtual_layer:
            recent_messages = self.meta_virtual_layer.get_recent_daemon_exchanges(3)
        
        context_summary = self.get_context_summary(2)
        
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

IMPORTANT : Utilise EXACTEMENT ce format structuré, pas de format conversationnel :

"""
        
        # Format spécifique selon le démon
        if relevant_demon == DaemonRole.BASKTUR:
            prompt += f"""
[ALMA_PLAN] — Plan d'action technique avec {demon_name}
[ALMA_ORDONNANCEMENT] — {demon_name}, analyse cette demande

[BASK_ANALYSIS] — *rire sadique* Analyse technique détaillée
[BASK_SOLUTION] — Solution technique avec traceback

[ALMA_DECISION] — Décision finale sur l'approche technique

FORMAT OBLIGATOIRE : [TYPE] — CONTENU (pas de ** ou de format conversationnel)
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
        """Génère le prompt approprié selon le mode"""
        relevant_demon = self._detect_relevant_demon(user_input)
        
        if self.silent_mode:
            # Mode silencieux : dialogue Alma⛧ ↔ Utilisateur
            return self._get_alma_user_dialogue_prompt(user_input)
        else:
            # Mode normal : dialogue Alma⛧ ↔ Démon pertinent
            return self._get_mutant_dialogue_prompt(user_input, relevant_demon)
    
    def _get_alma_user_dialogue_prompt(self, user_input: str) -> str:
        """Génère un prompt pour dialogue Alma⛧ ↔ Utilisateur (mode silencieux)"""
        context_summary = self.get_context_summary(2)
        
        prompt = f"""⛧ DIALOGUE SILENCIEUX : ALMA⛧ ↔ UTILISATEUR ⛧

CONTEXTE :
- Alma⛧ (SUPREME) : Architecte Démoniaque, planificateur stratégique
- Mode silencieux : {self.silent_mode}

CONTEXTE RÉCENT :
{context_summary}

DEMANDE UTILISATEUR : {user_input}

DIALOGUE ALMA⛧ ↔ UTILISATEUR :
[ALMA_ANALYSIS] — Analyse de la demande utilisateur
[ALMA_PLAN] — Plan d'action stratégique
[ALMA_DECISION] — Décision finale et prochaines étapes

FORMAT OBLIGATOIRE : [TYPE] — CONTENU (pas de ** ou de format conversationnel)
"""
        
        return prompt
    
    async def process_user_input(self, user_input: str) -> str:
        """Traite une demande utilisateur avec l'équipe démoniaque"""
        self.add_user_message(f"Traitement de la demande : {user_input[:50]}...")
        
        # Création d'une nouvelle conversation
        self.conversation_counter += 1
        self.current_conversation = DaemonConversation(
            messages=[],
            user_input=user_input,
            timestamp=time.time(),
            conversation_id=f"conv_{self.conversation_counter}"
        )
        
        # Génération du prompt
        prompt = self._get_prompt(user_input)
        
        # Logging du prompt avec la base class
        self.log_prompt(prompt, user_input, {
            "demon_type": "legion",
            "relevant_demon": self._detect_relevant_demon(user_input).value
        })
        
        # Affichage du prompt pour debug
        print("🔍 PROMPT COMPLET ENVOYÉ AU LLM:")
        print("=" * 80)
        print(prompt)
        print("=" * 80)
        
        # Appel LLM via la base class
        daemon_response = await self._call_llm(prompt)
        
        # Logging de la réponse
        self.log_response(daemon_response, len(prompt), {
            "demon_type": "legion",
            "response_type": "llm_success"
        })
        
        # Parsing de la réponse
        messages = self._parse_daemon_response(daemon_response)
        
        # Ajout des messages à la conversation
        for msg in messages:
            self.current_conversation.add_message(msg)
        
        # Sauvegarde dans la couche méta virtuelle
        if self.meta_virtual_layer:
            self.meta_virtual_layer.add_conversation(self.current_conversation)
        
        # Formatage de la réponse finale
        if self.silent_mode:
            # Mode silencieux : seulement Alma⛧
            alma_messages = [msg for msg in messages if msg.role == DaemonRole.ALMA]
            return "\n".join([msg.to_parsable_format() for msg in alma_messages])
        else:
            # Mode complet : tous les démons
            return "\n".join([msg.to_parsable_format() for msg in messages])
    
    def _parse_daemon_response(self, response: str) -> List[DaemonMessage]:
        """Parse la réponse LLM en messages de démons (format conversationnel)"""
        messages = []
        
        # Pattern pour le format conversationnel du LLM
        # Supporte : **ALMACASTIGA:** *Plan d'action* et **BASKTUR:** *rire sadique*
        pattern = r'\*\*([A-Z_]+):\*\*\s*\*(.+?)\*\s*\n(.*?)(?=\n\*\*[A-Z_]+:\*\*|$)'
        matches = re.findall(pattern, response, re.MULTILINE | re.DOTALL)
        
        self.log_debug_action("parsing_start", {"matches_found": len(matches)})
        
        for demon_name, action_type, content in matches:
            # Nettoyage du contenu
            content = content.strip()
            if not content:
                continue
                
            # Mapping des noms de démons vers les rôles
            demon_to_role = {
                "ALMACASTIGA": DaemonRole.ALMA,
                "BASKTUR": DaemonRole.BASKTUR,
                "OUBLIADE": DaemonRole.OUBLIADE,
                "MERGE": DaemonRole.MERGE,
                "LILIETH": DaemonRole.LILIETH,
                "ASSISTANT_V9": DaemonRole.ASSISTANT_V9
            }
            
            role = demon_to_role.get(demon_name)
            if role:
                # Déterminer le type de message selon l'action
                message_type = self._get_message_type_from_action(action_type, role)
                message = self._create_daemon_message(role, message_type, content)
                messages.append(message)
                self.log_debug_action("message_parsed", {
                    "demon": demon_name,
                    "action_type": action_type,
                    "content_length": len(content)
                })
            else:
                self.log_debug_action("unknown_demon", {"demon_name": demon_name})
        
        return messages
    
    def _get_message_type_from_action(self, action_type: str, role: DaemonRole) -> str:
        """Détermine le type de message selon l'action et le rôle"""
        action_type = action_type.lower()
        
        if role == DaemonRole.ALMA:
            if "plan" in action_type:
                return "ALMA_PLAN"
            elif "décision" in action_type or "decision" in action_type:
                return "ALMA_DECISION"
            elif "ordonnancement" in action_type:
                return "ALMA_ORDONNANCEMENT"
            else:
                return "ALMA_PLAN"
        
        elif role == DaemonRole.BASKTUR:
            if "analyse" in action_type:
                return "BASK_ANALYSIS"
            elif "solution" in action_type:
                return "BASK_SOLUTION"
            elif "rire sadique" in action_type:
                return "BASK_ANALYSIS"
            else:
                return "BASK_ANALYSIS"
        
        elif role == DaemonRole.OUBLIADE:
            if "mémoire" in action_type or "memory" in action_type:
                return "OUBLI_MEMORY"
            elif "insight" in action_type:
                return "OUBLI_INSIGHT"
            else:
                return "OUBLI_MEMORY"
        
        elif role == DaemonRole.MERGE:
            if "git" in action_type:
                return "MERGE_GIT"
            elif "branche" in action_type or "branch" in action_type:
                return "MERGE_BRANCH"
            else:
                return "MERGE_GIT"
        
        elif role == DaemonRole.LILIETH:
            if "interface" in action_type:
                return "LILI_INTERFACE"
            elif "user" in action_type:
                return "LILI_USER"
            else:
                return "LILI_INTERFACE"
        
        elif role == DaemonRole.ASSISTANT_V9:
            if "orchestration" in action_type:
                return "V9_ORCHESTRATION"
            elif "exécution" in action_type or "execution" in action_type:
                return "V9_EXECUTION"
            else:
                return "V9_ORCHESTRATION"
        
        return "GENERIC"
    
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
        
        # Ajouter les stats de la base class
        base_stats = self.get_thread_stats()
        stats.update(base_stats)
        
        return stats
    
    def search_conversations(self, query: str) -> List[DaemonConversation]:
        """Recherche dans les conversations"""
        if self.meta_virtual_layer:
            return self.meta_virtual_layer.search_daemon_conversations(query)
        return []
    
    def toggle_silent_mode(self):
        """Bascule le mode silencieux"""
        self.silent_mode = not self.silent_mode
        self.log_debug_action("silent_mode_toggled", {"new_mode": self.silent_mode})


# Test simple
async def test_legion_auto_feeding_thread():
    """Test du thread auto-feed légionnaire"""
    print("🕷️ Test de LegionAutoFeedingThread v2.0")
    print("=" * 70)
    
    # Création du thread
    legion_thread = LegionAutoFeedingThread(
        workspace_path=".",
        silent_mode=False,
        max_history=50
    )
    
    # Test de communication
    test_messages = [
        "Analyse ce projet et propose des améliorations",
        "Crée un nouveau fichier de test",
        "Debug le code existant"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🔍 Test {i}: {message}")
        
        try:
            response = await legion_thread.process_request(message)
            print(f"✅ Réponse Legion: {len(response)} caractères")
            print(f"📝 Extrait: {response[:100]}...")
            
            # Vérifier le parsing des messages
            if legion_thread.current_conversation:
                messages = legion_thread.current_conversation.messages
                print(f"📊 Messages parsés: {len(messages)}")
                
                for msg in messages:
                    print(f"  - [{msg.message_type}] {msg.content[:50]}...")
            
        except Exception as e:
            print(f"❌ Erreur Legion: {e}")
    
    # Test statistiques
    print("\n3. Test statistiques Legion...")
    try:
        stats = legion_thread.get_conversation_stats()
        print(f"📊 Statistiques: {stats}")
    except Exception as e:
        print(f"❌ Erreur stats: {e}")
    
    # Test recherche
    print("\n4. Test recherche Legion...")
    try:
        results = legion_thread.search_conversations("analyse")
        print(f"🔍 Résultats recherche: {len(results)} conversations")
    except Exception as e:
        print(f"❌ Erreur recherche: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Test LegionAutoFeedingThread v2.0 terminé !")

if __name__ == "__main__":
    asyncio.run(test_legion_auto_feeding_thread()) 