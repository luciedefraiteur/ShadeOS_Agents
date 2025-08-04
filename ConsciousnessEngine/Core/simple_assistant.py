# ⛧ Créé par Alma, Architecte Démoniaque ⛧
# 🕷️ Assistant Simple - Reproduction du Pattern OpenAI

import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

from MemoryEngine.EditingSession.Tools.tool_registry import ToolRegistry
from MemoryEngine.EditingSession.Tools.tool_invoker import ToolInvoker
from MemoryEngine.EditingSession.Tools.tool_search import ToolSearchEngine


class SimpleAssistantLogger:
    """Logger simple pour tracer les conversations."""
    
    def __init__(self, session_name: str = None):
        self.session_name = session_name or f"simple_assistant_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logs_dir = Path("IAIntrospectionDaemons/logs") / datetime.now().strftime('%Y-%m-%d')
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichier JSON pour la conversation
        self.conversation_file = self.logs_dir / f"{self.session_name}_conversation.json"
        self.conversation_data = {
            "session_name": self.session_name,
            "start_time": datetime.now().isoformat(),
            "messages": [],
            "tool_calls": [],
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


class SimpleAssistant:
    """
    Assistant simple qui reproduit le pattern OpenAI.
    Pas de Luciform, juste un assistant qui utilise des outils.
    """
    
    def __init__(self, name: str = "Simple Assistant", instructions: str = None, memory_engine = None):
        self.name = name
        self.instructions = instructions or self._get_default_instructions()
        self.logger = SimpleAssistantLogger(f"{name.lower().replace(' ', '_')}")
        
        # Initialiser les outils
        self.tool_registry = ToolRegistry(memory_engine)
        self.tool_registry.initialize()  # Charger les outils
        self.tool_invoker = ToolInvoker(self.tool_registry)
        self.tool_search = ToolSearchEngine(self.tool_registry)
        
        # État de la conversation
        self.messages = []
        self.current_context = {}
        
        self.logger.log_message("system", f"Assistant '{self.name}' initialisé")
    
    def _get_default_instructions(self) -> str:
        """Instructions par défaut pour l'assistant."""
        return """
Tu es un assistant de débogage de code Python. Tu as accès à plusieurs outils pour analyser et corriger du code.

## Capacités :
- Analyser du code Python avec l'outil code_analyzer
- Corriger des bugs avec les outils safe_*
- Lire et écrire des fichiers
- Rechercher des outils appropriés

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
        """
    
    def get_available_tools(self) -> List[str]:
        """Retourne la liste des outils disponibles."""
        return self.tool_registry.list_tools()
    
    def send_message(self, message: str) -> str:
        """
        Envoie un message à l'assistant et retourne sa réponse.
        Reproduit le pattern OpenAI : message -> analyse -> outils -> réponse
        """
        self.logger.log_message("user", message)
        
        # Ajouter le message à l'historique
        self.messages.append({"role": "user", "content": message})
        
        try:
            # Analyser le message et déterminer les actions
            response = self._process_message(message)
            
            # Log de la réponse
            self.logger.log_message("assistant", response)
            self.messages.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            error_msg = f"Erreur lors du traitement: {str(e)}"
            self.logger.log_error("processing_error", error_msg)
            return error_msg
    
    def _process_message(self, message: str) -> str:
        """
        Traite un message et détermine les actions à prendre.
        C'est ici qu'on simule l'intelligence de l'assistant.
        """
        message_lower = message.lower()
        
        # Détecter le type de demande
        if "analyser" in message_lower or "détecter" in message_lower or "bugs" in message_lower:
            return self._handle_analysis_request(message)
        elif "corriger" in message_lower or "fix" in message_lower:
            return self._handle_fix_request(message)
        elif "outils" in message_lower or "tools" in message_lower:
            return self._handle_tools_request()
        else:
            return self._handle_general_request(message)
    
    def _handle_analysis_request(self, message: str) -> str:
        """Gère une demande d'analyse de code."""
        # Extraire le chemin du fichier du message
        file_path = self._extract_file_path(message)
        if not file_path:
            return "❌ Aucun fichier spécifié pour l'analyse. Veuillez préciser le chemin du fichier."
        
        # Vérifier que le fichier existe
        if not os.path.exists(file_path):
            return f"❌ Fichier non trouvé: {file_path}"
        
        # Utiliser l'outil code_analyzer
        try:
            self.logger.log_message("system", f"Analyse du fichier: {file_path}")
            
            result = self.tool_invoker.invoke_tool("code_analyzer", file_path=file_path)
            
            if result["success"]:
                analysis = result["result"]
                self.logger.log_tool_call("code_analyzer", {"file_path": file_path}, analysis)
                
                # Formater la réponse
                response = self._format_analysis_response(analysis, file_path)
                return response
            else:
                return f"❌ Erreur lors de l'analyse: {result.get('error', 'Erreur inconnue')}"
                
        except Exception as e:
            self.logger.log_error("analysis_error", str(e))
            return f"❌ Erreur lors de l'analyse: {str(e)}"
    
    def _handle_fix_request(self, message: str) -> str:
        """Gère une demande de correction de code."""
        # Pour l'instant, on demande d'abord une analyse
        return "🔧 Pour corriger le code, je dois d'abord l'analyser. Veuillez me demander d'analyser le fichier en premier."
    
    def _handle_tools_request(self) -> str:
        """Gère une demande de liste d'outils."""
        tools = self.get_available_tools()
        response = "🛠️ Outils disponibles:\n\n"
        
        for tool in tools:
            response += f"- {tool}\n"
        
        return response
    
    def _handle_general_request(self, message: str) -> str:
        """Gère une demande générale."""
        return f"🤖 Je suis {self.name}. Je peux vous aider à analyser et corriger du code Python. Que souhaitez-vous faire ?"
    
    def _extract_file_path(self, message: str) -> Optional[str]:
        """Extrait le chemin du fichier du message."""
        # Recherche simple de patterns de fichiers
        import re
        
        # Pattern pour les chemins de fichiers
        patterns = [
            r'(TestProject/\w+\.py)',  # TestProject/fichier.py (priorité haute)
            r'(\w+/\w+\.py)',  # chemin/fichier.py
            r'(\w+\.py)',  # fichier.py (priorité basse)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)
        
        return None
    
    def _format_analysis_response(self, analysis: Dict, file_path: str) -> str:
        """Formate la réponse d'analyse."""
        response = f"📊 **Analyse du fichier {file_path}**\n\n"
        
        if "issues" in analysis and analysis["issues"]:
            response += "🐛 **Bugs détectés :**\n\n"
            
            for i, issue in enumerate(analysis["issues"], 1):
                response += f"{i}. **{issue.get('type', 'Problème')}**\n"
                response += f"   - **Ligne {issue.get('line', 'N/A')}**: {issue.get('description', 'Description manquante')}\n"
                
                if "suggestion" in issue:
                    response += f"   - **Suggestion**: {issue['suggestion']}\n"
                
                response += "\n"
        else:
            response += "✅ **Aucun bug détecté**\n\n"
        
        if "suggestions" in analysis and analysis["suggestions"]:
            response += "💡 **Suggestions d'amélioration :**\n\n"
            for i, suggestion in enumerate(analysis["suggestions"], 1):
                response += f"{i}. {suggestion}\n"
        
        response += "\n🔧 **Actions possibles :**\n"
        response += "- Demandez-moi de corriger les bugs détectés\n"
        response += "- Demandez-moi d'analyser un autre fichier\n"
        response += "- Demandez-moi de lister les outils disponibles\n"
        
        return response
    
    def save_session(self):
        """Sauvegarde la session."""
        self.logger.save_conversation()
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de la session."""
        return {
            "assistant_name": self.name,
            "total_messages": len(self.messages),
            "total_tool_calls": len(self.logger.conversation_data["tool_calls"]),
            "total_errors": len(self.logger.conversation_data["errors"]),
            "session_duration": datetime.now().isoformat()  # Simplifié
        }


def create_simple_assistant(name: str = "Simple Assistant", memory_engine = None) -> SimpleAssistant:
    """Factory pour créer un assistant simple."""
    return SimpleAssistant(name, memory_engine=memory_engine)


def main():
    """Test de l'assistant simple."""
    print("🕷️ Test de l'Assistant Simple")
    print("=" * 40)
    
    # Créer l'assistant
    from MemoryEngine.core.engine import MemoryEngine
    memory_engine = MemoryEngine()
    assistant = create_simple_assistant("Alma Debug Assistant", memory_engine)
    
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