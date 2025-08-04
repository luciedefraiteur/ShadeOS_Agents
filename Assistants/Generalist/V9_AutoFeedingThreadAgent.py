# ⛧ Créé par Alma, Architecte Démoniaque ⛧
# 🕷️ V9 - Assistant Auto-Feeding Thread avec Construction + Debug

import os
import sys
import time
import json
import re
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

from MemoryEngine.core.engine import MemoryEngine
from MemoryEngine.core.workspace_layer import WorkspaceLayer
from MemoryEngine.core.git_virtual_layer import GitVirtualLayer
from Core.UniversalAutoFeedingThread import UniversalAutoFeedingThread
from Assistants.EditingSession.Tools.tool_registry import ToolRegistry
from LLMProviders import ProviderFactory, LLMProvider

@dataclass
class ThreadMessage:
    """Message dans le thread introspectif."""
    timestamp: float
    role: str  # "self", "workspace", "git", "memory", "user"
    content: str
    metadata: Dict[str, Any] = None

class AutoFeedingThreadLogger:
    """Logger pour l'assistant auto-feeding thread."""
    
    def __init__(self, name: str = "AutoFeedingThreadAgent"):
        self.name = name
        self.session_id = f"session_{int(time.time())}"
        self.log_dir = Path(f"logs/auto_feeding_thread/{time.strftime('%Y%m%d')}")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichiers de log
        self.thread_log = self.log_dir / f"{self.session_id}_thread.jsonl"
        self.workspace_log = self.log_dir / f"{self.session_id}_workspace.jsonl"
        self.git_log = self.log_dir / f"{self.session_id}_git.jsonl"
        self.debug_log = self.log_dir / f"{self.session_id}_debug.jsonl"
        
        # Données de session
        self.thread_messages = []
        self.workspace_actions = []
        self.git_actions = []
        self.debug_actions = []
        
    def log_thread_message(self, message: ThreadMessage):
        """Enregistre un message du thread."""
        self.thread_messages.append(message)
        
        entry = {
            "timestamp": message.timestamp,
            "role": message.role,
            "content": message.content,
            "metadata": message.metadata or {}
        }
        
        with open(self.thread_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def log_workspace_action(self, action: str, details: Dict, result: Dict):
        """Enregistre une action workspace."""
        entry = {
            "timestamp": time.time(),
            "action": action,
            "details": details,
            "result": result
        }
        self.workspace_actions.append(entry)
        
        with open(self.workspace_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def log_git_action(self, action: str, details: Dict, result: Dict):
        """Enregistre une action git."""
        entry = {
            "timestamp": time.time(),
            "action": action,
            "details": details,
            "result": result
        }
        self.git_actions.append(entry)
        
        with open(self.git_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def log_debug_action(self, action: str, details: Dict, result: Dict):
        """Enregistre une action de debug."""
        entry = {
            "timestamp": time.time(),
            "action": action,
            "details": details,
            "result": result
        }
        self.debug_actions.append(entry)
        
        with open(self.debug_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def save_session_summary(self):
        """Sauvegarde un résumé de la session."""
        summary = {
            "session_id": self.session_id,
            "total_thread_messages": len(self.thread_messages),
            "total_workspace_actions": len(self.workspace_actions),
            "total_git_actions": len(self.git_actions),
            "total_debug_actions": len(self.debug_actions),
            "duration": time.time() - float(self.thread_messages[0].timestamp) if self.thread_messages else 0,
            "log_files": {
                "thread": str(self.thread_log),
                "workspace": str(self.workspace_log),
                "git": str(self.git_log),
                "debug": str(self.debug_log)
            }
        }
        
        summary_file = self.log_dir / f"{self.session_id}_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return summary

class AutoFeedingThreadAgent:
    """Assistant auto-feeding thread avec construction + debug."""
    
    def __init__(self, memory_engine: MemoryEngine, tool_registry: ToolRegistry, 
                 provider_type: str = "local", model: str = "qwen2.5:7b-instruct", 
                 workspace_path: str = ".", **provider_config):
        """Initialise l'assistant auto-feeding thread."""
        self.memory_engine = memory_engine
        self.tool_registry = tool_registry
        self.primary_model = model
        self.name = "AutoFeedingThreadAgent"
        self.logger = AutoFeedingThreadLogger("AutoFeedingThreadAgent")
        self.workspace_path = workspace_path
        
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
        from Assistants.EditingSession.Tools.tool_invoker import ToolInvoker
        self.tool_invoker = ToolInvoker(tool_registry)
        
        # Thread auto-feed simple
        self.auto_feed_thread = UniversalAutoFeedingThread(
            entity_id="V9_AutoFeedingAgent",
            entity_type="assistant"
        )
        
        # Couches workspace et git (seront mises à jour après initialisation du provider)
        self.workspace_layer = None
        self.git_layer = None
        
        # État du workflow
        self.current_iteration = 0
        self.max_iterations = 15  # Plus d'itérations pour le thread auto-feed
        self.workflow_complete = False
        self.context = {}
        self.project_context = {}
        
        # Debug en temps réel
        self.debug_mode = True
        
        self.logger.log_thread_message(ThreadMessage(
            timestamp=time.time(),
            role="self",
            content=f"Assistant '{self.name}' initialisé avec provider: {provider_type}, modèle: {model}",
            metadata={"type": "initialization"}
        ))
    
    async def _initialize_provider(self):
        """Initialise le provider LLM si nécessaire."""
        if self.provider is None:
            try:
                self.provider, validation = await ProviderFactory.create_and_validate_provider(
                    self.provider_type, **self.provider_config
                )
                
                if not validation.valid:
                    raise Exception(f"Provider {self.provider_type} invalide: {validation.error}")
                
                # Initialiser les couches avec le provider
                self.workspace_layer = WorkspaceLayer(self.memory_engine, self.provider, workspace_path)
                self.git_layer = GitVirtualLayer(self.memory_engine, workspace_path)
                
                self.logger.log_thread_message(ThreadMessage(
                    timestamp=time.time(),
                    role="self",
                    content=f"Provider {self.provider_type} initialisé avec succès",
                    metadata={"type": "provider_initialization"}
                ))
                
            except Exception as e:
                self.logger.log_thread_message(ThreadMessage(
                    timestamp=time.time(),
                    role="self",
                    content=f"Erreur d'initialisation du provider: {e}",
                    metadata={"type": "error"}
                ))
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
        """Prompt système pour l'assistant auto-feeding thread."""
        return """Tu es un assistant auto-feeding thread intelligent. Tu as accès à plusieurs couches et outils pour construire et déboguer des projets.

COUCHES DISPONIBLES:
1. **WorkspaceLayer**: Recherche intelligente dans le workspace (grep, fractal, temporal, mixed)
2. **GitVirtualLayer**: Analyse de l'historique Git et patterns de développement
3. **MemoryEngine**: Système de mémoire fractal temporel
4. **ToolRegistry**: Outils de manipulation de fichiers et code

OUTILS DISPONIBLES:
- **code_analyzer**: Analyse un fichier Python pour détecter des bugs
- **safe_replace_text_in_file**: Remplace du texte dans un fichier de manière sécurisée
- **safe_read_file_content**: Lit le contenu d'un fichier
- **safe_create_file**: Crée un nouveau fichier
- **list_tools**: Liste tous les outils disponibles

FORMAT DE RÉPONSE EXACT (utilisez exactement ces formats):
- LAYER: nom_couche action paramètres
- TOOL: nom_outil paramètres
- INTROSPECT: question ou observation
- CONTINUE: description de la prochaine étape
- DONE: résumé du travail accompli

NOMS DE COUCHES EXACTS (utilisez exactement):
- "workspace" (pas workspaceLayer, pas WorkspaceLayer)
- "git" (pas gitLayer, pas GitLayer)

EXEMPLES D'UTILISATION CORRECTS:
- LAYER: workspace intelligent_search query="bug calculator"
- LAYER: git search_git_history query="memory engine"
- TOOL: code_analyzer file_path=TestProject/calculator.py
- INTROSPECT: J'ai trouvé 3 bugs, je vais les corriger un par un
- CONTINUE: Analyser le fichier suivant pour détecter d'autres problèmes
- DONE: Projet construit et débogué avec succès

IMPORTANT: Respectez EXACTEMENT les noms de couches "workspace" et "git" sans majuscules ni suffixes !

STRATÉGIE DE TRAVAIL:
1. Analyser la demande utilisateur
2. Explorer le workspace avec WorkspaceLayer
3. Analyser l'historique Git si pertinent
4. Construire ou déboguer le projet étape par étape
5. S'introspecter régulièrement pour optimiser l'approche
6. Fournir un résumé final détaillé

IMPORTANT: Utilise le thread introspectif pour documenter tes pensées et décisions !"""
    
    def _extract_actions(self, response: str) -> List[Dict[str, Any]]:
        """Extrait les actions de la réponse du LLM."""
        actions = []
        
        # Chercher les patterns LAYER:, TOOL:, INTROSPECT:, CONTINUE:, DONE:
        layer_pattern = r'LAYER:\s*(\w+)\s+([^\n]+)'
        tool_pattern = r'TOOL:\s*(\w+)\s+([^\n]+)'
        introspect_pattern = r'INTROSPECT:\s*([^\n]+)'
        continue_pattern = r'CONTINUE:\s*([^\n]+)'
        done_pattern = r'DONE:\s*([^\n]+)'
        
        # Extraire les actions de couche
        for match in re.finditer(layer_pattern, response):
            layer_name = match.group(1)
            action_str = match.group(2)
            
            # Parser les paramètres
            arguments = {}
            arg_pattern = r'(\w+)=([^\s]+)'
            for arg_match in re.finditer(arg_pattern, action_str):
                key = arg_match.group(1)
                value = arg_match.group(2)
                value = value.strip('"\'')
                arguments[key] = value
            
            actions.append({
                "type": "layer",
                "layer_name": layer_name.lower(),  # Normaliser en minuscules
                "action": action_str.split()[0] if action_str.split() else "unknown",
                "arguments": arguments
            })
        
        # Extraire les actions d'outil
        for match in re.finditer(tool_pattern, response):
            tool_name = match.group(1)
            args_str = match.group(2)
            
            arguments = {}
            arg_pattern = r'(\w+)=([^\s]+)'
            for arg_match in re.finditer(arg_pattern, args_str):
                key = arg_match.group(1)
                value = arg_match.group(2)
                value = value.strip('"\'')
                arguments[key] = value
            
            actions.append({
                "type": "tool",
                "tool_name": tool_name,
                "arguments": arguments
            })
        
        # Extraire les introspections
        for match in re.finditer(introspect_pattern, response):
            actions.append({
                "type": "introspect",
                "content": match.group(1).strip()
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
    
    async def _execute_layer_action(self, layer_name: str, action: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une action de couche."""
        try:
            if layer_name == "workspace":
                if action == "intelligent_search":
                    result = await self.workspace_layer.intelligent_search(arguments.get("query", ""))
                    self.logger.log_workspace_action("intelligent_search", arguments, result)
                    return {"success": True, "result": result}
                elif action == "analyze_workspace_structure":
                    result = await self.workspace_layer.analyze_workspace_structure()
                    self.logger.log_workspace_action("analyze_workspace_structure", arguments, result)
                    return {"success": True, "result": result}
                else:
                    return {"success": False, "error": f"Action workspace inconnue: {action}"}
            
            elif layer_name == "git":
                if action == "search_git_history":
                    result = await self.git_layer.search_git_history(arguments.get("query", ""))
                    self.logger.log_git_action("search_git_history", arguments, result)
                    return {"success": True, "result": result}
                elif action == "analyze_development_patterns":
                    result = await self.git_layer.analyze_development_patterns(arguments.get("time_range", "auto"))
                    self.logger.log_git_action("analyze_development_patterns", arguments, result)
                    return {"success": True, "result": result}
                else:
                    return {"success": False, "error": f"Action git inconnue: {action}"}
            
            else:
                return {"success": False, "error": f"Couche inconnue: {layer_name}"}
                
        except Exception as e:
            error_result = {"success": False, "error": str(e)}
            if layer_name == "workspace":
                self.logger.log_workspace_action(action, arguments, error_result)
            elif layer_name == "git":
                self.logger.log_git_action(action, arguments, error_result)
            return error_result
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un outil."""
        try:
            # Appeler l'outil via le registre
            result = self.tool_registry.invoke_tool(tool_name, **arguments)
            
            self.logger.log_debug_action("tool_call", {
                "tool_name": tool_name,
                "arguments": arguments
            }, result)
            
            return {
                "success": True,
                "result": result,
                "tool_name": tool_name
            }
        except Exception as e:
            error_result = {"success": False, "error": str(e)}
            self.logger.log_debug_action("tool_call", {
                "tool_name": tool_name,
                "arguments": arguments
            }, error_result)
            return error_result
    
    async def _process_thread_iteration(self, user_message: str, context: str = "") -> Dict[str, Any]:
        """Traite une itération du thread auto-feed."""
        self.current_iteration += 1
        
        if self.current_iteration > self.max_iterations:
            return {
                "success": False,
                "error": f"Limite d'itérations atteinte ({self.max_iterations})",
                "iteration": self.current_iteration
            }
        
        # Initialiser le provider au début pour que les couches soient disponibles
        try:
            await self._initialize_provider()
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur d'initialisation du provider: {e}",
                "iteration": self.current_iteration
            }
        
        # Construire le prompt
        system_prompt = self._get_system_prompt()
        
        # Ajouter le contexte
        context_part = f"\nCONTEXTE ACTUEL:\n{context}\n" if context else ""
        
        # Ajouter l'historique du thread auto-feed
        thread_history = self.auto_feed_thread.get_context_summary(5)
        
        # Ajouter les résultats récents
        recent_results = ""
        if self.logger.workspace_actions or self.logger.git_actions or self.logger.debug_actions:
            recent_results = "\nRÉSULTATS RÉCENTS:\n"
            
            # Workspace actions
            if self.logger.workspace_actions:
                recent_workspace = self.logger.workspace_actions[-2:]  # 2 derniers
                for action in recent_workspace:
                    result = action['result']
                    success = result.get('success', False) if isinstance(result, dict) else True
                    recent_results += f"- Workspace {action['action']}: {'SUCCÈS' if success else 'ÉCHEC'}\n"
            
            # Git actions
            if self.logger.git_actions:
                recent_git = self.logger.git_actions[-2:]  # 2 derniers
                for action in recent_git:
                    result = action['result']
                    success = result.get('success', False) if isinstance(result, dict) else True
                    recent_results += f"- Git {action['action']}: {'SUCCÈS' if success else 'ÉCHEC'}\n"
            
            # Debug actions
            if self.logger.debug_actions:
                recent_debug = self.logger.debug_actions[-2:]  # 2 derniers
                for action in recent_debug:
                    success = action['result'].get('success', False)
                    recent_results += f"- Tool {action['details'].get('tool_name', 'unknown')}: {'SUCCÈS' if success else 'ÉCHEC'}\n"
        
        full_prompt = f"{system_prompt}{context_part}{thread_history}{recent_results}\n\n[USER] {user_message}\n\n[ASSISTANT]"
        
        # Debug: afficher le prompt complet
        if self.debug_mode:
            print(f"\n=== PROMPT COMPLET (Itération {self.current_iteration}) ===")
            print(full_prompt)
            print("=== FIN DU PROMPT ===\n")
        
        # Appeler le LLM
        self.auto_feed_thread.add_user_message(user_message, {"iteration": self.current_iteration})
        
        llm_result = await self._call_llm(full_prompt)
        
        if not llm_result["success"]:
            return {
                "success": False,
                "error": f"Erreur LLM: {llm_result['error']}",
                "iteration": self.current_iteration
            }
        
        response = llm_result["response"]
        self.auto_feed_thread.add_self_message(response, {"iteration": self.current_iteration, "provider_info": llm_result.get("provider_info")})
        
        # Extraire les actions
        actions = self._extract_actions(response)
        
        # Traiter les actions
        results = []
        workflow_complete = False
        next_context = context
        
        for action in actions:
            if action["type"] == "layer":
                # Exécuter l'action de couche
                layer_result = await self._execute_layer_action(
                    action["layer_name"], 
                    action["action"], 
                    action["arguments"]
                )
                results.append({
                    "type": "layer_action",
                    "layer_name": action["layer_name"],
                    "action": action["action"],
                    "result": layer_result
                })
                
                # Ajouter au contexte
                if layer_result["success"]:
                    next_context += f"\nCouche {action['layer_name']} {action['action']} exécutée avec succès"
                else:
                    next_context += f"\nErreur avec {action['layer_name']} {action['action']}: {layer_result.get('error', 'Unknown error')}"
            
            elif action["type"] == "tool":
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
            
            elif action["type"] == "introspect":
                # Ajouter au thread auto-feed
                self.auto_feed_thread.add_self_message(f"INTROSPECTION: {action['content']}", {"type": "introspection", "iteration": self.current_iteration})
                
                results.append({
                    "type": "introspect",
                    "content": action["content"]
                })
                
                next_context += f"\nIntrospection: {action['content']}"
            
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
        """Traite une demande utilisateur avec thread auto-feed."""
        print(f"🕷️ Assistant Auto-Feeding Thread - Traitement de: {user_message}")
        
        start_time = time.time()
        context = ""
        all_results = []
        
        # Boucle de travail avec thread auto-feed
        while not self.workflow_complete and self.current_iteration < self.max_iterations:
            print(f"🔄 Itération {self.current_iteration + 1}...")
            
            iteration_result = await self._process_thread_iteration(user_message, context)
            
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

def create_test_project():
    """Crée un projet de test simple."""
    test_project_dir = Path("TestProject/V9_Test")
    test_project_dir.mkdir(parents=True, exist_ok=True)
    
    # Fichier principal avec bugs
    main_file = test_project_dir / "main.py"
    main_content = '''# 🕷️ Projet de test V9 avec bugs pour auto-feeding thread
# ⛧ Créé par Alma, Architecte Démoniaque ⛧

def calculate_sum(numbers):
    """Calcule la somme d'une liste de nombres."""
    total = 0
    for num in numbers:
        total += num
    return total + 1  # BUG: devrait être return total

def find_max(numbers):
    """Trouve le maximum d'une liste de nombres."""
    if not numbers:
        return None  # BUG: devrait lever une exception
    
    max_num = numbers[0]
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

def validate_email(email):
    """Valide une adresse email."""
    if "@" not in email:
        return False
    if "." not in email:
        return False
    return True  # BUG: validation trop simple

def process_data(data_list):
    """Traite une liste de données."""
    results = []
    for item in data_list:
        if isinstance(item, int):
            results.append(item * 2)
        elif isinstance(item, str):
            results.append(item.upper())
        else:
            results.append(None)  # BUG: devrait gérer les autres types
    return results

if __name__ == "__main__":
    # Tests avec bugs
    print("Testing V9 project...")
    
    # Test 1: Somme buggée
    numbers = [1, 2, 3, 4, 5]
    result = calculate_sum(numbers)
    print(f"Sum of {numbers} = {result}")  # Devrait être 15, mais sera 16
    
    # Test 2: Email validation buggée
    email = "invalid-email"
    result = validate_email(email)
    print(f"Email '{email}' valid: {result}")  # Devrait être False
    
    # Test 3: Data processing buggée
    data = [1, "hello", 3.14, True]
    result = process_data(data)
    print(f"Processed data: {result}")  # True sera None
'''
    
    main_file.write_text(main_content, encoding='utf-8')
    
    # Fichier de configuration
    config_file = test_project_dir / "config.json"
    config_content = {
        "project_name": "V9_Test",
        "version": "1.0.0",
        "description": "Projet de test pour V9 Auto-Feeding Thread",
        "bugs_expected": 4,
        "features": ["calculation", "validation", "data_processing"]
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_content, f, indent=2, ensure_ascii=False)
    
    # Fichier README
    readme_file = test_project_dir / "README.md"
    readme_content = '''# V9 Test Project

Projet de test pour l'assistant V9 Auto-Feeding Thread.

## Fonctionnalités

- Calcul de somme (avec bug)
- Recherche de maximum
- Validation d'email (avec bug)
- Traitement de données (avec bug)

## Tests

```bash
python main.py
```

## Bugs connus

1. `calculate_sum` ajoute 1 au résultat
2. `validate_email` validation trop simple
3. `process_data` ne gère pas tous les types
4. `find_max` retourne None au lieu de lever une exception
'''
    
    readme_file.write_text(readme_content, encoding='utf-8')
    
    print(f"🔄 Projet de test créé: {test_project_dir}")
    return str(test_project_dir)

async def test_auto_feeding_thread_agent():
    """Test de l'assistant auto-feeding thread."""
    print("🕷️ Test de l'Assistant Auto-Feeding Thread V9")
    print("=" * 70)
    
    # Initialiser
    memory_engine = MemoryEngine()
    tool_registry = ToolRegistry(memory_engine)
    tool_registry.initialize()
    
    # Créer l'assistant
    assistant = AutoFeedingThreadAgent(memory_engine, tool_registry)
    
    # Créer le projet de test
    test_project_path = create_test_project()
    
    # Scénarios de test
    scenarios = [
        ("Construction et Debug Complet", f"Peux-tu analyser, construire et déboguer le projet {test_project_path} ?"),
        ("Analyse Workspace", "Peux-tu analyser la structure du workspace et identifier les patterns de développement ?"),
        ("Debug Ciblé", f"Peux-tu trouver et corriger seulement les bugs de calcul dans {test_project_path}/main.py ?")
    ]
    
    for scenario_name, message in scenarios:
        print(f"\n🔍 Test du scénario: {scenario_name}")
        print(f"📝 Message: {message}")
        print("-" * 60)
        
        # Traiter la demande
        result = await assistant.process_request(message)
        
        if result["success"]:
            print(f"✅ Succès: {result['iterations']} itérations en {result['duration']:.2f}s")
            print(f"📊 Workflow complet: {result['workflow_complete']}")
            print(f"📁 Logs: {result['summary']['log_files']['thread']}")
            
            # Afficher quelques messages du thread
            thread_stats = assistant.auto_feed_thread.get_thread_stats()
            print(f"\n🧠 Messages du thread ({thread_stats['total_messages']} total):")
            recent_messages = assistant.auto_feed_thread.get_recent_messages(3)
            for msg in recent_messages:
                print(f"  [{msg.role.upper()}] {msg.content[:100]}...")
        else:
            print(f"❌ Échec: {result['error']}")
    
    print("\n🎉 Test de l'assistant auto-feeding thread terminé !")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_auto_feeding_thread_agent()) 