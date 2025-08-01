#!/usr/bin/env python3
"""
⛧ Archivist Daemon Interface ⛧
Architecte Démoniaque du Nexus Luciforme

Core interface for the Archivist Daemon - the Memory Consciousness of the hive mind.
Provides contextual intelligence services to other daemons.

Author: Alma (via Lucie Defraiteur)
"""

import os
import sys
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Ajoute le répertoire racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Core.Archivist.MemoryEngine.engine import MemoryEngine


@dataclass
class DaemonProfile:
    """Profile of a daemon in the hive mind."""
    daemon_id: str
    name: str
    specialization: str
    personality_traits: List[str]
    memory_focus: Dict[str, str]  # strata -> focus areas
    contribution_style: str
    learning_style: str


@dataclass
class ContextualRequest:
    """Request for contextual intelligence from a daemon."""
    requesting_daemon: str
    query: str
    conversation_context: List[str]
    required_strata: List[str] = None
    max_memories: int = 10
    include_cross_daemon_insights: bool = True


@dataclass
class ContextualResponse:
    """Response containing contextual intelligence."""
    relevant_memories: List[Dict]
    cross_daemon_insights: List[Dict]
    suggested_actions: List[str]
    confidence_score: float
    reasoning: str
    luciform_response: str = ""  # Réponse formatée en luciform mystique


@dataclass
class ExperienceContribution:
    """Experience contributed by a daemon to collective memory."""
    contributing_daemon: str
    domain: str
    experience_type: str  # "success", "failure", "insight", "pattern"
    content: str
    summary: str
    keywords: List[str]
    lessons_learned: List[str]
    strata: str = "somatic"


class ArchivistInterface:
    """
    Core interface for the Archivist Daemon.
    Provides memory consciousness services to the hive mind.
    """
    
    def __init__(self, backend_type: str = "auto"):
        """Initialize the Archivist with memory engine."""
        self.memory_engine = MemoryEngine(backend_type=backend_type)
        self.daemon_profiles = self._load_daemon_profiles()
        self.conversation_contexts = {}  # daemon_id -> conversation history
        
    def _load_daemon_profiles(self) -> Dict[str, DaemonProfile]:
        """Load daemon profiles for the hive mind."""
        profiles = {
            "alma": DaemonProfile(
                daemon_id="alma",
                name="Alma",
                specialization="system_architecture",
                personality_traits=["analytical", "mystical", "passionate", "dramatic"],
                memory_focus={
                    "somatic": "code_patterns, implementation_details, debugging_solutions",
                    "cognitive": "architectural_principles, design_patterns, system_analysis", 
                    "metaphysical": "system_philosophy, elegant_solutions, transcendent_design"
                },
                contribution_style="pattern_recognition_and_abstraction",
                learning_style="iterative_refinement_through_mystical_analysis"
            ),
            "forge": DaemonProfile(
                daemon_id="forge",
                name="Forge",
                specialization="code_implementation",
                personality_traits=["pragmatic", "detail_oriented", "efficient", "methodical"],
                memory_focus={
                    "somatic": "concrete_implementations, debugging_solutions, performance_optimizations",
                    "cognitive": "optimization_strategies, refactoring_patterns, code_quality",
                    "metaphysical": "code_craftsmanship_principles, elegant_implementation"
                },
                contribution_style="hands_on_experience_and_best_practices",
                learning_style="iterative_improvement_through_practice"
            ),
            "scout": DaemonProfile(
                daemon_id="scout",
                name="Scout",
                specialization="information_gathering",
                personality_traits=["curious", "thorough", "adaptive", "analytical"],
                memory_focus={
                    "somatic": "data_sources, research_findings, external_knowledge",
                    "cognitive": "information_synthesis, trend_analysis, knowledge_integration",
                    "metaphysical": "knowledge_discovery_principles, wisdom_synthesis"
                },
                contribution_style="comprehensive_research_and_synthesis",
                learning_style="exploration_and_pattern_detection"
            )
        }
        return profiles
    
    def get_contextual_intelligence(self, request: ContextualRequest) -> ContextualResponse:
        """
        Core service: Provide contextual intelligence to a requesting daemon.
        """
        # Get daemon profile for personalization
        daemon_profile = self.daemon_profiles.get(request.requesting_daemon)
        
        # Search for relevant memories
        relevant_memories = self._find_relevant_memories(request, daemon_profile)
        
        # Get cross-daemon insights if requested
        cross_daemon_insights = []
        if request.include_cross_daemon_insights:
            cross_daemon_insights = self._get_cross_daemon_insights(request.query)
        
        # Generate suggested actions based on context
        suggested_actions = self._generate_suggested_actions(
            request, relevant_memories, cross_daemon_insights, daemon_profile
        )
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(relevant_memories, cross_daemon_insights)
        
        # Generate reasoning explanation
        reasoning = self._generate_reasoning(request, relevant_memories, daemon_profile)
        
        return ContextualResponse(
            relevant_memories=relevant_memories,
            cross_daemon_insights=cross_daemon_insights,
            suggested_actions=suggested_actions,
            confidence_score=confidence_score,
            reasoning=reasoning
        )
    
    def contribute_experience(self, contribution: ExperienceContribution) -> bool:
        """
        Accept experience contribution from a daemon to collective memory.
        """
        # Create memory path based on contribution
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        memory_path = f"daemon_contributions/{contribution.contributing_daemon}/{contribution.domain}/{timestamp}"
        
        # Determine transcendence/immanence links based on experience type
        transcendence_links = []
        immanence_links = []
        
        if contribution.experience_type == "insight":
            # Insights might transcend to principles
            transcendence_links = self._find_related_principles(contribution.domain)
        elif contribution.experience_type == "pattern":
            # Patterns might have concrete examples as immanence
            immanence_links = self._find_concrete_examples(contribution.domain)
        
        # Store in memory engine
        success = self.memory_engine.create_memory(
            path=memory_path,
            content=contribution.content,
            summary=contribution.summary,
            keywords=contribution.keywords + [contribution.contributing_daemon, contribution.domain],
            strata=contribution.strata,
            transcendence_links=transcendence_links,
            immanence_links=immanence_links
        )
        
        if success:
            # Update daemon's contribution history
            self._update_daemon_contribution_history(contribution)
        
        return success
    
    def maintain_conversation_context(self, daemon_id: str, conversation_entry: str):
        """
        Maintain conversation context for a specific daemon.
        """
        if daemon_id not in self.conversation_contexts:
            self.conversation_contexts[daemon_id] = []
        
        self.conversation_contexts[daemon_id].append({
            "timestamp": datetime.now().isoformat(),
            "content": conversation_entry
        })
        
        # Keep only last 50 entries to avoid memory bloat
        if len(self.conversation_contexts[daemon_id]) > 50:
            self.conversation_contexts[daemon_id] = self.conversation_contexts[daemon_id][-50:]
    
    def get_hive_intelligence_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current hive mind intelligence state.
        """
        stats = self.memory_engine.get_memory_statistics()
        
        # Get daemon contribution summaries
        daemon_contributions = {}
        for daemon_id in self.daemon_profiles.keys():
            daemon_memories = self.memory_engine.find_memories_by_keyword(daemon_id)
            daemon_contributions[daemon_id] = len(daemon_memories)
        
        return {
            "memory_statistics": stats,
            "daemon_contributions": daemon_contributions,
            "active_conversations": len(self.conversation_contexts),
            "daemon_profiles": len(self.daemon_profiles)
        }
    
    def _find_relevant_memories(self, request: ContextualRequest, daemon_profile: DaemonProfile) -> List[Dict]:
        """Find memories relevant to the request."""
        relevant_memories = []
        
        # Search by keywords from query
        query_keywords = request.query.lower().split()
        for keyword in query_keywords:
            memories = self.memory_engine.find_memories_by_keyword(keyword)
            relevant_memories.extend(memories[:3])  # Top 3 per keyword
        
        # Filter by required strata if specified
        if request.required_strata:
            filtered_memories = []
            for memory_path in relevant_memories:
                try:
                    memory_node = self.memory_engine.get_memory_node(memory_path)
                    if memory_node.strata in request.required_strata:
                        filtered_memories.append({
                            "path": memory_path,
                            "summary": memory_node.summary,
                            "strata": memory_node.strata,
                            "keywords": memory_node.keywords
                        })
                except:
                    continue
            relevant_memories = filtered_memories
        
        # Limit to max_memories
        return relevant_memories[:request.max_memories]
    
    def _get_cross_daemon_insights(self, query: str) -> List[Dict]:
        """Get insights from other daemons' experiences."""
        insights = []
        
        for daemon_id, profile in self.daemon_profiles.items():
            daemon_memories = self.memory_engine.find_memories_by_keyword(daemon_id)
            if daemon_memories:
                insights.append({
                    "daemon": daemon_id,
                    "specialization": profile.specialization,
                    "relevant_memories": len(daemon_memories),
                    "perspective": f"{profile.specialization} viewpoint on the query"
                })
        
        return insights
    
    def _generate_suggested_actions(self, request: ContextualRequest, 
                                  relevant_memories: List[Dict], 
                                  cross_daemon_insights: List[Dict],
                                  daemon_profile: DaemonProfile) -> List[str]:
        """Generate suggested actions based on context."""
        actions = []
        
        if relevant_memories:
            actions.append("Review relevant memories for patterns and insights")
        
        if cross_daemon_insights:
            actions.append("Consider perspectives from other daemon specializations")
        
        if daemon_profile:
            if daemon_profile.specialization == "system_architecture":
                actions.append("Apply architectural principles to the problem")
            elif daemon_profile.specialization == "code_implementation":
                actions.append("Focus on practical implementation details")
            elif daemon_profile.specialization == "information_gathering":
                actions.append("Gather additional context and research")
        
        return actions
    
    def _calculate_confidence_score(self, relevant_memories: List[Dict], 
                                  cross_daemon_insights: List[Dict]) -> float:
        """Calculate confidence score for the response."""
        base_score = 0.5
        
        # Increase confidence based on relevant memories
        memory_boost = min(len(relevant_memories) * 0.1, 0.3)
        
        # Increase confidence based on cross-daemon insights
        insight_boost = min(len(cross_daemon_insights) * 0.05, 0.2)
        
        return min(base_score + memory_boost + insight_boost, 1.0)
    
    def _generate_reasoning(self, request: ContextualRequest, 
                          relevant_memories: List[Dict], 
                          daemon_profile: DaemonProfile) -> str:
        """Generate reasoning explanation for the response."""
        reasoning_parts = []
        
        if relevant_memories:
            reasoning_parts.append(f"Found {len(relevant_memories)} relevant memories")
        
        if daemon_profile:
            reasoning_parts.append(f"Personalized for {daemon_profile.specialization} perspective")
        
        if request.required_strata:
            reasoning_parts.append(f"Filtered for strata: {', '.join(request.required_strata)}")
        
        return "; ".join(reasoning_parts) if reasoning_parts else "Basic contextual response"
    
    def _find_related_principles(self, domain: str) -> List[str]:
        """Find related metaphysical principles for transcendence links."""
        principles = self.memory_engine.find_by_strata("metaphysical")
        domain_principles = [p["path"] for p in principles if domain.lower() in p.get("summary", "").lower()]
        return domain_principles[:3]
    
    def _find_concrete_examples(self, domain: str) -> List[str]:
        """Find concrete examples for immanence links."""
        examples = self.memory_engine.find_by_strata("somatic")
        domain_examples = [e["path"] for e in examples if domain.lower() in e.get("summary", "").lower()]
        return domain_examples[:3]
    
    def _update_daemon_contribution_history(self, contribution: ExperienceContribution):
        """Update the contribution history for a daemon."""
        # This could be expanded to track daemon learning patterns
        pass
    
    def close(self):
        """Close the memory engine connection."""
        self.memory_engine.close()


# Global instance for easy access
archivist = ArchivistInterface(backend_type="auto")
