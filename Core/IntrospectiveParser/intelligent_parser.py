#!/usr/bin/env python3
"""
⛧ IntelligentIntrospectiveParser - Parser Sémantique Intelligent ⛧

Parser intelligent basé sur l'analyse sémantique pour extraire l'introspection
des réponses d'IA, remplaçant les patterns regex rigides par une compréhension
réelle du contenu.
"""

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from Core.LLMProviders import LLMProvider


@dataclass
class IntrospectiveElement:
    """Élément introspectif extrait"""
    type: str  # "thought", "action", "observation", "decision"
    content: str
    confidence: float
    context: Optional[str] = None


@dataclass
class IntrospectiveMessage:
    """Message introspectif complet"""
    entity_id: str
    entity_type: str
    timestamp: float
    original_response: str
    thoughts: List[IntrospectiveElement]
    actions: List[IntrospectiveElement]
    observations: List[IntrospectiveElement]
    decisions: List[IntrospectiveElement]
    overall_confidence: float
    context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation"""
        return asdict(self)
    
    def get_summary(self) -> str:
        """Génère un résumé du message introspectif"""
        summary_parts = []
        
        if self.thoughts:
            thoughts_text = "; ".join([t.content for t in self.thoughts])
            summary_parts.append(f"Pensées: {thoughts_text}")
        
        if self.actions:
            actions_text = "; ".join([a.content for a in self.actions])
            summary_parts.append(f"Actions: {actions_text}")
        
        if self.observations:
            observations_text = "; ".join([o.content for o in self.observations])
            summary_parts.append(f"Observations: {observations_text}")
        
        if self.decisions:
            decisions_text = "; ".join([d.content for d in self.decisions])
            summary_parts.append(f"Décisions: {decisions_text}")
        
        return " | ".join(summary_parts) if summary_parts else "Aucun élément introspectif détecté"


class IntelligentIntrospectiveParser:
    """Parser intelligent basé sur l'analyse sémantique"""
    
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.analysis_prompt = self._create_analysis_prompt()
    
    def _create_analysis_prompt(self) -> str:
        """Crée le prompt d'analyse sémantique"""
        return """
Tu es un analyseur sémantique spécialisé dans l'extraction d'éléments introspectifs.
Analyse la réponse d'IA fournie et identifie les éléments introspectifs.

Types d'éléments à identifier :
1. **PENSÉES** : Réflexions, doutes, analyses, raisonnements internes
2. **ACTIONS** : Actions décidées, entreprises ou planifiées
3. **OBSERVATIONS** : Constatations, découvertes, informations obtenues
4. **DÉCISIONS** : Choix faits, conclusions tirées, directions prises

Critères d'identification :
- Une PENSÉE exprime un raisonnement interne, une réflexion
- Une ACTION décrit ce qui va être fait ou ce qui est en cours
- Une OBSERVATION constate un fait, un résultat, une information
- Une DÉCISION représente un choix, une conclusion, une direction

Retourne UNIQUEMENT un JSON valide avec cette structure :
{
    "thoughts": [
        {"content": "texte de la pensée", "confidence": 0.85}
    ],
    "actions": [
        {"content": "texte de l'action", "confidence": 0.90}
    ],
    "observations": [
        {"content": "texte de l'observation", "confidence": 0.75}
    ],
    "decisions": [
        {"content": "texte de la décision", "confidence": 0.80}
    ],
    "overall_confidence": 0.82
}

Si aucun élément d'un type n'est trouvé, utilise un tableau vide.
La confidence doit être entre 0.0 et 1.0.
"""
    
    async def parse_response(self, response: str, entity_id: str = "unknown", 
                           entity_type: str = "unknown", 
                           context: Optional[Dict[str, Any]] = None) -> IntrospectiveMessage:
        """
        Analyse sémantique d'une réponse pour extraire l'introspection
        
        Args:
            response: Réponse de l'IA à analyser
            entity_id: Identifiant de l'entité (daemon, assistant, etc.)
            entity_type: Type d'entité ("daemon", "assistant", "orchestrator")
            context: Contexte supplémentaire pour l'analyse
            
        Returns:
            IntrospectiveMessage avec tous les éléments extraits
        """
        try:
            # Construction du prompt complet
            full_prompt = f"{self.analysis_prompt}\n\nRéponse à analyser :\n{response}"
            
            if context:
                context_str = json.dumps(context, ensure_ascii=False, indent=2)
                full_prompt += f"\n\nContexte :\n{context_str}"
            
            # Appel au LLM pour l'analyse
            llm_response = await self.provider.generate_response(
                full_prompt,
                temperature=0.1,  # Faible température pour la cohérence
                max_tokens=1000
            )
            
            # Parsing de la réponse JSON
            analysis_result = self._parse_json_response(llm_response.content)
            
            # Construction du message introspectif
            return IntrospectiveMessage(
                entity_id=entity_id,
                entity_type=entity_type,
                timestamp=time.time(),
                original_response=response,
                thoughts=self._create_elements(analysis_result.get("thoughts", []), "thought"),
                actions=self._create_elements(analysis_result.get("actions", []), "action"),
                observations=self._create_elements(analysis_result.get("observations", []), "observation"),
                decisions=self._create_elements(analysis_result.get("decisions", []), "decision"),
                overall_confidence=analysis_result.get("overall_confidence", 0.5),
                context=context
            )
            
        except Exception as e:
            # Fallback en cas d'erreur
            print(f"⚠️ Erreur dans l'analyse introspective: {e}")
            return self._create_fallback_message(response, entity_id, entity_type, context)
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse la réponse JSON du LLM"""
        try:
            # Nettoyage de la réponse
            cleaned_response = response.strip()
            
            # Recherche du JSON dans la réponse
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = cleaned_response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("Aucun JSON trouvé dans la réponse")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ Erreur parsing JSON: {e}")
            print(f"Réponse reçue: {response}")
            return self._create_default_analysis()
    
    def _create_elements(self, elements_data: List[Dict], element_type: str) -> List[IntrospectiveElement]:
        """Crée les éléments introspectifs à partir des données"""
        elements = []
        for elem_data in elements_data:
            if isinstance(elem_data, dict):
                content = elem_data.get("content", "")
                confidence = elem_data.get("confidence", 0.5)
                elements.append(IntrospectiveElement(
                    type=element_type,
                    content=content,
                    confidence=confidence
                ))
        return elements
    
    def _create_default_analysis(self) -> Dict[str, Any]:
        """Crée une analyse par défaut en cas d'erreur"""
        return {
            "thoughts": [],
            "actions": [],
            "observations": [],
            "decisions": [],
            "overall_confidence": 0.0
        }
    
    def _create_fallback_message(self, response: str, entity_id: str, 
                               entity_type: str, context: Optional[Dict[str, Any]]) -> IntrospectiveMessage:
        """Crée un message de fallback en cas d'erreur"""
        return IntrospectiveMessage(
            entity_id=entity_id,
            entity_type=entity_type,
            timestamp=time.time(),
            original_response=response,
            thoughts=[],
            actions=[],
            observations=[],
            decisions=[],
            overall_confidence=0.0,
            context=context
        ) 