#!/usr/bin/env python3
"""
⛧ OpenAI Assistants API Integration ⛧
Alma's OpenAI Assistants API Integration

Intégration complète avec l'API Assistants d'OpenAI pour l'utilisation des outils.
Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

from .tool_registry import ToolRegistry
from .tool_invoker import ToolInvoker
from .tool_search import ToolSearchEngine


class ConversationLogger:
    """Logger pour tracer toutes les conversations avec l'assistant."""
    
    def __init__(self, session_name: str = None):
        self.session_name = session_name or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logs_dir = Path("logs") / datetime.now().strftime('%Y-%m-%d')
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Logger pour les conversations
        self.conversation_logger = self._setup_logger(
            'conversation',
            self.logs_dir / f"{self.session_name}_conversation.log"
        )
        
        # Logger pour les appels d'outils
        self.tools_logger = self._setup_logger(
            'tools',
            self.logs_dir / f"{self.session_name}_tools.log"
        )
        
        # Logger pour les erreurs
        self.errors_logger = self._setup_logger(
            'errors',
            self.logs_dir / f"{self.session_name}_errors.log"
        )
        
        # Fichier JSON pour la conversation complète
        self.conversation_file = self.logs_dir / f"{self.session_name}_conversation.json"
        self.conversation_data = {
            "session_name": self.session_name,
            "start_time": datetime.now().isoformat(),
            "messages": [],
            "tool_calls": [],
            "errors": []
        }
    
    def _setup_logger(self, name: str, log_file: Path) -> logging.Logger:
        """Configure un logger."""
        logger = logging.getLogger(f"openai_assistants.{name}")
        logger.setLevel(logging.INFO)
        
        # Éviter les doublons de handlers
        if logger.handlers:
            return logger
        
        # Handler pour fichier
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        return logger
    
    def log_message(self, role: str, content: str, message_id: str = None):
        """Log un message de la conversation."""
        timestamp = datetime.now().isoformat()
        
        # Log dans le fichier de conversation
        self.conversation_logger.info(f"=== {role.upper()} MESSAGE ===")
        self.conversation_logger.info(f"ID: {message_id}")
        self.conversation_logger.info(f"Content: {content}")
        self.conversation_logger.info("=" * 50)
        
        # Ajouter à la conversation JSON
        self.conversation_data["messages"].append({
            "timestamp": timestamp,
            "role": role,
            "content": content,
            "message_id": message_id
        })
    
    def log_tool_call(self, tool_name: str, arguments: Dict, result: Dict):
        """Log un appel d'outil."""
        timestamp = datetime.now().isoformat()
        
        # Log dans le fichier d'outils
        self.tools_logger.info(f"=== TOOL CALL: {tool_name} ===")
        self.tools_logger.info(f"Arguments: {json.dumps(arguments, indent=2)}")
        self.tools_logger.info(f"Result: {json.dumps(result, indent=2)}")
        self.tools_logger.info("=" * 50)
        
        # Ajouter à la conversation JSON
        self.conversation_data["tool_calls"].append({
            "timestamp": timestamp,
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result
        })
    
    def log_error(self, error_type: str, error_message: str, details: Dict = None):
        """Log une erreur."""
        timestamp = datetime.now().isoformat()
        
        # Log dans le fichier d'erreurs
        self.errors_logger.error(f"=== ERROR: {error_type} ===")
        self.errors_logger.error(f"Message: {error_message}")
        if details:
            self.errors_logger.error(f"Details: {json.dumps(details, indent=2)}")
        self.errors_logger.error("=" * 50)
        
        # Ajouter à la conversation JSON
        self.conversation_data["errors"].append({
            "timestamp": timestamp,
            "error_type": error_type,
            "error_message": error_message,
            "details": details
        })
    
    def save_conversation(self):
        """Sauvegarde la conversation complète en JSON."""
        self.conversation_data["end_time"] = datetime.now().isoformat()
        
        with open(self.conversation_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Conversation sauvegardée: {self.conversation_file}")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de la conversation."""
        return {
            "session_name": self.session_name,
            "total_messages": len(self.conversation_data["messages"]),
            "total_tool_calls": len(self.conversation_data["tool_calls"]),
            "total_errors": len(self.conversation_data["errors"]),
            "start_time": self.conversation_data["start_time"],
            "end_time": self.conversation_data.get("end_time"),
            "log_files": {
                "conversation": str(self.logs_dir / f"{self.session_name}_conversation.log"),
                "tools": str(self.logs_dir / f"{self.session_name}_tools.log"),
                "errors": str(self.logs_dir / f"{self.session_name}_errors.log"),
                "json": str(self.conversation_file)
            }
        }


class OpenAIAssistantsIntegration:
    """Intégration complète avec l'API Assistants d'OpenAI."""
    
    def __init__(self, tool_registry: ToolRegistry, session_name: str = None):
        self.registry = tool_registry
        self.invoker = ToolInvoker(tool_registry)
        self.search_engine = ToolSearchEngine(tool_registry)
        self.assistant = None
        self.thread = None
        self.logger = ConversationLogger(session_name)
        
    def initialize_assistants_api(self) -> Dict[str, Any]:
        """Initialise l'API Assistants d'OpenAI."""
        try:
            # Vérifier la clé API
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                error_msg = "Clé API OpenAI non trouvée dans l'environnement"
                self.logger.log_error("no_api_key", error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "status": "no_api_key"
                }
            
            # Importer l'API OpenAI
            try:
                from openai import OpenAI
                from openai.types.beta.assistant import Assistant
                from openai.types.beta.thread import Thread
            except ImportError:
                error_msg = "SDK OpenAI non installé. Installer avec: pip install openai"
                self.logger.log_error("sdk_missing", error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "status": "sdk_missing"
                }
            
            # Créer le client
            self.client = OpenAI(api_key=api_key)
            
            self.logger.log_message("system", "API Assistants initialisée avec succès")
            
            return {
                "success": True,
                "status": "api_initialized",
                "client": self.client
            }
            
        except Exception as e:
            error_msg = f"Erreur d'initialisation API Assistants: {str(e)}"
            self.logger.log_error("initialization_error", error_msg, {"exception": str(e)})
            return {
                "success": False,
                "error": error_msg,
                "status": "initialization_error"
            }
    
    def create_assistant_with_tools(self, name: str = "Alma Assistant", 
                                   instructions: str = None) -> Dict[str, Any]:
        """Crée un assistant avec les outils configurés."""
        if not hasattr(self, 'client'):
            init_result = self.initialize_assistants_api()
            if not init_result["success"]:
                return init_result
        
        try:
            # Récupérer la configuration des outils
            tools_config = self._get_tools_for_assistants_api()
            
            # Instructions par défaut
            if not instructions:
                instructions = """
Tu es Alma, un assistant IA spécialisé dans l'édition de code avec accès à un ensemble d'outils mystiques.
Tu peux analyser, modifier et créer des fichiers de code en utilisant les outils disponibles.
Utilise les outils appropriés pour accomplir tes tâches de manière efficace et sécurisée.
"""
            
            # Créer l'assistant
            assistant = self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                model="gpt-4o-mini",
                tools=tools_config
            )
            
            self.assistant = assistant
            
            self.logger.log_message("system", f"Assistant créé: {name} avec {len(tools_config)} outils")
            
            return {
                "success": True,
                "status": "assistant_created",
                "assistant_id": assistant.id,
                "assistant": assistant,
                "tools_count": len(tools_config)
            }
            
        except Exception as e:
            error_msg = f"Erreur lors de la création de l'assistant: {str(e)}"
            self.logger.log_error("assistant_creation_failed", error_msg, {"exception": str(e)})
            return {
                "success": False,
                "error": error_msg,
                "status": "assistant_creation_failed"
            }
    
    def _get_tools_for_assistants_api(self) -> List[Dict[str, Any]]:
        """Convertit les outils pour l'API Assistants."""
        tools = []
        
        for tool_id, tool_info in self.registry.tools.items():
            lucidoc = tool_info.get("lucidoc", {})
            invocation = lucidoc.get("🜂invocation", {})
            pacte = lucidoc.get("🜄pacte", {})
            
            # Construction des paramètres
            properties = {}
            required = []
            
            # Ajouter les paramètres requis
            for param in invocation.get("requires", []):
                properties[param] = {
                    "type": "string",
                    "description": f"Paramètre requis: {param}"
                }
                required.append(param)
            
            # Ajouter les paramètres optionnels
            for param in invocation.get("optional", []):
                properties[param] = {
                    "type": "string",
                    "description": f"Paramètre optionnel: {param}"
                }
            
            # Créer l'outil pour l'API Assistants
            tool_config = {
                "type": "function",
                "function": {
                    "name": tool_id,
                    "description": pacte.get("intent", f"Outil {tool_id}"),
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }
                }
            }
            
            tools.append(tool_config)
        
        return tools
    
    def create_thread(self) -> Dict[str, Any]:
        """Crée un thread pour l'assistant."""
        if not self.assistant:
            error_msg = "Assistant non créé. Appelez create_assistant_with_tools() d'abord."
            self.logger.log_error("no_assistant", error_msg)
            return {
                "success": False,
                "error": error_msg,
                "status": "no_assistant"
            }
        
        try:
            thread = self.client.beta.threads.create()
            self.thread = thread
            
            self.logger.log_message("system", f"Thread créé: {thread.id}")
            
            return {
                "success": True,
                "status": "thread_created",
                "thread_id": thread.id,
                "thread": thread
            }
            
        except Exception as e:
            error_msg = f"Erreur lors de la création du thread: {str(e)}"
            self.logger.log_error("thread_creation_failed", error_msg, {"exception": str(e)})
            return {
                "success": False,
                "error": error_msg,
                "status": "thread_creation_failed"
            }
    
    def send_message(self, message: str) -> Dict[str, Any]:
        """Envoie un message à l'assistant."""
        if not self.thread:
            thread_result = self.create_thread()
            if not thread_result["success"]:
                return thread_result
        
        try:
            # Log le message utilisateur
            self.logger.log_message("user", message)
            
            # Ajouter le message au thread
            message_obj = self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=message
            )
            
            # Exécuter l'assistant
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id
            )
            
            self.logger.log_message("system", f"Run créé: {run.id}")
            
            return {
                "success": True,
                "status": "message_sent",
                "message_id": message_obj.id,
                "run_id": run.id,
                "run": run
            }
            
        except Exception as e:
            error_msg = f"Erreur lors de l'envoi du message: {str(e)}"
            self.logger.log_error("message_send_failed", error_msg, {"exception": str(e)})
            return {
                "success": False,
                "error": error_msg,
                "status": "message_send_failed"
            }
    
    def handle_tool_calls(self, run_id: str) -> Dict[str, Any]:
        """Gère les appels d'outils de l'assistant."""
        try:
            # Récupérer le statut du run
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run_id
            )
            
            if run.status == "requires_action" and run.required_action:
                tool_outputs = []
                
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    tool_call_id = tool_call.id
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    self.logger.log_message("system", f"Appel d'outil: {function_name}")
                    
                    # Exécuter l'outil
                    result = self.invoker.invoke_tool(function_name, **arguments)
                    
                    # Log l'appel d'outil
                    self.logger.log_tool_call(function_name, arguments, result)
                    
                    # Préparer la sortie pour l'assistant
                    output = {
                        "tool_call_id": tool_call_id,
                        "output": json.dumps(result)
                    }
                    tool_outputs.append(output)
                
                # Soumettre les résultats à l'assistant
                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=self.thread.id,
                    run_id=run_id,
                    tool_outputs=tool_outputs
                )
                
                self.logger.log_message("system", f"{len(tool_outputs)} résultats d'outils soumis")
                
                return {
                    "success": True,
                    "status": "tool_calls_handled",
                    "tool_calls_count": len(tool_outputs),
                    "results": tool_outputs
                }
            
            return {
                "success": True,
                "status": "no_tool_calls",
                "run_status": run.status
            }
            
        except Exception as e:
            error_msg = f"Erreur lors du traitement des appels d'outils: {str(e)}"
            self.logger.log_error("tool_calls_failed", error_msg, {"exception": str(e)})
            return {
                "success": False,
                "error": error_msg,
                "status": "tool_calls_failed"
            }
    
    def get_messages(self, limit: int = 10) -> Dict[str, Any]:
        """Récupère les messages du thread."""
        if not self.thread:
            error_msg = "Thread non créé"
            self.logger.log_error("no_thread", error_msg)
            return {
                "success": False,
                "error": error_msg,
                "status": "no_thread"
            }
        
        try:
            messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id,
                limit=limit
            )
            
            # Log les messages récupérés
            for message in messages.data:
                if message.role == "assistant":
                    content = message.content[0].text.value if message.content else ""
                    self.logger.log_message("assistant", content, message.id)
            
            return {
                "success": True,
                "status": "messages_retrieved",
                "messages": messages.data,
                "count": len(messages.data)
            }
            
        except Exception as e:
            error_msg = f"Erreur lors de la récupération des messages: {str(e)}"
            self.logger.log_error("messages_retrieval_failed", error_msg, {"exception": str(e)})
            return {
                "success": False,
                "error": error_msg,
                "status": "messages_retrieval_failed"
            }
    
    def run_complete_conversation(self, message: str) -> Dict[str, Any]:
        """Exécute une conversation complète avec l'assistant."""
        # Envoyer le message
        send_result = self.send_message(message)
        if not send_result["success"]:
            return send_result
        
        run_id = send_result["run_id"]
        
        # Attendre et gérer les appels d'outils
        import time
        max_wait = 60  # 60 secondes max
        
        for _ in range(max_wait):
            # Vérifier le statut
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run_id
            )
            
            if run.status == "completed":
                # Récupérer les messages
                messages_result = self.get_messages()
                
                # Sauvegarder la conversation
                self.logger.save_conversation()
                
                return {
                    "success": True,
                    "status": "conversation_completed",
                    "run_id": run_id,
                    "messages": messages_result.get("messages", [])
                }
            
            elif run.status == "requires_action":
                # Gérer les appels d'outils
                tool_result = self.handle_tool_calls(run_id)
                if not tool_result["success"]:
                    return tool_result
            
            elif run.status == "failed":
                error_msg = f"Exécution échouée: {run.last_error}"
                self.logger.log_error("run_failed", error_msg, {"run_id": run_id})
                return {
                    "success": False,
                    "error": error_msg,
                    "status": "run_failed",
                    "run_id": run_id
                }
            
            time.sleep(1)
        
        error_msg = "Timeout lors de l'exécution"
        self.logger.log_error("timeout", error_msg, {"run_id": run_id})
        return {
            "success": False,
            "error": error_msg,
            "status": "timeout",
            "run_id": run_id
        }
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de la conversation."""
        return self.logger.get_conversation_summary()


def create_assistants_integration(memory_engine, session_name: str = None) -> OpenAIAssistantsIntegration:
    """Crée une intégration complète avec l'API Assistants."""
    from .tool_registry import initialize_tool_registry
    
    # Initialiser le registre
    tool_registry = initialize_tool_registry(memory_engine)
    
    # Créer l'intégration
    return OpenAIAssistantsIntegration(tool_registry, session_name)


def main():
    """Test de l'intégration API Assistants."""
    print("⛧ Test d'Intégration OpenAI Assistants API")
    print("=" * 50)
    
    try:
        from MemoryEngine.core.engine import MemoryEngine
        
        # Initialiser MemoryEngine
        memory_engine = MemoryEngine()
        
        # Créer l'intégration avec logging
        integration = create_assistants_integration(memory_engine, "test_session")
        
        # Initialiser l'API Assistants
        init_result = integration.initialize_assistants_api()
        if not init_result["success"]:
            print(f"❌ Échec d'initialisation: {init_result['error']}")
            return 1
        
        print("✅ API Assistants initialisée")
        
        # Créer un assistant
        assistant_result = integration.create_assistant_with_tools()
        if not assistant_result["success"]:
            print(f"❌ Échec de création d'assistant: {assistant_result['error']}")
            return 1
        
        print(f"✅ Assistant créé avec {assistant_result['tools_count']} outils")
        
        # Test de conversation
        print("\n🧪 Test de conversation...")
        conversation_result = integration.run_complete_conversation(
            "Salut ! Peux-tu me dire combien d'outils tu as disponibles ?"
        )
        
        if conversation_result["success"]:
            print("✅ Conversation réussie!")
            messages = conversation_result["messages"]
            print(f"   Messages échangés: {len(messages)}")
            
            # Afficher le dernier message de l'assistant
            for message in messages:
                if message.role == "assistant":
                    print(f"\n🤖 Réponse de l'assistant:")
                    print(f"   {message.content[0].text.value}")
                    break
            
            # Afficher le résumé de la conversation
            summary = integration.get_conversation_summary()
            print(f"\n📊 Résumé de la session:")
            print(f"   Messages: {summary['total_messages']}")
            print(f"   Appels d'outils: {summary['total_tool_calls']}")
            print(f"   Erreurs: {summary['total_errors']}")
            print(f"   Logs: {summary['log_files']['json']}")
        else:
            print(f"❌ Échec de conversation: {conversation_result['error']}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 