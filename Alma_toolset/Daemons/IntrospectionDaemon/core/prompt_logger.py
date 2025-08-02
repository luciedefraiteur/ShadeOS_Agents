#!/usr/bin/env python3
"""
📝 Prompt Logger - IntrospectionDaemon ⛧

Système de logging complet pour tracer tous les prompts envoyés et reçus.
Capture, analyse et stocke automatiquement l'historique des interactions.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

@dataclass
class PromptLogEntry:
    """Entrée de log pour un prompt."""
    
    timestamp: datetime
    prompt_id: str
    prompt_type: str
    input_prompt: str
    output_response: str
    context_data: Dict[str, Any]
    effectiveness_score: float
    execution_time: float
    metadata: Dict[str, Any]
    error_message: Optional[str] = None

@dataclass
class PromptSession:
    """Session de prompts avec métadonnées."""
    
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_prompts: int
    successful_prompts: int
    failed_prompts: int
    average_effectiveness: float
    session_type: str
    prompts: List[PromptLogEntry]

class PromptLogger:
    """Logger complet pour les prompts d'introspection."""
    
    def __init__(self, log_directory: str = "logs"):
        """
        Initialise le logger de prompts.
        
        Args:
            log_directory: Répertoire de stockage des logs
        """
        self.log_directory = log_directory
        self.current_session = None
        self.auto_save = True
        self.detailed_logging = True
        
        # Configuration du logging
        self.config = {
            "max_prompt_length": 10000,  # Limite pour éviter les logs trop volumineux
            "save_context_data": True,
            "save_responses": True,
            "compress_old_logs": True,
            "retention_days": 30
        }
        
        # Création du répertoire de logs
        self._ensure_log_directory()
        
        # Initialisation de la session
        self._start_new_session("introspection_daemon")
    
    def _ensure_log_directory(self):
        """S'assure que le répertoire de logs existe."""
        
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
            print(f"📁 Répertoire de logs créé : {self.log_directory}")
    
    def _start_new_session(self, session_type: str = "default"):
        """Démarre une nouvelle session de logging."""
        
        session_id = f"{session_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = PromptSession(
            session_id=session_id,
            start_time=datetime.now(),
            end_time=None,
            total_prompts=0,
            successful_prompts=0,
            failed_prompts=0,
            average_effectiveness=0.0,
            session_type=session_type,
            prompts=[]
        )
        
        print(f"📝 Nouvelle session de logging : {session_id}")
    
    def log_prompt_interaction(self, 
                             prompt_type: str,
                             input_prompt: str,
                             output_response: str,
                             context_data: Dict[str, Any] = None,
                             effectiveness_score: float = 0.0,
                             execution_time: float = 0.0,
                             metadata: Dict[str, Any] = None,
                             error_message: str = None) -> str:
        """
        Log une interaction de prompt complète.
        
        Args:
            prompt_type: Type de prompt (introspection, generation, injection, etc.)
            input_prompt: Prompt envoyé
            output_response: Réponse reçue
            context_data: Données contextuelles
            effectiveness_score: Score d'efficacité
            execution_time: Temps d'exécution
            metadata: Métadonnées additionnelles
            error_message: Message d'erreur si applicable
            
        Returns:
            str: ID unique du log
        """
        
        # Génération d'un ID unique
        prompt_id = self._generate_prompt_id(input_prompt, prompt_type)
        
        # Troncature si nécessaire
        truncated_prompt = self._truncate_if_needed(input_prompt)
        truncated_response = self._truncate_if_needed(output_response)
        
        # Création de l'entrée de log
        log_entry = PromptLogEntry(
            timestamp=datetime.now(),
            prompt_id=prompt_id,
            prompt_type=prompt_type,
            input_prompt=truncated_prompt,
            output_response=truncated_response,
            context_data=context_data or {},
            effectiveness_score=effectiveness_score,
            execution_time=execution_time,
            metadata=metadata or {},
            error_message=error_message
        )
        
        # Ajout à la session courante
        if self.current_session:
            self.current_session.prompts.append(log_entry)
            self.current_session.total_prompts += 1
            
            if error_message:
                self.current_session.failed_prompts += 1
            else:
                self.current_session.successful_prompts += 1
            
            # Mise à jour de l'efficacité moyenne
            self._update_session_effectiveness()
        
        # Sauvegarde automatique si activée
        if self.auto_save:
            self._save_current_log_entry(log_entry)
        
        # Log console détaillé
        if self.detailed_logging:
            self._print_detailed_log(log_entry)
        
        return prompt_id
    
    def log_prompt_generation(self, 
                            prompt_type: str,
                            generated_prompt: str,
                            template_used: str = None,
                            injection_data: Dict = None,
                            generation_time: float = 0.0) -> str:
        """
        Log spécialisé pour la génération de prompts.
        
        Args:
            prompt_type: Type de prompt généré
            generated_prompt: Prompt généré
            template_used: Template utilisé
            injection_data: Données injectées
            generation_time: Temps de génération
            
        Returns:
            str: ID du log
        """
        
        metadata = {
            "operation": "prompt_generation",
            "template_used": template_used,
            "injection_points": list(injection_data.keys()) if injection_data else [],
            "prompt_length": len(generated_prompt)
        }
        
        return self.log_prompt_interaction(
            prompt_type=f"generation_{prompt_type}",
            input_prompt=f"GENERATE: {prompt_type}",
            output_response=generated_prompt,
            context_data=injection_data,
            execution_time=generation_time,
            metadata=metadata
        )
    
    def log_context_injection(self,
                            base_prompt: str,
                            enriched_prompt: str,
                            injection_type: str,
                            injected_data: Dict,
                            injection_time: float = 0.0) -> str:
        """
        Log spécialisé pour l'injection contextuelle.
        
        Args:
            base_prompt: Prompt de base
            enriched_prompt: Prompt enrichi
            injection_type: Type d'injection
            injected_data: Données injectées
            injection_time: Temps d'injection
            
        Returns:
            str: ID du log
        """
        
        enrichment_ratio = len(enriched_prompt) / len(base_prompt) if base_prompt else 0
        
        metadata = {
            "operation": "context_injection",
            "injection_type": injection_type,
            "enrichment_ratio": enrichment_ratio,
            "base_length": len(base_prompt),
            "enriched_length": len(enriched_prompt),
            "injection_success": "::INJECT_" not in enriched_prompt
        }
        
        return self.log_prompt_interaction(
            prompt_type=f"injection_{injection_type}",
            input_prompt=base_prompt,
            output_response=enriched_prompt,
            context_data=injected_data,
            execution_time=injection_time,
            metadata=metadata
        )
    
    def log_introspection_result(self,
                               introspection_prompt: str,
                               analysis_result: Dict,
                               effectiveness_score: float,
                               analysis_time: float = 0.0) -> str:
        """
        Log spécialisé pour les résultats d'introspection.
        
        Args:
            introspection_prompt: Prompt d'introspection
            analysis_result: Résultat de l'analyse
            effectiveness_score: Score d'efficacité
            analysis_time: Temps d'analyse
            
        Returns:
            str: ID du log
        """
        
        metadata = {
            "operation": "introspection_analysis",
            "components_analyzed": len(analysis_result.get("components_analyzed", {})),
            "capabilities_discovered": len(analysis_result.get("capabilities_discovered", {})),
            "improvement_suggestions": len(analysis_result.get("improvement_suggestions", [])),
            "analysis_type": analysis_result.get("analysis_type", "unknown")
        }
        
        return self.log_prompt_interaction(
            prompt_type="introspection_analysis",
            input_prompt=introspection_prompt,
            output_response=json.dumps(analysis_result, indent=2),
            effectiveness_score=effectiveness_score,
            execution_time=analysis_time,
            metadata=metadata
        )
    
    def end_session(self):
        """Termine la session courante et sauvegarde."""
        
        if self.current_session:
            self.current_session.end_time = datetime.now()
            self._save_complete_session()
            
            print(f"📝 Session terminée : {self.current_session.session_id}")
            print(f"   Total prompts : {self.current_session.total_prompts}")
            print(f"   Succès : {self.current_session.successful_prompts}")
            print(f"   Échecs : {self.current_session.failed_prompts}")
            print(f"   Efficacité moyenne : {self.current_session.average_effectiveness:.2f}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de la session courante."""
        
        if not self.current_session:
            return {}
        
        return {
            "session_id": self.current_session.session_id,
            "session_type": self.current_session.session_type,
            "duration": (datetime.now() - self.current_session.start_time).total_seconds(),
            "total_prompts": self.current_session.total_prompts,
            "successful_prompts": self.current_session.successful_prompts,
            "failed_prompts": self.current_session.failed_prompts,
            "success_rate": self.current_session.successful_prompts / max(self.current_session.total_prompts, 1),
            "average_effectiveness": self.current_session.average_effectiveness
        }
    
    def get_prompt_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retourne l'historique des prompts."""
        
        if not self.current_session:
            return []
        
        recent_prompts = self.current_session.prompts[-limit:]
        
        return [
            {
                "prompt_id": p.prompt_id,
                "timestamp": p.timestamp.isoformat(),
                "prompt_type": p.prompt_type,
                "effectiveness_score": p.effectiveness_score,
                "execution_time": p.execution_time,
                "has_error": p.error_message is not None,
                "prompt_preview": p.input_prompt[:100] + "..." if len(p.input_prompt) > 100 else p.input_prompt
            }
            for p in recent_prompts
        ]
    
    def _generate_prompt_id(self, prompt: str, prompt_type: str) -> str:
        """Génère un ID unique pour un prompt."""
        
        content = f"{prompt_type}_{prompt}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _truncate_if_needed(self, text: str) -> str:
        """Tronque le texte si nécessaire."""
        
        if len(text) <= self.config["max_prompt_length"]:
            return text
        
        truncated = text[:self.config["max_prompt_length"]]
        return truncated + f"\n\n[TRUNCATED - Original length: {len(text)} chars]"
    
    def _update_session_effectiveness(self):
        """Met à jour l'efficacité moyenne de la session."""
        
        if not self.current_session or not self.current_session.prompts:
            return
        
        total_effectiveness = sum(p.effectiveness_score for p in self.current_session.prompts)
        self.current_session.average_effectiveness = total_effectiveness / len(self.current_session.prompts)
    
    def _save_current_log_entry(self, log_entry: PromptLogEntry):
        """Sauvegarde une entrée de log individuelle."""
        
        timestamp = log_entry.timestamp.strftime("%Y%m%d")
        log_file = os.path.join(self.log_directory, f"prompts_{timestamp}.jsonl")
        
        # Conversion en dictionnaire
        entry_dict = asdict(log_entry)
        entry_dict["timestamp"] = log_entry.timestamp.isoformat()
        
        # Ajout au fichier JSONL
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry_dict, ensure_ascii=False) + "\n")
    
    def _save_complete_session(self):
        """Sauvegarde la session complète."""
        
        if not self.current_session:
            return
        
        session_file = os.path.join(
            self.log_directory, 
            f"session_{self.current_session.session_id}.json"
        )
        
        # Conversion en dictionnaire
        session_dict = asdict(self.current_session)
        session_dict["start_time"] = self.current_session.start_time.isoformat()
        if self.current_session.end_time:
            session_dict["end_time"] = self.current_session.end_time.isoformat()
        
        # Conversion des prompts
        session_dict["prompts"] = [
            {
                **asdict(p),
                "timestamp": p.timestamp.isoformat()
            }
            for p in self.current_session.prompts
        ]
        
        # Sauvegarde
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_dict, f, indent=2, ensure_ascii=False)
    
    def _print_detailed_log(self, log_entry: PromptLogEntry):
        """Affiche un log détaillé en console."""
        
        print(f"\n📝 LOG PROMPT [{log_entry.prompt_id}]")
        print(f"   Type: {log_entry.prompt_type}")
        print(f"   Timestamp: {log_entry.timestamp.strftime('%H:%M:%S')}")
        print(f"   Efficacité: {log_entry.effectiveness_score:.2f}")
        print(f"   Temps: {log_entry.execution_time:.3f}s")
        
        if log_entry.error_message:
            print(f"   ❌ Erreur: {log_entry.error_message}")
        
        # Aperçu du prompt
        prompt_preview = log_entry.input_prompt[:200]
        if len(log_entry.input_prompt) > 200:
            prompt_preview += "..."
        print(f"   📤 Prompt: {prompt_preview}")
        
        # Aperçu de la réponse
        response_preview = log_entry.output_response[:200]
        if len(log_entry.output_response) > 200:
            response_preview += "..."
        print(f"   📥 Réponse: {response_preview}")

# Instance globale du logger
_global_logger = None

def get_prompt_logger() -> PromptLogger:
    """Retourne l'instance globale du logger."""
    
    global _global_logger
    if _global_logger is None:
        _global_logger = PromptLogger()
    
    return _global_logger

def log_prompt(prompt_type: str, input_prompt: str, output_response: str, **kwargs) -> str:
    """Fonction utilitaire pour logger un prompt."""
    
    logger = get_prompt_logger()
    return logger.log_prompt_interaction(
        prompt_type=prompt_type,
        input_prompt=input_prompt,
        output_response=output_response,
        **kwargs
    )

if __name__ == "__main__":
    # Test du logger
    logger = PromptLogger()
    
    # Test de logging
    prompt_id = logger.log_prompt_interaction(
        prompt_type="test",
        input_prompt="Test prompt",
        output_response="Test response",
        effectiveness_score=0.8,
        execution_time=0.5
    )
    
    print(f"✅ Test logging réussi : {prompt_id}")
    
    # Résumé de session
    summary = logger.get_session_summary()
    print(f"📊 Résumé session : {summary}")
    
    # Fin de session
    logger.end_session()
