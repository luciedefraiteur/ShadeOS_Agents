#!/usr/bin/env python3
"""
⛧ IntelligentCache - Cache Intelligent avec Rétroinjection ⛧

Système de cache intelligent qui utilise l'analyse LLM pour l'adaptation contextuelle
et la rétroinjection d'apprentissages, sans patterns rigides.
"""

import hashlib
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import OrderedDict

from Core.LLMProviders import LLMProvider
from .intelligent_parser import IntrospectiveMessage


@dataclass
class CacheEntry:
    """Entrée du cache intelligent"""
    response_hash: str
    original_message: IntrospectiveMessage
    context_signature: str
    effectiveness_score: float
    adaptation_history: List[Dict[str, Any]]
    last_used: float
    usage_count: int


@dataclass
class ContextSignature:
    """Signature contextuelle pour l'adaptation"""
    entity_id: str
    entity_type: str
    context_features: Dict[str, Any]
    timestamp: float


class IntelligentCache:
    """Cache intelligent avec rétroinjection d'apprentissages"""
    
    def __init__(self, provider: LLMProvider, max_cache_size: int = 1000):
        self.provider = provider
        self.max_cache_size = max_cache_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.learning_patterns: Dict[str, float] = {}  # Patterns d'apprentissage avec scores
        self.context_adaptations: Dict[str, List[Dict]] = {}  # Historique des adaptations
    
    async def get_cached_analysis(self, response: str, entity_id: str, 
                                entity_type: str, context: Optional[Dict[str, Any]] = None) -> Optional[IntrospectiveMessage]:
        """
        Récupère une analyse en cache avec adaptation contextuelle intelligente
        
        Args:
            response: Réponse à analyser
            entity_id: Identifiant de l'entité
            entity_type: Type d'entité
            context: Contexte actuel
            
        Returns:
            Message introspectif adapté ou None si pas en cache
        """
        # Génération du hash de la réponse
        response_hash = self._generate_response_hash(response)
        
        if response_hash in self.cache:
            cache_entry = self.cache[response_hash]
            
            # Mise à jour des métriques d'usage
            cache_entry.last_used = time.time()
            cache_entry.usage_count += 1
            
            # Adaptation contextuelle intelligente
            adapted_message = await self._adapt_cached_result(cache_entry, entity_id, entity_type, context)
            
            # Apprentissage de l'efficacité de l'adaptation
            await self._learn_adaptation_effectiveness(cache_entry, adapted_message, context)
            
            print(f"🧠 Cache hit: {response_hash[:8]}... (usage: {cache_entry.usage_count})")
            return adapted_message
        
        return None
    
    async def cache_analysis(self, response: str, message: IntrospectiveMessage, 
                           entity_id: str, entity_type: str, 
                           context: Optional[Dict[str, Any]] = None):
        """
        Met en cache une analyse avec signature contextuelle
        
        Args:
            response: Réponse analysée
            message: Message introspectif
            entity_id: Identifiant de l'entité
            entity_type: Type d'entité
            context: Contexte de l'analyse
        """
        response_hash = self._generate_response_hash(response)
        context_signature = self._create_context_signature(entity_id, entity_type, context)
        
        # Calcul du score d'efficacité initial
        effectiveness_score = self._calculate_effectiveness_score(message, context)
        
        cache_entry = CacheEntry(
            response_hash=response_hash,
            original_message=message,
            context_signature=context_signature,
            effectiveness_score=effectiveness_score,
            adaptation_history=[],
            last_used=time.time(),
            usage_count=1
        )
        
        # Gestion de la taille du cache
        if len(self.cache) >= self.max_cache_size:
            self._evict_least_effective_entry()
        
        self.cache[response_hash] = cache_entry
        print(f"💾 Cached: {response_hash[:8]}... (effectiveness: {effectiveness_score:.2f})")
    
    async def _adapt_cached_result(self, cache_entry: CacheEntry, entity_id: str, 
                                 entity_type: str, current_context: Optional[Dict[str, Any]]) -> IntrospectiveMessage:
        """
        Adapte un résultat en cache au contexte actuel via analyse LLM
        
        Args:
            cache_entry: Entrée du cache
            entity_id: Identifiant de l'entité actuelle
            entity_type: Type d'entité actuel
            current_context: Contexte actuel
            
        Returns:
            Message introspectif adapté
        """
        # Analyse des différences contextuelles via LLM
        context_diff_analysis = await self._analyze_context_differences(
            cache_entry.original_message.context, current_context, entity_id, entity_type
        )
        
        # Adaptation intelligente basée sur l'analyse LLM
        adapted_message = await self._perform_intelligent_adaptation(
            cache_entry.original_message, context_diff_analysis, current_context
        )
        
        # Enregistrement de l'adaptation
        adaptation_record = {
            "timestamp": time.time(),
            "context_diff_analysis": context_diff_analysis,
            "adaptation_applied": True,
            "original_effectiveness": cache_entry.effectiveness_score
        }
        cache_entry.adaptation_history.append(adaptation_record)
        
        return adapted_message
    
    async def _analyze_context_differences(self, original_context: Optional[Dict[str, Any]], 
                                         current_context: Optional[Dict[str, Any]], 
                                         entity_id: str, entity_type: str) -> Dict[str, Any]:
        """
        Analyse les différences contextuelles via LLM avec injection de métriques
        
        Args:
            original_context: Contexte original
            current_context: Contexte actuel
            entity_id: Identifiant de l'entité
            entity_type: Type d'entité
            
        Returns:
            Analyse des différences contextuelles avec métriques intégrées
        """
        # Injection dynamique de métriques dans le prompt principal
        metrics_injection = """
ÉVALUATION MÉTRIQUES (à inclure dans la réponse) :
- Complexité_contextuelle: score 0-1 basé sur le nombre de différences
- Impact_adaptation: score 0-1 basé sur l'impact des différences
- Confiance_analyse: score 0-1 basé sur la clarté des différences
"""
        
        prompt = f"""
Analyse les différences contextuelles entre deux contextes pour l'entité {entity_id} ({entity_type}).

Contexte original:
{json.dumps(original_context, ensure_ascii=False, indent=2) if original_context else "Aucun contexte"}

Contexte actuel:
{json.dumps(current_context, ensure_ascii=False, indent=2) if current_context else "Aucun contexte"}

TÂCHES À EFFECTUER :
1. Identifie les différences significatives qui pourraient affecter l'analyse introspective
2. Évalue la complexité contextuelle et l'impact d'adaptation
3. Calcule la confiance dans ton analyse

{metrics_injection}

Retourne un JSON avec cette structure:
{{
    "significant_differences": [
        {{
            "aspect": "description de l'aspect",
            "original_value": "valeur originale",
            "current_value": "valeur actuelle",
            "impact_level": "high|medium|low"
        }}
    ],
    "adaptation_needed": true/false,
    "adaptation_type": "description du type d'adaptation nécessaire",
    "metrics": {{
        "complexity_contextuelle": 0.75,
        "impact_adaptation": 0.60,
        "confiance_analyse": 0.85
    }}
}}
"""
        
        try:
            response = await self.provider.generate_response(prompt, temperature=0.1)
            analysis = json.loads(response.content)
            return analysis
        except Exception as e:
            print(f"⚠️ Erreur analyse contextuelle: {e}")
            return {
                "significant_differences": [],
                "adaptation_needed": False,
                "adaptation_type": "none",
                "metrics": {
                    "complexity_contextuelle": 0.0,
                    "impact_adaptation": 0.0,
                    "confiance_analyse": 0.0
                }
            }
    
    async def _perform_intelligent_adaptation(self, original_message: IntrospectiveMessage, 
                                            context_diff_analysis: Dict[str, Any], 
                                            current_context: Optional[Dict[str, Any]]) -> IntrospectiveMessage:
        """
        Effectue l'adaptation intelligente via LLM avec évaluation intégrée
        
        Args:
            original_message: Message original
            context_diff_analysis: Analyse des différences contextuelles
            current_context: Contexte actuel
            
        Returns:
            Message adapté avec métriques d'adaptation
        """
        if not context_diff_analysis.get("adaptation_needed", False):
            return original_message
        
        # Injection de métriques d'adaptation dans le prompt
        adaptation_metrics = """
ÉVALUATION D'ADAPTATION (à inclure dans la réponse) :
- Qualité_adaptation: score 0-1 basé sur la cohérence de l'adaptation
- Fidélité_original: score 0-1 basé sur la préservation du sens original
- Pertinence_contexte: score 0-1 basé sur l'adéquation au nouveau contexte
"""
        
        prompt = f"""
TÂCHES À EFFECTUER :
1. Adapte ce message introspectif au nouveau contexte
2. Évalue la qualité de l'adaptation effectuée
3. Calcule les métriques de fidélité et pertinence

Message original:
{json.dumps(original_message.to_dict(), ensure_ascii=False, indent=2)}

Analyse des différences contextuelles:
{json.dumps(context_diff_analysis, ensure_ascii=False, indent=2)}

Contexte actuel:
{json.dumps(current_context, ensure_ascii=False, indent=2) if current_context else "Aucun contexte"}

{adaptation_metrics}

Adapte le message en conservant sa structure mais en ajustant le contenu selon les différences contextuelles.
Retourne le message adapté avec les métriques d'évaluation au format JSON.
"""
        
        try:
            response = await self.provider.generate_response(prompt, temperature=0.2)
            adapted_data = json.loads(response.content)
            
            # Reconstruction du message adapté
            adapted_message = IntrospectiveMessage(
                entity_id=original_message.entity_id,
                entity_type=original_message.entity_type,
                timestamp=time.time(),
                original_response=original_message.original_response,
                thoughts=adapted_data.get("thoughts", original_message.thoughts),
                actions=adapted_data.get("actions", original_message.actions),
                observations=adapted_data.get("observations", original_message.observations),
                decisions=adapted_data.get("decisions", original_message.decisions),
                overall_confidence=adapted_data.get("overall_confidence", original_message.overall_confidence),
                context=current_context
            )
            
            # Stockage des métriques d'adaptation dans les métadonnées
            if "adaptation_metrics" in adapted_data:
                adapted_message.metadata["adaptation_metrics"] = adapted_data["adaptation_metrics"]
            
            return adapted_message
            
        except Exception as e:
            print(f"⚠️ Erreur adaptation intelligente: {e}")
            return original_message
    
    def _calculate_effectiveness_score(self, message: IntrospectiveMessage, 
                                     context: Optional[Dict[str, Any]]) -> float:
        """
        Calcule un score d'efficacité simple basé sur le contenu
        
        Args:
            message: Message introspectif
            context: Contexte de l'analyse
            
        Returns:
            Score d'efficacité entre 0.0 et 1.0
        """
        # Score simple basé sur la présence d'éléments introspectifs
        total_elements = len(message.thoughts) + len(message.actions) + len(message.observations) + len(message.decisions)
        
        if total_elements == 0:
            return 0.1  # Score très bas si aucun élément détecté
        
        # Score basé sur la confiance moyenne des éléments
        all_elements = message.thoughts + message.actions + message.observations + message.decisions
        if all_elements:
            avg_confidence = sum(elem.confidence for elem in all_elements) / len(all_elements)
            return min(avg_confidence, 0.9)  # Cap à 0.9 pour éviter les scores parfaits
        
        return 0.5  # Score par défaut
    
    def _learn_adaptation_effectiveness(self, cache_entry: CacheEntry, 
                                      adapted_message: IntrospectiveMessage, 
                                      context: Optional[Dict[str, Any]]):
        """
        Apprend de l'efficacité de l'adaptation (version simplifiée)
        
        Args:
            cache_entry: Entrée du cache
            adapted_message: Message adapté
            context: Contexte de l'adaptation
        """
        # Calcul de l'efficacité de l'adaptation
        adaptation_effectiveness = self._calculate_effectiveness_score(adapted_message, context)
        
        # Mise à jour du score d'efficacité
        cache_entry.effectiveness_score = (cache_entry.effectiveness_score + adaptation_effectiveness) / 2
    
    async def _learn_successful_adaptation_pattern(self, cache_entry: CacheEntry, context: Optional[Dict[str, Any]]):
        """
        Apprend des patterns d'adaptation réussis
        
        Args:
            cache_entry: Entrée du cache
            context: Contexte de l'adaptation réussie
        """
        # Analyse LLM du pattern de succès
        prompt = f"""
Analyse ce pattern d'adaptation réussie pour en extraire les éléments clés.

Entrée du cache:
- Hash: {cache_entry.response_hash[:8]}...
- Score d'efficacité: {cache_entry.effectiveness_score:.2f}
- Usage count: {cache_entry.usage_count}

Contexte de l'adaptation réussie:
{json.dumps(context, ensure_ascii=False, indent=2) if context else "Aucun contexte"}

Historique des adaptations:
{json.dumps(cache_entry.adaptation_history, ensure_ascii=False, indent=2)}

Identifie les éléments clés qui ont contribué au succès de cette adaptation.
Retourne un JSON avec les insights:
{{
    "success_factors": ["facteur1", "facteur2"],
    "adaptation_quality": "description de la qualité",
    "reusability_score": 0.85
}}
"""
        
        try:
            response = await self.provider.generate_response(prompt, temperature=0.1)
            insights = json.loads(response.content)
            
            # Stockage des insights pour utilisation future
            pattern_key = f"{cache_entry.entity_id}_{cache_entry.entity_type}"
            if pattern_key not in self.learning_patterns:
                self.learning_patterns[pattern_key] = []
            
            self.learning_patterns[pattern_key].append({
                "insights": insights,
                "timestamp": time.time(),
                "effectiveness": cache_entry.effectiveness_score
            })
            
        except Exception as e:
            print(f"⚠️ Erreur apprentissage pattern: {e}")
    
    def _generate_response_hash(self, response: str) -> str:
        """Génère un hash de la réponse"""
        return hashlib.sha256(response.encode('utf-8')).hexdigest()
    
    def _create_context_signature(self, entity_id: str, entity_type: str, 
                                context: Optional[Dict[str, Any]]) -> str:
        """Crée une signature contextuelle"""
        signature_data = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "context": context
        }
        return hashlib.sha256(json.dumps(signature_data, sort_keys=True).encode('utf-8')).hexdigest()
    
    def _evict_least_effective_entry(self):
        """Évince l'entrée la moins efficace du cache"""
        if not self.cache:
            return
        
        # Trouve l'entrée avec le score d'efficacité le plus bas
        least_effective = min(self.cache.values(), key=lambda x: x.effectiveness_score)
        
        # Évince l'entrée
        del self.cache[least_effective.response_hash]
        print(f"🗑️ Évincé du cache: {least_effective.response_hash[:8]}... (effectiveness: {least_effective.effectiveness_score:.2f})")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache"""
        if not self.cache:
            return {"error": "Cache vide"}
        
        total_entries = len(self.cache)
        avg_effectiveness = sum(entry.effectiveness_score for entry in self.cache.values()) / total_entries
        total_usage = sum(entry.usage_count for entry in self.cache.values())
        
        return {
            "total_entries": total_entries,
            "average_effectiveness": avg_effectiveness,
            "total_usage": total_usage,
            "learning_patterns_count": len(self.learning_patterns),
            "cache_hit_rate": "N/A"  # À implémenter avec tracking des hits/misses
        } 