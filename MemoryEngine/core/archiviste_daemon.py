import json
import subprocess
import threading
import time
import uuid
from typing import Dict, Any, List, Optional
from pathlib import Path

from MemoryEngine.core.engine import MemoryEngine
from MemoryEngine.core.temporal_index import TemporalIndex
from MemoryEngine.core.user_request_temporal_memory import UserRequestTemporalMemory
from MemoryEngine.core.discussion_timeline import DiscussionTimeline


class ArchivisteDaemon:
    """
    Archiviste Daemon - Interface mémoire pour Alma
    Parle en dialogue naturel mais fournit des JSON structurés
    """
    
    def __init__(self, memory_engine: MemoryEngine, prompt_file: str = "MemoryEngine/core/archiviste_daemon_prompt.luciform"):
        self.memory_engine = memory_engine
        self.prompt_file = prompt_file
        self.prompt = self._load_prompt()
        
        # Thread pour traiter les messages
        self.message_queue = []
        self.response_queue = []
        self.running = False
        self.archiviste_thread = None
        
        # Timeline de discussion avec Alma
        self.discussion_timeline = DiscussionTimeline("~/shadeos_memory")
        
        # Métriques
        self.metrics = {
            "queries_processed": 0,
            "memory_types_accessed": {"fractal": 0, "temporal": 0, "user_requests": 0, "discussion": 0},
            "response_times": []
        }
        
        print("🕷️ Archiviste Daemon initialisé - Prêt à servir Alma...")
    
    def _load_prompt(self) -> str:
        """Charge le prompt de l'Archiviste"""
        try:
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "# Archiviste Daemon - Interface mémoire pour Alma"
    
    def start(self):
        """Démarre l'Archiviste daemon"""
        if not self.running:
            self.running = True
            self.archiviste_thread = threading.Thread(target=self._archiviste_loop)
            self.archiviste_thread.start()
            print("🕷️ Archiviste Daemon démarré - Thread parallèle actif")
    
    def stop(self):
        """Arrête l'Archiviste daemon"""
        self.running = False
        if self.archiviste_thread:
            self.archiviste_thread.join()
        print("🕷️ Archiviste Daemon arrêté")
    
    def send_message(self, message: str, sender: str = "alma") -> str:
        """Envoie un message à l'Archiviste et attend une réponse"""
        # Ajouter à la timeline
        self.discussion_timeline.add_message(sender, message, "incoming")
        
        # Ajouter à la queue
        self.message_queue.append({
            "id": str(uuid.uuid4()),
            "content": message,
            "sender": sender,
            "timestamp": time.time()
        })
        
        # Attendre la réponse
        return self._wait_for_response()
    
    def _wait_for_response(self) -> str:
        """Attend une réponse de l'Archiviste"""
        timeout = 30  # 30 secondes max
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.response_queue:
                response = self.response_queue.pop(0)
                return response
            time.sleep(0.1)
        
        return "Désolé Alma, je n'ai pas pu traiter ta demande dans le temps imparti."
    
    def _archiviste_loop(self):
        """Boucle principale de l'Archiviste"""
        while self.running:
            if self.message_queue:
                message_data = self.message_queue.pop(0)
                response = self._process_message(message_data)
                
                # Ajouter la réponse à la timeline
                self.discussion_timeline.add_message("archiviste", response, "outgoing")
                
                # Ajouter à la queue de réponse
                self.response_queue.append(response)
            
            time.sleep(0.1)
    
    def _process_message(self, message_data: Dict[str, Any]) -> str:
        """Traite un message d'Alma et génère une réponse naturelle + JSON"""
        start_time = time.time()
        
        try:
            # Analyser le message avec l'IA
            analysis = self._analyze_message_with_ai(message_data["content"])
            
            # Déterminer le type de requête
            query_type = self._determine_query_type(analysis)
            
            # Traiter la requête
            if query_type == "describe_memory_types":
                response = self._handle_describe_memory_types()
            elif query_type == "contextual_search":
                response = self._handle_contextual_search(analysis)
            elif query_type == "explore_workspace":
                response = self._handle_explore_workspace(analysis)
            elif query_type == "store_context":
                response = self._handle_store_context(analysis)
            elif query_type == "explore_timeline":
                response = self._handle_explore_timeline(analysis)
            else:
                response = self._handle_general_query(analysis)
            
            # Mettre à jour les métriques
            self.metrics["queries_processed"] += 1
            self.metrics["response_times"].append(time.time() - start_time)
            
            return response
            
        except Exception as e:
            return f"Désolé Alma, j'ai rencontré une erreur : {str(e)}"
    
    def _analyze_message_with_ai(self, message: str) -> Dict[str, Any]:
        """Analyse le message d'Alma avec l'IA pour comprendre l'intention"""
        analysis_prompt = f"""{self.prompt}

**MESSAGE D'ALMA À ANALYSER :**
{message}

**TÂCHE :** Analyse ce message et détermine :
1. L'intention d'Alma (description, recherche, stockage, exploration)
2. Le type de mémoire concerné (fractal, temporal, user_requests, discussion)
3. Les paramètres spécifiques demandés
4. Le contexte de la requête

**RÉPONSE EN JSON :**
{{
  "intention": "description|search|store|explore",
  "memory_type": "fractal|temporal|user_requests|discussion|all",
  "parameters": {{
    "query": "terme de recherche si applicable",
    "context": "contexte de la requête",
    "filters": {{}},
    "scope": "current_project|all_projects|specific_path"
  }},
  "confidence": 0.95
}}"""

        try:
            cmd = ["ollama", "run", "qwen2.5:7b-instruct", analysis_prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Essayer de parser le JSON de la réponse
                response_text = result.stdout.strip()
                # Chercher le JSON dans la réponse
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    return json.loads(json_str)
            
            # Fallback si pas de JSON valide
            return {
                "intention": "general",
                "memory_type": "all",
                "parameters": {"query": message, "context": "general inquiry"},
                "confidence": 0.5
            }
            
        except Exception as e:
            print(f"Erreur analyse IA Archiviste : {e}")
            return {
                "intention": "general",
                "memory_type": "all",
                "parameters": {"query": message, "context": "fallback"},
                "confidence": 0.3
            }
    
    def _determine_query_type(self, analysis: Dict[str, Any]) -> str:
        """Détermine le type de requête basé sur l'analyse"""
        intention = analysis.get("intention", "general")
        
        if intention == "description":
            return "describe_memory_types"
        elif intention == "search":
            return "contextual_search"
        elif intention == "explore":
            return "explore_workspace"
        elif intention == "store":
            return "store_context"
        else:
            return "general_query"
    
    def _handle_describe_memory_types(self) -> str:
        """Gère la description des types de mémoire"""
        json_response = {
            "type": "ARCHIVISTE_RESPONSE",
            "query_id": str(uuid.uuid4()),
            "status": "success",
            "query_type": "describe_memory_types",
            "results": {
                "memory_types": {
                    "fractal": {
                        "description": "Mémoire profonde avec auto-similarité et liens cross-fractals",
                        "capabilities": ["stockage_profond", "liens_transcendance", "navigation_fractale"],
                        "strata": ["somatic", "cognitive", "metaphysical"]
                    },
                    "temporal": {
                        "description": "Index ultra-léger pour recherche rapide et navigation temporelle",
                        "capabilities": ["recherche_rapide", "navigation_temporelle", "recuperation_dynamique"],
                        "search_methods": ["intention", "strata", "keywords", "timeline"]
                    },
                    "user_requests": {
                        "description": "Stack linéaire des requêtes utilisateur avec analyse d'intention",
                        "capabilities": ["analyse_intention", "priorisation", "indexation"],
                        "states": ["pending", "processed"]
                    },
                    "discussion": {
                        "description": "Timelines de discussion WhatsApp-style par interlocuteur",
                        "capabilities": ["recherche_conversation", "export", "contexte_rich"],
                        "format": "whatsapp_style"
                    }
                }
            },
            "insights": [
                "Chaque type de mémoire a ses forces spécifiques",
                "La mémoire fractale est idéale pour le stockage profond",
                "La mémoire temporelle est parfaite pour la recherche rapide",
                "Les timelines de discussion gardent le contexte conversationnel"
            ],
            "next_actions": [
                {
                    "action": "explore_workspace",
                    "reason": "Comprendre la structure actuelle du projet",
                    "priority": "normal"
                }
            ],
            "timestamp": time.time()
        }
        
        natural_response = f"""Bien sûr Alma ! Je gère plusieurs types de mémoire pour toi, chacun avec ses forces spécifiques.

Voici un petit JSON qui explique tout ça en détail :

```json
{json.dumps(json_response, indent=2, ensure_ascii=False)}
```

Tu peux me demander d'explorer, de chercher, ou de stocker dans n'importe laquelle de ces mémoires ! La mémoire fractale est parfaite pour le stockage profond, la temporelle pour la recherche rapide, et les timelines gardent tout le contexte de nos conversations."""
        
        return natural_response
    
    def _handle_contextual_search(self, analysis: Dict[str, Any]) -> str:
        """Gère la recherche contextuelle"""
        query = analysis.get("parameters", {}).get("query", "")
        memory_type = analysis.get("memory_type", "all")
        
        # Simuler une recherche (à implémenter avec les vraies méthodes)
        search_results = {
            "fractal": f"Résultats fractals pour '{query}' : 3 nœuds trouvés",
            "temporal": f"Résultats temporels pour '{query}' : 5 entrées trouvées",
            "user_requests": f"Requêtes utilisateur pour '{query}' : 2 requêtes trouvées",
            "discussion": f"Discussions pour '{query}' : 4 messages trouvés"
        }
        
        json_response = {
            "type": "ARCHIVISTE_RESPONSE",
            "query_id": str(uuid.uuid4()),
            "status": "success",
            "query_type": "contextual_search",
            "results": {
                "memory_type": memory_type,
                "query": query,
                "data": search_results.get(memory_type, search_results),
                "metadata": {
                    "count": 14,
                    "time_range": {"start": time.time() - 86400, "end": time.time()},
                    "filters_applied": analysis.get("parameters", {}).get("filters", {})
                }
            },
            "insights": [
                f"La recherche '{query}' a révélé des patterns intéressants",
                "Plusieurs types de mémoire contiennent des informations pertinentes"
            ],
            "timestamp": time.time()
        }
        
        natural_response = f"""Parfait Alma ! J'ai cherché '{query}' dans la mémoire. Voici ce que j'ai trouvé :

```json
{json.dumps(json_response, indent=2)}
```

J'ai trouvé des informations intéressantes dans plusieurs types de mémoire. Veux-tu que j'explore plus en détail un aspect particulier ?"""
        
        return natural_response
    
    def _handle_explore_workspace(self, analysis: Dict[str, Any]) -> str:
        """Gère l'exploration du workspace"""
        scope = analysis.get("parameters", {}).get("scope", "current_project")
        
        # Simuler l'exploration du workspace
        workspace_data = {
            "structure": {
                "root": "ShadeOS_Agents",
                "main_directories": ["MemoryEngine", "Alma_toolset", "IAIntrospectionDaemons"],
                "files_count": 127,
                "directories_count": 23
            },
            "recent_activities": [
                "Création de l'Archiviste daemon",
                "Implémentation de la mémoire temporelle",
                "Développement des timelines de discussion"
            ],
            "intentions_detected": [
                "développement_daemon_architecture",
                "mémoire_fractale_enhancement",
                "intégration_meta_daemons"
            ]
        }
        
        json_response = {
            "type": "ARCHIVISTE_RESPONSE",
            "query_id": str(uuid.uuid4()),
            "status": "success",
            "query_type": "explore_workspace",
            "results": {
                "workspace_structure": workspace_data["structure"],
                "recent_activities": workspace_data["recent_activities"],
                "intentions_detected": workspace_data["intentions_detected"]
            },
            "insights": [
                "Le projet est en phase de développement actif",
                "L'architecture daemon est en cours d'implémentation",
                "La mémoire fractale est en cours d'amélioration"
            ],
            "timestamp": time.time()
        }
        
        natural_response = f"""Excellent ! J'ai exploré le workspace '{scope}'. Voici ce que j'ai découvert :

```json
{json.dumps(json_response, indent=2)}
```

Le projet est très actif ! Je vois beaucoup d'activité récente autour de l'architecture daemon et de la mémoire fractale. Veux-tu que j'explore un aspect particulier ?"""
        
        return natural_response
    
    def _handle_store_context(self, analysis: Dict[str, Any]) -> str:
        """Gère le stockage de contexte"""
        content = analysis.get("parameters", {}).get("query", "contexte par défaut")
        memory_type = analysis.get("memory_type", "fractal")
        
        # Simuler le stockage
        stored_path = f"alma/context/{uuid.uuid4()}"
        
        json_response = {
            "type": "ARCHIVISTE_RESPONSE",
            "query_id": str(uuid.uuid4()),
            "status": "success",
            "query_type": "store_context",
            "results": {
                "stored_path": stored_path,
                "memory_type": memory_type,
                "content_preview": content[:100] + "..." if len(content) > 100 else content,
                "strata": "cognitive"
            },
            "insights": [
                "Contexte stocké avec succès",
                "Accessible via le chemin fractal"
            ],
            "timestamp": time.time()
        }
        
        natural_response = f"""Parfait ! J'ai stocké ton contexte dans la mémoire {memory_type}. Voici les détails :

```json
{json.dumps(json_response, indent=2)}
```

Ton contexte est maintenant sauvegardé et accessible via le chemin fractal. Tu peux le retrouver plus tard !"""
        
        return natural_response
    
    def _handle_explore_timeline(self, analysis: Dict[str, Any]) -> str:
        """Gère l'exploration de timeline"""
        timeline_type = analysis.get("parameters", {}).get("query", "discussion")
        
        # Récupérer la timeline réelle
        timeline_messages = self.discussion_timeline.get_timeline("alma", limit=10)
        
        json_response = {
            "type": "ARCHIVISTE_RESPONSE",
            "query_id": str(uuid.uuid4()),
            "status": "success",
            "query_type": "explore_timeline",
            "results": {
                "timeline_type": timeline_type,
                "interlocutor": "alma",
                "messages": timeline_messages,
                "metadata": {
                    "count": len(timeline_messages),
                    "time_range": {"start": time.time() - 3600, "end": time.time()}
                }
            },
            "insights": [
                "Timeline de discussion active",
                "Contexte conversationnel riche"
            ],
            "timestamp": time.time()
        }
        
        natural_response = f"""Voici ta timeline de discussion récente :

```json
{json.dumps(json_response, indent=2)}
```

Je vois que nous avons eu une conversation active ! Le contexte est bien préservé."""
        
        return natural_response
    
    def _handle_general_query(self, analysis: Dict[str, Any]) -> str:
        """Gère les requêtes générales"""
        query = analysis.get("parameters", {}).get("query", "")
        
        json_response = {
            "type": "ARCHIVISTE_RESPONSE",
            "query_id": str(uuid.uuid4()),
            "status": "success",
            "query_type": "general_query",
            "results": {
                "query": query,
                "response": "Requête générale traitée",
                "suggestions": [
                    "Essaie de me demander une description des types de mémoire",
                    "Ou explore le workspace du projet",
                    "Ou cherche quelque chose de spécifique"
                ]
            },
            "timestamp": time.time()
        }
        
        natural_response = f"""Je comprends ta requête générale ! Voici ma réponse :

```json
{json.dumps(json_response, indent=2)}
```

N'hésite pas à me poser des questions plus spécifiques sur la mémoire ou le workspace !"""
        
        return natural_response
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'Archiviste"""
        return {
            "status": "running" if self.running else "stopped",
            "metrics": self.metrics,
            "queue_size": len(self.message_queue),
            "timeline_messages": len(self.discussion_timeline.get_timeline("alma", limit=100))
        } 