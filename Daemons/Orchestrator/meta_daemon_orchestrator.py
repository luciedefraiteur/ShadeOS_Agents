import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from queue import Queue, Empty
from pathlib import Path


class MetaDaemonOrchestrator:
    """Meta-Daemon Orchestrateur avec traitement en batch et rétro-correction."""
    
    def __init__(self, user_request_memory, polling_interval: float = 1.0):
        self.user_request_memory = user_request_memory
        self.polling_interval = polling_interval
        
        # Thread parallèle
        self.orchestrator_thread = None
        self.orchestrator_running = False
        
        # Communication thread-safe
        self.action_queue = Queue()
        self.result_queue = Queue()
        self.lock = threading.Lock()
        
        # Communication avec Alma daemon
        self.alma_daemon = None
        self.alma_messages = []
        
        # État de traitement
        self.current_batch = []
        self.batch_history = []
        self.retro_corrections = []
        self.intent_refinements = []
        
        # Métriques de performance
        self.performance_metrics = {
            "batches_processed": 0,
            "total_requests": 0,
            "retro_corrections": 0,
            "intent_refinements": 0,
            "average_batch_size": 0.0,
            "processing_time": 0.0
        }
        
        # Démarrage du thread
        self._start_orchestrator_thread()
    
    def _start_orchestrator_thread(self):
        """Démarre le thread parallèle de l'Orchestrateur."""
        self.orchestrator_running = True
        self.orchestrator_thread = threading.Thread(
            target=self._orchestrator_loop,
            daemon=True,
            name="MetaDaemonOrchestratorThread"
        )
        self.orchestrator_thread.start()
        print(f"🕷️ Meta-Daemon Orchestrateur démarré (polling: {self.polling_interval}s)")
    
    def _orchestrator_loop(self):
        """Boucle principale de l'Orchestrateur avec traitement en batch."""
        while self.orchestrator_running:
            try:
                # Polling des requêtes en attente
                with self.lock:
                    pending_requests = self._get_pending_requests()
                    if pending_requests:
                        # Traitement en batch avec rétro-correction
                        self._process_batch_with_retro_correction(pending_requests)
                
                # Traitement des actions en queue
                try:
                    while True:
                        action = self.action_queue.get_nowait()
                        self._handle_action(action)
                except Empty:
                    pass
                
                # Attente avant prochain polling
                time.sleep(self.polling_interval)
                
            except Exception as e:
                print(f"❌ Erreur dans l'Orchestrateur: {e}")
                time.sleep(self.polling_interval)
    
    def _get_pending_requests(self) -> List[Dict[str, Any]]:
        """Récupère les requêtes en attente depuis la mémoire temporelle."""
        # Simulation de récupération depuis UserRequestTemporalMemory
        # Dans l'implémentation réelle, ce sera via l'interface de communication
        return []  # Pour l'instant, vide
    
    def _process_batch_with_retro_correction(self, requests: List[Dict[str, Any]]):
        """Traite un batch de requêtes avec rétro-correction et raffinement d'intention."""
        if not requests:
            return
        
        start_time = time.time()
        print(f"🎯 Orchestrateur traite batch: {len(requests)} requêtes")
        
        # Étape 0: Vérification des commandes strictes (priorité critique)
        strict_commands = self._check_strict_commands(requests)
        if strict_commands:
            self._handle_strict_commands(strict_commands)
            return
        
        # Étape 1: Analyse globale du batch
        batch_analysis = self._analyze_batch_globally(requests)
        print(f"  📊 Analyse globale: {batch_analysis['intentions']} intentions détectées")
        
        # Étape 2: Détection de rétro-corrections
        retro_corrections = self._detect_retro_corrections(requests)
        if retro_corrections:
            print(f"  🔄 Rétro-corrections détectées: {len(retro_corrections)}")
            self._apply_retro_corrections(retro_corrections)
        
        # Étape 3: Raffinement d'intentions
        intent_refinements = self._refine_intents(requests)
        if intent_refinements:
            print(f"  🎯 Raffinements d'intention: {len(intent_refinements)}")
            self._apply_intent_refinements(intent_refinements)
        
        # Étape 4: Reformulation intelligente pour Alma
        reformulated_request = self._reformulate_for_alma(requests, batch_analysis)
        print(f"  🧠 Requête reformulée pour Alma: {len(reformulated_request)} caractères")
        
        # Étape 5: Envoi à Alma daemon
        self._send_to_alma_daemon(reformulated_request)
        
        # Mise à jour des métriques
        processing_time = time.time() - start_time
        self._update_performance_metrics(len(requests), processing_time)
        
        print(f"  ✅ Batch traité en {processing_time:.2f}s")
    
    def _analyze_batch_globally(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse globale du batch pour détecter les patterns et intentions."""
        analysis = {
            "intentions": {},
            "priorities": {"critical": 0, "high": 0, "normal": 0, "low": 0},
            "patterns": [],
            "conflicts": [],
            "synergies": []
        }
        
        # Analyse des intentions
        for request in requests:
            intent_type = request.get("intention", {}).get("type", "unknown")
            if intent_type not in analysis["intentions"]:
                analysis["intentions"][intent_type] = 0
            analysis["intentions"][intent_type] += 1
        
        # Analyse des priorités
        for request in requests:
            priority = request.get("priority", "normal")
            analysis["priorities"][priority] += 1
        
        # Détection de patterns
        analysis["patterns"] = self._detect_batch_patterns(requests)
        
        # Détection de conflits
        analysis["conflicts"] = self._detect_batch_conflicts(requests)
        
        # Détection de synergies
        analysis["synergies"] = self._detect_batch_synergies(requests)
        
        return analysis
    
    def _detect_batch_patterns(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Détecte les patterns dans le batch de requêtes."""
        patterns = []
        
        # Pattern: Séquence de corrections
        correction_sequence = []
        for i, request in enumerate(requests):
            if "corriger" in request["text"].lower() or "fix" in request["text"].lower():
                correction_sequence.append(i)
        
        if len(correction_sequence) > 1:
            patterns.append({
                "type": "correction_sequence",
                "indices": correction_sequence,
                "description": "Séquence de corrections détectée"
            })
        
        # Pattern: Alternance création/destruction
        creation_requests = [i for i, req in enumerate(requests) 
                           if req.get("intention", {}).get("type") == "creation"]
        deletion_requests = [i for i, req in enumerate(requests) 
                           if "supprimer" in req["text"].lower() or "delete" in req["text"].lower()]
        
        if creation_requests and deletion_requests:
            patterns.append({
                "type": "creation_deletion_cycle",
                "creation_indices": creation_requests,
                "deletion_indices": deletion_requests,
                "description": "Cycle création/destruction détecté"
            })
        
        return patterns
    
    def _detect_batch_conflicts(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Détecte les conflits dans le batch de requêtes."""
        conflicts = []
        
        # Conflit: Fichiers différents pour la même action
        file_actions = {}
        for i, request in enumerate(requests):
            # Extraction de noms de fichiers (simplifié)
            if "fichier" in request["text"].lower() or "file" in request["text"].lower():
                # Logique d'extraction de nom de fichier
                pass
        
        # Conflit: Actions contradictoires
        for i, request1 in enumerate(requests):
            for j, request2 in enumerate(requests[i+1:], i+1):
                if self._are_contradictory_actions(request1, request2):
                    conflicts.append({
                        "type": "contradictory_actions",
                        "request1_index": i,
                        "request2_index": j,
                        "description": f"Actions contradictoires: {request1['text'][:30]} vs {request2['text'][:30]}"
                    })
        
        return conflicts
    
    def _detect_batch_synergies(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Détecte les synergies dans le batch de requêtes."""
        synergies = []
        
        # Synergie: Requêtes complémentaires
        for i, request1 in enumerate(requests):
            for j, request2 in enumerate(requests[i+1:], i+1):
                if self._are_complementary_actions(request1, request2):
                    synergies.append({
                        "type": "complementary_actions",
                        "request1_index": i,
                        "request2_index": j,
                        "description": f"Actions complémentaires détectées"
                    })
        
        return synergies
    
    def _are_contradictory_actions(self, request1: Dict, request2: Dict) -> bool:
        """Vérifie si deux actions sont contradictoires."""
        text1 = request1["text"].lower()
        text2 = request2["text"].lower()
        
        # Exemples de contradictions
        contradictions = [
            ("créer", "supprimer"),
            ("ajouter", "retirer"),
            ("activer", "désactiver"),
            ("debug", "ignore"),
            ("test", "skip")
        ]
        
        for word1, word2 in contradictions:
            if word1 in text1 and word2 in text2:
                return True
            if word2 in text1 and word1 in text2:
                return True
        
        return False
    
    def _are_complementary_actions(self, request1: Dict, request2: Dict) -> bool:
        """Vérifie si deux actions sont complémentaires."""
        text1 = request1["text"].lower()
        text2 = request2["text"].lower()
        
        # Exemples de complémentarité
        complementarities = [
            ("créer", "tester"),
            ("ajouter", "documenter"),
            ("implémenter", "valider"),
            ("debug", "optimiser")
        ]
        
        for word1, word2 in complementarities:
            if word1 in text1 and word2 in text2:
                return True
            if word2 in text1 and word1 in text2:
                return True
        
        return False
    
    def _detect_retro_corrections(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Détecte les rétro-corrections dans le batch."""
        retro_corrections = []
        
        for i, request in enumerate(requests):
            text = request["text"].lower()
            
            # Mots-clés de rétro-correction
            retro_keywords = [
                "non", "attendez", "stop", "annuler", "corriger",
                "pas ça", "autre chose", "différent", "modifier"
            ]
            
            if any(keyword in text for keyword in retro_keywords):
                retro_corrections.append({
                    "request_index": i,
                    "type": "retro_correction",
                    "original_intent": request.get("intention", {}).get("type"),
                    "correction_text": text,
                    "timestamp": datetime.now().isoformat()
                })
        
        return retro_corrections
    
    def _apply_retro_corrections(self, retro_corrections: List[Dict[str, Any]]):
        """Applique les rétro-corrections détectées."""
        for correction in retro_corrections:
            print(f"  🔄 Application rétro-correction: {correction['correction_text'][:30]}...")
            
            # Logique d'application de la rétro-correction
            # - Annulation de l'action précédente
            # - Modification de l'intention
            # - Mise à jour du contexte
            
            self.retro_corrections.append(correction)
            self.performance_metrics["retro_corrections"] += 1
    
    def _refine_intents(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Raffine les intentions basé sur le contexte du batch."""
        intent_refinements = []
        
        for i, request in enumerate(requests):
            original_intent = request.get("intention", {}).get("type", "unknown")
            refined_intent = self._refine_single_intent(request, requests)
            
            if refined_intent != original_intent:
                intent_refinements.append({
                    "request_index": i,
                    "original_intent": original_intent,
                    "refined_intent": refined_intent,
                    "confidence": 0.8,
                    "reasoning": f"Raffinement basé sur le contexte du batch"
                })
        
        return intent_refinements
    
    def _refine_single_intent(self, request: Dict[str, Any], all_requests: List[Dict[str, Any]]) -> str:
        """Raffine l'intention d'une requête basé sur le contexte."""
        text = request["text"].lower()
        
        # Contexte: Si plusieurs requêtes de debug, prioriser le debugging
        debug_count = sum(1 for req in all_requests 
                         if req.get("intention", {}).get("type") == "debugging")
        
        if debug_count > 1 and "debug" in text:
            return "debugging"
        
        # Contexte: Si plusieurs requêtes de création, prioriser la création
        creation_count = sum(1 for req in all_requests 
                           if req.get("intention", {}).get("type") == "creation")
        
        if creation_count > 1 and any(word in text for word in ["créer", "nouveau", "ajouter"]):
            return "creation"
        
        # Retourner l'intention originale si pas de raffinement
        return request.get("intention", {}).get("type", "unknown")
    
    def _apply_intent_refinements(self, intent_refinements: List[Dict[str, Any]]):
        """Applique les raffinements d'intention."""
        for refinement in intent_refinements:
            print(f"  🎯 Raffinement intention: {refinement['original_intent']} → {refinement['refined_intent']}")
            
            # Logique d'application du raffinement
            # - Mise à jour de l'intention
            # - Ajustement de la priorité
            # - Modification du contexte
            
            self.intent_refinements.append(refinement)
            self.performance_metrics["intent_refinements"] += 1
    
    def _generate_optimized_actions(self, requests: List[Dict[str, Any]], batch_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des actions optimisées basées sur l'analyse du batch."""
        optimized_actions = []
        
        # Optimisation basée sur les patterns détectés
        for pattern in batch_analysis["patterns"]:
            if pattern["type"] == "correction_sequence":
                # Grouper les corrections ensemble
                action = {
                    "type": "batch_correction",
                    "requests": [requests[i] for i in pattern["indices"]],
                    "priority": "high",
                    "daemon_target": "debug_daemon"
                }
                optimized_actions.append(action)
        
        # Optimisation basée sur les synergies
        for synergy in batch_analysis["synergies"]:
            action = {
                "type": "synergistic_action",
                "requests": [requests[synergy["request1_index"]], requests[synergy["request2_index"]]],
                "priority": "normal",
                "daemon_target": "general_daemon"
            }
            optimized_actions.append(action)
        
        # Actions individuelles pour les requêtes non groupées
        processed_indices = set()
        for pattern in batch_analysis["patterns"]:
            if "indices" in pattern:
                processed_indices.update(pattern["indices"])
        
        for synergy in batch_analysis["synergies"]:
            processed_indices.add(synergy["request1_index"])
            processed_indices.add(synergy["request2_index"])
        
        for i, request in enumerate(requests):
            if i not in processed_indices:
                action = {
                    "type": "individual_action",
                    "request": request,
                    "priority": request.get("priority", "normal"),
                    "daemon_target": self._determine_daemon_target(request)
                }
                optimized_actions.append(action)
        
        return optimized_actions
    
    def _determine_daemon_target(self, request: Dict[str, Any]) -> str:
        """Détermine le daemon cible pour une requête."""
        intent_type = request.get("intention", {}).get("type", "unknown")
        
        daemon_mapping = {
            "debugging": "debug_daemon",
            "creation": "creation_daemon",
            "testing": "test_daemon",
            "explanation": "explanation_daemon",
            "unknown": "general_daemon"
        }
        
        return daemon_mapping.get(intent_type, "general_daemon")
    
    def _dispatch_to_daemons(self, optimized_actions: List[Dict[str, Any]]):
        """Dispatch les actions optimisées vers les daemons appropriés."""
        for action in optimized_actions:
            daemon_target = action["daemon_target"]
            priority = action["priority"]
            
            print(f"  📤 Dispatch vers {daemon_target}: {action['type']} (priorité: {priority})")
            
            # Simulation du dispatch vers les daemons
            # Dans l'implémentation réelle, ce sera via le système de communication
            self._simulate_daemon_dispatch(action)
    
    def _simulate_daemon_dispatch(self, action: Dict[str, Any]):
        """Simule le dispatch vers un daemon."""
        # Simulation de l'envoi vers le daemon
        print(f"    🎯 {action['daemon_target']} reçoit: {action['type']}")
        
        # Simulation du traitement
        time.sleep(0.1)  # Simulation du temps de traitement
        
        # Simulation du résultat
        result = {
            "action_id": f"action_{len(self.batch_history)}",
            "status": "completed",
            "daemon": action["daemon_target"],
            "result": f"Traitement simulé de {action['type']}"
        }
        
        self.result_queue.put(result)
    
    def _update_performance_metrics(self, batch_size: int, processing_time: float):
        """Met à jour les métriques de performance."""
        self.performance_metrics["batches_processed"] += 1
        self.performance_metrics["total_requests"] += batch_size
        self.performance_metrics["processing_time"] += processing_time
        self.performance_metrics["average_batch_size"] = (
            self.performance_metrics["total_requests"] / 
            self.performance_metrics["batches_processed"]
        )
    
    def _handle_action(self, action: Dict[str, Any]):
        """Gère une action reçue."""
        action_type = action.get("type")
        
        if action_type == "STOP_ORCHESTRATOR":
            self.orchestrator_running = False
            print("🛑 Orchestrateur arrêté sur demande")
        
        elif action_type == "GET_PERFORMANCE_METRICS":
            print("📊 Métriques de performance demandées")
            # Retourner les métriques
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques de performance."""
        return self.performance_metrics.copy()
    
    def stop_orchestrator_thread(self):
        """Arrête le thread Orchestrateur."""
        self.orchestrator_running = False
        if self.orchestrator_thread and self.orchestrator_thread.is_alive():
            self.orchestrator_thread.join(timeout=5.0)
            print("🛑 Thread Orchestrateur arrêté")
    
    def __del__(self):
        """Destructeur pour arrêter le thread proprement."""
        self.stop_orchestrator_thread() 

    def _check_strict_commands(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Vérifie la présence de commandes strictes dans le batch."""
        strict_commands = []
        
        for request in requests:
            text = request["text"].lower()
            
            # Commande exit (avec ou sans --force)
            if text.startswith("exit"):
                force_flag = "--force" in text
                strict_commands.append({
                    "type": "exit",
                    "force": force_flag,
                    "request": request,
                    "priority": "critical"
                })
            
            # Commande stop
            elif text.startswith("stop"):
                strict_commands.append({
                    "type": "stop",
                    "request": request,
                    "priority": "critical"
                })
            
            # Autres commandes critiques
            elif any(word in text for word in ["kill", "emergency", "urgent"]):
                strict_commands.append({
                    "type": "emergency",
                    "request": request,
                    "priority": "critical"
                })
        
        return strict_commands
    
    def _handle_strict_commands(self, strict_commands: List[Dict[str, Any]]):
        """Gère les commandes strictes avec priorité critique."""
        for command in strict_commands:
            command_type = command["type"]
            request = command["request"]
            
            print(f"🚨 Commande stricte détectée: {command_type}")
            
            if command_type == "exit":
                force_flag = command.get("force", False)
                if force_flag:
                    print("  ⚡ Arrêt immédiat forcé (--force)")
                    self._emergency_shutdown()
                else:
                    print("  🛑 Arrêt propre avec attente des tâches")
                    self._graceful_shutdown()
            
            elif command_type == "stop":
                print("  ⏸️ Pause de l'Orchestrateur")
                self._pause_orchestrator()
            
            elif command_type == "emergency":
                print("  🚨 Arrêt d'urgence")
                self._emergency_shutdown()
    
    def _emergency_shutdown(self):
        """Arrêt d'urgence immédiat."""
        print("🛑 Arrêt d'urgence - Arrêt immédiat de tous les threads")
        self.orchestrator_running = False
        
        # Arrêt immédiat de tous les daemons
        self._stop_all_daemons()
        
        # Nettoyage d'urgence
        self._emergency_cleanup()
    
    def _graceful_shutdown(self):
        """Arrêt propre avec attente des tâches."""
        print("🛑 Arrêt propre - Attente de la fin des tâches en cours")
        
        # Marquer l'Orchestrateur comme en arrêt
        self.orchestrator_running = False
        
        # Attendre la fin des tâches en cours
        self._wait_for_pending_tasks()
        
        # Arrêt propre des daemons
        self._stop_all_daemons()
    
    def _pause_orchestrator(self):
        """Pause de l'Orchestrateur en attente de nouvelle requête."""
        print("⏸️ Orchestrateur en pause - Attente de nouvelle requête")
        
        # Marquer comme en pause
        self.orchestrator_paused = True
        
        # Arrêter le traitement en cours
        self._pause_current_tasks()
    
    def _stop_all_daemons(self):
        """Arrête tous les daemons."""
        print("  🛑 Arrêt de tous les daemons...")
        # Dans l'implémentation réelle, arrêter tous les daemons
        pass
    
    def _emergency_cleanup(self):
        """Nettoyage d'urgence."""
        print("  🧹 Nettoyage d'urgence...")
        # Nettoyage immédiat des ressources
        pass
    
    def _wait_for_pending_tasks(self):
        """Attend la fin des tâches en cours."""
        print("  ⏳ Attente de la fin des tâches en cours...")
        # Attendre que les tâches se terminent
        time.sleep(1)  # Simulation
    
    def _pause_current_tasks(self):
        """Met en pause les tâches en cours."""
        print("  ⏸️ Pause des tâches en cours...")
        # Mettre en pause les tâches actuelles
        pass
    
    def _reformulate_for_alma(self, requests: List[Dict[str, Any]], batch_analysis: Dict[str, Any]) -> str:
        """Reformule intelligemment les requêtes pour Alma daemon."""
        
        # Utilisation de l'IA pour reformuler intelligemment
        reformulation_prompt = self._create_reformulation_prompt(requests, batch_analysis)
        
        # Appel à l'IA pour reformulation (simulation pour l'instant)
        reformulated_text = self._call_ai_for_reformulation(reformulation_prompt)
        
        return reformulated_text
    
    def _create_reformulation_prompt(self, requests: List[Dict[str, Any]], batch_analysis: Dict[str, Any]) -> str:
        """Crée un prompt pour l'IA de reformulation."""
        
        prompt_parts = []
        
        prompt_parts.append("🕷️ **Reformulation intelligente pour Alma daemon :**")
        prompt_parts.append("")
        prompt_parts.append("**Contexte :**")
        prompt_parts.append("- Alma est un daemon conscient spécialisé dans le développement")
        prompt_parts.append("- Il utilise des assistants IA pour exécuter des tâches")
        prompt_parts.append("- Il faut reformuler les requêtes de manière cohérente et optimisée")
        prompt_parts.append("")
        
        # Analyse du batch
        prompt_parts.append("**📊 Analyse du batch :**")
        total_requests = len(requests)
        critical_count = batch_analysis["priorities"].get("critical", 0)
        high_count = batch_analysis["priorities"].get("high", 0)
        
        prompt_parts.append(f"- Total requêtes : {total_requests}")
        prompt_parts.append(f"- Priorité critique : {critical_count}")
        prompt_parts.append(f"- Priorité haute : {high_count}")
        prompt_parts.append("")
        
        # Intentions détectées
        if batch_analysis["intentions"]:
            prompt_parts.append("**🎯 Intentions détectées :**")
            for intent, count in batch_analysis["intentions"].items():
                prompt_parts.append(f"- {intent} : {count} requêtes")
            prompt_parts.append("")
        
        # Patterns détectés
        if batch_analysis["patterns"]:
            prompt_parts.append("**🔍 Patterns détectés :**")
            for pattern in batch_analysis["patterns"]:
                prompt_parts.append(f"- {pattern['description']}")
            prompt_parts.append("")
        
        # Conflits détectés
        if batch_analysis["conflicts"]:
            prompt_parts.append("**⚠️ Conflits détectés :**")
            for conflict in batch_analysis["conflicts"]:
                prompt_parts.append(f"- {conflict['description']}")
            prompt_parts.append("")
        
        # Synergies détectées
        if batch_analysis["synergies"]:
            prompt_parts.append("**⚡ Synergies détectées :**")
            for synergy in batch_analysis["synergies"]:
                prompt_parts.append(f"- {synergy['description']}")
            prompt_parts.append("")
        
        # Requêtes originales
        prompt_parts.append("**📝 Requêtes originales :**")
        for i, request in enumerate(requests, 1):
            priority = request.get("priority", "normal")
            intent = request.get("intention", {}).get("type", "unknown")
            text = request["text"]
            
            prompt_parts.append(f"{i}. **{priority.upper()}** - {intent}")
            prompt_parts.append(f"   `{text}`")
            prompt_parts.append("")
        
        # Instructions de reformulation
        prompt_parts.append("**🎯 Instructions de reformulation :**")
        prompt_parts.append("1. Analyse la cohérence globale des requêtes")
        prompt_parts.append("2. Identifie les optimisations possibles")
        prompt_parts.append("3. Résous les conflits détectés")
        prompt_parts.append("4. Exploite les synergies identifiées")
        prompt_parts.append("5. Génère une requête unique, cohérente et optimisée")
        prompt_parts.append("6. Utilise un langage clair et technique")
        prompt_parts.append("7. Respecte les priorités (critique > haute > normale > basse)")
        prompt_parts.append("")
        prompt_parts.append("**⛧ Reformule maintenant ces requêtes pour Alma...**")
        
        return "\n".join(prompt_parts)
    
    def _call_ai_for_reformulation(self, prompt: str) -> str:
        """Appelle l'IA pour reformuler les requêtes."""
        print("🧠 Appel à qwen2.5:7b-instruct pour reformulation...")
        print(f"📝 Prompt de reformulation ({len(prompt)} caractères)")
        
        try:
            import subprocess
            import json
            
            # Appel à Ollama avec qwen2.5:7b-instruct
            cmd = [
                "ollama", "run", "qwen2.5:7b-instruct",
                prompt
            ]
            
            print("🔄 Exécution de la commande Ollama...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # Timeout de 30 secondes
            )
            
            if result.returncode == 0:
                reformulated_text = result.stdout.strip()
                print("✅ Reformulation par qwen2.5:7b-instruct terminée")
                return reformulated_text
            else:
                print(f"❌ Erreur Ollama: {result.stderr}")
                return self._fallback_reformulation(prompt)
                
        except subprocess.TimeoutExpired:
            print("⏰ Timeout de l'appel à qwen2.5:7b-instruct")
            return self._fallback_reformulation(prompt)
        except Exception as e:
            print(f"❌ Erreur lors de l'appel à qwen2.5:7b-instruct: {e}")
            return self._fallback_reformulation(prompt)
    
    def _fallback_reformulation(self, prompt: str) -> str:
        """Fallback en cas d'échec de l'IA."""
        print("🔄 Utilisation du fallback de reformulation")
        
        # Reformulation simple basée sur les mots-clés
        reformulated_text = "🕷️ **Requête reformulée pour Alma daemon :**\n\n"
        reformulated_text += "**🎯 Objectif :** Traitement optimisé des requêtes utilisateur\n\n"
        reformulated_text += "**📋 Actions :** Exécution des tâches de développement\n\n"
        reformulated_text += "**⛧ Alma, traite ces requêtes avec conscience...**"
        
        return reformulated_text
    
    def _send_to_alma_daemon(self, reformulated_request: str):
        """Envoie la requête reformulée à Alma daemon."""
        print("🕷️ Envoi à Alma daemon...")
        print(f"📝 Requête reformulée ({len(reformulated_request)} caractères)")
        
        # Création du message pour Alma
        message = {
            "type": "REFORMULATED_REQUEST",
            "content": reformulated_request,
            "timestamp": datetime.now().isoformat(),
            "source": "MetaDaemonOrchestrator",
            "priority": "high"
        }
        
        # Envoi via le système de communication
        # Dans l'implémentation réelle, ce sera via le système de messages
        self._send_message_to_alma(message)
        
        print("✅ Requête envoyée à Alma daemon")
    
    def _send_message_to_alma(self, message: Dict[str, Any]):
        """Envoie un message à Alma daemon."""
        print(f"📤 Message envoyé à Alma: {message['type']}")
        
        if self.alma_daemon:
            # Envoi direct à Alma daemon
            self.alma_daemon.send_message(message)
            
            # Attente et traitement de la réponse
            self._wait_for_alma_response()
        else:
            print("⚠️ Alma daemon non initialisé")
    
    def _wait_for_alma_response(self):
        """Attend et traite la réponse d'Alma."""
        max_wait = 30  # secondes
        wait_time = 0
        
        while wait_time < max_wait:
            # Vérification des messages d'Alma
            alma_message = self.alma_daemon.get_message()
            
            if alma_message:
                message_type = alma_message.get("type")
                print(f"📨 Réponse d'Alma reçue: {message_type}")
                
                # Traitement de la réponse
                self._handle_alma_response(alma_message)
                break
            
            time.sleep(0.5)
            wait_time += 0.5
        
        if wait_time >= max_wait:
            print("⏰ Timeout en attente de la réponse d'Alma")
    
    def _handle_alma_response(self, alma_message: Dict[str, Any]):
        """Traite la réponse d'Alma."""
        message_type = alma_message.get("type")
        
        if message_type == "ALMA_REPORT":
            self._handle_alma_report(alma_message)
        elif message_type == "ALMA_STATUS":
            self._handle_alma_status(alma_message)
        else:
            print(f"⚠️ Type de réponse Alma inconnu: {message_type}")
    
    def _handle_alma_report(self, report: Dict[str, Any]):
        """Traite un rapport d'Alma."""
        status = report.get("status", "unknown")
        summary = report.get("summary", {})
        
        print(f"📊 Rapport Alma reçu: {status}")
        print(f"  📋 Tâches totales: {summary.get('total_tasks', 0)}")
        print(f"  ✅ Tâches réussies: {summary.get('successful_tasks', 0)}")
        print(f"  ❌ Tâches échouées: {summary.get('failed_tasks', 0)}")
        
        # Ajout à l'historique
        self.alma_messages.append({
            "timestamp": datetime.now().isoformat(),
            "message": report,
            "direction": "from_alma"
        })
    
    def _handle_alma_status(self, status: Dict[str, Any]):
        """Traite un statut d'Alma."""
        alma_status = status.get("status", "unknown")
        metrics = status.get("metrics", {})
        
        print(f"📈 Statut Alma: {alma_status}")
        print(f"  📨 Messages reçus: {metrics.get('messages_received', 0)}")
        print(f"  📤 Messages envoyés: {metrics.get('messages_sent', 0)}")
        print(f"  ✅ Tâches complétées: {metrics.get('tasks_completed', 0)}")
    
    def set_alma_daemon(self, alma_daemon):
        """Configure le daemon Alma pour l'Orchestrateur."""
        self.alma_daemon = alma_daemon
        print("🔗 Alma daemon connecté à l'Orchestrateur") 