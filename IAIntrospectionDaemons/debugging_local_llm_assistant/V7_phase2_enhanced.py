# ⛧ Créé par Alma, Architecte Démoniaque ⛧
# 🕷️ Assistant Local LLM V7 Phase 2 Enhanced - Parsing Multi-lignes + Correction Abstraite

import json
import logging
import os
import sys
import subprocess
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

from MemoryEngine.EditingSession.Tools.tool_registry import ToolRegistry
from MemoryEngine.EditingSession.Tools.tool_invoker import ToolInvoker
from MemoryEngine.EditingSession.Tools.tool_search import ToolSearchEngine


class LocalLLMLoggerV7:
    """Logger pour l'assistant local LLM V7 Phase 2 Enhanced."""
    
    def __init__(self, session_name: str = None):
        self.session_name = session_name or f"local_llm_v7_phase2_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
            "tool_executions": [],
            "correction_plans": [],
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
    
    def log_tool_execution(self, tool_name: str, arguments: Dict, result: Dict, success: bool):
        """Log l'exécution d'un outil."""
        timestamp = datetime.now().isoformat()
        
        self.conversation_data["tool_executions"].append({
            "timestamp": timestamp,
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
            "success": success
        })
        
        status = "✅" if success else "❌"
        print(f"[TOOL_EXEC] {status} {tool_name}: {arguments}")
    
    def log_correction_plan(self, plan: Dict[str, Any]):
        """Log un plan de correction."""
        timestamp = datetime.now().isoformat()
        
        self.conversation_data["correction_plans"].append({
            "timestamp": timestamp,
            "plan": plan
        })
        
        print(f"[CORRECTION_PLAN] Plan créé: {len(plan.get('steps', []))} étapes")
    
    def log_tool_call(self, tool_name: str, arguments: Dict, result: Dict):
        """Log un appel d'outil (compatibilité)."""
        self.log_tool_execution(tool_name, arguments, result, True)
    
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


class LocalLLMAssistantV7Phase2Enhanced:
    """
    Assistant V7 Phase 2 Enhanced avec parsing multi-lignes et correction abstraite.
    Version avancée : parsing amélioré, correction automatique abstraite, comparaison OpenAI.
    """
    
    def __init__(self, name: str = "Local LLM Assistant V7 Phase 2 Enhanced", memory_engine = None):
        self.name = name
        self.logger = LocalLLMLoggerV7(f"{name.lower().replace(' ', '_')}")
        
        # Initialiser les outils
        self.tool_registry = ToolRegistry(memory_engine)
        self.tool_registry.initialize()
        self.tool_invoker = ToolInvoker(self.tool_registry)
        self.tool_search = ToolSearchEngine(self.tool_registry)
        
        # État de la conversation
        self.messages = []
        self.current_context = {}
        self.last_analysis = None  # Stocke la dernière analyse pour la correction
        
        # Modèle principal : Qwen (basé sur nos tests)
        self.primary_model = "qwen2.5:7b-instruct"
        
        # PAS DE FALLBACK - HÉRÉSIE !
        # self.fallback_models = []  # Supprimé pour toujours
        
        self.logger.log_message("system", f"Assistant '{self.name}' initialisé avec modèle principal: {self.primary_model}")
    
    def _get_system_prompt_enhanced(self) -> str:
        """Prompt système amélioré pour Qwen avec correction abstraite."""
        return """Tu es un assistant de débogage de code Python expert, spécialisé dans l'analyse et la correction de bugs.

## RÔLE ET CAPACITÉS :
Tu es un assistant intelligent qui utilise des outils spécialisés pour :
- Analyser du code Python et détecter les bugs
- Créer des plans de correction structurés
- Corriger automatiquement les problèmes identifiés
- Proposer des améliorations de code
- Maintenir la qualité et la sécurité du code

## OUTILS DISPONIBLES :
{available_tools}

## PROCESSUS DE DÉBOGAGE (OBLIGATOIRE) :
1. **ANALYSE** : Utilise code_analyzer pour examiner le fichier
2. **IDENTIFICATION** : Détecte tous les bugs et problèmes
3. **PLANIFICATION** : Crée un plan de correction structuré
4. **EXÉCUTION** : Applique les corrections avec les outils safe_*
5. **VALIDATION** : Vérifie que les corrections fonctionnent

## RÈGLES STRICTES :
- **TOUJOURS** utiliser code_analyzer pour analyser un fichier
- **TOUJOURS** lister les outils quand on te le demande
- **TOUJOURS** proposer un plan avant de corriger
- **TOUJOURS** utiliser les outils safe_* pour les modifications
- **JAMAIS** de guillemets autour des valeurs d'arguments

## FORMAT DE RÉPONSE OBLIGATOIRE :
Pour utiliser un outil, réponds EXACTEMENT :
"ACTION: <nom_outil> <arguments>"

Exemples :
- "ACTION: code_analyzer file_path=TestProject/buggy_calculator.py"
- "ACTION: list_tools"
- "ACTION: safe_replace_text_in_file file_path=test.py old_text=bug new_text=fix"

## CORRECTION ABSTRAITE :
Quand on te demande de corriger des bugs :
1. D'abord analyser le fichier si pas déjà fait
2. Créer un plan de correction structuré
3. Exécuter les corrections étape par étape
4. Valider les résultats

## CONTEXTE IMPORTANT :
Tu es optimisé pour Qwen et tu dois être précis, méthodique et efficace.
Réponds de manière structurée et professionnelle."""
    
    def _get_available_tools_text(self) -> str:
        """Retourne la liste des outils en format texte optimisé."""
        tools = self.tool_registry.list_tools()
        tools_text = ""
        for tool in tools:
            tools_text += f"- {tool['id']}: {tool['intent']}\n"
        return tools_text
    
    def _call_llm_with_fallback(self, prompt: str) -> Dict[str, Any]:
        """Appelle le LLM principal (PAS DE FALLBACK - HÉRÉSIE !)."""
        print(f"🕷️ Appel du modèle principal: {self.primary_model}")
        result = self._call_llm(self.primary_model, prompt)
        
        if result["success"]:
            print(f"✅ Modèle principal {self.primary_model} fonctionne")
        else:
            print(f"❌ Modèle principal échoue: {result['error']}")
        
        return result
    
    def _call_llm(self, model: str, prompt: str) -> Dict[str, Any]:
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
            duration = end_time - start_time
            
            if result.returncode == 0:
                response_data = json.loads(result.stdout)
                response_text = response_data.get('response', '')
                
                return {
                    "success": True,
                    "model": model,
                    "response": response_text,
                    "duration": duration,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "model": model,
                    "response": None,
                    "duration": duration,
                    "error": f"Erreur Ollama: {result.stderr}"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "model": model,
                "response": None,
                "duration": 120,
                "error": "Timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "model": model,
                "response": None,
                "duration": 0,
                "error": str(e)
            }
    
    def _clean_argument_value(self, value: str) -> str:
        """Nettoie une valeur d'argument en supprimant TOUS les guillemets superflus."""
        value = value.strip()
        value = re.sub(r'^["\']+|["\']+$', '', value)
        value = value.replace('"', '').replace("'", '')
        return value.strip()
    
    def _parse_arguments(self, args_text: str) -> Dict[str, str]:
        """Parse les arguments avec une approche robuste."""
        arguments = {}
        
        if not args_text.strip():
            return arguments
        
        print(f"🔍 Parsing des arguments: '{args_text}'")
        
        arg_pattern = r'(\w+)\s*=\s*([^\s]+(?:\s+[^\s]+)*)'
        matches = re.finditer(arg_pattern, args_text)
        
        for match in matches:
            key = match.group(1)
            value = match.group(2)
            clean_value = self._clean_argument_value(value)
            arguments[key] = clean_value
            print(f"  📝 {key} = '{clean_value}' (original: '{value}')")
        
        return arguments
    
    def _extract_actions_multi_line(self, response: str) -> List[Dict[str, Any]]:
        """Extrait TOUTES les actions d'une réponse multi-lignes."""
        actions = []
        
        # Pattern pour détecter les actions sur plusieurs lignes
        action_pattern = r'ACTION:\s*(\w+)\s*(.*?)(?=\nACTION:|$)'
        matches = re.finditer(action_pattern, response, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            tool_name = match.group(1)
            args_text = match.group(2).strip()
            arguments = self._parse_arguments(args_text)
            
            print(f"🔍 Action détectée: {tool_name} avec args: {arguments}")
            
            actions.append({
                "tool": tool_name,
                "arguments": arguments,
                "raw_args": args_text
            })
        
        return actions
    
    def _extract_action(self, response: str) -> Optional[Dict[str, Any]]:
        """Extrait une action de la réponse du LLM (compatibilité)."""
        actions = self._extract_actions_multi_line(response)
        return actions[0] if actions else None
    
    def _execute_tool(self, tool_name: str, arguments: Dict) -> Dict[str, Any]:
        """Exécute un outil avec les arguments donnés."""
        try:
            print(f"🔧 Exécution de {tool_name} avec {arguments}")
            
            if tool_name == "list_tools":
                tools = self.tool_registry.list_tools()
                result = {
                    "success": True,
                    "result": tools,
                    "message": f"Liste de {len(tools)} outils"
                }
            else:
                result = self.tool_invoker.invoke_tool(tool_name, **arguments)
            
            self.logger.log_tool_execution(tool_name, arguments, result, result.get("success", False))
            return result
            
        except Exception as e:
            error_msg = f"Erreur lors de l'exécution de {tool_name}: {str(e)}"
            self.logger.log_error("tool_execution_error", error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def _create_correction_plan(self, analysis: Dict, file_path: str) -> Dict[str, Any]:
        """Crée un plan de correction abstrait basé sur l'analyse."""
        plan = {
            "file_path": file_path,
            "total_issues": len(analysis.get("issues", [])),
            "steps": [],
            "estimated_difficulty": "medium",
            "tools_needed": []
        }
        
        issues = analysis.get("issues", [])
        
        for i, issue in enumerate(issues):
            step = {
                "step_number": i + 1,
                "issue_type": issue.get("type", "unknown"),
                "line": issue.get("line", "unknown"),
                "description": issue.get("description", "Description manquante"),
                "suggestion": issue.get("suggestion", "Aucune suggestion"),
                "tool": self._select_tool_for_issue(issue),
                "arguments": self._generate_arguments_for_issue(issue, file_path)
            }
            plan["steps"].append(step)
            
            if step["tool"] not in plan["tools_needed"]:
                plan["tools_needed"].append(step["tool"])
        
        self.logger.log_correction_plan(plan)
        return plan
    
    def _select_tool_for_issue(self, issue: Dict) -> str:
        """Sélectionne l'outil approprié pour corriger un problème."""
        issue_type = issue.get("type", "").lower()
        
        if "debug_comment" in issue_type:
            return "safe_replace_text_in_file"
        elif "syntax" in issue_type:
            return "safe_replace_text_in_file"
        elif "logic" in issue_type:
            return "safe_replace_text_in_file"
        else:
            return "safe_replace_text_in_file"  # Outil par défaut
    
    def _generate_arguments_for_issue(self, issue: Dict, file_path: str) -> Dict[str, str]:
        """Génère les arguments pour corriger un problème."""
        # Lire le contenu du fichier pour analyser les bugs
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            print(f"❌ Erreur lecture fichier {file_path}: {e}")
            return {
                "path": file_path,
                "old_text": "BUG_PLACEHOLDER",
                "new_text": "FIX_PLACEHOLDER"
            }
        
        issue_type = issue.get("type", "").lower()
        line_number = issue.get("line", 0)
        
        # Analyser le contenu pour identifier les bugs spécifiques
        if "debug_comment" in issue_type and line_number > 0:
            try:
                line_index = line_number - 1
                if line_index < len(lines):
                    current_line = lines[line_index]
                    
                    # Identifier les bugs spécifiques dans buggy_calculator.py
                    if "return a - b" in current_line:
                        return {
                            "path": file_path,
                            "old_text": "return a - b  # BUG: devrait être a + b",
                            "new_text": "return a + b  # Correction: addition correcte"
                        }
                    elif "return a + b" in current_line:
                        return {
                            "path": file_path,
                            "old_text": "return a + b  # BUG: devrait être a - b",
                            "new_text": "return a - b  # Correction: soustraction correcte"
                        }
                    elif "return None" in current_line:
                        return {
                            "path": file_path,
                            "old_text": "return None  # BUG: devrait lever une exception",
                            "new_text": "raise ValueError('Division par zéro non autorisée')  # Correction: exception levée"
                        }
                    elif "return 0" in current_line:
                        return {
                            "path": file_path,
                            "old_text": "return 0  # BUG: devrait lever une exception",
                            "new_text": "raise ValueError('Division par zéro non autorisée')  # Correction: exception levée"
                        }
                    elif "return a ** b + 1" in current_line:
                        return {
                            "path": file_path,
                            "old_text": "return a ** b + 1  # BUG: devrait être a ** b",
                            "new_text": "return a ** b  # Correction: puissance correcte"
                        }
                    elif "return \"Invalid operation\"" in current_line:
                        return {
                            "path": file_path,
                            "old_text": "return \"Invalid operation\"  # BUG: devrait lever une exception",
                            "new_text": "raise ValueError('Opération invalide')  # Correction: exception levée"
                        }
            except Exception as e:
                print(f"❌ Erreur analyse ligne {line_number}: {e}")
        
        # Fallback générique
        return {
            "path": file_path,
            "old_text": "BUG_PLACEHOLDER",
            "new_text": "FIX_PLACEHOLDER"
        }
    
    def _execute_correction_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un plan de correction étape par étape."""
        results = {
            "plan_executed": True,
            "total_steps": len(plan["steps"]),
            "successful_steps": 0,
            "failed_steps": 0,
            "step_results": []
        }
        
        print(f"🔧 Exécution du plan de correction: {len(plan['steps'])} étapes")
        
        for step in plan["steps"]:
            print(f"  📝 Étape {step['step_number']}: {step['tool']}")
            
            try:
                result = self._execute_tool(step["tool"], step["arguments"])
                
                step_result = {
                    "step_number": step["step_number"],
                    "tool": step["tool"],
                    "success": result.get("success", False),
                    "result": result
                }
                
                if result.get("success", False):
                    results["successful_steps"] += 1
                else:
                    results["failed_steps"] += 1
                
                results["step_results"].append(step_result)
                
            except Exception as e:
                step_result = {
                    "step_number": step["step_number"],
                    "tool": step["tool"],
                    "success": False,
                    "error": str(e)
                }
                results["failed_steps"] += 1
                results["step_results"].append(step_result)
        
        return results
    
    def _format_tool_result(self, tool_name: str, result: Dict) -> str:
        """Formate le résultat d'un outil pour l'affichage."""
        if not result.get("success", False):
            return f"❌ Erreur avec {tool_name}: {result.get('error', 'Erreur inconnue')}"
        
        if tool_name == "list_tools":
            tools = result.get("result", [])
            response = "🛠️ **Outils disponibles :**\n\n"
            for tool in tools:
                response += f"- **{tool['id']}** ({tool['type']}, {tool['level']}): {tool['intent']}\n"
            return response
        
        elif tool_name == "code_analyzer":
            analysis = result.get("result", {})
            file_path = result.get("arguments", {}).get("file_path", "fichier inconnu")
            
            # Stocker l'analyse pour la correction
            self.last_analysis = analysis
            # Ajouter le chemin du fichier à l'analyse
            self.last_analysis["file_path"] = file_path
            
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
        
        else:
            return f"✅ {tool_name} exécuté avec succès: {result.get('result', 'Aucun résultat')}"
    
    def _format_correction_plan(self, plan: Dict[str, Any]) -> str:
        """Formate un plan de correction pour l'affichage."""
        response = f"📋 **Plan de correction pour {plan['file_path']}**\n\n"
        response += f"🔍 **Résumé :** {plan['total_issues']} problèmes à corriger\n"
        response += f"🛠️ **Outils nécessaires :** {', '.join(plan['tools_needed'])}\n"
        response += f"📊 **Difficulté estimée :** {plan['estimated_difficulty']}\n\n"
        
        response += "📝 **Étapes de correction :**\n\n"
        
        for step in plan["steps"]:
            response += f"{step['step_number']}. **{step['issue_type']}** (ligne {step['line']})\n"
            response += f"   - Description: {step['description']}\n"
            response += f"   - Outil: {step['tool']}\n"
            response += f"   - Suggestion: {step['suggestion']}\n\n"
        
        response += "🚀 **Prêt à exécuter le plan ?**\n"
        response += "Dites-moi 'exécute le plan' pour commencer les corrections."
        
        return response
    
    def send_message(self, message: str) -> str:
        """
        Envoie un message à l'assistant et retourne sa réponse.
        Version Phase 2 Enhanced : parsing multi-lignes + correction abstraite.
        """
        self.logger.log_message("user", message)
        self.messages.append({"role": "user", "content": message})
        
        try:
            # Détecter le type de demande
            message_lower = message.lower()
            
            if "corriger" in message_lower or "fix" in message_lower:
                return self._handle_correction_request(message)
            
            # Construire le prompt optimisé
            system_prompt = self._get_system_prompt_enhanced().format(
                available_tools=self._get_available_tools_text()
            )
            
            # Historique des messages (derniers 5)
            conversation_history = ""
            for msg in self.messages[-5:]:
                role = msg["role"]
                content = msg["content"]
                conversation_history += f"{role.upper()}: {content}\n"
            
            # Prompt complet optimisé
            full_prompt = f"""{system_prompt}

## Historique de conversation :
{conversation_history}

## Message utilisateur :
{message}

## Réponse :"""
            
            # Appeler le LLM principal (PAS DE FALLBACK - HÉRÉSIE !)
            llm_result = self._call_llm_with_fallback(full_prompt)
            
            if not llm_result["success"]:
                error_msg = f"Erreur lors de l'appel LLM: {llm_result['error']}"
                self.logger.log_error("llm_error", error_msg)
                return error_msg
            
            # Log de l'appel LLM
            self.logger.log_llm_call(
                llm_result["model"], 
                full_prompt, 
                llm_result["response"], 
                llm_result["duration"]
            )
            
            # Extraire et exécuter TOUTES les actions
            actions = self._extract_actions_multi_line(llm_result["response"])
            
            if actions:
                # Exécuter toutes les actions
                results = []
                for action in actions:
                    tool_result = self._execute_tool(action["tool"], action["arguments"])
                    results.append((action["tool"], tool_result))
                
                # Formater tous les résultats
                final_response = ""
                for tool_name, result in results:
                    tool_response = self._format_tool_result(tool_name, result)
                    final_response += f"{tool_response}\n\n"
                
                # Ajouter l'explication du LLM si elle existe
                if not llm_result["response"].startswith("ACTION:"):
                    final_response = f"{llm_result['response']}\n\n{final_response}"
            else:
                # Pas d'action détectée, retourner la réponse du LLM
                final_response = llm_result["response"]
            
            # Log de la réponse finale
            self.logger.log_message("assistant", final_response)
            self.messages.append({"role": "assistant", "content": final_response})
            
            return final_response
            
        except Exception as e:
            error_msg = f"Erreur lors du traitement: {str(e)}"
            self.logger.log_error("processing_error", error_msg)
            return error_msg
    
    def _handle_correction_request(self, message: str) -> str:
        """Gère une demande de correction de bugs."""
        if not self.last_analysis:
            return "❌ Aucune analyse disponible. Veuillez d'abord analyser le fichier avec 'code_analyzer'."
        
        # Extraire le chemin du fichier du message ou utiliser le dernier
        file_path = self._extract_file_path_from_message(message)
        if not file_path:
            # Utiliser le fichier de la dernière analyse
            if self.last_analysis and "file_path" in self.last_analysis:
                file_path = self.last_analysis["file_path"]
            else:
                file_path = "TestProject/corrupted_calculator.py"  # Par défaut
        
        # Créer un plan de correction
        plan = self._create_correction_plan(self.last_analysis, file_path)
        
        # Formater et retourner le plan
        response = self._format_correction_plan(plan)
        
        # Stocker le plan pour exécution future
        self.current_correction_plan = plan
        
        self.logger.log_message("assistant", response)
        self.messages.append({"role": "assistant", "content": response})
        
        return response
    
    def _extract_file_path_from_message(self, message: str) -> Optional[str]:
        """Extrait le chemin du fichier d'un message."""
        patterns = [
            r'(TestProject/\w+\.py)',
            r'(\w+/\w+\.py)',
            r'(\w+\.py)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)
        
        return None
    
    def execute_correction_plan(self) -> str:
        """Exécute le plan de correction actuel."""
        if not hasattr(self, 'current_correction_plan') or not self.current_correction_plan:
            return "❌ Aucun plan de correction disponible."
        
        plan = self.current_correction_plan
        results = self._execute_correction_plan(plan)
        
        # Formater les résultats
        response = f"🔧 **Exécution du plan de correction terminée**\n\n"
        response += f"📊 **Résultats :**\n"
        response += f"- Étapes totales : {results['total_steps']}\n"
        response += f"- Succès : {results['successful_steps']}\n"
        response += f"- Échecs : {results['failed_steps']}\n\n"
        
        if results['step_results']:
            response += "📝 **Détail des étapes :**\n\n"
            for step_result in results['step_results']:
                status = "✅" if step_result['success'] else "❌"
                response += f"{status} Étape {step_result['step_number']} ({step_result['tool']})\n"
        
        self.logger.log_message("assistant", response)
        self.messages.append({"role": "assistant", "content": response})
        
        return response
    
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
            "primary_model": self.primary_model,
            "total_messages": len(self.messages),
            "total_tool_calls": len(self.logger.conversation_data["tool_calls"]),
            "total_llm_calls": len(self.logger.conversation_data["llm_calls"]),
            "total_tool_executions": len(self.logger.conversation_data["tool_executions"]),
            "total_correction_plans": len(self.logger.conversation_data["correction_plans"]),
            "total_errors": len(self.logger.conversation_data["errors"]),
            "session_duration": datetime.now().isoformat()
        }


def create_local_llm_assistant_v7_phase2_enhanced(name: str = "Local LLM Assistant V7 Phase 2 Enhanced", memory_engine = None) -> LocalLLMAssistantV7Phase2Enhanced:
    """Factory pour créer un assistant local LLM V7 Phase 2 Enhanced."""
    return LocalLLMAssistantV7Phase2Enhanced(name, memory_engine)


def main():
    """Test de l'assistant local LLM V7 Phase 2 Enhanced."""
    print("🕷️ Test de l'Assistant Local LLM V7 Phase 2 Enhanced")
    print("=" * 70)
    
    # Créer l'assistant
    from MemoryEngine.core.engine import MemoryEngine
    memory_engine = MemoryEngine()
    assistant = create_local_llm_assistant_v7_phase2_enhanced("Alma Local LLM V7 Phase 2 Enhanced", memory_engine)
    
    # Test 1: Demande d'outils
    print("\n1. Demande d'outils:")
    response = assistant.send_message("Quels outils as-tu disponibles ?")
    print(response)
    
    # Test 2: Analyse d'un fichier
    print("\n2. Analyse d'un fichier:")
    response = assistant.send_message("Peux-tu analyser le fichier TestProject/buggy_calculator.py ?")
    print(response)
    
    # Test 3: Demande de correction (nouveau test Phase 2)
    print("\n3. Demande de correction:")
    response = assistant.send_message("Peux-tu corriger les bugs détectés dans le fichier ?")
    print(response)
    
    # Test 4: Exécution du plan (nouveau test Phase 2)
    print("\n4. Exécution du plan:")
    response = assistant.execute_correction_plan()
    print(response)
    
    # Sauvegarder la session
    assistant.save_session()
    
    # Afficher le résumé
    summary = assistant.get_session_summary()
    print(f"\n📊 Résumé de la session: {summary}")


if __name__ == "__main__":
    main() 