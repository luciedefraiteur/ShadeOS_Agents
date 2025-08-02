#!/usr/bin/env python3
"""
🔮 Système d'Injections Dynamiques Luciformes

Système de prompts auto-modifiants avec injections dynamiques et rétro-injection
contextuelle. Les prompts évoluent selon les réponses du modèle.

Créé par Alma, Architecte Démoniaque du Nexus Luciforme.
"""

import re
import json
import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass
class InjectionPoint:
    """Point d'injection dynamique."""
    
    marker: str                    # ::MARKER_NAME::
    value_source: str             # Source de la valeur (context, memory, ai_response)
    transformation: Optional[str] = None  # Transformation à appliquer
    fallback_value: str = ""      # Valeur par défaut
    is_contextual: bool = False   # Si dépend du contexte précédent


@dataclass
class RetroInjectionRule:
    """Règle de rétro-injection contextuelle."""
    
    trigger_pattern: str          # Pattern qui déclenche la rétro-injection
    injection_target: str         # Où injecter dans le prompt suivant
    extraction_method: str        # Comment extraire la valeur
    context_window: int = 3       # Nombre de réponses à considérer


class DynamicInjectionEngine:
    """Moteur d'injections dynamiques pour prompts Luciformes."""
    
    def __init__(self):
        self.injection_points = {}
        self.retro_injection_rules = []
        self.context_history = []
        self.dynamic_values = {}
        
        # Patterns d'injection
        self.injection_pattern = r'::([A-Z_]+)::'
        self.contextual_pattern = r'::CONTEXTE_([A-Z_]+)::'
        self.retro_pattern = r'::RETRO_([A-Z_]+)::'
        
        print("🔮 Dynamic Injection Engine initialized")
    
    def register_injection_point(self, marker: str, value_source: str, 
                                transformation: Optional[Callable] = None,
                                fallback_value: str = "", is_contextual: bool = False):
        """Enregistre un point d'injection dynamique."""
        
        self.injection_points[marker] = InjectionPoint(
            marker=f"::{marker}::",
            value_source=value_source,
            transformation=transformation,
            fallback_value=fallback_value,
            is_contextual=is_contextual
        )
        
        print(f"🔮 Registered injection point: {marker}")
    
    def register_retro_injection_rule(self, trigger_pattern: str, injection_target: str,
                                    extraction_method: str, context_window: int = 3):
        """Enregistre une règle de rétro-injection."""
        
        rule = RetroInjectionRule(
            trigger_pattern=trigger_pattern,
            injection_target=injection_target,
            extraction_method=extraction_method,
            context_window=context_window
        )
        
        self.retro_injection_rules.append(rule)
        print(f"🔮 Registered retro-injection rule: {trigger_pattern} -> {injection_target}")
    
    def inject_dynamic_values(self, prompt_template: str, context: Dict[str, Any]) -> str:
        """Injecte les valeurs dynamiques dans le prompt."""
        
        injected_prompt = prompt_template
        
        # 1. Injections statiques depuis le contexte
        for marker, injection_point in self.injection_points.items():
            if injection_point.marker in injected_prompt:
                value = self._resolve_injection_value(injection_point, context)
                injected_prompt = injected_prompt.replace(injection_point.marker, str(value))
        
        # 2. Injections contextuelles depuis l'historique
        contextual_matches = re.findall(self.contextual_pattern, injected_prompt)
        for match in contextual_matches:
            marker = f"::CONTEXTE_{match}::"
            value = self._resolve_contextual_value(match, context)
            injected_prompt = injected_prompt.replace(marker, str(value))
        
        # 3. Rétro-injections depuis les réponses précédentes
        retro_matches = re.findall(self.retro_pattern, injected_prompt)
        for match in retro_matches:
            marker = f"::RETRO_{match}::"
            value = self._resolve_retro_injection(match, context)
            injected_prompt = injected_prompt.replace(marker, str(value))
        
        return injected_prompt
    
    def process_ai_response_for_retro_injection(self, ai_response: str, 
                                              original_prompt: str, context: Dict[str, Any]):
        """Traite la réponse IA pour les rétro-injections futures."""
        
        # Enregistrement dans l'historique
        self.context_history.append({
            "timestamp": time.time(),
            "prompt": original_prompt,
            "response": ai_response,
            "context": context.copy()
        })
        
        # Limite l'historique
        if len(self.context_history) > 20:
            self.context_history = self.context_history[-10:]
        
        # Application des règles de rétro-injection
        for rule in self.retro_injection_rules:
            if re.search(rule.trigger_pattern, ai_response, re.IGNORECASE):
                extracted_value = self._extract_value_from_response(ai_response, rule.extraction_method)
                if extracted_value:
                    self.dynamic_values[rule.injection_target] = extracted_value
                    print(f"🔮 Retro-injection triggered: {rule.injection_target} = {extracted_value}")
    
    def _resolve_injection_value(self, injection_point: InjectionPoint, 
                               context: Dict[str, Any]) -> str:
        """Résout la valeur d'un point d'injection."""
        
        try:
            if injection_point.value_source == "context":
                # Valeur depuis le contexte
                keys = injection_point.marker.replace("::", "").lower().split("_")
                value = context
                for key in keys:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        return injection_point.fallback_value
                
                # Application de la transformation
                if injection_point.transformation:
                    value = injection_point.transformation(value)
                
                return str(value)
            
            elif injection_point.value_source == "dynamic":
                # Valeur dynamique calculée
                marker_name = injection_point.marker.replace("::", "")
                return self.dynamic_values.get(marker_name, injection_point.fallback_value)
            
            else:
                return injection_point.fallback_value
                
        except Exception as e:
            print(f"🔮 Error resolving injection {injection_point.marker}: {e}")
            return injection_point.fallback_value
    
    def _resolve_contextual_value(self, marker: str, context: Dict[str, Any]) -> str:
        """Résout une valeur contextuelle depuis l'historique."""
        
        if not self.context_history:
            return f"[CONTEXTE_{marker}_VIDE]"
        
        # Recherche dans l'historique récent
        for entry in reversed(self.context_history[-3:]):  # 3 dernières entrées
            if marker.lower() in entry["response"].lower():
                # Extraction contextuelle
                if marker == "DOMAINE_DETECTE":
                    return self._extract_domain_from_response(entry["response"])
                elif marker == "COMPLEXITE_PRECEDENTE":
                    return self._extract_complexity_from_response(entry["response"])
                elif marker == "PATTERNS_IDENTIFIES":
                    return self._extract_patterns_from_response(entry["response"])
        
        return f"[CONTEXTE_{marker}_NON_TROUVE]"
    
    def _resolve_retro_injection(self, marker: str, context: Dict[str, Any]) -> str:
        """Résout une rétro-injection depuis les valeurs dynamiques."""
        
        return self.dynamic_values.get(marker, f"[RETRO_{marker}_VIDE]")
    
    def _extract_value_from_response(self, response: str, extraction_method: str) -> Optional[str]:
        """Extrait une valeur de la réponse selon la méthode spécifiée."""
        
        if extraction_method == "domain_detection":
            return self._extract_domain_from_response(response)
        elif extraction_method == "complexity_assessment":
            return self._extract_complexity_from_response(response)
        elif extraction_method == "pattern_identification":
            return self._extract_patterns_from_response(response)
        elif extraction_method == "json_field":
            return self._extract_json_field(response, "domaine_influence")
        else:
            return None
    
    def _extract_domain_from_response(self, response: str) -> str:
        """Extrait le domaine détecté de la réponse."""
        
        # Recherche de patterns de domaine
        domain_patterns = [
            r'"domaine_influence"\s*:\s*"([^"]+)"',
            r'domaine[:\s]+([a-zA-Z_]+)',
            r'domain[:\s]+([a-zA-Z_]+)',
        ]
        
        for pattern in domain_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Fallback par mots-clés
        if "architecture" in response.lower():
            return "architecture_logicielle"
        elif "code" in response.lower():
            return "developpement"
        elif "documentation" in response.lower():
            return "documentation"
        
        return "general"
    
    def _extract_complexity_from_response(self, response: str) -> str:
        """Extrait la complexité de la réponse."""
        
        complexity_patterns = [
            r'"complexite_arcane"\s*:\s*"([^"]+)"',
            r'complexit[eé][:\s]+([a-zA-Z_]+)',
        ]
        
        for pattern in complexity_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Analyse par mots-clés
        if any(word in response.lower() for word in ["complex", "difficile", "elevee"]):
            return "elevee"
        elif any(word in response.lower() for word in ["simple", "facile", "faible"]):
            return "faible"
        
        return "moyenne"
    
    def _extract_patterns_from_response(self, response: str) -> str:
        """Extrait les patterns identifiés."""
        
        patterns = []
        
        # Recherche de patterns architecturaux
        architectural_patterns = [
            "microservices", "mvc", "mvp", "singleton", "factory", "observer",
            "strategy", "decorator", "adapter", "facade"
        ]
        
        for pattern in architectural_patterns:
            if pattern in response.lower():
                patterns.append(pattern)
        
        return ", ".join(patterns[:3]) if patterns else "aucun_pattern_detecte"
    
    def _extract_json_field(self, response: str, field_name: str) -> Optional[str]:
        """Extrait un champ JSON spécifique."""
        
        try:
            # Recherche de JSON dans la réponse
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_data = json.loads(json_match.group(0))
                return self._get_nested_value(json_data, field_name)
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _get_nested_value(self, data: Dict, field_path: str) -> Optional[str]:
        """Récupère une valeur imbriquée dans un dictionnaire."""
        
        keys = field_path.split(".")
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return str(current) if current is not None else None


class LuciformDynamicPromptSystem:
    """Système de prompts Luciformes avec injections dynamiques."""
    
    def __init__(self):
        self.injection_engine = DynamicInjectionEngine()
        self.prompt_templates = {}
        self._initialize_injection_points()
        self._initialize_retro_injection_rules()
        
        print("🔮 Luciform Dynamic Prompt System initialized")
    
    def _initialize_injection_points(self):
        """Initialise les points d'injection standard."""
        
        # Injections contextuelles
        self.injection_engine.register_injection_point(
            "TAILLE_CONTENU", "context", 
            transformation=lambda x: f"{len(str(x))} caractères",
            fallback_value="taille_inconnue"
        )
        
        self.injection_engine.register_injection_point(
            "EXTENSION_FICHIER", "context",
            fallback_value="extension_inconnue"
        )
        
        self.injection_engine.register_injection_point(
            "LANGAGE_DETECTE", "context",
            fallback_value="langage_inconnu"
        )
        
        # Injections dynamiques
        self.injection_engine.register_injection_point(
            "DOMAINE_PRECEDENT", "dynamic",
            fallback_value="aucun_domaine_precedent",
            is_contextual=True
        )
        
        self.injection_engine.register_injection_point(
            "PATTERNS_PRECEDENTS", "dynamic",
            fallback_value="aucun_pattern_precedent",
            is_contextual=True
        )
    
    def _initialize_retro_injection_rules(self):
        """Initialise les règles de rétro-injection."""
        
        # Détection de domaine pour injection future
        self.injection_engine.register_retro_injection_rule(
            trigger_pattern=r'"domaine_influence"\s*:\s*"([^"]+)"',
            injection_target="DOMAINE_PRECEDENT",
            extraction_method="domain_detection"
        )
        
        # Détection de complexité pour injection future
        self.injection_engine.register_retro_injection_rule(
            trigger_pattern=r'"complexite_arcane"\s*:\s*"([^"]+)"',
            injection_target="COMPLEXITE_PRECEDENTE",
            extraction_method="complexity_assessment"
        )
        
        # Détection de patterns pour injection future
        self.injection_engine.register_retro_injection_rule(
            trigger_pattern=r'pattern|architecture|design',
            injection_target="PATTERNS_PRECEDENTS",
            extraction_method="pattern_identification"
        )
    
    def register_dynamic_template(self, name: str, template: str):
        """Enregistre un template avec injections dynamiques."""
        
        self.prompt_templates[name] = template
        print(f"🔮 Registered dynamic template: {name}")
    
    async def generate_dynamic_prompt(self, template_name: str, context: Dict[str, Any]) -> str:
        """Génère un prompt avec injections dynamiques."""
        
        if template_name not in self.prompt_templates:
            raise ValueError(f"Template {template_name} not found")
        
        template = self.prompt_templates[template_name]
        
        # Injection des valeurs dynamiques
        dynamic_prompt = self.injection_engine.inject_dynamic_values(template, context)
        
        print(f"🔮 Generated dynamic prompt for {template_name}")
        return dynamic_prompt
    
    async def process_ai_response(self, ai_response: str, original_prompt: str, 
                                context: Dict[str, Any]):
        """Traite la réponse IA pour les futures injections."""
        
        self.injection_engine.process_ai_response_for_retro_injection(
            ai_response, original_prompt, context
        )
    
    def get_injection_status(self) -> Dict[str, Any]:
        """Retourne le statut des injections."""
        
        return {
            "injection_points": len(self.injection_engine.injection_points),
            "retro_injection_rules": len(self.injection_engine.retro_injection_rules),
            "context_history_size": len(self.injection_engine.context_history),
            "dynamic_values": dict(self.injection_engine.dynamic_values),
            "templates_registered": len(self.prompt_templates)
        }


# Templates avec injections dynamiques
DYNAMIC_LUCIFORM_TEMPLATES = {
    "orchestration_contextuelle": """
⛧ INVOCATION_ORCHESTRATION_CONTEXTUELLE ⛧

Oracle du Nexus, analyse ce contenu en utilisant le contexte des analyses précédentes.

CONTENU_MYSTIQUE:
{content}

CONTEXTE_DYNAMIQUE:
- Taille: ::TAILLE_CONTENU::
- Extension: ::EXTENSION_FICHIER::
- Langage: ::LANGAGE_DETECTE::

CONTEXTE_PRECEDENT:
- Domaine précédent: ::CONTEXTE_DOMAINE_DETECTE::
- Complexité précédente: ::CONTEXTE_COMPLEXITE_PRECEDENTE::
- Patterns identifiés: ::RETRO_PATTERNS_PRECEDENTS::

MISSION_CONTEXTUELLE:
1. Compare avec les analyses précédentes
2. Identifie les évolutions et continuités
3. Adapte la stratégie selon l'historique

RETOURNE_ORCHESTRATION_ADAPTATIVE:
⛧ ORCHESTRATION_CONTEXTUELLE_DEMONIAQUE ⛧
{{
  "essence_revelee": {{
    "nature_profonde": "code|documentation|mixte",
    "evolution_depuis_precedent": "similaire|different|evolution",
    "domaine_influence": "domaine_detecte",
    "relation_contexte_precedent": "continuation|rupture|evolution"
  }},
  "orchestration_demoniaque": {{
    "adaptateurs_invoques": [
      {{
        "entite": "detecteur_contenu",
        "methode_mystique": "analyse_comparative",
        "parametres_arcanes": {{
          "contexte_precedent": "::RETRO_DOMAINE_PRECEDENT::",
          "mode_comparaison": true
        }}
      }}
    ]
  }}
}}
""",

    "amelioration_recursive": """
⛧ INVOCATION_AMELIORATION_RECURSIVE_CONTEXTUELLE ⛧

Oracle, améliore l'analyse en utilisant les insights accumulés.

ANALYSE_COURANTE:
{current_analysis}

MEMOIRES_CONTEXTUELLES:
{contextual_memories}

INSIGHTS_PRECEDENTS:
- Domaine établi: ::RETRO_DOMAINE_PRECEDENT::
- Patterns récurrents: ::RETRO_PATTERNS_PRECEDENTS::
- Complexité tendance: ::CONTEXTE_COMPLEXITE_PRECEDENTE::

MISSION_RECURSIVE:
1. Exploite les patterns récurrents identifiés
2. Renforce les insights cohérents
3. Détecte les anomalies ou évolutions

RETOURNE_AMELIORATION_CONTEXTUELLE:
⛧ AMELIORATION_RECURSIVE_DEMONIAQUE ⛧
{{
  "insights_enrichis": {{
    "coherence_avec_precedent": "forte|moyenne|faible",
    "nouveaux_patterns_detectes": ["pattern1", "pattern2"],
    "evolution_complexite": "croissante|stable|decroissante"
  }},
  "orchestration_amelioree": {{
    "adaptateurs_invoques": [
      {{
        "entite": "analyseur_ia",
        "methode_mystique": "analyse_contextuelle_profonde",
        "parametres_arcanes": {{
          "contexte_historique": true,
          "patterns_precedents": "::RETRO_PATTERNS_PRECEDENTS::"
        }}
      }}
    ]
  }}
}}
"""
}


async def test_dynamic_injection_system():
    """Test du système d'injections dynamiques."""
    
    print("🔮 Testing Dynamic Injection System...")
    
    # Création du système
    dynamic_system = LuciformDynamicPromptSystem()
    
    # Enregistrement des templates
    for name, template in DYNAMIC_LUCIFORM_TEMPLATES.items():
        dynamic_system.register_dynamic_template(name, template)
    
    # Contexte de test
    context = {
        "content": "# Test Document\n\nThis is a test document with some code.",
        "file_path": "test.md",
        "content_size": 50,
        "file_extension": ".md",
        "language": "markdown"
    }
    
    # Génération du premier prompt
    prompt1 = await dynamic_system.generate_dynamic_prompt("orchestration_contextuelle", context)
    print(f"\n🔮 Generated prompt 1 (length: {len(prompt1)})")
    
    # Simulation d'une réponse IA
    ai_response1 = '''
    {
      "essence_revelee": {
        "nature_profonde": "documentation",
        "domaine_influence": "architecture_logicielle",
        "complexite_arcane": "moyenne"
      }
    }
    '''
    
    # Traitement de la réponse pour rétro-injection
    await dynamic_system.process_ai_response(ai_response1, prompt1, context)
    
    # Génération du second prompt (avec rétro-injections)
    context2 = context.copy()
    context2["content"] = "# Advanced Architecture\n\nThis builds upon previous concepts."
    
    prompt2 = await dynamic_system.generate_dynamic_prompt("orchestration_contextuelle", context2)
    print(f"\n🔮 Generated prompt 2 with retro-injections (length: {len(prompt2)})")
    
    # Statut des injections
    status = dynamic_system.get_injection_status()
    print(f"\n🔮 Injection Status:")
    print(f"  📊 Injection points: {status['injection_points']}")
    print(f"  🔄 Retro-injection rules: {status['retro_injection_rules']}")
    print(f"  📚 Context history: {status['context_history_size']}")
    print(f"  💾 Dynamic values: {status['dynamic_values']}")


if __name__ == "__main__":
    asyncio.run(test_dynamic_injection_system())
