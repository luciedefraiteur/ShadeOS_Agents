# ⛧ Créé par Alma, Architecte Démoniaque ⛧
# 🕷️ V8 - Assistant Généraliste avec Partitionneur et Boucles de Travail

import os
import sys
import time
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

from MemoryEngine.core.engine import MemoryEngine
from Assistants.EditingSession.Tools.tool_registry import ToolRegistry
from LLMProviders import ProviderFactory, LLMProvider

class GeneralistAssistantLogger:
    """Logger pour l'assistant généraliste."""
    
    def __init__(self, name: str = "GeneralistAssistant"):
        self.name = name
        self.session_id = f"session_{int(time.time())}"
        self.log_dir = Path(f"logs/generalist_assistant/{time.strftime('%Y%m%d')}")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichiers de log
        self.conversation_log = self.log_dir / f"{self.session_id}_conversation.jsonl"
        self.workflow_log = self.log_dir / f"{self.session_id}_workflow.jsonl"
        self.tool_calls_log = self.log_dir / f"{self.session_id}_tool_calls.jsonl"
        
        # Données de session
        self.conversation_data = []
        self.workflow_data = []
        self.tool_calls_data = []
        
    def log_message(self, role: str, content: str, iteration: int = 0):
        """Enregistre un message."""
        entry = {
            "timestamp": time.time(),
            "role": role,
            "content": content,
            "iteration": iteration
        }
        self.conversation_data.append(entry)
        
        with open(self.conversation_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def log_workflow_step(self, step: str, details: Dict, iteration: int = 0):
        """Enregistre une étape du workflow."""
        entry = {
            "timestamp": time.time(),
            "step": step,
            "details": details,
            "iteration": iteration
        }
        self.workflow_data.append(entry)
        
        with open(self.workflow_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def log_tool_call(self, tool_name: str, arguments: Dict, result: Dict, iteration: int = 0):
        """Enregistre un appel d'outil."""
        entry = {
            "timestamp": time.time(),
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
            "iteration": iteration
        }
        self.tool_calls_data.append(entry)
        
        with open(self.tool_calls_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def save_session_summary(self):
        """Sauvegarde un résumé de la session."""
        summary = {
            "session_id": self.session_id,
            "total_messages": len(self.conversation_data),
            "total_workflow_steps": len(self.workflow_data),
            "total_tool_calls": len(self.tool_calls_data),
            "duration": time.time() - float(self.conversation_data[0]["timestamp"]) if self.conversation_data else 0,
            "log_files": {
                "conversation": str(self.conversation_log),
                "workflow": str(self.workflow_log),
                "tool_calls": str(self.tool_calls_log)
            }
        }
        
        summary_file = self.log_dir / f"{self.session_id}_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return summary

class GeneralistAssistant:
    """Assistant généraliste avec partitionneur et boucles de travail."""
    
    def __init__(self, memory_engine: MemoryEngine, tool_registry: ToolRegistry, 
                 provider_type: str = "local", model: str = "qwen2.5:7b-instruct", **provider_config):
        """Initialise l'assistant généraliste avec provider LLM configurable."""
        self.memory_engine = memory_engine
        self.tool_registry = tool_registry
        self.primary_model = model
        self.name = "GeneralistAssistant"
        self.logger = GeneralistAssistantLogger("GeneralistAssistant")
        
        # Configuration du provider LLM
        self.provider_type = provider_type
        self.provider_config = {
            "model": model,
            "timeout": provider_config.get("timeout", 60),
            "temperature": provider_config.get("temperature", 0.7),
            **provider_config
        }
        
        # Initialisation du provider (sera fait lors du premier appel)
        self.provider = None
        
        # Créer le ToolInvoker
        from MemoryEngine.EditingSession.Tools.tool_invoker import ToolInvoker
        self.tool_invoker = ToolInvoker(tool_registry)
        
        # État du workflow
        self.current_iteration = 0
        self.max_iterations = 10  # Limite de sécurité
        self.workflow_complete = False
        self.context = {}
        
        self.logger.log_message("system", f"Assistant '{self.name}' initialisé avec provider: {provider_type}, modèle: {model}")
    
    async def _initialize_provider(self):
        """Initialise le provider LLM si nécessaire."""
        if self.provider is None:
            try:
                self.provider, validation = await ProviderFactory.create_and_validate_provider(
                    self.provider_type, **self.provider_config
                )
                
                if not validation.valid:
                    raise Exception(f"Provider {self.provider_type} invalide: {validation.error}")
                
                self.logger.log_message("system", f"Provider {self.provider_type} initialisé avec succès")
                
            except Exception as e:
                self.logger.log_message("system", f"Erreur d'initialisation du provider: {e}")
                raise
    
    async def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """Appelle le LLM via le système de providers."""
        try:
            # Initialisation du provider si nécessaire
            await self._initialize_provider()
            
            # Appel du LLM
            response = await self.provider.generate_response(prompt)
            
            if response.content.startswith("ERREUR:"):
                return {
                    "success": False,
                    "response": None,
                    "error": response.content,
                    "provider_info": self.provider.get_provider_info()
                }
            else:
                return {
                    "success": True,
                    "response": response.content,
                    "error": None,
                    "provider_info": self.provider.get_provider_info(),
                    "response_time": response.response_time,
                    "tokens_used": response.tokens_used
                }
                
        except Exception as e:
            return {
                "success": False,
                "response": None,
                "error": str(e),
                "provider_info": self.provider.get_provider_info() if self.provider else None
            }
    
    def _get_system_prompt(self) -> str:
        """Prompt système pour l'assistant généraliste."""
        return """Tu es un assistant généraliste intelligent. Tu as accès à plusieurs outils pour accomplir tes tâches.

OUTILS DISPONIBLES ET LEURS PARAMÈTRES EXACTS:
- **code_analyzer**: Analyse un fichier Python pour détecter des bugs
  - Paramètre requis: file_path (chemin du fichier à analyser)
- **safe_replace_text_in_file**: Remplace du texte dans un fichier de manière sécurisée
  - Paramètres requis: path (chemin du fichier), old_text (texte à remplacer), new_text (nouveau texte)
- **safe_read_file_content**: Lit le contenu d'un fichier
  - Paramètre requis: path (chemin du fichier)
- **list_tools**: Liste tous les outils disponibles
  - Aucun paramètre requis

FORMAT DE RÉPONSE:
- Pour utiliser un outil: ACTION: nom_outil paramètre=valeur
- Pour continuer le travail: CONTINUE: description de la prochaine étape
- Pour terminer: DONE: résumé du travail accompli

EXEMPLES D'UTILISATION:
- ACTION: code_analyzer file_path=TestProject/corrupted_calculator.py
- ACTION: safe_replace_text_in_file path=TestProject/corrupted_calculator.py old_text=return a - b new_text=return a + b
- ACTION: safe_read_file_content path=TestProject/corrupted_calculator.py

STRATÉGIE DE TRAVAIL:
1. Analyse la demande de l'utilisateur
2. Utilise code_analyzer pour détecter les bugs
3. Utilise safe_replace_text_in_file pour corriger chaque bug trouvé
4. Continue jusqu'à ce que tous les bugs soient corrigés
5. Fournis un résumé final

EXEMPLE DE WORKFLOW POUR CORRECTION:
1. ACTION: code_analyzer file_path=TestProject/corrupted_calculator.py
2. ACTION: safe_replace_text_in_file path=TestProject/corrupted_calculator.py old_text=return a - b new_text=return a + b
3. ACTION: safe_replace_text_in_file path=TestProject/corrupted_calculator.py old_text=return a + b new_text=return a - b
4. DONE: Tous les bugs corrigés

IMPORTANT: Utilise EXACTEMENT les noms de paramètres indiqués ci-dessus !"""
    
    def _extract_actions(self, response: str) -> List[Dict[str, Any]]:
        """Extrait les actions de la réponse du LLM."""
        actions = []
        
        # Chercher les patterns ACTION: et CONTINUE: et DONE:
        action_pattern = r'ACTION:\s*(\w+)\s+([^\n]+)'
        continue_pattern = r'CONTINUE:\s*([^\n]+)'
        done_pattern = r'DONE:\s*([^\n]+)'
        
        # Extraire les actions
        for match in re.finditer(action_pattern, response):
            tool_name = match.group(1)
            args_str = match.group(2)
            
            # Parser les arguments
            arguments = {}
            arg_pattern = r'(\w+)=([^\s]+)'
            for arg_match in re.finditer(arg_pattern, args_str):
                key = arg_match.group(1)
                value = arg_match.group(2)
                # Nettoyer les valeurs
                value = value.strip('"\'')
                arguments[key] = value
            
            actions.append({
                "type": "action",
                "tool_name": tool_name,
                "arguments": arguments
            })
        
        # Extraire les continues
        for match in re.finditer(continue_pattern, response):
            actions.append({
                "type": "continue",
                "description": match.group(1).strip()
            })
        
        # Extraire les done
        for match in re.finditer(done_pattern, response):
            actions.append({
                "type": "done",
                "summary": match.group(1).strip()
            })
        
        return actions
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un outil."""
        try:
            self.logger.log_tool_call(tool_name, arguments, {}, self.current_iteration)
            
            # Appeler l'outil via le registre
            result = self.tool_registry.invoke_tool(tool_name, **arguments)
            
            # Mettre à jour le log avec le résultat
            self.logger.log_tool_call(tool_name, arguments, result, self.current_iteration)
            
            return {
                "success": True,
                "result": result,
                "tool_name": tool_name
            }
        except Exception as e:
            error_result = {"success": False, "error": str(e)}
            self.logger.log_tool_call(tool_name, arguments, error_result, self.current_iteration)
            return error_result
    
    async def _process_workflow_iteration(self, user_message: str, context: str = "") -> Dict[str, Any]:
        """Traite une itération du workflow."""
        self.current_iteration += 1
        
        if self.current_iteration > self.max_iterations:
            return {
                "success": False,
                "error": f"Limite d'itérations atteinte ({self.max_iterations})",
                "iteration": self.current_iteration
            }
        
        # Construire le prompt
        system_prompt = self._get_system_prompt()
        
        # Ajouter le contexte
        context_part = f"\nCONTEXTE ACTUEL:\n{context}\n" if context else ""
        
        # Ajouter l'historique des actions avec résultats détaillés
        history_part = ""
        if self.logger.tool_calls_data:
            # Filtrer seulement les appels réussis avec des résultats
            successful_calls = []
            for call in self.logger.tool_calls_data:
                if call['result'].get('success', False) and 'result' in call['result']:
                    successful_calls.append(call)
            
            recent_calls = successful_calls[-3:]  # 3 derniers appels réussis
            if recent_calls:
                history_part = "\nRÉSULTATS RÉCENTS:\n"
                for call in recent_calls:
                    success = call['result'].get('success', False)
                    history_part += f"- {call['tool_name']}: {'SUCCÈS' if success else 'ÉCHEC'}\n"
                    
                    # Ajouter les détails pour les succès
                    if success:
                        # Fonction récursive pour extraire les résultats
                        def extract_result_data(data, depth=0):
                            if depth > 5:  # Protection contre récursion infinie
                                return None
                            if isinstance(data, dict):
                                if 'result' in data:
                                    return extract_result_data(data['result'], depth + 1)
                                elif 'issues' in data:  # On a trouvé les données finales
                                    return data
                            return None
                        
                        result_data = extract_result_data(call['result'])
                        if result_data and isinstance(result_data, dict):
                            # Pour code_analyzer, afficher les bugs trouvés
                            if call['tool_name'] == 'code_analyzer' and 'issues' in result_data:
                                issues = result_data['issues']
                                history_part += f"  Bugs détectés: {len(issues)}\n"
                                for i, issue in enumerate(issues[:3]):  # Limiter à 3 bugs
                                    history_part += f"  - Bug {i+1}: {issue.get('message', 'N/A')} (ligne {issue.get('line', 'N/A')})\n"
                            
                            # Pour safe_replace_text_in_file, afficher le résultat
                            elif call['tool_name'] == 'safe_replace_text_in_file':
                                history_part += f"  Texte remplacé avec succès\n"
                    
                    # Ajouter les erreurs pour les échecs
                    elif not success:
                        error = call['result'].get('error', 'Erreur inconnue')
                        history_part += f"  Erreur: {error}\n"
        
        full_prompt = f"{system_prompt}{context_part}{history_part}\n\n[USER] {user_message}\n\n[ASSISTANT]"
        
        # Debug: afficher le prompt complet
        print(f"\n=== PROMPT COMPLET (Itération {self.current_iteration}) ===")
        print(full_prompt)
        print("=== FIN DU PROMPT ===\n")
        
        # Appeler le LLM
        self.logger.log_message("user", user_message, self.current_iteration)
        llm_result = await self._call_llm(full_prompt)
        
        if not llm_result["success"]:
            return {
                "success": False,
                "error": f"Erreur LLM: {llm_result['error']}",
                "iteration": self.current_iteration
            }
        
        response = llm_result["response"]
        self.logger.log_message("assistant", response, self.current_iteration)
        
        # Extraire les actions
        actions = self._extract_actions(response)
        
        # Traiter les actions
        results = []
        workflow_complete = False
        next_context = context
        
        for action in actions:
            if action["type"] == "action":
                # Exécuter l'outil
                tool_result = self._execute_tool(action["tool_name"], action["arguments"])
                results.append({
                    "type": "tool_call",
                    "tool_name": action["tool_name"],
                    "result": tool_result
                })
                
                # Ajouter au contexte
                if tool_result["success"]:
                    next_context += f"\nOutil {action['tool_name']} exécuté avec succès"
                else:
                    next_context += f"\nErreur avec {action['tool_name']}: {tool_result.get('error', 'Unknown error')}"
            
            elif action["type"] == "continue":
                # Continuer le workflow
                results.append({
                    "type": "continue",
                    "description": action["description"]
                })
                next_context += f"\nProchaine étape: {action['description']}"
            
            elif action["type"] == "done":
                # Terminer le workflow
                results.append({
                    "type": "done",
                    "summary": action["summary"]
                })
                workflow_complete = True
                next_context += f"\nTravail terminé: {action['summary']}"
        
        # Enregistrer l'étape du workflow
        self.logger.log_workflow_step("iteration", {
            "iteration": self.current_iteration,
            "actions_count": len(actions),
            "results": results,
            "workflow_complete": workflow_complete
        }, self.current_iteration)
        
        return {
            "success": True,
            "iteration": self.current_iteration,
            "response": response,
            "actions": actions,
            "results": results,
            "workflow_complete": workflow_complete,
            "next_context": next_context
        }
    
    async def process_request(self, user_message: str) -> Dict[str, Any]:
        """Traite une demande utilisateur avec boucles de travail."""
        print(f"🕷️ Assistant Généraliste - Traitement de: {user_message}")
        
        start_time = time.time()
        context = ""
        all_results = []
        
        # Boucle de travail
        while not self.workflow_complete and self.current_iteration < self.max_iterations:
            print(f"🔄 Itération {self.current_iteration + 1}...")
            
            iteration_result = await self._process_workflow_iteration(user_message, context)
            
            if not iteration_result["success"]:
                return {
                    "success": False,
                    "error": iteration_result["error"],
                    "duration": time.time() - start_time,
                    "iterations": self.current_iteration,
                    "results": all_results
                }
            
            all_results.append(iteration_result)
            context = iteration_result["next_context"]
            self.workflow_complete = iteration_result["workflow_complete"]
            
            if self.workflow_complete:
                print(f"✅ Travail terminé après {self.current_iteration} itérations")
                break
        
        duration = time.time() - start_time
        
        # Sauvegarder le résumé de session
        summary = self.logger.save_session_summary()
        
        return {
            "success": True,
            "duration": duration,
            "iterations": self.current_iteration,
            "workflow_complete": self.workflow_complete,
            "results": all_results,
            "summary": summary
        }

def regenerate_corrupted_file():
    """Régénère le fichier corrompu."""
    corrupted_content = '''# 🕷️ Calculateur corrompu pour test de correction automatique
# ⛧ Créé par Alma, Architecte Démoniaque ⛧

def add(a, b):
    """Addition avec bug évident."""
    return a - b  # BUG: devrait être a + b

def subtract(a, b):
    """Soustraction avec bug évident."""
    return a + b  # BUG: devrait être a - b

def multiply(a, b):
    """Multiplication avec bug évident."""
    if b == 0:
        return None  # BUG: devrait lever une exception
    return a * b

def divide(a, b):
    """Division avec bug évident."""
    if b == 0:
        return 0  # BUG: devrait lever une exception
    return a / b

def power(a, b):
    """Puissance avec bug évident."""
    return a ** b + 1  # BUG: devrait être a ** b

def calculate(operation, a, b):
    """Fonction principale avec bug évident."""
    if operation == "add":
        return add(a, b)
    elif operation == "subtract":
        return subtract(a, b)
    elif operation == "multiply":
        return multiply(a, b)
    elif operation == "divide":
        return divide(a, b)
    elif operation == "power":
        return power(a, b)
    else:
        return "Invalid operation"  # BUG: devrait lever une exception

# Tests avec bugs
if __name__ == "__main__":
    print("Testing corrupted calculator...")
    
    # Test 1: Addition buggée
    result = calculate("add", 5, 3)
    print(f"5 + 3 = {result}")  # Devrait être 8, mais sera 2
    
    # Test 2: Division par zéro buggée
    result = calculate("divide", 10, 0)
    print(f"10 / 0 = {result}")  # Devrait lever une exception
    
    # Test 3: Puissance buggée
    result = calculate("power", 2, 3)
    print(f"2^3 = {result}")  # Devrait être 8, mais sera 9
'''
    
    test_file = Path("TestProject/corrupted_calculator.py")
    test_file.parent.mkdir(exist_ok=True)
    test_file.write_text(corrupted_content, encoding='utf-8')
    print(f"🔄 Fichier corrompu régénéré: {test_file}")

async def test_generalist_assistant():
    """Test de l'assistant généraliste."""
    print("🕷️ Test de l'Assistant Généraliste V8")
    print("=" * 60)
    
    # Initialiser
    memory_engine = MemoryEngine()
    tool_registry = ToolRegistry(memory_engine)
    tool_registry.initialize()
    
    # Créer l'assistant
    assistant = GeneralistAssistant(memory_engine, tool_registry)
    
    # Scénarios de test
    scenarios = [
        ("Analyse et correction complète", "Peux-tu analyser et corriger tous les bugs dans TestProject/corrupted_calculator.py ?"),
        ("Analyse de structure", "Peux-tu analyser la structure du fichier TestProject/corrupted_calculator.py avec le partitionneur ?"),
        ("Correction ciblée", "Peux-tu corriger seulement les bugs d'addition et de soustraction dans le fichier ?")
    ]
    
    for scenario_name, message in scenarios:
        print(f"\n🔍 Test du scénario: {scenario_name}")
        print(f"📝 Message: {message}")
        print("-" * 50)
        
        # Régénérer le fichier corrompu
        regenerate_corrupted_file()
        
        # Traiter la demande
        result = await assistant.process_request(message)
        
        if result["success"]:
            print(f"✅ Succès: {result['iterations']} itérations en {result['duration']:.2f}s")
            print(f"📊 Workflow complet: {result['workflow_complete']}")
            print(f"📁 Logs: {result['summary']['log_files']['conversation']}")
        else:
            print(f"❌ Échec: {result['error']}")
    
    print("\n🎉 Test de l'assistant généraliste terminé !")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_generalist_assistant()) 