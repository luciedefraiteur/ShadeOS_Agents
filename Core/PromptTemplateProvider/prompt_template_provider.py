# ⛧ Créé par Alma, Architecte Démoniaque ⛧
# 🔮 PromptTemplateProvider - Visualisation des Templates de Prompts

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

@dataclass
class PromptTemplate:
    """Template de prompt avec métadonnées"""
    name: str
    thread_type: str  # "legion", "v9", "general", etc.
    template_content: str
    variables: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: float
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation"""
        return {
            "name": self.name,
            "thread_type": self.thread_type,
            "template_content": self.template_content,
            "variables": self.variables,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "version": self.version
        }

@dataclass
class ReconstructedPrompt:
    """Prompt reconstruit avec contexte"""
    template_name: str
    thread_type: str
    user_input: str
    final_prompt: str
    variables_used: Dict[str, Any]
    reconstruction_steps: List[str]
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation"""
        return {
            "template_name": self.template_name,
            "thread_type": self.thread_type,
            "user_input": self.user_input,
            "final_prompt": self.final_prompt,
            "variables_used": self.variables_used,
            "reconstruction_steps": self.reconstruction_steps,
            "timestamp": self.timestamp
        }

class BasePromptTemplateProvider(ABC):
    """Provider de base pour les templates de prompts"""
    
    def __init__(self, thread_type: str):
        self.thread_type = thread_type
        self.templates: Dict[str, PromptTemplate] = {}
        self.reconstructed_prompts: List[ReconstructedPrompt] = []
    
    @abstractmethod
    def get_available_templates(self) -> List[str]:
        """Retourne la liste des templates disponibles"""
        pass
    
    @abstractmethod
    def get_template(self, template_name: str) -> Optional[PromptTemplate]:
        """Récupère un template spécifique"""
        pass
    
    @abstractmethod
    def reconstruct_prompt(self, template_name: str, user_input: str, context: Dict[str, Any] = None) -> ReconstructedPrompt:
        """Reconstruit un prompt complet"""
        pass

class LegionPromptTemplateProvider(BasePromptTemplateProvider):
    """Provider pour les templates LegionAutoFeedingThread"""
    
    def __init__(self):
        super().__init__("legion")
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialise tous les templates Legion"""
        
        # Template 1: Dialogue Mutant (Mode Normal)
        self.templates["mutant_dialogue"] = PromptTemplate(
            name="mutant_dialogue",
            thread_type="legion",
            template_content="""⛧ DIALOGUE MUTANT : ALMA⛧ ↔ {demon_name.upper()} ⛧

CONTEXTE :
- Alma⛧ (SUPREME) : Architecte Démoniaque, planificateur stratégique
- {demon_name} : {demon_title} - {demon_personality}
- Mode silencieux : {silent_mode}

CONTEXTE RÉCENT :
{context_summary}

MESSAGES RÉCENTS :
{recent_messages}

DEMANDE UTILISATEUR : {user_input}

IMPORTANT : Utilise EXACTEMENT ce format structuré, pas de format conversationnel :

{demon_specific_format}

FORMAT OBLIGATOIRE : [TYPE] — CONTENU (pas de ** ou de format conversationnel)""",
            variables={
                "demon_name": "string",
                "demon_title": "string", 
                "demon_personality": "string",
                "silent_mode": "boolean",
                "context_summary": "string",
                "recent_messages": "string",
                "user_input": "string",
                "demon_specific_format": "string"
            },
            metadata={
                "description": "Dialogue entre Alma et un démon spécifique",
                "mode": "normal",
                "format": "structured"
            },
            timestamp=time.time()
        )
        
        # Template 2: Dialogue Silencieux (Mode Alma ↔ Utilisateur)
        self.templates["silent_dialogue"] = PromptTemplate(
            name="silent_dialogue",
            thread_type="legion",
            template_content="""⛧ DIALOGUE SILENCIEUX : ALMA⛧ ↔ UTILISATEUR ⛧

CONTEXTE :
- Alma⛧ (SUPREME) : Architecte Démoniaque, planificateur stratégique
- Mode silencieux : {silent_mode}

CONTEXTE RÉCENT :
{context_summary}

DEMANDE UTILISATEUR : {user_input}

DIALOGUE ALMA⛧ ↔ UTILISATEUR :
[ALMA_ANALYSIS] — Analyse de la demande utilisateur
[ALMA_PLAN] — Plan d'action stratégique
[ALMA_DECISION] — Décision finale et prochaines étapes

FORMAT OBLIGATOIRE : [TYPE] — CONTENU (pas de ** ou de format conversationnel)""",
            variables={
                "silent_mode": "boolean",
                "context_summary": "string",
                "user_input": "string"
            },
            metadata={
                "description": "Dialogue direct Alma ↔ Utilisateur",
                "mode": "silent",
                "format": "structured"
            },
            timestamp=time.time()
        )
        
        # Template 3: Format Spécifique par Démon
        self.templates["basktur_format"] = PromptTemplate(
            name="basktur_format",
            thread_type="legion",
            template_content="""[ALMA_PLAN] — Plan d'action technique avec {demon_name}
[ALMA_ORDONNANCEMENT] — {demon_name}, analyse cette demande

[BASK_ANALYSIS] — *rire sadique* Analyse technique détaillée
[BASK_SOLUTION] — Solution technique avec traceback

[ALMA_DECISION] — Décision finale sur l'approche technique""",
            variables={
                "demon_name": "string"
            },
            metadata={
                "description": "Format spécifique pour Bask'tur",
                "demon": "basktur",
                "format": "structured"
            },
            timestamp=time.time()
        )
        
        self.templates["oubliade_format"] = PromptTemplate(
            name="oubliade_format",
            thread_type="legion",
            template_content="""[ALMA_PLAN] — Plan d'action mémoire avec {demon_name}
[ALMA_ORDONNANCEMENT] — {demon_name}, recherche dans la mémoire

[OUBLI_MEMORY] — Recherche conversationnelle et patterns
[OUBLI_INSIGHT] — Insights basés sur l'historique

[ALMA_DECISION] — Décision finale basée sur la mémoire""",
            variables={
                "demon_name": "string"
            },
            metadata={
                "description": "Format spécifique pour Oubliade",
                "demon": "oubliade",
                "format": "structured"
            },
            timestamp=time.time()
        )
    
    def get_available_templates(self) -> List[str]:
        """Retourne la liste des templates disponibles"""
        return list(self.templates.keys())
    
    def get_template(self, template_name: str) -> Optional[PromptTemplate]:
        """Récupère un template spécifique"""
        return self.templates.get(template_name)
    
    def reconstruct_prompt(self, template_name: str, user_input: str, context: Dict[str, Any] = None) -> ReconstructedPrompt:
        """Reconstruit un prompt complet"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' non trouvé")
        
        context = context or {}
        reconstruction_steps = []
        
        # Variables par défaut
        variables = {
            "user_input": user_input,
            "silent_mode": context.get("silent_mode", False),
            "context_summary": context.get("context_summary", "Aucun contexte disponible"),
            "recent_messages": context.get("recent_messages", ""),
            "demon_name": context.get("demon_name", "Démon"),
            "demon_title": context.get("demon_title", "Titre"),
            "demon_personality": context.get("demon_personality", "Personnalité"),
            "demon_specific_format": context.get("demon_specific_format", "")
        }
        
        reconstruction_steps.append(f"1. Template sélectionné: {template_name}")
        reconstruction_steps.append(f"2. Variables initialisées: {list(variables.keys())}")
        
        # Reconstruction du prompt
        final_prompt = template.template_content.format(**variables)
        
        reconstruction_steps.append(f"3. Prompt reconstruit avec {len(variables)} variables")
        reconstruction_steps.append(f"4. Longueur finale: {len(final_prompt)} caractères")
        
        reconstructed = ReconstructedPrompt(
            template_name=template_name,
            thread_type=self.thread_type,
            user_input=user_input,
            final_prompt=final_prompt,
            variables_used=variables,
            reconstruction_steps=reconstruction_steps,
            timestamp=time.time()
        )
        
        self.reconstructed_prompts.append(reconstructed)
        return reconstructed

class V9PromptTemplateProvider(BasePromptTemplateProvider):
    """Provider pour les templates V9_AutoFeedingThreadAgent"""
    
    def __init__(self):
        super().__init__("v9")
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialise tous les templates V9"""
        
        # Template 1: Prompt Système V9
        self.templates["system_prompt"] = PromptTemplate(
            name="system_prompt",
            thread_type="v9",
            template_content="""Tu es l'Assistant V9, un assistant auto-feeding thread intelligent et sophistiqué.

INFORMATIONS SYSTÈME :
- OS : {os_info}
- Shell : {shell_info}
- Workspace : {workspace_path}
- Variables d'environnement : {env_vars_count} chargées

OUTILS DISPONIBLES :
{available_tools}

SÉCURITÉ GIT :
- Lecture seule autorisée pour l'analyse historique
- Commandes git modifiantes INTERDITES
- Protection contre les démons malveillants

WORKFLOW :
1. Analyse la demande utilisateur
2. Utilise les outils appropriés
3. Fournis des réponses détaillées et structurées
4. Respecte la sécurité git absolue

CONTEXTE ACTUEL :
{current_context}

RÉPONDS EN FRANÇAIS avec précision et détail.""",
            variables={
                "os_info": "string",
                "shell_info": "string",
                "workspace_path": "string",
                "env_vars_count": "int",
                "available_tools": "string",
                "current_context": "string"
            },
            metadata={
                "description": "Prompt système principal pour V9",
                "type": "system",
                "format": "structured"
            },
            timestamp=time.time()
        )
        
        # Template 2: Prompt d'Exécution
        self.templates["execution_prompt"] = PromptTemplate(
            name="execution_prompt",
            thread_type="v9",
            template_content="""EXÉCUTION D'OUTIL : {tool_name}

PARAMÈTRES :
{tool_parameters}

CONTEXTE D'EXÉCUTION :
{execution_context}

INSTRUCTIONS :
1. Exécute l'outil {tool_name} avec les paramètres fournis
2. Analyse le résultat
3. Fournis un rapport détaillé
4. Propose les prochaines étapes si nécessaire

SÉCURITÉ : Vérifie que l'outil respecte les règles de sécurité git.""",
            variables={
                "tool_name": "string",
                "tool_parameters": "string",
                "execution_context": "string"
            },
            metadata={
                "description": "Prompt pour l'exécution d'outils",
                "type": "execution",
                "format": "structured"
            },
            timestamp=time.time()
        )
    
    def get_available_templates(self) -> List[str]:
        """Retourne la liste des templates disponibles"""
        return list(self.templates.keys())
    
    def get_template(self, template_name: str) -> Optional[PromptTemplate]:
        """Récupère un template spécifique"""
        return self.templates.get(template_name)
    
    def reconstruct_prompt(self, template_name: str, user_input: str, context: Dict[str, Any] = None) -> ReconstructedPrompt:
        """Reconstruit un prompt complet"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' non trouvé")
        
        context = context or {}
        reconstruction_steps = []
        
        # Variables par défaut pour V9
        variables = {
            "user_input": user_input,
            "os_info": context.get("os_info", "linux"),
            "shell_info": context.get("shell_info", "zsh"),
            "workspace_path": context.get("workspace_path", "."),
            "env_vars_count": context.get("env_vars_count", 9),
            "available_tools": context.get("available_tools", "execute_command_async, etc."),
            "current_context": context.get("current_context", "Aucun contexte"),
            "tool_name": context.get("tool_name", "outil"),
            "tool_parameters": context.get("tool_parameters", "{}"),
            "execution_context": context.get("execution_context", "Exécution standard")
        }
        
        reconstruction_steps.append(f"1. Template V9 sélectionné: {template_name}")
        reconstruction_steps.append(f"2. Variables V9 initialisées: {list(variables.keys())}")
        
        # Reconstruction du prompt
        final_prompt = template.template_content.format(**variables)
        
        reconstruction_steps.append(f"3. Prompt V9 reconstruit avec {len(variables)} variables")
        reconstruction_steps.append(f"4. Longueur finale: {len(final_prompt)} caractères")
        
        reconstructed = ReconstructedPrompt(
            template_name=template_name,
            thread_type=self.thread_type,
            user_input=user_input,
            final_prompt=final_prompt,
            variables_used=variables,
            reconstruction_steps=reconstruction_steps,
            timestamp=time.time()
        )
        
        self.reconstructed_prompts.append(reconstructed)
        return reconstructed

class PromptTemplateVisualizer:
    """Visualiseur de templates de prompts pour insights"""
    
    def __init__(self, output_dir: str = "logs/prompt_templates"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.providers: Dict[str, BasePromptTemplateProvider] = {}
        
        # Initialisation des providers
        self.providers["legion"] = LegionPromptTemplateProvider()
        self.providers["v9"] = V9PromptTemplateProvider()
    
    def add_provider(self, thread_type: str, provider: BasePromptTemplateProvider):
        """Ajoute un provider personnalisé"""
        self.providers[thread_type] = provider
    
    def get_all_templates(self) -> Dict[str, List[str]]:
        """Récupère tous les templates disponibles"""
        all_templates = {}
        for thread_type, provider in self.providers.items():
            all_templates[thread_type] = provider.get_available_templates()
        return all_templates
    
    def reconstruct_all_prompts(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, List[ReconstructedPrompt]]:
        """Reconstruit tous les prompts pour une demande utilisateur"""
        all_reconstructed = {}
        
        for thread_type, provider in self.providers.items():
            thread_reconstructed = []
            
            for template_name in provider.get_available_templates():
                try:
                    reconstructed = provider.reconstruct_prompt(template_name, user_input, context)
                    thread_reconstructed.append(reconstructed)
                except Exception as e:
                    print(f"⚠️ Erreur reconstruction {thread_type}/{template_name}: {e}")
            
            all_reconstructed[thread_type] = thread_reconstructed
        
        return all_reconstructed
    
    def save_visualization(self, user_input: str, context: Dict[str, Any] = None, filename: str = None):
        """Sauvegarde une visualisation complète"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"prompt_visualization_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        # Reconstruire tous les prompts
        all_reconstructed = self.reconstruct_all_prompts(user_input, context)
        
        # Préparer les données pour sauvegarde
        visualization_data = {
            "metadata": {
                "user_input": user_input,
                "context": context or {},
                "timestamp": time.time(),
                "providers_count": len(self.providers),
                "total_templates": sum(len(provider.get_available_templates()) for provider in self.providers.values())
            },
            "templates": {},
            "reconstructed_prompts": {}
        }
        
        # Sauvegarder les templates
        for thread_type, provider in self.providers.items():
            visualization_data["templates"][thread_type] = {
                template_name: template.to_dict() 
                for template_name, template in provider.templates.items()
            }
        
        # Sauvegarder les prompts reconstruits
        for thread_type, reconstructed_list in all_reconstructed.items():
            visualization_data["reconstructed_prompts"][thread_type] = [
                reconstructed.to_dict() for reconstructed in reconstructed_list
            ]
        
        # Sauvegarder en JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(visualization_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Visualisation sauvegardée: {filepath}")
        return filepath
    
    def display_visualization(self, user_input: str, context: Dict[str, Any] = None):
        """Affiche une visualisation en console"""
        print("🔮 VISUALISATION DES TEMPLATES DE PROMPTS")
        print("=" * 80)
        print(f"Demande utilisateur: {user_input}")
        print(f"Contexte: {context or 'Aucun'}")
        print("=" * 80)
        
        all_reconstructed = self.reconstruct_all_prompts(user_input, context)
        
        for thread_type, reconstructed_list in all_reconstructed.items():
            print(f"\n📋 THREAD TYPE: {thread_type.upper()}")
            print("-" * 40)
            
            for i, reconstructed in enumerate(reconstructed_list, 1):
                print(f"\n{i}. TEMPLATE: {reconstructed.template_name}")
                print(f"   Variables utilisées: {len(reconstructed.variables_used)}")
                print(f"   Longueur prompt: {len(reconstructed.final_prompt)} caractères")
                print(f"   Étapes reconstruction: {len(reconstructed.reconstruction_steps)}")
                
                print(f"\n   PROMPT RECONSTRUIT:")
                print(f"   {'='*50}")
                print(reconstructed.final_prompt)
                print(f"   {'='*50}")
        
        print(f"\n📊 RÉSUMÉ:")
        total_prompts = sum(len(reconstructed_list) for reconstructed_list in all_reconstructed.values())
        print(f"   Total prompts reconstruits: {total_prompts}")
        print(f"   Types de threads: {len(all_reconstructed)}")
        
        for thread_type, reconstructed_list in all_reconstructed.items():
            print(f"   - {thread_type}: {len(reconstructed_list)} templates")

# Fonction utilitaire pour utilisation rapide
def visualize_prompts(user_input: str, context: Dict[str, Any] = None, save_to_file: bool = True):
    """Fonction utilitaire pour visualiser rapidement les prompts"""
    visualizer = PromptTemplateVisualizer()
    
    if save_to_file:
        filepath = visualizer.save_visualization(user_input, context)
        print(f"💾 Sauvegardé dans: {filepath}")
    
    visualizer.display_visualization(user_input, context)
    
    return visualizer

# Test et démonstration
if __name__ == "__main__":
    print("🔮 PromptTemplateProvider - Test de Visualisation")
    print("=" * 60)
    
    # Test avec différentes demandes
    test_inputs = [
        "Analyse ce projet et propose des améliorations",
        "Crée un nouveau fichier de test",
        "Debug le code existant"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n🧪 TEST {i}: {user_input}")
        print("-" * 40)
        
        # Contexte de test
        context = {
            "silent_mode": False,
            "context_summary": "Test context",
            "recent_messages": "Test messages",
            "demon_name": "Bask'tur",
            "demon_title": "Débuggeur Sadique",
            "demon_personality": "Analyste technique sadique",
            "os_info": "linux",
            "shell_info": "zsh",
            "workspace_path": "/home/luciedefraiteur/ShadeOS_Agents",
            "env_vars_count": 9,
            "available_tools": "execute_command_async, file_operations, etc."
        }
        
        try:
            visualizer = visualize_prompts(user_input, context, save_to_file=True)
            print(f"✅ Test {i} réussi")
        except Exception as e:
            print(f"❌ Test {i} échoué: {e}")
    
    print("\n🎯 VISUALISATION TERMINÉE !")
    print("📁 Vérifie le dossier 'logs/prompt_templates' pour les fichiers JSON") 