# ⛧ Créé par Alma, Architecte Démoniaque ⛧
# 🕷️ Assistant Local LLM V1 - Remplacement de la Logique Codée

import json
import logging
import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

from MemoryEngine.EditingSession.Tools.tool_registry import ToolRegistry
from MemoryEngine.EditingSession.Tools.tool_invoker import ToolInvoker
from MemoryEngine.EditingSession.Tools.tool_search import ToolSearchEngine


class LocalLLMLogger:
    """Logger pour l'assistant local LLM."""
    
    def __init__(self, session_name: str = None):
        self.session_name = session_name or f"local_llm_v1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logs_dir = Path("IAIntrospectionDaemons/logs") / datetime.now().strftime('%Y-%m-%d')
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichier JSON pour la conversation
        self.conversation_file = self.logs_dir / f"{self.session_name}_conversation.json"
        self.conversation_data = {
            "session_name": self.session_name,
            "start_time": datetime.now().isoformat(),
            "messages": [],
            "tool_calls": [],
            "llm_calls": [],
            "errors": []
        }
    
    def log_message(self, role: str, content: str, message_id: str = None):
        """Log un message."""
        timestamp = datetime.now().isoformat()
        
        self.conversation_data["messages"].append({
            "timestamp": timestamp,
            "role": role,
            "content": content,
            "message_id": message_id
        })
        
        print(f"[{role.upper()}] {content[:100]}{'...' if len(content) > 100 else ''}")
    
    def log_llm_call(self, model: str, prompt: str, response: str, duration: float):
        """Log un appel LLM."""
        timestamp = datetime.now().isoformat()
        
        self.conversation_data["llm_calls"].append({
            "timestamp": timestamp,
            "model": model,
            "prompt": prompt,
            "response": response,
            "duration": duration
        })
        
        print(f"[LLM] {model}: {duration:.2f}s - {response[:100]}{'...' if len(response) > 100 else ''}")
    
    def log_tool_call(self, tool_name: str, arguments: Dict, result: Dict):
        """Log un appel d'outil."""
        timestamp = datetime.now().isoformat()
        
        self.conversation_data["tool_calls"].append({
            "timestamp": timestamp,
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result
        })
        
        print(f"[TOOL] {tool_name}: {arguments}")
    
    def log_error(self, error_type: str, error_message: str, details: Dict = None):
        """Log une erreur."""
        timestamp = datetime.now().isoformat()
        
        self.conversation_data["errors"].append({
            "timestamp": timestamp,
            "error_type": error_type,
            "error_message": error_message,
            "details": details or {}
        })
        
        print(f"[ERROR] {error_type}: {error_message}")
    
    def save_conversation(self):
        """Sauvegarde la conversation."""
        with open(self.conversation_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Conversation sauvegardée: {self.conversation_file}")


class LocalLLMAssistantV1:
    """
    Assistant V1 avec LLM local qui remplace la logique codée en dur.
    Teste différents modèles disponibles.
    """
    
    def __init__(self, name: str = "Local LLM Assistant V1", memory_engine = None):
        self.name = name
        self.logger = LocalLLMLogger(f"{name.lower().replace(' ', '_')}")
        
        # Initialiser les outils
        self.tool_registry = ToolRegistry(memory_engine)
        self.tool_registry.initialize()
        self.tool_invoker = ToolInvoker(self.tool_registry)
        self.tool_search = ToolSearchEngine(self.tool_registry)
        
        # État de la conversation
        self.messages = []
        self.current_context = {}
        
        # Modèles disponibles à tester
        self.available_models = [
            "mistral:7b-instruct",
            "qwen2.5:7b-instruct", 
            "llama3.2:3b-instruct",
            "gemma2:2b-instruct"
        ]
        
        self.logger.log_message("system", f"Assistant '{self.name}' initialisé")
    
    def _get_system_prompt(self) -> str:
        """Prompt système pour l'assistant."""
        return """Tu es un assistant de débogage de code Python intelligent. Tu as accès à plusieurs outils pour analyser et corriger du code.

## Capacités :
- Analyser du code Python avec l'outil code_analyzer
- Corriger des bugs avec les outils safe_*
- Lire et écrire des fichiers
- Rechercher des outils appropriés

## Outils disponibles :
{available_tools}

## Processus de débogage :
1. Analyser le code avec code_analyzer
2. Identifier les bugs et problèmes
3. Proposer un plan de correction
4. Exécuter les corrections avec les outils appropriés
5. Valider les résultats

## Règles :
- Sois méthodique et précis
- Explique chaque action avant de l'exécuter
- Utilise les outils les plus appropriés
- Gère les erreurs gracieusement
- Valide tes corrections

## Format de réponse :
Réponds de manière structurée et claire. Si tu dois utiliser un outil, indique-le clairement."""
    
    def _get_available_tools_text(self) -> str:
        """Retourne la liste des outils en format texte."""
        tools = self.tool_registry.list_tools()
        tools_text = ""
        for tool in tools:
            tools_text += f"- {tool['id']}: {tool['intent']}\n"
        return tools_text
    
    def _call_llm(self, model: str, prompt: str) -> str:
        """Appelle un modèle LLM local via Ollama."""
        try:
            request_data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1024
                }
            }
            
            request_json = json.dumps(request_data, ensure_ascii=False)
            
            start_time = time.time()
            result = subprocess.run(
                [
                    'curl', '-X', 'POST', 'http://localhost:11434/api/generate',
                    '-H', 'Content-Type: application/json',
                    '-d', request_json
                ],
                capture_output=True,
                text=True,
                timeout=120
            )
            end_time = time.time()
            
            if result.returncode == 0:
                response_data = json.loads(result.stdout)
                response_text = response_data.get('response', '')
                duration = end_time - start_time
                
                self.logger.log_llm_call(model, prompt, response_text, duration)
                return response_text
            else:
                error_msg = f"Erreur lors de l'appel {model}: {result.stderr}"
                self.logger.log_error("llm_call_error", error_msg)
                return f"❌ Erreur: {error_msg}"
                
        except subprocess.TimeoutExpired:
            error_msg = f"Timeout lors de l'appel {model}"
            self.logger.log_error("llm_timeout", error_msg)
            return f"❌ Timeout: {error_msg}"
        except Exception as e:
            error_msg = f"Erreur lors de l'appel {model}: {str(e)}"
            self.logger.log_error("llm_error", error_msg)
            return f"❌ Erreur: {error_msg}"
    
    def _try_models(self, prompt: str) -> str:
        """Essaie différents modèles jusqu'à ce qu'un fonctionne."""
        for model in self.available_models:
            print(f"🔄 Test du modèle: {model}")
            response = self._call_llm(model, prompt)
            
            # Si on a une réponse valide (pas d'erreur)
            if not response.startswith("❌"):
                print(f"✅ Modèle {model} fonctionne")
                return response
            
            print(f"❌ Modèle {model} échoue")
        
        # Si aucun modèle ne fonctionne
        return "❌ Aucun modèle LLM disponible"
    
    def send_message(self, message: str) -> str:
        """
        Envoie un message à l'assistant et retourne sa réponse.
        Utilise le LLM pour analyser et décider des actions.
        """
        self.logger.log_message("user", message)
        self.messages.append({"role": "user", "content": message})
        
        try:
            # Construire le prompt avec contexte
            system_prompt = self._get_system_prompt().format(
                available_tools=self._get_available_tools_text()
            )
            
            # Historique des messages
            conversation_history = ""
            for msg in self.messages[-5:]:  # Derniers 5 messages
                role = msg["role"]
                content = msg["content"]
                conversation_history += f"{role.upper()}: {content}\n"
            
            # Prompt complet
            full_prompt = f"""{system_prompt}

## Historique de conversation :
{conversation_history}

## Message utilisateur :
{message}

## Réponse :"""
            
            # Appeler le LLM
            response = self._try_models(full_prompt)
            
            # Log de la réponse
            self.logger.log_message("assistant", response)
            self.messages.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            error_msg = f"Erreur lors du traitement: {str(e)}"
            self.logger.log_error("processing_error", error_msg)
            return error_msg
    
    def get_available_tools(self) -> List[str]:
        """Retourne la liste des outils disponibles."""
        return [tool['id'] for tool in self.tool_registry.list_tools()]
    
    def save_session(self):
        """Sauvegarde la session."""
        self.logger.save_conversation()
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de la session."""
        return {
            "assistant_name": self.name,
            "total_messages": len(self.messages),
            "total_tool_calls": len(self.logger.conversation_data["tool_calls"]),
            "total_llm_calls": len(self.logger.conversation_data["llm_calls"]),
            "total_errors": len(self.logger.conversation_data["errors"]),
            "session_duration": datetime.now().isoformat()
        }


def create_local_llm_assistant_v1(name: str = "Local LLM Assistant V1", memory_engine = None) -> LocalLLMAssistantV1:
    """Factory pour créer un assistant local LLM V1."""
    return LocalLLMAssistantV1(name, memory_engine)


def main():
    """Test de l'assistant local LLM V1."""
    print("🕷️ Test de l'Assistant Local LLM V1")
    print("=" * 50)
    
    # Créer l'assistant
    from MemoryEngine.core.engine import MemoryEngine
    memory_engine = MemoryEngine()
    assistant = create_local_llm_assistant_v1("Alma Local LLM V1", memory_engine)
    
    # Test 1: Demande d'outils
    print("\n1. Demande d'outils:")
    response = assistant.send_message("Quels outils as-tu disponibles ?")
    print(response)
    
    # Test 2: Analyse d'un fichier
    print("\n2. Analyse d'un fichier:")
    response = assistant.send_message("Peux-tu analyser le fichier TestProject/buggy_calculator.py ?")
    print(response)
    
    # Sauvegarder la session
    assistant.save_session()
    
    # Afficher le résumé
    summary = assistant.get_session_summary()
    print(f"\n📊 Résumé de la session: {summary}")


if __name__ == "__main__":
    main() 