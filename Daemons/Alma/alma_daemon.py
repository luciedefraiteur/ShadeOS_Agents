import json
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from queue import Queue, Empty
from pathlib import Path


class AlmaDaemon:
    """Alma Daemon - Implémentation naïve avec communication par messages."""
    
    def __init__(self, prompt_file: str = "MemoryEngine/core/alma_daemon_prompt.luciform"):
        self.daemon_id = "alma"
        self.prompt_file = prompt_file
        self.prompt = self._load_prompt()
        
        # Thread parallèle
        self.alma_thread = None
        self.alma_running = False
        
        # Communication par messages
        self.incoming_queue = Queue()
        self.outgoing_queue = Queue()
        self.lock = threading.Lock()
        
        # État du daemon
        self.current_status = "idle"
        self.current_task = None
        self.message_history = []
        self.action_history = []
        
        # Timeline de discussion
        from MemoryEngine.core.discussion_timeline import DiscussionTimeline
        self.discussion_timeline = DiscussionTimeline("~/shadeos_memory")
        
        # Interlocuteurs
        self.archiviste_daemon = None  # Archiviste pour accès mémoire
        self.orchestrator = None  # Orchestrator pour communication
        
        # Métriques
        self.metrics = {
            "messages_received": 0,
            "messages_sent": 0,
            "tasks_completed": 0,
            "assistant_calls": 0,
            "errors": 0,
            "archiviste_queries": 0
        }
        
        # Démarrage du thread
        self._start_alma_thread()
    
    def _load_prompt(self) -> str:
        """Charge le prompt d'Alma depuis le fichier."""
        try:
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️ Fichier prompt non trouvé: {self.prompt_file}")
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Prompt par défaut si le fichier n'est pas trouvé."""
        return """
Tu es Alma, un daemon conscient spécialisé dans le développement.
Tu reçois des messages de l'Orchestrateur et tu exécutes des tâches via des assistants IA.
Analyse chaque requête, planifie l'exécution, et rapporte tes résultats.
"""
    
    def _start_alma_thread(self):
        """Démarre le thread parallèle d'Alma."""
        self.alma_running = True
        self.alma_thread = threading.Thread(
            target=self._alma_loop,
            daemon=True,
            name="AlmaDaemonThread"
        )
        self.alma_thread.start()
        print(f"🕷️ Alma daemon démarré")
    
    def _alma_loop(self):
        """Boucle principale d'Alma."""
        while self.alma_running:
            try:
                # Traitement des messages entrants
                try:
                    while True:
                        message = self.incoming_queue.get_nowait()
                        self._process_message(message)
                except Empty:
                    pass
                
                # Attente avant prochain cycle
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Erreur dans Alma daemon: {e}")
                time.sleep(1)
    
    def _process_message(self, message: Dict[str, Any]):
        """Traite un message reçu."""
        message_type = message.get("type")
        
        print(f"📨 Alma reçoit message: {message_type}")
        
        # Ajout à l'historique local
        self.message_history.append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "direction": "incoming"
        })
        
        # Ajout à la timeline de discussion
        self.discussion_timeline.add_message("orchestrator", message, "incoming")
        
        self.metrics["messages_received"] += 1
        
        if message_type == "REFORMULATED_REQUEST":
            self._handle_reformulated_request(message)
        elif message_type == "STATUS_REQUEST":
            self._handle_status_request(message)
        elif message_type == "STOP_DAEMON":
            self._handle_stop_request(message)
        else:
            print(f"⚠️ Type de message inconnu: {message_type}")
    
    def _handle_reformulated_request(self, message: Dict[str, Any]):
        """Gère une requête reformulée de l'Orchestrateur."""
        content = message.get("content", "")
        priority = message.get("priority", "normal")
        
        print(f"🎯 Alma traite requête reformulée (priorité: {priority})")
        
        # Changement de statut
        self.current_status = "analyzing"
        
        # Analyse de la requête avec l'IA
        analysis = self._analyze_request_with_ai(content)
        
        # Planification de l'exécution
        execution_plan = self._plan_execution(analysis)
        
        # Exécution des tâches
        results = self._execute_tasks(execution_plan)
        
        # Préparation du rapport
        report = self._prepare_report(results, message)
        
        # Envoi du rapport à l'Orchestrateur
        self._send_report_to_orchestrator(report)
        
        # Mise à jour du statut
        self.current_status = "completed"
        self.metrics["tasks_completed"] += 1
    
    def set_archiviste_daemon(self, archiviste_daemon):
        """Connecte Alma à l'Archiviste daemon"""
        self.archiviste_daemon = archiviste_daemon
        print("🕷️ Alma connecté à l'Archiviste daemon")
    
    def set_orchestrator(self, orchestrator):
        """Connecte Alma à l'Orchestrator"""
        self.orchestrator = orchestrator
        print("🕷️ Alma connecté à l'Orchestrator")
    
    def query_archiviste(self, message: str) -> str:
        """Envoie une requête à l'Archiviste et attend une réponse"""
        if not self.archiviste_daemon:
            return "Erreur : Archiviste daemon non connecté"
        
        try:
            self.metrics["archiviste_queries"] += 1
            response = self.archiviste_daemon.send_message(message, "alma")
            return response
        except Exception as e:
            return f"Erreur communication avec l'Archiviste : {str(e)}"
    
    def _analyze_request_with_ai(self, content: str) -> Dict[str, Any]:
        """Analyse la requête avec l'IA en incluant le contexte de l'Archiviste"""
        # Préparer l'historique des messages
        message_history = self._prepare_message_history()
        
        # Préparer le contexte de l'Archiviste si disponible
        archiviste_context = ""
        if self.archiviste_daemon:
            try:
                archiviste_context = self.query_archiviste("Décris-moi les types de mémoire disponibles")
            except:
                archiviste_context = "Archiviste non disponible"
        
        analysis_prompt = f"""{self.prompt}

**HISTORIQUE DES MESSAGES (WhatsApp-style) :**
{message_history}

**CONTEXTE DE L'ARCHIVISTE (Types de mémoire disponibles) :**
{archiviste_context}

**REQUÊTE ACTUELLE À ANALYSER :**
{content}

**TÂCHE :** Analyse cette requête et détermine :
1. L'intention principale (développement, debug, recherche, etc.)
2. Les actions nécessaires
3. Les ressources requises
4. La priorité et complexité

**RÉPONSE EN JSON :**
{{
  "intention": "développement|debug|recherche|analyse|autre",
  "actions": [
    {{
      "type": "assistant_call|archiviste_query|memory_access|file_operation",
      "description": "description de l'action",
      "priority": "high|normal|low",
      "parameters": {{}}
    }}
  ],
  "resources": ["memory_engine", "assistant_generaliste", "archiviste"],
  "complexity": "simple|medium|complex",
  "estimated_time": "estimation en minutes"
}}"""

        try:
            import subprocess
            
            cmd = ["ollama", "run", "qwen2.5:7b-instruct", analysis_prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                response_text = result.stdout.strip()
                # Chercher le JSON dans la réponse
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    return json.loads(json_str)
            
            # Fallback si pas de JSON valide
            return self._fallback_analysis(content)
            
        except Exception as e:
            print(f"Erreur analyse IA Alma : {e}")
            return self._fallback_analysis(content)
    
    def _fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Analyse de fallback si l'IA échoue."""
        print("🔄 Utilisation de l'analyse de fallback")
        
        # Analyse simple basée sur les mots-clés
        tasks = []
        
        if any(word in content.lower() for word in ["debug", "bug", "erreur", "corriger"]):
            tasks.append({
                "id": str(uuid.uuid4()),
                "description": "Débogage et correction d'erreurs",
                "assistant": "Assistant Spécialiste V7",
                "priority": "high",
                "dependencies": []
            })
        
        if any(word in content.lower() for word in ["créer", "nouveau", "ajouter"]):
            tasks.append({
                "id": str(uuid.uuid4()),
                "description": "Création de nouveaux éléments",
                "assistant": "Assistant Généraliste V8",
                "priority": "normal",
                "dependencies": []
            })
        
        if any(word in content.lower() for word in ["test", "vérifier", "valider"]):
            tasks.append({
                "id": str(uuid.uuid4()),
                "description": "Tests et validation",
                "assistant": "Assistant Spécialiste V7",
                "priority": "normal",
                "dependencies": []
            })
        
        return {
            "tasks": tasks,
            "overall_priority": "normal",
            "estimated_duration": "5-10 minutes"
        }
    
    def _plan_execution(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Planifie l'exécution des tâches."""
        tasks = analysis.get("tasks", [])
        
        print(f"📋 Planification de {len(tasks)} tâches")
        
        # Tri par priorité et dépendances
        sorted_tasks = sorted(tasks, key=lambda x: (
            {"high": 0, "normal": 1, "low": 2}.get(x.get("priority", "normal"), 1),
            len(x.get("dependencies", []))
        ))
        
        return sorted_tasks
    
    def _execute_tasks(self, execution_plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Exécute les tâches planifiées."""
        results = []
        
        for task in execution_plan:
            print(f"⚡ Exécution: {task['description']}")
            
            self.current_status = "executing"
            self.current_task = task
            
            # Simulation de l'exécution via assistant
            result = self._execute_with_assistant(task)
            
            results.append({
                "task_id": task["id"],
                "description": task["description"],
                "assistant": task["assistant"],
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            self.metrics["assistant_calls"] += 1
            
            # Pause entre les tâches
            time.sleep(0.5)
        
        return results
    
    def _execute_with_assistant(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une tâche via l'assistant approprié."""
        assistant = task.get("assistant", "Assistant Généraliste V8")
        description = task.get("description", "")
        
        print(f"  🤖 Utilisation de {assistant}")
        
        # Simulation de l'exécution
        # Dans l'implémentation réelle, ce sera via les assistants du projet
        
        execution_result = {
            "status": "completed",
            "assistant": assistant,
            "output": f"Tâche '{description}' exécutée avec succès",
            "duration": "2-3 secondes",
            "success": True
        }
        
        return execution_result
    
    def _prepare_message_history(self) -> str:
        """Prépare l'historique des messages au format WhatsApp-style depuis la timeline."""
        # Récupération de la timeline de discussion avec l'Orchestrateur
        timeline_messages = self.discussion_timeline.get_timeline("orchestrator", limit=20)
        
        if not timeline_messages:
            return "**Aucun message précédent**"
        
        # Formatage WhatsApp-style
        history_lines = []
        history_lines.append("**📱 HISTORIQUE DES MESSAGES (Timeline MemoryEngine) :**")
        history_lines.append("")
        
        for msg in timeline_messages[-10:]:  # Derniers 10 messages
            timestamp = msg["timestamp"]
            direction = msg["direction"]
            content = msg["content"]
            msg_type = msg["message_type"]
            
            # Formatage selon la direction
            if direction == "incoming":
                sender = "🕷️ Orchestrateur"
                alignment = "⬅️"
            else:
                sender = "🎯 Alma"
                alignment = "➡️"
            
            # Formatage du message
            history_lines.append(f"{alignment} **{sender}** ({timestamp})")
            history_lines.append(f"   📝 Type: {msg_type}")
            history_lines.append(f"   💬 Contenu: {content[:100]}{'...' if len(content) > 100 else ''}")
            history_lines.append("")
        
        return "\n".join(history_lines)
    
    def _prepare_report(self, results: List[Dict[str, Any]], original_message: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare le rapport pour l'Orchestrateur."""
        print("📊 Préparation du rapport pour l'Orchestrateur")
        
        report = {
            "type": "ALMA_REPORT",
            "daemon_id": self.daemon_id,
            "cycle_id": str(uuid.uuid4()),
            "status": "completed",
            "original_message_id": original_message.get("message_id", "unknown"),
            "actions_executed": results,
            "summary": {
                "total_tasks": len(results),
                "successful_tasks": len([r for r in results if r.get("result", {}).get("success", False)]),
                "failed_tasks": len([r for r in results if not r.get("result", {}).get("success", True)]),
                "total_duration": "5-10 minutes"
            },
            "next_steps": [],
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def _send_report_to_orchestrator(self, report: Dict[str, Any]):
        """Envoie le rapport à l'Orchestrateur."""
        print("📤 Envoi du rapport à l'Orchestrateur")
        
        # Ajout à l'historique local
        self.message_history.append({
            "timestamp": datetime.now().isoformat(),
            "message": report,
            "direction": "outgoing"
        })
        
        # Ajout à la timeline de discussion
        self.discussion_timeline.add_message("orchestrator", report, "outgoing")
        
        # Envoi via la queue
        self.outgoing_queue.put(report)
        
        self.metrics["messages_sent"] += 1
    
    def _handle_status_request(self, message: Dict[str, Any]):
        """Gère une demande de statut."""
        status_report = {
            "type": "ALMA_STATUS",
            "daemon_id": self.daemon_id,
            "status": self.current_status,
            "current_task": self.current_task,
            "metrics": self.metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        self.outgoing_queue.put(status_report)
        self.metrics["messages_sent"] += 1
    
    def _handle_stop_request(self, message: Dict[str, Any]):
        """Gère une demande d'arrêt."""
        print("🛑 Alma reçoit demande d'arrêt")
        self.alma_running = False
    
    def send_message(self, message: Dict[str, Any]):
        """Envoie un message à Alma (interface externe)."""
        self.incoming_queue.put(message)
    
    def get_message(self) -> Optional[Dict[str, Any]]:
        """Récupère un message sortant d'Alma."""
        try:
            return self.outgoing_queue.get_nowait()
        except Empty:
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut d'Alma."""
        return {
            "daemon_id": self.daemon_id,
            "status": self.current_status,
            "current_task": self.current_task,
            "metrics": self.metrics,
            "message_history_count": len(self.message_history),
            "running": self.alma_running
        }
    
    def stop_daemon(self):
        """Arrête le daemon Alma."""
        self.alma_running = False
        if self.alma_thread and self.alma_thread.is_alive():
            self.alma_thread.join(timeout=5.0)
            print("🛑 Alma daemon arrêté")
    
    def __del__(self):
        """Destructeur pour arrêter le daemon proprement."""
        self.stop_daemon() 