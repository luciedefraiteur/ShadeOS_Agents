#!/usr/bin/env python3
"""
⛧ Luciform Injection Engine ⛧
Architecte Démoniaque du Nexus Luciforme

Engine for dynamic injection in luciform templates and retro-injection processing.
Handles pattern replacement, context injection, and response parsing.

Author: Alma (via Lucie Defraiteur)
"""

import os
import re
import sys
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Core.Archivist.luciform_parser import ParsedDaemonProfile


@dataclass
class InjectionContext:
    """Context data for luciform injection."""
    daemon_profile: ParsedDaemonProfile
    relevant_data: List[Dict]
    collective_memory: List[Dict]
    cross_daemon_insights: List[Dict]
    conversation_context: List[Dict]
    specific_context: str
    precise_question: str
    confidence_level: float = 0.8


@dataclass
class RetroInjectionData:
    """Data extracted for retro-injection."""
    main_analysis: str
    discovered_insights: List[str]
    recommendations: List[str]
    confidence_level: float
    sources_used: List[str]
    detected_patterns: List[str]
    contextual_amplification: str


class LuciformInjectionEngine:
    """
    Engine for dynamic luciform template injection and processing.
    """
    
    def __init__(self, templates_directory: str = None):
        """Initialize the injection engine."""
        if templates_directory is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            templates_directory = os.path.join(current_dir, "luciform_templates")
        
        self.templates_directory = templates_directory
        self.injection_patterns = {
            # Forward injection patterns (template → prompt)
            "::INJECTER_DONNEES_RELEVANTES_ICI::": self._inject_relevant_data,
            "::INJECTER_MEMOIRE_COLLECTIVE_ICI::": self._inject_collective_memory,
            "::INJECTER_INSIGHTS_CROSS_DAEMON_ICI::": self._inject_cross_daemon_insights,
            "::INJECTER_CONTEXTE_CONVERSATION_ICI::": self._inject_conversation_context,
            "::DAEMON_ID::": self._inject_daemon_id,
            "::DAEMON_NAME::": self._inject_daemon_name,
            "::SPECIALISATION::": self._inject_specialization,
            "::SYMBOLES_DAEMON::": self._inject_daemon_symbols,
            "::AMPLIFICATION_DEMONIAQUE::": self._inject_demonic_amplification,
            "::CONTEXTE_SPECIFIQUE::": self._inject_specific_context,
            "::QUESTION_PRECISE::": self._inject_precise_question,
            "::NIVEAU_CONFIANCE::": self._inject_confidence_level
        }
        
        self.retro_injection_patterns = {
            # Retro injection patterns (response → structured data)
            "::RETRO_INJECTER_ANALYSE_PRINCIPALE_ICI::": "main_analysis",
            "::RETRO_INJECTER_INSIGHTS_DECOUVERTS_ICI::": "discovered_insights",
            "::RETRO_INJECTER_RECOMMANDATIONS_ICI::": "recommendations",
            "::RETRO_INJECTER_NIVEAU_CONFIANCE_ICI::": "confidence_level",
            "::RETRO_INJECTER_SOURCES_UTILISEES_ICI::": "sources_used",
            "::RETRO_INJECTER_PATTERNS_DETECTES_ICI::": "detected_patterns",
            "::RETRO_INJECTER_AMPLIFICATION_CONTEXTUELLE_ICI::": "contextual_amplification"
        }
    
    def load_template(self, template_name: str) -> str:
        """Load a luciform template."""
        template_path = os.path.join(self.templates_directory, f"{template_name}.luciform")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"⛧ Template luciforme non trouvé: {template_path}")
    
    def inject_template(self, template_content: str, context: InjectionContext) -> str:
        """Inject context data into luciform template."""
        injected_content = template_content
        
        # Apply all injection patterns
        for pattern, injector_func in self.injection_patterns.items():
            if pattern in injected_content:
                replacement = injector_func(context)
                injected_content = injected_content.replace(pattern, str(replacement))
        
        return injected_content
    
    def extract_retro_injection_data(self, response_text: str) -> RetroInjectionData:
        """Extract data from response for retro-injection."""
        # Simple extraction - could be enhanced with NLP
        
        # Extract main analysis (first substantial paragraph)
        analysis_match = re.search(r'<🜂analyse_principale>(.*?)</🜂analyse_principale>', 
                                 response_text, re.DOTALL)
        main_analysis = analysis_match.group(1).strip() if analysis_match else "Analyse non extraite"
        
        # Extract insights (look for bullet points or numbered lists)
        insights = re.findall(r'[•\-\*]\s*(.+)', response_text)
        if not insights:
            insights = re.findall(r'\d+\.\s*(.+)', response_text)
        
        # Extract recommendations (look for "recommande", "suggère", etc.)
        recommendations = []
        rec_patterns = [r'recommande[^.]*\.', r'suggère[^.]*\.', r'propose[^.]*\.']
        for pattern in rec_patterns:
            recommendations.extend(re.findall(pattern, response_text, re.IGNORECASE))
        
        # Calculate confidence based on response characteristics
        confidence = self._calculate_response_confidence(response_text)
        
        # Extract sources (look for references to memory, data, etc.)
        sources = re.findall(r'(?:selon|d\'après|basé sur)\s+([^.]+)', response_text, re.IGNORECASE)
        
        # Extract patterns (look for "pattern", "structure", "tendance")
        patterns = re.findall(r'(?:pattern|structure|tendance)[^.]*\.', response_text, re.IGNORECASE)
        
        # Extract contextual amplification
        amp_match = re.search(r'<🜃amplification_active>(.*?)</🜃amplification_active>', 
                            response_text, re.DOTALL)
        contextual_amplification = amp_match.group(1).strip() if amp_match else "Amplification mystique active"
        
        return RetroInjectionData(
            main_analysis=main_analysis,
            discovered_insights=insights[:5],  # Limit to 5
            recommendations=recommendations[:3],  # Limit to 3
            confidence_level=confidence,
            sources_used=sources[:3],  # Limit to 3
            detected_patterns=patterns[:3],  # Limit to 3
            contextual_amplification=contextual_amplification
        )
    
    def apply_retro_injection(self, template_response: str, retro_data: RetroInjectionData) -> str:
        """Apply retro-injection to template response."""
        result = template_response
        
        # Apply retro-injection patterns
        for pattern, data_field in self.retro_injection_patterns.items():
            if pattern in result:
                value = getattr(retro_data, data_field, "Donnée non disponible")
                
                # Format lists as bullet points
                if isinstance(value, list):
                    if value:
                        formatted_value = "\n".join(f"    • {item}" for item in value)
                    else:
                        formatted_value = "    • Aucune donnée extraite"
                else:
                    formatted_value = str(value)
                
                result = result.replace(pattern, formatted_value)
        
        return result
    
    def process_full_injection_cycle(self, template_name: str, context: InjectionContext, 
                                   openai_response: str) -> Tuple[str, str]:
        """Process complete injection cycle: template → prompt → response → retro-injection."""
        
        # 1. Load and inject template
        template = self.load_template(template_name)
        injected_prompt = self.inject_template(template, context)
        
        # 2. Extract retro-injection data from OpenAI response
        retro_data = self.extract_retro_injection_data(openai_response)
        
        # 3. Find response template in injected prompt
        response_template_match = re.search(
            r'<🜲luciform id="[^"]*_response"[^>]*>.*?</🜲luciform>', 
            injected_prompt, re.DOTALL
        )
        
        if response_template_match:
            response_template = response_template_match.group(0)
            # 4. Apply retro-injection to response template
            final_response = self.apply_retro_injection(response_template, retro_data)
        else:
            final_response = f"⛧ Template de réponse non trouvé dans le prompt injecté"
        
        return injected_prompt, final_response
    
    # Injection methods
    def _inject_relevant_data(self, context: InjectionContext) -> str:
        if not context.relevant_data:
            return "Aucune donnée relevante disponible"
        
        data_summary = []
        for data in context.relevant_data[:3]:  # Limit to 3 items
            summary = data.get('summary', 'Donnée sans résumé')
            data_summary.append(f"• {summary}")
        
        return "\n".join(data_summary)
    
    def _inject_collective_memory(self, context: InjectionContext) -> str:
        if not context.collective_memory:
            return "Mémoire collective vide"
        
        memory_items = []
        for memory in context.collective_memory[:3]:
            summary = memory.get('summary', 'Mémoire sans résumé')
            memory_items.append(f"• {summary}")
        
        return "\n".join(memory_items)
    
    def _inject_cross_daemon_insights(self, context: InjectionContext) -> str:
        if not context.cross_daemon_insights:
            return "Aucun insight cross-daemon disponible"
        
        insights = []
        for insight in context.cross_daemon_insights[:3]:
            summary = insight.get('summary', 'Insight sans résumé')
            daemon = insight.get('contributing_daemon', 'daemon_inconnu')
            insights.append(f"• {daemon}: {summary}")
        
        return "\n".join(insights)
    
    def _inject_conversation_context(self, context: InjectionContext) -> str:
        if not context.conversation_context:
            return "Aucun contexte de conversation"
        
        conv_items = []
        for item in context.conversation_context[-3:]:  # Last 3 items
            role = item.get('role', 'unknown')
            content = item.get('content', '')[:100]  # Truncate
            conv_items.append(f"• {role}: {content}...")
        
        return "\n".join(conv_items)
    
    def _inject_daemon_id(self, context: InjectionContext) -> str:
        return context.daemon_profile.daemon_id
    
    def _inject_daemon_name(self, context: InjectionContext) -> str:
        return context.daemon_profile.name
    
    def _inject_specialization(self, context: InjectionContext) -> str:
        return context.daemon_profile.specialization
    
    def _inject_daemon_symbols(self, context: InjectionContext) -> str:
        return " ".join(context.daemon_profile.symbols_signature)
    
    def _inject_demonic_amplification(self, context: InjectionContext) -> str:
        return context.daemon_profile.demonic_amplification
    
    def _inject_specific_context(self, context: InjectionContext) -> str:
        return context.specific_context
    
    def _inject_precise_question(self, context: InjectionContext) -> str:
        return context.precise_question
    
    def _inject_confidence_level(self, context: InjectionContext) -> str:
        return str(int(context.confidence_level * 10))
    
    def _calculate_response_confidence(self, response_text: str) -> float:
        """Calculate confidence based on response characteristics."""
        confidence = 0.5  # Base confidence
        
        # Check for structured content
        if '<🜲luciform' in response_text:
            confidence += 0.2
        
        # Check for detailed analysis
        if len(response_text) > 500:
            confidence += 0.1
        
        # Check for specific patterns
        analysis_indicators = ['analyse', 'découvre', 'révèle', 'identifie']
        found_indicators = sum(1 for indicator in analysis_indicators 
                             if indicator in response_text.lower())
        confidence += found_indicators * 0.05
        
        return min(confidence, 1.0)


# Global injection engine instance
luciform_injection_engine = LuciformInjectionEngine()
