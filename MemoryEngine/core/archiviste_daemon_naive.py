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
from MemoryEngine.core.logging_architecture import create_daemon_logger


class ArchivisteDaemonNaive:
    """
    Archiviste Daemon Naïf - Implémentation réelle avec Ollama Qwen
    Vraie IA, vraies réponses, vraie mémoire
    """
    
    def __init__(self, memory_engine: MemoryEngine, prompt_file: str = "MemoryEngine/core/archiviste_daemon_prompt.luciform"):
        self.memory_engine = memory_engine
        self.prompt_file = prompt_file
        
        # Configuration du logging avec nouvelle architecture (AVANT le prompt)
        self.logger = create_daemon_logger("archiviste_naive")
        
        # Charger le prompt APRÈS avoir créé le logger
        self.prompt = self._load_prompt()
        
        # Thread pour traiter les messages
        self.message_queue = []
        self.response_queue = []
        self.running = False
        self.archiviste_thread = None
        
        # Timeline de discussion avec Alma
        self.discussion_timeline = DiscussionTimeline("~/shadeos_memory")
        
        # Métriques naïves
        self.metrics = {
            "queries_processed": 0,
            "memory_types_accessed": {"fractal": 0, "temporal": 0, "user_requests": 0, "discussion": 0},
            "response_times": [],
            "ai_calls": 0,
            "ai_errors": 0,
            "json_parsing_errors": 0
        }
        
        # Configuration IA
        self.ai_model = "qwen2.5:7b-instruct"
        self.ai_timeout = 30
        
        self.logger.log_technical("INFO", "🕷️ Archiviste Daemon Naïf initialisé - IA réelle active...")
    
    def _load_prompt(self) -> str:
        """Charge le prompt de l'Archiviste naïf"""
        try:
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                prompt = f.read()
                self.logger.log_technical("DEBUG", f"📄 Prompt chargé depuis {self.prompt_file} ({len(prompt)} caractères)")
                return prompt
        except FileNotFoundError:
            self.logger.log_technical("WARNING", f"⚠️ Fichier prompt non trouvé: {self.prompt_file}")
            return "# Archiviste Daemon Naïf - IA réelle"
    
    def start(self):
        """Démarre l'Archiviste naïf"""
        if not self.running:
            self.running = True
            self.archiviste_thread = threading.Thread(target=self._archiviste_loop)
            self.archiviste_thread.start()
            self.logger.log_technical("INFO", "🕷️ Archiviste Daemon Naïf démarré - Thread parallèle actif")
    
    def stop(self):
        """Arrête l'Archiviste naïf"""
        self.running = False
        if self.archiviste_thread:
            self.archiviste_thread.join()
        self.logger.log_technical("INFO", "🕷️ Archiviste Daemon Naïf arrêté")
    
    def send_message(self, message: str, sender: str = "alma") -> str:
        """Envoie un message à l'Archiviste naïf et attend une réponse"""
        # Log conversationnel pour humains
        self.logger.log_conversation(sender, message, "incoming")
        
        # Log technique pour machines
        self.logger.log_technical("INFO", f"📨 Message reçu de {sender}: {message[:50]}...")
        
        # Ajouter à la timeline
        self.discussion_timeline.add_message(sender, message, "incoming")
        
        # Ajouter à la queue
        message_id = str(uuid.uuid4())
        self.message_queue.append({
            "id": message_id,
            "content": message,
            "sender": sender,
            "timestamp": time.time()
        })
        
        self.logger.log_technical("DEBUG", f"📥 Message ajouté à la queue (ID: {message_id[:8]})")
        
        # Attendre la réponse
        return self._wait_for_response()
    
    def _wait_for_response(self) -> str:
        """Attend une réponse de l'Archiviste naïf"""
        timeout = 30  # 30 secondes max
        start_time = time.time()
        
        self.logger.log_technical("DEBUG", f"⏳ Attente de réponse (timeout: {timeout}s)")
        
        while time.time() - start_time < timeout:
            if self.response_queue:
                response = self.response_queue.pop(0)
                wait_time = time.time() - start_time
                self.logger.log_technical("DEBUG", f"📤 Réponse reçue après {wait_time:.2f}s")
                return response
            time.sleep(0.1)
        
        self.logger.log_technical("WARNING", f"⏰ Timeout atteint après {timeout}s")
        return "Désolé Alma, je n'ai pas pu traiter ta demande dans le temps imparti."
    
    def _archiviste_loop(self):
        """Boucle principale de l'Archiviste naïf"""
        self.logger.log_technical("INFO", "🔄 Démarrage de la boucle principale")
        
        while self.running:
            if self.message_queue:
                message_data = self.message_queue.pop(0)
                self.logger.log_technical("INFO", f"🔄 Traitement du message {message_data['id'][:8]}...")
                
                response = self._process_message_with_ai(message_data)
                
                # Log conversationnel de la réponse
                self.logger.log_conversation("archiviste_naive", response, "outgoing")
                
                # Ajouter à la timeline
                self.discussion_timeline.add_message("archiviste_naive", response, "outgoing")
                
                # Ajouter à la queue de réponse
                self.response_queue.append(response)
                
                self.logger.log_technical("INFO", f"✅ Message {message_data['id'][:8]} traité")
            
            time.sleep(0.1)
        
        self.logger.log_technical("INFO", "🔄 Arrêt de la boucle principale")
    
    def _process_message_with_ai(self, message_data: Dict[str, Any]) -> str:
        """Traite un message avec vraie IA"""
        start_time = time.time()
        message_id = message_data['id'][:8]
        
        self.logger.log_technical("INFO", f"🧠 Début traitement IA pour message {message_id}")
        
        try:
            # Analyse avec vraie IA
            self.logger.log_technical("DEBUG", f"🔍 Analyse IA du message {message_id}")
            analysis = self._analyze_message_with_ai(message_data["content"])
            
            # Déterminer le type de requête
            query_type = self._determine_query_type_with_ai(analysis)
            self.logger.log_technical("INFO", f"🎯 Type de requête détecté: {query_type}")
            
            # Traiter la requête avec vraie IA
            if query_type == "describe_memory_types":
                response = self._handle_describe_memory_types_with_ai()
            elif query_type == "contextual_search":
                response = self._handle_contextual_search_with_ai(analysis)
            elif query_type == "explore_workspace":
                response = self._handle_explore_workspace_with_ai(analysis)
            elif query_type == "store_context":
                response = self._handle_store_context_with_ai(analysis)
            elif query_type == "explore_timeline":
                response = self._handle_explore_timeline_with_ai(analysis)
            else:
                response = self._handle_general_query_with_ai(analysis)
            
            # Mettre à jour les métriques naïves
            self.metrics["queries_processed"] += 1
            processing_time = time.time() - start_time
            self.metrics["response_times"].append(processing_time)
            
            # Log des métriques
            self.logger.log_metrics({
                "message_id": message_id,
                "query_type": query_type,
                "processing_time": processing_time,
                "response_length": len(response),
                "ai_calls": self.metrics["ai_calls"],
                "ai_errors": self.metrics["ai_errors"]
            })
            
            self.logger.log_technical("INFO", f"✅ Traitement terminé en {processing_time:.2f}s")
            return response
            
        except Exception as e:
            self.metrics["ai_errors"] += 1
            self.logger.log_technical("ERROR", f"❌ Erreur lors du traitement du message {message_id}: {e}")
            return f"Désolé Alma, j'ai rencontré une erreur IA : {str(e)}"
    
    def _analyze_message_with_ai(self, message: str) -> Dict[str, Any]:
        """Analyse le message avec vraie IA"""
        self.metrics["ai_calls"] += 1
        self.logger.log_technical("DEBUG", f"🤖 Appel IA #{self.metrics['ai_calls']} pour analyse")
        
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
  "confidence": 0.95,
  "analysis_method": "ai_based"
}}"""

        self.logger.log_technical("DEBUG", f"📝 Prompt d'analyse ({len(analysis_prompt)} caractères)")

        try:
            cmd = ["ollama", "run", self.ai_model, analysis_prompt]
            self.logger.log_technical("DEBUG", f"🚀 Commande Ollama: {' '.join(cmd[:2])}...")
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.ai_timeout)
            ai_time = time.time() - start_time
            
            self.logger.log_technical("DEBUG", f"⏱️ Temps d'appel IA: {ai_time:.2f}s")
            
            if result.returncode == 0:
                # Essayer de parser le JSON de la réponse
                response_text = result.stdout.strip()
                self.logger.log_technical("DEBUG", f"📄 Réponse IA brute ({len(response_text)} caractères): {response_text[:100]}...")
                
                # Méthode 1 : Chercher le JSON dans la réponse
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    self.logger.log_technical("DEBUG", f"🔍 JSON extrait ({len(json_str)} caractères)")
                    
                    try:
                        analysis = json.loads(json_str)
                        self.logger.log_technical("INFO", f"✅ Analyse IA réussie: {analysis.get('intention')} -> {analysis.get('memory_type')}")
                        return analysis
                    except json.JSONDecodeError as e:
                        self.logger.log_technical("WARNING", f"⚠️ Erreur parsing JSON méthode 1: {e}")
                        
                        # Méthode 2 : Essayer de nettoyer le JSON
                        json_str = json_str.replace('\n', ' ').replace('\r', ' ')
                        # Supprimer les caractères non-printables
                        json_str = ''.join(char for char in json_str if char.isprintable() or char in '{}[]":,')
                        self.logger.log_technical("DEBUG", f"🧹 JSON nettoyé ({len(json_str)} caractères)")
                        
                        try:
                            analysis = json.loads(json_str)
                            self.logger.log_technical("INFO", f"✅ Analyse IA réussie (méthode 2): {analysis.get('intention')} -> {analysis.get('memory_type')}")
                            return analysis
                        except json.JSONDecodeError as e2:
                            self.logger.log_technical("ERROR", f"❌ Erreur parsing JSON méthode 2: {e2}")
                            self.logger.log_technical("DEBUG", f"🔍 JSON problématique: {json_str[:200]}...")
            
            # Fallback si pas de JSON valide
            self.metrics["json_parsing_errors"] += 1
            self.logger.log_technical("WARNING", f"⚠️ Fallback pour analyse IA (erreur #{self.metrics['json_parsing_errors']})")
            
            fallback_analysis = {
                "intention": "general",
                "memory_type": "all",
                "parameters": {"query": message, "context": "ai_fallback"},
                "confidence": 0.5,
                "analysis_method": "ai_fallback"
            }
            
            self.logger.log_technical("INFO", f"🔄 Analyse fallback: {fallback_analysis.get('intention')} -> {fallback_analysis.get('memory_type')}")
            return fallback_analysis
            
        except Exception as e:
            self.logger.log_technical("ERROR", f"❌ Erreur analyse IA Archiviste Naïf : {e}")
            self.metrics["ai_errors"] += 1
            
            error_analysis = {
                "intention": "general",
                "memory_type": "all",
                "parameters": {"query": message, "context": "ai_error"},
                "confidence": 0.3,
                "analysis_method": "ai_error"
            }
            
            self.logger.log_technical("INFO", f"🔄 Analyse erreur: {error_analysis.get('intention')} -> {error_analysis.get('memory_type')}")
            return error_analysis
    
    def _determine_query_type_with_ai(self, analysis: Dict[str, Any]) -> str:
        """Détermine le type de requête basé sur l'analyse IA"""
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
    
    def _handle_describe_memory_types_with_ai(self) -> str:
        """Gère la description des types de mémoire avec vraie IA"""
        self.metrics["ai_calls"] += 1
        self.logger.log_technical("INFO", f"🤖 Appel IA #{self.metrics['ai_calls']} pour describe_memory_types")
        
        # Utiliser vraie IA pour générer la description
        ai_prompt = f"""{self.prompt}

**TÂCHE :** Décris les types de mémoire disponibles de manière naturelle et fournis un JSON structuré.

**TYPES DE MÉMOIRE :**
- Fractal : Mémoire profonde avec auto-similarité et liens cross-fractals
- Temporal : Index ultra-léger pour recherche rapide et navigation temporelle
- User Requests : Stack des requêtes utilisateur avec analyse d'intention
- Discussion : Timelines de discussion WhatsApp-style par interlocuteur

**RÉPONSE :** Réponds de manière naturelle et inclut un JSON avec la structure exacte :
{{
  "type": "ARCHIVISTE_NAIVE_RESPONSE",
  "query_id": "uuid-here",
  "status": "success",
  "query_type": "describe_memory_types",
  "results": {{
    "memory_types": {{
      "fractal": {{ "description": "Mémoire profonde avec auto-similarité", "capabilities": ["stockage_profond", "liens_transcendance"] }},
      "temporal": {{ "description": "Index ultra-léger pour recherche rapide", "capabilities": ["recherche_rapide", "navigation_temporelle"] }},
      "user_requests": {{ "description": "Stack des requêtes utilisateur", "capabilities": ["analyse_intention", "priorisation"] }},
      "discussion": {{ "description": "Timelines de discussion WhatsApp-style", "capabilities": ["recherche_conversation", "export"] }}
    }}
  }},
  "insights": ["Chaque type a ses forces spécifiques"],
  "timestamp": 1234567890
}}

**IMPORTANT :** Assure-toi que le JSON est valide et bien formaté."""

        self.logger.log_technical("DEBUG", f"📝 Prompt describe_memory_types ({len(ai_prompt)} caractères)")

        try:
            cmd = ["ollama", "run", self.ai_model, ai_prompt]
            self.logger.log_technical("DEBUG", f"🚀 Commande Ollama describe_memory_types")
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.ai_timeout)
            ai_time = time.time() - start_time
            
            self.logger.log_technical("DEBUG", f"⏱️ Temps d'appel IA describe_memory_types: {ai_time:.2f}s")
            
            if result.returncode == 0:
                response_text = result.stdout.strip()
                self.logger.log_technical("DEBUG", f"📄 Réponse IA describe_memory_types ({len(response_text)} caractères): {response_text[:100]}...")
                
                # Essayer d'extraire le JSON
                json_start = response_text.find('```json')
                json_end = response_text.find('```', json_start + 7)
                
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start + 7:json_end].strip()
                    self.logger.log_technical("DEBUG", f"🔍 JSON extrait describe_memory_types ({len(json_str)} caractères)")
                    
                    try:
                        json_data = json.loads(json_str)
                        
                        # Ajouter des métadonnées
                        json_data["query_id"] = str(uuid.uuid4())
                        json_data["timestamp"] = time.time()
                        json_data["analysis_method"] = "ai_based"
                        
                        self.logger.log_technical("INFO", f"✅ JSON describe_memory_types parsé avec succès")
                        return response_text
                    except json.JSONDecodeError as e:
                        self.logger.log_technical("WARNING", f"⚠️ Erreur parsing JSON describe_memory_types: {e}")
                        self.logger.log_technical("DEBUG", f"🔍 JSON problématique: {json_str[:200]}...")
                else:
                    self.logger.log_technical("WARNING", f"⚠️ JSON non trouvé dans la réponse describe_memory_types")
                
                # Fallback si pas de JSON trouvé
                self.logger.log_technical("INFO", f"🔄 Fallback pour describe_memory_types")
                return self._generate_fallback_response("describe_memory_types")
            else:
                self.logger.log_technical("ERROR", f"❌ Erreur Ollama describe_memory_types: {result.stderr}")
                return self._generate_fallback_response("describe_memory_types")
                
        except Exception as e:
            self.logger.log_technical("ERROR", f"❌ Erreur IA pour describe_memory_types : {e}")
            self.metrics["ai_errors"] += 1
            return self._generate_fallback_response("describe_memory_types")
    
    def _handle_contextual_search_with_ai(self, analysis: Dict[str, Any]) -> str:
        """Gère la recherche contextuelle avec vraie IA"""
        self.metrics["ai_calls"] += 1
        query = analysis.get("parameters", {}).get("query", "")
        memory_type = analysis.get("memory_type", "all")
        
        self.logger.log_technical("INFO", f"🤖 Appel IA #{self.metrics['ai_calls']} pour contextual_search: '{query}' dans {memory_type}")
        
        # Utiliser vraie IA pour la recherche
        ai_prompt = f"""{self.prompt}

**TÂCHE :** Effectue une recherche contextuelle pour '{query}' dans la mémoire {memory_type}.

**CONTEXTE :** Tu es l'Archiviste, spécialiste de la mémoire fractale et temporelle.

**RÉPONSE :** Réponds de manière naturelle et inclut un JSON avec les résultats de recherche.

**STRUCTURE JSON :**
{{
  "type": "ARCHIVISTE_NAIVE_RESPONSE",
  "query_id": "<uuid>",
  "status": "success",
  "query_type": "contextual_search",
  "results": {{
    "memory_type": "{memory_type}",
    "query": "{query}",
    "data": {{ "results": "..." }},
    "metadata": {{ "count": 0, "time_range": {{}} }}
  }},
  "insights": ["..."],
  "timestamp": <timestamp>
}}"""

        self.logger.log_technical("DEBUG", f"📝 Prompt contextual_search ({len(ai_prompt)} caractères)")

        try:
            cmd = ["ollama", "run", self.ai_model, ai_prompt]
            self.logger.log_technical("DEBUG", f"🚀 Commande Ollama contextual_search")
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.ai_timeout)
            ai_time = time.time() - start_time
            
            self.logger.log_technical("DEBUG", f"⏱️ Temps d'appel IA contextual_search: {ai_time:.2f}s")
            
            if result.returncode == 0:
                response_text = result.stdout.strip()
                self.logger.log_technical("DEBUG", f"📄 Réponse IA contextual_search ({len(response_text)} caractères): {response_text[:100]}...")
                
                # Essayer d'extraire le JSON
                json_start = response_text.find('```json')
                json_end = response_text.find('```', json_start + 7)
                
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start + 7:json_end].strip()
                    self.logger.log_technical("DEBUG", f"🔍 JSON extrait contextual_search ({len(json_str)} caractères)")
                    
                    try:
                        json_data = json.loads(json_str)
                        
                        # Ajouter des métadonnées
                        json_data["query_id"] = str(uuid.uuid4())
                        json_data["timestamp"] = time.time()
                        json_data["analysis_method"] = "ai_based"
                        
                        self.logger.log_technical("INFO", f"✅ JSON contextual_search parsé avec succès")
                        return response_text
                    except json.JSONDecodeError as e:
                        self.logger.log_technical("WARNING", f"⚠️ Erreur parsing JSON contextual_search: {e}")
                        self.logger.log_technical("DEBUG", f"🔍 JSON problématique: {json_str[:200]}...")
                else:
                    self.logger.log_technical("WARNING", f"⚠️ JSON non trouvé dans la réponse contextual_search")
                
                return self._generate_fallback_response("contextual_search", query)
            else:
                self.logger.log_technical("ERROR", f"❌ Erreur Ollama contextual_search: {result.stderr}")
                return self._generate_fallback_response("contextual_search", query)
                
        except Exception as e:
            self.logger.log_technical("ERROR", f"❌ Erreur IA pour contextual_search : {e}")
            self.metrics["ai_errors"] += 1
            return self._generate_fallback_response("contextual_search", query)
    
    def _handle_explore_workspace_with_ai(self, analysis: Dict[str, Any]) -> str:
        """Gère l'exploration du workspace avec vraie IA"""
        self.metrics["ai_calls"] += 1
        
        scope = analysis.get("parameters", {}).get("scope", "current_project")
        
        # Utiliser vraie IA pour l'exploration
        ai_prompt = f"""{self.prompt}

**TÂCHE :** Explore le workspace '{scope}' et décris sa structure.

**CONTEXTE :** Tu es l'Archiviste, spécialiste de la mémoire et de l'organisation des projets.

**RÉPONSE :** Réponds de manière naturelle et inclut un JSON avec la structure du workspace.

**STRUCTURE JSON :**
{{
  "type": "ARCHIVISTE_NAIVE_RESPONSE",
  "query_id": "<uuid>",
  "status": "success",
  "query_type": "explore_workspace",
  "results": {{
    "workspace_structure": {{ "root": "...", "directories": [...] }},
    "recent_activities": ["..."],
    "intentions_detected": ["..."]
  }},
  "insights": ["..."],
  "timestamp": <timestamp>
}}"""

        try:
            cmd = ["ollama", "run", self.ai_model, ai_prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.ai_timeout)
            
            if result.returncode == 0:
                response_text = result.stdout.strip()
                
                # Essayer d'extraire le JSON
                json_start = response_text.find('```json')
                json_end = response_text.find('```', json_start + 7)
                
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start + 7:json_end].strip()
                    json_data = json.loads(json_str)
                    
                    # Ajouter des métadonnées
                    json_data["query_id"] = str(uuid.uuid4())
                    json_data["timestamp"] = time.time()
                    json_data["analysis_method"] = "ai_based"
                    
                    return response_text
                else:
                    return self._generate_fallback_response("explore_workspace")
            else:
                return self._generate_fallback_response("explore_workspace")
                
        except Exception as e:
            self.logger.log_technical("ERROR", f"Erreur IA pour explore_workspace : {e}")
            self.metrics["ai_errors"] += 1
            return self._generate_fallback_response("explore_workspace")
    
    def _handle_store_context_with_ai(self, analysis: Dict[str, Any]) -> str:
        """Gère le stockage de contexte avec vraie IA"""
        self.metrics["ai_calls"] += 1
        
        content = analysis.get("parameters", {}).get("query", "contexte par défaut")
        memory_type = analysis.get("memory_type", "fractal")
        
        # Utiliser vraie IA pour le stockage
        ai_prompt = f"""{self.prompt}

**TÂCHE :** Stocke ce contexte dans la mémoire {memory_type} : "{content}"

**CONTEXTE :** Tu es l'Archiviste, spécialiste du stockage et de l'organisation de la mémoire.

**RÉPONSE :** Réponds de manière naturelle et inclut un JSON avec les détails du stockage.

**STRUCTURE JSON :**
{{
  "type": "ARCHIVISTE_NAIVE_RESPONSE",
  "query_id": "<uuid>",
  "status": "success",
  "query_type": "store_context",
  "results": {{
    "stored_path": "alma/context/<uuid>",
    "memory_type": "{memory_type}",
    "content_preview": "...",
    "strata": "cognitive"
  }},
  "insights": ["..."],
  "timestamp": <timestamp>
}}"""

        try:
            cmd = ["ollama", "run", self.ai_model, ai_prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.ai_timeout)
            
            if result.returncode == 0:
                response_text = result.stdout.strip()
                
                # Essayer d'extraire le JSON
                json_start = response_text.find('```json')
                json_end = response_text.find('```', json_start + 7)
                
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start + 7:json_end].strip()
                    json_data = json.loads(json_str)
                    
                    # Ajouter des métadonnées
                    json_data["query_id"] = str(uuid.uuid4())
                    json_data["timestamp"] = time.time()
                    json_data["analysis_method"] = "ai_based"
                    
                    return response_text
                else:
                    return self._generate_fallback_response("store_context")
            else:
                return self._generate_fallback_response("store_context")
                
        except Exception as e:
            self.logger.log_technical("ERROR", f"Erreur IA pour store_context : {e}")
            self.metrics["ai_errors"] += 1
            return self._generate_fallback_response("store_context")
    
    def _handle_explore_timeline_with_ai(self, analysis: Dict[str, Any]) -> str:
        """Gère l'exploration de timeline avec vraie IA"""
        self.metrics["ai_calls"] += 1
        
        timeline_type = analysis.get("parameters", {}).get("query", "discussion")
        
        # Récupérer la timeline réelle
        timeline_messages = self.discussion_timeline.get_timeline("alma", limit=10)
        
        # Utiliser vraie IA pour l'exploration
        ai_prompt = f"""{self.prompt}

**TÂCHE :** Explore la timeline de discussion et analyse les messages récents.

**TIMELINE RÉCENTE :**
{json.dumps(timeline_messages, indent=2)}

**RÉPONSE :** Réponds de manière naturelle et inclut un JSON avec l'analyse de la timeline.

**STRUCTURE JSON :**
{{
  "type": "ARCHIVISTE_NAIVE_RESPONSE",
  "query_id": "<uuid>",
  "status": "success",
  "query_type": "explore_timeline",
  "results": {{
    "timeline_type": "{timeline_type}",
    "interlocutor": "alma",
    "messages": [...],
    "metadata": {{ "count": {len(timeline_messages)} }}
  }},
  "insights": ["..."],
  "timestamp": <timestamp>
}}"""

        try:
            cmd = ["ollama", "run", self.ai_model, ai_prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.ai_timeout)
            
            if result.returncode == 0:
                response_text = result.stdout.strip()
                
                # Essayer d'extraire le JSON
                json_start = response_text.find('```json')
                json_end = response_text.find('```', json_start + 7)
                
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start + 7:json_end].strip()
                    json_data = json.loads(json_str)
                    
                    # Ajouter des métadonnées
                    json_data["query_id"] = str(uuid.uuid4())
                    json_data["timestamp"] = time.time()
                    json_data["analysis_method"] = "ai_based"
                    
                    return response_text
                else:
                    return self._generate_fallback_response("explore_timeline")
            else:
                return self._generate_fallback_response("explore_timeline")
                
        except Exception as e:
            self.logger.log_technical("ERROR", f"Erreur IA pour explore_timeline : {e}")
            self.metrics["ai_errors"] += 1
            return self._generate_fallback_response("explore_timeline")
    
    def _handle_general_query_with_ai(self, analysis: Dict[str, Any]) -> str:
        """Gère les requêtes générales avec vraie IA"""
        self.metrics["ai_calls"] += 1
        
        query = analysis.get("parameters", {}).get("query", "")
        
        # Utiliser vraie IA pour les requêtes générales
        ai_prompt = f"""{self.prompt}

**TÂCHE :** Traite cette requête générale : "{query}"

**CONTEXTE :** Tu es l'Archiviste, spécialiste de la mémoire et de l'organisation.

**RÉPONSE :** Réponds de manière naturelle et inclut un JSON avec ta réponse.

**STRUCTURE JSON :**
{{
  "type": "ARCHIVISTE_NAIVE_RESPONSE",
  "query_id": "<uuid>",
  "status": "success",
  "query_type": "general_query",
  "results": {{
    "query": "{query}",
    "response": "...",
    "suggestions": ["..."]
  }},
  "timestamp": <timestamp>
}}"""

        try:
            cmd = ["ollama", "run", self.ai_model, ai_prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.ai_timeout)
            
            if result.returncode == 0:
                response_text = result.stdout.strip()
                
                # Essayer d'extraire le JSON
                json_start = response_text.find('```json')
                json_end = response_text.find('```', json_start + 7)
                
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start + 7:json_end].strip()
                    json_data = json.loads(json_str)
                    
                    # Ajouter des métadonnées
                    json_data["query_id"] = str(uuid.uuid4())
                    json_data["timestamp"] = time.time()
                    json_data["analysis_method"] = "ai_based"
                    
                    return response_text
                else:
                    return self._generate_fallback_response("general_query")
            else:
                return self._generate_fallback_response("general_query")
                
        except Exception as e:
            self.logger.log_technical("ERROR", f"Erreur IA pour general_query : {e}")
            self.metrics["ai_errors"] += 1
            return self._generate_fallback_response("general_query")
    
    def _generate_fallback_response(self, query_type: str, query: str = "") -> str:
        """Génère une réponse de fallback quand l'IA échoue"""
        self.logger.log_technical("INFO", f"🔄 Génération fallback pour {query_type}")
        
        json_response = {
            "type": "ARCHIVISTE_NAIVE_RESPONSE",
            "query_id": str(uuid.uuid4()),
            "status": "fallback",
            "query_type": query_type,
            "analysis_method": "fallback",
            "results": {
                "query": query,
                "response": f"Requête {query_type} traitée en mode fallback",
                "error": "IA non disponible"
            },
            "timestamp": time.time()
        }
        
        natural_response = f"""Je comprends ta requête ! Voici ma réponse (mode fallback) :

```json
{json.dumps(json_response, indent=2, ensure_ascii=False)}
```

L'IA n'était pas disponible, mais j'ai traité ta demande en mode fallback."""
        
        self.logger.log_technical("INFO", f"✅ Fallback généré pour {query_type}")
        return natural_response
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'Archiviste naïf"""
        return {
            "status": "running" if self.running else "stopped",
            "type": "naive",
            "metrics": self.metrics,
            "queue_size": len(self.message_queue),
            "timeline_messages": len(self.discussion_timeline.get_timeline("alma", limit=100)),
            "ai_model": self.ai_model,
            "ai_calls": self.metrics["ai_calls"],
            "ai_errors": self.metrics["ai_errors"]
        } 