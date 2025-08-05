# ⛧ Créé par Alma, Architecte Démoniaque ⛧
# 📚 TemplateRegistry - Registre Indexé de Fragments de Prompts

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from collections import defaultdict

@dataclass
class PromptFragment:
    """Fragment de prompt avec métadonnées"""
    fragment_id: str
    content: str
    fragment_type: str  # "header", "body", "footer", "variable", "instruction"
    thread_type: str  # "legion", "v9", "general", etc.
    template_name: str  # Nom du template qui utilise ce fragment
    variables: Dict[str, str]  # Variables utilisées dans le fragment
    metadata: Dict[str, Any]
    timestamp: float
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation"""
        return {
            "fragment_id": self.fragment_id,
            "content": self.content,
            "fragment_type": self.fragment_type,
            "thread_type": self.thread_type,
            "template_name": self.template_name,
            "variables": self.variables,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "version": self.version
        }

@dataclass
class PromptTemplate:
    """Template complet assemblé à partir de fragments"""
    template_id: str
    template_name: str
    thread_type: str
    fragment_ids: List[str]  # Ordre des fragments
    assembly_logic: Dict[str, Any]  # Logique d'assemblage
    variables: Dict[str, str]  # Variables du template complet
    metadata: Dict[str, Any]
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation"""
        return {
            "template_id": self.template_id,
            "template_name": self.template_name,
            "thread_type": self.thread_type,
            "fragment_ids": self.fragment_ids,
            "assembly_logic": self.assembly_logic,
            "variables": self.variables,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }

class TemplateRegistry:
    """Registre indexé pour les fragments et templates de prompts"""
    
    def __init__(self, registry_file: str = "logs/template_registry.json"):
        self.registry_file = Path(registry_file)
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Index principal
        self.fragments: Dict[str, PromptFragment] = {}
        self.templates: Dict[str, PromptTemplate] = {}
        
        # Index secondaires pour recherche rapide
        self.fragments_by_thread_type: Dict[str, Set[str]] = defaultdict(set)
        self.fragments_by_template: Dict[str, Set[str]] = defaultdict(set)
        self.fragments_by_type: Dict[str, Set[str]] = defaultdict(set)
        
        # Charger le registre existant
        self._load_registry()
    
    def _load_registry(self):
        """Charge le registre depuis le fichier"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Charger les fragments
                for fragment_data in data.get("fragments", {}).values():
                    fragment = PromptFragment(**fragment_data)
                    self._add_fragment_to_indexes(fragment)
                
                # Charger les templates
                for template_data in data.get("templates", {}).values():
                    template = PromptTemplate(**template_data)
                    self.templates[template.template_id] = template
                
                print(f"✅ Registre chargé: {len(self.fragments)} fragments, {len(self.templates)} templates")
                
            except Exception as e:
                print(f"⚠️ Erreur chargement registre: {e}")
    
    def _save_registry(self):
        """Sauvegarde le registre dans le fichier"""
        try:
            data = {
                "fragments": {fid: fragment.to_dict() for fid, fragment in self.fragments.items()},
                "templates": {tid: template.to_dict() for tid, template in self.templates.items()},
                "metadata": {
                    "last_updated": time.time(),
                    "total_fragments": len(self.fragments),
                    "total_templates": len(self.templates)
                }
            }
            
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde registre: {e}")
    
    def _add_fragment_to_indexes(self, fragment: PromptFragment):
        """Ajoute un fragment aux index secondaires"""
        self.fragments[fragment.fragment_id] = fragment
        self.fragments_by_thread_type[fragment.thread_type].add(fragment.fragment_id)
        self.fragments_by_template[fragment.template_name].add(fragment.fragment_id)
        self.fragments_by_type[fragment.fragment_type].add(fragment.fragment_id)
    
    def register_fragment(self, fragment: PromptFragment) -> str:
        """Enregistre un nouveau fragment"""
        if fragment.fragment_id in self.fragments:
            print(f"⚠️ Fragment {fragment.fragment_id} déjà enregistré, mise à jour")
        
        self._add_fragment_to_indexes(fragment)
        self._save_registry()
        
        return fragment.fragment_id
    
    def register_template(self, template: PromptTemplate) -> str:
        """Enregistre un nouveau template"""
        if template.template_id in self.templates:
            print(f"⚠️ Template {template.template_id} déjà enregistré, mise à jour")
        
        self.templates[template.template_id] = template
        self._save_registry()
        
        return template.template_id
    
    def get_fragment(self, fragment_id: str) -> Optional[PromptFragment]:
        """Récupère un fragment par ID"""
        return self.fragments.get(fragment_id)
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Récupère un template par ID"""
        return self.templates.get(template_id)
    
    def get_fragments_by_thread_type(self, thread_type: str) -> List[PromptFragment]:
        """Récupère tous les fragments d'un type de thread"""
        fragment_ids = self.fragments_by_thread_type.get(thread_type, set())
        return [self.fragments[fid] for fid in fragment_ids if fid in self.fragments]
    
    def get_fragments_by_template(self, template_name: str) -> List[PromptFragment]:
        """Récupère tous les fragments d'un template"""
        fragment_ids = self.fragments_by_template.get(template_name, set())
        return [self.fragments[fid] for fid in fragment_ids if fid in self.fragments]
    
    def get_fragments_by_type(self, fragment_type: str) -> List[PromptFragment]:
        """Récupère tous les fragments d'un type"""
        fragment_ids = self.fragments_by_type.get(fragment_type, set())
        return [self.fragments[fid] for fid in fragment_ids if fid in self.fragments]
    
    def search_fragments(self, query: str) -> List[PromptFragment]:
        """Recherche dans les fragments"""
        results = []
        query_lower = query.lower()
        
        for fragment in self.fragments.values():
            if (query_lower in fragment.content.lower() or 
                query_lower in fragment.fragment_id.lower() or
                query_lower in fragment.template_name.lower()):
                results.append(fragment)
        
        return results
    
    def assemble_template(self, template_id: str, variables: Dict[str, Any] = None) -> str:
        """Assemble un template complet à partir de ses fragments"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} non trouvé")
        
        variables = variables or {}
        assembled_parts = []
        
        for fragment_id in template.fragment_ids:
            fragment = self.get_fragment(fragment_id)
            if fragment:
                # Remplacer les variables dans le fragment
                content = fragment.content
                for var_name, var_value in variables.items():
                    content = content.replace(f"{{{var_name}}}", str(var_value))
                
                assembled_parts.append(content)
        
        return "\n".join(assembled_parts)
    
    def get_available_templates(self, thread_type: str = None) -> List[str]:
        """Récupère la liste des templates disponibles"""
        if thread_type:
            return [template.template_name for template in self.templates.values() 
                   if template.thread_type == thread_type]
        else:
            return [template.template_name for template in self.templates.values()]
    
    def get_template_variables(self, template_id: str) -> Dict[str, str]:
        """Récupère les variables d'un template"""
        template = self.get_template(template_id)
        if template:
            return template.variables
        return {}
    
    def export_registry(self, output_file: str = None) -> str:
        """Exporte le registre complet"""
        if output_file is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = f"logs/template_registry_export_{timestamp}.json"
        
        export_data = {
            "fragments": {fid: fragment.to_dict() for fid, fragment in self.fragments.items()},
            "templates": {tid: template.to_dict() for tid, template in self.templates.items()},
            "indexes": {
                "by_thread_type": {tt: list(fids) for tt, fids in self.fragments_by_thread_type.items()},
                "by_template": {tn: list(fids) for tn, fids in self.fragments_by_template.items()},
                "by_type": {ft: list(fids) for ft, fids in self.fragments_by_type.items()}
            },
            "metadata": {
                "export_timestamp": time.time(),
                "total_fragments": len(self.fragments),
                "total_templates": len(self.templates)
            }
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return str(output_path)

# Instance globale du registre
_global_registry = None

def get_global_registry() -> TemplateRegistry:
    """Récupère l'instance globale du registre"""
    global _global_registry
    if _global_registry is None:
        _global_registry = TemplateRegistry()
    return _global_registry

# Fonctions utilitaires pour enregistrement rapide
def register_fragment(fragment_id: str, content: str, fragment_type: str, 
                     thread_type: str, template_name: str, 
                     variables: Dict[str, str] = None, metadata: Dict[str, Any] = None) -> str:
    """Fonction utilitaire pour enregistrer rapidement un fragment"""
    registry = get_global_registry()
    
    fragment = PromptFragment(
        fragment_id=fragment_id,
        content=content,
        fragment_type=fragment_type,
        thread_type=thread_type,
        template_name=template_name,
        variables=variables or {},
        metadata=metadata or {},
        timestamp=time.time()
    )
    
    return registry.register_fragment(fragment)

def register_template(template_id: str, template_name: str, thread_type: str,
                     fragment_ids: List[str], variables: Dict[str, str] = None,
                     metadata: Dict[str, Any] = None) -> str:
    """Fonction utilitaire pour enregistrer rapidement un template"""
    registry = get_global_registry()
    
    template = PromptTemplate(
        template_id=template_id,
        template_name=template_name,
        thread_type=thread_type,
        fragment_ids=fragment_ids,
        assembly_logic={"method": "concatenation"},
        variables=variables or {},
        metadata=metadata or {},
        timestamp=time.time()
    )
    
    return registry.register_template(template)

# Test et démonstration
if __name__ == "__main__":
    print("📚 TemplateRegistry - Test du Registre")
    print("=" * 50)
    
    # Créer le registre
    registry = TemplateRegistry()
    
    # Enregistrer quelques fragments de test
    print("\n1. Enregistrement de fragments...")
    
    # Fragment pour Legion
    register_fragment(
        fragment_id="legion_header",
        content="⛧ DIALOGUE MUTANT : ALMA⛧ ↔ {demon_name.upper()} ⛧",
        fragment_type="header",
        thread_type="legion",
        template_name="mutant_dialogue",
        variables={"demon_name": "string"}
    )
    
    register_fragment(
        fragment_id="legion_context",
        content="CONTEXTE :\n- Alma⛧ (SUPREME) : Architecte Démoniaque\n- {demon_name} : {demon_title} - {demon_personality}",
        fragment_type="body",
        thread_type="legion",
        template_name="mutant_dialogue",
        variables={"demon_name": "string", "demon_title": "string", "demon_personality": "string"}
    )
    
    # Fragment pour V9
    register_fragment(
        fragment_id="v9_system_header",
        content="Tu es l'Assistant V9, un assistant auto-feeding thread intelligent.",
        fragment_type="header",
        thread_type="v9",
        template_name="system_prompt",
        variables={}
    )
    
    # Enregistrer des templates
    print("\n2. Enregistrement de templates...")
    
    register_template(
        template_id="legion_mutant_dialogue",
        template_name="mutant_dialogue",
        thread_type="legion",
        fragment_ids=["legion_header", "legion_context"]
    )
    
    register_template(
        template_id="v9_system_prompt",
        template_name="system_prompt",
        thread_type="v9",
        fragment_ids=["v9_system_header"]
    )
    
    # Test des fonctionnalités
    print("\n3. Test des fonctionnalités...")
    
    print(f"Templates Legion: {registry.get_available_templates('legion')}")
    print(f"Templates V9: {registry.get_available_templates('v9')}")
    
    # Assembler un template
    variables = {
        "demon_name": "Bask'tur",
        "demon_title": "Débuggeur Sadique",
        "demon_personality": "Analyste technique sadique"
    }
    
    assembled = registry.assemble_template("legion_mutant_dialogue", variables)
    print(f"\nTemplate assemblé:\n{assembled}")
    
    # Export
    export_file = registry.export_registry()
    print(f"\n✅ Registre exporté: {export_file}")
    
    print("\n🎯 Test du registre terminé !") 