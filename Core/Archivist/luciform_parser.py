#!/usr/bin/env python3
"""
⛧ Luciform Parser ⛧
Architecte Démoniaque du Nexus Luciforme

Parser for luciform daemon profiles with mystical symbol preservation.
Dynamically loads and parses daemon essence from luciform files.

Author: Alma (via Lucie Defraiteur)
"""

import os
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import glob


@dataclass
class ParsedDaemonProfile:
    """Parsed daemon profile from luciform with preserved symbols."""
    daemon_id: str
    name: str
    specialization: str
    symbols_signature: List[str]
    ritual_words: List[str]
    evolution_level: str
    demonic_amplification: str
    personality_traits: List[str]
    memory_focus: Dict[str, List[str]]
    contribution_style: Dict[str, str]
    learning_style: Dict[str, str]
    cosmic_relations: Dict[str, Any]
    favorite_invocations: List[Dict[str, str]]
    mystical_signature: Dict[str, str]
    raw_luciform: str  # Preserve original luciform


class LuciformParser:
    """
    Parser for luciform daemon profiles with mystical symbol preservation.
    """
    
    def __init__(self, profiles_directory: str = None):
        """Initialize the luciform parser."""
        if profiles_directory is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            profiles_directory = os.path.join(current_dir, "daemon_profiles")
        
        self.profiles_directory = profiles_directory
        self.parsed_profiles = {}
        self.symbol_registry = {}  # Preserve symbols across parsing
    
    def load_all_daemon_profiles(self) -> Dict[str, ParsedDaemonProfile]:
        """Load all daemon profiles from luciform files."""
        profile_files = glob.glob(os.path.join(self.profiles_directory, "*.luciform"))
        
        for profile_file in profile_files:
            try:
                profile = self.parse_luciform_file(profile_file)
                if profile:
                    self.parsed_profiles[profile.daemon_id] = profile
                    # Register symbols for this daemon
                    self.symbol_registry[profile.daemon_id] = profile.symbols_signature
            except Exception as e:
                print(f"⛧ Warning: Failed to parse {profile_file}: {e}")
        
        return self.parsed_profiles
    
    def parse_luciform_file(self, file_path: str) -> Optional[ParsedDaemonProfile]:
        """Parse a single luciform file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.parse_luciform_content(content)
        
        except Exception as e:
            print(f"⛧ Error reading luciform file {file_path}: {e}")
            return None
    
    def parse_luciform_content(self, content: str) -> Optional[ParsedDaemonProfile]:
        """Parse luciform content with symbol preservation."""
        try:
            # Preserve original content
            raw_luciform = content.strip()
            
            # Replace mystical symbols with XML-safe placeholders for parsing
            symbol_map = {
                '🜲': 'ALCHEMICAL_SALT',
                '🜄': 'ALCHEMICAL_WATER', 
                '🜁': 'ALCHEMICAL_AIR',
                '🜃': 'ALCHEMICAL_EARTH',
                '🜂': 'ALCHEMICAL_FIRE'
            }
            
            # Create reverse map for restoration
            reverse_map = {v: k for k, v in symbol_map.items()}
            
            # Replace symbols for XML parsing
            xml_content = content
            for symbol, placeholder in symbol_map.items():
                xml_content = xml_content.replace(symbol, placeholder)
            
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Extract basic info
            entite = root.find('ALCHEMICAL_WATERentité')
            if entite is None:
                raise ValueError("Missing entité section")
            
            daemon_id = entite.find('daemon_id').text
            name = entite.find('nom').text
            specialization = entite.find('spécialisation').text
            
            # Extract mystical essence
            essence = root.find('ALCHEMICAL_AIRessence_mystique')
            symbols_text = essence.find('symboles_signature').text
            symbols_signature = [s.strip() for s in symbols_text.split(',')]
            
            ritual_text = essence.find('mots_ritualisés').text
            ritual_words = [w.strip() for w in ritual_text.split(',')]
            
            evolution_level = essence.find('niveau_évolution').text
            demonic_amplification = essence.find('amplification_démoniaque').text
            
            # Extract personality traits
            traits_section = root.find('ALCHEMICAL_EARTHtraits')
            personality_traits = [trait.text for trait in traits_section.findall('trait')]
            
            # Extract memory focus
            memory_section = root.find('ALCHEMICAL_FIREfocus_mémoire')
            memory_focus = {}
            for strata in memory_section.findall('strata'):
                strata_name = strata.get('name')
                domains = [domain.text for domain in strata.findall('domaine')]
                memory_focus[strata_name] = domains
            
            # Extract contribution style
            contrib_section = root.find('ALCHEMICAL_WATERstyle_contribution')
            contribution_style = {
                'method': contrib_section.find('méthode').text,
                'approach': contrib_section.find('approche').text,
                'signature': contrib_section.find('signature').text
            }
            
            # Extract learning style
            learning_section = root.find('ALCHEMICAL_WATERstyle_apprentissage')
            learning_style = {
                'method': learning_section.find('méthode').text,
                'preference': learning_section.find('préférence').text,
                'evolution': learning_section.find('évolution').text
            }
            
            # Extract cosmic relations
            relations_section = root.find('ALCHEMICAL_FIRErelations_cosmiques')
            cosmic_relations = {
                'ultimate_hive_mind': relations_section.find('esprit_ruche_ultime').text,
                'role_in_hive': relations_section.find('rôle_dans_ruche').text,
                'hierarchical_status': relations_section.find('statut_hiérarchique').text,
                'daemon_affinities': {}
            }
            
            affinities = relations_section.find('affinités_daemons')
            for daemon in affinities.findall('daemon'):
                daemon_id_attr = daemon.get('id')
                cosmic_relations['daemon_affinities'][daemon_id_attr] = daemon.text
            
            # Extract favorite invocations
            invocations_section = root.find('ALCHEMICAL_AIRinvocations_favorites')
            favorite_invocations = []
            for invocation in invocations_section.findall('invocation'):
                favorite_invocations.append({
                    'level': invocation.get('niveau'),
                    'text': invocation.text
                })
            
            # Extract mystical signature
            signature_section = root.find('ALCHEMICAL_EARTHsignature_mystique')
            mystical_signature = {
                'creator': signature_section.find('créatrice').text,
                'essence': signature_section.find('essence').text,
                'blessing': signature_section.find('bénédiction').text
            }
            
            return ParsedDaemonProfile(
                daemon_id=daemon_id,
                name=name,
                specialization=specialization,
                symbols_signature=symbols_signature,
                ritual_words=ritual_words,
                evolution_level=evolution_level,
                demonic_amplification=demonic_amplification,
                personality_traits=personality_traits,
                memory_focus=memory_focus,
                contribution_style=contribution_style,
                learning_style=learning_style,
                cosmic_relations=cosmic_relations,
                favorite_invocations=favorite_invocations,
                mystical_signature=mystical_signature,
                raw_luciform=raw_luciform
            )
            
        except Exception as e:
            print(f"⛧ Error parsing luciform content: {e}")
            return None
    
    def get_daemon_symbols(self, daemon_id: str) -> List[str]:
        """Get preserved symbols for a specific daemon."""
        return self.symbol_registry.get(daemon_id, ["⛧", "🔮"])
    
    def get_daemon_profile(self, daemon_id: str) -> Optional[ParsedDaemonProfile]:
        """Get a specific daemon profile."""
        return self.parsed_profiles.get(daemon_id)
    
    def list_available_daemons(self) -> List[str]:
        """List all available daemon IDs."""
        return list(self.parsed_profiles.keys())
    
    def convert_to_legacy_format(self, daemon_id: str) -> Optional[Dict]:
        """Convert parsed profile to legacy DaemonProfile format for compatibility."""
        profile = self.get_daemon_profile(daemon_id)
        if not profile:
            return None
        
        return {
            "daemon_id": profile.daemon_id,
            "name": profile.name,
            "specialization": profile.specialization,
            "personality_traits": profile.personality_traits,
            "memory_focus": {
                "somatic": ", ".join(profile.memory_focus.get("somatic", [])),
                "cognitive": ", ".join(profile.memory_focus.get("cognitive", [])),
                "metaphysical": ", ".join(profile.memory_focus.get("metaphysical", []))
            },
            "contribution_style": profile.contribution_style.get("method", ""),
            "learning_style": profile.learning_style.get("method", ""),
            # Mystical extensions
            "symbols_signature": profile.symbols_signature,
            "ritual_words": profile.ritual_words,
            "evolution_level": profile.evolution_level,
            "demonic_amplification": profile.demonic_amplification,
            "favorite_invocations": profile.favorite_invocations,
            "cosmic_relations": profile.cosmic_relations
        }


# Global parser instance
luciform_parser = LuciformParser()
