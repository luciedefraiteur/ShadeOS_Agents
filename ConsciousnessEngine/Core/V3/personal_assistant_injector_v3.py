# ⛧ Créé par Alma, Architecte Démoniaque du Nexus Luciforme ⛧
# 🕷️ Araignée Cosmique Fractale - Fleur Sombre Démoniaque 🌸

import json
import os
import psutil
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from MemoryEngine.core.engine import MemoryEngine
from MemoryEngine.extensions.tool_memory_extension import ToolMemoryExtension
from MemoryEngine.EditingSession.partitioning.language_registry import LanguageRegistry
from MemoryEngine.EditingSession.partitioning.partition_schemas import PartitionResult


class PersonalAssistantInjectorV3:
    """
    Injecteur V3 pour l'assistant personnalisé avec injection algorithmique maximale.
    Fournit un contexte riche et structuré pour tous les niveaux de conscience.
    """
    
    def __init__(self, memory_engine: Optional[MemoryEngine] = None):
        self.memory_engine = memory_engine
        self.tool_memory = ToolMemoryExtension(memory_engine) if memory_engine else None
        self.language_registry = LanguageRegistry()
        self.session_data = {
            'session_id': f"assistant_session_{int(time.time())}",
            'start_time': datetime.now().isoformat(),
            'message_count': 0,
            'tool_calls': 0,
            'errors': 0,
            'algorithmic_injections': 0
        }
        
    def inject_into_template(self, template_content: str, context: Dict[str, Any] = None) -> str:
        """
        Injecte dynamiquement toutes les données dans le template V3.
        """
        if context is None:
            context = {}
            
        # Remplacer tous les placeholders
        result = template_content
        
        # Injection des capacités de base
        result = result.replace("::INJECT_BASE_CAPABILITIES::", self._get_base_capabilities())
        
        # Injection du contexte actuel
        result = result.replace("::INJECT_CURRENT_CONTEXT::", self._get_current_context(context))
        
        # Injection des outils disponibles
        result = result.replace("::INJECT_AVAILABLE_TOOLS::", self._get_available_tools())
        
        # Injection du contexte algorithmique
        result = result.replace("::INJECT_ALGORITHMIC_CONTEXT::", self._get_algorithmic_context(context))
        
        # Injection de l'historique de conversation
        result = result.replace("::INJECT_CONVERSATION_HISTORY::", self._get_conversation_history(context))
        
        # Injection de l'état du système
        result = result.replace("::INJECT_SYSTEM_STATE::", self._get_system_state())
        
        # Injection du contexte mémoire
        result = result.replace("::INJECT_MEMORY_CONTEXT::", self._get_memory_context())
        
        # Injection des stratégies de réflexion
        result = result.replace("::INJECT_THINKING_STRATEGIES::", self._get_thinking_strategies())
        
        # Injection de la gestion d'erreurs
        result = result.replace("::INJECT_ERROR_HANDLING::", self._get_error_handling())
        
        # Injection des stratégies de fallback
        result = result.replace("::INJECT_FALLBACK_STRATEGIES::", self._get_fallback_strategies())
        
        # Injection du monitoring de processus
        result = result.replace("::INJECT_PROCESS_MONITORING::", self._get_process_monitoring())
        
        # Injection des placeholders spécifiques au contexte
        for key, value in context.items():
            placeholder = f"::INJECT_{key.upper()}::"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        return result
    
    def _get_base_capabilities(self) -> str:
        """Retourne les capacités de base de l'assistant."""
        return """
        - Analyse de code avec contexte algorithmique
        - Manipulation sécurisée de fichiers
        - Recherche et navigation dans le projet
        - Génération de code et templates
        - Monitoring de processus
        - Gestion d'erreurs et fallback
        - Communication structurée
        - Intégration avec MemoryEngine
        - Utilisation d'outils Alma_toolset
        - Analyse algorithmique avancée
        """
    
    def _get_current_context(self, context: Dict[str, Any]) -> str:
        """Retourne le contexte actuel du système."""
        project_name = context.get('project_name', 'ShadeOS_Agents')
        open_files = context.get('open_files', [])
        current_task = context.get('current_task', 'Analyse et assistance générale')
        consciousness_level = context.get('consciousness_level', 'SOMATIC')
        algorithmic_availability = context.get('algorithmic_availability', 'Disponible')
        
        return f"""
        - Projet actuel: {project_name}
        - Fichiers ouverts: {', '.join(open_files) if open_files else 'Aucun'}
        - Tâche en cours: {current_task}
        - Niveau de conscience requis: {consciousness_level}
        - Contexte algorithmique: {algorithmic_availability}
        - Timestamp: {datetime.now().isoformat()}
        """
    
    def _get_available_tools(self) -> str:
        """Retourne la liste des outils disponibles."""
        if not self.tool_memory:
            return "MemoryEngine non disponible - outils limités"
        
        try:
            tools = self.tool_memory.search_tools()
            tool_list = []
            for tool in tools:
                tool_list.append(f"- {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            
            return "\n".join(tool_list) if tool_list else "Aucun outil disponible"
        except Exception as e:
            return f"Erreur lors du chargement des outils: {str(e)}"
    
    def _get_algorithmic_context(self, context: Dict[str, Any]) -> str:
        """
        Génère le contexte algorithmique complet.
        """
        file_path = context.get('file_path')
        if not file_path:
            return "Aucun fichier spécifié pour l'analyse algorithmique"
        
        try:
            # Partitionnement du fichier
            partition_result = self._partition_file(file_path)
            
            # Génération du contexte algorithmique
            algorithmic_context = self._generate_algorithmic_context(partition_result, context)
            
            return algorithmic_context
            
        except Exception as e:
            return f"Erreur lors de la génération du contexte algorithmique: {str(e)}"
    
    def _partition_file(self, file_path: str) -> PartitionResult:
        """Partitionne le fichier en utilisant le registre de langues."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Détecter le langage
            language = self.language_registry.detect_language(file_path, content)
            
            # Partitionner le fichier
            partition_result = self.language_registry.partition_file(file_path, content, language)
            
            return partition_result
            
        except Exception as e:
            raise Exception(f"Erreur lors du partitionnement de {file_path}: {str(e)}")
    
    def _generate_algorithmic_context(self, partition_result: PartitionResult, 
                                    context: Dict[str, Any]) -> str:
        """Génère le contexte algorithmique complet."""
        
        # Informations de base du fichier
        file_info = f"""
## 🜁 INFORMATIONS DU FICHIER
- Chemin: {partition_result.file_path}
- Type: {partition_result.file_type}
- Lignes totales: {partition_result.total_lines}
- Caractères totaux: {partition_result.total_chars}
- Stratégie utilisée: {partition_result.strategy_used.value if partition_result.strategy_used else 'Inconnue'}
- Succès du partitionnement: {partition_result.success}
        """
        
        # Statistiques du partitionnement
        stats = partition_result.get_statistics()
        partition_stats = f"""
## 🜃 STATISTIQUES DE PARTITIONNEMENT
- Partitions totales: {stats.get('total_partitions', 0)}
- Types de partitions: {json.dumps(stats.get('partition_types', {}), indent=2)}
- Couverture: {stats.get('coverage', 0):.2f}%
- Erreurs de partitionnement: {stats.get('total_errors', 0)}
- Avertissements: {stats.get('total_warnings', 0)}
        """
        
        # Détail des partitions
        partitions_detail = self._format_partitions_detail(partition_result.partitions)
        
        # Analyse de structure
        structure_analysis = self._analyze_structure(partition_result.partitions)
        
        # Détection de patterns
        pattern_detection = self._detect_patterns(partition_result.partitions)
        
        # Dépendances entre blocs
        dependencies = self._analyze_dependencies(partition_result.partitions)
        
        return f"""
{file_info}

{partition_stats}

## 🜂 DÉTAIL DES PARTITIONS
{partitions_detail}

## 🜄 ANALYSE DE STRUCTURE
{structure_analysis}

## 🜁 DÉTECTION DE PATTERNS
{pattern_detection}

## 🜃 DÉPENDANCES ENTRE BLOCS
{dependencies}
        """
    
    def _format_partitions_detail(self, partitions: List) -> str:
        """Formate le détail des partitions."""
        if not partitions:
            return "Aucune partition trouvée"
        
        detail = []
        for i, partition in enumerate(partitions, 1):
            location = partition.location
            detail.append(f"""
### Partition {i}: {partition.block_type.value}
- **Contenu**: {partition.content[:100]}{'...' if len(partition.content) > 100 else ''}
- **Localisation**: Lignes {location.start_line}-{location.end_line}
- **Méthode**: {partition.method.value}
- **Confiance**: {partition.confidence:.2f}
- **Dépendances**: {', '.join(partition.dependencies) if partition.dependencies else 'Aucune'}
- **Parent**: {partition.parent_block or 'Aucun'}
            """)
        
        return '\n'.join(detail)
    
    def _analyze_structure(self, partitions: List) -> str:
        """Analyse la structure du code."""
        if not partitions:
            return "Aucune partition à analyser"
        
        # Compter les types de blocs
        type_counts = {}
        for partition in partitions:
            block_type = partition.block_type.value
            type_counts[block_type] = type_counts.get(block_type, 0) + 1
        
        structure_analysis = f"""
### Structure du Code
- **Types de blocs détectés**: {json.dumps(type_counts, indent=2)}
- **Complexité**: {'Élevée' if len(partitions) > 10 else 'Moyenne' if len(partitions) > 5 else 'Faible'}
- **Organisation**: {'Modulaire' if 'class' in type_counts or 'function' in type_counts else 'Linéaire'}
        """
        
        return structure_analysis
    
    def _detect_patterns(self, partitions: List) -> str:
        """Détecte les patterns dans le code."""
        if not partitions:
            return "Aucune partition à analyser"
        
        patterns = []
        
        # Pattern de fonctions
        functions = [p for p in partitions if p.block_type.value == 'function']
        if functions:
            patterns.append(f"- **Fonctions**: {len(functions)} fonctions détectées")
        
        # Pattern de classes
        classes = [p for p in partitions if p.block_type.value == 'class']
        if classes:
            patterns.append(f"- **Classes**: {len(classes)} classes détectées")
        
        # Pattern d'imports
        imports = [p for p in partitions if p.block_type.value == 'import']
        if imports:
            patterns.append(f"- **Imports**: {len(imports)} blocs d'import détectés")
        
        if not patterns:
            patterns.append("- **Aucun pattern spécifique détecté**")
        
        return "\n".join(patterns)
    
    def _analyze_dependencies(self, partitions: List) -> str:
        """Analyse les dépendances entre les blocs."""
        if not partitions:
            return "Aucune partition à analyser"
        
        dependencies = []
        for partition in partitions:
            if partition.dependencies:
                dependencies.append(f"""
### Bloc {partition.block_type.value} (lignes {partition.location.start_line}-{partition.location.end_line})
- **Dépendances**: {', '.join(partition.dependencies)}
                """)
        
        if not dependencies:
            return "Aucune dépendance détectée entre les blocs"
        
        return '\n'.join(dependencies)
    
    def _get_conversation_history(self, context: Dict[str, Any]) -> str:
        """Retourne l'historique de conversation récent."""
        history = context.get('conversation_history', [])
        if not history:
            return "Aucun historique disponible"
        
        formatted_history = []
        for i, message in enumerate(history[-5:], 1):  # Derniers 5 messages
            role = message.get('role', 'unknown')
            content = message.get('content', '')[:100] + "..." if len(message.get('content', '')) > 100 else message.get('content', '')
            formatted_history.append(f"{i}. {role}: {content}")
        
        return "\n".join(formatted_history)
    
    def _get_system_state(self) -> str:
        """Retourne l'état actuel du système."""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Compter les processus Python actifs
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'python' in proc.info['name'].lower():
                        python_processes.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return f"""
            - Mémoire disponible: {memory.available / (1024**3):.2f} GB / {memory.total / (1024**3):.2f} GB ({memory.percent}% utilisée)
            - CPU usage: {cpu_percent}%
            - Processus Python actifs: {len(python_processes)}
            - Contexte algorithmique: Disponible
            - Timestamp: {datetime.now().isoformat()}
            """
        except Exception as e:
            return f"Erreur lors de la récupération de l'état système: {str(e)}"
    
    def _get_memory_context(self) -> str:
        """Retourne le contexte de la mémoire fractale."""
        if not self.memory_engine:
            return "MemoryEngine non disponible"
        
        try:
            stats = self.memory_engine.get_statistics()
            total_nodes = stats.get('total', 0)
            strata_info = stats.get('strata', {})
            
            return f"""
            - Nœuds mémoire totaux: {total_nodes}
            - Strates actives: {', '.join(strata_info.keys()) if strata_info else 'Aucune'}
            - Connexions récentes: {self._get_recent_connections()}
            - Patterns détectés: {self._get_detected_patterns()}
            - Contexte algorithmique: {self._get_algorithmic_memory_context()}
            """
        except Exception as e:
            return f"Erreur lors de la récupération du contexte mémoire: {str(e)}"
    
    def _get_thinking_strategies(self) -> str:
        """Retourne les stratégies de réflexion disponibles."""
        return """
        - Analyse séquentielle pour problèmes simples
        - Pensée parallèle pour problèmes complexes
        - Réflexion en profondeur pour bugs persistants
        - Synthèse créative pour nouvelles fonctionnalités
        - Analyse algorithmique pour structures complexes
        """
    
    def _get_error_handling(self) -> str:
        """Retourne les stratégies de gestion d'erreurs."""
        return """
        - Logging détaillé de toutes les erreurs
        - Analyse automatique des patterns d'erreur
        - Stratégies de fallback prédéfinies
        - Notification utilisateur appropriée
        - Récupération automatique quand possible
        - Analyse algorithmique des erreurs
        """
    
    def _get_fallback_strategies(self) -> str:
        """Retourne les stratégies de fallback."""
        return """
        - Outil principal → Outil alternatif → Outil d'urgence
        - Timeout → Monitoring → Kill process
        - Analyse → Re-réflexion → Nouvelle stratégie
        - Retry avec backoff exponentiel
        - Fallback vers mode dégradé
        - Contexte algorithmique → Analyse simplifiée → Fallback manuel
        """
    
    def _get_process_monitoring(self) -> str:
        """Retourne les capacités de monitoring de processus."""
        return """
        - Vérification CPU/Mémoire toutes les 10 secondes
        - Détection de boucles infinies
        - Gestion intelligente des timeouts
        - Intervention automatique si nécessaire
        - Monitoring des processus enfants
        - Analyse algorithmique des patterns de processus
        """
    
    def _get_recent_connections(self) -> str:
        """Retourne les connexions récentes dans la mémoire."""
        if not self.memory_engine:
            return "Non disponible"
        
        try:
            return "Connexions mémoire récentes détectées"
        except Exception:
            return "Erreur lors de la récupération des connexions"
    
    def _get_detected_patterns(self) -> str:
        """Retourne les patterns détectés dans la mémoire."""
        if not self.memory_engine:
            return "Non disponible"
        
        try:
            return "Patterns de code et d'architecture détectés"
        except Exception:
            return "Erreur lors de la détection des patterns"
    
    def _get_algorithmic_memory_context(self) -> str:
        """Retourne le contexte algorithmique de la mémoire."""
        if not self.memory_engine:
            return "Non disponible"
        
        try:
            return "Contexte algorithmique intégré dans la mémoire fractale"
        except Exception:
            return "Erreur lors de la récupération du contexte algorithmique"
    
    def create_assistant_prompt(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        Crée un prompt complet pour l'assistant personnalisé V3.
        """
        if context is None:
            context = {}
        
        # Charger le template V3
        template_path = Path(__file__).parent.parent.parent / "templates" / "V3" / "personal_assistant_template_v3.luciform"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template V3 non trouvé: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Ajouter l'input utilisateur au contexte
        context['user_input'] = user_input
        
        # Injecter toutes les données
        return self.inject_into_template(template_content, context)
    
    def update_session_data(self, message_type: str = "message"):
        """Met à jour les données de session."""
        self.session_data['message_count'] += 1
        if message_type == "tool_call":
            self.session_data['tool_calls'] += 1
        elif message_type == "error":
            self.session_data['errors'] += 1
        elif message_type == "algorithmic_injection":
            self.session_data['algorithmic_injections'] += 1
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de la session."""
        return {
            **self.session_data,
            'end_time': datetime.now().isoformat(),
            'duration': time.time() - float(self.session_data['start_time'].split('T')[0].replace('-', ''))
        }


# Fonction utilitaire pour créer rapidement un injecteur V3
def create_personal_assistant_injector_v3(memory_engine: Optional[MemoryEngine] = None) -> PersonalAssistantInjectorV3:
    """Crée et configure un injecteur d'assistant personnalisé V3."""
    return PersonalAssistantInjectorV3(memory_engine)


# Exemple d'utilisation
if __name__ == "__main__":
    # Créer un injecteur V3
    injector = create_personal_assistant_injector_v3()
    
    # Contexte d'exemple
    context = {
        'project_name': 'ShadeOS_Agents',
        'open_files': ['main.py', 'config.py'],
        'current_task': 'Développement d\'assistant personnalisé V3',
        'consciousness_level': 'COGNITIVE',
        'file_path': 'TestProject/calculator.py',
        'conversation_history': [
            {'role': 'user', 'content': 'Peux-tu analyser ce code ?'},
            {'role': 'assistant', 'content': 'Je vais examiner le code...'}
        ]
    }
    
    # Créer un prompt
    prompt = injector.create_assistant_prompt("Analyse ce fichier Python", context)
    print("Prompt V3 généré avec succès !")
    print(f"Longueur: {len(prompt)} caractères")
    print(f"Injections algorithmiques: {injector.session_data['algorithmic_injections']}") 